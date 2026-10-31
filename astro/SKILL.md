---
name: astro
description: Astro framework guide covering islands, content collections with Zod, data fetching, astro:assets images, SSR and deployment. Use when working on .astro files, astro.config.mjs, src/content, client:* directives or getCollection.
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
## 📚 References

- Project structure → use the `project-structure` skill (references/astro.md).
- [references/components.md](references/components.md) — read when writing `.astro` components or framework islands.
- [references/content-collections.md](references/content-collections.md) — read when defining collection schemas or dynamic routes from collections.
- [references/data-fetching.md](references/data-fetching.md) — read when fetching at build time, in SSR, or writing API endpoints.
- [references/deployment.md](references/deployment.md) — read when configuring env vars, `astro.config.mjs`, or deploying.

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
