---
name: Next.js Revalidating
description: Expert guidance on revalidating cached data in Next.js using time-based (cacheLife) and on-demand (revalidateTag, updateTag, revalidatePath) strategies.
---

# Next.js Revalidating

Expert guidance on revalidating cached data in Next.js using time-based (cacheLife) and on-demand (revalidateTag, updateTag, revalidatePath) strategies.

@doc-version: 16.2.6

## Core Concepts

Revalidation คือกระบวนการอัปเดต cached data — ให้ response ยังเร็วจาก cache แต่ content ยังคง fresh

**2 กลยุทธ์หลัก:**
- **Time-based** — refresh อัตโนมัติตามเวลาที่กำหนด (`cacheLife`)
- **On-demand** — invalidate ด้วยมือหลัง mutation (`revalidateTag`, `updateTag`, `revalidatePath`)

> ต้องเปิด `cacheComponents: true` ใน next.config.ts

## Guidelines

### 1. `cacheLife` — Time-based Revalidation

ควบคุมว่า cached data จะ valid นานแค่ไหน ใช้ภายใน `"use cache"` scope:

```tsx
// app/lib/data.ts
import { cacheLife } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheLife('hours')
  return db.query('SELECT * FROM products')
}
```

#### Built-in Profiles

| Profile | `stale` | `revalidate` | `expire` |
|---------|---------|--------------|----------|
| `seconds` | 0 | 1s | 60s |
| `minutes` | 5m | 1m | 1h |
| `hours` | 5m | 1h | 1d |
| `days` | 5m | 1d | 1w |
| `weeks` | 5m | 1w | 30d |
| `max` | 5m | 30d | ~indefinite |

#### Custom Configuration

```tsx
'use cache'
cacheLife({
  stale: 3600,      // 1 hour — ยังใช้ stale content ได้
  revalidate: 7200, // 2 hours — revalidate ใน background
  expire: 86400,    // 1 day — หลังจากนี้ cache หมดอายุ
})
```

**ความหมายของแต่ละค่า:**
- **`stale`** — ระยะเวลาที่ client ใช้ cached content โดยไม่เช็ค server
- **`revalidate`** — ระยะเวลาก่อน server จะ regenerate cache ใน background
- **`expire`** — ระยะเวลาสูงสุดก่อน cache หมดอายุถาวร

> **Short-lived cache:** ถ้าใช้ `seconds` profile, `revalidate: 0`, หรือ `expire` ต่ำกว่า 5 นาที → cache จะถูก exclude จาก prerender และกลายเป็น dynamic hole

### 2. `cacheTag` — Tag ข้อมูลสำหรับ On-demand Invalidation

ใช้ tag กำกับ cached data เพื่อ invalidate ทีหลังได้:

```tsx
// app/lib/data.ts
import { cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheTag('products')
  return db.query('SELECT * FROM products')
}

export async function getProductById(id: string) {
  'use cache'
  cacheTag('products', `product-${id}`)
  return db.query('SELECT * FROM products WHERE id = ?', [id])
}
```

- ใส่ได้หลาย tags ต่อ function
- Tag เดียวกันใช้ในหลาย functions ได้ → invalidate ทีเดียวล้างหมด

### 3. `revalidateTag` — Stale-while-revalidate

Invalidate cache โดยยังเสิร์ฟ stale content ระหว่าง fresh content กำลังโหลด:

```tsx
// app/lib/actions.ts
'use server'

import { revalidateTag } from 'next/cache'

export async function updateProduct(id: string, formData: FormData) {
  await db.product.update({
    where: { id },
    data: { name: formData.get('name') as string },
  })

  revalidateTag('products', 'max') // stale-while-revalidate
}
```

**พฤติกรรม:**
1. Request แรกหลัง revalidate → ได้ stale content ทันที
2. Background: server สร้าง fresh content
3. Request ถัดไป → ได้ fresh content

**Argument ที่ 2 (stale window):**
- `'max'` — stale window นานที่สุด (แนะนำ)
- เมื่อ stale window หมด → request จะ block จนกว่า fresh content พร้อม

**เหมาะกับ:** Blog posts, product catalogs, content ที่ delay เล็กน้อยรับได้

### 4. `updateTag` — Immediate Expiration

Expire cache ทันที — user เห็นการเปลี่ยนแปลงของตัวเองทันที (read-your-own-writes):

```tsx
// app/lib/actions.ts
'use server'

import { updateTag } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const post = await db.post.create({
    data: {
      title: formData.get('title'),
      content: formData.get('content'),
    },
  })

  updateTag('posts')
  redirect(`/posts/${post.id}`)
}
```

**พฤติกรรม:**
- Cache ถูก expire ทันที
- Request ถัดไปจะได้ fresh content (ไม่มี stale)

**ข้อจำกัด:** ใช้ได้เฉพาะใน **Server Actions** เท่านั้น

### 5. `updateTag` vs `revalidateTag`

| | `updateTag` | `revalidateTag` |
|---|---|---|
| **ใช้ได้ใน** | Server Actions เท่านั้น | Server Actions + Route Handlers |
| **พฤติกรรม** | Expire cache ทันที | Stale-while-revalidate |
| **Use case** | User ต้องเห็นการเปลี่ยนแปลงทันที | Background refresh (delay เล็กน้อย OK) |
| **ตัวอย่าง** | สร้าง post → เห็น post ใหม่ทันที | อัปเดต catalog → ค่อยๆ refresh |

#### เลือกใช้อะไร?

```tsx
// User สร้าง post → ต้องเห็นทันที
export async function createPost(formData: FormData) {
  'use server'
  await db.post.create({ data: { title: formData.get('title') } })
  updateTag('posts') // ✅ ทันที
}

// Admin อัปเดต settings → delay เล็กน้อย OK
export async function updateSettings(formData: FormData) {
  'use server'
  await db.settings.update({ data: { theme: formData.get('theme') } })
  revalidateTag('settings', 'max') // ✅ stale-while-revalidate
}
```

### 6. `revalidatePath` — Invalidate ตาม Route Path

ใช้เมื่อไม่รู้ว่า route นั้นมี tags อะไรบ้าง:

```tsx
// app/lib/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function updateProfile(formData: FormData) {
  await db.user.update({
    where: { id: getCurrentUserId() },
    data: { name: formData.get('name') as string },
  })

  revalidatePath('/profile')
}
```

```tsx
// Revalidate หลาย paths
export async function updateUser(id: string) {
  await db.user.update({ where: { id }, data: { ... } })

  revalidatePath('/profile')
  revalidatePath('/dashboard')
  revalidatePath(`/users/${id}`)
}
```

> **แนะนำ:** ใช้ tag-based (`revalidateTag`/`updateTag`) มากกว่า path-based เมื่อทำได้ — แม่นยำกว่าและไม่ over-invalidate

### 7. แนวทางเลือกว่าควร Cache อะไร

**ควร Cache:**
- ข้อมูลที่ไม่ขึ้นกับ runtime data (cookies, headers)
- ข้อมูลที่ยอมรับได้ว่าจะ stale ชั่วคราว
- CMS content ที่มี update mechanism → ใช้ tags + cache นาน + revalidate เมื่อเปลี่ยน

**ไม่ควร Cache:**
- ข้อมูล personalized ต่อ user (ใช้ `<Suspense>` แทน)
- ข้อมูลที่ต้อง fresh ทุก request

```tsx
// ✅ Cache ได้ — ข้อมูลเหมือนกันทุกคน
export async function getPublicPosts() {
  'use cache'
  cacheLife('hours')
  cacheTag('posts')
  return db.post.findMany({ where: { published: true } })
}

// ❌ ไม่ควร cache — personalized
// ใช้ <Suspense> แทน
async function UserDashboard() {
  const session = await cookies()
  const userId = session.get('userId')?.value
  return db.user.findUnique({ where: { id: userId } })
}
```

> **Serverless:** In-memory cache อาจไม่ persist ข้าม revalidations ใน serverless environments — พิจารณาใช้ `'use cache: remote'`

## Complete Pattern

```tsx
// app/lib/data.ts — Data layer with caching
import { cacheLife, cacheTag } from 'next/cache'

export async function getPosts() {
  'use cache'
  cacheLife('hours')
  cacheTag('posts')
  return db.post.findMany({ orderBy: { createdAt: 'desc' } })
}

export async function getPost(slug: string) {
  'use cache'
  cacheLife('days')
  cacheTag('posts', `post-${slug}`)
  return db.post.findUnique({ where: { slug } })
}
```

```tsx
// app/lib/actions.ts — Mutations with revalidation
'use server'

import { updateTag, revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'

// User creates → sees immediately
export async function createPost(formData: FormData) {
  const post = await db.post.create({
    data: { title: formData.get('title') as string },
  })
  updateTag('posts')
  redirect(`/posts/${post.slug}`)
}

// Background update → slight delay OK
export async function refreshCatalog() {
  await syncFromCMS()
  revalidateTag('posts', 'max')
}
```

## Quick Reference

| API | ใช้ใน | พฤติกรรม | Use case |
|-----|--------|----------|----------|
| `cacheLife('hours')` | `"use cache"` scope | ตั้งเวลา cache | Time-based revalidation |
| `cacheTag('name')` | `"use cache"` scope | Tag สำหรับ invalidate | On-demand revalidation |
| `updateTag('name')` | Server Actions | Expire ทันที | Read-your-own-writes |
| `revalidateTag('name', 'max')` | Server Actions, Route Handlers | Stale-while-revalidate | Background refresh |
| `revalidatePath('/path')` | Server Actions, Route Handlers | Invalidate ทั้ง route | ไม่รู้ tags |

## สรุป

1. **Time-based:** `cacheLife()` กำหนดอายุ cache (seconds → max)
2. **Tag data:** `cacheTag()` กำกับ cache เพื่อ invalidate ทีหลัง
3. **User ต้องเห็นทันที:** `updateTag()` (Server Actions only)
4. **Background refresh OK:** `revalidateTag()` + stale window
5. **ไม่รู้ tags:** `revalidatePath()` (แต่ tag-based ดีกว่า)
6. **Cache เฉพาะข้อมูลที่ไม่ personalized** — personalized ใช้ `<Suspense>`
