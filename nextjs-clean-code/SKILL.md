---
name: nextjs-clean-code
description: Use when designing, implementing, or reviewing clean code in Next.js or React projects, especially folder boundaries for components/ui, hooks, helpers, lib, types, feature modules, and layered business logic.
---

# Next.js and React Clean Code Architecture

Apply these conventions to both Next.js and plain React projects. Next.js routing details still come from the installed documentation under `node_modules/next/dist/docs/`.

## First inspect the project

1. Read project-local rules, package scripts, path aliases, and existing feature structure.
2. For Next.js work, follow the source-of-truth workflow in the Next.js AI Coding Agents skill.
3. Preserve established names and boundaries unless the requested change requires migration.
4. Scale the structure to the application; do not create layers or shared folders with no real responsibility.

## Dependency direction

```text
Presentation -> Application -> Domain
Infrastructure -> Application/Domain ports
Composition Root -> concrete implementations
```

- Domain contains framework-free entities, policies, invariants, and errors.
- Application orchestrates use cases, authorization, transactions, DTOs, and ports.
- Infrastructure implements persistence, API, queue, cache, and filesystem adapters.
- Presentation maps UI, route, controller, or handler input to use cases.
- Inner layers never import framework, ORM, HTTP, or vendor types from outer layers.

## Folder responsibilities

| Folder | Responsibility |
|---|---|
| `components/ui/` | Reusable presentational primitives; no business rules or persistence |
| `components/` | Composed UI shared by real consumers |
| `hooks/` | Reusable React state, effects, subscriptions, and client behavior |
| `helpers/` | Small pure functions with explicit inputs and outputs |
| `lib/` | Named integrations, configuration, clients, and framework adapters |
| `types/` | Stable contracts shared across multiple features |
| `features/<feature>/` | Feature-owned UI, use cases, domain rules, ports, and adapters |

Keep a type, hook, or helper inside its feature when it has only one owner. Do not turn `helpers`, `lib`, `types`, `utils`, or `common` into dumping grounds.

## Next.js boundaries

- Keep `app/` or `pages/` focused on routing, composition, metadata, and boundary mapping.
- Keep pages, layouts, Route Handlers, and Server Actions thin.
- Validate external input and authorize mutations at the server boundary and use-case layer.
- Keep server-only dependencies outside Client Component import graphs.
- Do not fetch the application's own Route Handler from a Server Component when a direct use case or service call is available.

## React boundaries

- Keep route components thin and feature-oriented.
- Put server communication behind typed adapters or feature services.
- Keep reusable UI independent from router, global state, and API response shapes.
- Avoid moving state to a global store until multiple independent consumers require it.

## Code rules

- Prefer meaningful names, guard clauses, cohesive functions, and explicit return types at boundaries.
- Avoid `any`, hidden global state, cyclic imports, raw vendor payloads, and ORM records outside infrastructure.
- Use `import type` for type-only dependencies.
- Create shared abstractions only after real reuse exists.
- Follow the project's ID convention; when starting a new project without one, ULID is the preferred default.

## Review checklist

- Does each module have one clear owner and responsibility?
- Are business rules outside UI, routes, and persistence adapters?
- Do dependencies point inward without cycles?
- Are shared folders justified by multiple consumers?
- Are framework and vendor types mapped at boundaries?
- Can Domain and Application behavior be tested without rendering React or starting Next.js?
