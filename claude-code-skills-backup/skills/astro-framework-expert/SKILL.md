---
name: Astro Framework Expert
description: Expert guidance on Astro framework — components, content collections, islands architecture, data fetching, image optimization, deployment, and strict best practices.
---

# Astro Framework Expert

Expert guidance on Astro framework — components, content collections, islands architecture, data fetching, image optimization, deployment, and strict best practices.

## 🎯 Core Philosophy

Astro เป็น **content-first** web framework ที่ส่ง **zero JavaScript by default** — ใช้ Islands Architecture สำหรับ interactive components เท่านั้น

**Key Principles:**
- Static content → `.astro` components (zero JS)
- Interactive UI → Framework islands (React/Vue/Svelte) with explicit hydration
- Content → Collections with Zod schemas (type-safe at build time)
- Images → Always `<Image>` from `astro:assets`
- TypeScript strict mode + TailwindCSS utility-first

---

## ⚠️ Iron Laws (NON-NEGOTIABLE)

### 1. Astro Components for Static Content

**ALWAYS use `.astro` components for static content — reserve framework components for interactive islands only**

```astro
<!-- ✅ CORRECT — Static content in .astro (zero JS shipped) -->
---
const { title, description } = Astro.props
---
<article>
  <h1>{title}</h1>
  <p>{description}</p>
</article>
```

```tsx
// ❌ WRONG — React for non-interactive content (ships unnecessary JS)
export default function Article({ title, description }) {
  return (
    <article>
      <h1>{title}</h1>
      <p>{description}</p>
    </article>
  )
}
```

### 2. Content Collections with Zod Schemas

**ALWAYS use `defineCollection()` + schema validation — catches errors at build time**

```ts
// ✅ CORRECT — src/content/config.ts
import { defineCollection, z } from 'astro:content'

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    author: z.string(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    image: z.string().optional(),
  }),
})

export const collections = { blog }
```

```astro
<!-- ✅ CORRECT — Type-safe content access -->
---
import { getCollection } from 'astro:content'

const posts = await getCollection('blog', ({ data }) => !data.draft)
---
```

```astro
<!-- ❌ WRONG — Astro.glob() returns untyped data -->
---
const posts = await Astro.glob('../content/blog/*.md')
---
```

### 3. Explicit Island Hydration Directives

**ALWAYS specify hydration directives intentionally — wrong strategy defeats performance**

```astro
<!-- ✅ CORRECT — Intentional hydration -->
<SearchBar client:idle />          <!-- Below-fold, not urgent -->
<Newsletter client:visible />      <!-- Only when scrolled into view -->
<CartButton client:load />         <!-- Critical, needs immediate interactivity -->
<HeavyChart client:only="react" /> <!-- Client-only, no SSR -->
```

```astro
<!-- ❌ WRONG — client:load for everything -->
<Footer client:load />       <!-- Static! Use .astro instead -->
<Sidebar client:load />      <!-- Below-fold! Use client:idle -->
<LazyWidget client:load />   <!-- Off-screen! Use client:visible -->
```

| Directive | When to Use |
|-----------|-------------|
| `client:load` | Critical interactive UI (nav, auth buttons) |
| `client:idle` | Below-fold interactive (search, filters) |
| `client:visible` | Only when scrolled into view (charts, comments) |
| `client:media` | Only at specific viewport (mobile menu) |
| `client:only` | Client-only rendering (no SSR) |

### 4. Always Use `<Image>` from `astro:assets`

**NEVER use raw `<img>` tags — misses optimization, format conversion, LCP**

```astro
<!-- ✅ CORRECT -->
---
import { Image } from 'astro:assets'
import heroImage from '../assets/hero.jpg'
---
<Image src={heroImage} alt="Hero" width={1200} height={600} />

<!-- Remote images -->
<Image src="https://cdn.example.com/photo.jpg" alt="Photo" width={800} height={400} inferSize />
```

```astro
<!-- ❌ WRONG — raw img tag -->
<img src="/hero.jpg" alt="Hero" />
```

### 5. Never Use `Astro.glob()` for Typed Content

**Use Content Collections API for all structured content**

```astro
<!-- ✅ CORRECT — Full TypeScript support -->
---
import { getCollection, getEntry } from 'astro:content'

// Get all posts
const posts = await getCollection('blog')

// Get single entry
const post = await getEntry('blog', 'my-post')
---
```

```astro
<!-- ❌ WRONG — Untyped, no schema validation -->
---
const posts = await Astro.glob('../content/blog/*.md')
---
```

---

## 📁 Project Structure

```
src/
├── components/           # .astro components (static, zero JS)
│   ├── Header.astro
│   ├── Footer.astro
│   ├── Card.astro
│   └── islands/          # Framework components (interactive)
│       ├── SearchBar.tsx
│       ├── ThemeToggle.tsx
│       └── Newsletter.svelte
│
├── content/              # Content Collections
│   ├── config.ts         # Collection schemas (Zod)
│   ├── blog/
│   │   ├── first-post.md
│   │   └── second-post.mdx
│   └── docs/
│       └── getting-started.md
│
├── layouts/              # Page layouts
│   ├── BaseLayout.astro
│   ├── BlogLayout.astro
│   └── DocsLayout.astro
│
├── pages/                # File-based routing
│   ├── index.astro
│   ├── about.astro
│   ├── blog/
│   │   ├── index.astro
│   │   └── [slug].astro
│   └── api/
│       └── search.ts     # API endpoints
│
├── styles/               # Global styles
│   └── global.css
│
├── assets/               # Optimized assets (processed by Astro)
│   └── images/
│
└── utils/                # Utility functions
    └── format.ts
```

---

## 💻 Component Development

### Astro Component (Static)

```astro
---
// src/components/Card.astro
interface Props {
  title: string
  description: string
  href: string
  image?: ImageMetadata
}

const { title, description, href, image } = Astro.props
---

<a href={href} class="group block rounded-lg border p-4 hover:border-primary transition">
  {image && (
    <Image src={image} alt={title} class="rounded-md mb-4" width={400} height={200} />
  )}
  <h3 class="text-lg font-semibold group-hover:text-primary">{title}</h3>
  <p class="text-muted-foreground mt-1">{description}</p>
</a>
```

### Island Component (Interactive)

```tsx
// src/components/islands/SearchBar.tsx
import { useState } from 'react'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  async function handleSearch(value: string) {
    setQuery(value)
    if (value.length < 2) return setResults([])
    const res = await fetch(`/api/search?q=${encodeURIComponent(value)}`)
    setResults(await res.json())
  }

  return (
    <div>
      <input
        type="search"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search..."
        className="w-full rounded-md border px-4 py-2"
      />
      {results.length > 0 && (
        <ul className="mt-2 rounded-md border divide-y">
          {results.map((r) => (
            <li key={r.id} className="p-2">
              <a href={r.url}>{r.title}</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

Usage in `.astro`:
```astro
---
import SearchBar from '../components/islands/SearchBar'
---
<SearchBar client:idle />
```

---

## 📝 Content Collections

### Schema Definition

```ts
// src/content/config.ts
import { defineCollection, z } from 'astro:content'

const blog = defineCollection({
  type: 'content',
  schema: ({ image }) => z.object({
    title: z.string().max(100),
    description: z.string().max(200),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    cover: image().optional(),
  }),
})

const docs = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    order: z.number(),
    section: z.string(),
  }),
})

export const collections = { blog, docs }
```

### Dynamic Routes from Collections

```astro
---
// src/pages/blog/[slug].astro
import { getCollection } from 'astro:content'
import BlogLayout from '../../layouts/BlogLayout.astro'

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft)
  return posts.map((post) => ({
    params: { slug: post.slug },
    props: { post },
  }))
}

const { post } = Astro.props
const { Content } = await post.render()
---

<BlogLayout title={post.data.title} description={post.data.description}>
  <article>
    <h1>{post.data.title}</h1>
    <time datetime={post.data.pubDate.toISOString()}>
      {post.data.pubDate.toLocaleDateString()}
    </time>
    <Content />
  </article>
</BlogLayout>
```

---

## 🔧 Data Fetching

### Build-time (getStaticPaths)

```astro
---
export async function getStaticPaths() {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()

  return posts.map((post) => ({
    params: { id: post.id },
    props: { post },
  }))
}

const { post } = Astro.props
---
<h1>{post.title}</h1>
```

### Server-side (SSR mode)

```astro
---
// Only in SSR mode (output: 'server' or 'hybrid')
const res = await fetch('https://api.example.com/data', {
  headers: { Authorization: `Bearer ${import.meta.env.API_KEY}` },
})

if (!res.ok) {
  return Astro.redirect('/404')
}

const data = await res.json()
---
<div>{data.title}</div>
```

### API Endpoints

```ts
// src/pages/api/search.ts
import type { APIRoute } from 'astro'
import { getCollection } from 'astro:content'

export const GET: APIRoute = async ({ url }) => {
  const query = url.searchParams.get('q')?.toLowerCase() ?? ''

  if (query.length < 2) {
    return new Response(JSON.stringify([]), { status: 200 })
  }

  const posts = await getCollection('blog')
  const results = posts
    .filter((p) => p.data.title.toLowerCase().includes(query))
    .map((p) => ({ id: p.slug, title: p.data.title, url: `/blog/${p.slug}` }))

  return new Response(JSON.stringify(results), {
    headers: { 'Content-Type': 'application/json' },
  })
}
```

---

## 🚀 Build and Deployment

### Environment Variables

```bash
# .env
PUBLIC_SITE_URL=https://example.com  # Available on client
API_KEY=secret                        # Server-only
```

```astro
---
// Server-only
const apiKey = import.meta.env.API_KEY

// Available everywhere (prefixed with PUBLIC_)
const siteUrl = import.meta.env.PUBLIC_SITE_URL
---
```

### astro.config.mjs

```js
import { defineConfig } from 'astro/config'
import tailwind from '@astrojs/tailwind'
import react from '@astrojs/react'
import mdx from '@astrojs/mdx'
import sitemap from '@astrojs/sitemap'

export default defineConfig({
  site: 'https://example.com',
  integrations: [
    tailwind(),
    react(),
    mdx(),
    sitemap(),
  ],
  output: 'static', // or 'server', 'hybrid'
  image: {
    domains: ['cdn.example.com'],
  },
})
```

### Deploy Commands

```bash
# Build
astro build

# Preview production build locally
astro preview

# Deploy to platforms
# Netlify, Vercel, Cloudflare Pages — auto-detected
```

---

## ⚠️ Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|-----------------|
| React/Vue for static UI | Ships unnecessary JS; kills zero-JS default | Use `.astro` components |
| Raw `<img>` tags | Misses LCP optimization, format conversion | Use `<Image>` from `astro:assets` |
| Content without Zod schema | Errors surface at runtime, not build time | Define schema in `content/config.ts` |
| `client:load` for everything | Loads all JS on page load; defeats partial hydration | Use `client:idle` or `client:visible` |
| `Astro.glob()` for content | Returns untyped; no schema validation | Use `getCollection()` from `astro:content` |
| Inline styles | Inconsistent, hard to maintain | TailwindCSS utility classes |
| No TypeScript | Misses build-time error catching | Strict TypeScript always |

---

## Quick Reference

| Feature | API |
|---------|-----|
| Static component | `.astro` file |
| Interactive island | Framework component + `client:*` directive |
| Content collection | `getCollection()`, `getEntry()` |
| Image optimization | `<Image>` from `astro:assets` |
| API endpoint | `src/pages/api/*.ts` with `APIRoute` |
| Environment vars | `import.meta.env.PUBLIC_*` (client) / `import.meta.env.*` (server) |
| Dynamic routes | `getStaticPaths()` in `[param].astro` |
| Layouts | `<slot />` in layout components |

## สรุป

1. **Zero JS by default** — `.astro` สำหรับ static, framework islands สำหรับ interactive
2. **Content Collections + Zod** — type-safe content at build time
3. **Explicit hydration** — `client:load/idle/visible` ตาม priority
4. **`<Image>` always** — ห้ามใช้ raw `<img>`
5. **`getCollection()` always** — ห้ามใช้ `Astro.glob()` สำหรับ typed content
6. **TypeScript strict** — ทุกไฟล์
7. **TailwindCSS** — utility-first styling
8. **Environment vars** — `PUBLIC_` prefix สำหรับ client-accessible
