---
name: Next.js Memory Usage
description: Expert guidance on optimizing memory usage in Next.js — reduce dependencies, webpack optimizations, heap profiling, build workers, and preload control.
---

# Next.js Memory Usage

Expert guidance on optimizing memory usage in Next.js — reduce dependencies, webpack optimizations, heap profiling, build workers, and preload control.

@doc-version: 16.2.6

## Core Concepts

เมื่อ app ใหญ่ขึ้น memory usage เพิ่มทั้งตอน dev และ build — มีหลายวิธีลด memory:
- ลด dependencies
- Webpack memory optimizations
- Build workers
- Disable unnecessary features
- Heap profiling

## Guidelines

### 1. Reduce Dependencies

ใช้ [Bundle Analyzer](/docs/app/guides/package-bundling) หา dependencies ที่ใหญ่เกินไป:

```bash
npm install @next/bundle-analyzer
```

```js
// next.config.mjs
import bundleAnalyzer from '@next/bundle-analyzer'

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})

export default withBundleAnalyzer(nextConfig)
```

```bash
ANALYZE=true npm run build
```

### 2. Webpack Memory Optimizations

```js
// next.config.js
module.exports = {
  experimental: {
    webpackMemoryOptimizations: true,
  },
}
```

- ลด max memory usage
- อาจเพิ่ม compilation time เล็กน้อย
- Low-risk, experimental (v15.0.0+)

### 3. Webpack Build Worker

รัน webpack compilations ใน separate Node.js worker:

```js
// next.config.js
module.exports = {
  experimental: {
    webpackBuildWorker: true,
  },
}
```

- Default enabled ตั้งแต่ v14.1.0 (ถ้าไม่มี custom webpack config)
- ลด memory usage ระหว่าง builds อย่างมาก
- อาจไม่ compatible กับบาง custom webpack plugins

### 4. Debug Memory Usage During Build

```bash
next build --experimental-debug-memory-usage
```

- Print heap usage + GC statistics ตลอด build
- Auto heap snapshot เมื่อ memory ใกล้ limit
- ส่ง `SIGUSR2` signal เพื่อ take snapshot manually

### 5. Heap Profiling

#### Record Heap Profile

```bash
node --heap-prof node_modules/next/dist/bin/next build
```

- สร้าง `.heapprofile` file
- เปิดใน Chrome DevTools → Memory tab → Load Profile

#### Analyze Heap Snapshot

```bash
# Expose inspector
NODE_OPTIONS=--inspect next build

# Break before user code
NODE_OPTIONS=--inspect-brk next build
```

- Connect Chrome DevTools ไปที่ debugging port
- Record + analyze heap snapshot
- ดูว่า memory ถูก retain ที่ไหน

### 6. Disable Webpack Cache

ลด memory แลกกับ build speed:

```js
// next.config.mjs
const nextConfig = {
  webpack: (config, { dev }) => {
    if (config.cache && !dev) {
      config.cache = Object.freeze({
        type: 'memory',
      })
    }
    return config
  },
}

export default nextConfig
```

### 7. Disable TypeScript Checking During Build

ถ้า build OOM ตอน "Running TypeScript" step:

```js
// next.config.mjs
const nextConfig = {
  typescript: {
    // ⚠️ Dangerously allow builds with type errors
    ignoreBuildErrors: true,
  },
}
```

> **สำคัญ:** ทำ type checking ใน CI แยกต่างหาก — อย่า skip ทั้งหมด

### 8. Disable Source Maps

```js
// next.config.mjs
const nextConfig = {
  productionBrowserSourceMaps: false,
  experimental: {
    serverSourceMaps: false,
  },
  // ถ้า OOM ตอน "Generating static pages" (cacheComponents)
  enablePrerenderSourceMaps: false,
}
```

### 9. Disable Preloading Entries

Next.js preload ทุก page's JS modules ตอน server start — ลด response time แต่เพิ่ม initial memory:

```ts
// next.config.ts
const config = {
  experimental: {
    preloadEntriesOnStart: false,
  },
}
```

> Memory footprint จะเท่ากันในที่สุดถ้าทุก pages ถูก request

### 10. Increase Node.js Memory Limit

```bash
# Development
NODE_OPTIONS='--max-old-space-size=8192' npm run dev

# Build
NODE_OPTIONS='--max-old-space-size=8192' npm run build
```

| Value | Memory |
|-------|--------|
| `4096` | 4 GB |
| `8192` | 8 GB |
| `16384` | 16 GB |

## Optimization Priority

```
Memory Issues:
├── Build time (next build)
│   ├── 1. Use Turbopack (default dev, coming for build)
│   ├── 2. Enable webpackBuildWorker
│   ├── 3. Enable webpackMemoryOptimizations
│   ├── 4. Reduce dependencies
│   ├── 5. Disable source maps
│   ├── 6. Disable webpack cache
│   ├── 7. Disable TypeScript checking (do in CI)
│   └── 8. Increase NODE_OPTIONS memory
│
└── Runtime (next start / next dev)
    ├── 1. Reduce dependencies
    ├── 2. Disable preloadEntriesOnStart
    ├── 3. Increase NODE_OPTIONS memory
    └── 4. Use Turbopack for dev
```

## Quick Reference

| Option | Purpose | Version |
|--------|---------|---------|
| `webpackMemoryOptimizations: true` | ลด max memory (webpack) | v15.0.0+ |
| `webpackBuildWorker: true` | Build ใน separate worker | v14.1.0+ (default) |
| `--experimental-debug-memory-usage` | Debug memory during build | v14.2.0+ |
| `preloadEntriesOnStart: false` | ไม่ preload pages ตอน start | v16+ |
| `productionBrowserSourceMaps: false` | ไม่สร้าง source maps | All |
| `typescript.ignoreBuildErrors: true` | Skip type checking | All |
| `NODE_OPTIONS='--max-old-space-size=N'` | เพิ่ม memory limit | All |

## สรุป

1. **ลด dependencies** — Bundle Analyzer หา packages ที่ใหญ่
2. **`webpackMemoryOptimizations`** — ลด peak memory (experimental)
3. **Build worker** — default enabled, แยก webpack ไป worker
4. **Heap profiling** — `--heap-prof` + Chrome DevTools
5. **Disable source maps** — ลด memory ตอน build
6. **`preloadEntriesOnStart: false`** — ลด initial memory ตอน start
7. **เพิ่ม `--max-old-space-size`** — quick fix สำหรับ OOM
8. **Type checking ใน CI** — ไม่ต้องทำตอน build ถ้า memory ไม่พอ
