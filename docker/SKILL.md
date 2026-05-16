# Docker & Docker Compose

Expert guidance for building, running, and orchestrating containers with Docker and Docker Compose.

## Capabilities

- Write optimized, multi-stage Dockerfiles
- Configure Docker Compose services for development and production
- Implement health checks, networking, volumes, and secrets
- Troubleshoot container issues (build failures, networking, permissions)
- Apply security best practices (non-root users, minimal base images, layer caching)

## Guidelines

### Dockerfile Best Practices

- Use specific image tags (avoid `latest` in production)
- Order layers from least to most frequently changed for cache efficiency
- Use multi-stage builds to reduce final image size
- Run as non-root user
- Use `.dockerignore` to exclude unnecessary files
- Combine RUN commands to reduce layers
- Use `COPY` over `ADD` unless extracting archives

### Docker Compose Best Practices

- Use named volumes for persistent data
- Define explicit networks for service isolation
- Use `depends_on` with health checks for startup ordering
- Separate override files for dev vs production (`docker-compose.override.yml`)
- Use environment variable files (`.env`) for configuration
- Pin image versions in compose files

### Security

- Scan images for vulnerabilities (`docker scout`, `trivy`)
- Never store secrets in image layers — use build secrets or runtime secrets
- Limit container capabilities with `cap_drop: ALL`
- Use read-only filesystem where possible (`read_only: true`)

### Performance

- Leverage BuildKit for parallel builds and cache mounts
- Use `--mount=type=cache` for package manager caches
- Keep images small — prefer `alpine` or `distroless` base images
- Use `.dockerignore` aggressively

## Example Dockerfile (Multi-stage, Go)

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server .

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app/server /server
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/server"]
```

## Example Dockerfile (Node.js)

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
USER app
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## Example docker-compose.yml

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

## Common Commands

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start services in background |
| `docker compose down -v` | Stop and remove volumes |
| `docker compose logs -f <service>` | Follow logs |
| `docker compose exec <service> sh` | Shell into container |
| `docker build --no-cache .` | Build without cache |
| `docker system prune -af` | Clean up everything |
| `docker compose config` | Validate compose file |
