---
name: ci-cd
description: "CI/CD pipelines that build Docker images, push to AWS ECR and deploy to EC2 or ECS with smoke test and rollback. Use when editing .github/workflows, bitbucket-pipelines.yml, or ECR/EC2/ECS deploy, matrix builds, pipes, or rollback jobs."
---

# CI/CD (AWS ECR + EC2/ECS)

Pipeline pattern for building Docker images, pushing to AWS ECR, deploying to EC2 (SSH) or ECS (service update), with smoke testing, multi-service ordering and automatic rollback. Same shape on GitHub Actions and Bitbucket Pipelines.

## 1. Detect the provider

| Found in repo | Read |
|---|---|
| `.github/workflows/` | GitHub files below |
| `bitbucket-pipelines.yml` | [references/bitbucket.md](references/bitbucket.md) (includes Bitbucket vs GitHub Actions comparison) |

GitHub references:
- [references/github-workflow-template.md](references/github-workflow-template.md) - read when writing or editing the full build/push/deploy workflow YAML.
- [references/github-key-patterns.md](references/github-key-patterns.md) - read for smoke tests, credential cleanup, env files, multi-service ordering, concurrency, image tagging, or blue-green rollback.
- [references/github-production-pipeline.md](references/github-production-pipeline.md) - read for config validation, selective/matrix builds with registry cache, dependency-gated jobs, deploy diagnostics, or post-deploy verification.

## 2. Pipeline architecture (provider-agnostic)

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
│   ├── EC2: SSH, pull new images  |  ECS: update service with new image
│   ├── Smoke test (health check)
│   ├── Deploy RabbitMQ
│   ├── Deploy microservices (watcher, download, generate, upload)
│   ├── Deploy webapp (production)
│   └── Cleanup old images
│
└── Job 3: rollback (if deploy fails)
    ├── EC2: SSH, restart with previous image  |  ECS: redeploy previous task definition
    └── Bitbucket: also exposed as a custom manual pipeline
```

## 3. Required secrets and variables

Keep secrets encrypted; keep non-secret config as plain variables (GitHub: Secrets vs Variables; Bitbucket: Repository/Deployment variables, mark secrets "Secured").

| Name | Type | Purpose | Provider |
|---|---|---|---|
| `AWS_SECRET_ACCESS_KEY` | secret | AWS authentication | both |
| `EC2_SSH_KEY` | secret | SSH private key for EC2 | both (EC2) |
| `AUTH_SECRET` | secret | NextAuth/Auth.js secret | GitHub template |
| `AZURE_AD_CLIENT_SECRET` | secret | Azure AD OAuth | GitHub template |
| `POSTGRES_PASSWORD` | secret | Database password | GitHub template |
| `RABBITMQ_PASS` | secret | RabbitMQ password | GitHub template |
| `SFTP_PASSWORD` | secret | SFTP password | GitHub template |
| `AWS_ACCESS_KEY_ID` | variable | AWS authentication | both |
| `AWS_REGION` | variable | AWS region (e.g., ap-southeast-1) | both |
| `AWS_ACCOUNT_ID` | variable | AWS account number | both |
| `ECR_REPOSITORY` | variable | ECR repository name | both |
| `EC2_HOST` | variable | EC2 public IP/hostname | both (EC2) |
| `EC2_USER` | variable | SSH username (e.g., ubuntu) | both (EC2) |
| `ECS_CLUSTER`, `ECS_SERVICE` | variable | ECS target | Bitbucket (ECS) |
| `PUBLIC_DOMAIN` | variable | Production domain | GitHub template |
| `NEXT_PUBLIC_API_DATA_SOURCE` | variable | API URL (public) | GitHub template |

## 4. Best practices

```
□ Smoke test ก่อน deploy production
□ trap cleanup credentials (security)
□ --restart always สำหรับ production `docker run` ใน pipeline (compose ใช้ `unless-stopped`, ดู docker)
□ docker image prune -f --filter 'until=24h' หลัง deploy (เก็บ image ล่าสุดไว้ rollback มือได้เร็ว)
□ set -euo pipefail ทุก script (fail fast)
□ Concurrency control (ไม่ deploy ซ้อนกัน)
□ Rollback job เมื่อ deploy fail
□ แยก secrets (encrypted) กับ variables (non-encrypted)
□ Health check endpoint (/healthz) ใน app
□ Env file สำหรับ secrets (ไม่ใส่ใน docker run command)
□ Tag images by commit SHA (not only :latest) so rollback has a target
□ Keep smoke-test/rollback logic in a host script; the pipeline just invokes it
```
