---
name: Next.js Preserving UI State
description: Expert guidance on how React Activity preserves UI state across navigations in Next.js — dropdowns, forms, dialogs, auth, global styles, and testing.
---

# Next.js Preserving UI State

Expert guidance on how React Activity preserves UI state across navigations in Next.js — dropdowns, forms, dialogs, auth, global styles, and testing.

@doc-version: 16.2.6

## Core Concepts

เมื่อเปิด `cacheComponents: true` — Next.js ใช้ React `<Activity>` component:
- Pages ไม่ถูก unmount เมื่อ navigate ออก — ถูก hide ด้วย `display: none`
- **State ทั้งหมด persist:** `useState`, form inputs, scroll position, `<details>` expanded, video playback
- เก็บสูงสุด 3 routes — เกินนั้น oldest ถูก evict
- Effects cleanup รันเมื่อ hide, re-run เมื่อ visible

## Guidelines

### 1. Expandable UI (Dropdowns, Accordions)

**Keep:** Sidebar sections, FAQ accordion, filter panels (user set up intentionally)

**Reset:** Dropdown menus, popovers (transient interactions)

```tsx
'use client'

import { useState, useLayoutEffect } from 'react'

function SettingsDropdown() {
  const [isOpen, setIsOpen] = useState(false)

  // Close เมื่อ component ถูก hide (Activity hidden)
  useLayoutEffect(() => {
    return () => {
      setIsOpen(false)
    }
  }, [])

  return (
    <div>
      <button onClick={() => setIsOpen((o) => !o)}>Options</button>
      {isOpen && (
        <ul>
          <li><button>Edit Profile</button></li>
          <li><button>Change Password</button></li>
        </ul>
      )}
    </div>
  )
}
```

> `useLayoutEffect` cleanup รัน synchronously ก่อน hide — ไม่มี flash

### 2. Dialogs and Initialization Logic

**Problem:** Dialog open state persist → `isDialogOpen` ยังเป็น `true` เมื่อกลับมา → Effect ไม่ re-fire (ค่าไม่เปลี่ยน)

**Solution:** Derive dialog state จาก URL:

```tsx
'use client'

import { useSearchParams, useRouter } from 'next/navigation'
import { useEffect, useRef } from 'react'

function ProductTab() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const isDialogOpen = searchParams.get('edit') === 'true'
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isDialogOpen) {
      inputRef.current?.focus()
    }
  }, [isDialogOpen])

  return (
    <div>
      <button onClick={() => router.push('?edit=true')}>Edit Product</button>
      {isDialogOpen && (
        <dialog open>
          <input ref={inputRef} placeholder="Product name" />
          <button onClick={() => router.replace('?', { scroll: false })}>
            Close
          </button>
        </dialog>
      )}
    </div>
  )
}
```

### 3. Forms — Reset After Submit

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function NewItemPage() {
  const [name, setName] = useState('')
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const item = await createItem({ name })
    setName('') // Reset ก่อน navigate
    router.push(`/items/${item.id}`)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <button type="submit">Create</button>
    </form>
  )
}
```

### 4. Forms — Reset Stale Status Messages

```tsx
'use client'

import { useState, useRef, useLayoutEffect } from 'react'

function ContactForm() {
  const [name, setName] = useState('')
  const [status, setStatus] = useState<'idle' | 'success'>('idle')
  const shouldReset = useRef(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await sendMessage({ name })
    setStatus('success')
    shouldReset.current = true
  }

  // Reset stale success message เมื่อ Activity hides
  useLayoutEffect(() => {
    return () => {
      if (shouldReset.current) {
        shouldReset.current = false
        setStatus('idle')
        setName('')
      }
    }
  }, [])

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <button type="submit">Send</button>
      {status === 'success' && <p>Message sent!</p>}
    </form>
  )
}
```

> `shouldReset` ref ทำให้ cleanup รันเฉพาะหลัง submit — ไม่ reset draft ที่ยังไม่ submit

### 5. Reset All Form Fields (Callback Ref)

```tsx
<form
  ref={(form) => {
    return () => form?.reset() // Reset ทุก fields เมื่อ navigate ออก
  }}
>
  <input name="email" />
  <input name="message" />
  <button type="submit">Send</button>
</form>
```

### 6. State and Authentication

State persist ข้าม auth changes — draft ของ user A ไม่ควรเห็นโดย user B:

```tsx
'use client'

import { useState, useEffect, useRef } from 'react'

function UserScopedForm({ userId }: { userId: string | null }) {
  const [draft, setDraft] = useState('')
  const lastUserIdRef = useRef<string | null>(null)

  useEffect(() => {
    if (lastUserIdRef.current !== null && lastUserIdRef.current !== userId) {
      setDraft('') // Reset เมื่อ user เปลี่ยน
    }
    lastUserIdRef.current = userId
  }, [userId])

  return <textarea value={draft} onChange={(e) => setDraft(e.target.value)} />
}
```

**Alternative:** Key by user ID → `<Form key={userId} />`

**Logout:** ใช้ `window.location.href` แทน `router.push` → full reload clears all state

### 7. Global Styles — Disable When Hidden

```tsx
<style
  ref={(style) => {
    if (style) style.media = '' // Enable when visible
    return () => {
      if (style) style.media = 'not all' // Disable when hidden
    }
  }}
>
  {`:root { --page-accent: blue; }`}
</style>
```

### 8. Media Playback — Pause When Hidden

```tsx
'use client'

import { useLayoutEffect, useRef } from 'react'

function VideoPlayer({ src }: { src: string }) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useLayoutEffect(() => {
    const video = videoRef.current
    return () => {
      video?.pause() // Pause เมื่อ hidden, preserve position
    }
  }, [])

  return <video ref={videoRef} src={src} controls />
}
```

### 9. Distinguish First Mount vs Re-show

```tsx
'use client'

import { useEffect, useRef } from 'react'

function TrackedComponent() {
  const hasMountedRef = useRef(false)

  useEffect(() => {
    if (!hasMountedRef.current) {
      hasMountedRef.current = true
      console.log('First mount')
    } else {
      console.log('Became visible again')
    }
  }, [])

  return <div>...</div>
}
```

### 10. Using `<Activity>` in Components

Prerender hidden content at lower priority:

```tsx
'use client'

import { Activity, Suspense, useState, use } from 'react'

export function ExpandableComments({
  commentsPromise,
}: {
  commentsPromise: Promise<Comment[]>
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <>
      <button onClick={() => setExpanded((e) => !e)}>
        {expanded ? 'Hide' : 'Show'} Comments
      </button>
      <Activity mode={expanded ? 'visible' : 'hidden'}>
        <Suspense fallback={<div>Loading...</div>}>
          <Comments commentsPromise={commentsPromise} />
        </Suspense>
      </Activity>
    </>
  )
}

function Comments({ commentsPromise }: { commentsPromise: Promise<Comment[]> }) {
  const comments = use(commentsPromise)
  return <ul>{comments.map((c) => <li key={c.id}>{c.text}</li>)}</ul>
}
```

### 11. Testing with Activity

Hidden content has `display: none` but remains in DOM:

```ts
// ✅ Good — getByRole filters by visibility automatically
await page.getByRole('button', { name: 'Submit' }).click()
await page.getByRole('textbox', { name: 'Email' }).fill('test@example.com')

// ✅ Good — explicit visibility filter
await page.locator('.product-card').filter({ visible: true }).first().click()

// ❌ Avoid — may match hidden elements
await page.locator('.product-card').first().click()
```

## Decision Guide

| State Type | Keep? | Reset How? |
|-----------|:---:|---|
| Sidebar expanded sections | ✅ | — |
| Dropdown/popover open | ❌ | `useLayoutEffect` cleanup |
| Form draft (unsaved) | ✅ | — |
| Form after submit | ❌ | Reset in handler + `useLayoutEffect` |
| Success/error messages | ❌ | `useLayoutEffect` cleanup + ref flag |
| Dialog open state | Depends | Derive from URL (searchParams) |
| Video/audio playback | ❌ Pause | `useLayoutEffect` cleanup |
| Global CSS variables | ❌ Disable | Callback ref `media="not all"` |
| User-scoped data | ❌ Reset | Key by userId or Effect |

## สรุป

1. **Activity preserves all state** — `useState`, DOM, scroll, forms
2. **Reset transient UI** — `useLayoutEffect` cleanup (dropdowns, popovers)
3. **Dialogs** — derive state from URL (searchParams) ไม่ใช่ useState
4. **Forms** — reset ใน submit handler หรือ `useLayoutEffect` cleanup
5. **Auth** — key by userId หรือ `window.location.href` สำหรับ logout
6. **Global styles** — disable ด้วย `media="not all"` เมื่อ hidden
7. **Media** — pause ใน `useLayoutEffect` cleanup
8. **Testing** — ใช้ `getByRole` (auto-filter visibility)
9. **Max 3 routes** preserved — oldest evicted
