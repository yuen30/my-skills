---
name: Next.js CSS-in-JS
description: Expert guidance on using CSS-in-JS libraries with Next.js App Router — styled-components, styled-jsx, style registry pattern, and supported libraries.
---

# Next.js CSS-in-JS

Expert guidance on using CSS-in-JS libraries with Next.js App Router — styled-components, styled-jsx, style registry pattern, and supported libraries.

@doc-version: 16.2.6

## Core Concepts

CSS-in-JS ใน App Router ต้องใช้ **Client Components** และ pattern 3 ขั้นตอน:
1. **Style registry** — collect CSS rules ระหว่าง render
2. **`useServerInsertedHTML`** hook — inject rules ก่อน content
3. **Client Component wrapper** — หุ้มแอปด้วย registry ตอน SSR

> CSS-in-JS ต้องการ library ที่รองรับ React concurrent rendering

## Supported Libraries

| Library | Status |
|---------|--------|
| `styled-components` | ✅ Supported |
| `styled-jsx` | ✅ Supported (built-in) |
| `ant-design` | ✅ Supported |
| `chakra-ui` | ✅ Supported |
| `@mui/material` / `@mui/joy` | ✅ Supported |
| `@fluentui/react-components` | ✅ Supported |
| `kuma-ui` | ✅ Supported |
| `pandacss` | ✅ Supported |
| `stylex` | ✅ Supported |
| `tamagui` | ✅ Supported |
| `tss-react` | ✅ Supported |
| `vanilla-extract` | ✅ Supported |
| `emotion` | 🔄 Working on support |

## Guidelines

### 1. styled-components

#### Enable in next.config.js

```js
// next.config.js
module.exports = {
  compiler: {
    styledComponents: true,
  },
}
```

#### Create Style Registry

```tsx
// lib/registry.tsx
'use client'

import React, { useState } from 'react'
import { useServerInsertedHTML } from 'next/navigation'
import { ServerStyleSheet, StyleSheetManager } from 'styled-components'

export default function StyledComponentsRegistry({
  children,
}: {
  children: React.ReactNode
}) {
  // Only create stylesheet once with lazy initial state
  const [styledComponentsStyleSheet] = useState(() => new ServerStyleSheet())

  useServerInsertedHTML(() => {
    const styles = styledComponentsStyleSheet.getStyleElement()
    styledComponentsStyleSheet.instance.clearTag()
    return <>{styles}</>
  })

  if (typeof window !== 'undefined') return <>{children}</>

  return (
    <StyleSheetManager sheet={styledComponentsStyleSheet.instance}>
      {children}
    </StyleSheetManager>
  )
}
```

#### Wrap Root Layout

```tsx
// app/layout.tsx
import StyledComponentsRegistry from './lib/registry'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <StyledComponentsRegistry>{children}</StyledComponentsRegistry>
      </body>
    </html>
  )
}
```

#### Usage

```tsx
// app/page.tsx (or any Client Component)
'use client'

import styled from 'styled-components'

const Title = styled.h1`
  color: red;
  font-size: 2rem;
`

const Button = styled.button<{ $primary?: boolean }>`
  background: ${(props) => (props.$primary ? '#007bff' : 'white')};
  color: ${(props) => (props.$primary ? 'white' : '#007bff')};
  padding: 0.5rem 1rem;
  border: 2px solid #007bff;
  border-radius: 4px;
`

export default function Page() {
  return (
    <div>
      <Title>Hello styled-components</Title>
      <Button $primary>Primary</Button>
      <Button>Secondary</Button>
    </div>
  )
}
```

### 2. styled-jsx

#### Create Style Registry

```tsx
// app/registry.tsx
'use client'

import React, { useState } from 'react'
import { useServerInsertedHTML } from 'next/navigation'
import { StyleRegistry, createStyleRegistry } from 'styled-jsx'

export default function StyledJsxRegistry({ children }: { children: React.ReactNode }) {
  const [jsxStyleRegistry] = useState(() => createStyleRegistry())

  useServerInsertedHTML(() => {
    const styles = jsxStyleRegistry.styles()
    jsxStyleRegistry.flush()
    return <>{styles}</>
  })

  return <StyleRegistry registry={jsxStyleRegistry}>{children}</StyleRegistry>
}
```

#### Wrap Root Layout

```tsx
// app/layout.tsx
import StyledJsxRegistry from './registry'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <StyledJsxRegistry>{children}</StyledJsxRegistry>
      </body>
    </html>
  )
}
```

#### Usage

```tsx
// app/page.tsx (Client Component)
'use client'

export default function Page() {
  return (
    <div>
      <h1 className="title">Hello styled-jsx</h1>
      <style jsx>{`
        .title {
          color: red;
          font-size: 2rem;
        }
      `}</style>
    </div>
  )
}
```

### 3. General Pattern (Any CSS-in-JS Library)

```tsx
// lib/style-registry.tsx
'use client'

import { useState } from 'react'
import { useServerInsertedHTML } from 'next/navigation'

export default function StyleRegistry({ children }: { children: React.ReactNode }) {
  // 1. Create style sheet/registry (lazy initial state)
  const [sheet] = useState(() => createYourLibrarySheet())

  // 2. Inject collected styles into HTML head
  useServerInsertedHTML(() => {
    const styles = sheet.getStyles()
    sheet.flush()
    return <>{styles}</>
  })

  // 3. Wrap children with provider (server only)
  if (typeof window !== 'undefined') return <>{children}</>

  return (
    <YourLibraryProvider sheet={sheet}>
      {children}
    </YourLibraryProvider>
  )
}
```

## How It Works

```
Server Rendering:
1. Registry collects CSS rules during render
2. useServerInsertedHTML injects styles into <head>
3. HTML sent to client with styles already in place

Client Hydration:
4. Library takes over and manages dynamic styles
5. No flash of unstyled content (FOUC)

Streaming:
6. Styles from each chunk collected and appended
7. Works with React Suspense boundaries
```

## Important Notes

- **Client Components only** — CSS-in-JS ใช้ได้เฉพาะใน Client Components
- **Style registry ที่ top level** — efficient กว่า, ไม่ re-generate styles ทุก server render
- **ไม่ส่งใน Server Component payload** — styles ถูก extract แยก
- **`typeof window !== 'undefined'`** — skip provider บน client (hydration แล้ว)

## Recommendation

สำหรับ Next.js App Router แนะนำ:

| Priority | Approach | Reason |
|----------|----------|--------|
| 1st | Tailwind CSS | Zero runtime, Server Components compatible |
| 2nd | CSS Modules | Scoped, no runtime, Server Components compatible |
| 3rd | CSS-in-JS (styled-components, etc.) | Client Components only, runtime cost |

> **ถ้าเป็นไปได้** ใช้ Tailwind CSS หรือ CSS Modules — ทำงานกับ Server Components ได้โดยไม่ต้อง client boundary

## Quick Reference

| Library | Config Required | Registry Pattern |
|---------|:-:|:-:|
| styled-components | `compiler.styledComponents: true` | ✅ |
| styled-jsx | ไม่ต้อง (built-in) | ✅ |
| MUI | ดู MUI docs | ✅ |
| Chakra UI | ดู Chakra docs | ✅ |
| vanilla-extract | ไม่ต้อง (build-time) | ❌ |
| Panda CSS | ไม่ต้อง (build-time) | ❌ |

## สรุป

1. **CSS-in-JS ใช้ได้เฉพาะ Client Components** — ต้อง `'use client'`
2. **3 ขั้นตอน:** style registry → `useServerInsertedHTML` → wrap root layout
3. **styled-components:** เปิด `compiler.styledComponents` + registry
4. **styled-jsx:** built-in, ต้อง registry สำหรับ App Router
5. **แนะนำ Tailwind/CSS Modules** ถ้าไม่จำเป็นต้องใช้ CSS-in-JS
6. **Build-time CSS-in-JS** (vanilla-extract, Panda CSS) ไม่ต้อง registry
