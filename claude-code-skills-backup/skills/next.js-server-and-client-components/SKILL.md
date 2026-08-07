---
name: Next.js Server and Client Components
description: Expert guidance on when and how to use Server Components vs Client Components in Next.js App Router, including interleaving patterns, hydration, and best practices.
---

# Next.js Server and Client Components

Expert guidance on when and how to use Server Components vs Client Components in Next.js App Router, including interleaving patterns, hydration, and best practices.

@doc-version: 16.2.6

## Core Concepts

ใน Next.js App Router คอมโพเนนต์แบ่งเป็น 2 ประเภทตามสภาพแวดล้อมที่รัน:

- **Server Components** (default) — รันบนเซิร์ฟเวอร์เท่านั้น
- **Client Components** (`"use client"`) — รันบนเบราว์เซอร์ (และ server สำหรับ SSR)

## Guidelines

### 1. เมื่อไหร่ควรใช้คอมโพเนนต์ไหน?

| ฟีเจอร์ที่ต้องการ | Server | Client |
|:---|:---:|:---:|
| ดึงข้อมูลจาก Database/API | ✅ | ❌ |
| เก็บความลับ (API Keys, Tokens) | ✅ | ❌ |
| ลดขนาด JavaScript ที่ส่งไป Browser | ✅ | ❌ |
| เข้าถึง Backend resources โดยตรง | ✅ | ❌ |
| การโต้ตอบ (State, Event Handlers เช่น `onClick`) | ❌ | ✅ |
| ใช้ Hooks (`useEffect`, `useState`, `useReducer`) | ❌ | ✅ |
| ใช้ Browser APIs (`window`, `localStorage`, `navigator`) | ❌ | ✅ |
| ใช้ Custom Hooks ที่มี state/effects | ❌ | ✅ |

**กฎง่ายๆ:** ทุกอย่างเป็น Server Component เป็นค่าเริ่มต้น → เพิ่ม `"use client"` เฉพาะจุดที่ต้องโต้ตอบ

### 2. กลไกการทำงาน (Rendering Flow)

#### ฝั่งเซิร์ฟเวอร์:
1. เรนเดอร์ Server Components เป็น **RSC Payload** (โครงสร้างข้อมูลพิเศษ)
2. ใช้ RSC Payload + Client Components สร้าง HTML ล่วงหน้า (Prerender)
3. ส่ง HTML + RSC Payload + JS Bundle ไปเบราว์เซอร์

#### ฝั่งไคลเอนต์ (First Load):
1. แสดง HTML ทันที (เห็นหน้าเว็บเร็ว แต่ยังกดไม่ได้)
2. **Hydration** — นำ JavaScript มาทำให้ HTML โต้ตอบได้
3. Client Components พร้อมใช้งาน (กดปุ่ม, พิมพ์ input ได้)

#### การเปลี่ยนหน้า (Navigation):
- RSC Payload ถูก Prefetch ล่วงหน้า
- เปลี่ยนหน้าทันทีโดยไม่โหลด HTML ใหม่ทั้งก้อน
- อัปเดตเฉพาะ segment ที่เปลี่ยน

### 3. การใช้ `"use client"`

ใส่ไว้ **บรรทัดแรกสุด** ของไฟล์:

```tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  )
}
```

**กฎสำคัญ:** เมื่อไฟล์ใดมี `"use client"` → ไฟล์อื่นๆ ที่ถูก import เข้ามาในไฟล์นั้นจะกลายเป็น Client Component ทั้งหมดโดยอัตโนมัติ

```
"use client" ← boundary
├── ComponentA (client) ← import อะไรเข้ามาก็เป็น client หมด
│   ├── ComponentB (client)
│   └── ComponentC (client)
```

ไม่จำเป็นต้องใส่ `"use client"` ทุกไฟล์ — ใส่แค่ที่ "ขอบเขต" (boundary) ที่ต้องการ

### 4. การใช้ Server และ Client Components ร่วมกัน (Interleaving)

#### ❌ วิธีที่ผิด — Import Server Component ใน Client Component โดยตรง

```tsx
'use client'

// ❌ ห้ามทำแบบนี้!
import ServerComponent from './ServerComponent'

export default function ClientComponent() {
  return (
    <div>
      <ServerComponent /> {/* จะกลายเป็น Client Component! */}
    </div>
  )
}
```

#### ✅ วิธีที่ถูกต้อง — ส่งผ่าน `children` props

```tsx
// app/page.tsx (Server Component)
import ClientWrapper from './ClientWrapper'
import ServerContent from './ServerContent'

export default function Page() {
  return (
    <ClientWrapper>
      <ServerContent /> {/* ✅ เรนเดอร์บน server แล้วส่งผลลัพธ์มาวางใน slot */}
    </ClientWrapper>
  )
}
```

```tsx
// ClientWrapper.tsx
'use client'

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && children} {/* ✅ Server Component ถูกวางตรงนี้ */}
    </div>
  )
}
```

```tsx
// ServerContent.tsx (Server Component — ไม่มี "use client")
export default async function ServerContent() {
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()
  return <p>{json.message}</p>
}
```

**หลักการ:** Server Component ถูกเรนเดอร์บน server เสร็จก่อน → ส่งผลลัพธ์มาวางใน "ช่องว่าง" (slot) ของ Client Component

### 5. Context Providers

Context ใช้ State → ต้องเป็น Client Component:

```tsx
// providers.tsx
'use client'

import { createContext, useContext, useState } from 'react'

const ThemeContext = createContext<'light' | 'dark'>('light')

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  return (
    <ThemeContext.Provider value={theme}>
      {children} {/* ✅ children ยังเป็น Server Component ได้ */}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  return useContext(ThemeContext)
}
```

```tsx
// app/layout.tsx (Server Component)
import { ThemeProvider } from './providers'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          {children} {/* ✅ pages ภายในยังเป็น Server Component */}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**แนะนำ:** วาง Provider ไว้ที่ Layout และหุ้มแค่ `{children}` — ไม่ทำให้ทุกอย่างกลายเป็น Client

### 6. ป้องกันการรั่วไหลด้วย `server-only`

ใช้แพ็กเกจ `server-only` ป้องกันการเผลอ import code ฝั่ง server เข้าไปใน client:

```bash
npm install server-only
```

```tsx
// lib/secrets.ts
import 'server-only'

export function getSecretKey() {
  return process.env.SECRET_API_KEY
}
```

หากมีการ import `lib/secrets.ts` ในไฟล์ที่เป็น Client Component → **Build จะ Error ทันที** ป้องกันการรั่วไหลของ API Keys

### 7. Serialization — ข้อมูลที่ส่งข้าม Boundary

ข้อมูลที่ส่งจาก Server → Client ผ่าน props ต้อง **Serializable**:

```tsx
// ✅ ส่งได้
<ClientComp
  name="hello"           // string
  count={42}             // number
  items={['a', 'b']}    // array
  config={{ key: 'val' }} // plain object
  createdAt={new Date()} // Date
/>

// ❌ ส่งไม่ได้
<ClientComp
  onClick={() => {}}     // function
  ref={myRef}            // ref
  classInstance={obj}    // class instance
/>
```

## Pattern: ลดขนาด Client Bundle

แยก interactive ส่วนเล็กๆ ออกมาเป็น Client Component:

```tsx
// app/page.tsx (Server Component — ไม่ส่ง JS ไป browser)
import SearchButton from './SearchButton'

export default async function Navbar() {
  const user = await getUser()

  return (
    <nav>
      <h1>My App</h1>           {/* Server — ไม่มี JS */}
      <span>{user.name}</span>  {/* Server — ไม่มี JS */}
      <SearchButton />          {/* Client — เฉพาะส่วนนี้ส่ง JS */}
    </nav>
  )
}
```

```tsx
// SearchButton.tsx
'use client'

import { useState } from 'react'

export default function SearchButton() {
  const [query, setQuery] = useState('')
  return <input value={query} onChange={(e) => setQuery(e.target.value)} />
}
```

## Quick Reference

| หัวข้อ | Server Component | Client Component |
|--------|:---:|:---:|
| ค่าเริ่มต้น | ✅ (default) | ต้องใส่ `"use client"` |
| รันที่ | Server only | Server (SSR) + Client |
| ส่ง JS ไป browser | ❌ ไม่ส่ง | ✅ ส่ง |
| ใช้ `async/await` ใน component | ✅ | ❌ |
| เข้าถึง Database/Secrets | ✅ | ❌ |
| ใช้ State/Effects/Events | ❌ | ✅ |
| ใช้ Browser APIs | ❌ | ✅ |

## สรุป

1. **Default = Server Component** → เร็วกว่า, ปลอดภัยกว่า, JS น้อยกว่า
2. **เพิ่ม `"use client"` เฉพาะจุดที่ต้องโต้ตอบ** → ลด bundle size
3. **ส่ง Server Component เข้า Client ผ่าน `children`** → ไม่ใช่ import โดยตรง
4. **ใช้ `server-only`** → ป้องกันความลับรั่วไหล
5. **Props ข้าม boundary ต้อง serializable** → ไม่ส่ง function ได้
