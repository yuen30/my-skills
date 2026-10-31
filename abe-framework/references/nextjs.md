Read when the project has next.config.* or a "next" dependency; then read the matching nextjs-*.md for the task.

# Next.js

Project structure and code placement are covered by the separate `project-structure` skill.

## Routing

| Task | Reference | Read when |
|---|---|---|
| Any agent work on a Next.js project, new-project bootstrap, `nextjs-agent-rules` block | `nextjs-ai-agents.md` | Before code changes, or creating/inspecting/debugging/reviewing a project |
| Authn/authz, Server Actions, Route Handlers, env vars, caching, CSP, data exposure | `nextjs-data-security.md` | Implementing or auditing security |
| `pages/`, getServerSideProps, API Routes, `_app`/`_document`, router migration | `nextjs-pages-router.md` | App is Pages Router or hybrid (not for App Router-only apps) |
| Pre-release verification across correctness, security, perf, a11y, SEO, ops | `nextjs-production-checklist.md` | Preparing to ship |
| Major version bump, codemods, upgrade breakage | `nextjs-upgrading.md` | Upgrading Next.js, React or related tooling |

## Shared rules

- Run repository-defined commands (install from lockfile, typecheck, lint, tests, production build); report any unverified assumption explicitly.
- The `nextjs-agent-rules` block that `next dev` writes is managed: keep it, never edit inside the markers, put project rules outside it, and commit legitimate generated changes with the related work.
