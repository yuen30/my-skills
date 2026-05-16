---
name: Next.js Public Static Pages
description: Expert guidance on building public pages in Next.js — static components, cache components, streaming dynamic content, and Partial Prerendering.
---

# Next.js Public Static Pages

Expert guidance on building public pages in Next.js — static components, cache components, streaming dynamic content, and Partial Prerendering.

@doc-version: 16.2.6

## Core Concepts

Public pages แสดง content เดียวกันทุก user — prerender ล่วงหน้าได้:
- **Static components** — output ไม่เปลี่ยน, prerender ตอน build
- **Cache components** — fetch data แล้ว cache, prerender ได้เหมือน static
- **Dynamic components** — ขึ้นกับ request (user, location) → stream ตอน request time

**ผลลัพธ์:** Partial Prerendering (PPR) — static shell ส่งทันที + dynamic stream ตามหลัง

## Guidelines

### 1. Static Components (No Data)

```tsx
// app/products/page.tsx
function Header() {
  return <h1>Shop</h1>
}

export default async function Page() {
  return <Header />
}
```

- ไม่มี external data, request headers, params, time, random
- Prerender ตอน build อัตโนมัติ
- ไม่ต้อง config อะไร

### 2. Cache Components (Shared Data)

เมื่อ component fetch data ที่ shared ทุก user → ใช้ `"use cache"`:

```tsx
// app/products/page.tsx
import db from '@/db'
import { List } from '@/app/products/ui'

function Header() {
  return <h1>Shop</h1>
}

async function ProductList() {
  'use cache'
  const products = await db.product.findMany()
  return <List items={products} />
}

export default async function Page() {
  return (
    <>
      <Header />
      <ProductList />
    </>
  )
}
```

**ทำไมต้อง cache:**
- ไม่มี `"use cache"` → data fetch ทุก request → block response
- มี `"use cache"` → cache result → prerender ได้ → ไม่ block

**Build output:**
```
Route (app)      Revalidate  Expire
○ /products           15m      1y

○  (Static)  prerendered as static content
```

### 3. Dynamic Content + Streaming (PPR)

เมื่อบาง content ขึ้นกับ request (user location, A/B test) → stream ด้วย Suspense:

```tsx
// app/products/page.tsx
import { Suspense } from 'react'
import db from '@/db'
import { List, Promotion, PromotionSkeleton } from '@/app/products/ui'
import { getPromotion } from '@/app/products/data'

function Header() {
  return <h1>Shop</h1>
}

async function ProductList() {
  'use cache'
  const products = await db.product.findMany()
  return <List items={products} />
}

// Dynamic — depends on user/request
async function PromotionContent() {
  const promotion = await getPromotion() // user-specific
  return <Promotion data={promotion} />
}

export default async function Page() {
  return (
    <>
      <Suspense fallback={<PromotionSkeleton />}>
        <PromotionContent />
      </Suspense>
      <Header />
      <ProductList />
    </>
  )
}
```

**Build output:**
```
Route (app)      Revalidate  Expire
◐ /products    15m      1y

◐  (Partial Prerender)  Prerendered as static HTML with dynamic server-streamed content
```

**Request time flow:**
1. CDN serves prerendered shell ทันที (Header + ProductList + PromotionSkeleton)
2. Server renders PromotionContent → stream เข้ามาแทน skeleton

### 4. Component Types Summary

| Type | Characteristics | Rendering |
|------|----------------|-----------|
| **Static** | No data, no inputs | Prerendered at build |
| **Cache** (`"use cache"`) | Shared data, cacheable | Prerendered (cached) |
| **Dynamic** | Request-specific data | Streamed at request time |

### 5. Blocking Warning

ถ้า await data โดยไม่มี `"use cache"` หรือ `<Suspense>`:

```
Warning: Blocking data was accessed outside of Suspense
```

**แก้ไข:**
- Data shared ทุก user → `"use cache"` (prerender)
- Data per-user → `<Suspense>` (stream)

### 6. Decision Flow

```
Component มี async data?
├── ไม่มี → Static (prerender อัตโนมัติ)
│
└── มี → Data shared ทุก user?
    ├── ใช่ → "use cache" (prerender + cache)
    │
    └── ไม่ (per-user) → <Suspense> (stream)
```

### 7. Complete Pattern

```tsx
import { Suspense } from 'react'
import { cacheLife, cacheTag } from 'next/cache'

// Static — no data
function Header() {
  return <header><h1>My Store</h1></header>
}

// Static — no data
function Footer() {
  return <footer>© 2024</footer>
}

// Cache — shared data, prerendered
async function ProductGrid() {
  'use cache'
  cacheLife('hours')
  cacheTag('products')

  const products = await db.product.findMany({ where: { published: true } })
  return (
    <div className="grid grid-cols-3 gap-4">
      {products.map((p) => <ProductCard key={p.id} product={p} />)}
    </div>
  )
}

// Cache — shared data, prerendered
async function Categories() {
  'use cache'
  cacheLife('days')
  cacheTag('categories')

  const categories = await db.category.findMany()
  return <CategoryNav categories={categories} />
}

// Dynamic — per-user, streamed
async function PersonalizedBanner() {
  const user = await getCurrentUser() // request-specific
  const recommendation = await getRecommendation(user.id)
  return <Banner recommendation={recommendation} />
}

export default function Page() {
  return (
    <>
      <Header />
      <Categories />
      <Suspense fallback={<BannerSkeleton />}>
        <PersonalizedBanner />
      </Suspense>
      <ProductGrid />
      <Footer />
    </>
  )
}
```

**Result:** ส่วนใหญ่ของหน้า prerendered + cached → ส่งทันที จาก CDN, เฉพาะ PersonalizedBanner stream ตอน request

## Quick Reference

| Pattern | When | How |
|---------|------|-----|
| Static component | No data needed | Just render (auto prerender) |
| Cache component | Shared data (products, posts) | `"use cache"` + `cacheLife` |
| Dynamic + stream | Per-user data (recommendations) | `<Suspense fallback={...}>` |
| Revalidate cached | Data changes | `revalidateTag` / `updateTag` |

## สรุป

1. **Static components** — ไม่มี data → prerender อัตโนมัติ
2. **Cache components** — shared data + `"use cache"` → prerender ได้
3. **Dynamic components** — per-user data + `<Suspense>` → stream
4. **PPR** — static shell ส่งทันที + dynamic stream ตามหลัง
5. **Blocking warning** → ต้องเลือก: cache หรือ stream
6. **ไม่ต้อง config** — Next.js detect อัตโนมัติจาก code
