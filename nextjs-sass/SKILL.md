---
name: Next.js Sass
description: Expert guidance on using Sass/SCSS in Next.js — installation, CSS Modules, sassOptions, variables export, and implementation options.
---

# Next.js Sass

Expert guidance on using Sass/SCSS in Next.js — installation, CSS Modules, sassOptions, variables export, and implementation options.

@doc-version: 16.2.6

## Core Concepts

Next.js มี built-in support สำหรับ Sass:
- `.scss` (SCSS syntax — superset of CSS, แนะนำ)
- `.sass` (Indented syntax)
- `.module.scss` / `.module.sass` (CSS Modules — scoped)

## Guidelines

### 1. Installation

```bash
npm install --save-dev sass
```

### 2. Basic Usage

#### Global Styles

```scss
/* app/globals.scss */
$primary: #007bff;
$font-stack: 'Inter', sans-serif;

body {
  font-family: $font-stack;
  margin: 0;
  padding: 0;
}

h1 {
  color: $primary;
}
```

```tsx
// app/layout.tsx
import './globals.scss'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

#### CSS Modules (Scoped)

```scss
/* app/components/button.module.scss */
$radius: 4px;

.button {
  padding: 0.5rem 1rem;
  border-radius: $radius;
  border: none;
  cursor: pointer;

  &.primary {
    background: #007bff;
    color: white;
  }

  &.secondary {
    background: #6c757d;
    color: white;
  }

  &:hover {
    opacity: 0.9;
  }
}
```

```tsx
// app/components/button.tsx
import styles from './button.module.scss'

export function Button({ variant = 'primary', children }: {
  variant?: 'primary' | 'secondary'
  children: React.ReactNode
}) {
  return (
    <button className={`${styles.button} ${styles[variant]}`}>
      {children}
    </button>
  )
}
```

### 3. Sass Options (`next.config`)

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  sassOptions: {
    additionalData: `$var: red;`, // Prepend to every Sass file
  },
}

export default nextConfig
```

#### Common Options

```ts
const nextConfig: NextConfig = {
  sassOptions: {
    // Prepend variables/mixins to every file
    additionalData: `
      @use 'styles/variables' as *;
      @use 'styles/mixins' as *;
    `,

    // Include paths for @use/@import resolution
    includePaths: ['./styles'],

    // Sass implementation
    implementation: 'sass-embedded', // or 'sass' (default)
  },
}
```

#### `sass-embedded` (Faster)

```bash
npm install --save-dev sass-embedded
```

```ts
// next.config.ts
const nextConfig: NextConfig = {
  sassOptions: {
    implementation: 'sass-embedded',
  },
}
```

### 4. Sass Variables Export to JavaScript

```scss
/* app/variables.module.scss */
$primary-color: #64ff00;
$secondary-color: #007bff;
$font-size-lg: 1.5rem;

:export {
  primaryColor: $primary-color;
  secondaryColor: $secondary-color;
  fontSizeLg: $font-size-lg;
}
```

```tsx
// app/page.tsx
import variables from './variables.module.scss'

export default function Page() {
  return (
    <h1 style={{ color: variables.primaryColor, fontSize: variables.fontSizeLg }}>
      Hello, Next.js!
    </h1>
  )
}
```

### 5. Common Patterns

#### Shared Variables + Mixins

```scss
/* styles/_variables.scss */
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;

$color-primary: #007bff;
$color-danger: #dc3545;
$color-success: #28a745;
```

```scss
/* styles/_mixins.scss */
@mixin respond-to($breakpoint) {
  @if $breakpoint == sm {
    @media (min-width: 576px) { @content; }
  } @else if $breakpoint == md {
    @media (min-width: 768px) { @content; }
  } @else if $breakpoint == lg {
    @media (min-width: 992px) { @content; }
  }
}

@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}
```

```scss
/* app/components/card.module.scss */
@use 'styles/variables' as *;
@use 'styles/mixins' as *;

.card {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;

  @include respond-to(md) {
    padding: 2rem;
  }
}

.title {
  color: $color-primary;
}
```

#### Or use `additionalData` to auto-import:

```ts
// next.config.ts
const nextConfig: NextConfig = {
  sassOptions: {
    additionalData: `@use 'styles/variables' as *; @use 'styles/mixins' as *;`,
    includePaths: ['./'],
  },
}
```

### 6. Sass vs Tailwind CSS

| Feature | Sass | Tailwind CSS |
|---------|------|-------------|
| Variables | `$var` | CSS variables / `@theme` |
| Nesting | Built-in | CSS nesting (native) |
| Mixins | `@mixin` / `@include` | Utility classes |
| Scoping | CSS Modules | Utility classes (no conflicts) |
| Bundle size | Depends on usage | Purged unused classes |
| Learning curve | CSS + Sass syntax | Utility class names |

> **แนะนำ:** ใช้ Tailwind CSS สำหรับ projects ใหม่ — ใช้ Sass เมื่อมี existing Sass codebase หรือต้องการ complex computations

## Quick Reference

| File Extension | Type | Scoped? |
|---------------|------|:---:|
| `.scss` | SCSS syntax (global) | ❌ |
| `.sass` | Indented syntax (global) | ❌ |
| `.module.scss` | SCSS CSS Module | ✅ |
| `.module.sass` | Indented CSS Module | ✅ |

| Config Option | Purpose |
|--------------|---------|
| `additionalData` | Prepend code to every Sass file |
| `includePaths` | Directories for `@use`/`@import` resolution |
| `implementation` | `'sass'` (default) or `'sass-embedded'` (faster) |

## สรุป

1. **Install `sass`** — built-in support, ไม่ต้อง config เพิ่ม
2. **`.module.scss`** — scoped styles (CSS Modules)
3. **`sassOptions.additionalData`** — auto-import variables/mixins ทุกไฟล์
4. **`:export`** — ส่ง Sass variables ไป JavaScript
5. **`sass-embedded`** — faster compilation (optional)
6. **SCSS แนะนำ** — superset of CSS, ไม่ต้องเรียน indented syntax
