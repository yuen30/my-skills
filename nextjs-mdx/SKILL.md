---
name: Next.js MDX
description: Expert guidance on using Markdown and MDX in Next.js — @next/mdx setup, custom components, remark/rehype plugins, frontmatter, and dynamic imports.
---

# Next.js MDX

Expert guidance on using Markdown and MDX in Next.js — @next/mdx setup, custom components, remark/rehype plugins, frontmatter, and dynamic imports.

@doc-version: 16.2.6

## Core Concepts

MDX = Markdown + JSX — เขียน React components ใน markdown files ได้:
- `.mdx` files ทำหน้าที่เป็น pages/routes ได้โดยตรง
- Import MDX เป็น React components
- Custom components map กับ HTML elements
- รองรับ remark/rehype plugins

## Guidelines

### 1. Installation

```bash
npm install @next/mdx @mdx-js/loader @mdx-js/react @types/mdx
```

### 2. Configure `next.config.mjs`

```js
// next.config.mjs
import createMDX from '@next/mdx'

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
}

const withMDX = createMDX({
  // Add markdown plugins here
})

export default withMDX(nextConfig)
```

#### Handle `.md` files too

```js
const withMDX = createMDX({
  extension: /\.(md|mdx)$/,
})
```

### 3. Create `mdx-components.tsx` (Required)

```tsx
// mdx-components.tsx (project root)
import type { MDXComponents } from 'mdx/types'
import Image, { ImageProps } from 'next/image'

const components: MDXComponents = {
  h1: ({ children }) => (
    <h1 className="text-4xl font-bold mt-8 mb-4">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-3xl font-semibold mt-6 mb-3">{children}</h2>
  ),
  img: (props) => (
    <Image
      sizes="100vw"
      style={{ width: '100%', height: 'auto' }}
      {...(props as ImageProps)}
    />
  ),
  a: ({ href, children }) => (
    <a href={href} className="text-blue-600 hover:underline">
      {children}
    </a>
  ),
}

export function useMDXComponents(): MDXComponents {
  return components
}
```

> **บังคับ** — ไม่มีไฟล์นี้ `@next/mdx` จะไม่ทำงานกับ App Router

### 4. Using MDX as Pages (File-based Routing)

```
app/
├── blog/
│   └── hello/
│       └── page.mdx    ← MDX page at /blog/hello
├── mdx-components.tsx
└── layout.tsx
```

```mdx
<!-- app/blog/hello/page.mdx -->
import { Alert } from '@/components/alert'

# Hello World

This is my **MDX** page with a React component:

<Alert type="info">This is an alert!</Alert>
```

### 5. Import MDX into Pages

```mdx
<!-- content/welcome.mdx -->
import { Badge } from '@/components/badge'

# Welcome

Here's a <Badge>New</Badge> feature!
```

```tsx
// app/page.tsx
import Welcome from '@/content/welcome.mdx'

export default function Page() {
  return <Welcome />
}
```

### 6. Dynamic MDX Imports

```tsx
// app/blog/[slug]/page.tsx
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const { default: Post } = await import(`@/content/${slug}.mdx`)
  return <Post />
}

export function generateStaticParams() {
  return [{ slug: 'welcome' }, { slug: 'about' }]
}

export const dynamicParams = false
```

### 7. Custom Components (Local Override)

```tsx
// app/blog/page.tsx
import Welcome from '@/content/welcome.mdx'

function CustomH1({ children }: { children: React.ReactNode }) {
  return <h1 className="text-5xl text-blue-600">{children}</h1>
}

export default function Page() {
  return <Welcome components={{ h1: CustomH1 }} />
}
```

### 8. Shared Layout with Tailwind Typography

```bash
npm install @tailwindcss/typography
```

```tsx
// app/blog/layout.tsx
export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="prose prose-lg dark:prose-invert max-w-none">
      {children}
    </div>
  )
}
```

### 9. Frontmatter (Metadata)

`@next/mdx` ไม่รองรับ frontmatter โดยตรง — ใช้ exports แทน:

```mdx
<!-- content/blog-post.mdx -->
export const metadata = {
  title: 'My Blog Post',
  author: 'John Doe',
  date: '2024-01-15',
}

# {metadata.title}

Written by {metadata.author}
```

```tsx
// app/blog/page.tsx
import BlogPost, { metadata } from '@/content/blog-post.mdx'

export default function Page() {
  console.log(metadata) // { title: 'My Blog Post', author: 'John Doe', ... }
  return <BlogPost />
}
```

#### ถ้าต้องการ YAML frontmatter จริงๆ

ใช้ plugins:
- `remark-frontmatter` — parse YAML
- `remark-mdx-frontmatter` — expose เป็น exports
- `gray-matter` — parse ก่อน compile

### 10. Remark and Rehype Plugins

```js
// next.config.mjs
import remarkGfm from 'remark-gfm'
import rehypeSlug from 'rehype-slug'
import createMDX from '@next/mdx'

const nextConfig = {
  pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
}

const withMDX = createMDX({
  options: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [rehypeSlug],
  },
})

export default withMDX(nextConfig)
```

#### With Turbopack (string-based)

```js
const withMDX = createMDX({
  options: {
    remarkPlugins: [
      'remark-gfm',
      ['remark-toc', { heading: 'Table of Contents' }],
    ],
    rehypePlugins: [
      'rehype-slug',
      ['rehype-katex', { strict: true }],
    ],
  },
})
```

#### Popular Plugins

| Plugin | Purpose |
|--------|---------|
| `remark-gfm` | GitHub Flavored Markdown (tables, strikethrough) |
| `remark-toc` | Auto table of contents |
| `rehype-slug` | Add IDs to headings |
| `rehype-autolink-headings` | Link headings |
| `rehype-pretty-code` | Syntax highlighting |
| `rehype-katex` + `remark-math` | Math equations |

### 11. Rust-based MDX Compiler (Experimental)

```js
// next.config.js
module.exports = withMDX({
  experimental: {
    mdxRs: true,
    // หรือ with options:
    // mdxRs: {
    //   mdxType: 'gfm', // 'gfm' | 'commonmark'
    // },
  },
})
```

### 12. Blog Index from MDX Files

```tsx
// app/blog/page.tsx
import fs from 'fs'
import path from 'path'

async function getBlogPosts() {
  const contentDir = path.join(process.cwd(), 'content/blog')
  const files = fs.readdirSync(contentDir).filter((f) => f.endsWith('.mdx'))

  const posts = await Promise.all(
    files.map(async (file) => {
      const { metadata } = await import(`@/content/blog/${file}`)
      return {
        slug: file.replace('.mdx', ''),
        ...metadata,
      }
    })
  )

  return posts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export default async function BlogIndex() {
  const posts = await getBlogPosts()

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.slug}>
          <a href={`/blog/${post.slug}`}>{post.title}</a>
        </li>
      ))}
    </ul>
  )
}
```

## Quick Reference

| Feature | How |
|---------|-----|
| MDX as page | `app/blog/page.mdx` |
| Import MDX | `import Post from './post.mdx'` |
| Dynamic import | `await import(\`@/content/${slug}.mdx\`)` |
| Custom components | `mdx-components.tsx` (global) or `components` prop (local) |
| Plugins | `remarkPlugins` / `rehypePlugins` in config |
| Frontmatter | `export const metadata = {...}` |
| Tailwind styling | `@tailwindcss/typography` + `prose` class |
| Handle .md | `extension: /\.(md|mdx)$/` |

## สรุป

1. **Install** `@next/mdx` + `@mdx-js/loader` + `@mdx-js/react`
2. **Config** `next.config.mjs` — `pageExtensions` + `createMDX()`
3. **`mdx-components.tsx`** — required, define global component overrides
4. **3 วิธีใช้:** file-based routing, import, dynamic import
5. **Plugins:** remark (markdown) + rehype (HTML) — GFM, syntax highlight, etc.
6. **Frontmatter:** ใช้ `export const metadata` (ไม่ใช่ YAML by default)
7. **Tailwind Typography** — `prose` class สำหรับ styling
8. **Server Components** — MDX render บน server, ไม่เพิ่ม client JS
