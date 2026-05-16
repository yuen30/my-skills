---
name: Next.js Metadata and OG Images
description: Expert guidance on adding metadata for SEO, static/dynamic OG images, favicons, sitemaps, and robots.txt in Next.js App Router.
---

# Next.js Metadata and OG Images

Expert guidance on adding metadata for SEO, static/dynamic OG images, favicons, sitemaps, and robots.txt in Next.js App Router.

@doc-version: 16.2.6

## Core Concepts

Next.js มี Metadata APIs 3 แบบ:
1. **Static `metadata` object** — export ค่าคงที่
2. **Dynamic `generateMetadata` function** — fetch ข้อมูลมาสร้าง metadata
3. **File conventions** — ไฟล์พิเศษ (favicon, OG image, sitemap, robots.txt)

Next.js สร้าง `<head>` tags ให้อัตโนมัติ — รองรับเฉพาะ Server Components

## Default Fields

Next.js เพิ่ม 2 meta tags อัตโนมัติเสมอ:
```html
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

## Guidelines

### 1. Static Metadata

Export `metadata` object จาก `layout.tsx` หรือ `page.tsx`:

```tsx
// app/blog/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My Blog',
  description: 'A blog about web development',
  openGraph: {
    title: 'My Blog',
    description: 'A blog about web development',
    images: ['/og-blog.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My Blog',
    description: 'A blog about web development',
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
```

#### Common Metadata Fields

```tsx
export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Page description for SEO',
  keywords: ['Next.js', 'React', 'TypeScript'],
  authors: [{ name: 'Author Name' }],
  creator: 'Creator Name',
  openGraph: {
    title: 'OG Title',
    description: 'OG Description',
    url: 'https://example.com',
    siteName: 'Site Name',
    images: [
      {
        url: '/og.png',
        width: 1200,
        height: 630,
        alt: 'OG Image Alt',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Twitter Title',
    description: 'Twitter Description',
    images: ['/twitter-image.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
  alternates: {
    canonical: 'https://example.com/page',
  },
}
```

### 2. Dynamic Metadata (`generateMetadata`)

ใช้เมื่อ metadata ขึ้นกับข้อมูล (เช่น blog post title):

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata, ResolvingMetadata } from 'next'

type Props = {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

export async function generateMetadata(
  { params, searchParams }: Props,
  parent: ResolvingMetadata
): Promise<Metadata> {
  const slug = (await params).slug

  // fetch post information
  const post = await fetch(`https://api.vercel.app/blog/${slug}`).then((res) =>
    res.json()
  )

  return {
    title: post.title,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      images: [post.coverImage],
    },
  }
}

export default function Page({ params, searchParams }: Props) {
  // ...
}
```

#### Memoizing Data (ป้องกัน fetch ซ้ำ)

เมื่อ `generateMetadata` และ page ต้องใช้ข้อมูลเดียวกัน:

```tsx
// app/lib/data.ts
import { cache } from 'react'
import { db } from '@/app/lib/db'

// เรียก 2 ครั้ง แต่ execute แค่ครั้งเดียว
export const getPost = cache(async (slug: string) => {
  const res = await db.query.posts.findFirst({ where: eq(posts.slug, slug) })
  return res
})
```

```tsx
// app/blog/[slug]/page.tsx
import { getPost } from '@/app/lib/data'

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug) // ใช้ cache
  return { title: post.title, description: post.description }
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug) // ใช้ cache — ไม่ fetch ซ้ำ
  return <div>{post.title}</div>
}
```

#### Streaming Metadata

- Dynamic pages: metadata ถูก stream แยก ไม่ block UI rendering
- **Bots/crawlers** (Twitterbot, Slackbot, Bingbot): streaming ถูกปิด — metadata อยู่ใน `<head>` ทันที
- Prerendered pages: metadata ถูก resolve ตอน build time

### 3. File-based Metadata

#### Favicons

วาง `favicon.ico` ที่ root ของ `app` folder:

```
app/
├── favicon.ico          # Browser tab icon
├── icon.png             # App icon (various sizes)
├── apple-icon.png       # Apple device icon
├── layout.tsx
└── page.tsx
```

#### Static Open Graph Images

วาง `opengraph-image.jpg` ในโฟลเดอร์ route:

```
app/
├── opengraph-image.jpg      # Default OG image (ทั้งแอป)
├── twitter-image.jpg        # Twitter card image
├── layout.tsx
└── blog/
    ├── opengraph-image.jpg  # OG image เฉพาะ /blog (override ตัวบน)
    └── page.tsx
```

- ภาพที่อยู่ลึกกว่าจะ override ภาพที่อยู่ข้างบน
- รองรับ `.jpg`, `.jpeg`, `.png`, `.gif`

#### robots.txt

```
app/
└── robots.txt
```

หรือสร้างแบบ dynamic:

```tsx
// app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: '/private/',
    },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

#### sitemap.xml

```tsx
// app/sitemap.ts
import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://example.com',
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 1,
    },
    {
      url: 'https://example.com/blog',
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.8,
    },
  ]
}
```

### 4. Generated OG Images (`ImageResponse`)

สร้าง dynamic OG images ด้วย JSX + CSS:

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'
import { getPost } from '@/app/lib/data'

// Image metadata
export const size = {
  width: 1200,
  height: 630,
}

export const contentType = 'image/png'

// Image generation
export default async function Image({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)

  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 128,
          background: 'white',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {post.title}
      </div>
    )
  )
}
```

#### OG Image with Styling

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'
import { getPost } from '@/app/lib/data'

export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function Image({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)

  return new ImageResponse(
    (
      <div
        style={{
          height: '100%',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#1a1a2e',
          color: 'white',
          padding: '40px',
        }}
      >
        <div style={{ fontSize: 60, fontWeight: 'bold', textAlign: 'center' }}>
          {post.title}
        </div>
        <div style={{ fontSize: 30, marginTop: 20, opacity: 0.8 }}>
          {post.author} · {post.date}
        </div>
      </div>
    )
  )
}
```

**ข้อจำกัดของ `ImageResponse`:**
- รองรับเฉพาะ flexbox layout
- ไม่รองรับ `display: grid`
- รองรับ CSS subset (absolute positioning, text wrapping, nested images)

### 5. Title Templates

ใช้ template สำหรับ title ที่มี pattern ซ้ำ:

```tsx
// app/layout.tsx
export const metadata: Metadata = {
  title: {
    template: '%s | My Site',  // %s = title ของ child page
    default: 'My Site',        // fallback ถ้า child ไม่มี title
  },
}
```

```tsx
// app/blog/page.tsx
export const metadata: Metadata = {
  title: 'Blog', // ผลลัพธ์: "Blog | My Site"
}
```

## File Conventions Summary

| File | Purpose | Location |
|------|---------|----------|
| `favicon.ico` | Browser tab icon | `app/` root |
| `icon.png` | App icon | `app/` or route folder |
| `apple-icon.png` | Apple device icon | `app/` root |
| `opengraph-image.jpg` | Social share image | Any route folder |
| `twitter-image.jpg` | Twitter card image | Any route folder |
| `opengraph-image.tsx` | Dynamic OG image | Any route folder |
| `robots.txt` / `robots.ts` | Crawler instructions | `app/` root |
| `sitemap.xml` / `sitemap.ts` | Search engine sitemap | `app/` root |

## Quick Reference

| วิธี | ใช้เมื่อ |
|------|---------|
| `export const metadata` | Static metadata (title, description คงที่) |
| `export async function generateMetadata` | Dynamic metadata (ขึ้นกับข้อมูล) |
| `opengraph-image.jpg` | Static OG image |
| `opengraph-image.tsx` + `ImageResponse` | Dynamic OG image (ขึ้นกับข้อมูล) |
| `React.cache()` | Memoize data ที่ใช้ทั้ง metadata + page |

## สรุป

1. **Static metadata** — export `metadata` object สำหรับค่าคงที่
2. **Dynamic metadata** — `generateMetadata` สำหรับข้อมูลที่ fetch มา
3. **File-based** — วางไฟล์ (favicon, OG image, sitemap) ตาม convention
4. **Dynamic OG images** — `ImageResponse` + JSX สร้างภาพ on-the-fly
5. **Memoize** — ใช้ `React.cache()` ป้องกัน fetch ซ้ำระหว่าง metadata + page
6. **Title template** — `%s | Site Name` pattern
