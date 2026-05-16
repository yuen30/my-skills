---
name: Next.js Layouts and Pages
description: Expert guidance for creating pages, layouts, nested routes, dynamic segments, and navigation with the Next.js App Router file-system based routing.
---

# Next.js Layouts and Pages

Expert guidance for creating pages, layouts, nested routes, dynamic segments, and navigation with the Next.js App Router file-system based routing.

@doc-version: 16.2.6

## Core Concepts

Next.js ใช้ระบบ **File-system based routing** — โครงสร้างโฟลเดอร์และไฟล์กำหนดเส้นทาง (Route) ของเว็บไซต์โดยตรง

## Guidelines

### 1. Pages (`page.tsx`)

ไฟล์ `page.tsx` คือ UI หลักที่แสดงผลเมื่อเข้าถึง URL นั้นๆ ต้อง `export default` component ออกมา

```tsx
// app/page.tsx → URL: /
export default function Home() {
  return <h1>Welcome</h1>
}
```

```tsx
// app/about/page.tsx → URL: /about
export default function About() {
  return <h1>About Us</h1>
}
```

**กฎสำคัญ:**
- ทุก route ต้องมี `page.tsx` ถึงจะเข้าถึงได้
- ต้อง `export default` เสมอ
- รองรับทั้ง Server Component (default) และ Client Component

### 2. Layouts (`layout.tsx`)

Layout คือ UI ที่ใช้ร่วมกันในหลายหน้า เช่น Navbar, Sidebar, Footer

```tsx
// app/layout.tsx — Root Layout (บังคับต้องมี)
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav>Navigation</nav>
        <main>{children}</main>
        <footer>Footer</footer>
      </body>
    </html>
  )
}
```

**คุณสมบัติสำคัญ:**
- Layout **ไม่ถูก re-render** เมื่อเปลี่ยนหน้าภายใน layout เดียวกัน
- รักษา State เดิมไว้ได้ (เช่น input ที่พิมพ์ค้างอยู่)
- รับ `children` prop ซึ่งคือ page หรือ nested layout

**Root Layout (บังคับ):**
- ต้องอยู่ที่ `app/layout.tsx`
- ต้องมีแท็ก `<html>` และ `<body>`
- ทุกหน้าจะถูกครอบด้วย Root Layout

### 3. Nested Routes & Nested Layouts

ใช้การซ้อนโฟลเดอร์เพื่อสร้าง URL ซ้อนกัน:

```
app/
├── layout.tsx              # Root layout
├── page.tsx                # /
└── dashboard/
    ├── layout.tsx          # Dashboard layout (ซ้อนใน Root)
    ├── page.tsx            # /dashboard
    └── settings/
        └── page.tsx        # /dashboard/settings
```

```tsx
// app/dashboard/layout.tsx — Nested Layout
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <aside>
        <nav>Dashboard Nav</nav>
      </aside>
      <section>{children}</section>
    </div>
  )
}
```

**ผลลัพธ์:** หน้า `/dashboard/settings` จะถูกครอบด้วย:
1. Root Layout (html, body, nav, footer)
2. Dashboard Layout (sidebar)
3. Settings Page (content)

### 4. Dynamic Segments (`[slug]`)

ใช้ `[]` ครอบชื่อโฟลเดอร์สำหรับ URL ที่เปลี่ยนแปลงตามข้อมูล:

```
app/blog/[slug]/page.tsx → /blog/hello-world, /blog/my-post
```

```tsx
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  )
}
```

**รูปแบบ Dynamic Segments:**

| Pattern | ตัวอย่าง URL | `params` |
|---------|-------------|----------|
| `[slug]` | `/blog/hello` | `{ slug: 'hello' }` |
| `[...slug]` | `/blog/a/b/c` | `{ slug: ['a', 'b', 'c'] }` |
| `[[...slug]]` | `/blog` หรือ `/blog/a/b` | `{ slug: undefined }` หรือ `{ slug: ['a', 'b'] }` |

**สำคัญ:** ใน Next.js 16 ต้องใช้ `await params` เสมอ (params เป็น Promise)

### 5. Search Parameters (Query Strings)

#### Server Components — ใช้ `searchParams` prop

```tsx
// app/search/page.tsx → /search?q=hello
export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q } = await searchParams
  const results = await search(q)

  return (
    <div>
      <h1>Results for: {q}</h1>
      {results.map((r) => <p key={r.id}>{r.title}</p>)}
    </div>
  )
}
```

#### Client Components — ใช้ `useSearchParams()`

```tsx
'use client'
import { useSearchParams } from 'next/navigation'

export function SearchFilter() {
  const searchParams = useSearchParams()
  const category = searchParams.get('category')

  return <div>Category: {category}</div>
}
```

**หมายเหตุ:** การใช้ `searchParams` ทำให้หน้านั้นเป็น **Dynamic Rendering** อัตโนมัติ (ไม่ถูก static generate)

### 6. Linking and Navigation (`<Link>`)

ใช้ `<Link>` จาก `next/link` แทน `<a>` เสมอ:

```tsx
import Link from 'next/link'

export function Navigation() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href="/blog/hello-world">Blog Post</Link>
      <Link href={`/products/${product.id}`}>View Product</Link>
    </nav>
  )
}
```

**ข้อดีของ `<Link>`:**
- **Prefetching** — โหลดข้อมูลหน้าปลายทางล่วงหน้าเมื่อ Link ปรากฏบนหน้าจอ
- **Client-side Navigation** — เปลี่ยนหน้าโดยไม่โหลดทั้งเว็บใหม่ (SPA experience)
- **Partial Rendering** — เฉพาะส่วนที่เปลี่ยนถูก re-render, layout คงเดิม

#### Programmatic Navigation

```tsx
'use client'
import { useRouter } from 'next/navigation'

export function LogoutButton() {
  const router = useRouter()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return <button onClick={handleLogout}>Logout</button>
}
```

### 7. TypeScript Route Props Helpers

Next.js มี Global types ให้ใช้โดยไม่ต้อง import:

```tsx
// PageProps — สำหรับ page.tsx
export default async function Page({ params, searchParams }: PageProps) {
  const { slug } = await params
  const { q } = await searchParams
  return <div>{slug} - {q}</div>
}
```

```tsx
// LayoutProps — สำหรับ layout.tsx
export default function Layout({ children, params }: LayoutProps) {
  return <div>{children}</div>
}
```

**Type definitions:**
- `PageProps`: มี `params` (Promise) และ `searchParams` (Promise)
- `LayoutProps`: มี `children` (ReactNode) และ `params` (Promise)

## Quick Reference

| ไฟล์ | หน้าที่ | Re-render เมื่อเปลี่ยนหน้า? |
|------|--------|---------------------------|
| `page.tsx` | UI หลักของ route | ✅ ใช่ |
| `layout.tsx` | UI ที่ใช้ร่วมกัน | ❌ ไม่ (รักษา state) |
| `template.tsx` | เหมือน layout แต่ re-render ทุกครั้ง | ✅ ใช่ |

## สรุป

- สร้างหน้าด้วย `page.tsx`
- ส่วนที่ใช้ร่วมกันสร้างด้วย `layout.tsx`
- URL ที่เปลี่ยนตามข้อมูลใช้ `[slug]`
- ใช้ `<Link>` เสมอเพื่อให้เว็บเร็วขึ้น
- `await params` และ `await searchParams` ใน Next.js 16
