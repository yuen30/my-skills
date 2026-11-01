---
name: docker
description: "Building, running, and orchestrating containers with Docker and Docker Compose. Use when writing Dockerfiles, docker-compose.yml, multi-stage builds, healthchecks, volumes, networks, or debugging containers and images."
---

# Docker & Docker Compose

## Dockerfile

- Multi-stage always; final stage non-root (`USER app`, or distroless `:nonroot` for Go with `CGO_ENABLED=0`).
- Pin tags (no `latest` in prod); `COPY` over `ADD`; maintain `.dockerignore`.
- Layer order: dependency manifests -> install (`npm ci`, `go mod download`) -> source. Use BuildKit `--mount=type=cache` for package caches.
- Never put secrets in layers (`ARG`/`ENV`/`COPY .env`); use BuildKit `--mount=type=secret` or runtime secrets.
- Hardening: `cap_drop: [ALL]`, `read_only: true` where possible; scan with `docker scout`/`trivy`.
- Node pattern: builder runs `npm ci && npm run build`; final stage copies `dist`, `node_modules`, `package.json`, runs `CMD ["node", ...]` (exec form so signals reach the process).

## Compose

- `depends_on` with `condition: service_healthy` plus a healthcheck on the dependency (e.g. `pg_isready`) — plain `depends_on` doesn't wait for readiness.
- Named volumes for persistent data; explicit networks for isolation; pin image versions.
- Config via `.env`/env files, not hard-coded credentials; dev/prod split via `docker-compose.override.yml`.
- `restart: unless-stopped` for services.
- Validate with `docker compose config` after edits.
- `docker compose down -v` and `docker system prune -af` are destructive (delete volumes/all unused images) — confirm first.
