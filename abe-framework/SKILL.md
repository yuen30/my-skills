---
name: abe-framework
description: Framework guidance for Next.js, Astro, Angular, React (Vite SPA), React Three Fiber/Three.js, Go Fiber v3, Hono, Laravel, Filament, Django/DRF, Odoo addons and Frappe/ERPNext. Use when writing, reviewing, upgrading or debugging code in Next.js, Astro, Angular, React, R3F, Fiber, Hono, Laravel, Filament, Django, Odoo or Frappe, or when you see next.config, angular.json, astro.config, go.mod with gofiber, artisan, manage.py, __manifest__.py or hooks.py.
---

# ABE Framework

One skill for every supported framework. Detect the stack, then read ONLY the matching reference(s); do not load references for frameworks the project does not use.

## Step 1: Detect the stack

| Marker in the project | Read |
|---|---|
| `next.config.*` or `"next"` dependency | [nextjs.md](references/nextjs.md), plus the `nextjs-*.md` file for the task |
| `angular.json` / `@angular/core` | [angular.md](references/angular.md) |
| `astro.config.*` / `.astro` files | [astro.md](references/astro.md), plus the `astro-*.md` file for the task |
| `vite` + `react` without `next` | [react.md](references/react.md) |
| `three` / `@react-three/fiber` / `@react-three/drei` | [react-three-fiber.md](references/react-three-fiber.md) |
| `go.mod` requiring `github.com/gofiber/fiber` | [go-fiber.md](references/go-fiber.md) |
| `"hono"` dependency | [hono.md](references/hono.md) |
| `artisan` / `laravel/framework` in composer.json | [laravel.md](references/laravel.md) |
| `filament/filament` (or any `filament/*`) in composer.json | [filament.md](references/filament.md) (plus laravel.md for non-Filament Laravel code) |
| `manage.py` / Django dependency | [django.md](references/django.md) |
| `__manifest__.py` | [odoo.md](references/odoo.md) |
| `hooks.py` + `frappe` imports / bench | [frappe.md](references/frappe.md) |

Monorepos: detect per app/package from the file being changed, not from the repo root.

## Shared rules (apply to every framework)

- Detect the installed version first (lockfile / resolved package, not just the constraint) and state it before giving version-specific guidance. If detection is impossible, say so instead of guessing.
- Training-data knowledge of these frameworks may be stale. Prefer docs bundled with the installed package (e.g. `node_modules/next/dist/docs/`, `<vendor-dir>/filament/*/docs/`), then version-matched official docs or the `context7-auto-research` skill, over memory. If bundled docs are missing, say so.
- Do not invent APIs, classes, config keys or hook signatures; verify against the docs for the detected version.
- Don't mix legacy and new patterns of a major version. Follow the patterns of the installed version and the project's existing conventions; don't force a migration that was not asked for.
- Run the repository-defined checks (typecheck, lint, tests, build) and report anything unverified.

## Sibling skills

- `project-structure` — where files and folders go (layout, layering) for every stack.
- `abe-ui` — UI kit work: Tailwind v4, shadcn/ui, daisyUI.
- `web-research` — current facts, release notes, error fixes from the web.
- ORM skills — `prisma`, `drizzle-orm`, `eloquent-orm`, `sqlalchemy` for schema, migrations and queries.

## Reference routing

| File | Read when |
|---|---|
| [nextjs.md](references/nextjs.md) | Any Next.js work (entry point, shared Next.js rules) |
| [nextjs-ai-agents.md](references/nextjs-ai-agents.md) | Before code changes; creating, inspecting, debugging or reviewing a Next.js project; `nextjs-agent-rules` block |
| [nextjs-data-security.md](references/nextjs-data-security.md) | Authn/authz, Server Actions, Route Handlers, env vars, caching, CSP, data exposure |
| [nextjs-pages-router.md](references/nextjs-pages-router.md) | App uses `pages/`, getServerSideProps, API Routes, `_app`/`_document`, or router migration |
| [nextjs-production-checklist.md](references/nextjs-production-checklist.md) | Preparing a Next.js app to ship |
| [nextjs-upgrading.md](references/nextjs-upgrading.md) | Next.js/React major bump, codemods, upgrade breakage |
| [astro.md](references/astro.md) | Any Astro work (iron laws, anti-patterns, quick reference) |
| [astro-components.md](references/astro-components.md) | Writing `.astro` components or framework islands |
| [astro-content-collections.md](references/astro-content-collections.md) | Collection schemas, dynamic routes from collections |
| [astro-data-fetching.md](references/astro-data-fetching.md) | Build-time or SSR fetching, API endpoints |
| [astro-deployment.md](references/astro-deployment.md) | Env vars, `astro.config.mjs`, deploying |
| [angular.md](references/angular.md) | Angular components, signals, control flow, DI, migrations |
| [react.md](references/react.md) | Plain client-side React components, hooks, state (not Next.js) |
| [react-three-fiber.md](references/react-three-fiber.md) | 3D scenes with R3F, Three.js, Drei |
| [go-fiber.md](references/go-fiber.md) | Go Fiber v3 code or v2 to v3 migration |
| [hono.md](references/hono.md) | Hono routing, middleware, runtimes, zod validation, `hc` RPC |
| [laravel.md](references/laravel.md) | Laravel apps, artisan, upgrades, old vs new conventions |
| [filament.md](references/filament.md) | Filament resources, panels, forms, tables, widgets |
| [django.md](references/django.md) | Django models, DRF APIs, ORM optimization, auth, testing, production settings |
| [odoo.md](references/odoo.md) | Odoo addon models, XML views, security, odoo-bin setup |
| [frappe.md](references/frappe.md) | Frappe/ERPNext DocTypes, hooks.py, frappe ORM, whitelisted APIs, bench |
