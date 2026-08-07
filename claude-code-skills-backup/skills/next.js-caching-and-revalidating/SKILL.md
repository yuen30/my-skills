---
name: Next.js Caching and Revalidating
description: Expert guidance on caching data and UI in Next.js App Router using Cache Components, "use cache" directive, cacheLife, cacheTag, revalidateTag, updateTag, revalidatePath, and Partial Prerendering.
---

# Next.js Caching and Revalidating

Expert guidance on caching data and UI in Next.js App Router using Cache Components, "use cache" directive, Streaming, Suspense, and Partial Prerendering (PPR).

@doc-version: 16.2.6

## Core Concepts

Caching ใน Next.js คือการเก็บผลลัพธ์ของ data fetching และ computation ไว้ เพื่อให้ request ถัดไปไม่ต้องทำงานซ้ำ ทำให้เว็บเร็วขึ้น

**Cache Components** คือโมเดลใหม่ที่ใช้ `"use cache"` directive ควบคุมการ cache ในระดับ function หรือ component

## Guidelines

### 1. เปิดใช้งาน Cache Components

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
}

export default nextConfig
```

> เมื่อเปิด Cache Components, GET Route Handlers จะใช้ prerendering model เดียวกับ pages

### 2. การใช้ `"use cache"` Directive

#### Data-level Caching — cache ฟังก์ชันดึงข้อมูล

```tsx
// app/lib/data.ts
import { cacheLife } from 'next/cache'

export async function getUsers() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM users')
}
```

**ใช้เมื่อ:** ข้อมูลเดียวกันถูกใช้ในหลาย components หรือต้องการ cache data แยกจาก UI

#### UI-level Caching — cache ทั้ง component/page/layout

```tsx
// app/page.tsx
import { cacheLife } from 'next/cache'

export default async function Page() {
  'use cache'
  cacheLife('hours')

  const users = await db.query('SELECT * FROM users')

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

> ถ้าใส่ `"use cache"` ที่หัวไฟล์ → ทุก exported functions ในไฟล์จะถูก cache

#### Cache Keys

Arguments และ closed-over values จาก parent scopes จะกลายเป็น **cache key** อัตโนมัติ — input ต่างกัน = cache entry แยกกัน

```tsx
async function CachedContent({ sessionId }: { sessionId: string }) {
  'use cache'
  // sessionId เป็นส่วนหนึ่งของ cache key
  const data = await fetchUserData(sessionId)
  return <div>{data}</div>
}
```

### 3. Streaming Uncached Data (ไม่ cache)

สำหรับข้อมูลที่ต้องการ fresh ทุก request — **อย่าใช้ `"use cache"`** แต่ใช้ `<Suspense>` แทน:

```tsx
import { Suspense } from 'react'

async function LatestPosts() {
  const data = await fetch('https://api.example.com/posts')
  const posts = await data.json()

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}

export default function Page() {
  return (
    <>
      <h1>My Blog</h1>
      <Suspense fallback={<p>Loading posts...</p>}>
        <LatestPosts />
      </Suspense>
    </>
  )
}
```

- Fallback ถูกรวมใน static shell
- Content จริง stream เข้ามาตอน request time

### 4. Working with Runtime APIs

Runtime APIs ต้องการข้อมูลจาก request (cookies, headers, searchParams, params) — ต้องหุ้มด้วย `<Suspense>`:

```tsx
import { cookies } from 'next/headers'
import { Suspense } from 'react'

async function UserGreeting() {
  const cookieStore = await cookies()
  const theme = cookieStore.get('theme')?.value || 'light'
  return <p>Your theme: {theme}</p>
}

export default function Page() {
  return (
    <>
      <h1>Dashboard</h1>
      <Suspense fallback={<p>Loading...</p>}>
        <UserGreeting />
      </Suspense>
    </>
  )
}
```

#### ส่ง Runtime Values เข้า Cached Functions

```tsx
import { cookies } from 'next/headers'
import { Suspense } from 'react'

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProfileContent />
    </Suspense>
  )
}

// Component (ไม่ cache) อ่าน runtime data
async function ProfileContent() {
  const session = (await cookies()).get('session')?.value
  return <CachedContent sessionId={session!} />
}

// Cached component รับค่าเป็น prop (กลายเป็น cache key)
async function CachedContent({ sessionId }: { sessionId: string }) {
  'use cache'
  const data = await fetchUserData(sessionId)
  return <div>{data}</div>
}
```

> **Serverless:** `use cache` เก็บ in-memory โดย default ซึ่งไม่ persist ข้าม requests ใน serverless ใช้ `'use cache: remote'` สำหรับ durable shared caching

### 5. Non-deterministic Operations

`Math.random()`, `Date.now()`, `crypto.randomUUID()` ให้ค่าต่างกันทุกครั้ง — ต้องจัดการชัดเจน:

#### ต้องการค่าใหม่ทุก request — ใช้ `connection()`

```tsx
import { connection } from 'next/server'
import { Suspense } from 'react'

async function UniqueContent() {
  await connection()
  const uuid = crypto.randomUUID()
  return <p>Request ID: {uuid}</p>
}

export default function Page() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <UniqueContent />
    </Suspense>
  )
}
```

#### ต้องการค่าเดียวกันจนกว่า revalidate — ใช้ `"use cache"`

```tsx
export default async function Page() {
  'use cache'
  const buildId = crypto.randomUUID()
  return <p>Build ID: {buildId}</p>
}
```

### 6. Deterministic Operations

Synchronous I/O, module imports, pure computations — ถูกรวมใน static shell อัตโนมัติ:

```tsx
import fs from 'node:fs'

export default async function Page() {
  const content = fs.readFileSync('./config.json', 'utf-8')
  const constants = await import('./constants.json')
  const processed = JSON.parse(content).items.map((item) => item.value * 2)

  return (
    <div>
      <h1>{constants.appName}</h1>
      <ul>
        {processed.map((value, i) => (
          <li key={i}>{value}</li>
        ))}
      </ul>
    </div>
  )
}
```

> ถ้าต้องการ per-request data จาก synchronous source ให้เรียก `connection()` ก่อน query

### 7. How Rendering Works — Partial Prerendering (PPR)

Next.js สร้าง **static shell** จาก:

| ประเภท | วิธีจัดการ | ผลลัพธ์ |
|--------|-----------|---------|
| `"use cache"` | Cache ผลลัพธ์ | รวมใน static shell |
| `<Suspense>` | Fallback UI | Fallback ใน shell, content stream ตอน request |
| Deterministic ops | Pure computation | รวมใน static shell อัตโนมัติ |

**PPR = Partial Prerendering** — default behavior เมื่อเปิด Cache Components:
- Static content + cached content → ส่งทันที
- Dynamic content → stream เข้ามาทีหลัง

```
Static Shell (ส่งทันที):
┌─────────────────────────────┐
│ Header (static)             │
│ Blog Posts (cached)         │
│ [Loading preferences...]    │ ← Suspense fallback
│ [Loading...]                │ ← Suspense fallback
└─────────────────────────────┘

หลัง Stream:
┌─────────────────────────────┐
│ Header (static)             │
│ Blog Posts (cached)         │
│ Your theme: dark            │ ← streamed in
│ Create Post form            │ ← streamed in
└─────────────────────────────┘
```

**Error handling:** ถ้า component ที่ไม่สามารถ prerender ได้ไม่ถูกหุ้มด้วย `<Suspense>` หรือ `"use cache"` → จะเห็น error: `Uncached data was accessed outside of <Suspense>`

### 8. Complete Example — ทุกอย่างรวมกัน

```tsx
// app/blog/page.tsx
import { Suspense } from 'react'
import { cookies } from 'next/headers'
import { cacheLife, cacheTag, updateTag } from 'next/cache'
import Link from 'next/link'

export default function BlogPage() {
  return (
    <>
      {/* Static content — prerendered อัตโนมัติ */}
      <header>
        <h1>Our Blog</h1>
        <nav>
          <Link href="/">Home</Link> | <Link href="/about">About</Link>
        </nav>
      </header>

      {/* Cached dynamic content — รวมใน static shell */}
      <BlogPosts />

      {/* Runtime dynamic content — stream ตอน request time */}
      <Suspense fallback={<p>Loading your preferences...</p>}>
        <UserPreferences />
      </Suspense>

      {/* Mutation — server action ที่ revalidate cache */}
      <Suspense fallback={<p>Loading...</p>}>
        <CreatePost />
      </Suspense>
    </>
  )
}

// ทุกคนเห็นเหมือนกัน (revalidate ทุกชั่วโมง)
async function BlogPosts() {
  'use cache'
  cacheLife('hours')
  cacheTag('posts')

  const res = await fetch('https://api.vercel.app/blog')
  const posts = await res.json()

  return (
    <section>
      <h2>Latest Posts</h2>
      <ul>
        {posts.slice(0, 5).map((post: any) => (
          <li key={post.id}>
            <h3>{post.title}</h3>
            <p>By {post.author} on {post.date}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}

// Personalized ตาม cookie ของ user
async function UserPreferences() {
  const theme = (await cookies()).get('theme')?.value || 'light'
  const favoriteCategory = (await cookies()).get('category')?.value

  return (
    <aside>
      <p>Your theme: {theme}</p>
      {favoriteCategory && <p>Favorite category: {favoriteCategory}</p>}
    </aside>
  )
}

// Admin-only form ที่ revalidate cache หลังสร้าง post
async function CreatePost() {
  const isAdmin = (await cookies()).get('role')?.value === 'admin'
  if (!isAdmin) return null

  async function createPost(formData: FormData) {
    'use server'
    await db.post.create({ data: { title: formData.get('title') } })
    updateTag('posts')
  }

  return (
    <form action={createPost}>
      <input name="title" placeholder="Post title" required />
      <button type="submit">Publish</button>
    </form>
  )
}
```

### 9. Opting Out of Static Shell

วาง `<Suspense fallback={null}>` ครอบ body ใน Root Layout → ทั้งแอปจะ defer ไป request time:

```tsx
// app/layout.tsx
import { Suspense } from 'react'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <Suspense fallback={null}>
        <body>{children}</body>
      </Suspense>
    </html>
  )
}
```

> ใช้เฉพาะเมื่อต้องการ — จะทำให้ไม่มี static shell ส่งทันที

## Quick Reference

| สถานการณ์ | วิธี | ผลลัพธ์ |
|-----------|------|---------|
| ข้อมูลเปลี่ยนไม่บ่อย | `"use cache"` + `cacheLife()` | Cache ตามเวลาที่กำหนด |
| ข้อมูลต้อง fresh ทุก request | `<Suspense>` (ไม่ใช้ cache) | Stream ตอน request time |
| Runtime APIs (cookies, headers) | `<Suspense>` หุ้ม component | Stream ตอน request time |
| ส่ง runtime value เข้า cache | แยก component → ส่งเป็น prop | Prop = cache key |
| Non-deterministic (random) | `connection()` + `<Suspense>` | ค่าใหม่ทุก request |
| Non-deterministic (cache ได้) | `"use cache"` | ค่าเดิมจนกว่า revalidate |
| Deterministic (pure) | ไม่ต้องทำอะไร | รวมใน static shell อัตโนมัติ |
| Revalidate cache | `updateTag()` / `revalidateTag()` | ล้าง cache ทันที |

## Cache Directives

| Directive | ใช้เมื่อ |
|-----------|---------|
| `'use cache'` | Cache ทั่วไป (in-memory) |
| `'use cache: private'` | Cache ที่เข้าถึง runtime request APIs |
| `'use cache: remote'` | Durable shared caching (serverless) |

## สรุป

1. เปิด `cacheComponents: true` ใน next.config.ts
2. ใช้ `"use cache"` + `cacheLife()` สำหรับข้อมูลที่ cache ได้
3. ใช้ `<Suspense>` สำหรับข้อมูลที่ต้อง fresh ทุก request
4. Runtime APIs (cookies, headers) ต้องอยู่ใน `<Suspense>`
5. PPR = static shell ส่งทันที + dynamic content stream ตามหลัง
6. ถ้าไม่หุ้ม `<Suspense>` หรือ `"use cache"` → จะเจอ error ตอน build
