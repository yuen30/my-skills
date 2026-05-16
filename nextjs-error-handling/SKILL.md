---
name: Next.js Error Handling
description: Expert guidance on handling expected errors and uncaught exceptions in Next.js App Router using error boundaries, notFound, useActionState, and catchError.
---

# Next.js Error Handling

Expert guidance on handling expected errors and uncaught exceptions in Next.js App Router using error boundaries, notFound, useActionState, and catchError.

@doc-version: 16.2.6

## Core Concepts

Errors แบ่งเป็น 2 ประเภท:
- **Expected errors** — เกิดขึ้นได้ปกติ (validation fail, request fail) → จัดการด้วย return values
- **Uncaught exceptions** — bugs ที่ไม่คาดคิด → จัดการด้วย error boundaries

## Guidelines

### 1. Expected Errors — Server Functions

ใช้ `useActionState` จัดการ error จาก Server Actions — **อย่าใช้ try/catch + throw** แต่ให้ return error เป็น value:

```tsx
// app/actions.ts
'use server'

export async function createPost(prevState: any, formData: FormData) {
  const title = formData.get('title')
  const content = formData.get('content')

  const res = await fetch('https://api.vercel.app/posts', {
    method: 'POST',
    body: JSON.stringify({ title, content }),
  })

  if (!res.ok) {
    return { message: 'Failed to create post' }
  }

  const json = await res.json()
  return { message: '', data: json }
}
```

```tsx
// app/ui/form.tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

const initialState = { message: '' }

export function Form() {
  const [state, formAction, pending] = useActionState(createPost, initialState)

  return (
    <form action={formAction}>
      <label htmlFor="title">Title</label>
      <input type="text" id="title" name="title" required />

      <label htmlFor="content">Content</label>
      <textarea id="content" name="content" required />

      {state?.message && <p aria-live="polite">{state.message}</p>}

      <button disabled={pending}>Create Post</button>
    </form>
  )
}
```

**หลักการ:** Expected errors = return values, ไม่ใช่ thrown errors

### 2. Expected Errors — Server Components

ใช้ response เพื่อ conditionally render error message หรือ redirect:

```tsx
// app/page.tsx
export default async function Page() {
  const res = await fetch('https://api.example.com/data')
  const data = await res.json()

  if (!res.ok) {
    return <p>There was an error loading data.</p>
  }

  return <div>{data.title}</div>
}
```

### 3. Not Found (404)

ใช้ `notFound()` function + `not-found.tsx` file:

```tsx
// app/blog/[slug]/page.tsx
import { notFound } from 'next/navigation'
import { getPostBySlug } from '@/lib/posts'

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = getPostBySlug(slug)

  if (!post) {
    notFound()
  }

  return <div>{post.title}</div>
}
```

```tsx
// app/blog/[slug]/not-found.tsx
export default function NotFound() {
  return <div>404 - Page Not Found</div>
}
```

- `notFound()` จะ throw ไปหา `not-found.tsx` ที่ใกล้ที่สุด
- ถ้าไม่มี `not-found.tsx` ในโฟลเดอร์นั้น จะ bubble up ไปหาตัวบน

### 4. Uncaught Exceptions — Error Boundaries (`error.tsx`)

สร้าง `error.tsx` ในโฟลเดอร์ route เพื่อจับ uncaught errors:

```tsx
// app/dashboard/error.tsx
'use client' // Error boundaries ต้องเป็น Client Components

import { useEffect } from 'react'

export default function ErrorPage({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string }
  unstable_retry: () => void
}) {
  useEffect(() => {
    // Log error ไปยัง error reporting service
    console.error(error)
  }, [error])

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => unstable_retry()}>
        Try again
      </button>
    </div>
  )
}
```

**พฤติกรรม:**
- Errors bubble up ไปหา error boundary ที่ใกล้ที่สุด
- วาง `error.tsx` ในระดับต่างๆ ของ route hierarchy เพื่อ granular error handling
- `unstable_retry()` จะ re-fetch และ re-render segment นั้น

```
app/
├── error.tsx              # จับ error ทั้งแอป (ยกเว้น root layout)
├── layout.tsx
├── page.tsx
└── dashboard/
    ├── error.tsx          # จับ error เฉพาะ dashboard
    ├── page.tsx
    └── settings/
        ├── error.tsx      # จับ error เฉพาะ settings
        └── page.tsx
```

### 5. Component-level Error Boundaries (`unstable_catchError`)

สร้าง error boundary ที่หุ้มส่วนใดก็ได้ของ component tree:

```tsx
// app/custom-error-boundary.tsx
'use client'

import { unstable_catchError as catchError, type ErrorInfo } from 'next/error'

function ErrorFallback(
  props: { title: string },
  { error, unstable_retry }: ErrorInfo
) {
  return (
    <div>
      <h2>{props.title}</h2>
      <p>{error.message}</p>
      <button onClick={() => unstable_retry()}>Try again</button>
    </div>
  )
}

export default catchError(ErrorFallback)
```

ใช้งาน:

```tsx
// app/dashboard/page.tsx
import ErrorBoundary from './custom-error-boundary'

export default function DashboardPage({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <h1>Dashboard</h1>
      <ErrorBoundary title="Stats Error">
        <StatsWidget />
      </ErrorBoundary>
      <ErrorBoundary title="Chart Error">
        <RevenueChart />
      </ErrorBoundary>
    </div>
  )
}
```

### 6. Event Handler Errors

Error boundaries จับ errors ตอน **rendering** เท่านั้น — ไม่จับ errors ใน event handlers

จัดการด้วย `useState`:

```tsx
'use client'

import { useState } from 'react'

export function DeleteButton({ id }: { id: string }) {
  const [error, setError] = useState<string | null>(null)

  const handleClick = async () => {
    try {
      await deleteItem(id)
    } catch (e) {
      setError('Failed to delete item')
    }
  }

  if (error) {
    return <p className="text-red-500">{error}</p>
  }

  return <button onClick={handleClick}>Delete</button>
}
```

**ข้อยกเว้น:** errors ใน `startTransition` จาก `useTransition` จะ bubble up ไปหา error boundary:

```tsx
'use client'

import { useTransition } from 'react'

export function Button() {
  const [pending, startTransition] = useTransition()

  const handleClick = () =>
    startTransition(() => {
      throw new Error('Exception') // → bubble up ไป error boundary
    })

  return <button onClick={handleClick}>Click me</button>
}
```

### 7. Global Errors (`global-error.tsx`)

จับ errors ใน root layout — ต้องมี `<html>` และ `<body>` เอง:

```tsx
// app/global-error.tsx
'use client'

export default function GlobalError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string }
  unstable_retry: () => void
}) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={() => unstable_retry()}>Try again</button>
      </body>
    </html>
  )
}
```

> `global-error.tsx` แทนที่ root layout เมื่อ active — จึงต้อง define `<html>` + `<body>` เอง

## Error Handling Decision Tree

```
Error เกิดขึ้น
├── Expected? (validation, API fail, not found)
│   ├── Form validation → return error state + useActionState
│   ├── API fail → conditional render / redirect
│   └── Not found → notFound() + not-found.tsx
│
└── Unexpected? (bugs, crashes)
    ├── During rendering → error.tsx (error boundary)
    ├── In event handler → try/catch + useState
    ├── In startTransition → bubble up to error boundary
    └── In root layout → global-error.tsx
```

## Quick Reference

| สถานการณ์ | วิธีจัดการ | ไฟล์/API |
|-----------|-----------|----------|
| Form validation fail | Return error state | `useActionState` |
| API response error | Conditional render | `if (!res.ok)` |
| Resource not found | `notFound()` | `not-found.tsx` |
| Rendering crash | Error boundary | `error.tsx` |
| Component-level error | `catchError` wrapper | `unstable_catchError` |
| Event handler error | `try/catch` + `useState` | Manual handling |
| Root layout crash | Global error | `global-error.tsx` |
| Retry after error | `unstable_retry()` | Re-fetch + re-render |

## สรุป

1. **Expected errors = return values** — ไม่ throw, ใช้ `useActionState` แสดง error
2. **Not found = `notFound()`** — trigger `not-found.tsx`
3. **Uncaught exceptions = `error.tsx`** — error boundary จับ rendering errors
4. **Granular control = `unstable_catchError`** — หุ้มส่วนใดก็ได้
5. **Event handlers = manual try/catch** — error boundary ไม่จับ
6. **Global fallback = `global-error.tsx`** — ต้องมี `<html>` + `<body>`
7. **Recovery = `unstable_retry()`** — re-fetch และ re-render segment
