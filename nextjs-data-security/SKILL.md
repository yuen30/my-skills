---
name: Next.js Data Security
description: Expert guidance on data security in Next.js — Data Access Layer, DTOs, taint APIs, Server Actions security, input validation, and audit checklist.
---

# Next.js Data Security

Expert guidance on data security in Next.js — Data Access Layer, DTOs, taint APIs, Server Actions security, input validation, and audit checklist.

@doc-version: 16.2.6

## Core Concepts

React Server Components เปลี่ยนวิธีที่ data ถูก access — ต้องคิดใหม่เรื่อง security:
- Server Components เข้าถึง secrets/DB ได้ แต่ต้องระวังไม่ส่ง private data ไป client
- Server Actions เป็น public POST endpoints — ต้อง validate + authorize ทุกครั้ง
- Client Components ต้องได้รับเฉพาะ data ที่ safe

## Guidelines

### 1. Data Fetching Approaches

| Approach | ใช้เมื่อ | Security Level |
|----------|---------|:-:|
| External HTTP APIs | Existing large apps, separate backend teams | สูง (Zero Trust) |
| Data Access Layer (DAL) | New projects | สูงสุด (centralized) |
| Component-level | Prototypes, learning | ต่ำ (ต้องระวัง) |

> **แนะนำ:** เลือก 1 approach แล้วใช้ consistent ทั้งโปรเจกต์

### 2. Data Access Layer (DAL) — แนะนำ

Centralize data access + authorization:

```ts
// data/auth.ts
import { cache } from 'react'
import { cookies } from 'next/headers'

export const getCurrentUser = cache(async () => {
  const token = (await cookies()).get('AUTH_TOKEN')
  const decodedToken = await decryptAndValidate(token)
  // ไม่ return secret tokens หรือ private info
  return new User(decodedToken.id)
})
```

```ts
// data/user-dto.ts
import 'server-only'
import { getCurrentUser } from './auth'

function canSeeUsername(viewer: User) {
  return true
}

function canSeePhoneNumber(viewer: User, team: string) {
  return viewer.isAdmin || team === viewer.team
}

export async function getProfileDTO(slug: string) {
  const [rows] = await sql`SELECT * FROM user WHERE slug = ${slug}`
  const userData = rows[0]
  const currentUser = await getCurrentUser()

  // Return เฉพาะ data ที่ user มีสิทธิ์เห็น
  return {
    username: canSeeUsername(currentUser) ? userData.username : null,
    phonenumber: canSeePhoneNumber(currentUser, userData.team)
      ? userData.phonenumber
      : null,
  }
}
```

**DAL ต้อง:**
- ใช้ `import 'server-only'`
- ทำ authorization checks
- Return safe, minimal DTOs
- เป็นที่เดียวที่เข้าถึง `process.env` secrets

### 3. Preventing Data Leaks to Client

#### ❌ Bad: ส่ง raw data ไป Client Component

```tsx
// app/page.tsx
export default async function Page({ params }) {
  const [rows] = await sql`SELECT * FROM user WHERE slug = ${params.slug}`
  const userData = rows[0]
  // ❌ EXPOSED: ส่งทุก field ไป client (รวม password, internal IDs)
  return <Profile user={userData} />
}
```

#### ✅ Good: Sanitize ก่อนส่ง

```tsx
// app/page.tsx
import { getProfileDTO } from '@/data/user-dto'

export default async function Page({ params }) {
  const profile = await getProfileDTO(params.slug)
  // ✅ Safe: เฉพาะ public fields
  return <Profile user={profile} />
}
```

### 4. Taint APIs (Experimental)

ป้องกัน objects/values ถูกส่งไป client โดยไม่ตั้งใจ:

```js
// next.config.js
module.exports = {
  experimental: {
    taint: true,
  },
}
```

```ts
import { experimental_taintObjectReference } from 'react'

const user = await db.user.findUnique({ where: { id } })
experimental_taintObjectReference('Do not pass user to client', user)
// ถ้าพยายามส่ง user ไป Client Component → error
```

> Taint เป็น additional layer — ยังต้อง filter data ใน DAL

### 5. `server-only` Package

ป้องกัน server code ถูก import ใน client:

```ts
// lib/secrets.ts
import 'server-only'

export function getAPIKey() {
  return process.env.SECRET_API_KEY
}
```

ถ้า import ใน Client Component → **build error ทันที**

### 6. Server Actions Security

#### Built-in Protections

- **Secure action IDs** — encrypted, non-deterministic, recalculated between builds
- **Dead code elimination** — unused actions ถูกลบจาก client bundle
- **POST only** — ป้องกัน CSRF (ร่วมกับ SameSite cookies)
- **Origin check** — compare Origin vs Host header

#### Always Validate Input

```tsx
// ❌ BAD: Trust client input
export default async function Page({ searchParams }) {
  const isAdmin = searchParams.get('isAdmin')
  if (isAdmin === 'true') return <AdminPanel /> // Vulnerable!
}

// ✅ GOOD: Re-verify every time
import { cookies } from 'next/headers'
import { verifyAdmin } from './auth'

export default async function Page() {
  const token = (await cookies()).get('AUTH_TOKEN')
  const isAdmin = await verifyAdmin(token)
  if (isAdmin) return <AdminPanel />
}
```

#### Always Re-authorize in Actions

```tsx
// app/admin/page.tsx
export default async function AdminPage() {
  const session = await auth()
  if (!session?.user?.isAdmin) redirect('/login')

  return (
    <form
      action={async () => {
        'use server'
        // ✅ CRITICAL: Re-verify inside action
        const session = await auth()
        if (!session?.user?.isAdmin) throw new Error('Unauthorized')
        await db.record.deleteMany()
      }}
    >
      <button>Delete Records</button>
    </form>
  )
}
```

> Page-level auth ≠ Action-level auth — Server Actions เป็น separate entry points

#### Check Authorization (Not Just Authentication)

```ts
// app/actions.ts
'use server'

export async function deletePost(postId: string) {
  const session = await auth()
  if (!session?.user) throw new Error('Unauthorized')

  const post = await db.post.findUnique({ where: { id: postId } })

  // ✅ Check ownership (ป้องกัน IDOR)
  if (post.authorId !== session.user.id) {
    throw new Error('Forbidden')
  }

  await db.post.delete({ where: { id: postId } })
}
```

#### Control Return Values

```ts
// ❌ BAD: Return full database record
export async function updateUser(data: FormData) {
  return db.user.update({ ... }) // อาจมี internal fields
}

// ✅ GOOD: Return only what client needs
export async function updateUser(data: FormData) {
  await db.user.update({ ... })
  return { success: true }
}
```

### 7. DAL for Mutations

```ts
// data/posts.ts
import 'server-only'
import { auth } from '@/lib/auth'

export async function deletePost(postId: string) {
  const session = await auth()
  if (!session?.user) throw new Error('Unauthorized')

  const post = await db.post.findUnique({ where: { id: postId } })
  if (post.authorId !== session.user.id) throw new Error('Forbidden')

  await db.post.delete({ where: { id: postId } })
}
```

```ts
// app/actions.ts
'use server'

import { deletePost } from '@/data/posts'
import { revalidatePath } from 'next/cache'

export async function deletePostAction(postId: string) {
  await deletePost(postId) // Auth + authz inside DAL
  revalidatePath('/posts')
}
```

### 8. Closures and Encryption

Server Actions ใน component สร้าง closure — captured variables ถูก encrypt อัตโนมัติ:

```tsx
export default async function Page() {
  const publishVersion = await getLatestVersion()

  async function publish() {
    'use server'
    // publishVersion ถูก encrypt ก่อนส่งไป client
    if (publishVersion !== await getLatestVersion()) {
      throw new Error('Version changed')
    }
  }

  return <form><button formAction={publish}>Publish</button></form>
}
```

- Private key ใหม่ทุก build
- Self-hosting หลาย servers: ตั้ง `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`

```bash
openssl rand -base64 32
```

### 9. Allowed Origins (CSRF Protection)

```js
// next.config.js
module.exports = {
  experimental: {
    serverActions: {
      allowedOrigins: ['my-proxy.com', '*.my-proxy.com'],
    },
  },
}
```

### 10. No Mutations During Rendering

```tsx
// ❌ BAD: Side-effect during render
export default async function Page({ searchParams }) {
  if (searchParams.get('logout')) {
    cookies().delete('AUTH_TOKEN') // Side-effect!
  }
}

// ✅ GOOD: Use Server Action
import { logout } from './actions'

export default function Page() {
  return (
    <form action={logout}>
      <button type="submit">Logout</button>
    </form>
  )
}
```

## Security Audit Checklist

| Area | Check |
|------|-------|
| **DAL** | มี isolated Data Access Layer? DB packages ไม่ถูก import นอก DAL? |
| **`"use client"` files** | Props ไม่มี private data? Type signatures ไม่ broad เกินไป? |
| **`"use server"` files** | Arguments validated? User re-authorized? Ownership checked? Return values filtered? |
| **`/[param]/` folders** | Params validated? (user input!) |
| **`proxy.ts` + `route.ts`** | มี power มาก — audit เป็นพิเศษ |
| **Environment variables** | เฉพาะ DAL เข้าถึง `process.env`? `NEXT_PUBLIC_` ไม่มี secrets? |
| **Rate limiting** | Expensive operations มี rate limit? |

## สรุป

1. **ใช้ Data Access Layer** — centralize auth + data access + DTOs
2. **`server-only`** — ป้องกัน server code หลุดไป client
3. **Validate ทุก input** — อย่าเชื่อ searchParams, formData, headers
4. **Re-authorize ใน Server Actions** — page auth ≠ action auth
5. **Check ownership** — ป้องกัน IDOR (ไม่ใช่แค่ authentication)
6. **Return minimal data** — DTOs, ไม่ส่ง raw DB records
7. **ไม่ mutate ตอน render** — ใช้ Server Actions
8. **Taint APIs** — additional layer ป้องกัน accidental exposure
9. **Encryption** — closures ถูก encrypt อัตโนมัติ
10. **Audit regularly** — proxy.ts, route.ts, [param] folders
