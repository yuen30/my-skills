---
name: Next.js PPR Platform Guide
description: Expert guidance on implementing Partial Prerendering (PPR) on platforms — build artifacts, resume protocol, CDN integration, and adapter implementation.
---

# Next.js PPR Platform Guide

Expert guidance on implementing Partial Prerendering (PPR) on platforms — build artifacts, resume protocol, CDN integration, and adapter implementation.

@doc-version: 16.2.6

## Core Concepts

Partial Prerendering (PPR) รวม static + dynamic rendering ใน route เดียว:
- **Build time:** สร้าง static HTML shell + `postponedState` blob
- **Request time:** serve shell ทันที → stream dynamic content ตามหลัง

ผลลัพธ์: TTFB เร็วเท่า static page + dynamic content stream เข้ามา

## How PPR Works

### Build Time Output

สำหรับแต่ละ PPR route, Next.js สร้าง:

| Artifact | Description |
|----------|-------------|
| Static HTML shell | Content ที่ prerender ได้ + Suspense fallbacks |
| `postponedState` | Serialized blob (opaque — ห้ามแก้ไข) |
| RSC payload | Static portions สำหรับ client navigation |

### Request Time Flow

```
1. Request มาถึง
2. Server ส่ง static HTML shell ทันที (user เห็น content เร็ว)
3. Server resume rendering dynamic portions ด้วย postponedState
4. Dynamic content ถูก stream ไป client
5. React hydrate deferred Suspense boundaries
```

## Implementation Levels

### Level 1: Origin-Only (ง่ายที่สุด)

ทุก request ไปที่ Next.js server โดยตรง — `next start` ทำให้อัตโนมัติ:

```
Client → Next.js Server
         ├── Read shell from local cache
         ├── Send shell (streaming starts)
         ├── Render dynamic portions
         └── Stream dynamic content
```

**Requirements:** แค่ streaming HTTP responses — ไม่ต้อง infrastructure เพิ่ม

### Level 2: CDN Shell + Origin Compute (Optimized)

Cache shell ที่ CDN edge สำหรับ TTFB ที่เร็วขึ้น:

```
Client → CDN Edge
         ├── Serve cached shell ทันที (edge latency)
         ├── Send resume request ไป origin (parallel)
         │
         Origin Server
         ├── Render dynamic portions only
         └── Stream back to CDN
         │
CDN Edge ← Concatenate shell + dynamic → Client
```

**TTFB = edge latency** (ไม่ต้องรอ origin)

#### Lowest Latency: Edge Storage

Shell อยู่ใน edge KV store (populated ตอน build) แทน CDN cache — ไม่ต้อง cache hit/miss

## Resume Protocol

บอก Next.js handler ให้ render เฉพาะ dynamic portions (skip shell):

### CDN-to-Origin (HTTP)

```
POST /route HTTP/1.1
Host: origin.example.com
next-resume: 1
Content-Type: application/octet-stream

[postponedState blob as request body]
```

- Method: **POST**
- Header: `next-resume: 1`
- Body: `postponedState` blob
- Response: streamed dynamic content only

#### Server Action + PPR Resume

เมื่อ POST มีทั้ง Server Action + PPR resume:
- Body = `postponedState` + action body (concatenated)
- Header `x-next-resume-state-length` = byte length ของ postponedState prefix
- Handler แยก 2 ส่วนด้วย length

### Adapter-based (In-process)

ไม่ต้อง HTTP round-trip — invoke handler ตรง:

```ts
// Option 1: HTTP-style invocation
const req = new Request(url, {
  method: 'POST',
  headers: { 'next-resume': '1' },
  body: postponedState,
})
const res = await handler(req)

// Option 2: Direct metadata (bypass HTTP)
const res = await handler(req, res, {
  requestMeta: { postponed: postponedState },
})
```

### Finding PPR Routes in Build Output

```ts
// In adapter's onBuildComplete
for (const prerender of outputs.prerenders) {
  if (prerender.renderingMode === 'PARTIALLY_STATIC') {
    // This is a PPR route
    const shell = prerender.fallback.html
    const postponedState = prerender.fallback.postponedState
    const resumeHeaders = prerender.pprChain.headers
    // { 'next-resume': '1' }

    // Store in your cache/KV
    await store.put(prerender.path, { shell, postponedState })
  }
}
```

## Storing PPR Artifacts

**กฎสำคัญ:** Shell + postponedState ต้อง store + update **atomically**

```
❌ New shell + old postponedState = incorrect dynamic content
❌ Old shell + new postponedState = incorrect dynamic content
✅ Same-version shell + postponedState = correct
```

### Cache Updates (Revalidation)

ใช้ `requestMeta.onCacheEntryV2` จับ cache updates:

```ts
// In adapter
requestMeta.onCacheEntryV2 = (entry) => {
  // Atomically update both shell + postponedState
  await store.put(entry.path, {
    shell: entry.html,
    postponedState: entry.postponedState,
    timestamp: Date.now(),
  })
}
```

## Graceful Degradation

ถ้า postponedState ไม่มีหรือ stale:
- Fallback เป็น full server render
- User ได้ complete page (ไม่มี shell-first optimization)
- ไม่ broken — แค่ช้ากว่า

## Implementation Checklist

```
PPR Platform Implementation:
□ 1. Read PPR outputs at build time
     - Identify prerenders with renderingMode: 'PARTIALLY_STATIC'
     - Store shell HTML + postponedState in cache

□ 2. Serve shell at request time
     - Serve cached shell immediately
     - Begin streaming to client

□ 3. Resume dynamic rendering
     - CDN: POST + next-resume: 1 + postponedState body
     - Adapter: invoke handler directly
     - Stream response back to client

□ 4. Handle cache updates
     - Use onCacheEntryV2 for revalidation
     - Update shell + postponedState atomically

□ 5. Graceful degradation
     - Missing postponedState → full server render
     - Stale state → full server render
```

## Architecture Comparison

| Approach | TTFB | Complexity | Infrastructure |
|----------|------|:-:|---|
| Origin-only | Origin latency | ง่าย | Node.js server only |
| CDN cache shell | Edge latency | ปานกลาง | CDN + origin |
| Edge KV shell | Edge latency (no cache miss) | ซับซ้อน | Edge KV + origin |

## Quick Reference

| Concept | Detail |
|---------|--------|
| PPR route identifier | `renderingMode: 'PARTIALLY_STATIC'` |
| Resume header | `next-resume: 1` |
| Resume method | `POST` |
| Resume body | `postponedState` blob |
| Action + resume | `x-next-resume-state-length` header |
| Cache update hook | `requestMeta.onCacheEntryV2` |
| Adapter metadata | `requestMeta: { postponed: postponedState }` |

## สรุป

1. **PPR = static shell + dynamic stream** ใน route เดียว
2. **Origin-only:** ง่ายที่สุด — `next start` ทำให้อัตโนมัติ
3. **CDN shell:** TTFB = edge latency, dynamic stream จาก origin
4. **Resume protocol:** POST + `next-resume: 1` + postponedState body
5. **Atomic storage:** shell + postponedState ต้อง update ด้วยกัน
6. **Graceful degradation:** missing state → full render (ไม่ broken)
7. **Adapter:** ใช้ `onBuildComplete` + `onCacheEntryV2`
