---
name: Next.js Navigation and Prefetching
description: Expert guidance on Next.js navigation mechanics including prefetching, streaming, client-side transitions, optimization techniques, automatic/manual/hover-triggered prefetch, and fast page transitions.
---

# Next.js Navigation and Prefetching

Expert guidance on Next.js navigation mechanics including prefetching, streaming, client-side transitions, and optimization techniques for fast page transitions.

@doc-version: 16.2.6

## Core Concepts

Next.js ทำให้การเปลี่ยนหน้ารวดเร็วและลื่นไหลเหมือน SPA แม้จะเป็น Server Rendering ผ่าน 4 กลไกหลัก:

1. **Server Rendering** — เรนเดอร์ HTML ที่เซิร์ฟเวอร์ก่อนส่งมาเบราว์เซอร์
2. **Prefetching** — โหลดข้อมูลหน้าปลายทางล่วงหน้าใน background
3. **Streaming** — ส่ง UI บางส่วนมาแสดงก่อน (Header, Skeleton) ขณะรอข้อมูลที่เหลือ
4. **Client-side Transitions** — อัปเดตเฉพาะส่วนที่เปลี่ยน ไม่รีโหลดทั้งหน้า

## Guidelines

### 1. การใช้ `<Link>` Component

ใช้ `<Link>` จาก `next/link` แทน `<a>` เสมอ:

```tsx
import Link from 'next/link'

export function Navigation() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href={`/blog/${post.slug}`}>{post.title}</Link>
    </nav>
  )
}
```

**สิ่งที่ `<Link>` ทำให้อัตโนมัติ:**
- Prefetch หน้าปลายทางเมื่อ Link ปรากฏใน viewport
- Client-side navigation (ไม่รีโหลดทั้งหน้า)
- รักษา state ของ layout ที่ใช้ร่วมกัน
- อัปเดตเฉพาะ segment ที่เปลี่ยนแปลง

### 2. Prefetching (การโหลดล่วงหน้า)

Prefetching เกิดขึ้นอัตโนมัติเมื่อ `<Link>` ปรากฏใน viewport:

```tsx
// ✅ Prefetch อัตโนมัติ (default)
<Link href="/dashboard">Dashboard</Link>

// ❌ ปิด Prefetch (เหมาะสำหรับรายการลิงก์ยาวๆ)
<Link href="/dashboard" prefetch={false}>Dashboard</Link>
```

**Prefetch เมื่อ Hover (ประหยัดทรัพยากร):**

```tsx
'use client'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export function HoverPrefetchLink({ href, children }: { href: string; children: React.ReactNode }) {
  const router = useRouter()

  return (
    <Link
      href={href}
      prefetch={false}
      onMouseEnter={() => router.prefetch(href)}
    >
      {children}
    </Link>
  )
}
```

**หมายเหตุ:** `<Link>` เป็น Client Component — ต้องรอ Hydration (JavaScript โหลดเสร็จ) ก่อนถึงจะเริ่ม Prefetch ได้ ควรลดขนาด Bundle size เพื่อให้ Hydration เร็วขึ้น

### 3. Streaming กับ `loading.tsx`

สำหรับ Dynamic Routes ที่ต้องดึงข้อมูลใหม่เสมอ ใช้ `loading.tsx` เป็น Loading Skeleton:

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/3 mb-4" />
      <div className="h-4 bg-gray-200 rounded w-full mb-2" />
      <div className="h-4 bg-gray-200 rounded w-2/3" />
    </div>
  )
}
```

**ทำไมต้องมี `loading.tsx`:**
- ถูก Prefetch มารอไว้ก่อน → ผู้ใช้เห็น skeleton ทันทีที่คลิก
- ไม่ต้องรอ server response ก่อนแสดงผล
- ให้ feedback ว่าระบบกำลังทำงาน

### 4. Client-side Transitions

เมื่อเปลี่ยนหน้า Next.js จะ:
- อัปเดตเฉพาะ route segment ที่เปลี่ยน
- ไม่ล้าง state ของ layout ที่ใช้ร่วมกัน
- ไม่รีโหลด HTML ทั้งหน้า
- ไม่ re-render component ที่ไม่เปลี่ยนแปลง

```
เปลี่ยนจาก /dashboard/analytics → /dashboard/settings

Root Layout      → ไม่ re-render ✓
Dashboard Layout → ไม่ re-render ✓ (state คงเดิม)
Page Content     → re-render เฉพาะส่วนนี้
```

### 5. Programmatic Navigation (`useRouter`)

```tsx
'use client'
import { useRouter } from 'next/navigation'

export function NavigationActions() {
  const router = useRouter()

  return (
    <div>
      {/* เปลี่ยนหน้า */}
      <button onClick={() => router.push('/dashboard')}>Go to Dashboard</button>

      {/* แทนที่ history entry (กดย้อนกลับไม่ได้) */}
      <button onClick={() => router.replace('/login')}>Login</button>

      {/* ย้อนกลับ */}
      <button onClick={() => router.back()}>Back</button>

      {/* Prefetch ล่วงหน้า */}
      <button onMouseEnter={() => router.prefetch('/heavy-page')}>
        Hover to prefetch
      </button>
    </div>
  )
}
```

### 6. `useLinkStatus` — แสดงสถานะการโหลด

สำหรับเครือข่ายช้าที่ Prefetch ไม่ทัน ใช้ `useLinkStatus` แสดง loading indicator:

```tsx
'use client'
import Link from 'next/link'
import { useLinkStatus } from 'next/link'

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link href={href}>
      <LinkContent>{children}</LinkContent>
    </Link>
  )
}

function LinkContent({ children }: { children: React.ReactNode }) {
  const { pending } = useLinkStatus()

  return (
    <span>
      {children}
      {pending && <span className="ml-2 animate-spin">⏳</span>}
    </span>
  )
}
```

**Use cases:**
- แถบโหลดด้านบน (progress bar)
- Spinner ข้างลิงก์ที่กดไป
- Disable ปุ่มขณะรอ

### 7. `generateStaticParams` — Static Generation สำหรับ Dynamic Routes

หากรู้รายการหน้าทั้งหมดล่วงหน้า ใช้ `generateStaticParams` เพื่อ pre-render ตอน build:

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getAllPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

export default async function BlogPost({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)
  return <article>{post.content}</article>
}
```

**ผลลัพธ์:** หน้าเหล่านี้จะถูก generate เป็น static HTML ตอน build → Prefetch ได้เร็วมาก → เปลี่ยนหน้าแทบจะทันที

### 8. Native History API

จัดการ URL โดยไม่รีโหลดหน้า:

#### `pushState` — เพิ่ม history entry (กดย้อนกลับได้)

```tsx
'use client'
import { useSearchParams } from 'next/navigation'

export function SortSelector() {
  const searchParams = useSearchParams()

  function handleSort(sort: string) {
    const params = new URLSearchParams(searchParams.toString())
    params.set('sort', sort)
    window.history.pushState(null, '', `?${params.toString()}`)
  }

  return (
    <select onChange={(e) => handleSort(e.target.value)}>
      <option value="newest">Newest</option>
      <option value="price">Price</option>
    </select>
  )
}
```

#### `replaceState` — แทนที่ history entry (กดย้อนกลับไม่ได้)

```tsx
'use client'

export function LocaleSwitcher() {
  function changeLocale(locale: string) {
    window.history.replaceState(null, '', `/${locale}`)
  }

  return (
    <div>
      <button onClick={() => changeLocale('th')}>🇹🇭 ไทย</button>
      <button onClick={() => changeLocale('en')}>🇺🇸 English</button>
    </div>
  )
}
```

## Optimization Checklist

| เทคนิค | เมื่อไหร่ใช้ | ผลลัพธ์ |
|--------|-------------|---------|
| `<Link>` (default prefetch) | ทุกลิงก์ภายในแอป | เปลี่ยนหน้าทันที |
| `prefetch={false}` | รายการลิงก์ยาวๆ | ประหยัด bandwidth |
| Prefetch on hover | สมดุลระหว่างเร็วกับประหยัด | โหลดเฉพาะที่สนใจ |
| `loading.tsx` | Dynamic routes ทุกหน้า | เห็น skeleton ทันที |
| `generateStaticParams` | หน้าที่รู้ล่วงหน้าได้ | Static = เร็วสุด |
| `useLinkStatus` | เน็ตช้า / หน้าหนัก | แสดง loading feedback |
| ลด Bundle size | ทุกโปรเจกต์ | Hydration เร็ว → Prefetch เร็ว |

## สรุป

หัวใจของการทำให้ Next.js นำทางได้เร็ว:
1. ใช้ `<Link>` เสมอ → ได้ Prefetching + Client-side Transition
2. สร้าง `loading.tsx` → ได้ Streaming + Instant feedback
3. ใช้ `generateStaticParams` เมื่อทำได้ → Static = เร็วที่สุด
4. ใช้ `useLinkStatus` → รองรับเน็ตช้า
5. ลด Bundle size → Hydration เร็ว → ทุกอย่างเร็วตาม
