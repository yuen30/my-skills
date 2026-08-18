---
name: nextjs-pages-router
description: Use only for existing Pages Router or hybrid Next.js applications, legacy pages and API Routes, or an explicitly requested incremental migration between Pages Router and App Router.
---

# Next.js Pages Router

Pages Router behavior is version-sensitive. Resolve the installed Next.js package and read the Pages Router guides under `node_modules/next/dist/docs/` before changing routing, data fetching, API Routes, or special files.

## Trigger boundary

Use this skill when the affected app contains `pages/`, `src/pages/`, legacy API Routes, `_app`, `_document`, `_error`, or Pages Router data-fetching functions. Do not apply Pages Router conventions to an App Router-only application.

Do not migrate routers unless the user explicitly requests it.

## Inventory before editing

- route files, dynamic and catch-all segments
- `_app`, `_document`, `_error`, custom 404/500 pages
- API Routes and their authentication or validation
- server-side, static, ISR, and client-side data flows
- router hooks, redirects, locale routing, and middleware or Proxy
- shared layouts, providers, global styles, and document markup
- deployment constraints, runtime, cache, and revalidation behavior

## Maintenance rules

- Preserve URL, query, status, cache, redirect, and rendering semantics.
- Keep page components thin; move business rules into framework-independent use cases.
- Validate and authorize API Route input at the boundary.
- Return minimal serializable props and avoid leaking persistence records.
- Follow the installed docs for special files and data-fetching lifecycle.
- Add focused regression tests before refactoring legacy behavior.

## Incremental migration

1. Define the route or feature boundary being migrated.
2. Read both Pages Router and App Router migration guides from the installed package.
3. Map old rendering, data, error, metadata, auth, and cache semantics to explicit acceptance tests.
4. Move one coherent route group at a time.
5. Keep shared Domain and Application code router-independent.
6. Avoid importing App Router-only APIs into remaining Pages Router code.
7. Verify navigation between routers, rewrites, cookies, sessions, assets, and deployment output.
8. Remove legacy files only after no route or runtime path depends on them.

## Verification

- Run focused tests for affected routes and API endpoints.
- Exercise direct loads, client navigation, refresh, error, auth, and not-found paths.
- Run repository-defined typecheck, lint, full tests, and production build.
- For hybrid apps, test routes from both routers in the production-like runtime.

## Handover

State whether the result remains Pages Router, becomes hybrid, or completes a migration. List preserved semantics, changed URLs or contracts, verification evidence, and remaining legacy boundaries.
