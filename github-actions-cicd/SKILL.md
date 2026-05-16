---
name: GitHub Actions CI/CD (AWS ECR + EC2)
description: CI/CD pipeline pattern for building Docker images, pushing to AWS ECR, deploying to EC2 via SSH with smoke testing, multi-service orchestration, and automatic rollback.
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
            trap 'rm -f ~/.aws/credentials' EXIT

            # 1. Login ECR
            mkdir -p ~/.aws
            printf "[default]\naws_access_key_id = %s\naws_secret_access_key = %s\n" \
              '${{ vars.AWS_ACCESS_KEY_ID }}' \
              '${{ secrets.AWS_SECRET_ACCESS_KEY }}' > ~/.aws/credentials

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

            # 4. Deploy production
            docker rm -f "${APP_CONTAINER}" || true
            docker run -d \
              --name "${APP_CONTAINER}" \
              --restart always \
              -p 3000:3000 \
              -e NODE_ENV=production \
              "${IMAGE}"

            # 5. Cleanup
            docker image prune -a -f
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
            # Restart previous container or pull previous tag
            docker restart "${APP_CONTAINER}" || true
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
# Always cleanup credentials even if script fails
trap 'rm -f ~/.aws/credentials "${ENV_FILE:-}"' EXIT

# Write temporary credentials
printf "[default]\naws_access_key_id = %s\naws_secret_access_key = %s\n" \
  '${ACCESS_KEY}' '${SECRET_KEY}' > ~/.aws/credentials
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

```bash
# Deploy infrastructure first (RabbitMQ, Redis, etc.)
docker run -d --name rabbitmq --restart always \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER="${USER}" \
  -e RABBITMQ_DEFAULT_PASS="${PASS}" \
  rabbitmq:3.13-management-alpine

# Then deploy services that depend on it
docker run -d --name watcher --restart always --network host \
  -e RABBITMQ_URL="amqp://${USER}:${PASS}@127.0.0.1:5672/" \
  "${WATCHER_IMAGE}"
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
□ docker image prune -a -f หลัง deploy (save disk)
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
