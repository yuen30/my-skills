---
name: Next.js Instrumentation
description: Expert guidance on setting up instrumentation in Next.js — server startup code, OpenTelemetry, runtime-specific imports, and monitoring integration.
---

# Next.js Instrumentation

Expert guidance on setting up instrumentation in Next.js — server startup code, OpenTelemetry, runtime-specific imports, and monitoring integration.

@doc-version: 16.2.6

## Core Concepts

Instrumentation ให้คุณรัน code ตอน server startup — ใช้สำหรับ:
- Monitoring and logging tools
- OpenTelemetry integration
- Database connection pools
- Error tracking services (Sentry, Datadog)
- Performance monitoring

## Guidelines

### 1. Convention

สร้าง `instrumentation.ts` ที่ **root directory** (หรือใน `src/`):

```
project/
├── instrumentation.ts    # ← ที่นี่
├── app/
├── next.config.ts
└── package.json
```

หรือ:

```
project/
├── src/
│   ├── instrumentation.ts  # ← หรือที่นี่
│   ├── app/
│   └── pages/
└── next.config.ts
```

> **สำคัญ:** ไม่ใช่ใน `app/` หรือ `pages/` — ต้องอยู่ root level

### 2. Basic Setup

Export `register` function — ถูกเรียก **ครั้งเดียว** ตอน server instance เริ่มต้น:

```ts
// instrumentation.ts
import { registerOTel } from '@vercel/otel'

export function register() {
  registerOTel('next-app')
}
```

- ถูกเรียกก่อน server พร้อมรับ requests
- ต้อง complete ก่อน server เริ่มทำงาน

### 3. OpenTelemetry Integration

```bash
npm install @vercel/otel @opentelemetry/sdk-node @opentelemetry/resources
```

```ts
// instrumentation.ts
import { registerOTel } from '@vercel/otel'

export function register() {
  registerOTel('my-next-app')
}
```

#### Custom OpenTelemetry Setup

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { NodeSDK } = await import('@opentelemetry/sdk-node')
    const { Resource } = await import('@opentelemetry/resources')

    const sdk = new NodeSDK({
      resource: new Resource({
        'service.name': 'my-next-app',
      }),
      // Add exporters, processors, etc.
    })

    sdk.start()
  }
}
```

### 4. Runtime-specific Code

`register` ถูกเรียกในทุก environment — ใช้ `NEXT_RUNTIME` เพื่อ conditional import:

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./instrumentation-node')
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    await import('./instrumentation-edge')
  }
}
```

```ts
// instrumentation-node.ts
import * as Sentry from '@sentry/node'

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
})
```

```ts
// instrumentation-edge.ts
// Edge-compatible monitoring setup
```

| `NEXT_RUNTIME` | Environment |
|----------------|-------------|
| `'nodejs'` | Node.js server |
| `'edge'` | Edge Runtime |

### 5. Side Effects Import

Import files ที่มี side effects ใน `register` function (ไม่ใช่ top-level):

```ts
// instrumentation.ts
export async function register() {
  // ✅ Import ใน register — controlled side effects
  await import('package-with-side-effect')
}
```

> **ทำไมไม่ import ที่ top-level?** เพื่อ colocate side effects ในที่เดียว และหลีกเลี่ยง unintended consequences

### 6. Common Use Cases

#### Error Tracking (Sentry)

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const Sentry = await import('@sentry/node')
    Sentry.init({
      dsn: process.env.SENTRY_DSN,
      environment: process.env.NODE_ENV,
      tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
    })
  }
}
```

#### Database Connection Pool

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { initDB } = await import('./lib/db')
    await initDB()
  }
}
```

#### Custom Logger

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { initLogger } = await import('./lib/logger')
    initLogger({
      level: process.env.LOG_LEVEL || 'info',
      service: 'my-next-app',
    })
  }
}
```

#### Metrics Collection

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { collectDefaultMetrics } = await import('prom-client')
    collectDefaultMetrics()
  }
}
```

### 7. Client-side Instrumentation

สำหรับ client-side monitoring ใช้ `instrumentation-client.ts` แทน:

```ts
// instrumentation-client.ts (separate file)
// Runs before frontend code starts

// Analytics
posthog.init('phc_xxx', { api_host: 'https://app.posthog.com' })

// Error tracking
window.addEventListener('error', (event) => {
  reportError(event.error)
})
```

| File | Runs On | Purpose |
|------|---------|---------|
| `instrumentation.ts` | Server (startup) | Server monitoring, DB pools, OTel |
| `instrumentation-client.ts` | Client (before app) | Analytics, client error tracking |

## Quick Reference

| Feature | Detail |
|---------|--------|
| File location | Project root or `src/` |
| Export | `register` function |
| Called | Once per server instance startup |
| Timing | Before server accepts requests |
| Runtime check | `process.env.NEXT_RUNTIME` |
| Async | ✅ Supports async/await |
| `pageExtensions` | Must match if configured |

## สรุป

1. **สร้าง `instrumentation.ts`** ที่ project root
2. **Export `register` function** — เรียกครั้งเดียวตอน startup
3. **ใช้ `NEXT_RUNTIME`** — conditional import ตาม environment
4. **Import ใน `register`** — ไม่ใช่ top-level (controlled side effects)
5. **Use cases:** OpenTelemetry, Sentry, DB pools, custom loggers
6. **Client-side:** ใช้ `instrumentation-client.ts` แยกต่างหาก
