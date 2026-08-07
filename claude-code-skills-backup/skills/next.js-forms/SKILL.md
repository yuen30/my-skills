---
name: Next.js Forms
description: Expert guidance on creating forms with Server Actions in Next.js — validation, pending states, optimistic updates, error handling, and programmatic submission.
---

# Next.js Forms

Expert guidance on creating forms with Server Actions in Next.js — validation, pending states, optimistic updates, error handling, and programmatic submission.

@doc-version: 16.2.6

## Core Concepts

React extends HTML `<form>` ให้เรียก Server Actions ผ่าน `action` attribute:
- Server Action ได้รับ `FormData` อัตโนมัติ
- ทำงานบน server เท่านั้น (ปลอดภัย)
- รองรับ progressive enhancement (ทำงานแม้ไม่มี JS)

> **สำคัญ:** ต้อง verify authentication + authorization ใน Server Action ทุกครั้ง

## Guidelines

### 1. Basic Form with Server Action

```tsx
// app/invoices/page.tsx
import { auth } from '@/lib/auth'

export default function Page() {
  async function createInvoice(formData: FormData) {
    'use server'

    const session = await auth()
    if (!session?.user) throw new Error('Unauthorized')

    const rawFormData = {
      customerId: formData.get('customerId'),
      amount: formData.get('amount'),
      status: formData.get('status'),
    }

    // mutate data
    // revalidate cache
  }

  return (
    <form action={createInvoice}>
      <input name="customerId" required />
      <input name="amount" type="number" required />
      <select name="status">
        <option value="pending">Pending</option>
        <option value="paid">Paid</option>
      </select>
      <button type="submit">Create Invoice</button>
    </form>
  )
}
```

> **Tip:** ใช้ `Object.fromEntries(formData)` สำหรับ forms ที่มีหลาย fields

### 2. Passing Additional Arguments (`bind`)

```tsx
// app/client-component.tsx
'use client'

import { updateUser } from './actions'

export function UserProfile({ userId }: { userId: string }) {
  const updateUserWithId = updateUser.bind(null, userId)

  return (
    <form action={updateUserWithId}>
      <input type="text" name="name" />
      <button type="submit">Update User Name</button>
    </form>
  )
}
```

```ts
// app/actions.ts
'use server'

export async function updateUser(userId: string, formData: FormData) {
  const name = formData.get('name') as string
  await db.user.update({ where: { id: userId }, data: { name } })
}
```

> Alternative: `<input type="hidden" name="userId" value={userId} />` แต่ค่าจะอยู่ใน HTML (ไม่ encoded)

### 3. Form Validation

#### Client-side (HTML attributes)

```tsx
<input type="email" name="email" required />
<input type="text" name="name" minLength={2} required />
<input type="password" name="password" minLength={8} required />
```

#### Server-side (Zod)

```ts
// app/actions.ts
'use server'

import { z } from 'zod'

const schema = z.object({
  email: z.string().email('Invalid email'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export async function createUser(prevState: any, formData: FormData) {
  const validatedFields = schema.safeParse({
    email: formData.get('email'),
    name: formData.get('name'),
    password: formData.get('password'),
  })

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: 'Validation failed',
    }
  }

  // Mutate data...
  return { message: 'Success' }
}
```

### 4. Displaying Validation Errors (`useActionState`)

```tsx
// app/ui/signup.tsx
'use client'

import { useActionState } from 'react'
import { createUser } from '@/app/actions'

const initialState = { message: '', errors: {} }

export function SignupForm() {
  const [state, formAction, pending] = useActionState(createUser, initialState)

  return (
    <form action={formAction}>
      <div>
        <label htmlFor="email">Email</label>
        <input type="email" id="email" name="email" required />
        {state?.errors?.email && (
          <p className="text-red-500">{state.errors.email[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="name">Name</label>
        <input type="text" id="name" name="name" required />
        {state?.errors?.name && (
          <p className="text-red-500">{state.errors.name[0]}</p>
        )}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input type="password" id="password" name="password" required />
        {state?.errors?.password && (
          <ul className="text-red-500">
            {state.errors.password.map((error) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        )}
      </div>

      {state?.message && <p aria-live="polite">{state.message}</p>}

      <button disabled={pending} type="submit">
        {pending ? 'Signing up...' : 'Sign up'}
      </button>
    </form>
  )
}
```

> **Note:** เมื่อใช้ `useActionState` — Server Action ได้รับ `prevState` เป็น argument แรก

### 5. Pending State

#### ด้วย `useActionState`

```tsx
'use client'

import { useActionState } from 'react'
import { createUser } from '@/app/actions'

export function Signup() {
  const [state, formAction, pending] = useActionState(createUser, initialState)

  return (
    <form action={formAction}>
      {/* form fields */}
      <button disabled={pending}>
        {pending ? 'Submitting...' : 'Sign up'}
      </button>
    </form>
  )
}
```

#### ด้วย `useFormStatus` (แยก component)

```tsx
// app/ui/submit-button.tsx
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button disabled={pending} type="submit">
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}
```

```tsx
// app/ui/form.tsx
import { SubmitButton } from './submit-button'
import { createUser } from '@/app/actions'

export function Signup() {
  return (
    <form action={createUser}>
      {/* form fields */}
      <SubmitButton />
    </form>
  )
}
```

### 6. Optimistic Updates (`useOptimistic`)

```tsx
'use client'

import { useOptimistic } from 'react'
import { send } from './actions'

type Message = { message: string }

export function Thread({ messages }: { messages: Message[] }) {
  const [optimisticMessages, addOptimisticMessage] = useOptimistic<Message[], string>(
    messages,
    (state, newMessage) => [...state, { message: newMessage }]
  )

  const formAction = async (formData: FormData) => {
    const message = formData.get('message') as string
    addOptimisticMessage(message) // UI อัปเดตทันที
    await send(message)           // Server action ทำงาน background
  }

  return (
    <div>
      {optimisticMessages.map((m, i) => (
        <div key={i}>{m.message}</div>
      ))}
      <form action={formAction}>
        <input type="text" name="message" required />
        <button type="submit">Send</button>
      </form>
    </div>
  )
}
```

### 7. Multiple Actions in One Form (`formAction`)

```tsx
import { publishPost, saveDraft } from '@/app/actions'

export function PostForm() {
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

### 8. Programmatic Submission

```tsx
'use client'

export function Entry() {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (
      (e.ctrlKey || e.metaKey) &&
      (e.key === 'Enter' || e.key === 'NumpadEnter')
    ) {
      e.preventDefault()
      e.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <div>
      <textarea name="entry" rows={20} required onKeyDown={handleKeyDown} />
    </div>
  )
}
```

### 9. Complete Form Pattern

```tsx
// app/actions.ts
'use server'

import { z } from 'zod'
import { auth } from '@/lib/auth'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

const PostSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  content: z.string().min(1, 'Content is required'),
})

export async function createPost(prevState: any, formData: FormData) {
  // 1. Auth check
  const session = await auth()
  if (!session?.user) {
    return { message: 'Unauthorized' }
  }

  // 2. Validate
  const validatedFields = PostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  })

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors }
  }

  // 3. Mutate
  const post = await db.post.create({
    data: {
      ...validatedFields.data,
      authorId: session.user.id,
    },
  })

  // 4. Revalidate + Redirect
  revalidatePath('/posts')
  redirect(`/posts/${post.id}`)
}
```

```tsx
// app/posts/new/page.tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

export default function NewPostPage() {
  const [state, formAction, pending] = useActionState(createPost, {})

  return (
    <form action={formAction}>
      <div>
        <label htmlFor="title">Title</label>
        <input id="title" name="title" required />
        {state?.errors?.title && <p className="text-red-500">{state.errors.title[0]}</p>}
      </div>

      <div>
        <label htmlFor="content">Content</label>
        <textarea id="content" name="content" required />
        {state?.errors?.content && <p className="text-red-500">{state.errors.content[0]}</p>}
      </div>

      {state?.message && <p aria-live="polite">{state.message}</p>}

      <button disabled={pending} type="submit">
        {pending ? 'Creating...' : 'Create Post'}
      </button>
    </form>
  )
}
```

## Quick Reference

| Hook/API | Purpose |
|----------|---------|
| `useActionState` | State + pending + error handling |
| `useFormStatus` | Pending state (nested component) |
| `useOptimistic` | Optimistic UI updates |
| `formAction` prop | Multiple actions per form |
| `requestSubmit()` | Programmatic submission |
| `.bind(null, arg)` | Pass additional arguments |

## สรุป

1. **`<form action={serverAction}>`** — Server Action ได้รับ FormData อัตโนมัติ
2. **Validate ด้วย Zod** — server-side validation ทุกครั้ง
3. **`useActionState`** — แสดง errors + pending state
4. **`useFormStatus`** — pending indicator (แยก component)
5. **`useOptimistic`** — UI อัปเดตทันทีก่อน server ตอบ
6. **`bind`** — ส่ง arguments เพิ่มเติมนอก form fields
7. **Auth ทุกครั้ง** — ตรวจสอบ session ใน Server Action
8. **Progressive enhancement** — ทำงานแม้ไม่มี JavaScript
