## Local Development

### Full-Stack in Docker Compose

```bash
# 1. Copy and edit .env
cp .env.compose.example .env

# 2. Prepare archive directory
mkdir -p data/archive

# 3. Start all services
docker compose up -d --build

# 4. Validate config
docker compose config

# 5. View logs
docker compose logs -f webapp
docker compose logs -f download
```

**Services in Compose:**
- `webapp` (Next.js 16, port 3000)
- `rabbitmq` (RabbitMQ, port 5672)
- `watcher` (Go service)
- `download` (Go service)
- `notify` (Go service)
- `healthchecker` (Go service)

**Note:** PostgreSQL is external — configure via `POSTGRES_*` environment variables in `.env`. It is not started by docker-compose.yml. If you need a local PostgreSQL:
```bash
# Option 1: Run locally on host
brew install postgresql@15
pg_createdb -U postgres myapp_dev

# Option 2: Use separate container
docker run -d -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
```

### Host-Side Fallback (When SFTP Not Reachable from Containers)

If SFTP is on the host but containers cannot reach it (network issues), run services on the host:

```bash
# 1. Start only RabbitMQ in Docker
docker compose up -d rabbitmq

# 2. Start Go services on host (logged to .logs/)
bash scripts/run-local-services.sh

# Logs appear in:
# .logs/watcher.log
# .logs/download.log
# .logs/notify.log
# .logs/healthchecker.log
```

Ensure `RABBITMQ_URL` points to `localhost:5672` in `.env.local`.

### Webapp Commands (from `webapp/`)

```bash
# Using Bun (required runtime)
bun install
bun run dev          # dev server with Turbopack
bun run build        # webpack build (NOT turbopack for production)
bun run lint         # ESLint + Prettier
bun run typecheck    # tsc --noEmit
bun run test:e2e     # Playwright E2E tests
```

### Go Services Commands

```bash
# Test shared infrastructure
go test ./shared/common/...

# Test specific service
go test ./services/download/...

# Build service
go build -o dist/download ./services/download

# Run service locally
POSTGRES_URL=... RABBITMQ_URL=... ./dist/download
```
