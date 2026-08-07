---
name: Monorepo Scaffold — Next.js App Router + Go Microservices
description: Proven template for Next.js 16+ (React, TypeScript, Bun) storefront + Admin with Go 1.20+ microservices sharing cross-cutting infrastructure, featuring swappable API adapters (mock/real), Docker Compose full-stack local dev, and strict layered dependency rules.
---

# Monorepo Scaffold: Next.js App Router + Go Microservices

Template for a production-grade monorepo combining:
- **Next.js 16+ App Router** storefront and admin with React 19, TypeScript, Bun, Tailwind, shadcn/ui
- **Go 1.20+ microservices** (watcher, download, notify, healthchecker examples) coordinating via RabbitMQ into PostgreSQL
- **Shared Go infrastructure** (`shared/common/`) for config, MQ, SFTP client, database/ORM, logging, metrics — reused across all services, never duplicated
- **Swappable API adapters** (mock/real) for feature development before backend is ready
- **Docker Compose** local dev with fallback to host-side services when containers cannot reach SFTP
- **Strict layered architecture** with dependency direction rules enforced from day one

## Layout

```
project-root/
├── webapp/                          # Next.js 16+ App Router (React 19, TS, Bun)
│   ├── app/                         # App Router routes + layouts
│   │   ├── [locale]/                # Locale-prefixed routes (/en, /th, /vi if i18n)
│   │   │   ├── (public)/            # Unauthenticated routes
│   │   │   ├── (auth)/              # Auth-required routes
│   │   │   └── layout.tsx           # Root layout per locale
│   │   └── api/                     # Route handlers (thin proxy/delivery)
│   ├── components/
│   │   ├── ui/                      # Shared shadcn/ui primitives (Button, Card, etc.)
│   │   └── feature-*/               # Feature-specific compound components
│   ├── hooks/                       # Client state, browser orchestration (use client)
│   ├── providers/                   # React context providers
│   ├── lib/
│   │   ├── api/
│   │   │   └── adapters/
│   │   │       ├── mock/            # Mock adapter (behavior-equiv to real)
│   │   │       └── real/            # Real backend adapter
│   │   ├── auth/                    # Auth orchestration, next-auth config
│   │   ├── types/                   # Shared TS types, DTOs, contracts
│   │   └── helpers/                 # Pure functions (no framework, no side effects)
│   ├── helpers/                     # Reusable pure logic (no framework)
│   ├── types/                       # Shared TypeScript types
│   ├── i18n/                        # Locale routing config
│   ├── messages/                    # Translation files ({en,th,vi}.json)
│   ├── tests/                       # E2E tests (Playwright)
│   ├── auth.ts                      # next-auth configuration
│   ├── proxy.ts                     # Middleware: route guards, redirects, locale preservation
│   ├── next.config.ts               # Build config, rewrites, API exceptions
│   ├── Dockerfile                   # Container image
│   └── package.json / bunfig.toml   # Dependencies, bun config
│
├── services/                        # Go microservices
│   ├── watcher/                     # Example: monitors SFTP directory
│   │   └── internal/app/            # Composition root, wiring
│   ├── download/                    # Example: fetches and parses files
│   │   └── internal/app/            # Composition root, wiring
│   ├── notify/                      # Example: sends notifications
│   │   └── internal/app/            # Composition root, wiring
│   └── healthchecker/               # Example: periodic health checks
│       └── internal/app/            # Composition root, wiring
│
├── shared/
│   └── common/                      # Cross-cutting infrastructure (used by all services)
│       ├── config/                  # Environment & config loading
│       ├── logger/                  # Logging abstraction
│       ├── store/                   # Database/ORM (GORM) with shared models
│       ├── mq/                      # RabbitMQ client & topology (single instance)
│       ├── sftpclient/              # SFTP client (single instance)
│       ├── metrics/                 # Observability, prometheus
│       ├── jobs/                    # Job scheduling, retries
│       └── models/                  # Shared domain models across services
│
├── deploy/                          # Deployment & observability config
│   ├── docker-compose.yml           # Full-stack local dev orchestration
│   └── ...                          # K8s manifests, Helm charts, etc.
│
├── .github/workflows/               # CI/CD pipelines
├── .env.compose.example             # Docker Compose template (copy to .env)
├── .env.local.example               # Local host-side dev (Go services on host)
├── docker-compose.yml               # Full-stack orchestration
└── README.md                        # Setup, commands, architecture overview
```

## Next.js Webapp Layer Boundaries

### Presentation / Delivery (`app/`, `components/`, `handlers`)

- **Routes** (`app/[locale]/...`): thin orchestrators. Validate boundary input, invoke a hook/action, pass result to component.
- **Pages** (`page.tsx`, `layout.tsx`): server-side by default. Add `"use client"` only at smallest scope needing state/effects/browser APIs.
- **Route Handlers** (`app/api/...`): thin proxies. Parse request, call adapter client, map response, return HTTP.
- **Components** (`components/`): reusable presentation. Do NOT fetch from backend directly; accept data via props. Do NOT contain business rules.
- **Shared UI** (`components/ui/`): shadcn/ui primitives, no logic.

**Dependency:** app → components → hooks/lib; components never call adapters directly.

### Application / Use Cases (`hooks/`, `lib/auth/`, `lib/api/adapters/`)

- **Hooks** (`use*.ts`): client-side orchestration. Fetch via adapter, manage UI state, coordinate side effects.
- **Auth** (`lib/auth/`): auth flows, session, next-auth glue, customer login logic.
- **API Adapters** (`lib/api/adapters/{mock,real}`): **Single source of truth** for backend communication. Fetch/mutation logic, response normalization, error mapping. Both mock and real must be behavior-equivalent (same filtering, sorting, pagination, error codes, response shape).

**Adapter Selection by Environment:**
```typescript
// lib/api/client.ts (or similar)
const dataSource = process.env.NEXT_PUBLIC_API_DATA_SOURCE || "mock"; // "mock" | "real"
export const apiClient = dataSource === "real" ? realAdapter : mockAdapter;
```

### Domain / Helpers (`lib/helpers/`, `types/`)

- **Helpers** (`lib/helpers/`): pure functions. No framework, no ORM, no HTTP. String formatting, calculation, transformation.
- **Types** (`types/`): shared TypeScript contracts, DTOs, validation schemas.

**No dependency on outer layers.**

### Server-Only (`lib/auth/customer-login.ts`, auth.ts, etc.)

- Secrets, unrestricted backend responses, credentials.
- Never leak to Client Components via props.

### Routing & Internationalization

- **All user-facing routes** must include locale prefix: `/en/...`, `/th/...`, `/vi/...` (or whichever locales are supported).
- **Preserve locale in links and redirects** — always use `href="/[locale]/path"` or helper that injects locale.
- **Route guards** in `proxy.ts` (middleware): redirect unauthenticated users to login, preserve locale.
- **Messages** in `messages/{en,th,vi}.json`: user-facing text only (not debug/operational text).

## Go Microservices Layer Boundaries

### Service Composition Root (`services/<name>/internal/app/`)

Each service owns:
- **Main service struct** with dependencies injected
- **Wiring**: bootstrap config, mq client, database, logger
- **Handlers/Consumers**: specific to this service's business logic
- **HTTP server setup** (if this service exposes API routes)

**Never duplicate** config loaders, MQ clients, database stores across services. These belong in `shared/common/`.

### Cross-Cutting Infrastructure (`shared/common/`)

**Lived in one place only.** All services import and reuse:

- **Config** (`config/`): environment variable loading, validation, logging config. Single `Config` struct with all app settings.
- **MQ** (`mq/`): RabbitMQ client, topology (exchanges, queues, bindings). Single instance per deployment.
  - Watcher publishes to `my-app.download.jobs` queue → Download service consumes.
  - Download publishes to `my-app.archive.done` queue → Notify service consumes.
  - Each service Consumes from one or more queues; produces to zero or more queues.
- **SFTP Client** (`sftpclient/`): FTP/SFTP connection, login. Single instance per deployment.
- **Database** (`store/`): GORM ORM, migrations, shared models (User, Order, etc.). Single PostgreSQL instance.
- **Logger** (`logger/`): structured logging abstraction (JSON, fields, levels). All services use the same logger.
- **Metrics** (`metrics/`): Prometheus counters/gauges/histograms. Single metrics registry.
- **Jobs** (`jobs/`): job scheduling, retry logic, cron patterns.
- **Shared Models** (`models/`): domain entities referenced across multiple services (Order, Customer, etc.). Do NOT put service-specific models here.

### Pipeline Example: SFTP → Download → Archive

```
Watcher Service
  └─ watches WATCHER_PATHS on SFTP
     └─ publishes (filename, type) to mq.download_jobs queue

MQ (RabbitMQ, in shared/common/)
  └─ queue: my-app.download.jobs
     └─ consumers: [Download service]

Download Service
  └─ consumes from mq.download_jobs
     └─ fetches file from SFTP (sftpclient in shared/common/)
     └─ parses file (file-type parser, internal to download service)
     └─ validates & persists to PostgreSQL (store in shared/common/)
     └─ archives file to local or remote archive root
     └─ publishes (filename, status) to mq.archive_done queue

Notify Service
  └─ consumes from mq.archive_done
     └─ sends notification email / webhook
     └─ marks notification as sent in database
```

**Key rule:** No direct database writes without going through `shared/common/store`. No direct SFTP access without going through `shared/common/sftpclient`. No direct MQ access except through `shared/common/mq`.

## Adapter Pattern: Mock vs. Real

When backend API, external service, or feature is not yet ready, use **swappable adapters** to unblock frontend development.

### Setup in Next.js Webapp

```typescript
// lib/api/adapters/types.ts (shared interface)
export interface OrderAdapter {
  list(filter?: OrderFilter): Promise<Order[]>;
  getById(id: string): Promise<Order | null>;
  create(data: CreateOrderInput): Promise<Order>;
  update(id: string, data: UpdateOrderInput): Promise<Order>;
  delete(id: string): Promise<void>;
}

// lib/api/adapters/mock.ts (behavior-equivalent)
export const mockAdapter: OrderAdapter = {
  async list(filter?: OrderFilter) {
    // Return hardcoded or in-memory data matching real schema
    return [
      { id: 'order-1', customerId: 'cust-1', total: 100, status: 'pending', ... },
      // ...
    ];
  },
  // ... other methods
};

// lib/api/adapters/real.ts (talks to backend)
export const realAdapter: OrderAdapter = {
  async list(filter?: OrderFilter) {
    const params = new URLSearchParams();
    if (filter?.customerId) params.set('customerId', filter.customerId);
    const res = await apiFetch(`/api/orders?${params}`);
    if (!res.ok) throw new Error(`Orders list failed: ${res.status}`);
    const data = await res.json();
    return data.map(normalizeOrder); // normalize backend shape to shared type
  },
  // ... other methods
};

// lib/api/client.ts (selector)
const dataSource = process.env.NEXT_PUBLIC_API_DATA_SOURCE || 'mock';
export const orderAdapter = dataSource === 'real' ? realAdapter : mockAdapter;
```

### Environment Variable

```bash
# .env.local
NEXT_PUBLIC_API_DATA_SOURCE=mock     # development before backend ready
NEXT_PUBLIC_API_DATA_SOURCE=real     # once backend is deployed

# .env.production
NEXT_PUBLIC_API_DATA_SOURCE=real
```

### Rules for Mock Adapters

✅ **DO:**
- Match the real adapter's response shape, status codes, error messages exactly
- Implement filtering, sorting, pagination with the same logic as real (if applicable)
- Return realistically structured data (use ULIDs, valid dates, etc.)
- Throw errors matching real adapter error handling (timeout, 400, 404, 500, etc.)

❌ **DON'T:**
- Return empty arrays/stubs without behavior
- Skip validation that real adapter would do
- Use hardcoded, unfiltered data when filter is provided
- Ignore pagination parameters

**Test coverage:** When mock and real both exist, run the same test suite against both adapters to ensure behavior equivalence.

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

## Architecture Decision Rules

### 1. Dependency Direction (Non-Negotiable)

```
Presentation ──→ Application ──→ Domain
   (pages,          (hooks,         (types,
   components)      adapters)       helpers)
       ↑                ↑
       └────────────────┘
Infrastructure implements ports
(Database, MQ, SFTP, external APIs)
      ↑
      │ (inward-owned interfaces)
   Domain / Application
```

**Rules:**
- Inner layers (Domain, Application) **never import** outer layers (Presentation, Infrastructure, Composition Root).
- Outer layers **import** inner layers.
- Infrastructure implements inward-owned **ports** (interfaces defined in Domain/Application).
- No cycles, no hidden global state, no leaky ORM objects across boundaries.

### 2. New Primary Keys

Use **ULIDs** for new primary keys by default unless an external contract (SAP, ERP, customer database) mandates otherwise.

```go
// Go example using google/uuid or similar ULID library
id := ulid.Make()  // or uuid.NewString()
```

```typescript
// TypeScript: export as string
export type ID = string;
export function generateId(): ID {
  return crypto.randomUUID(); // or ulid library
}
```

### 3. Error Handling Across Boundaries

**Domain:** Define domain-specific error types (not generic strings).
```go
// shared/common/models/errors.go
type ValidationError struct {
  Field   string
  Message string
}

type NotFoundError struct {
  Entity string
  ID     string
}
```

**Application:** Catch domain errors, map to use-case errors (DTOs, API contracts).
```go
// services/download/internal/app/download.go
case *models.ValidationError:
  return &app.DownloadError{
    Code:    "INVALID_FILE",
    Message: err.Message,
    Status:  http.StatusBadRequest,
  }
```

**Delivery:** Translate to HTTP status, client error responses.
```typescript
// webapp lib/api/adapters/real.ts
if (!res.ok) {
  const err = await res.json();
  if (err.code === 'NOT_FOUND') throw new NotFoundError(...);
  if (err.code === 'INVALID_FILE') throw new ValidationError(...);
  throw new UnknownError(...);
}
```

### 4. TypeScript `any` Forbidden

- No `any` type (enforce via ESLint as error)
- Use explicit types and `import type` for type-only imports
- Generic types with constraints, not unconstrained generics

```typescript
// ❌ WRONG
const data: any = response;

// ✅ CORRECT
const data: OrderListResponse = response;
import type { OrderListResponse } from '@/types/orders';
```

### 5. Secrets & Sensitive Data

**Never commit:**
- `.env` files (use `.env.example` as template)
- API keys, passwords, database credentials
- Production data, logs with sensitive fields
- Mock data with real customer/financial information

**Store safely:**
- GitHub Secrets for CI/CD
- AWS Secrets Manager / HashiCorp Vault for production
- `.env.local` (gitignored) for local development

### 6. Database Migrations

- Use ORM-native migrations (GORM auto-migration for Go, etc.) or custom versioned SQL scripts
- Store migrations in `shared/common/store/migrations/`
- Never run destructive migrations without data backup
- Test migrations on a copy of production data before running on live

### 7. Configuration & Environment

All config loaded **once at startup** from environment variables, then passed to services as dependency-injected values.

```go
// shared/common/config/config.go
type Config struct {
  PostgresURL  string
  RabbitMQURL  string
  LogLevel     string
  // ...
}

func LoadConfig() (*Config, error) {
  return &Config{
    PostgresURL: os.Getenv("POSTGRES_URL"),
    RabbitMQURL: os.Getenv("RABBITMQ_URL"),
    LogLevel:    os.Getenv("LOG_LEVEL"),
  }, nil
}

// services/download/internal/app/app.go
func New(cfg *config.Config) *App {
  return &App{
    db:     store.NewStore(cfg.PostgresURL),
    mq:     mq.NewClient(cfg.RabbitMQURL),
    logger: logger.New(cfg.LogLevel),
  }
}
```

No runtime config changes or environment variable lookups inside handlers.

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

---

## Quick Reference: Rules Summary

| Rule | Location | Example |
|------|----------|---------|
| Locale-prefixed routes | `app/[locale]/...` | `/en/orders`, `/th/admin` |
| API adapters | `lib/api/adapters/{mock,real}` | `NEXT_PUBLIC_API_DATA_SOURCE=real` |
| Cross-cutting infra | `shared/common/{config,mq,sftpclient,store,...}` | All services import `shared/common/store` |
| Service wiring | `services/<name>/internal/app/` | Dependency injection in `New(cfg *config.Config)` |
| Secrets | `.env.local` (gitignored) | `POSTGRES_URL`, `RABBITMQ_URL` |
| Primary keys | ULIDs | `ulid.Make()` or `uuid.NewString()` |
| Forbidden | TypeScript `any`, duplicate MQ clients | `import type { Order } from '@/types'` |
| Dependency direction | Presentation → App → Domain ← Infra | Adapters call `shared/common/store`, not vice versa |

---

## See Also

- `next-auth` v5 for authentication patterns
- `next-intl` for internationalization in App Router
- `shadcn/ui` + Tailwind v4 for component library
- `Bun` for Node.js runtime + package manager
- `GORM` for Go ORM
- `RabbitMQ` for event-driven microservices
- PostgreSQL for persistence
- Docker Compose for local orchestration
