---
name: Next.js Multi-Zones
description: Expert guidance on building micro-frontends with Next.js Multi-Zones — separate apps under one domain, routing, assetPrefix, and cross-zone navigation.
---

# Next.js Multi-Zones

Expert guidance on building micro-frontends with Next.js Multi-Zones — separate apps under one domain, routing, assetPrefix, and cross-zone navigation.

@doc-version: 16.2.6

## Core Concepts

Multi-Zones แบ่ง large application เป็นหลาย Next.js apps ที่ serve ภายใต้ domain เดียวกัน:
- แต่ละ zone serve set of paths ที่แยกกัน
- Develop + deploy แต่ละ zone อิสระ
- ลด build time + bundle size ต่อ zone
- Zone อื่นใช้ framework อื่นได้

**Navigation:**
- **Soft navigation** — ภายใน zone เดียวกัน (ไม่ reload)
- **Hard navigation** — ข้าม zones (reload page)

## Guidelines

### 1. Example Architecture

```
Domain: example.com

Zone A (Main app):     /* (ทุก path ที่ไม่ตรงกับ zone อื่น)
Zone B (Blog):         /blog/*
Zone C (Dashboard):    /dashboard/*
```

แต่ละ zone เป็น Next.js app แยก — deploy แยก, repo แยกได้

### 2. Define a Zone (`assetPrefix`)

แต่ละ zone (ยกเว้น default) ต้องตั้ง `assetPrefix` เพื่อไม่ให้ static files ชนกัน:

```js
// next.config.js (Blog zone)
/** @type {import('next').NextConfig} */
const nextConfig = {
  assetPrefix: '/blog-static',
}

module.exports = nextConfig
```

- Assets ถูก serve ที่ `/blog-static/_next/...`
- Default zone (main app) ไม่ต้องตั้ง `assetPrefix`

> Next.js 15+ ไม่ต้อง rewrite สำหรับ static assets แล้ว

### 3. Route Requests to Correct Zone

#### ด้วย Rewrites (แนะนำ — low latency)

Main app ทำหน้าที่ route ไปยัง zones อื่น:

```js
// next.config.js (Main app — default zone)
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      // Blog zone
      {
        source: '/blog',
        destination: `${process.env.BLOG_DOMAIN}/blog`,
      },
      {
        source: '/blog/:path+',
        destination: `${process.env.BLOG_DOMAIN}/blog/:path+`,
      },
      {
        source: '/blog-static/:path+',
        destination: `${process.env.BLOG_DOMAIN}/blog-static/:path+`,
      },
      // Dashboard zone
      {
        source: '/dashboard',
        destination: `${process.env.DASHBOARD_DOMAIN}/dashboard`,
      },
      {
        source: '/dashboard/:path+',
        destination: `${process.env.DASHBOARD_DOMAIN}/dashboard/:path+`,
      },
      {
        source: '/dashboard-static/:path+',
        destination: `${process.env.DASHBOARD_DOMAIN}/dashboard-static/:path+`,
      },
    ]
  },
}

module.exports = nextConfig
```

```env
# .env.local
BLOG_DOMAIN=https://blog.internal.example.com
DASHBOARD_DOMAIN=https://dashboard.internal.example.com

# Local development
# BLOG_DOMAIN=http://localhost:3001
# DASHBOARD_DOMAIN=http://localhost:3002
```

#### ด้วย Proxy (Dynamic routing — feature flags)

```js
// proxy.js
import { NextResponse } from 'next/server'

export async function proxy(request) {
  const { pathname, search } = request.nextUrl

  // Feature flag: route /blog to new zone
  if (pathname.startsWith('/blog') && myFeatureFlag.isEnabled()) {
    return NextResponse.rewrite(
      `${process.env.BLOG_DOMAIN}${pathname}${search}`
    )
  }
}
```

### 4. Linking Between Zones

```tsx
// ✅ Same zone — ใช้ <Link> (soft navigation)
import Link from 'next/link'
<Link href="/products">Products</Link>

// ✅ Different zone — ใช้ <a> (hard navigation)
<a href="/blog/hello">Read Blog Post</a>
<a href="/dashboard">Go to Dashboard</a>
```

> `<Link>` จะพยายาม prefetch + soft navigate — ไม่ทำงานข้าม zones

### 5. Server Actions — Allowed Origins

เมื่อ domain เดียว serve หลาย apps ต้องระบุ allowed origins:

```js
// next.config.js (ทุก zone)
const nextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ['example.com', 'www.example.com'],
    },
  },
}
```

### 6. Sharing Code (Monorepo)

```
monorepo/
├── apps/
│   ├── main/          # Default zone (/)
│   │   ├── app/
│   │   └── next.config.js
│   ├── blog/          # Blog zone (/blog)
│   │   ├── app/
│   │   └── next.config.js
│   └── dashboard/     # Dashboard zone (/dashboard)
│       ├── app/
│       └── next.config.js
├── packages/
│   ├── ui/            # Shared components
│   ├── config/        # Shared config
│   └── utils/         # Shared utilities
└── package.json
```

- Monorepo ช่วย share code ง่าย
- ถ้าแยก repo → ใช้ NPM packages (public/private)
- Feature flags ช่วย enable/disable features ข้าม zones

### 7. Local Development

รัน multiple zones พร้อมกันบน different ports:

```json
// apps/main/package.json
{ "scripts": { "dev": "next dev -p 3000" } }

// apps/blog/package.json
{ "scripts": { "dev": "next dev -p 3001" } }

// apps/dashboard/package.json
{ "scripts": { "dev": "next dev -p 3002" } }
```

```env
# apps/main/.env.local
BLOG_DOMAIN=http://localhost:3001
DASHBOARD_DOMAIN=http://localhost:3002
```

ใช้ tools เช่น `turbo dev` หรือ `concurrently` รันทุก zones พร้อมกัน

## Important Rules

| Rule | Detail |
|------|--------|
| URL paths ต้อง unique ต่อ zone | 2 zones serve `/blog` ไม่ได้ |
| `assetPrefix` ต้อง unique ต่อ zone | ป้องกัน static files ชนกัน |
| Cross-zone links ใช้ `<a>` | `<Link>` ไม่ทำงานข้าม zones |
| Hard navigation ข้าม zones | Unload + reload resources |
| Pages ที่ visit ด้วยกันบ่อย → same zone | หลีกเลี่ยง hard navigation |

## Quick Reference

| Config | Purpose | Where |
|--------|---------|-------|
| `assetPrefix` | แยก static assets ต่อ zone | ทุก zone (ยกเว้น default) |
| `rewrites` | Route requests ไป zone อื่น | Default zone |
| `serverActions.allowedOrigins` | Allow cross-zone Server Actions | ทุก zone |
| Proxy | Dynamic routing (feature flags) | Default zone |

## สรุป

1. **แต่ละ zone = Next.js app แยก** — develop + deploy อิสระ
2. **`assetPrefix`** — ป้องกัน static files ชนกัน
3. **Rewrites ใน main app** — route requests ไป zone ที่ถูกต้อง
4. **Cross-zone links ใช้ `<a>`** — hard navigation (reload)
5. **Same-zone links ใช้ `<Link>`** — soft navigation (SPA)
6. **`serverActions.allowedOrigins`** — ระบุ domain ที่อนุญาต
7. **Monorepo** — share code ง่าย, deploy แยก
