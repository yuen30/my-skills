---
name: nextjs-data-security
description: Use when implementing or auditing Next.js authentication, authorization, Server Actions, Route Handlers, data access, environment variables, caching, CSP, and server-to-client data exposure.
---

# Next.js Data Security Review

Use the installed Next.js documentation as the API source of truth; this skill defines the review procedure and security invariants.

## Review workflow

1. Resolve the installed `next` package from the affected app.
2. Read the relevant bundled guides for authentication, data security, Server Actions, Route Handlers, environment variables, caching, proxy behavior, and CSP.
3. Map every external entry point and trust boundary.
4. Trace sensitive data from request to storage, cache, logs, and client output.
5. Report findings with file evidence, impact, exploit path, and smallest safe remediation.

## Required invariants

- Authenticate identity and authorize the requested resource or action separately.
- Re-authorize every mutation inside its Server Action, Route Handler, or use case.
- Treat route params, search params, headers, cookies, form data, and JSON bodies as untrusted input.
- Validate shape, size, allowed values, and ownership before side effects.
- Return minimal DTOs; never pass raw ORM records or vendor responses to Client Components.
- Keep secrets and privileged clients server-only.
- Never place secrets in browser-exposed environment variables.
- Keep authorization in the use case or data-access boundary, not only in layouts, Proxy, middleware, or hidden UI.
- Isolate user-specific cached data by identity and authorization context, or do not cache it.
- Apply rate limits and idempotency where expensive or repeatable mutations create risk.

## Boundary inventory

Audit at least:

- Server Actions and form actions
- Route Handlers and legacy API Routes
- dynamic route params and search params
- authentication callbacks and session refresh
- redirects, rewrites, Proxy, and middleware
- uploads, downloads, webhooks, and third-party callbacks
- environment variable reads
- server-to-client props and serialized errors
- caches, revalidation, logs, analytics, and traces

## Defense-in-depth

- Use server-only import guards where supported by the installed version.
- Use CSP appropriate to the deployment and rendering model.
- Treat tainting or framework-generated action protections as additional controls, not substitutes for validation and authorization.
- Avoid exposing internal identifiers when a public identifier or scoped lookup is sufficient.
- Map errors to stable public responses without leaking stack traces, queries, tokens, or private records.

## Verification

- Add or run negative tests for unauthenticated, unauthorized, cross-tenant, malformed, replayed, and oversized requests.
- Verify secrets are absent from client bundles and generated output.
- Verify cached responses cannot cross users or tenants.
- Re-run repository-defined typecheck, tests, lint, and build commands.

## Report format

Order findings by severity. For each finding include location, violated invariant, realistic impact, evidence, and remediation. Distinguish confirmed vulnerabilities from hardening suggestions.
