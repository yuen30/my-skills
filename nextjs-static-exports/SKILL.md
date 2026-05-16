---
name: Next.js Static Exports
description: Expert guidance on creating static exports in Next.js — configuration, supported features, unsupported features, image optimization, and deployment.
---

# Next.js Static Exports

Expert guidance on creating static exports in Next.js — configuration, supported features, unsupported features, image optimization, and deployment.

@doc-version: 16.2.6

## Core Concepts

Static export สร้าง HTML/CSS/JS files ที่ deploy ได้บน **ทุก web server** ที่ serve static files — ไม่ต้องมี Node.js server

- เริ่มเป็น static site / SPA
- อัปเกรดเป็น server features ทีหลังได้
- ลด bundle size ด้วย per-route HTML files

## Guidelines

### 1. Configuration

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',

  // Optional: /me → /me/ and /me.html → /me/index.html
  // trailingSlash: true,

  // Optional: change output directory (default: out)
  // distDir: 'dist',
}

module.exports = nextConfig
```

```bash
next build
# Output: out/ folder with static HTML/CSS/JS
```

### 2. Supported Features

#### Server Components (Build-time)

```tsx
// app/page.tsx — runs during `next build`
export default async function Page() {
  const res = await fetch('https://api.example.com/data')
  const data = await res.json()
  return <main>{data.title}</main>
}
```

- Server Components รันตอน build (เหมือน SSG)
- ผลลัพธ์ = static HTML + static payload สำหรับ client navigation

#### Client Components

```tsx
'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function Page() {
  const { data, error } = useSWR('/api/posts', fetcher)
  if (error) return 'Failed to load'
  if (!data) return 'Loading...'
  return <div>{data.title}</div>
}
```

- Client-side data fetching ด้วย SWR/React Query
- Route transitions = client-side (SPA behavior)

#### Image Optimization (Custom Loader)

```js
// next.config.js
const nextConfig = {
  output: 'export',
  images: {
    loader: 'custom',
    loaderFile: './my-loader.ts',
  },
}
```

```ts
// my-loader.ts
export default function cloudinaryLoader({
  src,
  width,
  quality,
}: {
  src: string
  width: number
  quality?: number
}) {
  const params = ['f_auto', 'c_limit', `w_${width}`, `q_${quality || 'auto'}`]
  return `https://res.cloudinary.com/demo/image/upload/${params.join(',')}${src}`
}
```

```tsx
import Image from 'next/image'

export default function Page() {
  return <Image alt="photo" src="/photo.jpg" width={300} height={300} />
}
```

#### Route Handlers (GET only, static)

```ts
// app/data.json/route.ts
export async function GET() {
  return Response.json({ name: 'Lee' })
}
// → generates out/data.json containing { "name": "Lee" }
```

#### Dynamic Routes (with `generateStaticParams`)

```tsx
// app/blog/[id]/page.tsx
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then((r) => r.json())
  return posts.map((post: any) => ({ id: String(post.id) }))
}

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post = await fetch(`https://api.example.com/posts/${id}`).then((r) => r.json())
  return <article>{post.title}</article>
}
```

#### Browser APIs (Client Components)

```tsx
'use client'

import { useEffect } from 'react'

export default function ClientComponent() {
  useEffect(() => {
    // Safe — runs only in browser
    console.log(window.innerHeight)
  }, [])

  return <div>...</div>
}
```

### 3. Unsupported Features

| Feature | Why |
|---------|-----|
| Dynamic Routes without `generateStaticParams` | ต้องรู้ paths ตอน build |
| `dynamicParams: true` | ไม่มี server generate on-demand |
| Route Handlers ที่ใช้ Request | ไม่มี server ตอน runtime |
| Cookies / Headers | ไม่มี request ตอน runtime |
| Rewrites / Redirects (config) | ไม่มี server process |
| Proxy (Middleware) | ไม่มี server process |
| ISR | ไม่มี server revalidate |
| Image Optimization (default loader) | ต้อง custom loader |
| Draft Mode | ไม่มี server |
| Server Actions | ไม่มี server |
| Intercepting Routes | ต้อง server |

### 4. Deployment

#### Output Structure

```
out/
├── index.html          # /
├── 404.html            # 404 page
├── blog/
│   ├── post-1.html     # /blog/post-1
│   └── post-2.html     # /blog/post-2
├── _next/
│   ├── static/         # JS/CSS bundles
│   └── data/           # Static data
└── images/             # Optimized images (if custom loader)
```

#### Nginx Config

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/out;

    location / {
        try_files $uri $uri.html $uri/ =404;
    }

    # Required when trailingSlash: false
    location /blog/ {
        rewrite ^/blog/(.*)$ /blog/$1.html break;
    }

    error_page 404 /404.html;
    location = /404.html {
        internal;
    }
}
```

#### Deploy Targets

- AWS S3 + CloudFront
- GitHub Pages
- Netlify (static)
- Vercel (static)
- Nginx / Apache
- Firebase Hosting
- Any static file server

### 5. SPA Mode

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

```tsx
// app/page.tsx
import Link from 'next/link'

export default function Page() {
  return (
    <nav>
      <Link href="/about">About</Link>
      <Link href="/blog">Blog</Link>
    </nav>
  )
}
```

- `<Link>` ยังทำ client-side navigation (SPA)
- ไม่ full page reload ระหว่าง routes
- Prefetching ยังทำงาน

## Decision: Static Export vs Server

| Need | Static Export | Server (`next start`) |
|------|:-:|:-:|
| Static content only | ✅ | ✅ |
| Client-side data fetching | ✅ | ✅ |
| ISR / On-demand revalidation | ❌ | ✅ |
| Server Actions (forms) | ❌ | ✅ |
| Proxy (auth redirects) | ❌ | ✅ |
| Dynamic Routes (unknown paths) | ❌ | ✅ |
| Image Optimization (built-in) | ❌ | ✅ |
| Hosting cost | ต่ำมาก (static) | ต้องมี server |

## Quick Reference

| Config | Purpose |
|--------|---------|
| `output: 'export'` | Enable static export |
| `trailingSlash: true` | `/page` → `/page/index.html` |
| `distDir: 'dist'` | Change output directory |
| `images.loader: 'custom'` | Custom image optimization |
| `images.loaderFile` | Path to loader function |

## สรุป

1. **`output: 'export'`** — สร้าง static HTML/CSS/JS ใน `out/`
2. **Server Components** — รันตอน build (SSG)
3. **Client Components** — SWR/React Query สำหรับ client data
4. **Dynamic Routes** — ต้องมี `generateStaticParams`
5. **Images** — ต้อง custom loader (Cloudinary, imgix, etc.)
6. **Route Handlers** — เฉพาะ GET static
7. **Deploy ได้ทุกที่** — S3, GitHub Pages, Nginx, etc.
8. **ไม่รองรับ:** ISR, Server Actions, Proxy, Cookies, Headers
