---
name: Next.js Draft Mode
description: Expert guidance on using Draft Mode in Next.js to preview draft content from headless CMS — enable/disable, secure access, and Cache Components integration.
---

# Next.js Draft Mode

Expert guidance on using Draft Mode in Next.js to preview draft content from headless CMS — enable/disable, secure access, and Cache Components integration.

@doc-version: 16.2.6

## Core Concepts

Draft Mode ให้คุณ preview draft content จาก headless CMS โดยไม่ต้อง rebuild ทั้ง site:
- Static pages สลับไป dynamic rendering
- เห็น draft changes ทันที
- ทำงานผ่าน cookie (`__prerender_bypass`)

## Guidelines

### 1. Create Route Handler (Enable Draft Mode)

```ts
// app/api/draft/route.ts
import { draftMode } from 'next/headers'
import { redirect } from 'next/navigation'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const secret = searchParams.get('secret')
  const slug = searchParams.get('slug')

  // ตรวจสอบ secret token
  if (secret !== process.env.DRAFT_SECRET_TOKEN || !slug) {
    return new Response('Invalid token', { status: 401 })
  }

  // ตรวจสอบว่า slug มีอยู่จริง
  const post = await getPostBySlug(slug)
  if (!post) {
    return new Response('Invalid slug', { status: 401 })
  }

  // Enable Draft Mode (set cookie)
  const draft = await draftMode()
  draft.enable()

  // Redirect ไปหน้าที่ต้องการ preview
  // ใช้ post.slug แทน searchParams.slug เพื่อป้องกัน open redirect
  redirect(post.slug)
}
```

### 2. Disable Draft Mode

```ts
// app/api/disable-draft/route.ts
import { draftMode } from 'next/headers'

export async function GET() {
  const draft = await draftMode()
  draft.disable()
  return new Response('Draft mode is disabled')
}
```

### 3. Preview Draft Content in Pages

```tsx
// app/posts/[slug]/page.tsx
import { draftMode } from 'next/headers'

async function getData(slug: string) {
  const { isEnabled } = await draftMode()

  // Fetch draft หรือ published content ตาม mode
  const url = isEnabled
    ? `https://cms.example.com/api/draft/${slug}`
    : `https://cms.example.com/api/published/${slug}`

  const res = await fetch(url)
  return res.json()
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const { title, content } = await getData(slug)

  return (
    <article>
      <h1>{title}</h1>
      <div>{content}</div>
    </article>
  )
}
```

### 4. Headless CMS Integration

#### Setup Draft URL ใน CMS

```
https://your-site.com/api/draft?secret=MY_SECRET_TOKEN&slug=/posts/{entry.fields.slug}
```

#### Flow

```
1. Editor คลิก "Preview" ใน CMS
2. CMS redirect ไป /api/draft?secret=xxx&slug=/posts/hello
3. Route Handler ตรวจสอบ secret + slug
4. Enable draft mode (set cookie)
5. Redirect ไป /posts/hello
6. Page render ด้วย draft content (dynamic rendering)
```

### 5. Draft Mode with Cache Components

เมื่อใช้ `"use cache"` + Draft Mode enabled:
- ทุก cached functions/components **re-execute ทุก request**
- Results **ไม่ถูก save** ไป cache (ไม่ pollute cached content)
- `fetch()` ใช้ original implementation (ไม่ผ่าน Next.js fetch cache)
- Response headers: `private, no-cache, no-store, max-age=0, must-revalidate`

```tsx
// app/post/[slug]/page.tsx
import { draftMode } from 'next/headers'

async function Post({ slug }: { slug: string }) {
  'use cache'

  const { isEnabled } = await draftMode()

  // Fetch draft หรือ published ตาม mode
  const post = isEnabled
    ? await fetchDraftPost(slug)
    : await fetchPublishedPost(slug)

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
    </article>
  )
}
```

**กฎใน Cache Components:**
- ✅ `draftMode()` — อ่าน `isEnabled` ได้
- ❌ `cookies()`, `headers()` — ไม่อนุญาต (ยกเว้น `"use cache: private"`)
- ❌ `draftMode().enable()` / `.disable()` — ทำได้เฉพาะใน Route Handlers / Server Actions

### 6. Security Best Practices

```ts
// app/api/draft/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const secret = searchParams.get('secret')
  const slug = searchParams.get('slug')

  // 1. ตรวจสอบ secret (ใช้ env variable)
  if (secret !== process.env.DRAFT_SECRET_TOKEN) {
    return new Response('Invalid token', { status: 401 })
  }

  // 2. ตรวจสอบว่า slug มีอยู่จริง
  if (!slug) {
    return new Response('Missing slug', { status: 400 })
  }

  const post = await getPostBySlug(slug)
  if (!post) {
    return new Response('Invalid slug', { status: 401 })
  }

  // 3. Enable draft mode
  const draft = await draftMode()
  draft.enable()

  // 4. Redirect ไป post.slug (ไม่ใช่ searchParams.slug)
  // ป้องกัน open redirect vulnerability
  redirect(post.slug)
}
```

**สำคัญ:**
- Secret token ต้องรู้เฉพาะ Next.js app + CMS
- ตรวจสอบว่า slug มีอยู่จริงก่อน enable
- Redirect ไป validated path เท่านั้น (ป้องกัน open redirect)

### 7. Draft Mode Indicator (Optional)

แสดง banner เมื่ออยู่ใน draft mode:

```tsx
// app/layout.tsx
import { draftMode } from 'next/headers'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const { isEnabled } = await draftMode()

  return (
    <html lang="en">
      <body>
        {isEnabled && (
          <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-black text-center py-1 z-50">
            Draft Mode — <a href="/api/disable-draft" className="underline">Exit</a>
          </div>
        )}
        {children}
      </body>
    </html>
  )
}
```

## How It Works

```
Normal (Production):
┌──────────────┐
│ Static Page  │ → Served from cache (fast)
│ (build time) │
└──────────────┘

Draft Mode Enabled:
┌──────────────┐
│ Dynamic Page │ → Rendered per-request (fresh draft content)
│ (request)    │
└──────────────┘

Cookie: __prerender_bypass = encrypted_value
```

## Quick Reference

| API | Purpose |
|-----|---------|
| `draftMode().enable()` | Enable draft mode (set cookie) |
| `draftMode().disable()` | Disable draft mode (delete cookie) |
| `draftMode().isEnabled` | Check if draft mode is active |

| Where | enable/disable | isEnabled |
|-------|:-:|:-:|
| Route Handler | ✅ | ✅ |
| Server Action | ✅ | ✅ |
| Server Component | ❌ | ✅ |
| `"use cache"` scope | ❌ | ✅ |

## สรุป

1. **สร้าง Route Handler** — enable draft mode ด้วย secret token
2. **ตรวจสอบ security** — secret + slug validation + ป้องกัน open redirect
3. **ใช้ `isEnabled`** ใน pages — fetch draft vs published content
4. **Cache Components** — draft mode bypass cache อัตโนมัติ
5. **CMS integration** — ตั้ง draft URL ใน CMS settings
6. **Disable** — สร้าง route สำหรับ exit draft mode
