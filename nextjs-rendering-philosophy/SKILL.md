---
name: Next.js Rendering Philosophy
description: Expert guidance on Next.js rendering model — static/dynamic as a spectrum at component level, PPR, infrastructure implications, and platform portability.
---

# Next.js Rendering Philosophy

Expert guidance on Next.js rendering model — static/dynamic as a spectrum at component level, PPR, infrastructure implications, and platform portability.

@doc-version: 16.2.6

## Core Concepts

Next.js treats static and dynamic rendering as a **spectrum at the component level** — ไม่ใช่ binary choice ที่ route level:

- Single page = static shell + cached functions + dynamic streaming
- Cached function อยู่ใน dynamic route ได้
- Static page อัปเดตได้โดยไม่ redeploy

นี่คือสิ่งที่ **Partial Prerendering**, **Cache Components** (`use cache`), และ **on-demand revalidation** enable

## The Spectrum

### Traditional Approaches

| Approach | Boundary | Trade-off |
|----------|----------|-----------|
| Build-time prerendering | Entire site | Simple deploy, ต้อง rebuild ทุก change |
| Route-level boundaries | Per route | Static OR dynamic (all-or-nothing) |
| **Component-level (Next.js)** | Per component | Flexible, infrastructure complexity |

### Next.js Component-level Model

```
Single Page Response:
┌─────────────────────────────────────┐
│ Static Shell (instant)              │ ← Prerendered at build
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Cached Function (revalidatable) │ │ ← "use cache" + cacheLife
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Dynamic Section (streamed)      │ │ ← Request-time, Suspense
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

ทั้งหมดอยู่ใน **single streaming response** — ไม่ต้องแยก routes หรือ client-side fetches

## What This Enables

| Benefit | How |
|---------|-----|
| Faster perceived load | Static shell renders ทันที, dynamic streams ตามหลัง |
| Incremental caching | เพิ่ม `"use cache"` ทีละ function ได้ ไม่ต้อง decide upfront |
| Granular caching | Cache function ไม่ใช่ route, revalidate tag ไม่ใช่ deployment |
| No rebuild for content | On-demand revalidation อัปเดต cached content |

### Example: Granular Caching

```tsx
// Expensive DB query cached independently
async function getAnalytics() {
  'use cache'
  cacheLife('hours')
  cacheTag('analytics')
  return db.query('SELECT ...')  // Cache เฉพาะ function นี้
}

// Page ยังเป็น dynamic ได้
export default async function Dashboard() {
  return (
    <>
      <Suspense fallback={<Skeleton />}>
        <UserGreeting />  {/* Dynamic — per user */}
      </Suspense>
      <AnalyticsChart data={await getAnalytics()} />  {/* Cached */}
    </>
  )
}
```

## Infrastructure Implications

Component-level boundaries ย้าย complexity จาก application code → hosting platform:

| Requirement | Why | Without It |
|-------------|-----|-----------|
| **Streaming** | Static + dynamic ใน single response | Responses buffered (ยังทำงาน แต่ช้ากว่า) |
| **Cache coordination** | Multi-instance revalidation propagation | Each instance independent (stale divergence) |
| **Cache consistency** | HTML + RSC payload ต้อง sync | Mismatched content during navigation |
| **PPR shell at CDN** | Static shell at edge latency | Shell served from origin (ช้ากว่า) |

### Minimum: Single Node.js Server

```bash
next start  # ทุก feature ทำงาน — ไม่ต้อง infrastructure เพิ่ม
```

### Optimal: Full Platform Integration

```
CDN Edge → Static shell (instant)
         → Resume request to origin
Origin   → Stream dynamic content
Shared Cache → Coordinate revalidation across instances
```

## Portability and Fidelity

### Functional Fidelity (Binary)

ทุก feature ทำงานถูกต้อง — verified ด้วย adapter test suite:
- Pass = fully supported deployment target
- Fail = some features don't work

### Performance Fidelity (Spectrum)

Features ทำงานที่ optimal performance:
- PPR shell at CDN latency (ไม่ใช่ origin)
- ISR stale-while-revalidate with sub-second propagation
- แต่ละ platform achieve ต่างกัน

| Platform | Functional | Performance |
|----------|:-:|---|
| Node.js server | ✅ | Origin latency |
| Docker | ✅ | Origin latency |
| Vercel | ✅ | Edge + optimal |
| Other adapters | ✅ (if passes tests) | Varies |

## Comparison with Other Models

### Build-time Only (Gatsby, Astro static)

```
✅ Simple: upload files to CDN
❌ Every change = rebuild + redeploy
❌ Dynamic content = client-side fetch after load
```

### Route-level (Traditional SSR)

```
✅ Clear: route is static OR dynamic
❌ Mostly-static page with 1 dynamic element = fully dynamic
❌ Or: fetch dynamic element on client (flash, extra request)
```

### Component-level (Next.js)

```
✅ Static shell + cached + dynamic ใน single response
✅ Cache/revalidate per function
✅ No client-side fetch needed for dynamic content
❌ Infrastructure complexity (streaming, cache coordination)
```

## Practical Impact

### For Developers

- ไม่ต้อง decide "static or dynamic" per route upfront
- เพิ่ม `"use cache"` incrementally
- Revalidate specific data ไม่ใช่ทั้ง page
- Dynamic content ไม่ force entire page เป็น dynamic

### For Platform Engineers

- ต้องรองรับ streaming (chunked transfer / HTTP/2)
- Multi-instance ต้อง shared cache + tag coordination
- PPR optimization ต้อง shell storage + resume protocol
- CDN ต้อง respect Vary headers + `_rsc` parameter

## Quick Reference

| Concept | Description |
|---------|-------------|
| Static component | No data, prerendered at build |
| Cache component | `"use cache"`, prerendered + revalidatable |
| Dynamic component | Request-specific, streamed via Suspense |
| PPR | Static shell + dynamic holes in single response |
| Functional fidelity | All features work (binary) |
| Performance fidelity | Optimal speed (spectrum) |

## สรุป

1. **Static/dynamic = spectrum** ไม่ใช่ binary choice
2. **Boundary อยู่ที่ component level** ไม่ใช่ route level
3. **Single response** = static shell + cached + dynamic streaming
4. **`"use cache"`** = cache per function, revalidate per tag
5. **Infrastructure trade-off:** flexibility → platform complexity
6. **Minimum:** Node.js server (ทุก feature ทำงาน)
7. **Optimal:** CDN + streaming + shared cache + PPR resume
8. **Functional fidelity** = adapter test suite passes
