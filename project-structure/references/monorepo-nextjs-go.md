Read when placing code in a monorepo combining a Next.js App Router webapp with Go microservices that share `shared/common/` infrastructure.

# Monorepo: Next.js Webapp + Go Microservices

## Layout

```text
project-root/
├── webapp/                       # Next.js App Router (React, TS, Bun)
│   ├── app/
│   │   ├── [locale]/             # Locale-prefixed routes (/en, /th, ...)
│   │   │   ├── (public)/         # Unauthenticated routes
│   │   │   ├── (auth)/           # Auth-required routes
│   │   │   └── layout.tsx
│   │   └── api/                  # Route handlers (thin proxy/delivery)
│   ├── components/
│   │   ├── ui/                   # shadcn/ui primitives
│   │   └── feature-*/            # Feature compound components
│   ├── hooks/                    # Client state, browser orchestration
│   ├── providers/                # React context providers
│   ├── lib/
│   │   ├── api/adapters/{mock,real}/  # Backend communication (single source of truth)
│   │   ├── auth/                 # Auth orchestration, next-auth config
│   │   ├── types/                # Shared TS types, DTOs, contracts
│   │   └── helpers/              # Pure functions
│   ├── helpers/  types/          # (see "Duplicate folders" below)
│   ├── i18n/  messages/          # Locale routing config, {en,th,vi}.json
│   ├── tests/                    # E2E (Playwright)
│   ├── auth.ts  proxy.ts  next.config.ts  Dockerfile
├── services/<name>/internal/app/ # Per-service composition root + handlers/consumers
├── shared/common/                # Cross-cutting Go infrastructure (one copy only)
│   ├── config/  logger/  store/  mq/  sftpclient/  metrics/  jobs/  models/
├── deploy/                       # docker-compose.yml, K8s/Helm
├── .github/workflows/
├── .env.compose.example  .env.local.example
└── docker-compose.yml
```

Duplicate folders: the source template lists both `lib/helpers/` + `helpers/` and `lib/types/` + `types/`. Pick one location per project (follow whichever the repo already uses) and never define the same type or helper in both.

## Webapp layers

| Layer | Path | Rules |
|---|---|---|
| Presentation | `app/`, `components/` | Routes validate boundary input, invoke a hook/action, pass result to a component. Pages are server by default; `"use client"` at smallest scope. Route Handlers: parse, call adapter, map, return. Components take data via props, never call adapters, no business rules. `components/ui/` has no logic. |
| Application | `hooks/`, `lib/auth/`, `lib/api/adapters/` | Hooks fetch via adapter and manage UI state. Adapters own fetch/mutation, normalization, error mapping. Mock and real adapters must be behavior-equivalent. |
| Domain | `lib/helpers/`, `types/` | Pure functions; shared contracts, DTOs, schemas. No framework, ORM, HTTP. No dependency on outer layers. |
| Server-only | `auth.ts`, `lib/auth/*` | Secrets, credentials, unrestricted backend responses. Never passed to Client Components. |

Dependency: `app → components → hooks/lib`. Adapter selection happens once:

```ts
// lib/api/client.ts
const dataSource = process.env.NEXT_PUBLIC_API_DATA_SOURCE || "mock"; // "mock" | "real"
export const apiClient = dataSource === "real" ? realAdapter : mockAdapter;
```

Routing: all user-facing routes carry the locale prefix; preserve locale in links and redirects; route guards live in `proxy.ts`; `messages/*.json` holds user-facing text only.

## Go service layers

- `services/<name>/internal/app/` is the composition root: main service struct with injected dependencies, wiring (config, MQ, DB, logger), service-specific handlers/consumers, HTTP server setup if the service exposes routes.
- `shared/common/` holds cross-cutting infrastructure, lived in one place only:
  - `config/` — single `Config` struct, loaded once at startup, injected (`New(cfg *config.Config)`); no env lookups inside handlers.
  - `mq/` — RabbitMQ client and topology (exchanges, queues, bindings).
  - `sftpclient/`, `logger/`, `metrics/`, `jobs/`.
  - `store/` — GORM, shared models, migrations in `store/migrations/`.
  - `models/` — entities referenced across multiple services only; service-specific models stay in the service. Domain error types (`ValidationError`, `NotFoundError`) live here.
- Never duplicate config loaders, MQ clients, or DB stores per service.
- No DB writes except via `shared/common/store`; no SFTP except via `sftpclient`; no MQ except via `mq`.

## Errors across boundaries

Domain defines typed errors → Application maps them to use-case errors (code, message, status) → the webapp adapter translates error codes into typed client errors.

## Rules summary

| Rule | Location |
|---|---|
| Locale-prefixed routes | `app/[locale]/...` |
| API adapters | `lib/api/adapters/{mock,real}` |
| Cross-cutting infra | `shared/common/{config,mq,sftpclient,store,...}` |
| Service wiring | `services/<name>/internal/app/` |
| Secrets | `.env.local` (gitignored); `.env.example` committed |
| Primary keys | ULID unless an external contract mandates otherwise |
| Forbidden | TypeScript `any`, duplicate MQ/DB clients |
| Dependency direction | Presentation → Application → Domain ← Infrastructure |
