---
name: Next.js Caching Previous Model
description: Expert guidance on caching and revalidating data without Cache Components — fetch options, unstable_cache, route segment configs, and on-demand revalidation.
---

# Next.js Caching (Previous Model)

Expert guidance on caching and revalidating data without Cache Components — fetch options, unstable_cache, route segment configs, and on-demand revalidation.

@doc-version: 16.2.6

## Core Concepts

สำหรับโปรเจกต์ที่ **ไม่ได้เปิด** `cacheComponents: true` — ใช้โมเดลเดิม:
- `fetch` + `cache` option
- `unstable_cache` สำหรับ non-fetch functions
- Route segment configs (`dynamic`, `revalidate`, `fetchCache`)
- On-demand revalidation (`revalidateTag`, `revalidatePath`)

## Guidelines

### 1. Caching `fetch` Requests

โดย default `fetch` **ไม่ถูก cache** — ต้อง opt-in:

```tsx
// Cached — ใช้ force-cache
export default async function Page() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'force-cache',
  })
  return <div>{data}</div>
}
```

```tsx
// Not cached (default)
export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

```tsx
// Explicitly not cached
export default async function Page() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'no-store',
  })
  return <div>{data}</div>
}
```

### 2. `unstable_cache` — Non-fetch Functions

สำหรับ database queries และ async functions ที่ไม่ใช่ `fetch`:

```ts
// app/lib/data.ts
import { unstable_cache } from 'next/cache'
import { db } from '@/lib/db'

export const getCachedUser = unstable_cache(
  async (id: string) => {
    return db.select().from(users).where(eq(users.id, id)).then((res) => res[0])
  },
  ['user'],  // cache key prefix
  {
    tags: ['user'],       // สำหรับ on-demand revalidation
    revalidate: 3600,     // revalidate ทุก 1 ชั่วโมง
  }
)
```

**Parameters:**
1. Function — async function ที่ต้องการ cache
2. Key prefix — array of strings สำหรับ cache key
3. Options:
   - `tags` — array of tags สำหรับ `revalidateTag`
   - `revalidate` — seconds ก่อน revalidate

### 3. Time-based Revalidation

#### fetch + `next.revalidate`

```tsx
export default async function Page() {
  // Revalidate ทุก 1 ชั่วโมง
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 },
  })
  return <div>{data}</div>
}
```

#### Route Segment Config `revalidate`

ตั้ง default revalidation time สำหรับทั้ง route:

```tsx
// app/blog/page.tsx
export const revalidate = 3600 // revalidate ทุก 1 ชั่วโมง

export default async function Page() {
  const data = await fetch('https://api.example.com/posts', {
    cache: 'force-cache',
  })
  return <div>{data}</div>
}
```

| Value | Behavior |
|-------|----------|
| `false` (default) | Cache indefinitely (เหมือน `Infinity`) |
| `0` | Always dynamic (ไม่ cache) |
| `number` | Revalidate ทุก n seconds |

**กฎ:** ค่า `revalidate` ที่ต่ำที่สุดในทุก layout/page ของ route จะเป็นค่าที่ใช้ทั้ง route

### 4. Route Segment Config `dynamic`

ควบคุม rendering behavior ทั้ง route:

```tsx
// app/page.tsx
export const dynamic = 'auto'
// 'auto' | 'force-dynamic' | 'error' | 'force-static'
```

| Value | Behavior |
|-------|----------|
| `'auto'` (default) | Cache ได้มากที่สุดโดยไม่บังคับ |
| `'force-dynamic'` | Dynamic rendering ทุก request (เหมือน `no-store`) |
| `'error'` | Force prerender — error ถ้ามี dynamic APIs |
| `'force-static'` | Force prerender — cookies/headers return empty |

### 5. On-demand Revalidation

#### Tag fetch requests

```ts
// app/lib/data.ts
export async function getUserById(id: string) {
  const data = await fetch(`https://api.example.com/users/${id}`, {
    next: { tags: ['user'] },
  })
  return data.json()
}
```

#### `revalidateTag`

```ts
// app/actions.ts
'use server'

import { revalidateTag } from 'next/cache'

export async function updateUser(id: string) {
  await db.user.update({ where: { id }, data: { ... } })
  revalidateTag('user')
}
```

#### `revalidatePath`

```ts
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function updateProfile() {
  await db.user.update({ ... })
  revalidatePath('/profile')
}
```

### 6. Deduplicating Requests (`React.cache`)

สำหรับ ORM/database ที่ไม่ใช่ `fetch` (fetch ถูก memoize อัตโนมัติ):

```ts
// app/lib/data.ts
import { cache } from 'react'
import { db, posts, eq } from '@/lib/db'

export const getPost = cache(async (id: string) => {
  const post = await db.query.posts.findFirst({
    where: eq(posts.id, parseInt(id)),
  })
  return post
})
```

- เรียกหลายครั้งใน render pass เดียวกัน → query แค่ครั้งเดียว
- ใช้ได้ทั้งใน `generateMetadata` และ page component

### 7. Preloading Data

เริ่ม fetch ก่อน blocking work:

```ts
// lib/data.ts
import { cache } from 'react'
import 'server-only'

export const getItem = cache(async (id: string) => {
  const res = await fetch(`https://api.example.com/items/${id}`)
  return res.json()
})

export const preload = (id: string) => {
  void getItem(id) // เริ่ม fetch ทันที ไม่ await
}
```

```tsx
// app/item/[id]/page.tsx
import { getItem, preload, checkIsAvailable } from '@/lib/data'

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  // เริ่ม fetch ทันที
  preload(id)

  // ทำงานอื่นระหว่างรอ
  const isAvailable = await checkIsAvailable()

  return isAvailable ? <Item id={id} /> : null
}

async function Item({ id }: { id: string }) {
  const result = await getItem(id) // ใช้ cached result
  return <div>{result.name}</div>
}
```

### 8. `fetchCache` (Advanced)

ควบคุม default cache behavior ของทุก `fetch` ใน route:

```tsx
export const fetchCache = 'auto'
// 'auto' | 'default-cache' | 'only-cache' | 'force-cache'
// | 'default-no-store' | 'only-no-store' | 'force-no-store'
```

| Value | Default cache option |
|-------|---------------------|
| `'auto'` (default) | Cache before dynamic APIs, no-cache after |
| `'default-cache'` | `force-cache` ถ้าไม่ระบุ |
| `'only-cache'` | ทุก fetch ต้อง cache — error ถ้า `no-store` |
| `'force-cache'` | ทุก fetch เป็น `force-cache` |
| `'default-no-store'` | `no-store` ถ้าไม่ระบุ |
| `'only-no-store'` | ทุก fetch ต้อง no-store — error ถ้า `force-cache` |
| `'force-no-store'` | ทุก fetch เป็น `no-store` |

## Comparison: Previous Model vs Cache Components

| Feature | Previous Model | Cache Components |
|---------|---------------|-----------------|
| Cache fetch | `cache: 'force-cache'` | `"use cache"` directive |
| Cache non-fetch | `unstable_cache()` | `"use cache"` in function |
| Time-based | `next: { revalidate: n }` | `cacheLife('hours')` |
| Tag | `next: { tags: ['x'] }` | `cacheTag('x')` |
| Invalidate | `revalidateTag('x')` | `revalidateTag('x')` / `updateTag('x')` |
| Route config | `export const dynamic = ...` | ไม่จำเป็น (PPR อัตโนมัติ) |

## Quick Reference

| สถานการณ์ | วิธี |
|-----------|------|
| Cache fetch request | `fetch(url, { cache: 'force-cache' })` |
| Cache with revalidation | `fetch(url, { next: { revalidate: 3600 } })` |
| Cache non-fetch | `unstable_cache(fn, keys, { tags, revalidate })` |
| Force dynamic | `export const dynamic = 'force-dynamic'` |
| Force static | `export const dynamic = 'force-static'` |
| Tag for invalidation | `fetch(url, { next: { tags: ['name'] } })` |
| Invalidate by tag | `revalidateTag('name')` |
| Invalidate by path | `revalidatePath('/path')` |
| Deduplicate | `React.cache(fn)` |
| Preload | `void cachedFn(id)` |

## สรุป

1. **`fetch` ไม่ cache โดย default** — ต้อง opt-in ด้วย `cache: 'force-cache'`
2. **`unstable_cache`** สำหรับ non-fetch (DB queries)
3. **`next: { revalidate: n }`** — time-based revalidation
4. **`next: { tags: [...] }`** — tag สำหรับ on-demand invalidation
5. **Route segment configs** — `dynamic`, `revalidate`, `fetchCache`
6. **`React.cache`** — deduplicate ใน render pass เดียวกัน
7. **Preload pattern** — เริ่ม fetch ก่อน blocking work
8. **พิจารณา migrate ไป Cache Components** (`cacheComponents: true`) สำหรับ DX ที่ดีกว่า
