---
name: hono
description: Use when developing a Hono backend — routing, middleware, Context API, choosing/verifying a runtime target (Cloudflare Workers, Deno, Bun, Node.js), validation with zod, or generating a type-safe RPC client with hc. Detect installed hono version before trusting version-specific API claims.
---

# Hono

Expert guidance on Hono — a small, fast, web-standards-based framework that runs on Cloudflare Workers, Deno, Bun, Node.js, and other edge runtimes.

**Precondition:** Hono iterates fast. Before asserting version-specific middleware/API behavior, check the installed version:

```shell
grep '"hono"' package.json
# or
npm ls hono
```

Canonical docs: `https://hono.dev/docs` — re-verify against the installed version rather than relying on memory alone.

## Core Routing API

```ts
import { Hono } from 'hono'

const app = new Hono()

app.get('/users/:id', (c) => c.json({ id: c.req.param('id') }))
app.post('/users', (c) => c.json({ created: true }, 201))
app.put('/users/:id', (c) => c.text('updated'))
app.delete('/users/:id', (c) => c.body(null, 204))

// Wildcard
app.get('/files/*', (c) => c.text('matched wildcard'))

// Route grouping (mount a sub-app under a base path)
const api = new Hono()
api.get('/users', (c) => c.json([]))
app.route('/api', api)
```

- Path params: `c.req.param('id')` (single) or `c.req.param()` (all as object).
- Query params: `c.req.query('q')` or `c.req.queries('tag')` for repeated keys.

## Middleware Pattern

```ts
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { jwt } from 'hono/jwt'

app.use('*', logger())
app.use('/api/*', cors())
app.use('/api/*', jwt({ secret: process.env.JWT_SECRET! }))

// Custom middleware signature — (c, next) => ...
app.use('*', async (c, next) => {
  const start = Date.now()
  await next()
  c.header('X-Response-Time', `${Date.now() - start}ms`)
})
```

- Middleware order matters — registered top-to-bottom, `await next()` continues the chain.
- Built-ins live under `hono/<name>` (e.g. `hono/cors`, `hono/logger`, `hono/jwt`, `hono/basic-auth`, `hono/compress`) — confirm availability/options against the installed version's docs, not memory.

## Context API (`c`)

Hono replaces Express-style `(req, res)` with a single `Context` object:

```ts
app.post('/echo', async (c) => {
  const body = await c.req.json()      // parse JSON body
  const header = c.req.header('X-Foo') // read a request header
  c.header('X-Custom', 'value')        // set a response header
  c.status(201)                        // set status (or pass as 2nd arg to c.json/c.text)
  return c.json({ echoed: body })
})

app.get('/plain', (c) => c.text('hello'))
app.get('/redirect', (c) => c.redirect('/plain'))
```

- `c.req` — request accessors (`param`, `query`, `header`, `json()`, `text()`, `parseBody()` for forms).
- `c.json()` / `c.text()` / `c.html()` / `c.body()` — response builders; all return a `Response`.
- `c.set()` / `c.get()` — pass typed data between middleware and handlers within one request (use with `Env`/`Variables` generics for type safety, not string-keyed globals).

## Runtime-Agnostic Design

The same `app` (route + middleware definitions) can target multiple runtimes — only the **entrypoint/adapter** differs:

```ts
// Cloudflare Workers — app.ts is the default export, no separate server needed
export default app

// Deno
Deno.serve(app.fetch)

// Bun
export default app // Bun reads `fetch` export automatically

// Node.js — requires the adapter package
import { serve } from '@hono/node-server'
serve(app)
```

Before assuming an API is available, check which runtime the project actually targets (`wrangler.toml` → Workers, `Deno.json`/`deno.json` → Deno, `bunfig.toml`/Bun lockfile → Bun, `@hono/node-server` dependency → Node). Node-specific APIs (`fs`, `child_process`, raw file system access) do **not** work on Cloudflare Workers or other edge runtimes — don't reach for them without confirming the target first.

## Hono RPC (`hc`)

Generates a type-safe client directly from server route definitions — useful in a monorepo where frontend and Hono backend share types without a codegen step:

```ts
// server.ts
const route = app.get('/users/:id', (c) => c.json({ id: c.req.param('id'), name: 'Alice' }))
export type AppType = typeof route

// client.ts (frontend)
import { hc } from 'hono/client'
import type { AppType } from '../server'

const client = hc<AppType>('http://localhost:8787')
const res = await client.users[':id'].$get({ param: { id: '123' } })
const data = await res.json() // typed as { id: string, name: string }
```

- Export the **chained** route type (`typeof route`), not the bare `app` — chaining is what carries per-route type info.
- Keep the exported route-building chain in one file/module boundary the client can import; don't scatter route definitions in a way that breaks the inferred type chain.

## Validation with zod

Commonly paired via `@hono/zod-validator`:

```ts
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const schema = z.object({ name: z.string().min(1), age: z.number().int().positive() })

app.post('/users', zValidator('json', schema), (c) => {
  const data = c.req.valid('json') // typed, validated
  return c.json(data, 201)
})
```

- Validation target is the first arg: `'json'`, `'query'`, `'param'`, `'header'`, `'form'`.
- On failure, `zValidator` short-circuits with a 400 by default — pass a callback as the 3rd arg to customize the error response shape.

## Architecture Note (SoC)

Hono route handlers are **Presentation/Delivery layer only** — same as controllers/handlers in any other framework used in this codebase. Keep them thin:

```ts
// ✅ thin handler — validate, delegate, map response
app.post('/orders', zValidator('json', createOrderSchema), async (c) => {
  const dto = c.req.valid('json')
  const result = await createOrderUseCase(dto) // Application layer
  return c.json(result, 201)
})

// ❌ business logic inline in the closure — belongs in Application/Domain
app.post('/orders', zValidator('json', createOrderSchema), async (c) => {
  const dto = c.req.valid('json')
  if (dto.total > 10000 && !dto.approvedBy) { /* ...business rule... */ }
  await db.insert(/* ... */)
  return c.json({ ok: true })
})
```

- Handlers: validate boundary input (via `zValidator` or manual checks), call a use case, map the result to a response. No business rules, no direct ORM/DB calls, no vendor payloads returned raw.
- Middleware for cross-cutting concerns (auth, logging, CORS) stays in Presentation too — it should not embed business rules either.

## Migration Notes

Canonical migration guide: `https://hono.dev/docs/MIGRATION` (mirrored at `https://github.com/honojs/hono/blob/main/docs/MIGRATION.md`). Before assuming an older or newer API pattern is correct, check this guide against the version range spanning the project's detected installed version and whatever version training data/memory might be biased toward.

Known major breaking-change milestones:

| Jump | Breaking changes |
|---|---|
| v3 → v4 | `c.jsonT()` removed → use `c.json()`; `c.stream()`/`c.streamText()` removed → use `stream()`/`streamText()` from `hono/streaming`; `c.env()` removed → use `getRuntimeKey()` from `hono/adapter`; `req.cookie()` removed → use `getCookie()` from `hono/cookie`; `app.showRoutes()` removed → use `showRoutes()` from `hono/dev`; Next.js adapter `hono/nextjs` removed → use `hono/vercel`; Cloudflare Workers `serveStatic` now requires a `manifest` option |
| v2 → v3 | `c.req` changed from being (close to) a raw `Request` to `HonoRequest` — use `c.req.raw` for the underlying `Request`; `StaticRouter` removed; Validator Middleware API changed; `serveStatic` moved from middleware to per-runtime adapters (`hono/cloudflare-workers`, `hono/bun`, etc.) |
| v4.3.x → v4.4.0 | No breaking change, but Deno distribution moved from `deno.land/x` to JSR (`jsr:@hono/hono`) — update Deno imports accordingly |

This list is not exhaustive — always cross-check the official migration guide for the exact version jump in the project, since Hono ships breaking changes fairly often across majors.

## Quick Reference

| Concern | API |
|---|---|
| Route | `app.get/post/put/delete(path, handler)` |
| Group | `app.route('/prefix', subApp)` |
| Path param | `c.req.param('name')` |
| Query param | `c.req.query('name')` |
| JSON body | `await c.req.json()` |
| JSON response | `c.json(data, status?)` |
| Text response | `c.text(str, status?)` |
| Set header | `c.header('X-Foo', 'bar')` |
| Set status | `c.status(201)` (or as 2nd arg to `c.json`/`c.text`) |
| Middleware | `app.use(path?, (c, next) => ...)` |
| Node entrypoint | `@hono/node-server`'s `serve(app)` |
| Type-safe client | `hc<AppType>(baseUrl)` from `hono/client` |
| Validation | `zValidator(target, zodSchema)` from `@hono/zod-validator` |
