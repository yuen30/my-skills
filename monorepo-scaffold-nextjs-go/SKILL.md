---
name: monorepo-scaffold-nextjs-go
description: Monorepo template, Next.js App Router (Bun) plus Go microservices with shared infra, mock/real API adapters, Docker Compose and layered rules. Use when scaffolding or extending a Next.js + Go monorepo with RabbitMQ and PostgreSQL.
---

# Monorepo Scaffold: Next.js App Router + Go Microservices

Template for a production-grade monorepo combining:
- **Next.js 16+ App Router** storefront and admin with React 19, TypeScript, Bun, Tailwind, shadcn/ui
- **Go 1.20+ microservices** (watcher, download, notify, healthchecker examples) coordinating via RabbitMQ into PostgreSQL
- **Shared Go infrastructure** (`shared/common/`) for config, MQ, SFTP client, database/ORM, logging, metrics — reused across all services, never duplicated
- **Swappable API adapters** (mock/real) for feature development before backend is ready
- **Docker Compose** local dev with fallback to host-side services when containers cannot reach SFTP
- **Strict layered architecture** with dependency direction rules enforced from day one

> **Note:** The version pins in this scaffold (Next.js 16+, React 19, Go 1.20+, next-auth v5, etc.) reflect the stack current as of when this skill was written. Before scaffolding a new project, verify current latest stable versions (e.g. `npm view next version`, `npm view react version`, `go version` / https://go.dev/dl/) rather than assuming the pinned versions here are still latest. The scaffold's *structure and patterns* (monorepo layout, adapter pattern, etc.) remain valid across version bumps even as specific version numbers change.

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

See [references/adapters.md](references/adapters.md) — read when implementing or swapping mock/real API adapters.

## Local Development

See [references/local-dev.md](references/local-dev.md) — read when setting up Docker Compose, env vars or running the stack locally.

## Architecture Decision Rules

See [references/decision-rules.md](references/decision-rules.md) — read when making an architectural decision (where code goes, new service, shared infra).

## Project Initialization Checklist

See [references/init-checklist.md](references/init-checklist.md) — read when bootstrapping a new project from this template.

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
