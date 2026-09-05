---
name: Bitbucket Pipelines CI/CD (AWS ECR + EC2/ECS)
description: Bitbucket Pipelines CI/CD — bitbucket-pipelines.yml structure (pipelines/branches/custom, steps, caches, artifacts, services), deploying to AWS (ECR login + push, EC2 via SSH pipe, ECS service update), Bitbucket Deployments (staging/production environments with required approvals), and a comparison against GitHub Actions for choosing the right platform per repo.
---

# Bitbucket Pipelines CI/CD (AWS ECR + EC2/ECS)

CI/CD pattern for repos hosted on Bitbucket, building Docker images, pushing to
AWS ECR, and deploying to EC2 (via SSH) or ECS (via service update).

## `bitbucket-pipelines.yml` Structure

```yaml
image: atlassian/default-image:4

definitions:
  caches:
    docker-layer: /var/lib/docker
  services:
    docker:
      memory: 3072

pipelines:
  default:
    - step:
        name: Lint & Test
        image: node:22-alpine
        caches: [node]
        script:
          - npm ci
          - npm run lint
          - npm test

  branches:
    dev:
      - step:
          name: Build & Push to ECR
          services: [docker]
          script:
            - pipe: atlassian/aws-ecr-push-image:2.4.0
              variables:
                AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
                AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
                AWS_DEFAULT_REGION: $AWS_REGION
                IMAGE_NAME: $ECR_REPOSITORY
                TAGS: "dev-${BITBUCKET_COMMIT}"
      - step:
          name: Deploy to EC2 (dev)
          deployment: staging
          script:
            - pipe: atlassian/ssh-run:0.9.0
              variables:
                SSH_USER: $EC2_USER
                SERVER: $EC2_HOST
                SSH_KEY: $EC2_SSH_KEY
                COMMAND: "bash /opt/deploy/deploy.sh dev-${BITBUCKET_COMMIT}"

  custom:
    manual-rollback:
      - step:
          name: Rollback
          deployment: production
          script:
            - pipe: atlassian/ssh-run:0.9.0
              variables:
                SSH_USER: $EC2_USER
                SERVER: $EC2_HOST
                SSH_KEY: $EC2_SSH_KEY
                COMMAND: "bash /opt/deploy/rollback.sh"
```

### Key sections

| Section | Purpose |
|---|---|
| `pipelines.default` | Runs on every push to any branch not otherwise matched — typically lint/test only |
| `pipelines.branches.<name>` | Runs only on pushes to a specific branch (e.g. `dev`, `main`) — build/deploy |
| `pipelines.pull-requests.<pattern>` | Runs on PR events — validation without deploy |
| `pipelines.custom.<name>` | Manually triggered from the Bitbucket UI/API — rollback, one-off jobs |
| `definitions.caches` | Named cache dirs reused across pipeline runs (dependency caches, Docker layer cache) |
| `definitions.services` | Sidecar services available to a step (`docker` for `docker build`, or `postgres`/`redis` for integration tests) |
| `artifacts` | Files produced by one step and made available to a later step in the same pipeline |

### Artifacts between steps

```yaml
- step:
    name: Build
    script:
      - npm run build
    artifacts:
      - dist/**
- step:
    name: Deploy
    script:
      - ls dist/ # available here, built in the previous step
```

## Deploying to AWS

### 1. ECR login + build/push (raw Docker, no pipe)

```yaml
- step:
    name: Build & Push
    services: [docker]
    script:
      - pipe: atlassian/aws-ecr-push-image:2.4.0
        variables:
          AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
          AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
          AWS_DEFAULT_REGION: $AWS_REGION
          IMAGE_NAME: $ECR_REPOSITORY
          TAGS: "${BITBUCKET_COMMIT}"
```

Or without the pipe, for finer control over the Dockerfile/build-args:

```yaml
script:
  - pipe: atlassian/aws-ecr-push-image:2.4.0 # login only pattern alternative:
  - export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
  - aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
  - docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$BITBUCKET_COMMIT .
  - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$BITBUCKET_COMMIT
```

### 2. Deploy to EC2 via SSH pipe

```yaml
- step:
    name: Deploy to EC2
    deployment: production
    script:
      - pipe: atlassian/ssh-run:0.9.0
        variables:
          SSH_USER: $EC2_USER
          SERVER: $EC2_HOST
          SSH_KEY: $EC2_SSH_KEY
          COMMAND: >
            docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$BITBUCKET_COMMIT &&
            bash /opt/deploy/deploy.sh $BITBUCKET_COMMIT
```

Keep the actual smoke-test/blue-green rollback logic in a script on the host
(`/opt/deploy/deploy.sh`), same pattern as the GitHub Actions equivalent in
`github-actions-cicd/SKILL.md` — `ssh-run` just invokes it remotely.

### 3. Deploy to ECS via service update

```yaml
- step:
    name: Deploy to ECS
    deployment: production
    script:
      - pipe: atlassian/aws-ecs-deploy:1.13.0
        variables:
          AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
          AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
          AWS_DEFAULT_REGION: $AWS_REGION
          CLUSTER_NAME: $ECS_CLUSTER
          SERVICE_NAME: $ECS_SERVICE
          IMAGE_NAME: "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$BITBUCKET_COMMIT"
          FORCE_NEW_DEPLOYMENT: "true"
```

Or raw AWS CLI when you need to update a specific container definition rather
than the whole task:

```bash
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $ECS_SERVICE \
  --force-new-deployment
```

## Bitbucket Deployments — Environments & Approvals

`deployment: staging` / `deployment: production` on a step ties it to a named
Bitbucket **Deployment environment**, which supports:

- Environment-scoped variables/secrets (`Repository settings → Deployments`) —
  separate `AWS_ACCESS_KEY_ID` per environment instead of one global secret.
- **Required reviewers / manual approval gates** before a deployment step runs
  (`Repository settings → Deployments → production → Enable deployment
  permissions`) — a human must approve in the UI before the step executes.
- Deployment history/dashboard (`Repository → Deployments` tab) showing what
  was deployed where and when, separate from raw pipeline run history.

```yaml
- step:
    name: Deploy to Production
    deployment: production   # ties to the "production" environment + its variables/approvals
    trigger: manual          # extra gate: pipeline pauses until manually triggered in UI
    script:
      - pipe: atlassian/aws-ecs-deploy:1.13.0
        variables: { ... }
```

`trigger: manual` and Deployment environment approval are two independent gates
— use `trigger: manual` for "someone must click Run", and environment approval
for "a specific approver role must sign off," and combine both for production.

## Comparison: Bitbucket Pipelines vs GitHub Actions

| Aspect | Bitbucket Pipelines | GitHub Actions |
|---|---|---|
| Config file | `bitbucket-pipelines.yml` (repo root) | `.github/workflows/*.yml` |
| Reusable steps | "Pipes" (`atlassian/aws-ecr-push-image`, etc.) — Bitbucket/Atlassian-maintained marketplace | "Actions" — much larger community marketplace (`aws-actions/*`, `docker/*`) |
| Branch/PR triggers | `branches`, `pull-requests`, `tags`, `custom` blocks | `on: push/pull_request` with `branches`/`paths` filters |
| Environments/approvals | Built-in Deployments (environment-scoped vars + required reviewers) | `environments:` with required reviewers (similar concept, different config surface) |
| Matrix builds | Supported via `matrix` (parallel steps), less mature than Actions matrix | Native `strategy.matrix`, well-documented, used heavily in `github-actions-cicd/SKILL.md` |
| Concurrency control | `pipelines` run per-branch by default; concurrency groups less explicit | `concurrency:` key — precise group + `cancel-in-progress` control |
| Self-hosted runners | "Runners" (self-hosted), fewer built-in OS/arch options | Self-hosted runners, broad OS/arch matrix, wider ecosystem |
| Best fit | Teams already on Bitbucket/Jira, simpler pipelines, tight environment/approval needs | Teams on GitHub, complex multi-service pipelines (selective builds, matrix, heavy conditional job graphs) — see `github-actions-cicd/SKILL.md` for the validate/detect-services/rollback pattern |

Both platforms can express the same validate → build → deploy → rollback shape;
choose based on where the repo is hosted, not feature superiority — migrate the
concepts (fail-fast validation, smoke test before swap, DLX-style rollback job),
not a 1:1 YAML port.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Docker build fails with no daemon | Missing `services: [docker]` on the step |
| Secrets visible in logs | Use `Repository variables` marked "Secured", never `echo` them directly |
| Deploy step runs without approval | Forgot to enable "deployment permissions" on the environment in repo settings |
| Stale image cached across builds | `definitions.caches.docker-layer` persists `/var/lib/docker` — bust it via cache key change if a base image update isn't picked up |
| Pipeline never deploys `main` | `pipelines.branches` block name must exactly match the branch (or use `pipelines.tags`/`custom` for other triggers) |

## สรุป

1. `pipelines.default` = lint/test on every push; `pipelines.branches.<name>` = build/deploy per branch; `pipelines.custom` = manual jobs (rollback)
2. Use Atlassian pipes (`aws-ecr-push-image`, `ssh-run`, `aws-ecs-deploy`) for common AWS steps, or raw `aws`/`docker` CLI for finer control
3. `deployment: staging|production` ties a step to a Bitbucket Deployment environment — gives environment-scoped secrets + optional required-approval gate
4. Combine `trigger: manual` + environment approval for production deploys needing a human sign-off
5. Same validate → build → deploy → rollback shape as GitHub Actions — pick the platform by where the repo lives, port the pattern not the YAML syntax
6. `services: [docker]` required on any step running `docker build`
