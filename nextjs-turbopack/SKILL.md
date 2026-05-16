---
name: Next.js Build Tools (Turbopack and SWC Compiler)
description: Expert guidance on Next.js build tools — Turbopack bundler, SWC compiler, configuration, webpack differences, styled-components, Jest, remove console, define, and performance tracing.
---

# Next.js Build Tools (Turbopack and SWC Compiler)

Expert guidance on Turbopack in Next.js — default bundler, configuration, supported features, webpack differences, performance tracing, and migration.

@doc-version: 16.2.6

## Core Concepts

Turbopack เป็น **incremental bundler** เขียนด้วย Rust, built into Next.js:
- **Default bundler** ตั้งแต่ Next.js 16
- **Unified graph** — single graph สำหรับ client + server
- **Incremental** — cache results ถึง function level, ไม่ทำซ้ำ
- **Lazy bundling** — bundle เฉพาะที่ request จริง
- **Parallel** — ใช้ทุก CPU cores

## Getting Started

Turbopack เป็น default — ไม่ต้อง config:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

### ใช้ Webpack แทน

```json
{
  "scripts": {
    "dev": "next dev --webpack",
    "build": "next build --webpack"
  }
}
```

## Supported Features

### Language

| Feature | Status |
|---------|:---:|
| JavaScript & TypeScript | ✅ (SWC) |
| ECMAScript (ESNext) | ✅ |
| CommonJS (`require`) | ✅ |
| ESM (`import`) | ✅ |
| Babel | ✅ (auto-detect config) |

### Framework & React

| Feature | Status |
|---------|:---:|
| JSX / TSX | ✅ |
| Fast Refresh | ✅ |
| React Server Components | ✅ |
| App Router | ✅ |
| Pages Router | ✅ |

### CSS & Styling

| Feature | Status |
|---------|:---:|
| Global CSS | ✅ |
| CSS Modules | ✅ (Lightning CSS) |
| CSS Nesting | ✅ |
| `@import` | ✅ |
| PostCSS | ✅ (auto-detect config) |
| Sass / SCSS | ✅ |
| Tailwind CSS | ✅ (via PostCSS) |

### Assets & Resolution

| Feature | Status |
|---------|:---:|
| Static assets (images, fonts) | ✅ |
| JSON imports | ✅ |
| Path aliases (`tsconfig.json`) | ✅ |
| Custom extensions | ✅ |

## Configuration

```js
// next.config.js
module.exports = {
  turbopack: {
    // Webpack loaders
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },

    // Resolve aliases (like webpack resolve.alias)
    resolveAlias: {
      underscore: 'lodash',
      'old-package': 'new-package',
    },

    // Custom file extensions
    resolveExtensions: ['.mdx', '.tsx', '.ts', '.jsx', '.js', '.json'],
  },
}
```

### Experimental Options

```js
// next.config.js
module.exports = {
  experimental: {
    // Filesystem cache (dev — enabled by default)
    turbopackFileSystemCacheForDev: true,

    // Filesystem cache (build — opt-in)
    turbopackFileSystemCacheForBuild: true,
  },
}
```

| Option | Dev Default | Build Default |
|--------|:-:|:-:|
| `turbopackFileSystemCacheForDev` | `true` | N/A |
| `turbopackFileSystemCacheForBuild` | N/A | `false` |
| `turbopackMinify` | `false` | `true` |
| `turbopackSourceMaps` | `true` | `productionBrowserSourceMaps` |
| `turbopackTreeShaking` | `false` | `false` |
| `turbopackScopeHoisting` | `false` | `true` |

## Known Differences from Webpack

### Filesystem Root

Turbopack resolves จาก project root — files นอก root ไม่ถูก resolve:

```js
// next.config.js
module.exports = {
  turbopack: {
    root: '..', // Parent directory (for linked packages)
  },
}
```

### CSS Module Ordering

Turbopack ใช้ JS import order สำหรับ CSS Modules:

```tsx
import utilStyles from './utils.module.css'   // ← appears first in CSS
import buttonStyles from './button.module.css' // ← appears second
```

### Sass `~` Syntax (Not Supported)

```scss
// ❌ Legacy tilde syntax
@import '~bootstrap/dist/css/bootstrap.min.css';

// ✅ Direct import
@import 'bootstrap/dist/css/bootstrap.min.css';
```

Workaround:
```js
module.exports = {
  turbopack: {
    resolveAlias: { '~*': '*' },
  },
}
```

### Webpack Plugins (Not Supported)

Turbopack ไม่รองรับ webpack plugins — ใช้ [webpack loaders](/docs/app/api-reference/config/next-config-js/turbopack#configuring-webpack-loaders) แทน

### `webpack()` Config (Not Recognized)

```js
// ❌ Not recognized by Turbopack
module.exports = {
  webpack: (config) => { ... },
}

// ✅ Use turbopack config instead
module.exports = {
  turbopack: {
    rules: { ... },
    resolveAlias: { ... },
  },
}
```

## Unsupported Features

| Feature | Status |
|---------|--------|
| `sassOptions.functions` | ❌ (Rust can't execute JS functions) |
| `webpack()` in next.config | ❌ (use `turbopack` config) |
| Yarn PnP | ❌ Not planned |
| `experimental.urlImports` | ❌ Not planned |
| `experimental.esmExternals` | ❌ Not planned |
| Legacy CSS `:local`/`:global` standalone | ❌ |
| CSS `@value` rule | ❌ (use CSS variables) |
| `composes` from `.css` (non-module) | ❌ (rename to `.module.css`) |

## Performance Tracing

```bash
# Generate trace file
NEXT_TURBOPACK_TRACING=1 next dev

# Navigate around to reproduce issue
# Stop server

# Analyze trace
npx next internal trace .next/dev/trace-turbopack

# View at https://trace.nextjs.org/
```

## Magic Comments

| Comment | Webpack | Turbopack |
|---------|:---:|:---:|
| `webpackIgnore: true` | ✅ | ✅ |
| `turbopackIgnore: true` | ❌ | ✅ |
| `turbopackOptional: true` | ❌ | ✅ |

```js
// Skip bundling — runtime import
const mod = await import(/* turbopackIgnore: true */ 'runtime-module')

// Suppress error if module doesn't exist
const feature = await import(/* turbopackOptional: true */ './optional')
```

## Platform Support

| Platform | Architecture |
|----------|-------------|
| macOS | x64, ARM64 |
| Windows | x64, ARM64 |
| Linux (glibc) | x64, ARM64 |
| Linux (musl) | x64, ARM64 |

> Platforms without native bindings (FreeBSD, OpenBSD) → fallback to WASM (no Turbopack, use `--webpack`)

## Version History

| Version | Changes |
|---------|---------|
| v16.0.0 | Default bundler + auto Babel support |
| v15.5.0 | Build support (beta) |
| v15.3.0 | Build support (experimental) |
| v15.0.0 | Dev stable |

## Quick Reference

| Command | Purpose |
|---------|---------|
| `next dev` | Dev with Turbopack (default) |
| `next build` | Build with Turbopack (default) |
| `next dev --webpack` | Dev with webpack |
| `next build --webpack` | Build with webpack |
| `NEXT_TURBOPACK_TRACING=1 next dev` | Generate performance trace |

## สรุป

1. **Default bundler** ตั้งแต่ Next.js 16 — ไม่ต้อง config
2. **เร็วกว่า webpack** — incremental, lazy, parallel, Rust
3. **Zero-config** สำหรับ CSS, TypeScript, React, PostCSS, Sass
4. **Webpack loaders** รองรับ — plugins ไม่รองรับ
5. **`turbopack` config** แทน `webpack()` ใน next.config
6. **Filesystem cache** — enabled by default สำหรับ dev
7. **Tracing** — `NEXT_TURBOPACK_TRACING=1` สำหรับ debug performance
8. **Fallback** — ใช้ `--webpack` ถ้าต้องการ webpack plugins
