---
name: Next.js Prefetching
description: Expert guidance on configuring prefetching in Next.js — automatic, manual, hover-triggered, disabled, client cache, and troubleshooting patterns.
---

# Next.js Prefetching

Expert guidance on configuring prefetching in Next.js — automatic, manual, hover-triggered, disabled, client cache, and troubleshooting patterns.

@doc-version: 16.2.6

## Core Concepts

Prefetching โหลด resources ของหน้าถัดไปล่วงหน้า — เมื่อ user คลิก navigation จะรู้สึก instant:
- Next.js code-split ตาม routes อัตโนมัติ
- เฉพาะ code ของ current route ถูกโหลด
- Routes อื่นถูก prefetch ใน background
- Client-side transition ไม่มี full page reload

## Static vs Dynamic Prefetching

| | Static Page | Dynamic Page |
|---|---|---|
| Prefetched | ✅ Full route | ❌ (ยกเว้นมี `loading.js`) |
| Client Cache TTL | 5 min (default) | Off (ยกเว้น enable `staleTimes`) |
| Server roundtrip on click | ❌ No | ✅ Yes (streamed) |

## Guidelines

### 1. Automatic Prefetch (Default)

```tsx
import Link from 'next/link'

export default function NavLink() {
  return <Link href="/about">About</Link>
}
```

| Context | Prefetched Payload | Client Cache TTL |
|---------|-------------------|-----------------|
| No `loading.js` | Entire page | Until app reload |
| With `loading.js` | Layout to first loading boundary | 30s (configurable) |

- ทำงานเฉพาะ production
- Prefetch เมื่อ Link เข้า viewport

### 2. Manual Prefetch (`router.prefetch`)

```tsx
'use client'

import { useRouter } from 'next/navigation'

export function PricingCard() {
  const router = useRouter()

  return (
    <div onMouseEnter={() => router.prefetch('/pricing')}>
      <a href="/pricing">View Pricing</a>
    </div>
  )
}
```

ใช้สำหรับ:
- Links นอก viewport
- Response to analytics/scroll
- Custom components ที่ไม่ใช่ `<Link>`

### 3. Hover-triggered Prefetch

Prefetch เมื่อ hover แทน viewport (ประหยัด resources):

```tsx
'use client'

import Link from 'next/link'
import { useState } from 'react'

export function HoverPrefetchLink({
  href,
  children,
}: {
  href: string
  children: React.ReactNode
}) {
  const [active, setActive] = useState(false)

  return (
    <Link
      href={href}
      prefetch={active ? null : false}
      onMouseEnter={() => setActive(true)}
    >
      {children}
    </Link>
  )
}
```

- `prefetch={false}` → ไม่ prefetch ตอน viewport
- `prefetch={null}` → restore default prefetching เมื่อ hover
- สมดุลระหว่าง performance กับ resource usage

### 4. Extending Link (`onInvalidate`)

Recreate `<Link>` behavior ด้วย `useRouter`:

```tsx
'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

function ManualPrefetchLink({
  href,
  children,
}: {
  href: string
  children: React.ReactNode
}) {
  const router = useRouter()

  useEffect(() => {
    let cancelled = false
    const poll = () => {
      if (!cancelled) router.prefetch(href, { onInvalidate: poll })
    }
    poll()
    return () => { cancelled = true }
  }, [href, router])

  return (
    <a
      href={href}
      onClick={(event) => {
        event.preventDefault()
        router.push(href)
      }}
    >
      {children}
    </a>
  )
}
```

`onInvalidate` — เรียกเมื่อ Next.js สงสัยว่า cached data stale → refresh prefetch

### 5. Disabled Prefetch

```tsx
// ปิด prefetch สำหรับ link เฉพาะ
<Link prefetch={false} href={`/blog/${post.id}`}>
  {post.title}
</Link>
```

```tsx
// Wrapper component สำหรับ consistent usage
'use client'

import Link, { LinkProps } from 'next/link'

function NoPrefetchLink({
  prefetch,
  ...rest
}: LinkProps & { children: React.ReactNode }) {
  return <Link {...rest} prefetch={false} />
}
```

**ใช้เมื่อ:**
- รายการ links ยาวมาก (infinite scroll, tables)
- Footer links ที่ไม่ค่อยถูกคลิก
- ต้องการประหยัด bandwidth

### 6. Prefetch Optimizations

#### Client Cache

- Prefetched RSC payloads เก็บ in-memory ตาม route segments
- Navigate ระหว่าง sibling routes → reuse parent layout, fetch เฉพาะ leaf page
- ลด network traffic

#### Prefetch Scheduler (Priority Queue)

1. Links ใน viewport
2. Links ที่ user hover/touch (intent)
3. Newer links แทนที่ older ones
4. Links ที่ scroll ออกจาก viewport ถูก discard

#### PPR + Prefetching

- Static shell ถูก prefetch → stream ทันที
- Dynamic content stream เมื่อ ready
- `revalidateTag`/`revalidatePath` refresh prefetches อัตโนมัติ

## Troubleshooting

### Side-effects ถูก trigger ตอน prefetch

```tsx
// ❌ Bad — trackPageView รันตอน prefetch
export default function Layout({ children }: { children: React.ReactNode }) {
  trackPageView() // Runs during prefetch!
  return <div>{children}</div>
}
```

```tsx
// ✅ Good — ย้ายไป useEffect (รันเฉพาะตอน user visit)
'use client'

import { useEffect } from 'react'
import { trackPageView } from '@/lib/analytics'

export function AnalyticsTracker() {
  useEffect(() => {
    trackPageView()
  }, [])
  return null
}
```

```tsx
// Layout ใช้ AnalyticsTracker
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <AnalyticsTracker />
      {children}
    </div>
  )
}
```

### Too many prefetches (large lists)

```tsx
// ❌ Problem: 1000 links ใน viewport → 1000 prefetches
{posts.map((post) => (
  <Link href={`/blog/${post.id}`}>{post.title}</Link>
))}
```

```tsx
// ✅ Solution 1: Disable prefetch
{posts.map((post) => (
  <Link prefetch={false} href={`/blog/${post.id}`}>{post.title}</Link>
))}

// ✅ Solution 2: Hover-triggered (better UX)
{posts.map((post) => (
  <HoverPrefetchLink href={`/blog/${post.id}`}>{post.title}</HoverPrefetchLink>
))}
```

## Quick Reference

| Pattern | When to Use | Code |
|---------|-------------|------|
| Automatic | Default (most links) | `<Link href="...">` |
| Manual | Outside viewport, custom triggers | `router.prefetch(href)` |
| Hover-triggered | Large lists, balance perf/resources | `prefetch={active ? null : false}` |
| Disabled | Footer, rarely clicked links | `prefetch={false}` |
| With invalidation | Long-lived pages, stale data | `router.prefetch(href, { onInvalidate })` |

| `prefetch` prop | Behavior |
|----------------|----------|
| `undefined` (default) | Prefetch เมื่อเข้า viewport |
| `null` | Default static prefetching |
| `false` | ไม่ prefetch เลย |
| `true` | Prefetch full route (static + dynamic) |

## สรุป

1. **Default:** `<Link>` prefetch อัตโนมัติเมื่อเข้า viewport
2. **Static pages:** prefetch ทั้ง route, cache 5 min
3. **Dynamic pages:** prefetch เฉพาะ loading boundary
4. **Hover-triggered:** ประหยัด resources สำหรับ large lists
5. **`prefetch={false}`:** ปิดสำหรับ links ที่ไม่ค่อยใช้
6. **Side-effects:** ย้ายไป `useEffect` (ไม่ใช่ render time)
7. **Scheduler:** prioritize viewport → hover → newer links
