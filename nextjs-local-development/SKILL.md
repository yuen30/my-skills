---
name: Next.js Local Development
description: Expert guidance on optimizing Next.js local development — Turbopack, antivirus, imports, Tailwind config, memory, Docker, and Turbopack tracing.
---

# Next.js Local Development

Expert guidance on optimizing Next.js local development — Turbopack, antivirus, imports, Tailwind config, memory, Docker, and Turbopack tracing.

@doc-version: 16.2.6

## Core Concepts

`next dev` compile routes on-demand (เมื่อเปิดหน้านั้น) — ต่างจาก `next build` ที่ compile ทั้งหมด ถ้า dev ช้า มักเกิดจาก:
- Antivirus scanning files
- Large imports / barrel files
- Tailwind scanning too many files
- Docker filesystem overhead
- Memory constraints

## Guidelines

### 1. Check Antivirus

#### macOS — Disable Gatekeeper for Terminal

```bash
sudo spctl developer-mode enable-terminal
```

แล้วไป System Settings → Privacy & Security → Developer Tools → enable terminal ของคุณ

#### Windows — Exclude Project from Defender

1. Windows Security → Virus & threat protection → Manage settings
2. Add or remove exclusions → Add Folder → เลือก project folder

### 2. Update Next.js + Use Turbopack (Default)

```bash
npm install next@latest
npm run dev  # Turbopack เป็น default แล้ว
```

Turbopack เร็วกว่า webpack อย่างมากสำหรับ development

ถ้าต้องการ webpack:
```bash
npm run dev -- --webpack
```

### 3. Optimize Imports

#### Icon Libraries — Import เฉพาะที่ใช้

```tsx
// ❌ Bad — import ทั้ง library (thousands of icons)
import { TriangleIcon } from '@phosphor-icons/react'

// ✅ Good — import เฉพาะ icon ที่ต้องการ
import { TriangleIcon } from '@phosphor-icons/react/dist/csr/Triangle'
```

#### Barrel Files — Import ตรงจาก file

```tsx
// ❌ Bad — barrel file re-exports ทุกอย่าง
import { Button } from '@/components'

// ✅ Good — import ตรง
import { Button } from '@/components/ui/button'
```

#### `optimizePackageImports`

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
  },
}
```

> Turbopack optimize imports อัตโนมัติ — ไม่ต้อง config นี้

### 4. Tailwind CSS — Scan เฉพาะที่จำเป็น

```js
// tailwind.config.js

// ❌ Bad — scan ทั้ง monorepo รวม node_modules
module.exports = {
  content: ['../../packages/**/*.{js,ts,jsx,tsx}'],
}

// ✅ Good — scan เฉพาะ src folders
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx}',
  ],
}
```

> Tailwind 3.4.8+ จะ warn ถ้า content config อาจช้า

### 5. Custom Webpack — ลดหรือเอาออก

ถ้ามี custom webpack config ที่ช้า:
- พิจารณาว่าจำเป็นสำหรับ dev ไหม
- ใช้เฉพาะ production builds
- หรือย้ายไป Turbopack loaders

### 6. Memory Optimization

สำหรับ apps ขนาดใหญ่:

```bash
# เพิ่ม memory limit
NODE_OPTIONS='--max-old-space-size=8192' npm run dev
```

ดู [Memory Usage guide](/docs/app/guides/memory-usage)

### 7. Server Components HMR Cache

Cache fetch responses ระหว่าง HMR refreshes:

```js
// next.config.js
module.exports = {
  experimental: {
    serverComponentsHmrCache: true,
  },
}
```

- ลด API calls ตอน dev
- Response เร็วขึ้นหลัง save file

### 8. Avoid Docker for Development (Mac/Windows)

Docker filesystem access บน Mac/Windows ช้ามาก:
- HMR อาจใช้เวลาหลายวินาทีถึงนาที
- เกิดจาก filesystem operations ข้าม OS boundary

**แนะนำ:**
- ✅ ใช้ local dev (`npm run dev`) สำหรับ development
- ✅ ใช้ Docker สำหรับ production deployment + testing
- ถ้าต้องใช้ Docker dev → ใช้บน Linux machine/VM

## Debugging Tools

### Fetch Logging

```js
// next.config.js
module.exports = {
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
}
```

### Turbopack Tracing

วิเคราะห์ compile time ของแต่ละ module:

```bash
# 1. Generate trace
NEXT_TURBOPACK_TRACING=1 npm run dev

# 2. Navigate around / reproduce problem

# 3. Stop dev server

# 4. Analyze trace
npx next internal trace .next/dev/trace-turbopack

# 5. View at https://trace.nextjs.org/
```

**Trace viewer tips:**
- Default: "Aggregated in order" (รวม timings)
- Switch to "Spans in order" เพื่อดูแต่ละ individual time

### Dependency Analysis

```bash
# Visualize dependency graph
npx madge --image graph.svg ./src

# Find circular dependencies
npx madge --circular ./src
```

## Performance Checklist

```
Local Dev Optimization:
□ Antivirus — exclude project folder
□ Next.js — latest version + Turbopack (default)
□ Imports — no barrel files, specific icon imports
□ Tailwind — content array ไม่ scan node_modules
□ Webpack — ลด custom config หรือใช้ Turbopack
□ Memory — เพิ่ม NODE_OPTIONS ถ้าจำเป็น
□ Docker — ใช้ local dev แทน (Mac/Windows)
□ HMR cache — enable serverComponentsHmrCache
```

## Quick Reference

| Issue | Solution |
|-------|----------|
| Slow file access | Exclude from antivirus |
| Slow compilation | Update Next.js + Turbopack |
| Large bundles | Optimize imports, avoid barrel files |
| Tailwind slow | Narrow `content` array |
| HMR slow (Docker) | Use local dev instead |
| Memory issues | Increase `--max-old-space-size` |
| Slow Server Components | Enable `serverComponentsHmrCache` |
| Debug compile time | Turbopack tracing |

## สรุป

1. **Turbopack** — default bundler, เร็วกว่า webpack มาก
2. **Antivirus** — exclude project folder (Windows Defender, Gatekeeper)
3. **Imports** — specific imports, ไม่ใช้ barrel files, `optimizePackageImports`
4. **Tailwind** — scan เฉพาะ src folders
5. **Docker** — ใช้ local dev บน Mac/Windows (Docker filesystem ช้า)
6. **Turbopack tracing** — วิเคราะห์ compile time per module
7. **`serverComponentsHmrCache`** — cache fetch ระหว่าง HMR
