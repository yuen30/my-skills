---
name: Next.js Backend for Frontend
description: Expert guidance on using Next.js as a backend — Route Handlers, Proxy, content negotiation, webhooks, proxying to backends, and security best practices.
---

# Next.js Backend for Frontend

Expert guidance on using Next.js as a backend — Route Handlers, Proxy, content negotiation, webhooks, proxying to backends, and security best practices.

@doc-version: 16.2.6

## Core Concepts

Next.js รองรับ "Backend for Frontend" pattern — สร้าง public endpoints ที่:
- รับ HTTP requests ทุกประเภท
- Return content type ใดก็ได้ (ไม่ใช่แค่ HTML)
- เข้าถึง data sources และทำ side effects

ใช้ผ่าน:
- **Route Handlers** (`route.ts`) — API endpoints
- **Proxy** (`proxy.ts`) — request interception
- **Rewrites** (`next.config.js`) — URL mapping

## Guidelines

### 1. Public Endpoints (Route Handlers)

```ts
// app/api/route.ts
export function GET(request: Request) {
  return Response.json({ message: 'Hello' })
}
```

#### Error Handling

```ts
// app/api/route.ts
import { submit } from '@/lib/submit'

export async function POST(request: Request) {
  try {
    await submit(request)
    return new Response(null, { status: 204 })
  } catch (reason) {
    const message = reason instanceof Error ? reason.message : 'Unexpected error'
    return new Response(message, { status: 500 })
  }
}
```

> อย่า expose sensitive information ใน error messages ที่ส่งไป client

### 2. Content Types

Route Handlers serve ได้ทุก content type:

#### RSS Feed

```ts
// app/rss.xml/route.ts
export async function GET() {
  const rssResponse = await fetch('https://api.example.com/posts')
  const posts = await rssResponse.json()

  const rssFeed = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>My Blog</title>
    ${posts.map((post: any) => `
    <item>
      <title>${post.title}</title>
      <link>${post.url}</link>
      <pubDate>${post.date}</pubDate>
    </item>`).join('')}
  </channel>
</rss>`

  return new Response(rssFeed, {
    headers: { 'Content-Type': 'application/xml' },
  })
}
```

#### Custom Content Types

| URL Pattern | Use Case |
|-------------|----------|
| `app/rss.xml/route.ts` | RSS feed |
| `app/llms.txt/route.ts` | LLM documentation |
| `app/.well-known/[...path]/route.ts` | Well-known URIs |
| `app/api/export/route.ts` | CSV/Excel export |

### 3. Content Negotiation

Serve different content จาก URL เดียวกันตาม `Accept` header:

#### Rewrite Config

```js
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/docs/:slug*',
        destination: '/docs/md/:slug*',
        has: [
          {
            type: 'header',
            key: 'accept',
            value: '(.*)text/markdown(.*)',
          },
        ],
      },
    ]
  },
}
```

#### Markdown Route Handler

```ts
// app/docs/md/[...slug]/route.ts
import { getDocsMd, generateDocsStaticParams } from '@/lib/docs'

export async function generateStaticParams() {
  return generateDocsStaticParams()
}

export async function GET(_: Request, ctx: RouteContext<'/docs/md/[...slug]'>) {
  const { slug } = await ctx.params
  const mdDoc = await getDocsMd({ slug })

  if (mdDoc == null) {
    return new Response(null, { status: 404 })
  }

  return new Response(mdDoc, {
    headers: {
      'Content-Type': 'text/markdown; charset=utf-8',
      Vary: 'Accept', // บอก CDN ว่า response ขึ้นกับ Accept header
    },
  })
}
```

```bash
# Returns Markdown
curl -H "Accept: text/markdown" https://example.com/docs/getting-started

# Returns HTML page
curl https://example.com/docs/getting-started
```

### 4. Consuming Request Payloads

```ts
// JSON body
export async function POST(request: Request) {
  const data = await request.json()
  return Response.json({ received: data })
}

// Form data
export async function POST(request: Request) {
  const formData = await request.formData()
  const email = formData.get('email')
  const contents = formData.get('contents')
  // validate + process
}

// Text body
export async function POST(request: Request) {
  const text = await request.text()
  return new Response(text)
}
```

> **สำคัญ:** Request body อ่านได้ครั้งเดียว — ใช้ `request.clone()` ถ้าต้องอ่านซ้ำ

### 5. Data Manipulation

Transform, filter, aggregate data จากหลาย sources:

```ts
// app/api/weather/route.ts
import { parseWeatherData } from '@/lib/weather'

export async function POST(request: Request) {
  const body = await request.json()
  const searchParams = new URLSearchParams({ lat: body.lat, lng: body.lng })

  try {
    const weatherResponse = await fetch(`${weatherEndpoint}?${searchParams}`)
    if (!weatherResponse.ok) {
      return new Response('Weather service unavailable', { status: 502 })
    }

    const weatherData = await weatherResponse.text()
    const payload = parseWeatherData.asJSON(weatherData)
    return new Response(payload, { status: 200 })
  } catch (reason) {
    const message = reason instanceof Error ? reason.message : 'Unexpected exception'
    return new Response(message, { status: 500 })
  }
}
```

> ใช้ `POST` เมื่อ request มี sensitive data (geo-location) — `GET` อาจถูก cache/log

### 6. Proxying to a Backend

```ts
// app/api/[...slug]/route.ts
import { isValidRequest } from '@/lib/utils'

export async function POST(request: Request, { params }: { params: Promise<{ slug: string[] }> }) {
  const clonedRequest = request.clone()
  const isValid = await isValidRequest(clonedRequest)

  if (!isValid) {
    return new Response(null, { status: 400, statusText: 'Bad Request' })
  }

  const { slug } = await params
  const pathname = slug.join('/')
  const proxyURL = new URL(pathname, 'https://api.example.com')
  const proxyRequest = new Request(proxyURL, request)

  try {
    return fetch(proxyRequest)
  } catch (reason) {
    const message = reason instanceof Error ? reason.message : 'Unexpected exception'
    return new Response(message, { status: 500 })
  }
}
```

### 7. Webhooks and Callback URLs

#### Webhook (CMS revalidation)

```ts
// app/webhook/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { revalidateTag } from 'next/cache'

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get('token')

  if (token !== process.env.REVALIDATE_SECRET_TOKEN) {
    return NextResponse.json({ success: false }, { status: 401 })
  }

  const tag = request.nextUrl.searchParams.get('tag')
  if (!tag) {
    return NextResponse.json({ success: false }, { status: 400 })
  }

  revalidateTag(tag)
  return NextResponse.json({ success: true })
}
```

#### OAuth Callback

```ts
// app/auth/callback/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get('session_token')
  const redirectUrl = request.nextUrl.searchParams.get('redirect_url')

  const response = NextResponse.redirect(new URL(redirectUrl!, request.url))
  response.cookies.set({
    value: token!,
    name: '_token',
    path: '/',
    secure: true,
    httpOnly: true,
    expires: undefined, // session cookie
  })

  return response
}
```

### 8. Proxy for Auth Gate

```ts
// proxy.ts
import { isAuthenticated } from '@/lib/auth'

export const config = {
  matcher: '/api/:function*',
}

export function proxy(request: Request) {
  if (!isAuthenticated(request)) {
    return Response.json(
      { success: false, message: 'authentication failed' },
      { status: 401 }
    )
  }
}
```

### 9. Security Best Practices

| Practice | Description |
|----------|-------------|
| Validate inputs | ตรวจสอบ content type, size, sanitize XSS |
| Rate limiting | ป้องกัน abuse + ใช้ host-level rate limiting |
| Verify credentials | ตรวจสอบ auth ก่อนให้เข้าถึง resources |
| Minimal responses | ลบ sensitive data จาก responses + logs |
| Rotate secrets | เปลี่ยน API keys สม่ำเสมอ |
| Timeouts | ป้องกัน long-running requests |
| Header safety | อย่าส่ง request headers ไป response โดยตรง |

### 10. NextRequest and NextResponse

```ts
import { type NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const nextUrl = request.nextUrl

  if (nextUrl.searchParams.get('redirect')) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  if (nextUrl.searchParams.get('rewrite')) {
    return NextResponse.rewrite(new URL('/', request.url))
  }

  return NextResponse.json({ pathname: nextUrl.pathname })
}
```

## Caveats

| สถานการณ์ | คำแนะนำ |
|-----------|---------|
| Server Components ต้องการ data | Fetch จาก source โดยตรง ไม่ผ่าน Route Handler |
| Build time (prerender) | Route Handler ไม่มี server → build fail |
| Server Actions | ใช้สำหรับ mutations ไม่ใช่ data fetching (sequential) |
| Static export (`output: 'export'`) | เฉพาะ GET + `force-static` เท่านั้น |
| Serverless/Lambda | ไม่ share data ข้าม requests, ไม่มี filesystem write, timeout |
| WebSockets | ไม่ทำงานบน serverless (connection closes) |

## Quick Reference

| Feature | File | Purpose |
|---------|------|---------|
| Route Handler | `app/api/route.ts` | API endpoint |
| Proxy | `proxy.ts` | Request interception |
| Rewrites | `next.config.js` | URL mapping |
| Webhook | `app/webhook/route.ts` | External event handling |
| Callback | `app/auth/callback/route.ts` | OAuth/third-party flows |

## สรุป

1. **Route Handlers** — public HTTP endpoints, ทุก method, ทุก content type
2. **Proxy** — auth gate, redirects, rewrites ก่อนถึง route
3. **Content negotiation** — rewrites + Accept header
4. **Validate ทุก input** — อย่าเชื่อ request data
5. **Server Components fetch ตรง** — ไม่ผ่าน Route Handler
6. **ใช้ try/catch** — อย่า expose sensitive errors
7. **Rate limit + auth** — ป้องกัน abuse
