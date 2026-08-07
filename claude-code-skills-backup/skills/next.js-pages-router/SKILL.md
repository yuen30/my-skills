---
name: Next.js Pages Router
description: Expert guidance for building web applications with Next.js Pages Router, including SSR, SSG, ISR, API Routes, and data fetching with getStaticProps/getServerSideProps.
---

# Next.js Pages Router

Expert guidance for building web applications with Next.js Pages Router, including SSR, SSG, ISR, API Routes, and data fetching with getStaticProps/getServerSideProps.

@doc-version: 16.2.6

## Capabilities

- Set up Next.js projects using the Pages Router
- Build pages with SSR, SSG, and CSR rendering strategies
- Fetch data with `getStaticProps`, `getStaticPaths`, and `getServerSideProps`
- Create API Routes for backend logic
- Implement ISR (Incremental Static Regeneration)
- Customize `_app.tsx`, `_document.tsx`, and error pages
- Handle routing, dynamic routes, and navigation
- Optimize images, fonts, and third-party scripts
- Deploy with self-hosting, Docker, or static export

## Guidelines

### When to Use Pages Router

- Existing projects already using Pages Router
- Migrating from older Next.js versions incrementally
- Projects that rely heavily on `getServerSideProps` / `getStaticProps` patterns
- For new projects, prefer the **App Router** unless you have specific reasons

### Project Structure

```
├── pages/
│   ├── _app.tsx            # Custom App (wraps all pages)
│   ├── _document.tsx       # Custom Document (HTML structure)
│   ├── index.tsx           # Home page (/)
│   ├── about.tsx           # /about
│   ├── blog/
│   │   ├── index.tsx       # /blog
│   │   └── [slug].tsx      # /blog/:slug
│   ├── [...slug].tsx       # Catch-all route
│   ├── [[...slug]].tsx     # Optional catch-all
│   └── api/
│       ├── hello.ts        # /api/hello
│       └── posts/
│           └── [id].ts     # /api/posts/:id
├── public/
├── styles/
├── lib/
├── components/
├── next.config.js
└── tsconfig.json
```

### Pages and Routing

```tsx
// pages/index.tsx — Home page
export default function Home() {
  return <h1>Welcome</h1>
}
```

```tsx
// pages/blog/[slug].tsx — Dynamic route
import { useRouter } from 'next/router'

export default function BlogPost() {
  const router = useRouter()
  const { slug } = router.query
  return <article>Post: {slug}</article>
}
```

### Custom App (`_app.tsx`)

```tsx
// pages/_app.tsx
import type { AppProps } from 'next/app'
import '@/styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  )
}
```

### Custom Document (`_document.tsx`)

```tsx
// pages/_document.tsx
import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head />
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
```

### Data Fetching

#### Static Site Generation (SSG) — `getStaticProps`

```tsx
// pages/blog/index.tsx
import type { InferGetStaticPropsType, GetStaticProps } from 'next'

type Post = { id: string; title: string }

export const getStaticProps: GetStaticProps<{ posts: Post[] }> = async () => {
  const res = await fetch('https://api.example.com/posts')
  const posts: Post[] = await res.json()

  return {
    props: { posts },
    revalidate: 60, // ISR: regenerate every 60 seconds
  }
}

export default function Blog({ posts }: InferGetStaticPropsType<typeof getStaticProps>) {
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

#### Dynamic SSG — `getStaticPaths`

```tsx
// pages/blog/[slug].tsx
import type { GetStaticPaths, GetStaticProps } from 'next'

export const getStaticPaths: GetStaticPaths = async () => {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()

  const paths = posts.map((post: any) => ({
    params: { slug: post.slug },
  }))

  return {
    paths,
    fallback: 'blocking', // or false, or true
  }
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const res = await fetch(`https://api.example.com/posts/${params?.slug}`)
  const post = await res.json()

  if (!post) return { notFound: true }

  return {
    props: { post },
    revalidate: 60,
  }
}

export default function Post({ post }: { post: any }) {
  return <article>{post.title}</article>
}
```

#### Server-Side Rendering (SSR) — `getServerSideProps`

```tsx
// pages/dashboard.tsx
import type { GetServerSideProps } from 'next'

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { req, res, params, query } = context

  const token = req.cookies.session
  if (!token) {
    return { redirect: { destination: '/login', permanent: false } }
  }

  const data = await fetch('https://api.example.com/dashboard', {
    headers: { Authorization: `Bearer ${token}` },
  }).then((r) => r.json())

  return { props: { data } }
}

export default function Dashboard({ data }: { data: any }) {
  return <div>{data.summary}</div>
}
```

#### Client-Side Fetching (SWR)

```tsx
'use client'
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export default function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher)

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error</div>
  return <div>Hello, {data.name}</div>
}
```

### API Routes

```tsx
// pages/api/posts.ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const posts = await db.post.findMany()
    return res.status(200).json(posts)
  }

  if (req.method === 'POST') {
    const post = await db.post.create({ data: req.body })
    return res.status(201).json(post)
  }

  res.setHeader('Allow', ['GET', 'POST'])
  res.status(405).end(`Method ${req.method} Not Allowed`)
}
```

```tsx
// pages/api/posts/[id].ts
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query

  if (req.method === 'GET') {
    const post = await db.post.findUnique({ where: { id: String(id) } })
    if (!post) return res.status(404).json({ error: 'Not found' })
    return res.status(200).json(post)
  }

  if (req.method === 'DELETE') {
    await db.post.delete({ where: { id: String(id) } })
    return res.status(204).end()
  }

  res.status(405).end()
}
```

### Incremental Static Regeneration (ISR)

```tsx
export const getStaticProps: GetStaticProps = async () => {
  const data = await fetchData()

  return {
    props: { data },
    revalidate: 60, // Revalidate at most every 60 seconds
  }
}
```

- Pages are generated at build time
- After `revalidate` seconds, next request triggers background regeneration
- Stale content served until new page is ready
- Use `res.revalidate('/path')` in API routes for on-demand ISR

```tsx
// pages/api/revalidate.ts
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const secret = req.query.secret
  if (secret !== process.env.REVALIDATION_SECRET) {
    return res.status(401).json({ message: 'Invalid token' })
  }

  await res.revalidate('/blog')
  return res.json({ revalidated: true })
}
```

### Navigation

```tsx
import Link from 'next/link'

<Link href="/about">About</Link>
<Link href={`/blog/${post.slug}`}>Read more</Link>
<Link href="/dashboard" prefetch={false}>Dashboard</Link>
```

```tsx
import { useRouter } from 'next/router'

function MyComponent() {
  const router = useRouter()

  // Programmatic navigation
  router.push('/dashboard')
  router.replace('/login')
  router.back()

  // Access route info
  const { pathname, query, asPath, locale } = router
}
```

### Middleware

```tsx
// middleware.ts (project root)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
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
  alt="Hero"
  width={1200}
  height={600}
  priority
/>

// Remote images require config
// next.config.js:
// images: { remotePatterns: [{ hostname: 'cdn.example.com' }] }
```

### Font Optimization

```tsx
// pages/_app.tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function App({ Component, pageProps }: AppProps) {
  return (
    <main className={inter.className}>
      <Component {...pageProps} />
    </main>
  )
}
```

### Error Pages

```tsx
// pages/404.tsx
export default function Custom404() {
  return <h1>404 - Page Not Found</h1>
}
```

```tsx
// pages/500.tsx
export default function Custom500() {
  return <h1>500 - Server Error</h1>
}
```

```tsx
// pages/_error.tsx
import type { NextPageContext } from 'next'

function Error({ statusCode }: { statusCode?: number }) {
  return <p>{statusCode ? `Error ${statusCode}` : 'Client error'}</p>
}

Error.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404
  return { statusCode }
}

export default Error
```

### Environment Variables

- `.env.local` — local secrets (gitignored)
- `.env` — defaults
- `NEXT_PUBLIC_*` — exposed to the browser

```tsx
// Server only (getStaticProps, getServerSideProps, API routes)
const secret = process.env.API_SECRET

// Client accessible
const url = process.env.NEXT_PUBLIC_API_URL
```

### Rendering Strategies Summary

| Strategy | Function | When |
|----------|----------|------|
| SSG | `getStaticProps` | Build time (+ ISR) |
| SSG + Dynamic | `getStaticPaths` + `getStaticProps` | Build time per path |
| SSR | `getServerSideProps` | Every request |
| CSR | Client hooks (SWR, useEffect) | After hydration |
| ISR | `getStaticProps` + `revalidate` | Background regeneration |

### `fallback` Options in `getStaticPaths`

| Value | Behavior |
|-------|----------|
| `false` | Only pre-rendered paths; others → 404 |
| `true` | Serve fallback page, generate in background |
| `'blocking'` | SSR on first request, then cache like SSG |

### Deployment

```bash
# Build
next build

# Start production server
next start

# Static export (no server needed)
# next.config.js: output: 'export'
next build
```

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
