---
name: http-status-codes
description: HTTP status code reference (1xx-5xx), REST status conventions per operation, and frontend error handling. Use when choosing status codes for API endpoints, designing error responses, or handling fetch/axios errors.
---

# HTTP Status Codes

Opinionated REST rules. Standard code meanings are assumed known.

## Pick the right code

- **401 vs 403**: 401 = not authenticated (no/expired/invalid token). 403 = authenticated but not allowed. Never 403 for a missing login.
- **404 vs 403 for hidden resources**: if revealing existence is a leak (other tenant's record, private resource), return 404, not 403.
- **400 vs 422**: 400 = unreadable request (malformed JSON, wrong content-type, bad query syntax). 422 = parsed fine but fails validation. The client treats 400 as a code bug and 422 as user input to fix.
- **409**: valid request that conflicts with current state (duplicate unique field, stale version/ETag, delete with dependents).
- **POST that creates**: `201` + `Location` header + created resource body. Never `200`. Non-creating actions (`/login`, `/search`) use `200`.
- **Async work** (queue/background job): `202` plus a status URL, not `200`.
- **PUT/PATCH**: `200` with body, or `204` if nothing to return.
- **DELETE**: `204`. Repeating a delete: pick one (204 or 404) and keep it consistent.
- **GET unknown id**: `404`, never `200` with `null`/empty body.
- **429 / 503**: always send `Retry-After`.
- **5xx is for server faults only.** Never 500 for validation or not-found. Upstream failure: 502/504.

## Error response shape

Use one shape for every error (prefer RFC 9457 `application/problem+json`):

```json
{ "type": "validation_error", "title": "Invalid input", "status": 422,
  "detail": "...", "errors": { "email": ["must be a valid email"] } }
```

- Stable machine-readable `type`/`code`; human `message` is not for branching.
- Field errors keyed by field name. No stack traces or internals in 5xx bodies.

## Frontend rules

- `fetch` does not throw on 4xx/5xx: check `res.ok`. `axios` throws: read `error.response?.status`.
- Handle `204` before calling `res.json()`; parse error bodies with `.catch(() => null)`.
- 401: clear session and redirect to login. 422: show field errors. 429: honour `Retry-After`.
- Auto-retry exactly these four: 429, 502, 503, 504 (with backoff). Never retry anything else.
- Map statuses to typed errors (`AuthError`, `ValidationError`, `RateLimitError`, `ApiError`) in one place; do not scatter `status ===` checks through UI code.

## Common mistakes

- `200` with `{ "success": false }`: hides failure from cache, monitoring, retry, gateways.
- 500 for client errors: causes false alerts and masks real outages.
- Mixing 401/403, 400/422 (see above).
- Leaking resource existence through 403 vs 404.
