---
name: nextjs-ai-agents
description: Use when an AI agent must create, inspect, implement, debug, or review a Next.js project. Resolves version-matched documentation before code changes and handles the generated nextjs-agent-rules block safely.
---

# Next.js AI Coding Agents

Treat the documentation bundled with the project's installed `next` package as the source of truth. Next.js APIs, conventions, defaults, and file structure may differ from training data or this skill.

## Required workflow

1. Start from the file or app being changed, not automatically from the repository root.
2. Find the nearest package root and inspect its `package.json`, lockfile, scripts, and installed `next/package.json`.
3. Resolve `node_modules/next/dist/docs/` from that package root. In monorepos, the package may be hoisted or unavailable from the workspace root.
4. Search and read only the guides relevant to the task before writing code.
5. Follow deprecation and migration notices from those local guides.
6. Inspect existing project conventions and tests before choosing an implementation.
7. Run the project's own narrow checks, then its required build/typecheck/lint/tests.

If the installed package or bundled docs are unavailable, inspect the package manager and workspace layout first. Do not guess an API from memory. Use official Next.js documentation that matches the installed version only as a fallback.

## New project bootstrap

- Respect the requested package manager, runtime, deployment target, and repository rules; do not impose a fixed stack.
- Inspect the current scaffolder's help and generated files instead of copying flags or versions from this skill.
- Add authentication, database, i18n, UI, testing, and Docker dependencies only when the project requires them.
- After installation, switch immediately to the bundled-doc workflow above and establish boundaries with `nextjs-clean-code`.

## Generated agent rules

`next dev` may write a managed block similar to:

```md
<!-- BEGIN:nextjs-agent-rules -->
...
<!-- END:nextjs-agent-rules -->
```

- Keep the managed block; deleting it only causes `next dev` to recreate the change.
- Do not manually edit text inside the markers.
- Put project-specific rules outside the markers.
- Resolve the generator from the installed package, typically under `next/dist/server/lib/generate-agent-files.js`, before making assumptions about its behavior.
- If the generated block is a legitimate project change, commit it with the related work so the tree remains clean.

## Efficient documentation lookup

- Search filenames and headings before opening whole guides.
- Read the smallest relevant set: routing, rendering, data, caching, security, deployment, or migration.
- For cross-cutting changes, record which local guides informed the decision.
- Prefer local runtime behavior and tests over examples copied from another Next.js version.

## Completion criteria

- The implementation matches the installed Next.js version.
- Deprecated behavior was not introduced.
- Managed agent rules remain intact.
- Verification uses repository-defined commands.
- Any unverified assumption is reported explicitly.
