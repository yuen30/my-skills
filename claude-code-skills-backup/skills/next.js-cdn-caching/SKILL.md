---
name: Next.js CDN Caching
description: Expert guidance on CDN caching with Next.js — Cache-Control headers, static assets, Vary headers, custom request headers, and pathname-based cache keying direction.
---

# Next.js CDN Caching

Expert guidance on CDN caching with Next.js — Cache-Control headers, static assets, Vary headers, custom request headers, and pathname-based cache keying direction.

@doc-version: 16.2.6

## Core Concepts

Next.js ตั้ง standard `Cache-Control` headers ที่ CDNs ใช้ cache responses ที่ edge ได้ แต่มีความท้าทายจาก custom headers ที่ทำให้ response vary ตาม request state

## Guidelines

### 1. Cache-Control Headers (What Works Today)

Next.js ตั้ง headers ตาม rendering strategy:

| Route Type | Cache-Control Header |
|-----------|---------------------|
| Static (no revalidation) | `s-maxage=31536000` (1 year) |
| ISR (time-based) | `s-maxage={revalidate}, stale-while-revalidate={expire - revalidate}` |
| Dynamic (no caching) | `private, no-cache, no-store, max-age=0, must-revalidate` |

**CDNs ที่รองรับ `s-maxage` + `stale-while-revalidate`** สามารถ cache static และ ISR pages ที่ edge ได้

#### On-demand Revalidation + CDN

CDN caching **ไม่รองรับ** on-demand revalidation (`revalidateTag`/`revalidatePath`) โดยตรง — CDN จะ serve cached copy จนกว่า TTL หมด

**Pattern แก้ไข:**
1. เรียก `revalidateTag()`/`revalidatePath()` → invalidate Next.js server cache
2. เรียก CDN purge API สำหรับ affected keys (ทั้ง HTML และ RSC variants)

```ts
'use server'

import { revalidateTag } from 'next/cache'

export async function updatePost() {
  await db.post.update({ ... })

  // 1. Invalidate Next.js cache
  revalidateTag('posts')

  // 2. Purge CDN cache
  await fetch('https://cdn.example.com/purge', {
    method: 'POST',
    body: JSON.stringify({ tags: ['posts'] }),
    headers: { Authorization: `Bearer ${process.env.CDN_PURGE_TOKEN}` },
  })
}
```

### 2. Static Assets

Assets จาก `/_next/static/` มี content hashes ใน filename:

```
Cache-Control: public, max-age=31536000, immutable
```

- JavaScript, CSS, images, fonts
- Content hash = cache forever safely
- ใช้ `assetPrefix` สำหรับ serve จาก CDN domain อื่น:

```ts
// next.config.ts
const nextConfig = {
  assetPrefix: 'https://cdn.example.com',
}
```

### 3. Static Prefetches (PPR-enabled Routes)

เมื่อ route มี PPR enabled + `next-router-prefetch` header:
- Response เป็น deterministic (เหมือนกันทุก request)
- CDN cache ได้ถ้า:
  1. Include `_rsc` search parameter ใน cache key
  2. Respect `Cache-Control` headers

### 4. Where CDN Caching Is Challenging

App Router responses vary ตาม custom request headers:

| Header | Purpose | Impact |
|--------|---------|--------|
| `rsc` | Return RSC payload แทน HTML | **ต้อง preserve** |
| `next-router-state-tree` | Client router state สำหรับ targeted updates | ทำให้ cache vary สูง |
| `next-router-prefetch` | Prefetch request | **ต้อง preserve** |
| `next-router-segment-prefetch` | Specific segment prefetch | Optional |
| `next-url` | Interception routes URL | เฉพาะ interception routes |

Next.js ตั้ง `Vary` header เพื่อบอก CDN แต่หลาย CDNs ไม่รองรับ `Vary` ดี

#### `_rsc` Search Parameter

Next.js แก้ปัญหาด้วย `_rsc` parameter — hash ของ relevant request headers ที่ทำหน้าที่เป็น cache key:

```
/blog/hello?_rsc=abc123  → RSC response
/blog/hello              → HTML response
```

ทำให้ CDNs ที่ ignore `Vary` ยังทำงานถูกต้อง

### 5. Handling Headers at CDN

#### ต้อง Preserve (Critical)

| Header/Param | ทำไม |
|-------------|------|
| `rsc` header | บอก server ให้ return RSC payload — ถ้าหาย = client navigation พัง |
| `_rsc` search param | แยก response variants — ต้องอยู่ใน cache key |
| `next-router-prefetch` + `_rsc` | Required สำหรับ prefetch flows |

#### Safe to Ignore (Graceful Degradation)

| Header | ผลเมื่อหาย |
|--------|-----------|
| `next-router-state-tree` | Server return full payload แทน targeted update (ใหญ่กว่า) |
| `next-router-segment-prefetch` | Fallback เป็น broader prefetch |
| `next-url` | Interception routes ไม่ทำงาน — degrade เป็น regular navigation |

### 6. Proxy (Middleware) กับ CDN

`proxy.ts` ควรรัน **ก่อน** CDN cache:

```
Client → Proxy (auth, redirects) → CDN Cache → Origin Server
```

ถ้า deployment วาง proxy หลัง CDN:
- Configure CDN ให้ bypass cache สำหรับ routes ที่ขึ้นกับ proxy decisions
- หรือใช้ edge function ที่ CDN level

### 7. Direction: Pathname-Based Cache Keying (อนาคต)

Next.js team กำลังย้าย cache-affecting inputs เข้าไปใน URL pathname:

```
/my/page.rsc                              → Full page RSC payload
/my/page.segments/path/to/segment.segment.rsc → Segment RSC payload
```

**ข้อดี:**
- Pathname = cache key (ไม่ต้อง Vary)
- Search params drop ได้ safely
- Standard HTTP cache headers เพียงพอ
- ไม่ต้อง CDN edge logic พิเศษ

**สถานะ:** Active design — patterns บางส่วนใช้แล้วใน segment prefetches และ `output: 'export'`

### 8. CDN Configuration Checklist

```
CDN Setup for Next.js:
□ Preserve _rsc search parameter ใน cache key
□ Forward rsc header ไป origin
□ Forward next-router-prefetch header ไป origin
□ อย่า strip query parameters จาก cache keys
□ Respect Cache-Control headers (s-maxage, stale-while-revalidate)
□ วาง proxy.ts ก่อน CDN cache layer
□ Setup CDN purge API สำหรับ on-demand revalidation
□ ใช้ assetPrefix สำหรับ static assets ถ้าต้องการ separate CDN
```

## Quick Reference

| Content | Cache-Control | CDN Cacheable? |
|---------|--------------|:-:|
| Static pages | `s-maxage=31536000` | ✅ |
| ISR pages | `s-maxage=N, stale-while-revalidate=M` | ✅ |
| Dynamic pages | `private, no-cache, no-store` | ❌ |
| Static assets (`/_next/static/`) | `public, max-age=31536000, immutable` | ✅ |
| PPR static prefetch | Varies (with `_rsc` param) | ✅ (ถ้า preserve `_rsc`) |

## สรุป

1. **Static + ISR pages** — CDN cache ได้ผ่าน `s-maxage` + `stale-while-revalidate`
2. **On-demand revalidation** — ต้อง purge CDN เพิ่มเติมจาก `revalidateTag`
3. **`_rsc` parameter** — ต้องอยู่ใน cache key (แยก HTML vs RSC)
4. **`rsc` header** — ต้อง forward ไป origin (ห้าม strip)
5. **Static assets** — immutable, cache forever, ใช้ `assetPrefix` สำหรับ CDN domain
6. **Proxy ก่อน CDN** — ให้ auth/redirects ทำงานก่อน cache
7. **อนาคต** — pathname-based keying จะทำให้ CDN caching ง่ายขึ้นมาก
