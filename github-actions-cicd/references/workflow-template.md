## Workflow Template

> **Note:** The Action versions pinned in the examples below (e.g. `actions/checkout@v4`, `aws-actions/configure-aws-credentials@v4`, `appleboy/ssh-action@v1.0.3`) are illustrative and may drift behind the current major release over time. Before copying them into a production workflow, verify the latest tagged release for each action (e.g. `gh release list --repo <owner>/<action-repo> -L 5` or the action's repo Releases page) rather than assuming the version shown here is current.

```yaml
name: CI/CD Build and Deploy

on:
  push:
    branches: ["dev"]

permissions:
  contents: read

concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ vars.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, Tag, and Push (webapp)
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY }}
        run: |
          docker build \
            --build-arg NEXT_PUBLIC_API_DATA_SOURCE="${{ vars.NEXT_PUBLIC_API_DATA_SOURCE }}" \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:webapp ./webapp
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:webapp

      - name: Build, Tag, and Push (service)
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY }}
        run: |
          docker build \
            -t $ECR_REGISTRY/$ECR_REPOSITORY:watcher \
            -f services/watcher/Dockerfile .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:watcher

  deploy:
    needs: build-and-push
    if: ${{ needs.build-and-push.result == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - name: SSH to EC2 and Deploy
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ vars.EC2_HOST }}
          username: ${{ vars.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          port: 22
          script_stop: true
          envs: TARGET_REGION,TARGET_ACCOUNT,TARGET_REPO,PUBLIC_DOMAIN
          script: |
            set -euo pipefail

            # 1. Login ECR — write credentials to a throwaway file, never touch ~/.aws
            export AWS_SHARED_CREDENTIALS_FILE="$(mktemp)"
            chmod 600 "${AWS_SHARED_CREDENTIALS_FILE}"
            trap 'rm -f "${AWS_SHARED_CREDENTIALS_FILE}"' EXIT
            printf "[default]\naws_access_key_id = %s\naws_secret_access_key = %s\n" \
              '${{ vars.AWS_ACCESS_KEY_ID }}' \
              '${{ secrets.AWS_SECRET_ACCESS_KEY }}' > "${AWS_SHARED_CREDENTIALS_FILE}"

            IMAGE="${TARGET_ACCOUNT}.dkr.ecr.${TARGET_REGION}.amazonaws.com/${TARGET_REPO}:webapp"
            APP_CONTAINER="myapp"

            aws ecr get-login-password --region ${TARGET_REGION} | \
              docker login --username AWS --password-stdin \
              ${TARGET_ACCOUNT}.dkr.ecr.${TARGET_REGION}.amazonaws.com

            # 2. Pull + prune dangling
            docker pull "${IMAGE}"
            docker image prune -f

            # 3. Smoke test
            SMOKE_CONTAINER="${APP_CONTAINER}_smoke"
            docker rm -f "${SMOKE_CONTAINER}" || true
            docker run -d --name "${SMOKE_CONTAINER}" -p 127.0.0.1:3001:3000 "${IMAGE}"

            SMOKE_OK="false"
            for i in $(seq 1 15); do
              if curl -fsS http://127.0.0.1:3001/healthz >/dev/null; then
                SMOKE_OK="true"
                break
              fi
              sleep 3
            done

            docker rm -f "${SMOKE_CONTAINER}" || true

            if [ "${SMOKE_OK}" != "true" ]; then
              echo "Smoke test failed"
              exit 1
            fi

            # 4. Deploy production — blue-green swap with automatic rollback on failure
            wait_for_url() {
              local container="$1" url="$2" retries="$3"
              for i in $(seq 1 "${retries}"); do
                if [ "$(docker inspect -f '{{.State.Running}}' "${container}" 2>/dev/null)" != "true" ]; then
                  echo "[wait_for_url] ${container} stopped running"
                  return 1
                fi
                if curl -fsS "${url}" >/dev/null 2>&1; then
                  return 0
                fi
                sleep 3
              done
              return 1
            }

            deploy_with_rollback() {
              local name="$1" image="$2" health_url="$3"
              shift 3
              local prev="${name}_previous"

              docker rm -f "${prev}" || true
              if docker inspect "${name}" >/dev/null 2>&1; then
                docker stop "${name}" >/dev/null
                docker rename "${name}" "${prev}"
              fi

              docker run -d --name "${name}" --restart always "$@" "${image}"

              if wait_for_url "${name}" "${health_url}" 15; then
                docker rm -f "${prev}" || true
                echo "[deploy_with_rollback] ${name} healthy, removed ${prev}"
              else
                echo "[deploy_with_rollback] ${name} failed health check, rolling back"
                docker logs --tail 200 "${name}" || true
                docker rm -f "${name}" || true
                if docker inspect "${prev}" >/dev/null 2>&1; then
                  docker rename "${prev}" "${name}"
                  docker start "${name}"
                fi
                return 1
              fi
            }

            deploy_with_rollback "${APP_CONTAINER}" "${IMAGE}" "http://127.0.0.1:3000/healthz" \
              -p 3000:3000 -e NODE_ENV=production

            # 5. Cleanup — keep last 24h of images so a manual rollback can still pull a recent tag
            docker image prune -f --filter 'until=24h'
        env:
          TARGET_REGION: ${{ vars.AWS_REGION }}
          TARGET_ACCOUNT: ${{ vars.AWS_ACCOUNT_ID }}
          TARGET_REPO: ${{ vars.ECR_REPOSITORY }}
          PUBLIC_DOMAIN: ${{ vars.PUBLIC_DOMAIN }}

  rollback:
    needs: deploy
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - name: SSH to EC2 and Rollback
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ vars.EC2_HOST }}
          username: ${{ vars.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          port: 22
          script_stop: true
          script: |
            set -euo pipefail
            APP_CONTAINER="myapp"
            PREV_CONTAINER="${APP_CONTAINER}_previous"
            # deploy_with_rollback already auto-rolls-back on failed health checks;
            # this job is the backup path for failures outside that function
            # (e.g. SSH drop, script crash before rollback ran).
            if docker inspect "${PREV_CONTAINER}" >/dev/null 2>&1; then
              docker rm -f "${APP_CONTAINER}" || true
              docker rename "${PREV_CONTAINER}" "${APP_CONTAINER}"
              docker start "${APP_CONTAINER}"
            else
              docker restart "${APP_CONTAINER}" || true
            fi
```

