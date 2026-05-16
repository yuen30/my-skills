---
name: Next.js Deploying to Platforms
description: Expert guidance on deploying Next.js to different platforms — feature requirements, CDN compatibility, adapters, streaming, shared cache, and infrastructure decisions.
---

# Next.js Deploying to Platforms

Expert guidance on deploying Next.js to different platforms — feature requirements, CDN compatibility, adapters, streaming, shared cache, and infrastructure decisions.

@doc-version: 16.2.6

## Core Concepts

Next.js treats static/dynamic content as a spectrum at the component level — different features require different platform capabilities. A single Node.js server (`next start`) handles **every** feature correctly.

**Minimum requirement:** Node.js server + `sharp` package (for Image Optimization)

## Guidelines

### 1. Minimum Requirements

```bash
# ทุก feature ทำงานได้ด้วย:
next start
```

รองรับ: Server Components, ISR, PPR, Cache Components, Server Actions, Proxy, `after()`

**Additional infrastructure** (CDN, edge compute, shared cache) ปรับปรุง performance แต่ไม่จำเป็นสำหรับ correctness

### 2. Functional vs Performance Fidelity

| Level | Meaning | How to Verify |
|-------|---------|---------------|
| **Functional fidelity** | ทุก feature ทำงานถูกต้อง | Adapter test suite passes |
| **Performance fidelity** | Features ทำงานที่ optimal performance | Platform-specific optimization |

- Functional = binary (pass/fail)
- Performance = spectrum (แต่ละ platform ต่างกัน)

### 3. Feature Support Matrix

| Feature | Streaming | Shared Cache | Edge Stitching | Notes |
|---------|:-:|:-:|:-:|-------|
| Server Components | Required | No | No | Basic streaming |
| ISR (time-based) | No | Recommended | No | Works per-instance |
| ISR (on-demand) | No | Recommended | No | Tag propagation needs shared cache |
| PPR | Required | Recommended | Optional | Performance optimization |
| Cache Components (`use cache`) | Required | Recommended | No | Cross-instance consistency |
| Proxy / Middleware | No | No | No | Edge or origin |
| Server Actions | Required | No | No | POST + streaming response |
| `after()` | No | No | No | Needs graceful shutdown |

**Streaming Required** = platform ต้องรองรับ chunked transfer encoding หรือ HTTP/2 streaming และต้องไม่ buffer response

**Shared Cache Recommended** = multiple instances ต้องการ shared cache เพื่อ coordinate revalidation

### 4. Without Shared Cache

แต่ละ instance maintain cache ของตัวเอง:
- Features ยังทำงานถูกต้อง per-instance
- Revalidation events ไม่ propagate ข้าม instances
- อาจเห็น stale content ต่างกันระหว่าง instances

**แก้ไข:** ใช้ cache handlers:
- `cacheHandler` (singular) — ISR, route handlers, fetch, image optimization
- `cacheHandlers` (plural) — `'use cache'` directive backends

```ts
// next.config.ts
const nextConfig = {
  cacheHandler: require.resolve('./cache-handler.mjs'),
  cacheHandlers: {
    default: require.resolve('./cache-handler-use-cache.mjs'),
  },
}
```

### 5. CDN Infrastructure Compatibility

| CDN | Edge Compute | Key-Value / Tags | Blob Storage | PPR Resuming |
|-----|-------------|-----------------|--------------|:---:|
| Cloudflare | Workers | KV | R2 | ✅ (worker) |
| Akamai | EdgeWorkers | EdgeKV | Object Storage | ✅ (worker) |
| Amazon CloudFront | Lambda@Edge | KeyValueStore | S3 | ✅ (Lambda) |
| Fastly | Compute | KV Store | Object Storage | ✅ (WASM) |
| Azure | Functions | Managed Redis | Blob Storage | ✅ (server) |
| Google Cloud | Cloud Run | Various KV | Cloud Storage | ✅ (server) |

> เหล่านี้คือ building blocks — ส่วนใหญ่ community adapters deploy เป็น Docker/Node.js server

### 6. Adapters

Adapter API ให้ platforms customize build + deploy output:

```ts
// next.config.ts
const nextConfig = {
  adapterPath: './my-adapter',
}
```

**Adapter ทำอะไร:**
- Run at build time
- Produce platform-specific output
- ใช้ public API (ไม่มี private hooks)

**Integration surface:**
- Adapter → build-time output
- `cacheHandler` → runtime server cache (ISR, fetch, images)
- `cacheHandlers` → runtime `'use cache'` backends

### 7. Verified Adapters

Requirements:
1. **Open source** — community + Next.js team inspect ได้
2. **Runs compatibility test suite** — visibility into feature support

| Platform | Status |
|----------|--------|
| Vercel | ✅ Verified |
| Bun | ✅ Verified |
| Cloudflare | Working toward verified |
| Netlify | Working toward verified |

**Benefits ของ verified adapters:**
- Coordinated testing ก่อน major releases
- Early access to API changes
- Direct support จาก Next.js team
- Listed ใน official documentation

### 8. Deployment Decision Guide

```
เลือก Platform:

├── ต้องการทุก feature + optimal performance
│   └── Vercel (verified adapter, full CDN integration)
│
├── ต้องการทุก feature + self-host
│   ├── Single instance → next start (ง่ายที่สุด)
│   ├── Multiple instances → next start + shared cache (Redis, etc.)
│   └── Docker → output: 'standalone' + shared cache
│
├── ต้องการ edge deployment
│   ├── Cloudflare Workers → Cloudflare adapter
│   ├── AWS Lambda@Edge → custom adapter
│   └── Other CDN → check CDN compatibility table
│
├── ไม่ต้องการ server (static only)
│   └── output: 'export' → S3, GitHub Pages, Nginx
│
└── Existing infrastructure
    └── Custom adapter + cacheHandler configuration
```

### 9. Multi-Instance Considerations

| Concern | Single Instance | Multiple Instances |
|---------|:-:|:-:|
| ISR revalidation | ✅ Works | ⚠️ Needs shared cache |
| On-demand revalidation | ✅ Works | ⚠️ Tag propagation needs shared cache |
| Cache consistency | ✅ Always consistent | ⚠️ May diverge without shared cache |
| `use cache` | ✅ Works | ⚠️ Needs shared cache for consistency |
| Server Actions | ✅ Works | ✅ Works (stateless) |
| Proxy | ✅ Works | ✅ Works (stateless) |

### 10. Streaming Requirements

Features ที่ต้องการ streaming:
- Server Components (progressive delivery)
- PPR (static shell + dynamic holes)
- Cache Components
- Server Actions (streaming response)

**ถ้า platform ไม่รองรับ streaming:**
- Responses ถูก buffer แล้วส่งทั้งก้อน
- ยังทำงานได้ แต่สูญเสีย streaming performance benefit
- TTFB จะช้ากว่า

## Quick Reference

| Deployment Target | Features | Setup Complexity |
|-------------------|----------|:-:|
| `next start` (single) | All | ง่าย |
| `next start` + shared cache | All + multi-instance | ปานกลาง |
| Docker standalone | All | ปานกลาง |
| Vercel | All + optimal perf | ง่ายมาก |
| Static export | Limited | ง่าย |
| Custom adapter | All (varies) | ซับซ้อน |

## สรุป

1. **Minimum:** Node.js server (`next start`) รองรับทุก feature
2. **Streaming:** Required สำหรับ Server Components, PPR, Cache Components
3. **Shared cache:** Recommended สำหรับ multi-instance (ISR, on-demand revalidation)
4. **Adapters:** Public API, ใครก็สร้างได้ — verified = open source + test suite
5. **Single instance:** ง่ายที่สุด, ทุกอย่างทำงาน
6. **Multi-instance:** ต้อง shared cache เพื่อ consistency
7. **Performance fidelity:** Platform-specific optimization (CDN, edge, PPR resuming)
