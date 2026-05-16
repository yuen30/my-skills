---
name: Next.js JSON-LD
description: Expert guidance on implementing JSON-LD structured data in Next.js for SEO and AI — schema.org types, XSS prevention, TypeScript typing, and common patterns.
---

# Next.js JSON-LD

Expert guidance on implementing JSON-LD structured data in Next.js for SEO and AI — schema.org types, XSS prevention, TypeScript typing, and common patterns.

@doc-version: 16.2.6

## Core Concepts

JSON-LD (JavaScript Object Notation for Linked Data) คือ structured data format ที่ช่วย:
- Search engines เข้าใจ content ของหน้า
- AI systems ตีความข้อมูล
- Rich results ใน Google Search (stars, prices, images)

ใช้ native `<script type="application/ld+json">` tag (ไม่ใช่ `next/script`)

## Guidelines

### 1. Basic Implementation

```tsx
// app/products/[id]/page.tsx
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await getProduct(id)

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    image: product.image,
    description: product.description,
  }

  return (
    <section>
      {/* JSON-LD structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
        }}
      />
      {/* Page content */}
      <h1>{product.name}</h1>
    </section>
  )
}
```

> **XSS Prevention:** `.replace(/</g, '\\u003c')` ป้องกัน malicious strings ที่มี `<script>` tags

### 2. TypeScript Typing with `schema-dts`

```bash
npm install schema-dts
```

```tsx
import { Product, WithContext } from 'schema-dts'

const jsonLd: WithContext<Product> = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: 'Next.js Sticker',
  image: 'https://nextjs.org/imgs/sticker.png',
  description: 'Dynamic at the speed of static.',
}
```

### 3. Common Schema Types

#### Product

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Product',
  name: product.name,
  image: product.images,
  description: product.description,
  offers: {
    '@type': 'Offer',
    price: product.price,
    priceCurrency: 'THB',
    availability: 'https://schema.org/InStock',
    url: `https://example.com/products/${product.id}`,
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: product.rating,
    reviewCount: product.reviewCount,
  },
}
```

#### Article / Blog Post

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: post.title,
  description: post.excerpt,
  image: post.coverImage,
  datePublished: post.publishedAt,
  dateModified: post.updatedAt,
  author: {
    '@type': 'Person',
    name: post.author.name,
    url: post.author.url,
  },
  publisher: {
    '@type': 'Organization',
    name: 'My Blog',
    logo: {
      '@type': 'ImageObject',
      url: 'https://example.com/logo.png',
    },
  },
}
```

#### Organization

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'My Company',
  url: 'https://example.com',
  logo: 'https://example.com/logo.png',
  sameAs: [
    'https://twitter.com/mycompany',
    'https://github.com/mycompany',
  ],
  contactPoint: {
    '@type': 'ContactPoint',
    telephone: '+66-2-xxx-xxxx',
    contactType: 'customer service',
  },
}
```

#### BreadcrumbList

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    {
      '@type': 'ListItem',
      position: 1,
      name: 'Home',
      item: 'https://example.com',
    },
    {
      '@type': 'ListItem',
      position: 2,
      name: 'Products',
      item: 'https://example.com/products',
    },
    {
      '@type': 'ListItem',
      position: 3,
      name: product.name,
      item: `https://example.com/products/${product.id}`,
    },
  ],
}
```

#### FAQ

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map((faq) => ({
    '@type': 'Question',
    name: faq.question,
    acceptedAnswer: {
      '@type': 'Answer',
      text: faq.answer,
    },
  })),
}
```

#### WebSite (Sitelinks Search)

```tsx
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'My Site',
  url: 'https://example.com',
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: 'https://example.com/search?q={search_term_string}',
    },
    'query-input': 'required name=search_term_string',
  },
}
```

### 4. Reusable JSON-LD Component

```tsx
// components/json-ld.tsx
type JsonLdProps = {
  data: Record<string, unknown>
}

export function JsonLd({ data }: JsonLdProps) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, '\\u003c'),
      }}
    />
  )
}
```

```tsx
// app/products/[id]/page.tsx
import { JsonLd } from '@/components/json-ld'

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const product = await getProduct(id)

  return (
    <>
      <JsonLd
        data={{
          '@context': 'https://schema.org',
          '@type': 'Product',
          name: product.name,
          description: product.description,
        }}
      />
      <h1>{product.name}</h1>
    </>
  )
}
```

### 5. Multiple JSON-LD Blocks

หน้าเดียวมีได้หลาย JSON-LD blocks:

```tsx
export default async function Page() {
  return (
    <>
      {/* Organization */}
      <JsonLd data={{ '@context': 'https://schema.org', '@type': 'Organization', ... }} />

      {/* Breadcrumbs */}
      <JsonLd data={{ '@context': 'https://schema.org', '@type': 'BreadcrumbList', ... }} />

      {/* Page content */}
      <main>...</main>
    </>
  )
}
```

### 6. Validation

ทดสอบ structured data:
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema Markup Validator](https://validator.schema.org/)

## Important Notes

- ใช้ native `<script>` tag — ไม่ใช่ `next/script` (JSON-LD ไม่ใช่ executable code)
- **Sanitize output** — `.replace(/</g, '\\u003c')` ป้องกัน XSS
- วางใน `layout.tsx` หรือ `page.tsx` (Server Components)
- ใช้ `schema-dts` สำหรับ TypeScript type safety

## Quick Reference

| Schema Type | Use Case |
|-------------|----------|
| `Product` | สินค้า (price, rating, availability) |
| `Article` | Blog posts, news articles |
| `Organization` | Company info, logo, social links |
| `BreadcrumbList` | Navigation breadcrumbs |
| `FAQPage` | FAQ sections |
| `WebSite` | Sitelinks search box |
| `Event` | Events (date, location, tickets) |
| `Recipe` | Recipes (ingredients, steps, time) |
| `LocalBusiness` | Local business (address, hours) |
| `Person` | People (name, job, social) |

## สรุป

1. **ใช้ `<script type="application/ld+json">`** — native tag, ไม่ใช่ `next/script`
2. **Sanitize ด้วย `.replace(/</g, '\\u003c')`** — ป้องกัน XSS
3. **TypeScript:** ใช้ `schema-dts` สำหรับ type safety
4. **สร้าง reusable `<JsonLd>` component** — ใช้ซ้ำทั้งโปรเจกต์
5. **หลาย blocks ต่อหน้าได้** — Organization + Breadcrumbs + Product
6. **Validate** ด้วย Google Rich Results Test
