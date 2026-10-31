---
name: github-actions-cicd
description: "GitHub Actions (.github/workflows) pipeline to build Docker images, push to AWS ECR, deploy to EC2 over SSH with smoke test and auto-rollback. Use when writing GitHub Actions workflows, ECR/EC2 deploys, matrix builds, or rollback jobs."
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

See [references/workflow-template.md](references/workflow-template.md) — read when writing or editing the full build/push/deploy workflow YAML.

## Key Patterns

See [references/key-patterns.md](references/key-patterns.md) — read when you need smoke tests, credential cleanup, env files, multi-service ordering, concurrency, image tagging, or blue-green rollback.

## Advanced: Production-grade Pipeline

See [references/production-pipeline.md](references/production-pipeline.md) — read when you need config validation, selective/matrix builds with registry cache, dependency-gated jobs, deploy diagnostics, or post-deploy verification.

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
