---
name: github-action-ecr
description: CI/CD pipeline using GitHub Actions + ECR + EC2. Builds and pushes per-service Docker images to a single ECR repo with service-specific tags, then deploys via SSH with `docker run`. Designed for TOA E-Ordering monorepo. WHEN: "ECR deploy", "GitHub Actions ECR", "CI/CD ECR", "build ECR image", "deploy to EC2 via ECR", "push to ECR", "single ECR repo multiple tags", "per-service tags", "GitHub Actions SSH deploy".
---

# GitHub Actions ECR Deployment

## Architecture

- **Single ECR repo** (`ECR_REPOSITORY`) with **per-service tags** (`:webapp`, `:watcher`, `:download`, `:generate`, `:upload`).
- **No unique commit tags** — only `:latest` per service; rollback relies on previous image still being cached or re-pulled.
- **EC2 host** via `appleboy/ssh-action` with inline `-e` env vars (no temp env file).
- **Go microservices** use `--network host` to reach RabbitMQ on `127.0.0.1:5672`.
- **RabbitMQ** (`rabbitmq:3.13-management-alpine`) runs as a Docker container on the same EC2.

## Required GitHub Vars

### AWS / Host
| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM access key (var, not secret — used in script) |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key (secret) |
| `AWS_REGION` | e.g. `ap-southeast-1` |
| `AWS_ACCOUNT_ID` | 12-digit account ID |
| `ECR_REPOSITORY` | Single repo name, e.g. `test_ecr_image` |
| `EC2_HOST` | Public IP or DNS of EC2 |
| `EC2_USER` | SSH user (e.g. `ec2-user`) |
| `EC2_SSH_KEY` | SSH private key (secret) |

### Webapp
| Variable | Description |
|----------|-------------|
| `PUBLIC_DOMAIN` | e.g. `eorder.example.com` |
| `NEXT_PUBLIC_API_DATA_SOURCE` | `mock` or `api` |
| `ORDERING_API_BASE_URL` | Backend API base URL |
| `NEXT_PUBLIC_INTERNAL_API_URL` | Internal API URL |

### RabbitMQ
| Variable | Description |
|----------|-------------|
| `RABBITMQ_USER` | RabbitMQ user (var) |
| `RABBITMQ_PASS` | RabbitMQ password (secret) |

### PostgreSQL
| Variable | Description |
|----------|-------------|
| `POSTGRES_HOST` | RDS endpoint |
| `POSTGRES_USER` | DB user |
| `POSTGRES_DB` | DB name |
| `POSTGRES_PASSWORD` | DB password (secret) |

### SFTP
| Variable | Description |
|----------|-------------|
| `SFTP_HOST` | SFTP server hostname |
| `SFTP_PORT` | Usually `22` |
| `SFTP_USERNAME` | SFTP user |
| `SFTP_PASSWORD` | SFTP password (secret) |

### Per-Service Vars

| Service | Vars |
|---------|------|
| watcher | `WATCHER_PATHS` |
| download | `DOWNLOAD_SOURCE_ROOT`, `ARCHIVE_ROOT`, `DOWNLOAD_FLOW_FOLDER`, `DOWNLOAD_REMOTE_ARCHIVE_ROOT` |
| generate | `GENERATE_FLOW_FOLDER`, `GENERATE_REMOTE_ROOT` |
| upload | `UPLOAD_FLOW_FOLDER`, `UPLOAD_REMOTE_ROOT` |

## Workflow Structure

```
jobs:
  build-and-push:      # Build + push all images
    steps:
      - Checkout
      - Configure AWS credentials
      - Login to ECR
      - Build/Push: webapp, watcher, download, generate, upload

  deploy:              # SSH into EC2, pull images, docker run
    needs: build-and-push
    steps:
      - SSH to EC2 via appleboy/ssh-action
      - Login ECR on EC2
      - Docker run: rabbitmq (if not running)
      - Docker run: watcher, download, generate, upload (--network host)
      - Docker run: webapp (port 3000, --env-file for auth secrets)
      - Prune old images

  rollback:            # On deploy failure
    needs: deploy
    if: failure()
    steps:
      - SSH + rollback webapp only
```

## Deploy Patterns

### Go Microservice (e.g. watcher)
```yaml
docker run -d \
  --name e_ordering_watcher \
  --restart always \
  --network host \
  -e SERVICE_NAME=sftp-watcher \
  -e SERVICE_HTTP_ADDR=:8080 \
  -e RABBITMQ_URL="amqp://${RABBITMQ_USER}:${RABBITMQ_PASS}@127.0.0.1:5672/" \
  -e POSTGRES_HOST="${POSTGRES_HOST}" \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -e SFTP_HOST="${SFTP_HOST}" \
  -e SFTP_PORT="${SFTP_PORT}" \
  -e SFTP_USERNAME="${SFTP_USERNAME}" \
  -e SFTP_PASSWORD="${SFTP_PASSWORD}" \
  -e SFTP_STRICT_HOST_KEY=false \
  -e WATCHER_PATHS="${WATCHER_PATHS}" \
  "${IMAGE_URI}"
```

### Webapp (port mapping + auth file)
```yaml
docker run -d \
  --name e_ordering_vn \
  --restart always \
  -p 3000:3000 \
  --env-file /tmp/eorder_auth.env \
  -e NEXTAUTH_URL="https://${PUBLIC_DOMAIN}" \
  -e NEXT_PUBLIC_API_DATA_SOURCE="${NEXT_PUBLIC_API_DATA_SOURCE}" \
  "${IMAGE_URI}"
```

### RabbitMQ
```yaml
docker run -d \
  --name e_ordering_rabbitmq \
  --restart always \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER="${RABBITMQ_USER}" \
  -e RABBITMQ_DEFAULT_PASS="${RABBITMQ_PASS}" \
  -v rabbitmq_data:/var/lib/rabbitmq \
  rabbitmq:3.13-management-alpine
```

## Critical Details

- **`SFTP_STRICT_HOST_KEY=false`** is set because no `SFTP_KNOWN_HOSTS` is configured. Do not use in production without known hosts.
- **`--network host`** for Go services so they can reach RabbitMQ on localhost without Docker DNS.
- **Auth secrets** (`AUTH_SECRET`, `AZURE_AD_CLIENT_SECRET`) are written to a temp file via heredoc and passed with `--env-file`. This avoids exposing secrets in the process list.
- **Rollback** only covers `webapp`. Other services are not rolled back.
- **Image prune** `docker image prune -a -f` runs at end of deploy to reclaim disk space.
- **SSM is avoided** — env vars passed directly via GitHub vars/secrets to avoid IAM `ssm:GetParameter` permission issues.
