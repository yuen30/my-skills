---
name: Next.js Mutating Data
description: Expert guidance on mutating data in Next.js App Router using Server Functions, Server Actions, forms, revalidation, and security best practices.
---

# Next.js Mutating Data

Expert guidance on mutating data in Next.js App Router using Server Functions, Server Actions, forms, revalidation, and security best practices.

@doc-version: 16.2.6

## Core Concepts

- **Server Function** — ฟังก์ชัน async ที่รันบน server เท่านั้น แต่เรียกจาก client ได้ผ่าน HTTP POST
- **Server Action** — Server Function ที่ใช้ในบริบท mutation (เพิ่ม/ลบ/แก้ข้อมูล) โดย Next.js จัดการ UI update + data update ใน single roundtrip

## Guidelines

### 1. การสร้าง Server Functions (`"use server"`)

#### ในไฟล์แยก (ใช้ได้ทั้ง Server และ Client Components)

```tsx
// app/actions.ts
'use server'

import { db } from '@/lib/db'
import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  await db.post.create({ data: { title, content } })
  revalidatePath('/posts')
}

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } })
  revalidatePath('/posts')
}
```

#### Inline ใน Server Component

```tsx
// app/posts/page.tsx (Server Component)
export default function PostsPage() {
  async function create(formData: FormData) {
    'use server'
    const title = formData.get('title') as string
    await db.post.create({ data: { title } })
    revalidatePath('/posts')
  }

  return (
    <form action={create}>
      <input name="title" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

**กฎสำคัญ:**
- ไฟล์ที่มี `"use server"` ที่หัวไฟล์ → ทุกฟังก์ชันที่ export เป็น Server Function
- ใน Server Component ใส่ `"use server"` ที่บรรทัดแรกของฟังก์ชัน
- Client Components **ต้อง import** จากไฟล์ภายนอก (ไม่สามารถเขียน inline ได้)

### 2. การเรียกใช้งาน (Invocation)

#### ผ่าน Forms — `action` prop

```tsx
// app/posts/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Publish</button>
    </form>
  )
}
```

ฟังก์ชันจะได้รับ `FormData` อัตโนมัติ:

```tsx
'use server'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string
  // ...
}
```

#### ผ่าน `formAction` — หลายปุ่มในฟอร์มเดียว

```tsx
import { publishPost, saveDraft } from '@/app/actions'

export default function PostForm() {
  return (
    <form>
      <input name="title" required />
      <textarea name="content" required />
      <button formAction={saveDraft}>Save Draft</button>
      <button formAction={publishPost}>Publish</button>
    </form>
  )
}
```

#### ผ่าน Event Handlers (Client Components)

```tsx
'use client'

import { deletePost } from '@/app/actions'

export function DeleteButton({ postId }: { postId: string }) {
  async function handleDelete() {
    await deletePost(postId)
  }

  return (
    <button onClick={handleDelete}>
      Delete
    </button>
  )
}
```

### 3. Pending State — แสดงสถานะการโหลด

#### ใช้ `useActionState`

```tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

export function CreatePostForm() {
  const [state, action, isPending] = useActionState(createPost, null)

  return (
    <form action={action}>
      <input name="title" required disabled={isPending} />
      <textarea name="content" required disabled={isPending} />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Post'}
      </button>
      {state?.error && <p className="text-red-500">{state.error}</p>}
    </form>
  )
}
```

Server Action ที่ return state:

```tsx
'use server'

export async function createPost(prevState: any, formData: FormData) {
  const title = formData.get('title') as string

  if (!title) {
    return { error: 'Title is required' }
  }

  await db.post.create({ data: { title } })
  revalidatePath('/posts')
  return { success: true }
}
```

#### ใช้ `useTransition`

```tsx
'use client'

import { useTransition } from 'react'
import { deletePost } from '@/app/actions'

export function DeleteButton({ postId }: { postId: string }) {
  const [isPending, startTransition] = useTransition()

  return (
    <button
      onClick={() => startTransition(() => deletePost(postId))}
      disabled={isPending}
    >
      {isPending ? 'Deleting...' : 'Delete'}
    </button>
  )
}
```

### 4. Data Freshness — ทำให้ข้อมูลเป็นปัจจุบัน

#### `revalidatePath()` — ล้าง cache ตาม path

```tsx
'use server'

import { revalidatePath } from 'next/cache'

export async function updatePost(id: string, formData: FormData) {
  await db.post.update({ where: { id }, data: { title: formData.get('title') as string } })

  revalidatePath('/posts')        // ล้าง cache หน้า /posts
  revalidatePath(`/posts/${id}`)  // ล้าง cache หน้า post นั้นด้วย
}
```

#### `revalidateTag()` — ล้าง cache ตาม tag

```tsx
'use server'

import { revalidateTag } from 'next/cache'

export async function createComment(formData: FormData) {
  await db.comment.create({ data: { body: formData.get('body') as string } })

  revalidateTag('comments') // ล้าง cache ทุกที่ที่ tag ว่า 'comments'
}
```

#### `refresh()` — โหลดข้อมูลหน้าปัจจุบันใหม่ (Client-side)

```tsx
'use client'

import { useRouter } from 'next/navigation'
import { likePost } from '@/app/actions'

export function LikeButton({ postId }: { postId: string }) {
  const router = useRouter()

  async function handleLike() {
    await likePost(postId)
    router.refresh() // สั่งให้ Client Router โหลดข้อมูลใหม่
  }

  return <button onClick={handleLike}>❤️ Like</button>
}
```

### 5. Redirect หลัง Mutation

```tsx
'use server'

import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const post = await db.post.create({
    data: { title: formData.get('title') as string },
  })

  revalidatePath('/posts')
  redirect(`/posts/${post.id}`) // ส่งผู้ใช้ไปหน้า post ใหม่
}
```

**หมายเหตุ:** `redirect()` ต้องเรียกนอก try/catch (มันทำงานโดย throw error ภายใน)

### 6. Cookies

```tsx
'use server'

import { cookies } from 'next/headers'

export async function setTheme(theme: string) {
  const cookieStore = await cookies()
  cookieStore.set('theme', theme)
}

export async function getTheme() {
  const cookieStore = await cookies()
  return cookieStore.get('theme')?.value ?? 'light'
}

export async function clearSession() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
}
```

### 7. เรียก Server Action ใน `useEffect`

```tsx
'use client'

import { useEffect, startTransition } from 'react'
import { incrementViews } from '@/app/actions'

export function ViewCounter({ postId }: { postId: string }) {
  useEffect(() => {
    startTransition(() => {
      incrementViews(postId)
    })
  }, [postId])

  return null
}
```

```tsx
// app/actions.ts
'use server'

export async function incrementViews(postId: string) {
  await db.post.update({
    where: { id: postId },
    data: { views: { increment: 1 } },
  })
}
```

### 8. ความปลอดภัย (สำคัญมาก)

Server Functions = API Endpoint ที่เข้าถึงได้ผ่าน POST Request โดยตรง

**กฎเหล็ก:** ตรวจสอบ Authentication + Authorization ภายในฟังก์ชันทุกครั้ง

```tsx
'use server'

import { auth } from '@/lib/auth'
import { redirect } from 'next/navigation'

export async function deletePost(postId: string) {
  // ✅ ตรวจสอบสิทธิ์ทุกครั้ง
  const session = await auth()
  if (!session?.user) {
    redirect('/login')
  }

  // ✅ ตรวจสอบ ownership
  const post = await db.post.findUnique({ where: { id: postId } })
  if (post?.authorId !== session.user.id) {
    throw new Error('Unauthorized')
  }

  // ✅ ปลอดภัยแล้ว ค่อยลบ
  await db.post.delete({ where: { id: postId } })
  revalidatePath('/posts')
}
```

**อย่าเชื่อ input จาก client:**

```tsx
'use server'

import { z } from 'zod'

const PostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1).max(10000),
})

export async function createPost(formData: FormData) {
  // ✅ Validate input เสมอ
  const parsed = PostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  })

  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors }
  }

  await db.post.create({ data: parsed.data })
  revalidatePath('/posts')
}
```

## Quick Reference

| หัวข้อ | วิธี |
|--------|------|
| สร้าง Server Function | `"use server"` ที่หัวไฟล์หรือในฟังก์ชัน |
| เรียกผ่าน Form | `<form action={serverAction}>` |
| เรียกผ่าน Event | `onClick={() => serverAction()}` |
| แสดง Loading | `useActionState` หรือ `useTransition` |
| ล้าง Cache | `revalidatePath()` / `revalidateTag()` |
| โหลดใหม่ฝั่ง Client | `router.refresh()` |
| เปลี่ยนหน้า | `redirect('/path')` |
| จัดการ Cookie | `cookies().set()` / `.get()` / `.delete()` |
| เรียกตอนโหลดหน้า | `useEffect` + `startTransition` |

## สรุป

1. ใช้ `"use server"` สร้างฟังก์ชันรันบน server
2. เรียกผ่าน form `action` หรือ event handler
3. จัดการ loading ด้วย `useActionState` / `useTransition`
4. อัปเดตข้อมูลด้วย `revalidatePath()` / `revalidateTag()` / `refresh()`
5. **ตรวจสอบ auth + validate input ภายในฟังก์ชันทุกครั้ง**
