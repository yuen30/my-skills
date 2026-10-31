## Project Initialization Checklist

When starting a new project with this scaffold:

### Phase 1: Monorepo & Infra Setup

- [ ] Create `webapp/`, `services/`, `shared/common/` directories
- [ ] Init Next.js 16 App Router in `webapp/` (Bun runtime)
- [ ] Init Go modules in each service and `shared/common/`
- [ ] Create `docker-compose.yml` with RabbitMQ, PostgreSQL (or external), Webapp, and one placeholder Go service
- [ ] Create `.env.compose.example` template (all required env vars documented)
- [ ] Add `Dockerfile` to `webapp/` and each service (`services/*/Dockerfile`)
- [ ] Set up `.gitignore` (exclude `node_modules/`, `.env`, `.logs/`, `data/`, `dist/`)
- [ ] Add `README.md` with setup commands, architecture diagram, and link to this skill

### Phase 2: Layered Architecture Enforcement

**Next.js:**
- [ ] Establish `app/[locale]/...` routing with locale middleware in `proxy.ts`
- [ ] Create `components/ui/` and `hooks/` directories
- [ ] Create `lib/api/adapters/{mock,real}` with shared interface
- [ ] Add `lib/helpers/` for pure functions
- [ ] Add `types/` for shared TS contracts
- [ ] ESLint rule: forbid `any` type
- [ ] Add path alias `@/*` in `tsconfig.json` and `next.config.ts`

**Go Services:**
- [ ] Establish `services/<name>/internal/app/` composition root pattern
- [ ] Create minimal `shared/common/{config,logger,store,mq,sftpclient,models}/`
- [ ] Add shared `Config` struct in `shared/common/config/`
- [ ] Set up RabbitMQ topic/queue topology in `shared/common/mq/`
- [ ] Define shared domain models in `shared/common/models/`
- [ ] No duplicate config loaders, MQ clients, or ORM instances across services

### Phase 3: API Adapter Switchboard

- [ ] Implement mock adapter with realistic data and behavior (filters, sorts, etc.)
- [ ] Implement real adapter talking to backend (or stub it for later)
- [ ] Create `lib/api/client.ts` that selects adapter based on `NEXT_PUBLIC_API_DATA_SOURCE` env var
- [ ] Add `NEXT_PUBLIC_API_DATA_SOURCE` to `.env.local` and `.env.example` (default: `mock`)
- [ ] Document in README: how to switch adapters, what mock data is available

### Phase 4: Local Development

- [ ] Create `docker-compose.yml` with compose services for all backend
- [ ] Add `scripts/run-local-services.sh` for host-side fallback
- [ ] Create `.env.compose.example` (template for `.env`)
- [ ] Document startup steps in README: `docker compose up -d`, app available at `http://localhost:3000`
- [ ] Test full-stack flow: webapp → adapter → backend (or mock if using mock adapter)

### Phase 5: CI/CD & Verification

- [ ] Add GitHub Actions workflow: lint/typecheck/build webapp
- [ ] Add GitHub Actions workflow: go test, docker build
- [ ] Document verification commands in README (or reference AGENTS.md)
- [ ] Set up linting, type-checking, e2e test runs in CI

### Phase 6: Documentation

- [ ] Update `AGENTS.md` with:
  - Architecture boundaries (webapp, services, shared, deploy)
  - Critical constraints (locale routing, env vars, adapter switch, external PostgreSQL)
  - Coding rules (no `any`, guard clauses, layer boundaries)
  - Verification commands (bun run lint/build, go test, docker compose config)
- [ ] Update `CLAUDE.md` with:
  - Project description (two parts: Next.js storefront + Go microservices)
  - Commands (bun install, go test, docker compose up -d)
  - Architecture overview (watcher/download/notify pipeline, adapter switch)
  - Conventions (ULIDs, TypeScript no-any, env vars, PostgreSQL external)
- [ ] Keep `webapp/AGENTS.md` with layer-specific rules and verification
