---
name: Next.js Deploying
description: Expert guidance on deploying Next.js applications — Node.js server, Docker, static export, and platform adapters (Vercel, Cloudflare, AWS, etc.).
---

# Next.js Deploying

Expert guidance on deploying Next.js applications — Node.js server, Docker, static export, and platform adapters (Vercel, Cloudflare, AWS, etc.).

@doc-version: 16.2.6

## Core Concepts

Next.js รองรับ 4 วิธี deploy:

| Deployment Option | Feature Support |
|-------------------|----------------|
| Node.js server | All features |
| Docker container | All features |
| Static export | Limited (ไม่มี server) |
| Adapters | Varies (ขึ้นกับ platform) |

## Guidelines

### 1. Node.js Server

Deploy ไปยัง provider ที่รองรับ Node.js — รองรับทุก Next.js features:

#### package.json

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

#### Deploy Steps

```bash
# 1. Build
npm run build

# 2. Start production server
npm run start
```

#### Providers ที่รองรับ

- Flightcontrol
- Railway
- Replit
- Hostinger
- ทุก provider ที่รัน Node.js ได้

### 2. Docker

Deploy ด้วย Docker container — รองรับทุก Next.js features:

#### Standalone Output (แนะนำ)

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
}

export default nextConfig
```

#### Dockerfile (Production)

```dockerfile
FROM node:22-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

#### docker-compose.yml

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb

volumes:
  pgdata:
```

#### Docker Providers

- DigitalOcean
- Fly.io
- Google Cloud Run
- Render
- SST
- Kubernetes
- ทุก provider ที่รัน Docker ได้

> **Development:** ใช้ `npm run dev` แทน Docker ตอน dev บน Mac/Windows — performance ดีกว่า

### 3. Static Export

Deploy เป็น static HTML/CSS/JS — ไม่ต้องมี server:

#### Configuration

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
}

export default nextConfig
```

#### Build

```bash
npm run build
# Output: out/ folder with static files
```

#### Deploy ไปที่

- AWS S3 + CloudFront
- GitHub Pages
- Nginx
- Apache
- Netlify (static)
- Vercel (static)
- ทุก static hosting

#### ข้อจำกัด (ไม่รองรับ)

- Server Components ที่ fetch data ตอน request time
- Dynamic Routes ที่ไม่มี `generateStaticParams`
- Route Handlers ที่ไม่ใช่ GET static
- Proxy (Middleware)
- ISR (Incremental Static Regeneration)
- Image Optimization (ต้องใช้ external loader)
- Draft Mode

### 4. Adapters

Platform adapters ปรับ Next.js ให้ทำงานบน infrastructure เฉพาะ:

#### Verified Adapters (ผ่าน test suite)

| Platform | Status |
|----------|--------|
| Vercel | ✅ Verified |
| Bun | ✅ Verified |

#### Other Platforms (integration ของตัวเอง)

| Platform | Notes |
|----------|-------|
| Cloudflare | กำลังทำ verified adapter |
| Netlify | กำลังทำ verified adapter |
| AWS Amplify | Own integration |
| Firebase App Hosting | Own integration |
| Deno Deploy | Own integration |
| Appwrite Sites | Own integration |

#### Custom Adapter

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  adapterPath: './my-adapter',
}

export default nextConfig
```

## Deployment Checklist

### Before Deploy

```bash
# 1. Build and check for errors
npm run build

# 2. Test production locally
npm run start

# 3. Check environment variables
# .env.production or platform env settings
```

### Environment Variables

```bash
# Production environment variables (ตั้งที่ platform)
DATABASE_URL=postgres://...
API_SECRET_KEY=...
NEXT_PUBLIC_API_URL=https://api.example.com  # Client-accessible
```

### Performance

```ts
// next.config.ts
const nextConfig: NextConfig = {
  // Standalone output for Docker (smaller image)
  output: 'standalone',

  // Image optimization
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.example.com' },
    ],
  },

  // Compress responses
  compress: true,
}
```

## Decision Guide

```
เลือก Deployment Option:

├── ต้องการทุก features + ง่ายที่สุด
│   └── Vercel (verified adapter)
│
├── ต้องการทุก features + self-host
│   ├── มี Docker infrastructure → Docker + standalone output
│   └── มี Node.js server → Node.js server
│
├── ไม่ต้องการ server features (static site / SPA)
│   └── Static Export → S3, GitHub Pages, Nginx
│
└── ต้องการ platform เฉพาะ
    └── ใช้ Adapter ของ platform นั้น
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `next build` | Build for production |
| `next start` | Start Node.js production server |
| `next build` (with `output: 'export'`) | Generate static files |
| `next build` (with `output: 'standalone'`) | Generate minimal server for Docker |

| Config | Effect |
|--------|--------|
| `output: 'standalone'` | Minimal server output for Docker |
| `output: 'export'` | Static HTML/CSS/JS only |
| `adapterPath` | Custom platform adapter |
| `compress: true` | Gzip compression (default) |

## สรุป

1. **Node.js server** — `next build` + `next start`, รองรับทุก features
2. **Docker** — ใช้ `output: 'standalone'` + multi-stage Dockerfile
3. **Static export** — `output: 'export'`, limited features, ไม่ต้องมี server
4. **Adapters** — Vercel/Bun (verified), Cloudflare/Netlify/AWS (own integration)
5. **เลือก Vercel** ถ้าต้องการง่ายที่สุด + ทุก features
6. **เลือก Docker** ถ้าต้องการ self-host + ทุก features
