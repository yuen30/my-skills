---
name: nextjs-production-checklist
description: Use before releasing a Next.js application to review correctness, security, performance, caching, accessibility, SEO, observability, build output, and deployment readiness against the installed version.
---

# Next.js Production Review

This is a verification workflow, not a static API checklist. Read the installed Next.js guides relevant to the application's router, rendering, caching, runtime, and deployment target before judging readiness.

## Establish the release target

1. Identify the app package, installed Next.js version, router, runtime, package manager, and deployment topology.
2. Inspect repository scripts, CI workflow, environment schema, container or platform configuration, and rollback path.
3. Define critical user journeys and production acceptance criteria.
4. Record what can be verified locally, in CI, and only after deployment.

## Correctness gates

- Run repository-defined formatting, lint, typecheck, unit, integration, E2E, and production build commands.
- Test production output using the project's actual start or preview path.
- Verify loading, empty, error, not-found, and unauthorized states for critical routes.
- Check route, Server Action, Route Handler, and cache behavior against local bundled docs.
- Resolve deprecation warnings and generated agent-rule changes.

## Security gates

- Apply the Next.js Data Security Review skill to public and privileged boundaries.
- Confirm secrets remain server-side and required environment variables fail fast.
- Verify authentication, resource authorization, validation, rate limits, headers, CSP, and error redaction.
- Confirm user-specific or tenant-specific data cannot leak through caching or logs.

## Performance and caching

- Measure before optimizing; capture comparable build, bundle, field, or lab evidence.
- Inspect client boundaries, dependency weight, waterfalls, image/font/script behavior, and route rendering mode.
- Verify cache lifetime, invalidation, personalization, and multi-instance behavior match product requirements.
- Test cold start and degraded upstream behavior where operationally relevant.

## Product quality

- Verify keyboard navigation, focus, labels, contrast, reduced motion, and responsive layouts.
- Check metadata, canonical URLs, robots, sitemap, social previews, and structured data where applicable.
- Confirm analytics and consent behavior do not expose sensitive data.
- Validate locale-aware routing and formatting for every supported locale.

## Operations

- Verify health/readiness behavior, structured logs, traces, metrics, alert ownership, and useful failure diagnostics.
- Confirm deployment order, migrations, backward compatibility, rollback, and artifact immutability.
- Test required volumes, permissions, proxies, CDN behavior, streaming, and graceful shutdown for the target environment.
- Ensure CI uses the lockfile and caches only safe, reproducible artifacts.

## Final report

Classify each gate as:

- **Verified** — supported by a command, test, artifact, or live observation.
- **Not verified** — requires an environment or access not available.
- **Failed** — blocks release until resolved.
- **Accepted risk** — explicitly owned with impact and follow-up.

Do not declare production-ready when required checks are missing or failures are hidden behind assumptions.
