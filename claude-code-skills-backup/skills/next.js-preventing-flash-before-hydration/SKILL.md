---
name: Next.js Preventing Flash Before Hydration
description: Expert guidance on preventing visible flash when hydrating — inline scripts for dates, themes, persisted state, and suppressHydrationWarning.
---

# Next.js Preventing Flash Before Hydration

Expert guidance on preventing visible flash when hydrating — inline scripts for dates, themes, persisted state, and suppressHydrationWarning.

@doc-version: 16.2.6

## Core Concepts

Server ไม่มี access ถึง user preferences (locale, timezone, theme, localStorage) — render ด้วย default แล้ว client ต้อง correct ก่อน user เห็น

**ปัญหา:**
- Client Component re-render → hydration error
- `useEffect` → flash (user เห็น server value ก่อน)
- Server-only → ไม่ได้ client-specific formatting

**Solution:** Inline `<script>` ที่รัน synchronously ระหว่าง HTML parsing — **ก่อน first paint**

## Guidelines

### 1. Dates and Formatting

#### Problem

```tsx
// ❌ Hydration error — server locale ≠ client locale
'use client'
export function EventDate({ date }: { date: string }) {
  return <p>{new Date(date).toLocaleDateString()}</p>
}
```

#### Solution: Inline Script

```tsx
// app/events/page.tsx (Server Component)
import { getEvent } from '@/app/lib/events'

export default async function Page() {
  const event = await getEvent('nextjs-conf')

  return (
    <section>
      <h1>{event.name}</h1>
      <p id="event-date" suppressHydrationWarning>
        {new Date(event.date).toLocaleDateString()}
      </p>
      <script
        dangerouslySetInnerHTML={{
          __html: `document.getElementById("event-date").textContent=new Date("${event.date}").toLocaleDateString()`,
        }}
      />
    </section>
  )
}
```

#### Reusable Component (Hard + Soft Navigation)

```tsx
// app/components/inline-script.tsx
export function InlineScript({ html }: { html: string }) {
  return (
    <script
      type={typeof window === 'undefined' ? 'text/javascript' : 'text/plain'}
      suppressHydrationWarning
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
```

```tsx
// app/components/local-date.tsx
'use client'

import { useId } from 'react'
import { InlineScript } from './inline-script'

export function LocalDate({
  date,
  options,
}: {
  date: string
  options?: Intl.DateTimeFormatOptions
}) {
  const id = useId()

  return (
    <>
      <time id={id} dateTime={date} suppressHydrationWarning>
        {new Date(date).toLocaleDateString(undefined, options)}
      </time>
      <InlineScript
        html={`{var n=document.getElementById("${id}");if(n)n.textContent=new Date("${date}").toLocaleDateString(undefined,${JSON.stringify(options)})}`}
      />
    </>
  )
}
```

**How it works:**
- **Hard navigation:** script executes during HTML parsing → corrects date
- **Client navigation:** `toLocaleDateString()` runs in browser (Client Component)
- **Script type:** `text/javascript` on server (executes), `text/plain` on client (ignored)

### 2. Theme (Dark/Light Mode)

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="light" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem("theme");if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){}})()`,
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

```css
/* app/globals.css */
[data-theme='light'] {
  --background: #ffffff;
  --foreground: #000000;
}

[data-theme='dark'] {
  --background: #0a0a0a;
  --foreground: #ededed;
}
```

- Script ใน `<head>` → รันก่อน content paint
- `try/catch` → handle localStorage unavailable
- ไม่มี flash ระหว่าง light → dark

### 3. Persisted UI State (Accordion/Tabs)

Sync inline script กับ React state ด้วย **lazy state initializer**:

```tsx
'use client'

import { useState, useCallback } from 'react'
import { InlineScript } from './inline-script'

const STORAGE_KEY = 'open-section'
const DEFAULT_ID = 'setup'

export function Accordion() {
  // Lazy initializer อ่านจาก localStorage (เหมือน inline script)
  const [openId, setOpenId] = useState(() => {
    if (typeof window === 'undefined') return DEFAULT_ID
    return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_ID
  })

  const handleToggle = useCallback(
    (id: string) => (e: React.ToggleEvent<HTMLDetailsElement>) => {
      if (e.newState === 'open') {
        setOpenId(id)
        localStorage.setItem(STORAGE_KEY, id)
      }
    },
    []
  )

  return (
    <div>
      <details id="section-setup" open={openId === 'setup'} onToggle={handleToggle('setup')}>
        <summary>Setup</summary>
        <p>Content...</p>
      </details>
      {/* more sections */}

      <InlineScript
        html={`{var id=localStorage.getItem("${STORAGE_KEY}")??"${DEFAULT_ID}";["setup","usage","deploy"].forEach(function(s){var el=document.getElementById("section-"+s);if(el){if(s===id)el.setAttribute("open","");else el.removeAttribute("open")}})}`}
      />
    </div>
  )
}
```

**Key:** Inline script + lazy `useState` ทั้งคู่อ่านจาก localStorage → always agree → no mismatch

### 4. `suppressHydrationWarning` Explained

| Without | With |
|---------|------|
| React detects mismatch → hydration error | React keeps DOM as-is (DOM wins) |
| Client-renders from nearest boundary | Discards client output for that element |
| Inline script corrections on other elements lost | Corrections preserved |

**ใช้เมื่อ:** Inline script เปลี่ยน DOM ก่อน React hydrate — บอก React ให้ accept DOM

### 5. When to Use Other Approaches

| Situation | Approach |
|-----------|----------|
| Date depends on request data (cookies/headers) | `headers()` / `cookies()` server-side |
| Live updates (countdown, clock) | Client Component + `useEffect` + `suppressHydrationWarning` |
| Page already fully dynamic | Format with `Accept-Language` header |
| Multi-language content | Internationalization (per-locale builds) |

### Why Not `useEffect`?

```
Timeline:
HTML arrives → Browser paints server value → React loads → Hydrates → useEffect → Correction
                    ↑ FLASH HERE ↑

With inline script:
HTML arrives → Script corrects DOM → Browser paints correct value → React hydrates
                                          ↑ NO FLASH ↑
```

- `useEffect` = after hydration + paint → user sees server value first
- `useLayoutEffect` = after hydration, before paint → still flash on slow connections
- **Inline script** = during HTML parsing → before any paint

## Quick Reference

| Pattern | Use Case | Key Points |
|---------|----------|------------|
| Date formatting | Locale/timezone mismatch | `toLocaleDateString()` in script |
| Theme | Dark/light mode | Script in `<head>`, `data-theme` attribute |
| Persisted state | Accordion, tabs from localStorage | Lazy `useState` + inline script |
| Reusable component | Multiple instances | `useId()` + `InlineScript` helper |

| Requirement | Detail |
|-------------|--------|
| `suppressHydrationWarning` | On elements modified by script |
| `dangerouslySetInnerHTML` | For inline script content |
| CSP with nonces | Required if strict CSP (no `'unsafe-inline'`) |
| `try/catch` in scripts | Handle localStorage unavailable |

## สรุป

1. **Inline `<script>`** รัน synchronously ก่อน first paint — ไม่มี flash
2. **`suppressHydrationWarning`** บอก React ให้ accept DOM ที่ script แก้ไข
3. **Dates:** `toLocaleDateString()` ใน script + `<time dateTime>`
4. **Theme:** script ใน `<head>` อ่าน localStorage → set `data-theme`
5. **Persisted state:** lazy `useState` + inline script อ่านจาก source เดียวกัน
6. **Reusable:** `InlineScript` helper + `useId()` สำหรับ multiple instances
7. **`useEffect` ไม่พอ** — flash ก่อน hydration บน slow connections
