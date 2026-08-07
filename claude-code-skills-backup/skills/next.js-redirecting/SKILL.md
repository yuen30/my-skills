---
name: Next.js Redirecting
description: Expert guidance on handling redirects in Next.js — redirect, permanentRedirect, useRouter, next.config.js redirects, Proxy, and managing redirects at scale.
---

# Next.js Redirecting

Expert guidance on handling redirects in Next.js — redirect, permanentRedirect, useRouter, next.config.js redirects, Proxy, and managing redirects at scale.

@doc-version: 16.2.6

## Core Concepts

| API | Purpose | Where | Status Code |
|-----|---------|-------|:-:|
| `redirect` | After mutation/event | Server Components, Server Actions, Route Handlers | 307 / 303 |
| `permanentRedirect` | After mutation (permanent) | Server Components, Server Actions, Route Handlers | 308 |
| `useRouter` | Client-side navigation | Event Handlers in Client Components | N/A |
| `redirects` in next.config | Path-based redirects | Config file | 307 / 308 |
| `NextResponse.redirect` | Conditional redirects | Proxy | Any |

**Execution order:** `next.config.js` redirects → Proxy → rendering

## Guidelines

### 1. `redirect` — After Mutations

```ts
// app/actions.ts
'use server'

import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function createPost(id: string) {
  try {
    await db.post.create({ ... })
  } catch (error) {
    // Handle errors
  }

  revalidatePath('/posts')
  redirect(`/post/${id}`) // ← ต้องอยู่นอก try/catch
}
```

**สำคัญ:**
- `redirect` throws error internally → ต้องเรียก **นอก** `try/catch`
- Server Action → returns 303 (See Other)
- อื่นๆ → returns 307 (Temporary Redirect)
- รองรับ absolute URLs (external links)

### 2. `permanentRedirect` — Permanent URL Change

```ts
// app/actions.ts
'use server'

import { permanentRedirect } from 'next/navigation'
import { revalidateTag } from 'next/cache'

export async function updateUsername(username: string, formData: FormData) {
  try {
    await db.user.update({ ... })
  } catch (error) {
    // Handle errors
  }

  revalidateTag('username')
  permanentRedirect(`/profile/${username}`) // 308 Permanent
}
```

**ใช้เมื่อ:** Entity's canonical URL เปลี่ยน (username, slug)

### 3. `useRouter` — Client-side Navigation

```tsx
'use client'

import { useRouter } from 'next/navigation'

export default function Page() {
  const router = useRouter()

  return (
    <button onClick={() => router.push('/dashboard')}>
      Dashboard
    </button>
  )
}
```

> ถ้าไม่ต้อง programmatic → ใช้ `<Link>` แทน

### 4. `redirects` in `next.config.js` — Path-based

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async redirects() {
    return [
      // Basic redirect
      {
        source: '/about',
        destination: '/',
        permanent: true, // 308
      },
      // Wildcard path matching
      {
        source: '/blog/:slug',
        destination: '/news/:slug',
        permanent: true,
      },
      // Regex matching
      {
        source: '/old-blog/:slug(\\d{1,})',
        destination: '/news/:slug',
        permanent: false, // 307
      },
    ]
  },
}

export default nextConfig
```

**ข้อจำกัด:**
- Platform limits (Vercel: 1,024 redirects)
- รันก่อน Proxy
- ใช้สำหรับ redirects ที่รู้ล่วงหน้า

### 5. `NextResponse.redirect` in Proxy — Conditional

```ts
// proxy.ts
import { NextResponse, NextRequest } from 'next/server'
import { authenticate } from 'auth-provider'

export function proxy(request: NextRequest) {
  const isAuthenticated = authenticate(request)

  if (isAuthenticated) {
    return NextResponse.next()
  }

  // Redirect to login if not authenticated
  return NextResponse.redirect(new URL('/login', request.url))
}

export const config = {
  matcher: '/dashboard/:path*',
}
```

**ใช้เมื่อ:**
- Conditional redirects (auth, A/B test, geo)
- Large number of redirects (1000+)
- Dynamic logic ที่ config ทำไม่ได้

### 6. Managing Redirects at Scale (1000+)

#### Bloom Filter + Route Handler

```ts
// proxy.ts
import { NextResponse, NextRequest } from 'next/server'
import { ScalableBloomFilter } from 'bloom-filters'
import GeneratedBloomFilter from './redirects/bloom-filter.json'

const bloomFilter = ScalableBloomFilter.fromJSON(GeneratedBloomFilter as any)

export async function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Quick check: is this path possibly in our redirect list?
  if (bloomFilter.has(pathname)) {
    // Verify with actual data (handles false positives)
    const api = new URL(
      `/api/redirects?pathname=${encodeURIComponent(pathname)}`,
      request.nextUrl.origin
    )

    try {
      const res = await fetch(api)
      if (res.ok) {
        const entry = await res.json()
        if (entry) {
          return NextResponse.redirect(
            entry.destination,
            entry.permanent ? 308 : 307
          )
        }
      }
    } catch (error) {
      console.error(error)
    }
  }

  return NextResponse.next()
}
```

```ts
// app/api/redirects/route.ts
import { NextRequest, NextResponse } from 'next/server'
import redirects from '@/app/redirects/redirects.json'

type RedirectEntry = { destination: string; permanent: boolean }

export function GET(request: NextRequest) {
  const pathname = request.nextUrl.searchParams.get('pathname')
  if (!pathname) return new Response('Bad Request', { status: 400 })

  const redirect = (redirects as Record<string, RedirectEntry>)[pathname]
  if (!redirect) return new Response('No redirect', { status: 400 })

  return NextResponse.json(redirect)
}
```

**ข้อดี:**
- Bloom filter = O(1) lookup (fast, memory-efficient)
- ไม่ต้อง import large file ใน Proxy
- Handle false positives ด้วย Route Handler verification
- ไม่ต้อง redeploy เมื่อเพิ่ม redirects (update JSON/DB)

## Decision Guide

```
Redirect needed:
├── Known at build time? (URL structure change)
│   └── next.config.js redirects
│
├── After mutation? (create post, update username)
│   ├── Temporary → redirect()
│   └── Permanent → permanentRedirect()
│
├── Conditional? (auth, geo, A/B)
│   └── Proxy (NextResponse.redirect)
│
├── Client-side event? (button click)
│   └── useRouter().push()
│
└── Large scale? (1000+ redirects)
    └── Proxy + Bloom filter + DB/JSON
```

## Quick Reference

| Method | Status | Use Case |
|--------|:---:|---|
| `redirect(url)` | 307/303 | After Server Action/mutation |
| `permanentRedirect(url)` | 308 | Canonical URL changed permanently |
| `router.push(url)` | — | Client-side event handler |
| `next.config.js` redirects | 307/308 | Known path changes |
| `NextResponse.redirect(url)` | Any | Conditional (auth, geo) |
| `NextResponse.redirect(url, 308)` | 308 | Permanent in Proxy |

## สรุป

1. **`redirect()`** — หลัง mutation, ต้องอยู่นอก try/catch
2. **`permanentRedirect()`** — URL เปลี่ยนถาวร (308)
3. **`useRouter().push()`** — client-side event handlers
4. **`next.config.js`** — path-based, รู้ล่วงหน้า, รันก่อน Proxy
5. **Proxy** — conditional, dynamic logic, large scale
6. **Scale (1000+)** — Bloom filter + Route Handler + DB/JSON
7. **`redirect` throws** — เรียกนอก try/catch เสมอ
