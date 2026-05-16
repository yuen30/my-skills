---
name: Next.js Production Checklist
description: Comprehensive checklist for optimizing Next.js applications before production — performance, security, SEO, accessibility, and bundle analysis.
---

# Next.js Production Checklist

Comprehensive checklist for optimizing Next.js applications before production — performance, security, SEO, accessibility, and bundle analysis.

@doc-version: 16.2.6

## Automatic Optimizations (No Config Needed)

| Optimization | Description |
|-------------|-------------|
| Server Components | Default — no client JS for server-rendered content |
| Code-splitting | Automatic per route segment |
| Prefetching | Links in viewport prefetched in background |
| Prerendering | Server + Client Components prerendered at build time |
| Caching | Data requests, rendered results, static assets cached |

## During Development

### Routing and Rendering

```
□ Use Layouts for shared UI + partial rendering
□ Use <Link> for client-side navigation + prefetching
□ Create custom error pages (error.tsx, not-found.tsx)
□ Follow Server/Client Component composition patterns
□ Place "use client" boundaries as low as possible
□ Wrap Request-time APIs (cookies, searchParams) in <Suspense>
□ Avoid Request-time APIs in Root Layout (opts entire app into dynamic)
```

### Data Fetching and Caching

```
□ Fetch data in Server Components (not Route Handlers from Server Components)
□ Use Route Handlers only for Client Component → backend access
□ Use loading.tsx + Suspense for streaming
□ Fetch data in parallel (Promise.all) to reduce waterfalls
□ Verify data requests are cached appropriately
□ Cache non-fetch requests (unstable_cache or "use cache")
□ Use public/ directory for static assets
```

### UI and Accessibility

```
□ Use Server Actions for form submissions + server-side validation
□ Add app/global-error.tsx for uncaught errors
□ Add app/global-not-found.tsx for unmatched routes
□ Use next/font (auto-host, no layout shift)
□ Use next/image (auto-optimize, no layout shift, WebP)
□ Use next/script (defer third-party, don't block main thread)
□ Use eslint-plugin-jsx-a11y for accessibility linting
```

### Security

```
□ Use Tainting API to prevent sensitive data exposure
□ Verify auth + authorization inside every Server Action
□ Move database access to server-only Data Access Layer
□ Add rate limiting for expensive operations
□ Ensure .env.* files are in .gitignore
□ Only prefix public variables with NEXT_PUBLIC_
□ Consider Content Security Policy (CSP)
□ Don't rely on Proxy/layout alone for auth (Server Actions are separate endpoints)
```

### Metadata and SEO

```
□ Use Metadata API (title, description, openGraph)
□ Create OG images (static or dynamic with ImageResponse)
□ Generate sitemap.xml
□ Generate robots.txt
□ Add structured data (JSON-LD)
```

### Type Safety

```
□ Use TypeScript
□ Enable Next.js TypeScript plugin
□ Use strict mode in tsconfig.json
```

## Before Going to Production

### Build and Test

```bash
# 1. Build locally — catch errors
next build

# 2. Test in production-like environment
next start

# 3. Run Lighthouse in incognito
# Chrome DevTools → Lighthouse tab
```

### Core Web Vitals

```
□ Run Lighthouse (simulated test)
□ Check field data (CrUX, Vercel Analytics)
□ Use useReportWebVitals hook for real user metrics
□ Target: LCP < 2.5s, INP < 200ms, CLS < 0.1
```

### Bundle Analysis

```bash
# Install analyzer
npm install @next/bundle-analyzer

# Run with ANALYZE=true
ANALYZE=true npm run build
```

**Tools:**
- [@next/bundle-analyzer](https://www.npmjs.com/package/@next/bundle-analyzer) — visualize bundles
- [Import Cost](https://marketplace.visualstudio.com/items?itemName=wix.vscode-import-cost) — VS Code extension
- [Bundle Phobia](https://bundlephobia.com/) — check package size before installing
- [Package Phobia](https://packagephobia.com/) — install size
- [bundlejs](https://bundlejs.com/) — tree-shaking analysis

## Performance Patterns

### Reduce Client JS

```tsx
// ✅ Server Component (default) — no JS sent to client
export default async function Page() {
  const data = await getData()
  return <div>{data.title}</div>
}

// ✅ "use client" only where needed (interactive parts)
// Keep boundary as low as possible in component tree
```

### Optimize Images

```tsx
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // Above-the-fold only
/>
```

### Optimize Fonts

```tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

// Apply in layout — self-hosted, no external requests
```

### Streaming

```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <>
      <h1>Dashboard</h1> {/* Sent immediately */}
      <Suspense fallback={<Skeleton />}>
        <SlowComponent /> {/* Streamed when ready */}
      </Suspense>
    </>
  )
}
```

### Parallel Data Fetching

```tsx
// ✅ Parallel — fast
const [posts, users] = await Promise.all([
  getPosts(),
  getUsers(),
])

// ❌ Sequential — slow (waterfall)
const posts = await getPosts()
const users = await getUsers()
```

## Security Checklist

| Area | Check |
|------|-------|
| Server Actions | Auth + authorization inside every action |
| Data Access | `server-only` Data Access Layer |
| Environment | `.env.local` gitignored, no secrets in `NEXT_PUBLIC_` |
| Input validation | Zod/schema validation in Server Actions |
| CSP | Nonce-based or `'unsafe-inline'` |
| Rate limiting | Expensive operations protected |
| Tainting | Sensitive objects/values tainted |
| CSRF | Server Actions use POST + origin check (built-in) |

## Quick Reference

| Category | Key Actions |
|----------|-------------|
| Performance | Server Components, code-splitting, prefetching, streaming |
| Images | `next/image` with `priority` for LCP |
| Fonts | `next/font` (self-hosted, no CLS) |
| Scripts | `next/script` (defer, don't block) |
| Security | Auth in actions, DAL, CSP, env vars |
| SEO | Metadata API, OG images, sitemap, robots |
| Accessibility | `eslint-plugin-jsx-a11y`, semantic HTML |
| Bundle | `@next/bundle-analyzer`, lazy loading |
| Testing | `next build` + `next start` + Lighthouse |

## สรุป

1. **Server Components default** — ลด client JS อัตโนมัติ
2. **`<Link>` + Layouts** — prefetching + partial rendering
3. **Streaming + Suspense** — ไม่ block ทั้ง route
4. **Parallel fetch** — `Promise.all` ลด waterfalls
5. **Auth ใน Server Actions** — ไม่พึ่ง Proxy/layout alone
6. **Metadata API** — SEO + OG images + sitemap
7. **Bundle analysis** — หา dependencies ที่ใหญ่เกินไป
8. **`next build` + `next start`** — test ก่อน deploy
9. **Lighthouse + Web Vitals** — measure real performance
