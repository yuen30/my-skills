---
name: Next.js Upgrading
description: Expert guidance on upgrading Next.js applications to the latest version or canary, including upgrade commands and version migration guides.
---

# Next.js Upgrading

Expert guidance on upgrading Next.js applications to the latest version or canary, including upgrade commands and version migration guides.

@doc-version: 16.2.6

## Core Concepts

Next.js มี built-in `upgrade` command (ตั้งแต่ v16.1.0) ที่จัดการ upgrade + codemods ให้อัตโนมัติ

## Guidelines

### 1. Upgrade to Latest Version

#### ใช้ `next upgrade` (แนะนำ — v16.1.0+)

```bash
# pnpm
pnpm next upgrade

# npm
npx next upgrade

# yarn
yarn next upgrade

# bun
bunx next upgrade
```

Command นี้จะ:
- อัปเดต Next.js + React + dependencies
- รัน codemods ที่จำเป็นอัตโนมัติ
- แจ้ง breaking changes ที่ต้องแก้ไขเอง

#### สำหรับ versions ก่อน 16.1.0

```bash
npx @next/codemod@canary upgrade latest
```

#### Manual Upgrade

```bash
# pnpm
pnpm i next@latest react@latest react-dom@latest eslint-config-next@latest

# npm
npm i next@latest react@latest react-dom@latest eslint-config-next@latest

# yarn
yarn add next@latest react@latest react-dom@latest eslint-config-next@latest

# bun
bun add next@latest react@latest react-dom@latest eslint-config-next@latest
```

### 2. Canary Version

ใช้ canary เพื่อทดสอบ features ใหม่ก่อน stable release:

```bash
# ต้องอยู่ latest stable ก่อน แล้วค่อย upgrade เป็น canary
pnpm add next@canary

# npm
npm i next@canary

# yarn
yarn add next@canary

# bun
bun add next@canary
```

#### Features ที่อยู่ใน Canary

**Authentication:**
- `forbidden` function
- `unauthorized` function
- `forbidden.js` file convention
- `unauthorized.js` file convention
- `authInterrupts` config option

### 3. Version Migration Guides

#### Version 15 → 16

Key changes:
- **Proxy** (เดิมคือ Middleware) — เปลี่ยนชื่อ, ย้ายจาก `middleware.ts` เป็น `proxy.ts`
- **Cache Components** — `cacheComponents: true` + `"use cache"` directive
- **`params` เป็น Promise** — ต้อง `await params` ใน pages/layouts
- **`searchParams` เป็น Promise** — ต้อง `await searchParams`
- **React 19** — required
- **Turbopack** — default bundler สำหรับ dev

```bash
# Upgrade command จัดการ codemods ให้
npx next upgrade
```

#### Version 14 → 15

Key changes:
- **Async Request APIs** — `cookies()`, `headers()` เป็น async
- **Caching defaults เปลี่ยน** — fetch ไม่ cache โดย default
- **React 19 RC** — required
- **`next/image`** — ลบ legacy image component

#### Version 13 → 14

Key changes:
- **Node.js 18.17** minimum
- **Server Actions** stable
- **Turbopack** improvements
- **Partial Prerendering** (experimental)

### 4. Upgrade Checklist

```
Before Upgrade:
□ Commit current code (clean git state)
□ Check current Next.js version: npx next --version
□ Read version migration guide
□ Check dependencies compatibility

During Upgrade:
□ Run: npx next upgrade
□ Fix any codemod warnings
□ Update deprecated APIs manually

After Upgrade:
□ Run: npm run build (check for errors)
□ Run: npm run dev (test locally)
□ Test critical paths
□ Check for deprecation warnings in console
□ Update CI/CD if needed
```

### 5. Common Upgrade Issues

#### `params` is now a Promise (v16)

```tsx
// ❌ Before (v15)
export default function Page({ params }: { params: { slug: string } }) {
  return <div>{params.slug}</div>
}

// ✅ After (v16)
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  return <div>{slug}</div>
}
```

#### `cookies()` / `headers()` are async (v15+)

```tsx
// ❌ Before
import { cookies } from 'next/headers'
const cookieStore = cookies()

// ✅ After
import { cookies } from 'next/headers'
const cookieStore = await cookies()
```

#### Middleware → Proxy (v16)

```bash
# Rename file
mv middleware.ts proxy.ts
```

```tsx
// ❌ Before (middleware.ts)
export function middleware(request) { ... }

// ✅ After (proxy.ts)
export function proxy(request) { ... }
```

## Quick Reference

| Action | Command |
|--------|---------|
| Upgrade to latest | `npx next upgrade` |
| Upgrade (pre-16.1) | `npx @next/codemod@canary upgrade latest` |
| Install canary | `npm i next@canary` |
| Check version | `npx next --version` |
| Run codemods only | `npx @next/codemod@latest` |

| Version | React Required | Node.js Minimum |
|---------|---------------|-----------------|
| 16.x | React 19 | Node.js 18.18+ |
| 15.x | React 19 RC | Node.js 18.17+ |
| 14.x | React 18 | Node.js 18.17+ |

## สรุป

1. **ใช้ `npx next upgrade`** — จัดการทุกอย่างให้อัตโนมัติ (v16.1.0+)
2. **อ่าน migration guide** ก่อน upgrade major version
3. **Commit ก่อน upgrade** — ให้ revert ได้ถ้ามีปัญหา
4. **Build + test หลัง upgrade** — ตรวจสอบ errors
5. **Canary** — ใช้ทดสอบ features ใหม่ ไม่ใช่ production
