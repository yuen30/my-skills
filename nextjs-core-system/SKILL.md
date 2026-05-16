---
name: Next.js App Router
description: Expert guidance for building full-stack web applications with Next.js 16 App Router, including Server Components, caching, data fetching, and deployment.
---

# Next.js App Router

Expert guidance for building full-stack web applications with Next.js 16 App Router, including Server Components, caching, data fetching, and deployment.

@doc-version: 16.2.6

## Capabilities

- Set up and configure Next.js projects with TypeScript
- Build pages, layouts, and navigation with the App Router
- Use Server and Client Components effectively
- Fetch, mutate, cache, and revalidate data
- Handle errors, loading states, and streaming
- Optimize images, fonts, and metadata
- Create API Route Handlers
- Deploy to Vercel, self-host, or static export
- Implement authentication, internationalization, and multi-tenant patterns

## Guidelines

### Project Setup

```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir
```

### Project Structure

#### Top-level Folders

| Folder | Purpose |
|--------|---------|
| `app` | App Router (core routing) |
| `pages` | Pages Router (legacy) |
| `public` | Static assets (images, fonts, etc.) |
| `src` | Optional — separates source code from config files |

#### Top-level Config Files

| File | Purpose |
|------|---------|
| `next.config.js` | Next.js configuration |
| `package.json` | Dependencies and scripts |
| `middleware.ts` | Request-time middleware (root only) |
| `proxy.ts` | Proxy requests configuration |
| `.env` / `.env.local` | Environment variables |
| `tsconfig.json` | TypeScript configuration |

#### Routing File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Page UI (makes route publicly accessible) |
| `layout.tsx` | Shared UI for segment and children |
| `loading.tsx` | Loading UI (Suspense boundary) |
| `error.tsx` | Error UI (Error boundary) |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint (no UI) |
| `template.tsx` | Re-rendered layout (no state preservation) |
| `default.tsx` | Parallel route fallback |

#### Dynamic Routes

| Convention | Purpose |
|-----------|---------|
| `[slug]` | Dynamic segment |
| `[...slug]` | Catch-all segment |
| `[[...slug]]` | Optional catch-all segment |

#### Route Organization

| Convention | Purpose |
|-----------|---------|
| `(folderName)` | Route Group — groups routes without affecting URL |
| `_folderName` | Private Folder — excluded from routing (internal logic, components) |
| `@slot` | Parallel Routes — render multiple pages in same layout |
| `(.)folder` | Intercepting Routes — intercept navigation (e.g., modals) |

#### Metadata File Conventions

| File | Purpose |
|------|---------|
| `favicon.ico` | Browser tab icon |
| `icon.png` | App icon |
| `apple-icon.png` | Apple device icon |
| `opengraph-image.png` | Social share image (OG) |
| `twitter-image.png` | Twitter card image |
| `sitemap.xml` | Search engine sitemap |
| `robots.txt` | Crawler instructions |

#### Recommended Project Organization Strategies

**Strategy 1: Project files outside `app`** — keep all code (components, lib, utils) at root, use `app` only for routing:

```
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       └── page.tsx
├── components/
│   ├── ui/
│   └── shared/
├── lib/
└── middleware.ts
```

**Strategy 2: Top-level folders inside `app`** — shared code lives inside `app` using private folders:

```
├── app/
│   ├── _components/
│   ├── _lib/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       └── page.tsx
```

**Strategy 3: Split by feature/route (Colocation)** — related files live next to their route:

```
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       ├── _components/
│       │   └── stats-card.tsx
│       ├── _lib/
│       │   └── fetch-stats.ts
│       ├── layout.tsx
│       └── page.tsx
```

#### Full Example Structure

```
src/
├── app/
│   ├── layout.tsx              # Root layout (required)
│   ├── page.tsx                # Home page (/)
│   ├── loading.tsx             # Global loading UI
│   ├── error.tsx               # Global error UI
│   ├── not-found.tsx           # 404 UI
│   ├── (marketing)/            # Route group — no URL impact
│   │   ├── about/page.tsx      # /about
│   │   └── blog/page.tsx       # /blog
│   ├── (shop)/                 # Another route group
│   │   ├── layout.tsx          # Separate layout for shop
│   │   └── products/page.tsx   # /products
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard layout
│   │   ├── page.tsx            # /dashboard
│   │   ├── @analytics/         # Parallel route slot
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx        # /dashboard/settings
│   ├── blog/
│   │   ├── [slug]/             # Dynamic: /blog/:slug
│   │   │   └── page.tsx
│   │   └── [...categories]/    # Catch-all: /blog/a/b/c
│   │       └── page.tsx
│   └── api/
│       └── posts/
│           └── route.ts        # API: /api/posts
├── components/
├── lib/
└── middleware.ts
```

### Server vs Client Components

By default, all components in the App Router are **Server Components**.

```tsx
// Server Component (default) — runs on the server only
export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()
  return <div>{json.title}</div>
}
```

```tsx
'use client'
// Client Component — runs on the client (and server for SSR)
import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

**When to use Client Components:**
- `useState`, `useEffect`, `useReducer` or other hooks
- Event handlers (`onClick`, `onChange`, etc.)
- Browser-only APIs (`window`, `localStorage`)
- Class components

**Keep Server Components as default** — only add `'use client'` when needed.

### Layouts and Pages

```tsx
// app/layout.tsx — Root Layout (required)
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

```tsx
// app/dashboard/layout.tsx — Nested Layout
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <nav>Sidebar</nav>
      <main>{children}</main>
    </div>
  )
}
```

### Linking and Navigation

```tsx
import Link from 'next/link'

<Link href="/dashboard">Dashboard</Link>
<Link href={`/blog/${post.slug}`}>Read more</Link>
```

```tsx
'use client'
import { useRouter } from 'next/navigation'

export function NavigateButton() {
  const router = useRouter()
  return <button onClick={() => router.push('/dashboard')}>Go</button>
}
```

### Data Fetching

```tsx
// Server Component — fetch directly (no useEffect needed)
async function getData() {
  const res = await fetch('https://api.example.com/data')
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export default async function Page() {
  const data = await getData()
  return <main>{data.title}</main>
}
```

### Caching with "use cache"

```tsx
'use cache'

export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  const json = await data.json()
  return <div>{json.title}</div>
}
```

```tsx
import { cacheLife } from 'next/cache'

async function getData() {
  'use cache'
  cacheLife('hours')
  const res = await fetch('https://api.example.com/data')
  return res.json()
}
```

### Revalidation

```tsx
import { revalidatePath, revalidateTag } from 'next/cache'

// Time-based: configure via cacheLife
// On-demand:
revalidatePath('/blog')
revalidateTag('posts')
```

```tsx
// Tag a cached function
import { cacheTag } from 'next/cache'

async function getPosts() {
  'use cache'
  cacheTag('posts')
  return fetch('/api/posts').then(r => r.json())
}
```

### Server Actions (Mutating Data)

```tsx
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  await db.post.create({ data: { title } })
  revalidatePath('/posts')
}
```

```tsx
// app/posts/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPost() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

### Route Handlers (API Routes)

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const posts = await db.post.findMany()
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await db.post.create({ data: body })
  return NextResponse.json(post, { status: 201 })
}
```

### Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)
  return <article>{post.content}</article>
}

// Static generation for dynamic routes
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({ slug: post.slug }))
}
```

### Loading and Streaming

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <main>
      <h1>Dashboard</h1>
      <Suspense fallback={<div>Loading stats...</div>}>
        <AsyncStats />
      </Suspense>
    </main>
  )
}
```

### Error Handling

```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### Middleware

```tsx
// middleware.ts (root of project)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  if (!request.cookies.get('session')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*'],
}
```

### Image Optimization

```tsx
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority
/>
```

### Font Optimization

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  )
}
```

### Metadata and SEO

```tsx
// app/layout.tsx or app/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My App',
  description: 'Built with Next.js',
  openGraph: {
    title: 'My App',
    description: 'Built with Next.js',
    images: ['/og.png'],
  },
}
```

```tsx
// Dynamic metadata
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)
  return { title: post.title, description: post.excerpt }
}
```

### Environment Variables

- `.env.local` — local secrets (gitignored)
- `.env` — defaults
- `NEXT_PUBLIC_*` — exposed to the browser

```tsx
// Server only
const apiKey = process.env.API_SECRET_KEY

// Client accessible
const publicUrl = process.env.NEXT_PUBLIC_API_URL
```

### Deployment

```bash
# Build for production
next build

# Self-host with Node.js
next start

# Static export
# next.config.ts: output: 'export'
next build
```

### next.config.ts

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.example.com' },
    ],
  },
  experimental: {
    viewTransition: true,
    reactCompiler: true,
  },
}

export default nextConfig
```

## Key Patterns

| Pattern | Approach |
|---------|----------|
| Auth | Middleware + Server Actions |
| Forms | Server Actions + `useActionState` |
| Data fetching | Server Components + `"use cache"` |
| Real-time | Client Components + WebSocket/SSE |
| i18n | Dynamic routes `[locale]/` + middleware |
| Multi-tenant | Middleware + dynamic subdomains |
| Static pages | `generateStaticParams` + ISR |
| API | Route Handlers (`app/api/route.ts`) |

## File Conventions

| File | Purpose |
|------|---------|
| `layout.tsx` | Shared UI for a segment and its children |
| `page.tsx` | Unique UI of a route (makes route accessible) |
| `loading.tsx` | Loading UI (Suspense boundary) |
| `error.tsx` | Error UI (Error boundary) |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint (no UI) |
| `template.tsx` | Re-rendered layout (no state preservation) |
| `default.tsx` | Parallel route fallback |
| `middleware.ts` | Request-time logic (root only) |

## Common Commands

| Command | Description |
|---------|-------------|
| `npx create-next-app@latest` | Create new project |
| `next dev --turbopack` | Dev server with Turbopack |
| `next build` | Production build |
| `next start` | Start production server |
| `next lint` | Run ESLint |

## Dependencies

```json
{
  "next": "^16",
  "react": "^19",
  "react-dom": "^19",
  "typescript": "^5"
}
```
