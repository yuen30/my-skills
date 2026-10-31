---
name: project-structure
description: Single entry point for where code and folders go, across stacks. Use when creating or placing files/folders, scaffolding, reviewing layering, or splitting fat modules in any stack. Not for framework API usage (use the framework skill).
---

# Project Structure

Decide where new code, files, and folders belong, and review existing layering. Framework APIs (ORM calls, routing APIs, component syntax) live in the framework skills; this skill only answers "where does it go and what may it import".

## Step 0: Inspect before placing

1. Read project-local rules (CLAUDE.md, AGENTS.md, README), package scripts, path aliases, and the existing feature layout.
2. Preserve established names and boundaries unless the requested change requires migration.
3. Scale the structure to the application; do not create layers or shared folders with no real responsibility.

## Step 1: Detect stack, read ONLY the matching reference(s)

| Marker in repo | Read |
|---|---|
| `next.config.*` or `app/` / `pages/` with `next` in package.json | [nextjs.md](references/nextjs.md) + [frontend-layers.md](references/frontend-layers.md) |
| `vite.config.*` + `react`, no `next` | [frontend-layers.md](references/frontend-layers.md) |
| `go.mod` requiring `github.com/gofiber/fiber` | [go-fiber.md](references/go-fiber.md) |
| pnpm/turbo/bun workspace with a Next.js app plus `services/` Go modules and `shared/common/` | [monorepo-nextjs-go.md](references/monorepo-nextjs-go.md) |
| `manage.py` | [django.md](references/django.md) |
| `__manifest__.py` | [odoo.md](references/odoo.md) |
| `hooks.py` + `modules.txt` (Frappe app) | [frappe.md](references/frappe.md) |
| `astro.config.*` | [astro.md](references/astro.md) |

Reviewing or splitting a fat React/Next.js component: also read [frontend-smells-and-refactor.md](references/frontend-smells-and-refactor.md).

No marker matches: apply only the universal rules below.

## Universal rules

### Dependency direction

```text
Presentation -> Application -> Domain
Infrastructure -> Application/Domain ports
Composition Root -> concrete implementations
```

- **Domain**: framework-free entities, value objects, policies, invariants, typed errors.
- **Application**: use cases, orchestration, authorization, transactions, DTOs, ports (interfaces it owns).
- **Infrastructure**: persistence, API, queue, cache, filesystem adapters; implements Application/Domain ports.
- **Presentation**: maps UI, route, controller, or handler input to a use case. Thin.
- **Composition root**: loads config once at startup, wires concrete implementations, injects them.
- Inner layers never import framework, ORM, HTTP, or vendor types from outer layers.
- No cycles: if A imports B, B must not import A.
- Map vendor/ORM payloads at the Infrastructure boundary; never pass raw ORM records or vendor responses outward.

### Where does this code go?

| The code... | Layer | Typical home |
|---|---|---|
| Parses request/route input, renders, returns HTTP | Presentation | routes, pages, controllers, handlers, components |
| Coordinates a use case, transaction, authorization | Application | service / use case / hook (client orchestration) |
| Expresses a business rule or invariant, no I/O | Domain | policy, entity, feature domain module |
| Talks to DB, external API, queue, SFTP, filesystem | Infrastructure | repository, adapter, client |
| Loads env/config, builds clients, wires dependencies | Composition root | `app.go`, `internal/app/`, settings, `lib/` config |
| Is a pure generic utility (format, parse, math) with no domain meaning | Shared helper | `helpers/` / `utils/` |
| Is a type/contract used by 2+ modules | Shared types | `types/` / `models/` / DTO file |
| Has exactly one owner | Stays with its owner | same file or the feature folder |

### Naming and colocation

- Keep a type, hook, helper, or constant inside its feature when it has only one owner; move it to a shared folder only when a second consumer appears, and update both call sites.
- Create shared abstractions only after real reuse exists.
- Do not turn `helpers`, `lib`, `types`, `utils`, or `common` into dumping grounds.
- Cross-cutting infrastructure (config loader, DB store, MQ client, logger) lives in one place only; never duplicate it per service/feature.
- Single source of truth for each type/contract; never redefine the same shape in two files.
- Follow the project's ID convention; when starting a new project without one, ULID is the preferred default unless an external contract mandates otherwise.
- Follow the stack's file naming (e.g. snake_case `*_controller.go` in Go, `test_*.py` in Python, one file per model/table) as described in the matching reference.

### Review checklist

- Does each module have one clear owner and responsibility?
- Are business rules outside UI, routes, controllers, and persistence adapters?
- Do dependencies point inward without cycles?
- Are shared folders justified by multiple consumers?
- Are framework, ORM, and vendor types mapped at boundaries?
- Can Domain and Application behavior be tested without a framework, DB, or network?
- Is config read once at startup, not inside handlers?

### Top smells

- Business logic inline in UI/JSX, controllers, or route handlers.
- Direct `fetch`/DB/vendor call from presentation code instead of an adapter or service.
- "Pure" helper importing React, hooks, ORM, or network clients.
- Generic UI primitive importing business types.
- Same type or rule defined in several places.
- Duplicated infra client (MQ, DB, config) per service instead of shared.
- Raw ORM/vendor objects leaking past the Infrastructure boundary.
- Over-engineering: full layered split for plain CRUD with no business rules.
- Fat module (component > ~150-200 lines, controller doing several use cases): split by layer.
