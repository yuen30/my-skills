---
name: Next.js Route Handlers
description: Expert guidance on creating API endpoints with Next.js Route Handlers — HTTP methods, caching, request/response helpers, and route resolution rules.
---

# Next.js Route Handlers

Expert guidance on creating API endpoints with Next.js Route Handlers — HTTP methods, caching, request/response helpers, and route resolution rules.

@doc-version: 16.2.6

## Core Concepts

Route Handlers ใช้สร้าง custom API endpoints ด้วย Web Request/Response APIs — เทียบเท่า API Routes ใน Pages Router แต่ใช้ใน `app` directory

- ไฟล์: `route.ts` (หรือ `route.js`)
- ใช้ Web standard Request/Response APIs
- รองรับ HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`

## Guidelines

### 1. Basic Route Handler

```tsx
// app/api/route.ts
export async function GET(request: Request) {
  return Response.json({ message: 'Hello, World!' })
}
```

### 2. HTTP Methods

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server'

// GET /api/posts
export async function GET(request: NextRequest) {
  const posts = await db.post.findMany()
  return NextResponse.json(posts)
}

// POST /api/posts
export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await db.post.create({ data: body })
  return NextResponse.json(post, { status: 201 })
}
```

```tsx
// app/api/posts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server'

// GET /api/posts/:id
export async function GET(
  request: NextRequest,
  ctx: RouteContext<'/api/posts/[id]'>
) {
  const { id } = await ctx.params
  const post = await db.post.findUnique({ where: { id } })

  if (!post) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  return NextResponse.json(post)
}

// PUT /api/posts/:id
export async function PUT(
  request: NextRequest,
  ctx: RouteContext<'/api/posts/[id]'>
) {
  const { id } = await ctx.params
  const body = await request.json()
  const post = await db.post.update({ where: { id }, data: body })
  return NextResponse.json(post)
}

// DELETE /api/posts/:id
export async function DELETE(
  request: NextRequest,
  ctx: RouteContext<'/api/posts/[id]'>
) {
  const { id } = await ctx.params
  await db.post.delete({ where: { id } })
  return new NextResponse(null, { status: 204 })
}
```

> Method ที่ไม่ได้ export → Next.js return `405 Method Not Allowed` อัตโนมัติ

### 3. Request Helpers

#### Query Parameters

```tsx
// GET /api/search?q=hello&page=2
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get('q')    // 'hello'
  const page = searchParams.get('page')  // '2'

  const results = await search(query, Number(page))
  return NextResponse.json(results)
}
```

#### Headers

```tsx
import { headers } from 'next/headers'

export async function GET() {
  const headersList = await headers()
  const userAgent = headersList.get('user-agent')
  return NextResponse.json({ userAgent })
}
```

#### Cookies

```tsx
import { cookies } from 'next/headers'

export async function GET() {
  const cookieStore = await cookies()
  const token = cookieStore.get('session')?.value

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  return NextResponse.json({ authenticated: true })
}
```

#### Request Body

```tsx
export async function POST(request: NextRequest) {
  // JSON body
  const json = await request.json()

  // Form data
  const formData = await request.formData()
  const name = formData.get('name')

  // Text body
  const text = await request.text()

  return NextResponse.json({ received: true })
}
```

### 4. Response Helpers

```tsx
// JSON response
return NextResponse.json({ data: 'value' })

// JSON with status
return NextResponse.json({ error: 'Not found' }, { status: 404 })

// Custom headers
return new NextResponse(JSON.stringify(data), {
  status: 200,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'max-age=3600',
  },
})

// Redirect
return NextResponse.redirect(new URL('/login', request.url))

// No content
return new NextResponse(null, { status: 204 })

// Stream response
const stream = new ReadableStream({
  async start(controller) {
    controller.enqueue(new TextEncoder().encode('Hello'))
    controller.close()
  },
})
return new NextResponse(stream)
```

### 5. Caching

Route Handlers **ไม่ถูก cache** โดย default ยกเว้น `GET` ที่ opt-in:

#### Without Cache Components (legacy)

```tsx
// app/api/items/route.ts
export const dynamic = 'force-static'

export async function GET() {
  const res = await fetch('https://api.example.com/data', {
    headers: { 'API-Key': process.env.DATA_API_KEY! },
  })
  const data = await res.json()
  return Response.json({ data })
}
```

#### With Cache Components

เมื่อเปิด `cacheComponents: true`:

**Static (prerendered at build time):**

```tsx
// app/api/project-info/route.ts
export async function GET() {
  return Response.json({ projectName: 'Next.js' })
}
```

**Dynamic (request time):**

```tsx
// app/api/random-number/route.ts
export async function GET() {
  return Response.json({ randomNumber: Math.random() })
}
```

**Runtime data (request time):**

```tsx
// app/api/user-agent/route.ts
import { headers } from 'next/headers'

export async function GET() {
  const headersList = await headers()
  const userAgent = headersList.get('user-agent')
  return Response.json({ userAgent })
}
```

**Cached with `use cache` (ต้องแยกเป็น helper function):**

```tsx
// app/api/products/route.ts
import { cacheLife } from 'next/cache'

export async function GET() {
  const products = await getProducts()
  return Response.json(products)
}

async function getProducts() {
  'use cache'
  cacheLife('hours')
  return await db.query('SELECT * FROM products')
}
```

> `use cache` ใช้ตรงใน Route Handler body ไม่ได้ — ต้องแยกเป็น helper function

**สิ่งที่ทำให้ prerendering หยุด:**
- Network requests, database queries
- `request.url`, `request.headers`, `request.cookies`, `request.body`
- Runtime APIs: `cookies()`, `headers()`, `connection()`
- Non-deterministic operations: `Math.random()`, `Date.now()`

### 6. Route Resolution Rules

**กฎสำคัญ:** `route.ts` กับ `page.tsx` อยู่ใน route segment เดียวกันไม่ได้

| Page | Route | Result |
|------|-------|--------|
| `app/page.js` | `app/route.js` | ✗ Conflict |
| `app/page.js` | `app/api/route.js` | ✓ Valid |
| `app/[user]/page.js` | `app/api/route.js` | ✓ Valid |

**Route Handler characteristics:**
- ไม่มี layouts
- ไม่มี client-side navigation
- เป็น lowest level routing primitive

### 7. Nested Routes

```
app/
└── api/
    ├── route.ts              # /api
    ├── posts/
    │   ├── route.ts          # /api/posts
    │   └── [id]/
    │       └── route.ts      # /api/posts/:id
    ├── users/
    │   ├── route.ts          # /api/users
    │   └── [id]/
    │       ├── route.ts      # /api/users/:id
    │       └── posts/
    │           └── route.ts  # /api/users/:id/posts
    └── auth/
        ├── login/
        │   └── route.ts      # /api/auth/login
        └── logout/
            └── route.ts      # /api/auth/logout
```

### 8. TypeScript — RouteContext Helper

```tsx
// app/users/[id]/route.ts
import type { NextRequest } from 'next/server'

export async function GET(_req: NextRequest, ctx: RouteContext<'/users/[id]'>) {
  const { id } = await ctx.params
  return Response.json({ id })
}
```

> Types ถูก generate ตอน `next dev`, `next build`, หรือ `next typegen`

### 9. Common Patterns

#### CORS

```tsx
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}

export async function GET(request: NextRequest) {
  const data = await getData()

  return NextResponse.json(data, {
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  })
}
```

#### File Upload

```tsx
export async function POST(request: NextRequest) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)

  // Save file
  await writeFile(`./uploads/${file.name}`, buffer)

  return NextResponse.json({ filename: file.name, size: file.size })
}
```

#### Streaming (SSE)

```tsx
export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(encoder.encode(`data: Message ${i}\n\n`))
        await new Promise((r) => setTimeout(r, 1000))
      }
      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  })
}
```

## Quick Reference

| HTTP Method | ใช้สำหรับ | Cached? |
|-------------|----------|---------|
| `GET` | อ่านข้อมูล | Opt-in ได้ |
| `POST` | สร้างข้อมูล | ❌ ไม่ cache |
| `PUT` | อัปเดตทั้งหมด | ❌ ไม่ cache |
| `PATCH` | อัปเดตบางส่วน | ❌ ไม่ cache |
| `DELETE` | ลบข้อมูล | ❌ ไม่ cache |
| `HEAD` | เช็ค headers | ❌ ไม่ cache |
| `OPTIONS` | CORS preflight | ❌ ไม่ cache |

## สรุป

1. สร้าง API ด้วย `route.ts` — export functions ตาม HTTP method
2. ใช้ Web standard Request/Response APIs (+ NextRequest/NextResponse helpers)
3. `route.ts` กับ `page.tsx` อยู่ route segment เดียวกันไม่ได้
4. GET ไม่ถูก cache โดย default — opt-in ด้วย `force-static` หรือ `use cache`
5. POST, PUT, DELETE ไม่ถูก cache เลย
6. ใช้ `RouteContext` helper สำหรับ typed params
