---
name: Next.js Migrating to Cache Components
description: Expert guidance on migrating from route segment configs to Cache Components — replacing dynamic, revalidate, fetchCache with "use cache" and cacheLife.
---

# Next.js Migrating to Cache Components

Expert guidance on migrating from route segment configs to Cache Components — replacing dynamic, revalidate, fetchCache with "use cache" and cacheLife.

@doc-version: 16.2.6

## Core Concepts

เมื่อเปิด `cacheComponents: true` — route segment configs (`dynamic`, `revalidate`, `fetchCache`) ถูกแทนที่ด้วย `"use cache"` + `cacheLife`

## Migration Guide

### 1. `dynamic = "force-dynamic"` → ลบออก

Pages เป็น dynamic by default แล้ว — ไม่ต้องระบุ:

```tsx
// ❌ Before
export const dynamic = 'force-dynamic'

export default function Page() {
  return <div>...</div>
}
```

```tsx
// ✅ After — แค่ลบออก
export default function Page() {
  return <div>...</div>
}
```

### 2. `dynamic = "force-static"` → `"use cache"` + `cacheLife('max')`

```tsx
// ❌ Before
export const dynamic = 'force-static'

export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

```tsx
// ✅ After
import { cacheLife } from 'next/cache'

export default async function Page() {
  'use cache'
  cacheLife('max')

  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

**ถ้ามี runtime APIs (cookies, headers):**
- ลบ runtime data access ออก (เพราะ force-static ไม่ควรมี)
- หรือหุ้มด้วย `<Suspense>`

### 3. `revalidate = N` → `"use cache"` + `cacheLife()`

```tsx
// ❌ Before
export const revalidate = 3600 // 1 hour

export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

```tsx
// ✅ After
import { cacheLife } from 'next/cache'

export default async function Page() {
  'use cache'
  cacheLife('hours')

  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

#### Mapping revalidate values to cacheLife profiles

| Before (`revalidate`) | After (`cacheLife`) |
|----------------------|---------------------|
| `1` | `cacheLife('seconds')` |
| `60` | `cacheLife('minutes')` |
| `3600` | `cacheLife('hours')` |
| `86400` | `cacheLife('days')` |
| `604800` | `cacheLife('weeks')` |
| `false` / very long | `cacheLife('max')` |
| Custom value | `cacheLife({ stale: N, revalidate: M, expire: X })` |

### 4. `fetchCache` → ลบออก

ไม่จำเป็นแล้ว — `"use cache"` cache ทุก data fetching ใน scope อัตโนมัติ:

```tsx
// ❌ Before
export const fetchCache = 'force-cache'

export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

```tsx
// ✅ After
export default async function Page() {
  'use cache'
  // ทุก fetches ใน scope นี้ถูก cache อัตโนมัติ
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

### 5. `runtime = 'edge'` → ลบออก

Cache Components ต้องการ Node.js runtime — ลบ `runtime = 'edge'`:

```tsx
// ❌ Before
export const runtime = 'edge'
```

```tsx
// ✅ After — ลบออก (ใช้ Node.js default)
// ถ้าต้องการ edge behavior → ใช้ Proxy แทน
```

### 6. `fetch` options → `"use cache"`

```tsx
// ❌ Before
const data = await fetch('https://api.example.com/data', {
  cache: 'force-cache',
  next: { revalidate: 3600, tags: ['posts'] },
})
```

```tsx
// ✅ After
import { cacheLife, cacheTag } from 'next/cache'

async function getData() {
  'use cache'
  cacheLife('hours')
  cacheTag('posts')
  const res = await fetch('https://api.example.com/data')
  return res.json()
}
```

### 7. UI State Preservation (Behavior Change)

เมื่อเปิด Cache Components — Next.js ใช้ React `<Activity>` component:
- **Component state persists** ข้าม navigations (ไม่ unmount)
- `useState`, form inputs, scroll position ไม่ถูก reset

#### ต้องแก้ไขถ้า code rely on unmounting:

**Dropdowns/Popovers — ยังเปิดอยู่เมื่อ navigate กลับ:**

```tsx
'use client'

import { useLayoutEffect } from 'react'

function Dropdown({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  // Close เมื่อ component ถูก "hide" (Activity hidden)
  useLayoutEffect(() => {
    return () => onClose() // Cleanup closes dropdown
  }, [onClose])

  // ...
}
```

**Forms after submission — input values persist:**

```tsx
'use client'

function ContactForm() {
  const [state, action] = useActionState(submitForm, null)

  // Reset form หลัง submit สำเร็จ
  useEffect(() => {
    if (state?.success) {
      formRef.current?.reset()
    }
  }, [state])

  // ...
}
```

**Dialogs — initialization logic ไม่ re-fire:**

```tsx
// Derive dialog state from URL แทน useState
import { useSearchParams } from 'next/navigation'

function Dialog() {
  const searchParams = useSearchParams()
  const isOpen = searchParams.get('dialog') === 'true'
  // ...
}
```

## Complete Migration Example

### Before (Route Segment Configs)

```tsx
// app/blog/page.tsx
export const dynamic = 'force-static'
export const revalidate = 3600

export default async function BlogPage() {
  const posts = await fetch('https://api.example.com/posts', {
    next: { tags: ['posts'] },
  }).then((r) => r.json())

  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

### After (Cache Components)

```tsx
// app/blog/page.tsx
import { cacheLife, cacheTag } from 'next/cache'

export default async function BlogPage() {
  'use cache'
  cacheLife('hours')
  cacheTag('posts')

  const posts = await fetch('https://api.example.com/posts').then((r) => r.json())

  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

## Quick Reference

| Before (Route Segment Config) | After (Cache Components) |
|-------------------------------|--------------------------|
| `dynamic = 'force-dynamic'` | ลบออก (default) |
| `dynamic = 'force-static'` | `'use cache'` + `cacheLife('max')` |
| `revalidate = N` | `'use cache'` + `cacheLife(profile)` |
| `fetchCache = 'force-cache'` | `'use cache'` (auto) |
| `runtime = 'edge'` | ลบออก (ใช้ Proxy แทน) |
| `fetch({ cache: 'force-cache' })` | `'use cache'` ใน function |
| `fetch({ next: { tags } })` | `cacheTag()` |
| `fetch({ next: { revalidate } })` | `cacheLife()` |

## สรุป

1. **`dynamic = 'force-dynamic'`** → ลบออก (default แล้ว)
2. **`dynamic = 'force-static'`** → `"use cache"` + `cacheLife('max')`
3. **`revalidate = N`** → `"use cache"` + `cacheLife(profile)`
4. **`fetchCache`** → ลบออก (auto ใน `"use cache"` scope)
5. **`runtime = 'edge'`** → ลบออก (ใช้ Node.js + Proxy)
6. **UI state persists** — เพิ่ม cleanup logic ถ้า rely on unmounting
7. **ใส่ `"use cache"` ใกล้ data access ที่สุด** — granular caching
