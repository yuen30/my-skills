---
name: Next.js Streaming
description: Expert guidance on streaming in Next.js — Suspense boundaries, loading.js, static shell, progressive rendering, Web Vitals, and infrastructure requirements.
---

# Next.js Streaming

Expert guidance on streaming in Next.js — Suspense boundaries, loading.js, static shell, progressive rendering, Web Vitals, and infrastructure requirements.

@doc-version: 16.2.6

## Core Concepts

Streaming ส่ง HTML เป็น chunks ทีละส่วน — browser เริ่ม render ขณะ server ยังสร้าง content ที่เหลือ:
- Static parts (layouts, nav, fallbacks) ส่งทันที
- Dynamic parts stream เข้ามาเมื่อ resolve
- แต่ละ `<Suspense>` boundary = independent streaming point

## How It Works

### Request Flow

```
1. Browser requests page
2. Server sends static shell ทันที:
   - Layouts, navigation, Suspense fallbacks
   - <link>, <script> tags (early resource discovery)
3. Server continues rendering async components
4. Each Suspense boundary resolves → stream HTML + swap script
5. Browser swaps fallback → real content (no JS needed for swap)
6. React hydrates each boundary independently
```

### Two Streams

| Stream | Content | When |
|--------|---------|------|
| HTML stream | Progressive HTML chunks + swap scripts | Initial page load |
| Component payload | Serialized React tree (RSC) | Embedded in HTML + client navigation |

### Static Shell

ทุกอย่างที่ render ก่อน async work = **static shell**:
- Layouts, navigation
- Suspense fallbacks
- Prerendered at build time (with Cache Components)
- Served instantly from CDN

## Guidelines

### 1. Page-level Streaming (`loading.js`)

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded mb-4" />
      <div className="h-4 w-full bg-gray-200 rounded mb-2" />
      <div className="h-4 w-2/3 bg-gray-200 rounded" />
    </div>
  )
}
```

- Auto-wraps `page.js` ใน `<Suspense>`
- Layout renders ทันที (static shell)
- Skeleton แสดงจนกว่า page resolves
- Prefetched สำหรับ instant navigation

### 2. Granular Streaming (`<Suspense>`)

#### Parallel Boundaries (Independent)

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react'

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <div className="grid grid-cols-2 gap-4">
        <Suspense fallback={<p>Loading revenue...</p>}>
          <Revenue />
        </Suspense>
        <Suspense fallback={<p>Loading orders...</p>}>
          <RecentOrders />
        </Suspense>
      </div>
      <Suspense fallback={<p>Loading recommendations...</p>}>
        <Recommendations />
      </Suspense>
    </div>
  )
}
```

- แต่ละ boundary resolve อิสระ
- ไม่ block กัน — เร็วสุดมาก่อน

#### Nested Boundaries (Progressive Detail)

```tsx
export default async function ProductPage({ params }) {
  const { id } = await params
  return (
    <div>
      <h1>Product</h1>
      <Suspense fallback={<p>Loading details...</p>}>
        <ProductDetails id={id} />
        <Suspense fallback={<p>Loading reviews...</p>}>
          <Reviews productId={id} />
        </Suspense>
      </Suspense>
    </div>
  )
}
```

- Outer resolves → inner becomes visible
- Progressive reveal: details → reviews

### 3. Push Dynamic Access Down

```tsx
// ❌ Bad — await ที่ top blocks ทุกอย่าง
export default async function Layout({ children }) {
  const cookieStore = await cookies() // Blocks entire layout!
  return <div>{children}</div>
}

// ✅ Good — pass promise down, await ใน Suspense
export default function Layout({ children }) {
  const cookieStore = cookies() // Start work, don't await
  return (
    <div>
      <Nav>
        <Suspense fallback={<p>Loading user...</p>}>
          <UserMenu cookiePromise={cookieStore} />
        </Suspense>
      </Nav>
      {children}
    </div>
  )
}
```

**หลักการ:** Defer dynamic access ไปที่ component ที่ต้องการจริงๆ — ภายใน Suspense boundary

### 4. Streaming Data to Client (`use()`)

```tsx
// app/dashboard/page.tsx (Server Component)
import { Suspense } from 'react'
import { StatsChart } from './stats-chart'

export default function Dashboard() {
  const statsPromise = getStats() // Start fetch, don't await
  return (
    <Suspense fallback={<p>Loading chart...</p>}>
      <StatsChart dataPromise={statsPromise} />
    </Suspense>
  )
}
```

```tsx
// app/dashboard/stats-chart.tsx (Client Component)
'use client'
import { use } from 'react'

export function StatsChart({ dataPromise }: { dataPromise: Promise<Stats> }) {
  const stats = use(dataPromise) // Suspends until resolved
  return <div>{/* render chart */}</div>
}
```

### 5. Streaming in Route Handlers

```ts
// app/api/stream/route.ts
export async function GET() {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(encoder.encode(`Chunk ${i + 1}\n`))
        await new Promise((resolve) => setTimeout(resolve, 200))
      }
      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Content-Type-Options': 'nosniff',
    },
  })
}
```

## Web Vitals Impact

| Metric | Without Streaming | With Streaming |
|--------|:-:|:-:|
| TTFB | Slowest query | Shell render time |
| FCP | After all data | Immediate (shell) |
| LCP | Depends on data | Keep LCP outside Suspense |
| CLS | N/A | Match skeleton dimensions |
| INP | Single hydration pass | Split hydration (per boundary) |

**Tips:**
- LCP element (hero image, heading) → **outside** Suspense boundaries
- Skeleton fallbacks → **match dimensions** of final content (prevent CLS)
- More Suspense boundaries → better INP (smaller hydration tasks)

## `loading.js` vs `<Suspense>`

| | `loading.js` | `<Suspense>` |
|---|---|---|
| Scope | Entire page | Any component |
| Setup | Drop in file | Wrap explicitly |
| Navigation | Prefetched as instant fallback | Not prefetched by default |
| Best for | Pages where nothing renders without data | Most pages (granular control) |

> **แนะนำ:** ใช้ `<Suspense>` ใกล้ dynamic access ที่สุด — `loading.js` เป็น fallback สุดท้าย

## The HTTP Contract

เมื่อ streaming เริ่ม → status code (200) ถูกส่งแล้ว → **เปลี่ยนไม่ได้**:

- `notFound()` mid-stream → inject `<meta name="robots" content="noindex">` (ไม่ใช่ 404)
- `redirect()` mid-stream → client-side redirect (ไม่ใช่ HTTP redirect)
- Error mid-stream → `error.js` boundary catches (status ยังเป็น 200)

**แก้ไข:** เรียก `notFound()` / validate **ก่อน** Suspense boundary:

```tsx
export default async function Page({ params }) {
  const { slug } = await params
  const exists = await checkSlugExists(slug) // Fast check
  if (!exists) notFound() // Real 404 (before streaming starts)

  return (
    <Suspense fallback={<p>Loading...</p>}>
      <PostContent slug={slug} />
    </Suspense>
  )
}
```

## Infrastructure Requirements

| Layer | Requirement |
|-------|-------------|
| Reverse proxy (nginx) | `X-Accel-Buffering: no` |
| Load balancer | Support chunked transfer / HTTP/2 |
| CDN | Pass through chunked responses |
| Serverless | Streaming mode enabled (e.g., AWS Lambda) |
| Compression | Flush aggressively (gzip/brotli may buffer) |

```js
// next.config.js — disable nginx buffering
module.exports = {
  async headers() {
    return [{
      source: '/:path*{/}?',
      headers: [{ key: 'X-Accel-Buffering', value: 'no' }],
    }]
  },
}
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `loading.js` | Full-page skeleton |
| Sibling `<Suspense>` | Independent parallel sections |
| Nested `<Suspense>` | Progressive detail reveal |
| Pass promise + `use()` | Stream data to Client Component |
| Route Handler stream | SSE, file download, raw chunks |
| Push dynamic down | Maximize static shell |

## สรุป

1. **Streaming = send HTML chunks** ทีละส่วน — browser render ทันที
2. **Static shell** ส่งก่อน — layouts, nav, fallbacks
3. **`<Suspense>`** = streaming point — แต่ละ boundary อิสระ
4. **Push dynamic access down** — maximize static shell
5. **`loading.js`** = page-level fallback, prefetched
6. **Web Vitals:** LCP outside Suspense, match skeleton dimensions, split hydration
7. **HTTP contract:** status code ส่งแล้วเปลี่ยนไม่ได้ — validate ก่อน Suspense
8. **Infrastructure:** disable buffering ทั้ง chain
