Read when placing code in a Next.js project (App Router or Pages Router): routing-folder boundaries, server/client split, feature modules.

# Next.js Structure

Next.js routing details come from the installed docs under `node_modules/next/dist/docs/`. This file covers only where code goes.

## Folder responsibilities

| Folder | Responsibility |
|---|---|
| `app/` or `pages/` | Routing, composition, metadata, boundary mapping only |
| `components/ui/` | Reusable presentational primitives; no business rules or persistence |
| `components/` | Composed UI shared by real consumers |
| `hooks/` | Reusable React state, effects, subscriptions, client behavior |
| `helpers/` | Small pure functions with explicit inputs and outputs |
| `lib/` | Named integrations, configuration, clients, framework adapters |
| `types/` | Stable contracts shared across multiple features |
| `features/<feature>/` | Feature-owned UI, use cases, domain rules, ports, adapters |

Keep a type, hook, or helper inside its feature when it has only one owner.

## Routing-layer boundaries

- Keep pages, layouts, Route Handlers, and Server Actions thin: parse/validate boundary input, call a use case or service, map the result.
- Pages and layouts are Server Components by default; add `"use client"` only at the smallest scope that needs state, effects, or browser APIs.
- Validate external input and authorize mutations at the server boundary and in the use-case layer.
- Keep server-only dependencies (secrets, credentials, unrestricted backend responses) outside Client Component import graphs; never pass them to Client Components via props.
- Do not fetch the application's own Route Handler from a Server Component when a direct use-case or service call is available.

## React boundaries (also apply to plain React)

- Keep route components thin and feature-oriented.
- Put server communication behind typed adapters or feature services.
- Keep reusable UI independent from router, global state, and API response shapes.
- Do not move state to a global store until multiple independent consumers require it.

## Code rules at boundaries

- Meaningful names, guard clauses, cohesive functions, explicit return types at boundaries.
- No `any`, hidden global state, cyclic imports, raw vendor payloads, or ORM records outside infrastructure.
- Use `import type` for type-only dependencies.

## Review checklist

- Are `app/`/`pages/` files only routing, composition, and boundary mapping?
- Are business rules outside UI, routes, and persistence adapters?
- Is anything server-only reachable from a `"use client"` file?
- Can Domain and Application behavior be tested without rendering React or starting Next.js?
