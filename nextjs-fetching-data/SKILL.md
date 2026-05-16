---
name: Next.js Fetching Data
description: Expert guidance on data fetching in Next.js App Router — Server Components, Streaming, Suspense, parallel/sequential patterns, and client-side fetching with React use API.
---

# Next.js Fetching Data

Expert guidance on data fetching in Next.js App Router — Server Components, Streaming, Suspense, parallel/sequential patterns, and client-side fetching with React use API.

@doc-version: 16.2.6

## Core Concepts

ใน App Router การดึงข้อมูลถูกออกแบบให้ทำบน Server เป็นหลัก เพราะปลอดภัยและเร็วกว่า พร้อมระบบ Streaming ที่ทยอยแสดงผลไม่ให้หน้าค้าง

## Guidelines

### 1. การดึงข้อมูลใน Server Components (แนะนำ)

Server Components รองรับ `async/await` โดยตรง:

#### ใช้ `fetch` API

```tsx
// app/posts/page.tsx (Server Component)
export default async function PostsPage() {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()

  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

#### ใช้ ORM / Database โดยตรง

```tsx
// app/users/page.tsx (Server Component)
import { db } from '@/lib/db'

export default async function UsersPage() {
  // ✅ ปลอดภัย — Code นี้รันบน Server เท่านั้น
  // API Keys และ Connection strings ไม่หลุดไป Browser
  const users = await db.user.findMany()

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

#### Memoization อัตโนมัติ

หากมีการ `fetch` ด้วย URL + options เดียวกันซ้ำในหลาย components ภายใน request เดียวกัน Next.js จะดึงข้อมูลเพียงครั้งเดียว:

```tsx
// ทั้ง 2 components เรียก fetch เดียวกัน → Next.js ดึงแค่ครั้งเดียว
// components/Header.tsx
async function Header() {
  const user = await fetch('https://api.example.com/user').then(r => r.json())
  return <h1>Hello, {user.name}</h1>
}

// components/Sidebar.tsx
async function Sidebar() {
  const user = await fetch('https://api.example.com/user').then(r => r.json())
  return <nav>Role: {user.role}</nav>
}
```

### 2. Streaming — ทยอยแสดงผลไม่ให้หน้าค้าง

#### `loading.tsx` — Loading UI สำหรับทั้งหน้า

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-8 bg-gray-200 rounded w-1/3" />
      <div className="h-4 bg-gray-200 rounded w-full" />
      <div className="h-4 bg-gray-200 rounded w-2/3" />
    </div>
  )
}
```

- แสดงอัตโนมัติระหว่างรอข้อมูลใน `page.tsx`
- ถูก Prefetch ล่วงหน้า → ผู้ใช้เห็น skeleton ทันทีที่คลิก

#### `<Suspense>` — Loading UI เฉพาะบางส่วน (Granular)

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <main>
      <h1>Dashboard</h1> {/* แสดงทันที */}

      <Suspense fallback={<div>Loading stats...</div>}>
        <Stats /> {/* รอข้อมูล → แสดง fallback ก่อน */}
      </Suspense>

      <Suspense fallback={<div>Loading chart...</div>}>
        <RevenueChart /> {/* รอข้อมูลอีกชุด → แสดง fallback แยก */}
      </Suspense>
    </main>
  )
}

async function Stats() {
  const stats = await fetch('https://api.example.com/stats').then(r => r.json())
  return <div>{stats.totalUsers} users</div>
}

async function RevenueChart() {
  const data = await fetch('https://api.example.com/revenue').then(r => r.json())
  return <div>Revenue: {data.total}</div>
}
```

**ข้อดี:** ส่วนที่เสร็จก่อนแสดงก่อน ไม่ต้องรอทุกอย่างพร้อม

### 3. การดึงข้อมูลใน Client Components

#### React `use` API — ส่ง Promise จาก Server มา Client

```tsx
// app/posts/page.tsx (Server Component)
import PostList from './PostList'

export default function PostsPage() {
  // สร้าง Promise บน Server (ไม่ await)
  const postsPromise = fetch('https://api.example.com/posts').then(r => r.json())

  return (
    <PostList postsPromise={postsPromise} />
  )
}
```

```tsx
// app/posts/PostList.tsx (Client Component)
'use client'

import { use } from 'react'

export default function PostList({ postsPromise }: { postsPromise: Promise<any[]> }) {
  // use() จะ "unwrap" Promise — ทำงานร่วมกับ Suspense
  const posts = use(postsPromise)

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

**ข้อดี:** เริ่มดึงข้อมูลบน Server ทันที แต่ Client Component เป็นคนแสดงผล (เหมาะกับ interactive lists)

#### Library ภายนอก (SWR / React Query)

```tsx
'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function LiveData() {
  const { data, error, isLoading } = useSWR('/api/live-stats', fetcher, {
    refreshInterval: 5000, // Refetch ทุก 5 วินาที
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading data</div>
  return <div>Active users: {data.activeUsers}</div>
}
```

### 4. Patterns — รูปแบบการดึงข้อมูล

#### Parallel Fetching (ดึงพร้อมกัน) — แนะนำ

```tsx
// ✅ ดึงพร้อมกัน — เร็วกว่า (เวลารวม = ตัวที่ช้าที่สุด)
async function Dashboard() {
  const [stats, revenue, users] = await Promise.all([
    fetch('https://api.example.com/stats').then(r => r.json()),
    fetch('https://api.example.com/revenue').then(r => r.json()),
    fetch('https://api.example.com/users').then(r => r.json()),
  ])

  return (
    <div>
      <StatsCard data={stats} />
      <RevenueChart data={revenue} />
      <UserList data={users} />
    </div>
  )
}
```

```
Timeline (Parallel):
stats    |████|
revenue  |██████|
users    |███|
Total:   |██████| ← เร็ว (รอแค่ตัวที่นานสุด)
```

#### Sequential Fetching (ดึงตามลำดับ) — เมื่อข้อมูลขึ้นต่อกัน

```tsx
// เมื่อ request ที่ 2 ต้องใช้ข้อมูลจาก request แรก
async function ArtistAlbums({ artistId }: { artistId: string }) {
  // ต้องรู้ artist ก่อน ถึงจะหา albums ได้
  const artist = await fetch(`/api/artists/${artistId}`).then(r => r.json())
  const albums = await fetch(`/api/artists/${artist.id}/albums`).then(r => r.json())

  return (
    <div>
      <h1>{artist.name}</h1>
      <ul>
        {albums.map((album: any) => <li key={album.id}>{album.title}</li>)}
      </ul>
    </div>
  )
}
```

**แก้ปัญหา Sequential ช้า:** ใช้ `<Suspense>` ทยอยแสดงผล

```tsx
import { Suspense } from 'react'

async function ArtistPage({ artistId }: { artistId: string }) {
  const artist = await fetch(`/api/artists/${artistId}`).then(r => r.json())

  return (
    <div>
      <h1>{artist.name}</h1> {/* แสดงทันที */}
      <Suspense fallback={<div>Loading albums...</div>}>
        <Albums artistId={artist.id} /> {/* ทยอยแสดง */}
      </Suspense>
    </div>
  )
}

async function Albums({ artistId }: { artistId: string }) {
  const albums = await fetch(`/api/artists/${artistId}/albums`).then(r => r.json())
  return <ul>{albums.map((a: any) => <li key={a.id}>{a.title}</li>)}</ul>
}
```

#### `React.cache` — Memoize ฟังก์ชันที่ไม่ใช่ fetch

```tsx
import { cache } from 'react'
import { db } from '@/lib/db'

// ✅ ถูกเรียกซ้ำใน request เดียวกัน → query แค่ครั้งเดียว
export const getUser = cache(async (userId: string) => {
  const user = await db.user.findUnique({ where: { id: userId } })
  return user
})
```

```tsx
// ใช้ใน Layout
export default async function Layout({ children }: { children: React.ReactNode }) {
  const user = await getUser('123') // query ครั้งแรก
  return <nav>{user?.name}</nav>
}

// ใช้ใน Page — ไม่ query ซ้ำ (ใช้ cache)
export default async function Page() {
  const user = await getUser('123') // ใช้ผลลัพธ์จาก cache
  return <h1>Welcome, {user?.name}</h1>
}
```

### 5. แชร์ข้อมูลระหว่าง Server และ Client

ใช้ `React.cache` + Context Provider ส่ง Promise จาก Server ไป Client ทั่วทั้งแอป:

```tsx
// lib/user.ts
import { cache } from 'react'

export const getUser = cache(async () => {
  const res = await fetch('https://api.example.com/me')
  return res.json()
})
```

```tsx
// app/layout.tsx (Server Component)
import { UserProvider } from './UserProvider'
import { getUser } from '@/lib/user'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const userPromise = getUser() // ไม่ await — ส่ง Promise ไป

  return (
    <html lang="en">
      <body>
        <UserProvider userPromise={userPromise}>
          {children}
        </UserProvider>
      </body>
    </html>
  )
}
```

```tsx
// UserProvider.tsx
'use client'

import { createContext, useContext, use } from 'react'

const UserContext = createContext<any>(null)

export function UserProvider({ userPromise, children }: { userPromise: Promise<any>; children: React.ReactNode }) {
  const user = use(userPromise)
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>
}

export function useUser() {
  return useContext(UserContext)
}
```

## Quick Reference

| วิธี | ใช้เมื่อ | ที่รัน |
|------|---------|--------|
| `await fetch()` ใน Server Component | ดึงข้อมูลทั่วไป | Server |
| `await db.query()` ใน Server Component | Query DB โดยตรง | Server |
| `Promise.all([...])` | ดึงหลายอย่างพร้อมกัน | Server |
| `<Suspense>` + async component | ทยอยแสดงผล | Server |
| `loading.tsx` | Loading UI ทั้งหน้า | Server |
| React `use(promise)` | Client ต้องแสดงข้อมูลจาก Server | Client |
| SWR / React Query | Real-time, polling, client cache | Client |
| `React.cache()` | Memoize non-fetch functions | Server |

## สรุป

1. **ดึงข้อมูลบน Server เป็นหลัก** → ปลอดภัย, เร็ว, ไม่ส่ง secrets ไป browser
2. **ใช้ `Promise.all`** → โหลดข้อมูลพร้อมกัน ลดเวลารวม
3. **ใช้ `loading.tsx` หรือ `<Suspense>`** → ผู้ใช้ไม่ต้องรอนาน เห็น UI ทันที
4. **Memoization อัตโนมัติ** → fetch เดียวกันซ้ำไม่เปลือง
5. **ใช้ `React.cache`** → สำหรับ ORM/DB ที่ไม่ใช่ fetch
6. **ส่ง Promise ไป Client ด้วย `use()`** → เมื่อต้องการ interactivity
