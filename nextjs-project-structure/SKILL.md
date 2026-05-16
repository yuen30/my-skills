---
name: Next.js Project Structure
description: Expert guidance on Next.js folder/file conventions, routing files, dynamic routes, route groups, private folders, metadata files, and project organization strategies.
---

# Next.js Project Structure

Expert guidance on Next.js folder/file conventions, routing files, dynamic routes, route groups, private folders, metadata files, and project organization strategies.

@doc-version: 16.2.6

## Core Concepts

Next.js ใช้ file-system based routing — โครงสร้างโฟลเดอร์กำหนด URL routes โดยตรง Next.js ไม่บังคับวิธีจัดระเบียบโปรเจกต์ แต่มี conventions และ features ช่วย

## Guidelines

### 1. Top-level Folders

| Folder | Purpose |
|--------|---------|
| `app` | App Router (core routing) |
| `pages` | Pages Router (legacy) |
| `public` | Static assets (images, fonts, etc.) |
| `src` | Optional — separates source code from config files |

### 2. Top-level Files

| File | Purpose |
|------|---------|
| `next.config.js` | Configuration file for Next.js |
| `package.json` | Project dependencies and scripts |
| `instrumentation.ts` | OpenTelemetry and Instrumentation |
| `proxy.ts` | Next.js request proxy (formerly middleware) |
| `.env` | Environment variables |
| `.env.local` | Local environment variables (gitignored) |
| `.env.production` | Production environment variables |
| `.env.development` | Development environment variables |
| `eslint.config.mjs` | ESLint configuration |
| `tsconfig.json` | TypeScript configuration |
| `next-env.d.ts` | TypeScript declaration for Next.js (auto-generated) |

### 3. Routing Files

| File | Extensions | Purpose |
|------|-----------|---------|
| `layout` | `.js` `.jsx` `.tsx` | Layout (shared UI) |
| `page` | `.js` `.jsx` `.tsx` | Page (makes route public) |
| `loading` | `.js` `.jsx` `.tsx` | Loading UI (Suspense boundary) |
| `not-found` | `.js` `.jsx` `.tsx` | Not found UI (404) |
| `error` | `.js` `.jsx` `.tsx` | Error UI (Error boundary) |
| `global-error` | `.js` `.jsx` `.tsx` | Global error UI |
| `route` | `.js` `.ts` | API endpoint |
| `template` | `.js` `.jsx` `.tsx` | Re-rendered layout |
| `default` | `.js` `.jsx` `.tsx` | Parallel route fallback page |

### 4. Nested Routes

Folders define URL segments — nesting folders nests segments:

| Path | URL | Notes |
|------|-----|-------|
| `app/layout.tsx` | — | Root layout wraps all routes |
| `app/blog/layout.tsx` | — | Wraps `/blog` and descendants |
| `app/page.tsx` | `/` | Public route |
| `app/blog/page.tsx` | `/blog` | Public route |
| `app/blog/authors/page.tsx` | `/blog/authors` | Public route |

**กฎสำคัญ:** Route จะ public ก็ต่อเมื่อมี `page.js` หรือ `route.js` อยู่ในโฟลเดอร์นั้น

### 5. Dynamic Routes

| Pattern | URL Example | Notes |
|---------|-------------|-------|
| `app/blog/[slug]/page.tsx` | `/blog/my-first-post` | Single param |
| `app/shop/[...slug]/page.tsx` | `/shop/clothing/shirts` | Catch-all |
| `app/docs/[[...slug]]/page.tsx` | `/docs` หรือ `/docs/api/router` | Optional catch-all |

เข้าถึงค่าผ่าน `params` prop (ต้อง `await` ใน v16):

```tsx
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  return <div>{slug}</div>
}
```

### 6. Route Groups `(folderName)`

จัดกลุ่ม routes โดย **ไม่ส่งผลต่อ URL**:

| Path | URL | Notes |
|------|-----|-------|
| `app/(marketing)/page.tsx` | `/` | Group omitted from URL |
| `app/(shop)/cart/page.tsx` | `/cart` | Share layouts within `(shop)` |

**ใช้สำหรับ:**
- จัดกลุ่มตาม section (marketing, admin, shop)
- แยก layouts ในระดับเดียวกัน
- สร้าง multiple root layouts
- ใส่ `loading.tsx` เฉพาะบาง routes

#### Multiple Root Layouts

```
app/
├── (marketing)/
│   ├── layout.tsx      # Root layout สำหรับ marketing (มี <html><body>)
│   ├── page.tsx        # /
│   └── about/page.tsx  # /about
└── (shop)/
    ├── layout.tsx      # Root layout สำหรับ shop (มี <html><body>)
    ├── cart/page.tsx   # /cart
    └── products/page.tsx # /products
```

#### Opt-in Layout

```
app/
├── (shop)/
│   ├── layout.tsx      # Layout เฉพาะ account + cart
│   ├── account/page.tsx
│   └── cart/page.tsx
└── checkout/page.tsx   # ไม่ใช้ layout ของ (shop)
```

#### Loading Skeleton เฉพาะบาง Route

```
app/dashboard/
├── (overview)/
│   ├── loading.tsx     # Loading เฉพาะ overview page
│   └── page.tsx
└── settings/page.tsx   # ไม่มี loading skeleton
```

### 7. Private Folders `_folderName`

Prefix ด้วย underscore → **ไม่ถูกนำไปสร้างเป็น route**:

| Path | URL | Notes |
|------|-----|-------|
| `app/blog/_components/Post.tsx` | — | Not routable |
| `app/blog/_lib/data.ts` | — | Not routable |

**ใช้สำหรับ:**
- แยก UI logic จาก routing logic
- จัดระเบียบ internal files
- หลีกเลี่ยง naming conflicts กับ Next.js file conventions

> ถ้าต้องการ URL segment ที่ขึ้นต้นด้วย underscore ใช้ `%5F` (URL-encoded): `%5FfolderName`

### 8. Parallel Routes `@slot`

Named slots ที่ render โดย parent layout:

| Pattern | Meaning | Use Case |
|---------|---------|----------|
| `@folder` | Named slot | Sidebar + main content |

```
app/
├── layout.tsx          # รับ @analytics และ @team เป็น props
├── @analytics/page.tsx # Slot: analytics
├── @team/page.tsx      # Slot: team
└── page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div>
      {children}
      {analytics}
      {team}
    </div>
  )
}
```

### 9. Intercepting Routes

Render route อื่นใน current layout โดยไม่เปลี่ยน URL (เช่น modal):

| Pattern | Meaning | Use Case |
|---------|---------|----------|
| `(.)folder` | Intercept same level | Preview sibling as modal |
| `(..)folder` | Intercept parent | Open child as overlay |
| `(..)(..)folder` | Intercept two levels | Deeply nested overlay |
| `(...)folder` | Intercept from root | Show any route in current view |

### 10. Metadata File Conventions

#### App Icons

| File | Format | Purpose |
|------|--------|---------|
| `favicon` | `.ico` | Favicon |
| `icon` | `.ico` `.jpg` `.jpeg` `.png` `.svg` | App Icon |
| `icon` | `.js` `.ts` `.tsx` | Generated App Icon |
| `apple-icon` | `.jpg` `.jpeg` `.png` | Apple App Icon |
| `apple-icon` | `.js` `.ts` `.tsx` | Generated Apple App Icon |

#### Open Graph and Twitter

| File | Format | Purpose |
|------|--------|---------|
| `opengraph-image` | `.jpg` `.jpeg` `.png` `.gif` | OG image file |
| `opengraph-image` | `.js` `.ts` `.tsx` | Generated OG image |
| `twitter-image` | `.jpg` `.jpeg` `.png` `.gif` | Twitter image file |
| `twitter-image` | `.js` `.ts` `.tsx` | Generated Twitter image |

#### SEO

| File | Format | Purpose |
|------|--------|---------|
| `sitemap` | `.xml` | Sitemap file |
| `sitemap` | `.js` `.ts` | Generated Sitemap |
| `robots` | `.txt` | Robots file |
| `robots` | `.js` `.ts` | Generated Robots file |

### 11. Component Hierarchy

Special files render ในลำดับนี้:

```
layout.tsx
└── template.tsx
    └── error.tsx (React error boundary)
        └── loading.tsx (React suspense boundary)
            └── not-found.tsx (React error boundary)
                └── page.tsx หรือ nested layout.tsx
```

ใน nested routes — components ของ child segment ถูกซ้อนใน parent segment

### 12. Colocation

ไฟล์ใน `app` directory ที่ไม่ใช่ `page.js` หรือ `route.js` จะ **ไม่ถูก route** — สามารถวางไฟล์อื่นๆ ข้างๆ ได้อย่างปลอดภัย:

```
app/blog/
├── page.tsx            # ← routable (/blog)
├── PostCard.tsx        # ← ไม่ routable (safe)
├── utils.ts            # ← ไม่ routable (safe)
└── blog.module.css     # ← ไม่ routable (safe)
```

## Project Organization Strategies

### Strategy 1: Project files outside `app`

เก็บ code ทั้งหมดที่ root — ใช้ `app` เฉพาะ routing:

```
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       └── page.tsx
├── components/
│   ├── ui/
│   └── shared/
├── lib/
│   ├── db.ts
│   └── utils.ts
└── hooks/
```

### Strategy 2: Top-level folders inside `app`

เก็บ shared code ใน `app` ด้วย private folders:

```
├── app/
│   ├── _components/
│   ├── _lib/
│   ├── _hooks/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       └── page.tsx
```

### Strategy 3: Split by feature/route (Colocation)

เก็บไฟล์ที่เกี่ยวข้องไว้ข้างๆ route:

```
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       ├── _components/
│       │   └── stats-card.tsx
│       ├── _lib/
│       │   └── fetch-stats.ts
│       ├── layout.tsx
│       └── page.tsx
```

## Quick Reference

| Convention | Purpose | ส่งผลต่อ URL? |
|-----------|---------|:---:|
| `page.tsx` | ทำให้ route public | ✅ |
| `layout.tsx` | Shared UI | ❌ |
| `[slug]` | Dynamic segment | ✅ |
| `(group)` | Route group | ❌ |
| `_folder` | Private folder | ❌ |
| `@slot` | Parallel route | ❌ |
| `(.)folder` | Intercepting route | ❌ |

## สรุป

1. **Folders = URL segments** — nesting folders = nesting URLs
2. **`page.tsx` ทำให้ route public** — ไม่มี page = ไม่ accessible
3. **Route Groups `()`** — จัดกลุ่มไม่กระทบ URL
4. **Private Folders `_`** — exclude จาก routing
5. **Colocation ปลอดภัย** — ไฟล์ที่ไม่ใช่ page/route ไม่ถูก route
6. **เลือก strategy ที่เหมาะกับทีม** — consistent ทั้งโปรเจกต์
