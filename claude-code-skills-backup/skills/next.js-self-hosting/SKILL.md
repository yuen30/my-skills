---
name: Next.js Self-Hosting
description: Expert guidance on self-hosting Next.js — reverse proxy, caching, ISR, multi-instance, Docker, streaming, version skew, and environment variables.
---

# Next.js Self-Hosting

Expert guidance on self-hosting Next.js — reverse proxy, caching, ISR, multi-instance, Docker, streaming, version skew, and environment variables.

@doc-version: 16.2.6

## Core Concepts

Self-hosting Next.js = run `next start` on your own infrastructure (Node.js server, Docker, Kubernetes) — ทุก feature ทำงานได้ แต่ต้อง configure บางอย่างเอง

## Guidelines

### 1. Reverse Proxy (แนะนำ)

ใช้ nginx/Caddy/Traefik หน้า Next.js server:

```nginx
# nginx.conf
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**ข้อดี:** Handle malformed requests, slow connections, rate limiting, payload limits — offload จาก Next.js

### 2. Streaming Support

ต้อง disable buffering สำหรับ streaming (PPR, Suspense):

```js
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*{/}?',
        headers: [
          { key: 'X-Accel-Buffering', value: 'no' },
        ],
      },
    ]
  },
}
```

**ตรวจสอบทั้ง chain:**
- Load balancer → support chunked transfer / HTTP/2
- Reverse proxy → pass through without buffering
- ถ้า buffer → PPR ไม่ได้ TTFB advantage

### 3. Environment Variables

```tsx
import { connection } from 'next/server'

export default async function Page() {
  await connection() // Force dynamic rendering

  // Runtime env — evaluate ตอน request (ไม่ใช่ build)
  const dbUrl = process.env.DATABASE_URL
  // ...
}
```

- **Server env** → runtime (dynamic rendering)
- **`NEXT_PUBLIC_`** → build-time (inlined)
- Docker: ใช้ singular image + runtime env ต่าง environment ได้

### 4. Caching and ISR

Default: file-system cache บน disk — ทำงานอัตโนมัติสำหรับ single instance

#### Custom Cache Handler (Multi-instance / Ephemeral)

```js
// next.config.js
module.exports = {
  cacheHandler: require.resolve('./cache-handler.js'),
  cacheMaxMemorySize: 0, // Disable in-memory caching
}
```

```js
// cache-handler.js
const cache = new Map()

module.exports = class CacheHandler {
  constructor(options) {
    this.options = options
  }

  async get(key) {
    return cache.get(key)
  }

  async set(key, data, ctx) {
    cache.set(key, {
      value: data,
      lastModified: Date.now(),
      tags: ctx.tags,
    })
  }

  async revalidateTag(tags) {
    tags = [tags].flat()
    for (let [key, value] of cache) {
      if (value.tags.some((tag) => tags.includes(tag))) {
        cache.delete(key)
      }
    }
  }

  resetRequestCache() {}
}
```

**Production:** ใช้ Redis, DynamoDB, S3 แทน in-memory Map

### 5. Multi-Instance Deployments

#### Server Functions Encryption Key

ทุก instance ต้องใช้ key เดียวกัน:

```bash
# Generate key
openssl rand -base64 32

# Set env (ทุก instance)
NEXT_SERVER_ACTIONS_ENCRYPTION_KEY=your-generated-key next build
```

ถ้าไม่ตั้ง → "Failed to find Server Action" errors ข้าม instances

#### Deployment ID (Version Skew Protection)

```js
// next.config.js
module.exports = {
  deploymentId: process.env.DEPLOYMENT_VERSION,
}
```

- Detect client/server version mismatch
- Trigger hard navigation เมื่อ mismatch
- ป้องกัน missing assets, navigation failures

#### Shared Cache

```js
// next.config.js
module.exports = {
  cacheHandler: require.resolve('./redis-cache-handler.js'),
  cacheMaxMemorySize: 0,
}
```

#### Tag Coordination (`refreshTags`)

```js
// cache-handler.js
module.exports = class CacheHandler {
  async refreshTags() {
    // Sync tag state จาก shared storage (Redis)
    // เรียกก่อนทุก request
    try {
      const recentInvalidations = await redis.getRecentTags()
      this.localTags.merge(recentInvalidations)
    } catch (error) {
      // Must catch! ถ้า throw → request fails
      console.error('Failed to refresh tags:', error)
    }
  }

  async revalidateTag(tags) {
    // Write invalidation ไป shared storage
    await redis.set(`tag:${tag}`, Date.now())
  }
}
```

### 6. Build ID Consistency

```js
// next.config.js
module.exports = {
  generateBuildId: async () => {
    return process.env.GIT_HASH
  },
}
```

ใช้เมื่อ rebuild ต่าง environment — ให้ build ID เดียวกัน

### 7. Image Optimization

- ทำงาน zero-config กับ `next start`
- glibc Linux: อาจต้อง [configure sharp](https://sharp.pixelplumbing.com/install#linux-memory-allocator)
- Static export: ต้อง custom image loader
- ปิดได้ด้วย `unoptimized: true`

### 8. `after()` — Graceful Shutdown

```bash
# Send SIGINT or SIGTERM for graceful shutdown
kill -SIGTERM <pid>
```

- Next.js จะ finish in-flight requests
- Execute pending `after()` callbacks
- แนะนำ drain period 10-30 seconds

### 9. Static Assets on CDN

```js
// next.config.js
module.exports = {
  assetPrefix: 'https://cdn.example.com',
}
```

- JS/CSS served จาก CDN domain
- Trade-off: extra DNS + TLS resolution

## Multi-Instance Checklist

```
Multi-Instance Self-Hosting:
□ NEXT_SERVER_ACTIONS_ENCRYPTION_KEY — same key ทุก instance
□ deploymentId — version skew protection
□ Custom cache handler — shared storage (Redis, S3)
□ refreshTags() — tag coordination ข้าม instances
□ generateBuildId — consistent build ID
□ Streaming support — disable buffering ทั้ง chain
□ Graceful shutdown — SIGTERM + drain period
```

## Architecture

```
Single Instance:
Client → Reverse Proxy → Next.js Server (next start)
                         └── File-system cache (disk)

Multi-Instance:
Client → Load Balancer → Reverse Proxy → Next.js Instance 1
                                       → Next.js Instance 2
                                       → Next.js Instance 3
                                              ↕
                                       Shared Cache (Redis)
```

## Quick Reference

| Feature | Single Instance | Multi-Instance |
|---------|:-:|:-:|
| ISR | ✅ Auto (disk) | ⚠️ Needs shared cache |
| On-demand revalidation | ✅ Auto | ⚠️ Needs tag coordination |
| Server Actions | ✅ Auto | ⚠️ Needs encryption key |
| Image Optimization | ✅ Auto | ✅ Auto |
| Streaming | ✅ (disable proxy buffering) | ✅ (disable proxy buffering) |
| Version skew | N/A | ⚠️ Needs deploymentId |

## สรุป

1. **Reverse proxy** — nginx/Caddy หน้า Next.js (security, rate limiting)
2. **Streaming** — disable buffering ทั้ง chain (nginx, LB)
3. **Single instance** — ทุกอย่างทำงาน auto (file-system cache)
4. **Multi-instance** — ต้อง shared cache + encryption key + deploymentId
5. **Tag coordination** — `refreshTags()` sync จาก Redis ก่อนทุก request
6. **Runtime env** — `connection()` + `process.env` สำหรับ Docker promotion
7. **Graceful shutdown** — SIGTERM + drain period 10-30s
8. **`assetPrefix`** — serve static assets จาก CDN
