---
name: Next.js Authentication
description: Expert guidance on implementing authentication in Next.js — sign-up/login, session management, authorization, DAL pattern, and security best practices.
---

# Next.js Authentication

Expert guidance on implementing authentication in Next.js — sign-up/login, session management, authorization, DAL pattern, and security best practices.

@doc-version: 16.2.6

## Core Concepts

Authentication แบ่งเป็น 3 ส่วน:
1. **Authentication** — ยืนยันตัวตน (username/password, OAuth)
2. **Session Management** — รักษา auth state ข้าม requests
3. **Authorization** — ควบคุมสิทธิ์การเข้าถึง routes และ data

## Guidelines

### 1. Authentication — Sign-up/Login

#### Form + Server Action

```tsx
// app/ui/signup-form.tsx
'use client'

import { useActionState } from 'react'
import { signup } from '@/app/actions/auth'

export default function SignupForm() {
  const [state, action, pending] = useActionState(signup, undefined)

  return (
    <form action={action}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" name="name" placeholder="Name" />
      </div>
      {state?.errors?.name && <p>{state.errors.name}</p>}

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" placeholder="Email" />
      </div>
      {state?.errors?.email && <p>{state.errors.email}</p>}

      <div>
        <label htmlFor="password">Password</label>
        <input id="password" name="password" type="password" />
      </div>
      {state?.errors?.password && (
        <ul>
          {state.errors.password.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}

      <button disabled={pending} type="submit">Sign Up</button>
    </form>
  )
}
```

#### Validation with Zod

```ts
// app/lib/definitions.ts
import * as z from 'zod'

export const SignupFormSchema = z.object({
  name: z.string().min(2, { error: 'Name must be at least 2 characters long.' }).trim(),
  email: z.email({ error: 'Please enter a valid email.' }).trim(),
  password: z
    .string()
    .min(8, { error: 'Be at least 8 characters long' })
    .regex(/[a-zA-Z]/, { error: 'Contain at least one letter.' })
    .regex(/[0-9]/, { error: 'Contain at least one number.' })
    .regex(/[^a-zA-Z0-9]/, { error: 'Contain at least one special character.' })
    .trim(),
})

export type FormState =
  | { errors?: { name?: string[]; email?: string[]; password?: string[] }; message?: string }
  | undefined
```

#### Server Action

```ts
// app/actions/auth.ts
'use server'

import { SignupFormSchema, FormState } from '@/app/lib/definitions'
import { createSession } from '@/app/lib/session'
import { redirect } from 'next/navigation'
import bcrypt from 'bcrypt'

export async function signup(state: FormState, formData: FormData) {
  // 1. Validate form fields
  const validatedFields = SignupFormSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    password: formData.get('password'),
  })

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors }
  }

  // 2. Hash password
  const { name, email, password } = validatedFields.data
  const hashedPassword = await bcrypt.hash(password, 10)

  // 3. Insert user into database
  const data = await db.insert(users).values({
    name,
    email,
    password: hashedPassword,
  }).returning({ id: users.id })

  const user = data[0]
  if (!user) {
    return { message: 'An error occurred while creating your account.' }
  }

  // 4. Create session
  await createSession(user.id)

  // 5. Redirect
  redirect('/dashboard')
}
```

### 2. Session Management

#### Stateless Sessions (JWT in Cookie)

**Generate secret key:**

```bash
openssl rand -base64 32
```

```env
SESSION_SECRET=your_secret_key
```

**Encrypt/Decrypt with Jose:**

```ts
// app/lib/session.ts
import 'server-only'
import { SignJWT, jwtVerify } from 'jose'
import { cookies } from 'next/headers'

const secretKey = process.env.SESSION_SECRET
const encodedKey = new TextEncoder().encode(secretKey)

export async function encrypt(payload: { userId: string; expiresAt: Date }) {
  return new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(encodedKey)
}

export async function decrypt(session: string | undefined = '') {
  try {
    const { payload } = await jwtVerify(session, encodedKey, {
      algorithms: ['HS256'],
    })
    return payload
  } catch (error) {
    console.log('Failed to verify session')
  }
}
```

**Create session:**

```ts
// app/lib/session.ts (continued)
export async function createSession(userId: string) {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  const session = await encrypt({ userId, expiresAt })

  const cookieStore = await cookies()
  cookieStore.set('session', session, {
    httpOnly: true,
    secure: true,
    expires: expiresAt,
    sameSite: 'lax',
    path: '/',
  })
}
```

**Update/Refresh session:**

```ts
export async function updateSession() {
  const session = (await cookies()).get('session')?.value
  const payload = await decrypt(session)

  if (!session || !payload) return null

  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  const cookieStore = await cookies()
  cookieStore.set('session', session, {
    httpOnly: true,
    secure: true,
    expires,
    sameSite: 'lax',
    path: '/',
  })
}
```

**Delete session (logout):**

```ts
export async function deleteSession() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
}
```

```ts
// app/actions/auth.ts
import { deleteSession } from '@/app/lib/session'
import { redirect } from 'next/navigation'

export async function logout() {
  await deleteSession()
  redirect('/login')
}
```

#### Cookie Options (Recommended)

| Option | Value | Purpose |
|--------|-------|---------|
| `httpOnly` | `true` | ป้องกัน JS อ่าน cookie |
| `secure` | `true` | ส่งผ่าน HTTPS เท่านั้น |
| `sameSite` | `'lax'` | ป้องกัน CSRF |
| `expires` | Date | หมดอายุอัตโนมัติ |
| `path` | `'/'` | ใช้ได้ทุก path |

#### Database Sessions

```ts
// app/lib/session.ts
import { cookies } from 'next/headers'
import { db } from '@/app/lib/db'

export async function createSession(userId: number) {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)

  // 1. Create session in database
  const data = await db.insert(sessions).values({
    userId,
    expiresAt,
  }).returning({ id: sessions.id })

  const sessionId = data[0].id

  // 2. Encrypt session ID
  const session = await encrypt({ sessionId, expiresAt })

  // 3. Store in cookie
  const cookieStore = await cookies()
  cookieStore.set('session', session, {
    httpOnly: true,
    secure: true,
    expires: expiresAt,
    sameSite: 'lax',
    path: '/',
  })
}
```

### 3. Authorization

#### Data Access Layer (DAL)

Centralize authorization logic:

```ts
// app/lib/dal.ts
import 'server-only'
import { cache } from 'react'
import { cookies } from 'next/headers'
import { decrypt } from '@/app/lib/session'
import { redirect } from 'next/navigation'

export const verifySession = cache(async () => {
  const cookie = (await cookies()).get('session')?.value
  const session = await decrypt(cookie)

  if (!session?.userId) {
    redirect('/login')
  }

  return { isAuth: true, userId: session.userId }
})

export const getUser = cache(async () => {
  const session = await verifySession()
  if (!session) return null

  try {
    const data = await db.query.users.findMany({
      where: eq(users.id, session.userId),
      columns: { id: true, name: true, email: true },
    })
    return data[0]
  } catch (error) {
    console.log('Failed to fetch user')
    return null
  }
})
```

#### Optimistic Checks with Proxy

```ts
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'
import { decrypt } from '@/app/lib/session'
import { cookies } from 'next/headers'

const protectedRoutes = ['/dashboard']
const publicRoutes = ['/login', '/signup', '/']

export default async function proxy(req: NextRequest) {
  const path = req.nextUrl.pathname
  const isProtectedRoute = protectedRoutes.includes(path)
  const isPublicRoute = publicRoutes.includes(path)

  // Decrypt session from cookie (optimistic check only)
  const cookie = (await cookies()).get('session')?.value
  const session = await decrypt(cookie)

  // Redirect to /login if not authenticated
  if (isProtectedRoute && !session?.userId) {
    return NextResponse.redirect(new URL('/login', req.nextUrl))
  }

  // Redirect to /dashboard if authenticated
  if (isPublicRoute && session?.userId && !req.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/dashboard', req.nextUrl))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
}
```

> **สำคัญ:** Proxy ทำ optimistic checks เท่านั้น (อ่านจาก cookie) — ไม่ query database เพื่อ performance

#### Authorization in Server Components

```tsx
// app/dashboard/page.tsx
import { verifySession } from '@/app/lib/dal'

export default async function Dashboard() {
  const session = await verifySession()
  const userRole = session?.user?.role

  if (userRole === 'admin') {
    return <AdminDashboard />
  } else if (userRole === 'user') {
    return <UserDashboard />
  } else {
    redirect('/login')
  }
}
```

#### Authorization in Server Actions

```ts
// app/lib/actions.ts
'use server'

import { verifySession } from '@/app/lib/dal'

export async function deleteUser(userId: string) {
  const session = await verifySession()

  if (session?.user?.role !== 'admin') {
    return null // หรือ throw error
  }

  await db.delete(users).where(eq(users.id, userId))
}
```

#### Authorization in Route Handlers

```ts
// app/api/admin/route.ts
import { verifySession } from '@/app/lib/dal'

export async function GET() {
  const session = await verifySession()

  if (!session) {
    return new Response(null, { status: 401 })
  }

  if (session.user.role !== 'admin') {
    return new Response(null, { status: 403 })
  }

  // Continue for authorized users
}
```

### 4. Data Transfer Objects (DTO)

Return เฉพาะข้อมูลที่จำเป็น:

```ts
// app/lib/dto.ts
import 'server-only'
import { getUser } from '@/app/lib/dal'

export async function getProfileDTO(slug: string) {
  const data = await db.query.users.findMany({
    where: eq(users.slug, slug),
  })
  const user = data[0]
  const currentUser = await getUser()

  return {
    username: user.username,
    // แสดง phone เฉพาะ admin หรือ same team
    phonenumber: currentUser?.isAdmin || user.team === currentUser?.team
      ? user.phonenumber
      : null,
  }
}
```

### 5. Security Best Practices

- **Hash passwords** ด้วย bcrypt ก่อนเก็บ database
- **Validate input** ด้วย Zod ทุกครั้งใน Server Actions
- **Cookie: httpOnly + secure + sameSite** — ป้องกัน XSS + CSRF
- **Proxy = optimistic checks only** — ไม่ query database
- **DAL = secure checks** — verify session ใกล้ data source ที่สุด
- **DTO = minimal data** — ไม่ส่ง sensitive fields ไป client
- **`server-only`** — ป้องกัน session logic หลุดไป client
- **`React.cache`** — memoize verifySession ไม่ query ซ้ำ

## Auth Libraries

| Library | Features |
|---------|----------|
| NextAuth.js (Auth.js) | OAuth, credentials, session management |
| Clerk | Full auth UI, user management, RBAC |
| Auth0 | Enterprise SSO, MFA |
| Better Auth | Lightweight, flexible |
| Supabase Auth | PostgreSQL-based, social logins |
| Kinde | User management, feature flags |
| WorkOS | Enterprise SSO, directory sync |

## Session Management Libraries

| Library | Use Case |
|---------|----------|
| Jose | JWT (Edge Runtime compatible) |
| Iron Session | Encrypted cookie sessions |

## Architecture Summary

```
Request Flow:
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐
│  Proxy  │────▶│  Layout │────▶│  Page   │────▶│  Data    │
│(optimis)│     │         │     │         │     │  Access  │
└─────────┘     └─────────┘     └─────────┘     │  Layer   │
                                                  └──────────┘
Optimistic        Don't check     verifySession()  verifySession()
cookie check      auth here       + fetch data     + query DB
(no DB query)     (partial render)
```

## สรุป

1. **Authentication:** Server Actions + Zod validation + bcrypt hash
2. **Session:** JWT in httpOnly cookie (Jose) หรือ database sessions
3. **Authorization:** DAL pattern + `verifySession()` + `React.cache`
4. **Proxy:** Optimistic checks only (cookie, ไม่ query DB)
5. **DTO:** Return เฉพาะข้อมูลที่จำเป็น
6. **ใช้ Auth Library** ถ้าต้องการ OAuth, MFA, social logins
