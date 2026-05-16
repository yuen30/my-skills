---
name: Next.js How Revalidation Works
description: Deep dive into Next.js revalidation internals — tag system, soft tags, multi-instance coordination, cache handlers, and graceful degradation.
---

# Next.js How Revalidation Works

Deep dive into Next.js revalidation internals — tag system, soft tags, multi-instance coordination, cache handlers, and graceful degradation.

@doc-version: 16.2.6

## Core Concepts

Revalidation คือการอัปเดต cached content โดยไม่ต้อง redeploy — เป็นส่วนสำคัญของ Next.js rendering model

**2 ประเภท:**
- **Time-based** — stale-while-revalidate pattern (serve stale → regenerate background)
- **On-demand** — explicit invalidation ด้วย `revalidateTag()` / `revalidatePath()`

## Guidelines

### 1. The Revalidation Model

#### Time-based

```
Request → Cache Hit (age > revalidate duration)
         ├── Serve stale content ทันที (user ไม่ต้องรอ)
         └── Background: regenerate fresh content
              └── Next request → ได้ fresh content
```

#### On-demand

```
revalidateTag('posts') called
         ├── Cache entries with tag 'posts' → marked stale
         └── Next request → triggers fresh render
```

### 2. What Gets Revalidated

เมื่อ route ถูก revalidate → Next.js regenerate **ทั้ง**:
- **HTML response** (สำหรับ direct navigation)
- **RSC Payload** (สำหรับ client-side navigation)

ทั้งสองถูกเก็บใน cache entry เดียวกัน

#### ถ้า HTML กับ RSC ไม่ sync กัน

| ปัญหา | ผลลัพธ์ |
|--------|---------|
| HTML จาก render A + RSC จาก render B | User เห็น content ไม่ตรงกันตอน client navigation |
| Cross-deployment skew | Client deploy A + Server deploy B = mismatch |

**แก้ไข:**
- Cache HTML + RSC ด้วยกัน (same TTL, same invalidation)
- Respect `Vary` header
- ใช้ `deploymentId` สำหรับ rolling deployments

### 3. Tag System Architecture

#### Explicit Tags (Developer-defined)

```ts
import { cacheTag } from 'next/cache'

async function getPosts() {
  'use cache'
  cacheTag('posts')  // ← explicit tag
  return db.post.findMany()
}

// Invalidate:
revalidateTag('posts')  // ← ทุก entry ที่มี tag 'posts' ถูก invalidate
```

#### Soft Tags (Auto-generated)

Next.js สร้าง soft tags อัตโนมัติจาก route path:

```
Route: /blog/hello

Soft tags generated:
├── _N_T_/layout
├── _N_T_/blog/layout
├── _N_T_/blog/hello/layout
└── _N_T_/blog/hello
```

**`revalidatePath('/blog/hello')` invalidates:**
- `_N_T_/layout`
- `_N_T_/blog/layout`
- `_N_T_/blog/hello/layout`
- `_N_T_/blog/hello`

> นี่คือเหตุผลที่ `revalidatePath` ทำงานผ่าน tag system เดียวกัน

### 4. Multi-Instance Considerations

#### Default Behavior (Single Instance)

- File-system cache handles consistency อัตโนมัติ
- Atomic writes on local filesystem
- Tag state maintained in memory
- ไม่ต้อง config เพิ่ม

#### Problem: Multiple Instances

```
Instance A: revalidateTag('posts') → local cache invalidated ✅
Instance B: ยังไม่รู้ → serve stale content ❌
Instance C: ยังไม่รู้ → serve stale content ❌
```

#### Solution: Shared Cache + Tag Coordination

Cache Handler API มี 2 hooks สำหรับ distributed coordination:

```ts
// cache-handler.ts
export default class MyCacheHandler {
  // เรียกเมื่อ revalidateTag() ถูก invoke
  async updateTags(tags: string[]) {
    // Write invalidation event ไป shared storage (Redis, DB)
    await redis.set(`tag:${tag}`, Date.now())
  }

  // เรียกก่อนทุก request — check shared storage
  async refreshTags() {
    try {
      // Read recent invalidation events จาก shared storage
      const recentTags = await redis.getRecentInvalidations()
      // Update local tag state
      this.localTags.merge(recentTags)
    } catch (error) {
      // ต้อง catch errors! ถ้า throw → request fails
      // Catch แล้ว serve potentially stale content แทน
      console.error('Failed to refresh tags:', error)
    }
  }
}
```

### 5. Implementation Patterns

#### Single Instance

```
✅ Default file-system cache
✅ No configuration needed
✅ Atomic local writes
✅ In-memory tag state
```

#### Multi-Instance with Shared Cache

```ts
// next.config.ts
const nextConfig = {
  cacheHandler: require.resolve('./cache-handler.mjs'),  // ISR, fetch, images
  cacheHandlers: {
    default: require.resolve('./use-cache-handler.mjs'), // 'use cache' entries
  },
}
```

**Steps:**
1. Store tag invalidation timestamps ใน shared service (Redis, DynamoDB)
2. Implement `updateTags()` → write to shared service
3. Implement `refreshTags()` → read from shared service (catch errors!)
4. Store cache entries (HTML + RSC) ใน shared storage

#### CDN Integration

- Respect `Vary` header
- ไม่ cache HTML กับ RSC แยก TTL
- ดู [CDN Caching guide](/docs/app/guides/cdn-caching)

### 6. Cache Handler API (Key Methods)

| Method | Called When | Purpose |
|--------|------------|---------|
| `get(key, softTags)` | Cache lookup | Return cached entry or `undefined` |
| `set(key, value, tags)` | After render | Store cache entry |
| `updateTags(tags)` | `revalidateTag()` called | Write invalidation to shared storage |
| `refreshTags()` | Before each request | Sync local state from shared storage |
| `getExpiration(tags)` | Checking staleness | Return latest revalidation timestamp |

#### `getExpiration()` Semantics

```ts
// Returns most recent revalidation timestamp across all tags
// Returns 0 if none have been revalidated
const timestamp = handler.getExpiration(['posts', 'user-123'])

// Entry is stale if:
if (timestamp > entry.timestamp) {
  // → trigger fresh render
}
```

#### Soft Tags in `get()`

```ts
async get(key: string, softTags?: string[]) {
  const entry = await this.storage.get(key)
  if (!entry) return undefined

  // Check if any soft tag has been invalidated after entry's timestamp
  if (softTags) {
    const expiration = await this.getExpiration(softTags)
    if (expiration > entry.timestamp) {
      return undefined // Treat as cache miss
    }
  }

  return entry
}
```

### 7. Graceful Degradation

| Failure | Behavior | Impact |
|---------|----------|--------|
| Cache write failure | Response still served (writes are async) | Entry lost, next request re-renders |
| Cache read failure | Handler returns `undefined` → fresh render | Extra server load |
| HTML/RSC inconsistency | Mismatched content during client navigation | Fix: cache together + respect Vary |
| Cross-deployment skew | `deploymentId` triggers hard navigation | Brief flash during deploy |
| `refreshTags()` failure | Must catch! Serve with last known state | Potentially stale content |

> **Key principle:** Cache failures = degraded performance (stale, extra renders), **not** broken applications

### 8. `cacheHandler` vs `cacheHandlers`

| Config | Covers | Used By |
|--------|--------|---------|
| `cacheHandler` (singular) | ISR, route handlers, patched fetch, `unstable_cache`, image optimization | Server cache paths |
| `cacheHandlers` (plural) | `'use cache'` directive backends | Cache Components |

```ts
// next.config.ts
const nextConfig = {
  // Server cache (ISR, fetch, images)
  cacheHandler: require.resolve('./server-cache-handler.mjs'),

  // 'use cache' directive
  cacheHandlers: {
    default: require.resolve('./use-cache-handler.mjs'),
  },
}
```

### 9. Pages Router vs App Router

| Feature | Pages Router | App Router |
|---------|-------------|-----------|
| On-demand ISR | `res.revalidate()`, `x-prerender-revalidate` | `revalidateTag()`, `revalidatePath()` |
| Cache handler | `cacheHandler` (singular) | `cacheHandler` + `cacheHandlers` |
| Tag system | ❌ | ✅ (explicit + soft tags) |
| Static optimization | Auto (pure static, not revalidated) | PPR + Cache Components |

## Quick Reference

| Concept | Description |
|---------|-------------|
| Explicit tag | Developer-defined via `cacheTag()` |
| Soft tag | Auto-generated from route path (`_N_T_/...`) |
| `revalidateTag()` | Invalidate by explicit tag |
| `revalidatePath()` | Invalidate by path (uses soft tags internally) |
| `updateTags()` | Cache handler: write invalidation to shared storage |
| `refreshTags()` | Cache handler: sync from shared storage (must catch errors) |
| `getExpiration()` | Return latest revalidation timestamp for tags |
| `deploymentId` | Detect cross-deployment skew → hard navigation |

## สรุป

1. **Revalidation regenerates HTML + RSC together** — ต้อง cache ด้วยกัน
2. **Tag system:** explicit tags (`cacheTag`) + soft tags (auto from path)
3. **`revalidatePath` ใช้ soft tags** — invalidate ทั้ง path hierarchy
4. **Single instance:** file-system cache ทำงานอัตโนมัติ
5. **Multi-instance:** ต้อง shared cache + `updateTags`/`refreshTags`
6. **`refreshTags()` ต้อง catch errors** — ถ้า throw = request fails
7. **Graceful degradation:** cache failures = stale content, ไม่ใช่ broken app
8. **CDN:** respect Vary header, cache HTML+RSC together
