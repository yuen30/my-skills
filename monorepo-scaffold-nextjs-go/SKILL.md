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

## Layout & Layer Boundaries

Monorepo layout and Next.js/Go layer/dependency rules → use the `project-structure` skill (references/monorepo-nextjs-go.md).

## Adapter Pattern: Mock vs. Real

See [references/adapters.md](references/adapters.md) — read when implementing or swapping mock/real API adapters.

## Local Development

See [references/local-dev.md](references/local-dev.md) — read when setting up Docker Compose, env vars or running the stack locally.

## Architecture Decision Rules

See [references/decision-rules.md](references/decision-rules.md) — read when making an architectural decision (where code goes, new service, shared infra).

## Project Initialization Checklist

See [references/init-checklist.md](references/init-checklist.md) — read when bootstrapping a new project from this template.

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
