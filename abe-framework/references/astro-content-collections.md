Read when defining Astro collection schemas or dynamic routes from collections.

# Content Collections

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
