---
name: Next.js Clean Code Architecture
description: Foundation skill — clean code principles, strict rules, folder structure, naming conventions, and architectural patterns for Next.js 16 with TypeScript. Reference this in ALL Next.js work.
---

# Next.js Clean Code Architecture

**Identifier:** `nextjs-clean-code`
**Target:** Next.js 16.x (App Router), TypeScript 5.x

## 🎯 Core Philosophy

สถาปัตยกรรมนี้ยึดหลัก **Separation of Concerns** และ **Single Responsibility** เพื่อทำให้โปรเจกต์ Next.js 16 ขยายตัวได้ง่าย (Scalable) และง่ายต่อการบำรุงรักษา โดยแบ่งแยกหน้าที่การทำงานออกจากกันอย่างเด็ดขาดตามโฟลเดอร์โครงสร้าง และจำกัดพฤติกรรมให้ `app/` ทำหน้าที่เป็นเพียง **ทางผ่านของ Route** เท่านั้น

## ⚠️ Foundation Skill — Reference This in ALL Next.js Work

This skill defines the **architectural rules** for the entire project. When writing any Next.js code (forms, route handlers, data fetching, etc.), ALWAYS follow these principles. เมื่อได้รับคำสั่งให้เขียนโค้ด ให้อ้างอิงโครงสร้างนี้เสมอ

---

## 🛠️ Strict Rules (กฎเหล็ก — NON-NEGOTIABLE)

เมื่อ AI ได้รับคำสั่งให้เขียนหรือแก้ไขโค้ดในโปรเจกต์นี้ **ต้องปฏิบัติตามกฎต่อไปนี้อย่างเคร่งครัด:**

### Rule 1: Routing Only (`app/`)

**ห้ามใส่ Business Logic, Data Fetching ดิบ, หรือการแปลงโครงสร้าง Data ใน `app/` เด็ดขาด**

ให้ทำหน้าที่เป็น Thin Pages ที่เรียกใช้ Service แล้วส่งข้อมูลต่อให้ Component ทันที

```tsx
// ✅ CORRECT — Thin Page
import { getStats } from '@/services/dashboard.service'
import { DashboardContent } from '@/components/dashboard/dashboard-content'

export default async function DashboardPage() {
  const stats = await getStats()
  return <DashboardContent stats={stats} />
}
```

```tsx
// ❌ WRONG — Fat Page (business logic in app/)
export default async function DashboardPage() {
  const res = await fetch('https://api.example.com/stats')
  const data = await res.json()
  const filtered = data.filter(item => item.active)
  const sorted = filtered.sort((a, b) => b.date - a.date)
  return <div>{sorted.map(...)}</div>
}
```

### Rule 2: Server-Only Isolation (`services/`)

**ทุกไฟล์ใน `services/` ต้องประกาศ `import 'server-only'` ที่บรรทัดแรก** เพื่อป้องกันไม่ให้ Logic ฝั่ง Server หลุดไปรันบน Client Browser

```tsx
// ✅ CORRECT
import 'server-only'
import { db } from '@/lib/db'
import type { User } from '@/types'

export async function getUserById(id: string): Promise<User | null> {
  try {
    if (!id) return null
    return await db.user.findUnique({ where: { id } })
  } catch (error) {
    console.error(`[UserService] Failed to fetch user ${id}:`, error)
    return null
  }
}
```

### Rule 3: Strict Naming Style

| Type | Convention | Example |
|------|-----------|---------|
| Files (ทั่วไป) | `kebab-case` | `user-card.tsx`, `dashboard-content.tsx` |
| Files (hooks) | `kebab-case` + `use-` prefix | `use-debounce.ts`, `use-local-storage.ts` |
| Files (services) | `kebab-case` + `.service` suffix | `user.service.ts`, `product.service.ts` |
| Files (actions) | `kebab-case` + `.actions` suffix | `user.actions.ts`, `auth.actions.ts` |
| Components | `PascalCase` | `UserCard`, `DashboardContent` |
| Functions/Variables | `camelCase` | `getUserById`, `formatCurrency` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE`, `DEFAULT_PAGE_SIZE` |
| Types/Interfaces | `PascalCase` | `User`, `ApiResponse`, `PaginatedResponse` |

### Rule 4: Primary Key Format — ULID Only

**ในทุก Database Schema, Type Definition หรือ Mock Data หากมี ID หรือ Primary Key ให้บังคับใช้ฟอร์แมต ULID เป็นสตริงเสมอ**

```tsx
// ✅ CORRECT — ULID string
interface User {
  id: string  // ULID: "01HXYZ..."
  name: string
  email: string
}

// ❌ WRONG — UUID or auto-increment
interface User {
  id: number           // ❌ Auto-increment
  uuid: string         // ❌ UUID format
}
```

### Rule 5: No `any` Policy

**ห้ามใช้ `any` ในโค้ดเด็ดขาด** หากไม่ทราบแน่ชัดให้ใช้ Generic Type, `unknown` หรือกำหนด Type/Interface กลางไว้ที่ `types/`

```tsx
// ✅ CORRECT
function processData<T>(data: T): T { ... }
function handleError(error: unknown): void { ... }

// ❌ WRONG
function processData(data: any): any { ... }
```

### Rule 6: Guard Clauses — Early Return

**เขียน `if (!condition) return` เพื่อเคลียร์ Error ด้านบนสุดของฟังก์ชัน** ห้ามเขียน nested if/else หลายชั้น

```tsx
// ✅ CORRECT — Guard Clauses
export async function updateProfile(prevState: ApiResponse<null>, formData: FormData) {
  const session = await auth()
  if (!session?.user) return { success: false, error: 'Unauthorized' }

  const parsed = schema.safeParse({ name: formData.get('name') })
  if (!parsed.success) return { success: false, error: parsed.error.flatten().fieldErrors }

  await db.user.update({ where: { id: session.user.id }, data: parsed.data })
  revalidatePath('/profile')
  return { success: true }
}

// ❌ WRONG — Nested conditions
export async function updateProfile(prevState, formData) {
  const session = await auth()
  if (session?.user) {
    const parsed = schema.safeParse(...)
    if (parsed.success) {
      await db.user.update(...)
      return { success: true }
    } else {
      return { success: false, error: '...' }
    }
  } else {
    return { success: false, error: 'Unauthorized' }
  }
}
```

---

## 📁 Project Structure

```
src/
├── app/                    # Routing ONLY — NO business logic
│   ├── layout.tsx
│   ├── page.tsx
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── settings/page.tsx
│   └── api/
│       └── webhooks/route.ts
│
├── components/             # UI Components (props-driven, no data fetching)
│   ├── ui/                 # Atomic: Button, Input, Card (shadcn/ui)
│   ├── forms/              # Form compositions: LoginForm, SettingsForm
│   ├── layouts/            # Layout structures: Header, Sidebar, Footer
│   └── shared/             # Reusable composites: UserCard, SearchBar
│
├── lib/                    # Core libraries & configurations
│   ├── db.ts              # Database client (Prisma/Drizzle)
│   ├── auth.ts            # Auth configuration
│   ├── utils.ts           # cn() utility
│   └── constants.ts       # App-wide constants
│
├── hooks/                  # Custom React hooks (client-side only)
│   ├── use-debounce.ts
│   ├── use-media-query.ts
│   └── use-local-storage.ts
│
├── helpers/                # Pure utility functions (NO React dependency)
│   ├── format.ts          # formatDate, formatCurrency, formatNumber
│   ├── validate.ts        # Zod schemas
│   └── transform.ts       # Data transformation functions
│
├── types/                  # Centralized TypeScript definitions
│   ├── index.ts           # Shared domain types (User, Post, etc.)
│   ├── api.ts             # API response types
│   ├── database.ts        # Database model types
│   └── forms.ts           # Form state types
│
├── services/               # Data Access Layer (server-only)
│   ├── user.service.ts
│   ├── product.service.ts
│   └── dashboard.service.ts
│
├── actions/                # Server Actions (mutations only)
│   ├── auth.actions.ts
│   ├── user.actions.ts
│   └── product.actions.ts
│
└── config/                 # App configuration
    ├── site.ts            # Site metadata
    ├── navigation.ts      # Nav items
    └── dashboard.ts       # Dashboard config
```

---

## 📦 Import Order Rule (บังคับเรียงลำดับ)

```tsx
// 1. Core — React/Next.js
import { Suspense } from 'react'
import Link from 'next/link'
import Image from 'next/image'

// 2. Third-party libraries
import { z } from 'zod'

// 3. Core Shared — lib/config
import { db } from '@/lib/db'
import { siteConfig } from '@/config/site'

// 4. Services & Actions
import { getUsers } from '@/services/user.service'
import { deleteUser } from '@/actions/user.actions'

// 5. UI & Layout Components
import { Button } from '@/components/ui/button'
import { UserCard } from '@/components/shared/user-card'

// 6. Hooks & Helpers
import { useDebounce } from '@/hooks/use-debounce'
import { formatDate } from '@/helpers/format'

// 7. Types (always use `import type`)
import type { User } from '@/types'
import type { ApiResponse } from '@/types/api'
```

---

## 💻 Best Practice Code Snippets

### Thin Page Pattern

```tsx
// src/app/dashboard/page.tsx
import { getStats } from '@/services/dashboard.service'
import { DashboardContent } from '@/components/dashboard/dashboard-content'

export default async function DashboardPage() {
  const stats = await getStats()
  return <DashboardContent stats={stats} />
}
```

### Service Layer

```tsx
// src/services/user.service.ts
import 'server-only'
import { db } from '@/lib/db'
import type { User, PaginatedResponse } from '@/types'

export async function getUsers(page = 1, pageSize = 10): Promise<PaginatedResponse<User>> {
  const offset = (page - 1) * pageSize

  const [users, total] = await Promise.all([
    db.user.findMany({ skip: offset, take: pageSize, orderBy: { createdAt: 'desc' } }),
    db.user.count(),
  ])

  return {
    data: users,
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize),
  }
}

export async function getUserById(id: string): Promise<User | null> {
  try {
    if (!id) return null
    return await db.user.findUnique({ where: { id } })
  } catch (error) {
    console.error(`[UserService] Failed to fetch user with ULID ${id}:`, error)
    return null
  }
}
```

### Server Action with Guard Clauses

```tsx
// src/actions/user.actions.ts
'use server'

import { auth } from '@/lib/auth'
import { db } from '@/lib/db'
import { revalidatePath } from 'next/cache'
import { updateProfileSchema } from '@/helpers/validate'
import type { ApiResponse } from '@/types/api'

export async function updateProfile(
  prevState: ApiResponse<null>,
  formData: FormData
): Promise<ApiResponse<null>> {
  // Guard 1: Auth
  const session = await auth()
  if (!session?.user) {
    return { success: false, error: 'Unauthorized' }
  }

  // Guard 2: Validation
  const parsed = updateProfileSchema.safeParse({
    name: formData.get('name'),
    bio: formData.get('bio'),
  })
  if (!parsed.success) {
    return { success: false, error: parsed.error.flatten().fieldErrors.name?.[0] }
  }

  // Mutate
  try {
    await db.user.update({
      where: { id: session.user.id },
      data: parsed.data,
    })
    revalidatePath('/profile')
    return { success: true }
  } catch (error) {
    console.error('[UserAction] Profile update failed:', error)
    return { success: false, error: 'Internal Server Error' }
  }
}
```

### Component (Props-driven, No Fetching)

```tsx
// src/components/shared/user-card.tsx
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import type { User } from '@/types'

interface UserCardProps {
  user: User
}

export function UserCard({ user }: UserCardProps) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-lg border">
      <Avatar>
        <AvatarImage src={user.avatar} alt={user.name} />
        <AvatarFallback>{user.name[0]}</AvatarFallback>
      </Avatar>
      <div>
        <p className="font-medium">{user.name}</p>
        <p className="text-sm text-muted-foreground">{user.email}</p>
      </div>
      <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
        {user.role}
      </Badge>
    </div>
  )
}
```

### Helpers (Pure Functions)

```tsx
// src/helpers/format.ts
export function formatDate(date: string | Date, locale = 'th-TH'): string {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatCurrency(amount: number, currency = 'THB'): string {
  return new Intl.NumberFormat('th-TH', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return `${str.slice(0, length)}...`
}
```

### Validation Schemas

```tsx
// src/helpers/validate.ts
import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export const updateProfileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  bio: z.string().max(500).optional(),
})

export type LoginInput = z.infer<typeof loginSchema>
export type UpdateProfileInput = z.infer<typeof updateProfileSchema>
```

### Centralized Types

```tsx
// src/types/index.ts
export interface User {
  id: string  // ULID format
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'user' | 'editor'
  createdAt: string
  updatedAt: string
}

export interface Post {
  id: string  // ULID format
  title: string
  content: string
  slug: string
  authorId: string
  tags: string[]
  published: boolean
  createdAt: string
  updatedAt: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
```

```tsx
// src/types/api.ts
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
```

---

## ⚠️ Do & Don't (Anti-Patterns)

| ✅ Do | ❌ Don't |
|-------|---------|
| Thin Pages — `app/` ผูก Component กับ Data Source เท่านั้น | Fat Pages — fetch/query ตรงใน `page.tsx` |
| Guard Clauses — `if (!x) return` ด้านบนสุด | Nested If/Ternaries — เงื่อนไขซ้อนหลายชั้น |
| Centralized Types — ประกาศใน `types/` | Inline Types — ประกาศ type สดในพารามิเตอร์ |
| Centralized Helpers — pure functions ใน `helpers/` | Logic in Components — แปลงข้อมูลปนใน render |
| `import 'server-only'` ใน services | ลืมใส่ — server code หลุดไป client |
| `import type { X }` สำหรับ types | `import { X }` สำหรับ type-only imports |
| ULID string สำหรับ IDs | UUID, auto-increment number |
| `unknown` หรือ Generic เมื่อไม่แน่ใจ type | `any` ทุกกรณี |
| Early return + flat code | Deeply nested conditions |
| Named exports สำหรับ components | Default exports (ยกเว้น pages) |

---

## 🔄 Complete Request Flow

```
User visits /dashboard/posts
│
├── app/(dashboard)/posts/page.tsx        ← Thin Page (routing only)
│   └── calls getPosts() from services/
│   └── renders <PostList posts={posts} />
│
├── services/post.service.ts              ← Data Access (server-only)
│   └── queries database with auth check
│   └── returns typed PaginatedResponse<Post>
│
├── components/posts/post-list.tsx        ← UI (props-driven)
│   └── maps posts → <PostCard />
│   └── uses helpers/format.ts for dates
│
├── components/posts/post-card.tsx        ← UI (atomic)
│   └── renders with components/ui/*
│   └── delete button calls action
│
├── actions/post.actions.ts               ← Mutation (Server Action)
│   └── auth guard → validate → mutate → revalidate
│
├── helpers/validate.ts                   ← Pure validation (Zod)
│   └── postSchema definition
│
└── types/index.ts                        ← Type definitions
    └── Post, User, PaginatedResponse
```

---

## สรุป

1. **`app/` = routing only** — thin pages delegate ไป services + components
2. **`services/` = server-only** — data access layer, `import 'server-only'`
3. **`actions/` = mutations** — auth → validate → mutate → revalidate
4. **`components/` = UI only** — props-driven, no data fetching
5. **`hooks/` = stateful logic** — client-side encapsulation
6. **`helpers/` = pure functions** — no React dependency
7. **`types/` = centralized** — all TypeScript definitions
8. **ULID** — primary key format (ห้าม UUID/auto-increment)
9. **No `any`** — ใช้ generics, `unknown`, หรือ define types
10. **Guard Clauses** — early return, flat code, no nesting
11. **Import Order** — Core → Third-party → Internal → Types
12. **`import type`** — สำหรับ type-only imports เสมอ
