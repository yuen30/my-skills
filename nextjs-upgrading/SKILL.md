---
name: nextjs-upgrading
description: Use when upgrading Next.js, React, or related tooling; planning a major-version migration; applying codemods; or resolving deprecations without relying on stale version-specific instructions.
---

# Next.js Upgrading

Derive upgrade commands and breaking changes from the installed package and its bundled migration guides. Do not treat commands or version tables remembered by the model as authoritative.

## Prepare

1. Require a clean or clearly understood working tree.
2. Identify every Next.js app in the workspace and its package manager.
3. Record installed versions of Next.js, React, React DOM, TypeScript, lint tooling, adapters, and major integrations.
4. Inventory App Router, Pages Router, hybrid routes, custom server, runtime targets, experimental flags, and deprecated APIs.
5. Read the migration guides under each installed `node_modules/next/dist/docs/`.
6. Define the target version and verify its official requirements before changing dependencies.

## Execute incrementally

1. Upgrade framework dependencies with the repository's package manager.
2. Review available official codemods for the exact source and target versions.
3. Inspect codemod diffs before accepting them; never combine them blindly with unrelated refactors.
4. Resolve compiler and type errors in bounded groups.
5. Update configuration, runtime, CI, containers, and deployment adapters only where required.
6. Keep compatibility shims temporary and document their removal condition.

## Preserve generated rules

Run the relevant development workflow and inspect whether Next.js created or refreshed the `nextjs-agent-rules` block. Keep the managed block intact and commit legitimate generated changes with the upgrade.

## Verification ladder

Use repository-defined commands in this order where available:

1. install from lockfile
2. focused tests for migrated behavior
3. typecheck and lint
4. full test suite
5. production build and production-like start
6. critical E2E journeys
7. deployment smoke tests and observability checks

Compare routing, rendering, caching, authentication, mutations, error handling, and asset behavior before and after the upgrade.

## Risk controls

- Separate framework upgrade commits from product refactors when practical.
- Do not adopt canary or experimental features in production without explicit scope and rollback.
- Preserve lockfile integrity and review transitive dependency changes.
- Check third-party compatibility rather than assuming peer dependency warnings are harmless.
- Stop when migration documentation conflicts with observed runtime behavior; reproduce and narrow the discrepancy first.

## Handover

Report source and target versions, migration guides used, codemods applied, manual changes, verification evidence, remaining deprecations, rollback path, and known risks.
