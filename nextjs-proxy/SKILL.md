---
name: Next.js Proxy
description: Expert guidance on using Next.js Proxy (formerly Middleware) to run code before requests complete — redirects, rewrites, header modification, and route matching.
---

# Next.js Proxy

Expert guidance on using Next.js Proxy (formerly Middleware) to run code before requests complete — redirects, rewrites, header modification, and route matching.

@doc-version: 16.2.6

## Core Concepts

Proxy (เดิมคือ Middleware — เปลี่ยนชื่อตั้งแต่ Next.js 16) ให้คุณรัน code ก่อน request จะเสร็จสมบูรณ์ สามารถ:
- Redirect ไปหน้าอื่น
- Rewrite URL
- แก้ไข request/response headers
- ตอบกลับโดยตรง (ไม่ผ่าน route)

## Guidelines

### 1. Convention

สร้างไฟล์ `proxy.ts` ที่ project root (หรือใน `src/` ถ้าใช้):

```
project/
├── proxy.ts          # ← ที่นี่
├── app/
├── next.config.ts
└── package.json
```

หรือ:

```
project/
├── src/
│   ├── proxy.ts      # ← หรือที่นี่
│   └── app/
├── next.config.ts
└── package.json
```

> **มีได้แค่ 1 ไฟล์** ต่อ project — แยก logic เป็น modules แล้ว import เข้ามาได้

### 2. Basic Example

```tsx
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

// หรือใช้ default export:
// export default function proxy(request: NextRequest) { ... }

export const config = {
  matcher: '/about/:path*',
}
```

### 3. Use Cases

#### Redirect ตามเงื่อนไข

```tsx
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const token = request.cookies.get('session')?.value

  // ไม่มี session → redirect ไป login
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
}
```

#### Rewrite URL

```tsx
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // A/B test: 50% ของ users เห็นหน้าใหม่
  if (pathname === '/pricing') {
    const bucket = request.cookies.get('ab-bucket')?.value
    if (bucket === 'b') {
      return NextResponse.rewrite(new URL('/pricing-new', request.url))
    }
  }

  return NextResponse.next()
}
```

#### แก้ไข Headers

```tsx
export function proxy(request: NextRequest) {
  // เพิ่ม request header
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-request-id', crypto.randomUUID())

  // ส่งต่อ request พร้อม headers ใหม่
  const response = NextResponse.next({
    request: { headers: requestHeaders },
  })

  // เพิ่ม response header
  response.headers.set('x-response-time', Date.now().toString())

  return response
}
```

#### ตอบกลับโดยตรง

```tsx
export function proxy(request: NextRequest) {
  // Block specific paths
  if (request.nextUrl.pathname.startsWith('/api/internal')) {
    return NextResponse.json(
      { error: 'Forbidden' },
      { status: 403 }
    )
  }

  return NextResponse.next()
}
```

#### Internationalization (i18n)

```tsx
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // ตรวจสอบว่ามี locale ใน path หรือไม่
  const pathnameHasLocale = ['en', 'th', 'ja'].some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )

  if (pathnameHasLocale) return NextResponse.next()

  // Detect locale จาก Accept-Language header
  const locale = request.headers.get('accept-language')?.includes('th')
    ? 'th'
    : 'en'

  return NextResponse.redirect(new URL(`/${locale}${pathname}`, request.url))
}

export const config = {
  matcher: ['/((?!_next|api|favicon.ico).*)'],
}
```

#### Rate Limiting (Basic)

```tsx
const rateLimit = new Map<string, { count: number; timestamp: number }>()

export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api')) {
    const ip = request.headers.get('x-forwarded-for') ?? 'unknown'
    const now = Date.now()
    const windowMs = 60_000 // 1 minute
    const maxRequests = 100

    const record = rateLimit.get(ip)

    if (record && now - record.timestamp < windowMs) {
      if (record.count >= maxRequests) {
        return NextResponse.json(
          { error: 'Too many requests' },
          { status: 429 }
        )
      }
      record.count++
    } else {
      rateLimit.set(ip, { count: 1, timestamp: now })
    }
  }

  return NextResponse.next()
}
```

### 4. Matcher — กำหนด paths ที่ Proxy ทำงาน

```tsx
export const config = {
  matcher: '/about/:path*',
}
```

#### หลาย paths

```tsx
export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*', '/api/:path*'],
}
```

#### Regex pattern

```tsx
export const config = {
  matcher: [
    // Match ทุก path ยกเว้น static files และ images
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
```

#### ไม่ใช้ matcher (ทำงานทุก request)

ถ้าไม่ export `config` → Proxy จะทำงานทุก request (ไม่แนะนำ — ช้า)

### 5. Organizing Proxy Logic

แยก logic เป็น modules:

```tsx
// lib/proxy/auth.ts
import { NextRequest, NextResponse } from 'next/server'

export function authProxy(request: NextRequest) {
  const token = request.cookies.get('session')?.value
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return null // ไม่ต้องทำอะไร
}
```

```tsx
// lib/proxy/headers.ts
import { NextRequest, NextResponse } from 'next/server'

export function headersProxy(request: NextRequest) {
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-request-id', crypto.randomUUID())
  return requestHeaders
}
```

```tsx
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { authProxy } from './lib/proxy/auth'
import { headersProxy } from './lib/proxy/headers'

export function proxy(request: NextRequest) {
  // Auth check
  const authResponse = authProxy(request)
  if (authResponse) return authResponse

  // Add headers
  const requestHeaders = headersProxy(request)

  return NextResponse.next({
    request: { headers: requestHeaders },
  })
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

### 6. ข้อจำกัดและข้อควรระวัง

**ไม่ควรใช้ Proxy สำหรับ:**
- Slow data fetching (ทำให้ทุก request ช้า)
- Full session management / authorization (ใช้เป็น optimistic check เท่านั้น)
- Heavy computation

**ข้อจำกัด:**
- `fetch` ใน Proxy ไม่รองรับ `options.cache`, `options.next.revalidate`, `options.next.tags`
- มีได้แค่ 1 ไฟล์ `proxy.ts` ต่อ project
- ทำงานบน Edge Runtime (ไม่ใช่ Node.js full)

**สำหรับ simple redirects:** ใช้ `redirects` ใน `next.config.ts` แทน:

```ts
// next.config.ts
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/old-page',
        destination: '/new-page',
        permanent: true,
      },
    ]
  },
}
```

## Quick Reference

| Action | Method |
|--------|--------|
| Redirect | `NextResponse.redirect(new URL('/path', request.url))` |
| Rewrite | `NextResponse.rewrite(new URL('/path', request.url))` |
| Continue (pass through) | `NextResponse.next()` |
| Respond directly | `NextResponse.json({ ... }, { status: 403 })` |
| Add request header | `NextResponse.next({ request: { headers } })` |
| Add response header | `response.headers.set('key', 'value')` |
| Read cookie | `request.cookies.get('name')?.value` |
| Set cookie | `response.cookies.set('name', 'value', { httpOnly: true })` |
| Delete cookie | `response.cookies.delete('name')` |
| Read header | `request.headers.get('name')` |
| Get pathname | `request.nextUrl.pathname` |
| Get search params | `request.nextUrl.searchParams` |

### 7. Cookies API

```tsx
export function proxy(request: NextRequest) {
  // Read cookies
  const session = request.cookies.get('session')
  const allCookies = request.cookies.getAll()
  const hasSession = request.cookies.has('session')

  // Set cookies on response
  const response = NextResponse.next()
  response.cookies.set('theme', 'dark')
  response.cookies.set({
    name: 'session',
    value: 'abc123',
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
  })

  // Delete cookie
  response.cookies.delete('old-cookie')

  return response
}
```

### 8. CORS

```tsx
const allowedOrigins = ['https://acme.com', 'https://my-app.org']

export function proxy(request: NextRequest) {
  const origin = request.headers.get('origin') ?? ''
  const isAllowedOrigin = allowedOrigins.includes(origin)

  // Handle preflight
  if (request.method === 'OPTIONS') {
    return NextResponse.json({}, {
      headers: {
        ...(isAllowedOrigin && { 'Access-Control-Allow-Origin': origin }),
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    })
  }

  // Handle simple requests
  const response = NextResponse.next()
  if (isAllowedOrigin) {
    response.headers.set('Access-Control-Allow-Origin', origin)
  }
  return response
}

export const config = { matcher: '/api/:path*' }
```

### 9. Negative Matching (Exclude Paths)

```tsx
export const config = {
  matcher: [
    {
      source: '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
}
```

- `missing` — run only when headers/cookies are absent
- `has` — run only when headers/cookies are present

### 10. `waitUntil` (Background Work)

```tsx
import { NextResponse } from 'next/server'
import type { NextFetchEvent, NextRequest } from 'next/server'

export function proxy(req: NextRequest, event: NextFetchEvent) {
  // Background analytics — doesn't block response
  event.waitUntil(
    fetch('https://analytics.example.com', {
      method: 'POST',
      body: JSON.stringify({ pathname: req.nextUrl.pathname }),
    })
  )

  return NextResponse.next()
}
```

### 11. Unit Testing (Experimental)

```ts
import { unstable_doesProxyMatch } from 'next/experimental/testing/server'
import { isRewrite, getRewrittenUrl } from 'next/experimental/testing/server'

// Test matcher
expect(unstable_doesProxyMatch({
  config,
  nextConfig,
  url: '/test',
})).toEqual(false)

// Test proxy function
const request = new NextRequest('https://example.com/docs')
const response = await proxy(request)
expect(isRewrite(response)).toEqual(true)
expect(getRewrittenUrl(response)).toEqual('https://other.com/docs')
```

### 12. Migration from Middleware

```bash
# Automatic migration
npx @next/codemod@canary middleware-to-proxy .
```

Changes:
- `middleware.ts` → `proxy.ts`
- `export function middleware()` → `export function proxy()`
- Runtime: now defaults to Node.js (was Edge)

## Execution Order

```
1. headers (next.config.js)
2. redirects (next.config.js)
3. Proxy (rewrites, redirects, responses)
4. beforeFiles rewrites (next.config.js)
5. Filesystem routes (public/, _next/static/, pages/, app/)
6. afterFiles rewrites (next.config.js)
7. Dynamic Routes (/blog/[slug])
8. fallback rewrites (next.config.js)
```

> **Server Functions** ไม่ใช่ separate routes — handled as POST to the route ที่ใช้ Proxy matcher ที่ exclude path จะ skip Server Function calls ด้วย

## สรุป

1. **สร้าง `proxy.ts`** ที่ project root (1 ไฟล์เท่านั้น)
2. **Export `proxy` function** (named หรือ default)
3. **ใช้ `matcher`** กำหนด paths ที่ต้องการ
4. **ใช้สำหรับ:** redirects, rewrites, headers, auth checks, i18n, CORS
5. **อย่าใช้สำหรับ:** slow data fetching, heavy computation
6. **Simple redirects** → ใช้ `next.config.ts` redirects แทน
7. **Cookies:** `request.cookies.get()` / `response.cookies.set()`
8. **`waitUntil`** — background work ไม่ block response
9. **Migration:** `npx @next/codemod middleware-to-proxy .`
10. **Runtime:** Node.js by default (ตั้งแต่ v16)
