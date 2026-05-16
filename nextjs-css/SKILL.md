---
name: Next.js Styling
description: Expert guidance on styling Next.js applications — Tailwind CSS, CSS Modules, Global CSS, CSS-in-JS (styled-components, styled-jsx), Sass/SCSS, external stylesheets, and CSS ordering.
---

# Next.js Styling

Expert guidance on styling Next.js applications with Tailwind CSS, CSS Modules, Global CSS, external stylesheets, and CSS ordering best practices.

@doc-version: 16.2.6

## Core Concepts

Next.js รองรับหลายวิธีในการจัดการ CSS:
- **Tailwind CSS** — utility-first framework (แนะนำ)
- **CSS Modules** — scoped CSS ต่อ component
- **Global CSS** — styles ที่ใช้ทั้งแอป
- **External Stylesheets** — CSS จาก packages ภายนอก
- **Sass** — CSS preprocessor
- **CSS-in-JS** — styled-components, emotion, etc.

## Guidelines

### 1. Tailwind CSS (แนะนำ)

#### Installation

```bash
npm install -D tailwindcss @tailwindcss/postcss
```

#### PostCSS Config

```js
// postcss.config.mjs
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

#### Global CSS File

```css
/* app/globals.css */
@import 'tailwindcss';
```

#### Import ใน Root Layout

```tsx
// app/layout.tsx
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

#### ใช้งาน

```tsx
// app/page.tsx
export default function Page() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Welcome to Next.js!</h1>
    </main>
  )
}
```

> ถ้าต้องการ broader browser support สำหรับ browsers เก่า ดู Tailwind CSS v3 setup

### 2. CSS Modules

CSS Modules สร้าง unique class names อัตโนมัติ — ไม่มี naming collisions:

#### สร้างไฟล์ `.module.css`

```css
/* app/blog/blog.module.css */
.blog {
  padding: 24px;
}

.title {
  font-size: 2rem;
  font-weight: bold;
}

.card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
}
```

#### Import ใน Component

```tsx
// app/blog/page.tsx
import styles from './blog.module.css'

export default function Page() {
  return (
    <main className={styles.blog}>
      <h1 className={styles.title}>Blog</h1>
      <div className={styles.card}>
        <p>Post content</p>
      </div>
    </main>
  )
}
```

**ข้อดี:**
- Scoped ต่อ component — ไม่ conflict กับ CSS อื่น
- ใช้ชื่อ class เดียวกันในไฟล์ต่างกันได้
- Tree-shaking — CSS ที่ไม่ใช้จะถูกตัดออก

### 3. Global CSS

สำหรับ styles ที่ใช้ทั้งแอป:

```css
/* app/global.css */
body {
  padding: 20px 20px 60px;
  max-width: 680px;
  margin: 0 auto;
}
```

```tsx
// app/layout.tsx
import './global.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

> Global styles import ได้ในทุก layout, page, หรือ component ใน `app` directory แต่แนะนำให้ใช้เฉพาะ truly global CSS (เช่น Tailwind base styles, CSS reset)

**ข้อควรระวัง:** Global CSS ไม่ถูก remove เมื่อ navigate ระหว่าง routes — อาจเกิด conflicts ได้

### 4. External Stylesheets

Import CSS จาก npm packages ได้ทุกที่ใน `app` directory:

```tsx
// app/layout.tsx
import 'bootstrap/dist/css/bootstrap.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="container">{children}</body>
    </html>
  )
}
```

> React 19 รองรับ `<link rel="stylesheet" href="..." />` ใน components ได้ด้วย

### 5. CSS Ordering and Merging

Next.js จัดลำดับ CSS ตาม **ลำดับที่ import ใน code**:

```tsx
// page.tsx
import { BaseButton } from './base-button' // ← CSS ของ BaseButton มาก่อน
import styles from './page.module.css'      // ← CSS ของ page มาทีหลัง

export default function Page() {
  return <BaseButton className={styles.primary} />
}
```

```tsx
// base-button.tsx
import styles from './base-button.module.css' // ← ถูก import ก่อน page.module.css

export function BaseButton() {
  return <button className={styles.primary} />
}
```

**ผลลัพธ์:** `base-button.module.css` จะอยู่ก่อน `page.module.css` ใน final CSS

### 6. Best Practices — CSS Ordering

- Import CSS ในไฟล์ entry เดียวเมื่อทำได้
- Import global styles + Tailwind ที่ root ของแอป
- **ใช้ Tailwind CSS** สำหรับ styling ส่วนใหญ่
- ใช้ CSS Modules เมื่อ Tailwind utilities ไม่เพียงพอ
- ใช้ naming convention ที่สม่ำเสมอ: `<name>.module.css`
- Extract shared styles เป็น shared components
- ปิด linters/formatters ที่ auto-sort imports (เช่น ESLint `sort-imports`)
- ใช้ `cssChunking` option ใน next.config.js เพื่อควบคุม CSS chunking

### 7. Development vs Production

| | Development (`next dev`) | Production (`next build`) |
|---|---|---|
| CSS updates | Fast Refresh (ทันที) | ต้อง build ใหม่ |
| CSS files | แยกไฟล์ตามปกติ | Minified + code-split `.css` files |
| JS disabled | ต้องมี JS สำหรับ Fast Refresh | CSS ยังทำงานได้ |
| CSS ordering | อาจต่างจาก production | ลำดับสุดท้ายที่ถูกต้อง |

> **สำคัญ:** ตรวจสอบ CSS ordering ด้วย `next build` เสมอ — development อาจแสดงลำดับต่างกัน

## Recommended Styling Strategy

```
Styling Decision:
├── Layout/spacing/colors/typography → Tailwind CSS utilities
├── Complex component-specific styles → CSS Modules
├── Truly global styles (reset, base) → Global CSS (import ที่ root layout)
├── Third-party library styles → External Stylesheets
├── Dynamic styles based on props → Tailwind + cn() utility
└── Animation-heavy components → CSS Modules หรือ CSS-in-JS
```

## Example: Combining Approaches

```tsx
// app/layout.tsx
import './globals.css' // Tailwind + global resets

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
```

```tsx
// app/dashboard/page.tsx
import styles from './dashboard.module.css' // Scoped styles for complex layout

export default function DashboardPage() {
  return (
    <div className={styles.grid}>
      {/* Tailwind for simple styling */}
      <div className="rounded-lg border p-4 shadow-sm">
        <h2 className="text-lg font-semibold">Stats</h2>
      </div>

      {/* CSS Module for complex grid layout */}
      <div className={styles.chartContainer}>
        <Chart />
      </div>
    </div>
  )
}
```

```css
/* app/dashboard/dashboard.module.css */
.grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  grid-template-rows: auto 1fr;
  gap: 1rem;
  height: calc(100vh - 4rem);
}

.chartContainer {
  grid-column: 2;
  grid-row: 1 / -1;
  overflow: hidden;
}
```

## Quick Reference

| วิธี | ใช้เมื่อ | Scope |
|------|---------|-------|
| Tailwind CSS | Styling ทั่วไป (แนะนำ) | Utility classes |
| CSS Modules | Complex component styles | Scoped ต่อ component |
| Global CSS | Reset, base styles, Tailwind import | ทั้งแอป |
| External Stylesheets | Third-party CSS (Bootstrap, etc.) | ทั้งแอป |
| Sass | ต้องการ variables, mixins, nesting | Scoped หรือ Global |
| CSS-in-JS | Dynamic styles, theme-based | Component-level |

## สรุป

1. **ใช้ Tailwind CSS เป็นหลัก** — ครอบคลุม styling ส่วนใหญ่
2. **CSS Modules สำหรับ complex layouts** — scoped, ไม่ conflict
3. **Global CSS เฉพาะ truly global** — reset, base, Tailwind import
4. **ระวังลำดับ CSS** — import order = CSS order
5. **ตรวจสอบด้วย `next build`** — dev อาจแสดงลำดับต่างจาก production
