---
name: Next.js Environment Variables
description: Expert guidance on using environment variables in Next.js — .env files, NEXT_PUBLIC_ prefix, load order, runtime vs build-time, and testing environments.
---

# Next.js Environment Variables

Expert guidance on using environment variables in Next.js — .env files, NEXT_PUBLIC_ prefix, load order, runtime vs build-time, and testing environments.

@doc-version: 16.2.6

## Core Concepts

Next.js มี built-in support สำหรับ environment variables:
- `.env` files → load เข้า `process.env` อัตโนมัติ
- `NEXT_PUBLIC_` prefix → expose ไป browser (inline ตอน build)
- Server-only variables → ปลอดภัย ไม่หลุดไป client

## Guidelines

### 1. Loading Environment Variables

```env
# .env
DB_HOST=localhost
DB_USER=myuser
DB_PASS=mypassword
```

ใช้ใน server code:

```ts
// app/api/route.ts
export async function GET() {
  const db = await myDB.connect({
    host: process.env.DB_HOST,
    username: process.env.DB_USER,
    password: process.env.DB_PASS,
  })
  // ...
}
```

#### Multiline Variables

```env
# .env
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
Kh9NV...
-----END DSA PRIVATE KEY-----"

# หรือใช้ \n
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nKh9NV...\n-----END DSA PRIVATE KEY-----\n"
```

#### Variable References

```env
# .env
TWITTER_USER=nextjs
TWITTER_URL=https://x.com/$TWITTER_USER
# ผลลัพธ์: https://x.com/nextjs

# Escape $ ถ้าต้องการใช้จริง
PRICE=\$100
```

### 2. `NEXT_PUBLIC_` — Browser Variables

ตัวแปรที่ต้องการใช้ใน browser ต้อง prefix ด้วย `NEXT_PUBLIC_`:

```env
# .env
NEXT_PUBLIC_ANALYTICS_ID=abcdefghijk
NEXT_PUBLIC_API_URL=https://api.example.com

# ❌ ไม่ expose ไป browser
SECRET_API_KEY=super_secret
DATABASE_URL=postgres://...
```

```tsx
// ✅ ใช้ได้ทั้ง server + client
const analyticsId = process.env.NEXT_PUBLIC_ANALYTICS_ID

// ✅ Server only — ปลอดภัย
const dbUrl = process.env.DATABASE_URL
```

**สำคัญ:** `NEXT_PUBLIC_` variables ถูก **inline ตอน build** — ไม่เปลี่ยนตาม runtime environment

```ts
// ✅ ถูก inline
setupAnalytics(process.env.NEXT_PUBLIC_ANALYTICS_ID)

// ❌ ไม่ถูก inline (dynamic lookup)
const varName = 'NEXT_PUBLIC_ANALYTICS_ID'
setupAnalytics(process.env[varName])

// ❌ ไม่ถูก inline
const env = process.env
setupAnalytics(env.NEXT_PUBLIC_ANALYTICS_ID)
```

### 3. Runtime Environment Variables (Server)

อ่าน env variables ตอน runtime ใน dynamic rendering:

```tsx
// app/page.tsx
import { connection } from 'next/server'

export default async function Page() {
  await connection() // Force dynamic rendering

  // ค่านี้ถูก evaluate ตอน runtime (ไม่ใช่ build time)
  const value = process.env.MY_VALUE

  return <div>{value}</div>
}
```

**ข้อดี:** ใช้ Docker image เดียว promote ผ่านหลาย environments ได้

### 4. Environment Variable Load Order

ค้นหาตามลำดับ (หยุดเมื่อเจอ):

1. `process.env` (system environment)
2. `.env.$(NODE_ENV).local` (e.g., `.env.development.local`)
3. `.env.local` (ไม่โหลดเมื่อ `NODE_ENV=test`)
4. `.env.$(NODE_ENV)` (e.g., `.env.development`)
5. `.env`

### 5. File Conventions

| File | Purpose | Git |
|------|---------|:---:|
| `.env` | Default ทุก environment | ✅ Commit |
| `.env.local` | Local overrides (secrets) | ❌ Gitignore |
| `.env.development` | Development defaults | ✅ Commit |
| `.env.development.local` | Local dev overrides | ❌ Gitignore |
| `.env.production` | Production defaults | ✅ Commit |
| `.env.production.local` | Local prod overrides | ❌ Gitignore |
| `.env.test` | Test defaults | ✅ Commit |
| `.env.test.local` | Local test overrides | ❌ Gitignore |

> `.env` files ต้องอยู่ที่ project root (ไม่ใช่ใน `/src`)

### 6. Test Environment

```env
# .env.test
DATABASE_URL=postgres://localhost/test_db
API_URL=http://localhost:3001
```

- โหลดเมื่อ `NODE_ENV=test`
- `.env.local` **ไม่ถูกโหลด** ใน test (ให้ทุกคนได้ผลเหมือนกัน)
- `.env.development` และ `.env.production` ไม่ถูกโหลดใน test

#### Load Env ใน Test Setup (Jest)

```ts
// jest.setup.ts
import { loadEnvConfig } from '@next/env'

export default async () => {
  const projectDir = process.cwd()
  loadEnvConfig(projectDir)
}
```

### 7. `@next/env` — Load Outside Next.js Runtime

สำหรับ ORM configs, test runners, scripts ที่อยู่นอก Next.js:

```bash
npm install @next/env
```

```ts
// envConfig.ts
import { loadEnvConfig } from '@next/env'

const projectDir = process.cwd()
loadEnvConfig(projectDir)
```

```ts
// orm.config.ts
import './envConfig'

export default defineConfig({
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
})
```

### 8. Best Practices

```env
# .env.local (gitignored — secrets)
DATABASE_URL=postgres://user:pass@host:5432/db
AUTH_SECRET=super_secret_key
STRIPE_SECRET_KEY=sk_live_xxx

# .env (committed — non-sensitive defaults)
NEXT_PUBLIC_APP_NAME=My App
NEXT_PUBLIC_API_URL=https://api.example.com

# .env.development (committed — dev defaults)
NEXT_PUBLIC_API_URL=http://localhost:3001

# .env.production (committed — prod defaults)
NEXT_PUBLIC_API_URL=https://api.production.com
```

**กฎ:**
- ❌ อย่า commit secrets (`.env.local` ต้อง gitignore)
- ✅ Commit non-sensitive defaults (`.env`, `.env.development`)
- ✅ ใช้ `NEXT_PUBLIC_` เฉพาะค่าที่ safe สำหรับ browser
- ❌ อย่าใส่ API keys ใน `NEXT_PUBLIC_`
- ✅ ใช้ `server-only` ป้องกัน server env หลุดไป client

### 9. Docker / Multi-Environment

```env
# .env.production
# ค่าที่ inline ตอน build (NEXT_PUBLIC_)
NEXT_PUBLIC_APP_URL=https://myapp.com
```

```bash
# Runtime env (server-only) — ตั้งตอน run container
docker run -e DATABASE_URL=postgres://... -e AUTH_SECRET=xxx myapp
```

**`NEXT_PUBLIC_` = build-time** → ต้อง set ก่อน `next build`
**Server env = runtime** → set ตอน run ได้ (dynamic rendering)

## Quick Reference

| Variable Type | Available | When Evaluated |
|--------------|-----------|----------------|
| `process.env.SECRET` | Server only | Runtime |
| `process.env.NEXT_PUBLIC_X` | Server + Client | Build time (inlined) |
| Runtime server env | Server only | Request time (dynamic) |

| NODE_ENV | Auto-set by |
|----------|-------------|
| `development` | `next dev` |
| `production` | `next build`, `next start` |
| `test` | Test runners (Jest, Vitest) |

## สรุป

1. **`.env` files** — auto-loaded เข้า `process.env`
2. **`NEXT_PUBLIC_`** — expose ไป browser (inline ตอน build)
3. **Server variables** — ปลอดภัย ไม่หลุดไป client
4. **Load order** — `.local` > `.$(NODE_ENV)` > `.env`
5. **Test env** — `.env.test`, ไม่โหลด `.env.local`
6. **`@next/env`** — load env นอก Next.js runtime
7. **Docker** — `NEXT_PUBLIC_` = build-time, server env = runtime
8. **อย่า commit secrets** — ใช้ `.env.local` (gitignored)
