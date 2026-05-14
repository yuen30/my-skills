---
name: nextjs16-proxy
description: "Next.js 16 Proxy (อดีต Middleware) — ใช้ `proxy.ts` แทน `middleware.ts`, Default runtime เป็น Node.js, ไม่มี Edge Runtime แล้ว. ใช้เมื่อเขียนหรือแก้ไข Proxy Logic, auth guard, redirect, rewrite, locale detection."
---

# Next.js 16 Proxy (Middleware Replacement)

## Key Breaking Changes from Old Middleware

| Old (≤15) | New (16+) |
|---|---|
| `middleware.ts` | `proxy.ts` |
| export function name: `middleware` | export function name: `proxy` |
| Default runtime: **Edge** | Default runtime: **Node.js** |
| `export const config = { runtime: 'edge' }` | **Not supported** — throws error |
| `NextFetchEvent` 2nd param | Still available |
| Both `middleware.ts` and `proxy.ts` can coexist | **Error** if both exist |

## File Convention

Place `proxy.ts` at project root (same level as `app/` or `pages/`).

```ts
// proxy.ts — must export `proxy` function or default export
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/home', request.url))
}

export const config = {
  matcher: '/about/:path*',
}
```

If you customized `pageExtensions`, name it `proxy.page.ts` instead.

## TypeScript Type

Use `NextProxy` for automatic type inference of both `request` and `event`:

```ts
import type { NextProxy } from 'next/server'

export const proxy: NextProxy = (request, event) => {
  event.waitUntil(Promise.resolve())
  return Response.json({ pathname: request.nextUrl.pathname })
}
```

## Config (matcher)

Must be **static constants** (cannot use variables).

### Basic patterns

```ts
// Single path
export const config = { matcher: '/about' }

// Multiple paths
export const config = { matcher: ['/about/:path*', '/dashboard/:path*'] }

// Negative match (exclude)
export const config = {
  matcher: '/((?!api|_next/static|_next/image|favicon.ico|healthz).*)',
}
```

### Advanced matcher with `has` / `missing`

```ts
export const config = {
  matcher: [
    {
      source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
    {
      source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
      has: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
}
```

## Common Patterns

### 1. Auth guard + next-intl locale (our project's pattern)

```ts
// proxy.ts
import createMiddleware from 'next-intl/middleware'
import { NextRequest, NextResponse } from 'next/server'
import { getToken } from 'next-auth/jwt'

import { routing } from '@/i18n/routing'
import { getLocaleFromPathname, localizePath } from '@/lib/i18n-paths'
import { sanitizeCallbackUrl } from '@/lib/auth/redirect'

const PUBLIC_PATHS = new Set(['/login'])
const intlMiddleware = createMiddleware(routing)

function stripLocale(pathname: string): string {
  for (const locale of routing.locales) {
    const prefix = `/${locale}`
    if (pathname === prefix) return '/'
    if (pathname.startsWith(`${prefix}/`))
      return pathname.slice(prefix.length) || '/'
  }
  return pathname
}

export default async function proxy(request: NextRequest) {
  const { nextUrl } = request
  const pathWithoutLocale = stripLocale(nextUrl.pathname)
  const activeLocale =
    getLocaleFromPathname(nextUrl.pathname) ?? routing.defaultLocale
  const isPublicPath = PUBLIC_PATHS.has(pathWithoutLocale)
  const secret = process.env.AUTH_SECRET ?? process.env.NEXTAUTH_SECRET

  // next-auth cookie name depends on protocol
  const isSecure =
    nextUrl.protocol === 'https:' ||
    request.headers.get('x-forwarded-proto') === 'https'
  const cookieName = isSecure
    ? '__Secure-authjs.session-token'
    : 'authjs.session-token'

  const token = await getToken({ req: request, secret, cookieName }).catch(
    () => null,
  )
  const isSignedIn = Boolean(token)

  // Public path → redirect signed-in users, otherwise let intl handle
  if (isPublicPath) {
    if (isSignedIn) {
      const callbackUrl = sanitizeCallbackUrl(
        nextUrl.searchParams.get('callbackUrl'),
      )
      return NextResponse.redirect(
        new URL(localizePath(activeLocale, callbackUrl), nextUrl),
      )
    }
    return intlMiddleware(request)
  }

  // Protected → redirect to login
  if (!isSignedIn) {
    const loginUrl = new URL(`/${activeLocale}/login`, nextUrl)
    loginUrl.searchParams.set(
      'callbackUrl',
      pathWithoutLocale + (nextUrl.search || ''),
    )
    return NextResponse.redirect(loginUrl)
  }

  // Admin role check
  if (pathWithoutLocale.startsWith('/admin') && token) {
    const roleValues = [token.role, ...(Array.isArray(token.roles) ? token.roles : [])]
      .filter(Boolean)
      .map((r) => String(r).toLowerCase())
    if (!roleValues.includes('admin')) {
      return NextResponse.redirect(new URL(`/${activeLocale}`, nextUrl))
    }
  }

  return intlMiddleware(request)
}

export const config = {
  matcher: '/((?!api|healthz|_next/static|_next/image|favicon.ico|.*\\..*).*)',
}
```

### 2. Simple auth redirect

```ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  if (!request.cookies.has('session')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

export const config = { matcher: '/dashboard/:path*' }
```

### 3. CORS for API routes

```ts
const allowedOrigins = ['https://acme.com']
const corsOptions = {
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

export function proxy(request: NextRequest) {
  const origin = request.headers.get('origin') ?? ''
  const isAllowed = allowedOrigins.includes(origin)

  if (request.method === 'OPTIONS') {
    return NextResponse.json(
      {},
      {
        headers: {
          ...(isAllowed && { 'Access-Control-Allow-Origin': origin }),
          ...corsOptions,
        },
      },
    )
  }

  const response = NextResponse.next()
  if (isAllowed) response.headers.set('Access-Control-Allow-Origin', origin)
  Object.entries(corsOptions).forEach(([k, v]) => response.headers.set(k, v))
  return response
}

export const config = { matcher: '/api/:path*' }
```

### 4. Set headers to pass data to pages

```ts
export function proxy(request: NextRequest) {
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-user-id', '123')

  const response = NextResponse.next({
    request: { headers: requestHeaders }, // upstream (pages/api)
  })
  response.headers.set('x-custom', 'hello') // downstream (client)
  return response
}
```

## Important Gotchas

- **No shared globals**: Proxy runs separately from render code. Don't rely on shared modules/globals.
- **Pass data via headers/cookies/URL**: Use `NextResponse.next({ request: { headers } })` not `NextResponse.next({ headers })`.
- **RSC requests**: Next.js strips Flight headers (`rsc`, `next-router-state-tree`) from the proxy `request` object. Use `NextResponse.rewrite()` instead of manual `fetch` rewrite.
- **Server Functions**: Not separate routes — they POST to the route they're used in. A matcher that excludes a path also skips Server Function calls on that path. Always verify auth inside Server Functions too.
- **`_next/data` routes**: Continue to trigger proxy even if excluded in matcher (by design for security).
- **No `runtime` config**: Setting `runtime: 'edge'` or `runtime: 'nodejs'` in proxy config throws an error.
- **Migration codemod**: `npx @next/codemod@canary middleware-to-proxy .`

## Execution Order

1. `headers` from `next.config.js`
2. `redirects` from `next.config.js`
3. **Proxy** (rewrites, redirects, etc.)
4. `beforeFiles` rewrites
5. Filesystem routes (`public/`, `_next/static/`, `pages/`, `app/`)
6. `afterFiles` rewrites
7. Dynamic Routes (`/blog/[slug]`)
8. `fallback` rewrites

## Reference

- [Proxy API docs](https://nextjs.org/docs/app/api-reference/file-conventions/proxy)
- [NextRequest](https://nextjs.org/docs/app/api-reference/functions/next-request)
- [NextResponse](https://nextjs.org/docs/app/api-reference/functions/next-response)
- [Middleware to Proxy migration](https://nextjs.org/docs/messages/middleware-to-proxy)
