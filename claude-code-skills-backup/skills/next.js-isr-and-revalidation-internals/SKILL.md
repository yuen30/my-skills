---
name: Next.js ISR and Revalidation Internals
description: Expert guidance on ISR in Next.js — time-based revalidation, on-demand revalidation, generateStaticParams, tag system architecture, multi-instance coordination, cache handlers, and graceful degradation.
---

# Next.js ISR and Revalidation Internals

Expert guidance on ISR in Next.js — time-based revalidation, on-demand revalidation, generateStaticParams, caching, and multi-instance considerations.

@doc-version: 16.2.6

## Core Concepts

ISR ให้คุณ:
- อัปเดต static content โดยไม่ rebuild ทั้ง site
- ลด server load ด้วย prerendered static pages
- จัดการ content จำนวนมากโดยไม่ต้อง build นาน
- `cache-control` headers ถูกเพิ่มอัตโนมัติ

## Guidelines

### 1. Basic ISR Example

```tsx
// app/blog/[id]/page.tsx
interface Post {
  id: string
  title: string
  content: string
}

// Invalidate cache ทุก 60 วินาที
export const revalidate = 60

export async function generateStaticParams() {
  const posts: Post[] = await fetch('https://api.vercel.app/blog').then((res) =>
    res.json()
  )
  return posts.map((post) => ({ id: String(post.id) }))
}

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post: Post = await fetch(`https://api.vercel.app/blog/${id}`).then(
    (res) => res.json()
  )

  return (
    <main>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </main>
  )
}
```

**Flow:**
1. `next build` → generate ทุก blog posts ที่รู้
2. Requests → served จาก cache ทันที
3. หลัง 60 วินาที → request ถัดไปยังได้ stale page
4. Background: regenerate fresh version
5. เสร็จแล้ว → request ถัดไปได้ fresh page
6. Path ใหม่ (เช่น `/blog/26`) → generate on-demand

### 2. Time-based Revalidation

```tsx
// app/blog/page.tsx
export const revalidate = 3600 // Invalidate ทุก 1 ชั่วโมง

export default async function Page() {
  const data = await fetch('https://api.vercel.app/blog')
  const posts = await data.json()

  return (
    <main>
      <h1>Blog Posts</h1>
      <ul>
        {posts.map((post: any) => (
          <li key={post.id}>{post.title}</li>
        ))}
      </ul>
    </main>
  )
}
```

**Stale-while-revalidate pattern:**
1. Request มาหลัง revalidate time → serve stale ทันที (เร็ว)
2. Background: regenerate fresh version
3. Request ถัดไป → ได้ fresh version

> **แนะนำ:** ตั้ง revalidate สูง (เช่น 1 ชั่วโมง) — ถ้าต้องการ precision ใช้ on-demand แทน

### 3. On-demand Revalidation with `revalidatePath`

```ts
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createPost() {
  // ... create post in database

  // Invalidate cache สำหรับ /posts route
  revalidatePath('/posts')
}
```

- Invalidate ทั้ง route
- Regeneration เกิดตอน request ถัดไป (ไม่ใช่ทันที)
- ไม่ต้องรู้ว่ามี tags อะไร

### 4. On-demand Revalidation with `revalidateTag`

#### Tag fetch requests

```tsx
// app/blog/page.tsx
export default async function Page() {
  const data = await fetch('https://api.vercel.app/blog', {
    next: { tags: ['posts'] },
  })
  const posts = await data.json()
  // ...
}
```

#### Tag non-fetch (ORM/DB)

```tsx
// app/blog/page.tsx
import { unstable_cache } from 'next/cache'
import { db, posts } from '@/lib/db'

const getCachedPosts = unstable_cache(
  async () => {
    return await db.select().from(posts)
  },
  ['posts'],
  { revalidate: 3600, tags: ['posts'] }
)

export default async function Page() {
  const posts = await getCachedPosts()
  // ...
}
```

#### Invalidate by tag

```ts
// app/actions.ts
'use server'

import { revalidateTag } from 'next/cache'

export async function createPost() {
  // ... create post

  // Invalidate ทุก data ที่ tag 'posts'
  revalidateTag('posts')
}
```

### 5. `generateStaticParams` — Pre-render at Build Time

```tsx
// app/blog/[id]/page.tsx
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then((r) => r.json())

  return posts.map((post: any) => ({
    id: String(post.id),
  }))
}
```

**`dynamicParams` behavior:**

| Value | Behavior สำหรับ paths ที่ไม่ได้ pre-render |
|-------|------------------------------------------|
| `true` (default) | Generate on-demand + cache |
| `false` | Return 404 |

```tsx
// ถ้าต้องการ 404 สำหรับ paths ที่ไม่รู้จัก
export const dynamicParams = false
```

### 6. Error Handling

ถ้า error เกิดระหว่าง revalidation:
- Last successfully generated data ยังถูก serve จาก cache
- Request ถัดไป → Next.js retry revalidation
- ไม่มี downtime

### 7. Debugging ISR

#### Logging fetches

```js
// next.config.js
module.exports = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
}
```

#### Debug cache hits/misses

```env
# .env
NEXT_PRIVATE_DEBUG_CACHE=1
```

#### Response header

ดู `x-nextjs-cache` header:

| Value | Meaning |
|-------|---------|
| `HIT` | Served from cache |
| `STALE` | Served from cache, revalidating in background |
| `MISS` | Not in cache, rendered fresh |
| `REVALIDATED` | Regenerated via on-demand revalidation |

#### Test locally

```bash
next build
next start
# → ISR ทำงานเหมือน production
```

### 8. Caveats

| Issue | Detail |
|-------|--------|
| Node.js runtime only | ไม่รองรับ Edge Runtime |
| ไม่รองรับ Static Export | `output: 'export'` ไม่มี server |
| Multiple fetch revalidate times | ใช้ค่าต่ำสุดสำหรับ route |
| `revalidate: 0` หรือ `no-store` | Route กลายเป็น dynamic |
| Proxy ไม่ทำงานกับ on-demand ISR | Revalidate exact path (ไม่ใช่ rewritten path) |
| Multi-instance | Default cache เป็น per-instance |
| Background regeneration | นับเป็น compute เพิ่มบน per-request billing platforms |

### 9. Multi-Instance

Default file-system cache เป็น per-instance:
- On-demand revalidation invalidate เฉพาะ instance ที่รับ call
- ใช้ shared cache handler สำหรับ coordination

```ts
// next.config.ts
const nextConfig = {
  cacheHandler: require.resolve('./cache-handler.mjs'),
}
```

ดู [How Revalidation Works](/docs/app/guides/how-revalidation-works) สำหรับ architecture

### 10. Customizing Cache Location

```ts
// next.config.ts
const nextConfig = {
  cacheHandler: require.resolve('./cache-handler.mjs'),
  cacheMaxMemorySize: 0, // Disable in-memory caching
}
```

ใช้สำหรับ:
- Persist cache ไป durable storage
- Share cache ข้าม containers/instances
- ดู [Self-Hosting guide](/docs/app/guides/self-hosting#caching-and-isr)

## Platform Support

| Deployment | ISR Support |
|-----------|:-:|
| Node.js server | ✅ |
| Docker container | ✅ |
| Static export | ❌ |
| Adapters | Platform-specific |

## Quick Reference

| Config/API | Purpose |
|-----------|---------|
| `export const revalidate = 60` | Time-based revalidation (seconds) |
| `export const dynamicParams = true` | Allow on-demand generation for unknown paths |
| `generateStaticParams()` | Pre-render paths at build time |
| `revalidatePath('/path')` | On-demand invalidation by path |
| `revalidateTag('tag')` | On-demand invalidation by tag |
| `unstable_cache(fn, keys, opts)` | Cache non-fetch with tags + revalidate |
| `next: { tags: ['x'] }` | Tag fetch requests |

## สรุป

1. **`export const revalidate = N`** — time-based ISR (stale-while-revalidate)
2. **`generateStaticParams`** — pre-render known paths at build time
3. **On-demand:** `revalidatePath` (ทั้ง route) หรือ `revalidateTag` (granular)
4. **Error resilient** — serve last good version ถ้า revalidation fail
5. **Node.js runtime only** — ไม่รองรับ Edge หรือ Static Export
6. **Multi-instance** — ต้อง shared cache handler
7. **Debug:** `NEXT_PRIVATE_DEBUG_CACHE=1` + `x-nextjs-cache` header
8. **ตั้ง revalidate สูง** (ชั่วโมง) — ใช้ on-demand สำหรับ precision
