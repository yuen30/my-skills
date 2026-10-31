Read when fetching data in Astro at build time, in SSR, or writing API endpoints.

# Data Fetching

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
