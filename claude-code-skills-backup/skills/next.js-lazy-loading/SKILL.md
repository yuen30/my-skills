---
name: Next.js Lazy Loading
description: Expert guidance on lazy loading in Next.js — next/dynamic, React.lazy, code splitting, SSR skip, external libraries, and magic comments.
---

# Next.js Lazy Loading

Expert guidance on lazy loading in Next.js — next/dynamic, React.lazy, code splitting, SSR skip, external libraries, and magic comments.

@doc-version: 16.2.6

## Core Concepts

Lazy loading ลด JavaScript ที่ต้องโหลดตอนแรก — defer loading Client Components และ libraries จนกว่าจะต้องใช้จริง

**2 วิธี:**
1. `next/dynamic` — composite ของ `React.lazy()` + `Suspense`
2. `React.lazy()` + `Suspense` — React native API

> Server Components ถูก code split อัตโนมัติ + ใช้ streaming — lazy loading ใช้กับ **Client Components** เท่านั้น

## Guidelines

### 1. Dynamic Import Client Components

```tsx
'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'

// Load ทันที แต่แยก bundle
const ComponentA = dynamic(() => import('../components/A'))

// Load เมื่อ condition เป็น true
const ComponentB = dynamic(() => import('../components/B'))

// Load เฉพาะ client-side (ไม่ SSR)
const ComponentC = dynamic(() => import('../components/C'), { ssr: false })

export default function Page() {
  const [showMore, setShowMore] = useState(false)

  return (
    <div>
      <ComponentA />
      {showMore && <ComponentB />}
      <button onClick={() => setShowMore(!showMore)}>Toggle</button>
      <ComponentC />
    </div>
  )
}
```

### 2. Skip SSR (`ssr: false`)

สำหรับ components ที่ใช้ browser-only APIs:

```tsx
'use client'

import dynamic from 'next/dynamic'

// ไม่ render บน server — เฉพาะ client
const MapComponent = dynamic(() => import('../components/Map'), {
  ssr: false,
})

const ChartComponent = dynamic(() => import('../components/Chart'), {
  ssr: false,
  loading: () => <div className="h-64 animate-pulse bg-gray-200" />,
})

export default function Dashboard() {
  return (
    <div>
      <MapComponent />
      <ChartComponent />
    </div>
  )
}
```

> **สำคัญ:** `ssr: false` ใช้ได้เฉพาะใน **Client Components** — ใช้ใน Server Components จะ error

### 3. Custom Loading Component

```tsx
'use client'

import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('../components/HeavyComponent'), {
  loading: () => (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/3 mb-4" />
      <div className="h-4 bg-gray-200 rounded w-full mb-2" />
      <div className="h-4 bg-gray-200 rounded w-2/3" />
    </div>
  ),
})

export default function Page() {
  return <HeavyComponent />
}
```

### 4. Named Exports

```tsx
// components/hello.tsx
'use client'

export function Hello() {
  return <p>Hello!</p>
}

export function Goodbye() {
  return <p>Goodbye!</p>
}
```

```tsx
// app/page.tsx
import dynamic from 'next/dynamic'

// Import specific named export
const Hello = dynamic(() =>
  import('../components/hello').then((mod) => mod.Hello)
)

const Goodbye = dynamic(() =>
  import('../components/hello').then((mod) => mod.Goodbye)
)
```

### 5. Dynamic Import Server Components

Server Component ตัวเองไม่ถูก lazy-load แต่ **children Client Components** จะถูก lazy-load:

```tsx
// app/page.tsx (Server Component)
import dynamic from 'next/dynamic'

const ServerComponent = dynamic(() => import('../components/ServerComponent'))

export default function Page() {
  return (
    <div>
      <ServerComponent />
    </div>
  )
}
```

- ช่วย preload static assets (CSS) เมื่อใช้ใน Server Components
- ❌ `ssr: false` ใช้ใน Server Components ไม่ได้

### 6. Loading External Libraries On-demand

```tsx
'use client'

import { useState } from 'react'

export default function SearchPage() {
  const [results, setResults] = useState<any[]>()

  return (
    <div>
      <input
        type="text"
        placeholder="Search"
        onChange={async (e) => {
          const { value } = e.currentTarget

          // Load fuse.js เฉพาะเมื่อ user พิมพ์
          const Fuse = (await import('fuse.js')).default
          const fuse = new Fuse(['Tim', 'Joe', 'Bel', 'Lee'])

          setResults(fuse.search(value))
        }}
      />
      <pre>{JSON.stringify(results, null, 2)}</pre>
    </div>
  )
}
```

#### Other Examples

```tsx
// Load heavy library on button click
async function handleExport() {
  const xlsx = await import('xlsx')
  const workbook = xlsx.utils.book_new()
  // ...
}

// Load date library when needed
async function formatDate(date: Date) {
  const { format } = await import('date-fns')
  return format(date, 'PPP')
}

// Load markdown parser on demand
async function renderMarkdown(content: string) {
  const { marked } = await import('marked')
  return marked(content)
}
```

### 7. React.lazy() + Suspense (Alternative)

```tsx
'use client'

import { lazy, Suspense } from 'react'

const LazyComponent = lazy(() => import('../components/LazyComponent'))

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  )
}
```

### 8. Magic Comments

#### `webpackIgnore` / `turbopackIgnore`

Skip bundling — import เกิดตอน runtime:

```ts
// Module ไม่ถูก bundle — import ตอน runtime
const runtime = await import(/* webpackIgnore: true */ 'runtime-module')

// Turbopack variant
const plugin = await import(/* turbopackIgnore: true */ pluginPath)
```

#### `turbopackOptional` (Turbopack only)

Suppress build errors เมื่อ module อาจไม่มี:

```ts
// ไม่ error ตอน build ถ้า module ไม่มี
// แต่ throw ตอน runtime ถ้า execute
const feature = await import(/* turbopackOptional: true */ './optional-feature')
```

**Use cases:**
- Conditional features ที่อาจไม่ได้ install
- Plugin systems
- Gradual migrations

## Patterns

### Modal (Load on Open)

```tsx
'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'

const Modal = dynamic(() => import('../components/Modal'))

export default function Page() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>
      {isOpen && <Modal onClose={() => setIsOpen(false)} />}
    </div>
  )
}
```

### Tab Content (Load on Switch)

```tsx
'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'

const tabs = {
  overview: dynamic(() => import('./tabs/Overview')),
  analytics: dynamic(() => import('./tabs/Analytics')),
  settings: dynamic(() => import('./tabs/Settings')),
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<keyof typeof tabs>('overview')
  const TabContent = tabs[activeTab]

  return (
    <div>
      <nav>
        {Object.keys(tabs).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab as any)}>
            {tab}
          </button>
        ))}
      </nav>
      <TabContent />
    </div>
  )
}
```

## Quick Reference

| Method | Use Case | SSR |
|--------|----------|:---:|
| `dynamic(() => import(...))` | Client Components | ✅ (default) |
| `dynamic(..., { ssr: false })` | Browser-only components | ❌ |
| `dynamic(..., { loading })` | Custom loading UI | ✅ |
| `await import('lib')` | External libraries on-demand | N/A |
| `React.lazy()` + `Suspense` | React native alternative | ✅ |

| Magic Comment | Purpose |
|--------------|---------|
| `webpackIgnore: true` | Skip bundling (runtime import) |
| `turbopackIgnore: true` | Skip bundling (Turbopack) |
| `turbopackOptional: true` | Suppress error if module missing |

## สรุป

1. **`next/dynamic`** — lazy load Client Components (แยก bundle)
2. **`ssr: false`** — เฉพาะ client-side (browser APIs)
3. **`loading` option** — custom skeleton/spinner
4. **`await import('lib')`** — load libraries on-demand (event-driven)
5. **Server Components** — auto code split (ไม่ต้อง lazy load)
6. **Named exports** — `.then((mod) => mod.ComponentName)`
7. **Magic comments** — control bundler behavior
