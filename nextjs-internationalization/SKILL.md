---
name: Next.js Internationalization
description: Expert guidance on implementing i18n in Next.js App Router — locale routing, Proxy redirect, dictionaries, static rendering, and i18n libraries.
---

# Next.js Internationalization

Expert guidance on implementing i18n in Next.js App Router — locale routing, Proxy redirect, dictionaries, static rendering, and i18n libraries.

@doc-version: 16.2.6

## Core Concepts

Next.js i18n ประกอบด้วย:
- **Internationalized routing** — URL sub-paths (`/fr/products`) หรือ domains (`my-site.fr/products`)
- **Localization** — แสดง content ตามภาษาที่เลือก (dictionaries/translations)
- **Locale detection** — ตรวจจับภาษาจาก `Accept-Language` header

## Guidelines

### 1. Project Structure

```
app/
├── [lang]/
│   ├── layout.tsx          # Root layout with lang param
│   ├── page.tsx            # Home page
│   ├── products/
│   │   └── page.tsx        # /en/products, /th/products
│   ├── dictionaries.ts     # Dictionary loader
│   └── dictionaries/
│       ├── en.json
│       ├── th.json
│       └── nl.json
└── proxy.ts                # Locale detection + redirect
```

### 2. Locale Detection with Proxy

```ts
// proxy.ts
import { NextResponse } from 'next/server'
import { match } from '@formatjs/intl-localematcher'
import Negotiator from 'negotiator'

const locales = ['en', 'th', 'nl']
const defaultLocale = 'en'

function getLocale(request: Request): string {
  const headers = { 'accept-language': request.headers.get('accept-language') || '' }
  const languages = new Negotiator({ headers }).languages()
  return match(languages, locales, defaultLocale)
}

export function proxy(request: Request) {
  const { pathname } = new URL(request.url)

  // Check if pathname already has a locale
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )

  if (pathnameHasLocale) return

  // Redirect to locale-prefixed path
  const locale = getLocale(request)
  const url = new URL(`/${locale}${pathname}`, request.url)
  return NextResponse.redirect(url)
}

export const config = {
  matcher: [
    // Skip internal paths (_next, api, static files)
    '/((?!_next|api|favicon.ico|.*\\..*).*)',
  ],
}
```

**Dependencies:**

```bash
npm install @formatjs/intl-localematcher negotiator
npm install -D @types/negotiator
```

### 3. Dictionaries (Localization)

#### Dictionary Files

```json
// app/[lang]/dictionaries/en.json
{
  "navigation": {
    "home": "Home",
    "products": "Products",
    "about": "About"
  },
  "products": {
    "cart": "Add to Cart",
    "price": "Price"
  },
  "common": {
    "loading": "Loading...",
    "error": "Something went wrong"
  }
}
```

```json
// app/[lang]/dictionaries/th.json
{
  "navigation": {
    "home": "หน้าแรก",
    "products": "สินค้า",
    "about": "เกี่ยวกับ"
  },
  "products": {
    "cart": "เพิ่มลงตะกร้า",
    "price": "ราคา"
  },
  "common": {
    "loading": "กำลังโหลด...",
    "error": "เกิดข้อผิดพลาด"
  }
}
```

#### Dictionary Loader

```ts
// app/[lang]/dictionaries.ts
import 'server-only'

const dictionaries = {
  en: () => import('./dictionaries/en.json').then((module) => module.default),
  th: () => import('./dictionaries/th.json').then((module) => module.default),
  nl: () => import('./dictionaries/nl.json').then((module) => module.default),
}

export type Locale = keyof typeof dictionaries

export const hasLocale = (locale: string): locale is Locale =>
  locale in dictionaries

export const getDictionary = async (locale: Locale) => dictionaries[locale]()
```

> **`server-only`** — dictionaries โหลดบน server เท่านั้น ไม่เพิ่ม client bundle size

### 4. Using Dictionaries in Pages

```tsx
// app/[lang]/page.tsx
import { notFound } from 'next/navigation'
import { getDictionary, hasLocale } from './dictionaries'

export default async function Page({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params

  if (!hasLocale(lang)) notFound()

  const dict = await getDictionary(lang)

  return (
    <main>
      <h1>{dict.navigation.home}</h1>
      <button>{dict.products.cart}</button>
    </main>
  )
}
```

### 5. Root Layout with `lang` Attribute

```tsx
// app/[lang]/layout.tsx
import { hasLocale } from './dictionaries'
import { notFound } from 'next/navigation'

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ lang: string }>
}) {
  const { lang } = await params

  if (!hasLocale(lang)) notFound()

  return (
    <html lang={lang}>
      <body>{children}</body>
    </html>
  )
}
```

### 6. Static Rendering (`generateStaticParams`)

Pre-render ทุก locale ตอน build:

```tsx
// app/[lang]/layout.tsx
export async function generateStaticParams() {
  return [{ lang: 'en' }, { lang: 'th' }, { lang: 'nl' }]
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ lang: string }>
}) {
  return (
    <html lang={(await params).lang}>
      <body>{children}</body>
    </html>
  )
}
```

### 7. Language Switcher

```tsx
// app/[lang]/_components/language-switcher.tsx
'use client'

import { usePathname, useRouter } from 'next/navigation'

const locales = [
  { code: 'en', label: 'English' },
  { code: 'th', label: 'ไทย' },
  { code: 'nl', label: 'Nederlands' },
]

export function LanguageSwitcher({ currentLocale }: { currentLocale: string }) {
  const pathname = usePathname()
  const router = useRouter()

  function switchLocale(newLocale: string) {
    // Replace current locale in pathname
    const newPathname = pathname.replace(`/${currentLocale}`, `/${newLocale}`)
    router.push(newPathname)
  }

  return (
    <div>
      {locales.map((locale) => (
        <button
          key={locale.code}
          onClick={() => switchLocale(locale.code)}
          disabled={locale.code === currentLocale}
        >
          {locale.label}
        </button>
      ))}
    </div>
  )
}
```

### 8. Metadata per Locale

```tsx
// app/[lang]/page.tsx
import type { Metadata } from 'next'
import { getDictionary, hasLocale } from './dictionaries'

export async function generateMetadata({
  params,
}: {
  params: Promise<{ lang: string }>
}): Promise<Metadata> {
  const { lang } = await params
  if (!hasLocale(lang)) return {}

  const dict = await getDictionary(lang)

  return {
    title: dict.navigation.home,
    description: dict.common.description,
  }
}
```

### 9. Alternate Links (SEO)

```tsx
// app/[lang]/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  alternates: {
    languages: {
      'en': '/en',
      'th': '/th',
      'nl': '/nl',
    },
  },
}
```

## i18n Libraries

| Library | Features |
|---------|----------|
| [`next-intl`](https://next-intl.dev) | Full-featured, App Router support, type-safe |
| [`next-international`](https://github.com/QuiiBz/next-international) | Type-safe, lightweight |
| [`next-i18n-router`](https://github.com/i18nexus/next-i18n-router) | Routing focused |
| [`paraglide-next`](https://inlang.com/m/osslbuzt/paraglide-next-i18n) | Compiler-based, tree-shaking |
| [`lingui`](https://lingui.dev) | ICU MessageFormat, extraction |
| [`tolgee`](https://tolgee.io) | In-context editing, OTA updates |
| [`next-intlayer`](https://intlayer.org) | Visual editor, type-safe |

## Quick Reference

| Concept | Implementation |
|---------|---------------|
| Locale detection | Proxy + `Accept-Language` header |
| URL structure | `/[lang]/...` dynamic segment |
| Translations | JSON dictionaries + `getDictionary()` |
| Type safety | `hasLocale()` type guard |
| Static render | `generateStaticParams` per locale |
| HTML lang | `<html lang={lang}>` in root layout |
| SEO | `alternates.languages` in metadata |
| Bundle size | `server-only` — dictionaries ไม่ส่งไป client |

## สรุป

1. **Proxy** — detect locale จาก `Accept-Language` + redirect
2. **`app/[lang]/`** — ทุก route อยู่ใต้ dynamic locale segment
3. **Dictionaries** — JSON files + `getDictionary()` (server-only)
4. **`hasLocale()`** — type guard + 404 สำหรับ locale ที่ไม่รองรับ
5. **`generateStaticParams`** — pre-render ทุก locale
6. **Server Components** — dictionaries ไม่เพิ่ม client JS bundle
7. **ใช้ library** (next-intl, etc.) สำหรับ features เพิ่มเติม (plurals, formatting, etc.)
