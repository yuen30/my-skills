---
name: nextjs
description: Next.js workflows for agents, security review, Pages Router, pre-release checks and upgrades. Use when working on a Next.js project, auditing it, shipping it, bumping versions, or maintaining a pages/ app.
---

# Next.js

Treat the docs bundled with the installed `next` package (`node_modules/next/dist/docs/`, resolved from the app's own package root) as the source of truth. Version-specific APIs, commands, codemods and version tables remembered by the model are not authoritative; if the bundled docs are missing, say so instead of guessing.

Project structure and code placement are covered by the separate `project-structure` skill.

## Routing

| Task | Reference | Read when |
|---|---|---|
| Any agent work on a Next.js project, new-project bootstrap, `nextjs-agent-rules` block | [ai-agents.md](references/ai-agents.md) | Before code changes, or creating/inspecting/debugging/reviewing a project |
| Authn/authz, Server Actions, Route Handlers, env vars, caching, CSP, data exposure | [data-security.md](references/data-security.md) | Implementing or auditing security |
| `pages/`, getServerSideProps, API Routes, `_app`/`_document`, router migration | [pages-router.md](references/pages-router.md) | App is Pages Router or hybrid (not for App Router-only apps) |
| Pre-release verification across correctness, security, perf, a11y, SEO, ops | [production-checklist.md](references/production-checklist.md) | Preparing to ship |
| Major version bump, codemods, upgrade breakage | [upgrading.md](references/upgrading.md) | Upgrading Next.js, React or related tooling |

## Shared rules

- Run repository-defined commands (install from lockfile, typecheck, lint, tests, production build); report any unverified assumption explicitly.
- The `nextjs-agent-rules` block that `next dev` writes is managed: keep it, never edit inside the markers, put project rules outside it, and commit legitimate generated changes with the related work.
