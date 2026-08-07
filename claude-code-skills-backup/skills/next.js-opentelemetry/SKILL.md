---
name: Next.js OpenTelemetry
description: Expert guidance on instrumenting Next.js with OpenTelemetry — @vercel/otel, manual setup, custom spans, default spans, exporters, and deployment.
---

# Next.js OpenTelemetry

Expert guidance on instrumenting Next.js with OpenTelemetry — @vercel/otel, manual setup, custom spans, default spans, exporters, and deployment.

@doc-version: 16.2.6

## Core Concepts

OpenTelemetry เป็น platform-agnostic standard สำหรับ observability:
- **Traces** — track request flow ข้าม services
- **Spans** — unit of work ภายใน trace
- **Exporters** — ส่ง telemetry data ไป backend (Jaeger, Datadog, etc.)

Next.js มี built-in OpenTelemetry instrumentation — auto-create spans สำหรับ routes, fetches, rendering

## Guidelines

### 1. Quick Setup with `@vercel/otel`

```bash
npm install @vercel/otel @opentelemetry/sdk-logs @opentelemetry/api-logs @opentelemetry/instrumentation
```

```ts
// instrumentation.ts (project root)
import { registerOTel } from '@vercel/otel'

export function register() {
  registerOTel({ serviceName: 'next-app' })
}
```

เสร็จ — ทำงานทั้งบน Vercel และ self-hosted

### 2. Manual OpenTelemetry Configuration

สำหรับ control เต็มที่:

```bash
npm install @opentelemetry/sdk-node @opentelemetry/resources @opentelemetry/semantic-conventions @opentelemetry/sdk-trace-node @opentelemetry/exporter-trace-otlp-http
```

```ts
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./instrumentation.node')
  }
}
```

```ts
// instrumentation.node.ts
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { resourceFromAttributes } from '@opentelemetry/resources'
import { NodeSDK } from '@opentelemetry/sdk-node'
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-node'
import { ATTR_SERVICE_NAME } from '@opentelemetry/semantic-conventions'

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: 'next-app',
  }),
  spanProcessor: new SimpleSpanProcessor(new OTLPTraceExporter()),
})

sdk.start()
```

> `NodeSDK` ไม่ compatible กับ Edge Runtime — ต้อง conditional import ด้วย `NEXT_RUNTIME === 'nodejs'`

### 3. Custom Spans

```bash
npm install @opentelemetry/api
```

```ts
import { trace } from '@opentelemetry/api'

export async function fetchGithubStars() {
  return await trace
    .getTracer('nextjs-example')
    .startActiveSpan('fetchGithubStars', async (span) => {
      try {
        const res = await fetch('https://api.github.com/repos/vercel/next.js')
        const data = await res.json()
        span.setAttribute('github.stars', data.stargazers_count)
        return data.stargazers_count
      } catch (error) {
        span.recordException(error as Error)
        throw error
      } finally {
        span.end()
      }
    })
}
```

### 4. Default Spans (Auto-instrumented)

Next.js สร้าง spans อัตโนมัติ:

| Span | Type | Description |
|------|------|-------------|
| `[method] [route]` | `BaseServer.handleRequest` | Root span ทุก incoming request |
| `render route (app) [route]` | `AppRender.getBodyResult` | Rendering route ใน App Router |
| `fetch [method] [url]` | `AppRender.fetch` | Fetch requests ใน code |
| `executing api route (app) [route]` | `AppRouteRouteHandlers.runHandler` | API Route Handler execution |
| `getServerSideProps [route]` | `Render.getServerSideProps` | Pages Router SSR |
| `getStaticProps [route]` | `Render.getStaticProps` | Pages Router SSG |
| `render route (pages) [route]` | `Render.renderDocument` | Pages Router rendering |
| `generateMetadata [page]` | `ResolveMetadata.generateMetadata` | Metadata generation |
| `resolve page components` | `NextNodeServer.findPageComponents` | Resolving page components |
| `resolve segment modules` | `NextNodeServer.getLayoutOrPageModule` | Loading layout/page modules |
| `start response` | `NextNodeServer.startResponse` | First byte sent |

#### Custom Attributes

| Attribute | Description |
|-----------|-------------|
| `next.span_name` | Span name |
| `next.span_type` | Unique span type identifier |
| `next.route` | Route pattern (e.g., `/[param]/user`) |
| `next.rsc` | Whether request is RSC (true/false) |
| `next.page` | Internal page identifier |

### 5. Environment Variables

| Variable | Purpose |
|----------|---------|
| `NEXT_OTEL_VERBOSE=1` | Show more spans (default: minimal) |
| `NEXT_OTEL_FETCH_DISABLED=1` | Disable fetch span instrumentation |

### 6. Testing Locally

ใช้ [OpenTelemetry dev environment](https://github.com/vercel/opentelemetry-collector-dev-setup):

```bash
# Start collector + Jaeger UI
docker compose up -d

# Run Next.js with verbose tracing
NEXT_OTEL_VERBOSE=1 npm run dev

# View traces at http://localhost:16686 (Jaeger UI)
```

### 7. Deployment

#### Vercel

ทำงาน out of the box — connect observability provider ใน Vercel dashboard

#### Self-hosted

1. Spin up OpenTelemetry Collector
2. Configure collector ให้รับ data จาก Next.js app
3. Set `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable

```env
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318
```

#### Custom Exporter (ไม่ต้องมี Collector)

```ts
// instrumentation.node.ts
import { NodeSDK } from '@opentelemetry/sdk-node'
import { DatadogExporter } from 'datadog-exporter' // example

const sdk = new NodeSDK({
  spanProcessor: new SimpleSpanProcessor(new DatadogExporter()),
})

sdk.start()
```

### 8. Common Observability Backends

| Backend | Exporter Package |
|---------|-----------------|
| Jaeger | `@opentelemetry/exporter-trace-otlp-http` |
| Datadog | `@datadog/opentelemetry-exporter` |
| New Relic | `@newrelic/opentelemetry-exporter` |
| Honeycomb | `@honeycombio/opentelemetry-node` |
| Grafana Tempo | `@opentelemetry/exporter-trace-otlp-http` |
| AWS X-Ray | `@opentelemetry/exporter-trace-otlp-http` |

### 9. Production Configuration

```ts
// instrumentation.node.ts
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { resourceFromAttributes } from '@opentelemetry/resources'
import { NodeSDK } from '@opentelemetry/sdk-node'
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-node'
import { ATTR_SERVICE_NAME, ATTR_DEPLOYMENT_ENVIRONMENT } from '@opentelemetry/semantic-conventions'

const sdk = new NodeSDK({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: 'next-app',
    [ATTR_DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV,
  }),
  // BatchSpanProcessor สำหรับ production (efficient)
  spanProcessor: new BatchSpanProcessor(
    new OTLPTraceExporter({
      url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
    })
  ),
})

sdk.start()
```

> **Production:** ใช้ `BatchSpanProcessor` แทน `SimpleSpanProcessor` — batch spans ก่อนส่ง (efficient กว่า)

## Quick Reference

| Setup | Complexity | Edge Support |
|-------|:-:|:-:|
| `@vercel/otel` | ง่าย | ✅ |
| Manual `NodeSDK` | ปานกลาง | ❌ (Node.js only) |
| Custom exporter | ซับซ้อน | Depends |

## สรุป

1. **`@vercel/otel`** — quickest setup, ทำงานทั้ง Vercel + self-hosted
2. **Manual setup** — full control, Node.js runtime only
3. **Custom spans** — `trace.getTracer().startActiveSpan()`
4. **Default spans** — auto-instrumented (routes, fetches, rendering)
5. **`NEXT_OTEL_VERBOSE=1`** — ดู spans เพิ่มเติม
6. **Production** — ใช้ `BatchSpanProcessor` + OTLP exporter
7. **Conditional import** — `NEXT_RUNTIME === 'nodejs'` สำหรับ Node.js-only code
