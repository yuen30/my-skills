---
name: Next.js Font Optimization
description: Expert guidance on optimizing fonts in Next.js using next/font — Google Fonts self-hosting, local fonts, variable fonts, and zero layout shift.
---

# Next.js Font Optimization

Expert guidance on optimizing fonts in Next.js using next/font — Google Fonts self-hosting, local fonts, variable fonts, and zero layout shift.

@doc-version: 16.2.6

## Core Concepts

`next/font` ทำให้ fonts ถูก optimize อัตโนมัติ:
- **Self-hosting** — fonts ถูก serve จาก domain เดียวกับแอป (ไม่ request ไป Google)
- **Zero layout shift** — ไม่มี CLS จากการโหลด font
- **Privacy** — ไม่มี external network requests ไปยัง font providers
- **Performance** — fonts ถูก include เป็น static assets

## Guidelines

### 1. Google Fonts (แนะนำ)

Import font จาก `next/font/google` — self-host อัตโนมัติ:

#### Variable Font (แนะนำ — ดีที่สุด)

```tsx
// app/layout.tsx
import { Geist } from 'next/font/google'

const geist = Geist({
  subsets: ['latin'],
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={geist.className}>
      <body>{children}</body>
    </html>
  )
}
```

#### Non-variable Font (ต้องระบุ weight)

```tsx
// app/layout.tsx
import { Roboto } from 'next/font/google'

const roboto = Roboto({
  weight: '400',
  subsets: ['latin'],
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={roboto.className}>
      <body>{children}</body>
    </html>
  )
}
```

#### หลาย Weights

```tsx
import { Roboto } from 'next/font/google'

const roboto = Roboto({
  weight: ['400', '500', '700'],
  subsets: ['latin'],
})
```

#### หลาย Fonts

```tsx
import { Inter, Roboto_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  variable: '--font-roboto-mono',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

### 2. Local Fonts

ใช้ `next/font/local` สำหรับ font files ที่เก็บในโปรเจกต์:

#### Single File

```tsx
// app/layout.tsx
import localFont from 'next/font/local'

const myFont = localFont({
  src: './my-font.woff2',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={myFont.className}>
      <body>{children}</body>
    </html>
  )
}
```

#### Multiple Files (Font Family)

```tsx
import localFont from 'next/font/local'

const roboto = localFont({
  src: [
    {
      path: './Roboto-Regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './Roboto-Italic.woff2',
      weight: '400',
      style: 'italic',
    },
    {
      path: './Roboto-Bold.woff2',
      weight: '700',
      style: 'normal',
    },
    {
      path: './Roboto-BoldItalic.woff2',
      weight: '700',
      style: 'italic',
    },
  ],
})
```

> Path ถูก resolve relative to ไฟล์ที่เรียก `localFont` — เก็บ fonts ไว้ที่ไหนก็ได้ (`public`, `app/fonts/`, etc.)

### 3. CSS Variable (ใช้กับ Tailwind)

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter', // สร้าง CSS variable
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
```

ใช้ใน Tailwind CSS:

```css
/* app/globals.css */
@import 'tailwindcss';

@theme {
  --font-sans: var(--font-inter);
}
```

### 4. Scoped Fonts (เฉพาะบาง Component)

Fonts ถูก scope ตาม component ที่ใช้:

```tsx
// app/page.tsx
import { Playfair_Display } from 'next/font/google'

const playfair = Playfair_Display({
  subsets: ['latin'],
})

export default function Page() {
  return (
    <div>
      <h1 className={playfair.className}>Beautiful Heading</h1>
      <p>This paragraph uses the default font</p>
    </div>
  )
}
```

### 5. Font Options

```tsx
const font = Font({
  subsets: ['latin'],           // Required: character subsets
  weight: ['400', '700'],      // Required for non-variable fonts
  style: ['normal', 'italic'], // Optional: font styles
  variable: '--font-name',     // Optional: CSS variable name
  display: 'swap',             // Optional: font-display (default: 'swap')
  preload: true,               // Optional: preload font (default: true)
  fallback: ['system-ui'],     // Optional: fallback fonts
  adjustFontFallback: true,    // Optional: adjust fallback metrics (default: true)
})
```

## Common Patterns

### App-wide Font (Root Layout)

```tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  )
}
```

### Heading + Body Fonts

```tsx
import { Inter, Playfair_Display } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-body',
})

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-heading',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="font-body">{children}</body>
    </html>
  )
}
```

```css
/* globals.css */
@import 'tailwindcss';

@theme {
  --font-body: var(--font-body);
  --font-heading: var(--font-heading);
}
```

### Monospace for Code

```tsx
import { JetBrains_Mono } from 'next/font/google'

const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
})
```

## Quick Reference

| Source | Import | ใช้เมื่อ |
|--------|--------|---------|
| Google Fonts | `next/font/google` | ต้องการ Google Font + self-host |
| Local Files | `next/font/local` | มี font files เอง (.woff2, .ttf) |

| Property | ค่า | หมายเหตุ |
|----------|-----|----------|
| `className` | string | ใส่ใน element โดยตรง |
| `variable` | CSS variable | ใช้กับ Tailwind / CSS variables |
| `style` | object | inline style object |

## สรุป

1. **ใช้ `next/font/google`** — self-host อัตโนมัติ, ไม่ request ไป Google
2. **เลือก variable fonts** — performance ดีกว่า, flexible
3. **ใส่ที่ Root Layout** — apply ทั้งแอป
4. **ใช้ `variable` prop** — สร้าง CSS variable สำหรับ Tailwind
5. **Zero layout shift** — `next/font` จัดการ font-display + fallback metrics ให้
6. **Local fonts** — ใช้ `next/font/local` สำหรับ custom/licensed fonts
