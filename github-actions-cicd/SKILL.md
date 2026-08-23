---
name: GitHub Actions CI/CD (AWS ECR + EC2)
description: CI/CD pipeline pattern for building Docker images, pushing to AWS ECR, deploying to EC2 via SSH with smoke testing, multi-service orchestration, and automatic rollback. Includes advanced production patterns for config validation, selective/matrix builds with registry caching, dependency-gated jobs, and blue-green rollback.
---

# GitHub Actions CI/CD (AWS ECR + EC2)

CI/CD pipeline pattern for building Docker images, pushing to AWS ECR, deploying to EC2 via SSH with smoke testing, multi-service orchestration, and automatic rollback.

## Pipeline Architecture

```
Push to dev branch
│
├── Job 1: build-and-push
│   ├── Checkout code
│   ├── Configure AWS credentials
│   ├── Login to ECR
│   └── Build + push Docker images (webapp, watcher, download, generate, upload)
│
├── Job 2: deploy (needs: build-and-push)
│   ├── SSH to EC2
│   ├── Pull new images
│   ├── Smoke test (health check)
│   ├── Deploy RabbitMQ
│   ├── Deploy microservices (watcher, download, generate, upload)
│   ├── Deploy webapp (production)
│   └── Cleanup old images
│
└── Job 3: rollback (if deploy fails)
    ├── SSH to EC2
    └── Restart with previous image
```

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

## Key Patterns

### 1. Smoke Test Before Deploy

```bash
# Run container on different port
docker run -d --name smoke -p 127.0.0.1:3001:3000 "${IMAGE}"

# Health check loop (max 45 seconds)
for i in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:3001/healthz >/dev/null; then
    SMOKE_OK="true"
    break
  fi
  sleep 3
done

# Fail if health check didn't pass
if [ "${SMOKE_OK}" != "true" ]; then
  docker logs smoke || true
  docker rm -f smoke || true
  exit 1
fi

docker rm -f smoke || true
```

### 2. Credential Cleanup (Security)

```bash
# Never write AWS credentials to a fixed path on the host (~/.aws/credentials
# persists between runs). Use a throwaway file scoped to this script instead.
export AWS_SHARED_CREDENTIALS_FILE="$(mktemp)"
chmod 600 "${AWS_SHARED_CREDENTIALS_FILE}"
trap 'rm -f "${AWS_SHARED_CREDENTIALS_FILE}" "${ENV_FILE:-}"' EXIT

# Write temporary credentials
printf "[default]\naws_access_key_id = %s\naws_secret_access_key = %s\n" \
  '${ACCESS_KEY}' '${SECRET_KEY}' > "${AWS_SHARED_CREDENTIALS_FILE}"
```

### 3. Environment File for Secrets

```bash
# Create temp env file for docker --env-file
ENV_FILE="$(mktemp)"
cat > "${ENV_FILE}" <<'EOF'
AUTH_SECRET=xxx
DATABASE_URL=xxx
EOF

docker run --env-file "${ENV_FILE}" ...

# Cleaned up by trap
```

### 4. Multi-service Deployment

Order matters when services depend on each other for message delivery — a
downstream consumer must be ready before anything can safely produce to it.

```bash
# 1. Infrastructure first (message broker)
docker run -d --name rabbitmq --restart always \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER="${USER}" \
  -e RABBITMQ_DEFAULT_PASS="${PASS}" \
  rabbitmq:3.13-management-alpine

# 2. Consumer next — it must be up and subscribed before anyone publishes,
#    otherwise early messages have no consumer and can be dropped/unprocessed.
docker run -d --name consumer-service --restart always --network host \
  -e RABBITMQ_URL="amqp://${USER}:${PASS}@127.0.0.1:5672/" \
  "${CONSUMER_IMAGE}"

# 3. Producer last — safe to start only once the consumer is ready
docker run -d --name producer-service --restart always --network host \
  -e RABBITMQ_URL="amqp://${USER}:${PASS}@127.0.0.1:5672/" \
  "${PRODUCER_IMAGE}"
```

### 5. Concurrency Control

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false  # Don't cancel running deploys
```

### 6. Image Tagging Strategy

```bash
# Tag by service name (simple)
$ECR_REGISTRY/$ECR_REPOSITORY:webapp
$ECR_REGISTRY/$ECR_REPOSITORY:watcher
$ECR_REGISTRY/$ECR_REPOSITORY:download

# Tag by git SHA (for rollback)
$ECR_REGISTRY/$ECR_REPOSITORY:webapp-${{ github.sha }}

# Tag by date
$ECR_REGISTRY/$ECR_REPOSITORY:webapp-$(date +%Y%m%d-%H%M%S)
```

### 7. Blue-Green Deploy with Automatic Rollback

แทนที่จะ `docker restart` container เดิม (ซึ่งไม่ช่วยถ้า image ใหม่พังจริง ๆ) ให้ rename
container เดิมเก็บไว้เป็น `_previous`, รัน container ใหม่, health-check ด้วย polling loop,
แล้ว auto-rollback กลับไปใช้ `_previous` ถ้า health check ไม่ผ่าน:

```bash
wait_for_url() {
  local container="$1" url="$2" retries="$3"
  for i in $(seq 1 "${retries}"); do
    if [ "$(docker inspect -f '{{.State.Running}}' "${container}" 2>/dev/null)" != "true" ]; then
      return 1
    fi
    curl -fsS "${url}" >/dev/null 2>&1 && return 0
    sleep 3
  done
  return 1
}

deploy_with_rollback() {
  local name="$1" image="$2" health_url="$3"; shift 3
  local prev="${name}_previous"

  docker rm -f "${prev}" || true
  if docker inspect "${name}" >/dev/null 2>&1; then
    docker stop "${name}" >/dev/null
    docker rename "${name}" "${prev}"
  fi

  docker run -d --name "${name}" --restart always "$@" "${image}"

  if wait_for_url "${name}" "${health_url}" 15; then
    docker rm -f "${prev}" || true
  else
    docker logs --tail 200 "${name}" || true
    docker rm -f "${name}" || true
    if docker inspect "${prev}" >/dev/null 2>&1; then
      docker rename "${prev}" "${name}"
      docker start "${name}"
    fi
    return 1
  fi
}
```

## Advanced: Production-grade Pipeline

Pattern สำหรับ pipeline ที่มีหลาย services และต้องการ selective build (build เฉพาะ
service ที่เปลี่ยน), validate config ก่อนรัน, และ verify การ deploy อย่างละเอียด.

### 1. Validate Job — ตรวจ required Variables/Secrets ก่อนอะไรทั้งหมด

Fail fast ก่อนที่จะเสีย CI minutes ไปกับ build/deploy ที่จะพังเพราะ config ขาด รวมถึง
conditional-required (var A จำเป็นเฉพาะเมื่อ var B เป็นค่าใดค่าหนึ่ง) และ enum validation.

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Validate required config
        env:
          DEPLOY_TARGET: ${{ vars.DEPLOY_TARGET }}
          EC2_HOST: ${{ vars.EC2_HOST }}
          SFTP_HOST: ${{ vars.SFTP_HOST }}
        run: |
          set -euo pipefail
          missing=()

          # Always-required
          for name in AWS_ACCESS_KEY_ID AWS_REGION AWS_ACCOUNT_ID ECR_REPOSITORY DEPLOY_TARGET; do
            [ -z "${!name:-}" ] && missing+=("${name}")
          done

          # Conditional-required: SFTP_HOST only required when DEPLOY_TARGET=sftp
          if [ "${DEPLOY_TARGET}" = "sftp" ] && [ -z "${SFTP_HOST:-}" ]; then
            missing+=("SFTP_HOST (required when DEPLOY_TARGET=sftp)")
          fi

          if [ "${#missing[@]}" -gt 0 ]; then
            echo "Missing required vars/secrets:"
            printf '  - %s\n' "${missing[@]}"
            exit 1
          fi

          # Enum validation
          case "${DEPLOY_TARGET}" in
            ec2|sftp|ecs) ;;
            *)
              echo "DEPLOY_TARGET must be one of: ec2, sftp, ecs (got '${DEPLOY_TARGET}')"
              exit 1
              ;;
          esac
```

### 2. Detect-Services Job — selective/incremental multi-service build

Build เฉพาะ service ที่ source เปลี่ยน หรือ image ยังไม่มีใน ECR (first deploy). Diff
`before`/`current` SHA ด้วย `git diff`, fallback เป็น full tree เมื่อ `before` เป็น all-zero
(first push / force-push).

```yaml
  detect-services:
    needs: validate
    runs-on: ubuntu-latest
    outputs:
      watcher: ${{ steps.detect.outputs.watcher }}
      webapp: ${{ steps.detect.outputs.webapp }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ vars.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ vars.AWS_REGION }}

      - id: detect
        env:
          ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY }}
        run: |
          set -euo pipefail
          BEFORE="${{ github.event.before }}"
          if [ -z "${BEFORE}" ] || [ "${BEFORE}" = "0000000000000000000000000000000000000000" ]; then
            CHANGED="$(git ls-tree -r --name-only HEAD)"
          else
            CHANGED="$(git diff --name-only "${BEFORE}" "${{ github.sha }}" || git ls-tree -r --name-only HEAD)"
          fi

          for svc in watcher webapp; do
            BUILD="false"
            if echo "${CHANGED}" | grep -q "^services/${svc}/\|^${svc}/"; then
              BUILD="true"
            elif ! aws ecr describe-images --repository-name "${ECR_REPOSITORY}" \
                    --image-ids imageTag="${svc}" >/dev/null 2>&1; then
              BUILD="true"  # image missing in ECR — must build at least once
            fi
            echo "${svc}=${BUILD}" >> "${GITHUB_OUTPUT}"
          done
```

### 3. Matrix Build with Skippable Steps + Registry Layer Cache

`fail-fast: false` กัน matrix job หนึ่งพังแล้วยกเลิก job อื่น. ทุก step ที่แพง (checkout,
login, buildx, build) มี `if:` gate จาก output ของ `detect-services` เพื่อ skip ไปเลยถ้า
ไม่จำเป็น (ประหยัด CI minutes จริง ๆ ไม่ใช่แค่ skip logic ข้างในสคริปต์).

```yaml
  build:
    needs: detect-services
    strategy:
      fail-fast: false
      matrix:
        service: [watcher, webapp]
    runs-on: ubuntu-latest
    steps:
      - name: Determine whether build is required
        id: gate
        run: |
          echo "required=${{ needs.detect-services.outputs[matrix.service] }}" >> "${GITHUB_OUTPUT}"

      - name: Checkout Code
        if: steps.gate.outputs.required == 'true'
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        if: steps.gate.outputs.required == 'true'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ vars.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to Amazon ECR
        if: steps.gate.outputs.required == 'true'
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        if: steps.gate.outputs.required == 'true'
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        if: steps.gate.outputs.required == 'true'
        uses: docker/build-push-action@v6
        with:
          context: ./services/${{ matrix.service }}
          push: true
          tags: ${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ matrix.service }}
          cache-from: type=registry,ref=${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ matrix.service }}-cache
          cache-to: type=registry,ref=${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ matrix.service }}-cache,mode=max
```

### 4. Dependency-Ordered Job Graph — treat "skipped" as success, not a blocker

เมื่อ matrix job บาง service ไม่ build เลย (`skipped`) job ที่ต่อจากนั้นต้องไม่ถือว่านั่นคือ
ความล้มเหลว มีแค่ `success` ของ matrix ตัวที่ build จริงเท่านั้นที่ต้อง block.

```yaml
  deploy:
    needs: [build, detect-services]
    if: >
      always() &&
      needs.detect-services.result == 'success' &&
      (needs.build.result == 'success' || needs.build.result == 'skipped')
    runs-on: ubuntu-latest
    steps:
      # ...deploy steps...
```

### 5. Deploy Script Diagnostics — report exactly which phase failed

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

PHASE="init"
trap 'echo "[ERROR] Deploy failed during ${PHASE} at line ${LINENO}: ${BASH_COMMAND}"' ERR

PHASE="login ecr"
aws ecr get-login-password --region "${TARGET_REGION}" | docker login --username AWS --password-stdin "${REGISTRY}"

PHASE="pull images"
docker pull "${IMAGE}"

PHASE="deploy webapp"
deploy_with_rollback "myapp" "${IMAGE}" "http://127.0.0.1:3000/healthz" -p 3000:3000
```

### 6. Post-Deploy Final Verification

หลัง deploy ครบทุก service แล้ว ให้ loop เช็ค container ที่ต้อง running ทั้งหมด +
HTTP health endpoint ทั้งหมด แล้ว print ตารางสถานะ — hard-fail ถ้ามีตัวไหน down/unhealthy
(catch partial failure ที่ single "docker run สำเร็จ" เช็คไม่เจอ).

```bash
PHASE="post-deploy verification"
FAILED="false"

echo "container | status"
for c in myapp watcher rabbitmq; do
  if [ "$(docker inspect -f '{{.State.Running}}' "${c}" 2>/dev/null)" = "true" ]; then
    echo "${c} | UP"
  else
    echo "${c} | DOWN"
    FAILED="true"
  fi
done

echo "service | health | url"
declare -A HEALTH_URLS=(
  [webapp]="http://127.0.0.1:3000/healthz"
  [watcher]="http://127.0.0.1:3100/healthz"
)
for svc in "${!HEALTH_URLS[@]}"; do
  url="${HEALTH_URLS[${svc}]}"
  if curl -fsS "${url}" >/dev/null 2>&1; then
    echo "${svc} | HEALTHY | ${url}"
  else
    echo "${svc} | UNHEALTHY | ${url}"
    FAILED="true"
  fi
done

if [ "${FAILED}" = "true" ]; then
  echo "Post-deploy verification failed"
  exit 1
fi
```

## Required Secrets & Variables

### Secrets (encrypted)

| Secret | Purpose |
|--------|---------|
| `AWS_SECRET_ACCESS_KEY` | AWS authentication |
| `EC2_SSH_KEY` | SSH private key for EC2 |
| `AUTH_SECRET` | NextAuth/Auth.js secret |
| `AZURE_AD_CLIENT_SECRET` | Azure AD OAuth |
| `POSTGRES_PASSWORD` | Database password |
| `RABBITMQ_PASS` | RabbitMQ password |
| `SFTP_PASSWORD` | SFTP password |

### Variables (non-encrypted)

| Variable | Purpose |
|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS authentication |
| `AWS_REGION` | AWS region (e.g., ap-southeast-1) |
| `AWS_ACCOUNT_ID` | AWS account number |
| `ECR_REPOSITORY` | ECR repository name |
| `EC2_HOST` | EC2 public IP/hostname |
| `EC2_USER` | SSH username (e.g., ubuntu) |
| `PUBLIC_DOMAIN` | Production domain |
| `NEXT_PUBLIC_API_DATA_SOURCE` | API URL (public) |

## Best Practices

```
□ Smoke test ก่อน deploy production
□ trap cleanup credentials (security)
□ --restart always สำหรับ production containers
□ docker image prune -f --filter 'until=24h' หลัง deploy (เก็บ image ล่าสุดไว้ rollback มือได้เร็ว)
□ set -euo pipefail ทุก script (fail fast)
□ Concurrency control (ไม่ deploy ซ้อนกัน)
□ Rollback job เมื่อ deploy fail
□ แยก secrets (encrypted) กับ variables (non-encrypted)
□ Health check endpoint (/healthz) ใน app
□ Env file สำหรับ secrets (ไม่ใส่ใน docker run command)
```

## สรุป

1. **Build → Push → Deploy → Rollback** pipeline
2. **Smoke test** ก่อน swap production container
3. **Credential cleanup** ด้วย `trap` (security)
4. **Multi-service** — deploy infrastructure ก่อน, services ตามหลัง
5. **Concurrency** — ไม่ cancel running deploys
6. **Rollback** — automatic เมื่อ deploy job fails
7. **Image prune** — cleanup disk หลัง deploy
8. **`--restart always`** — containers restart อัตโนมัติ
