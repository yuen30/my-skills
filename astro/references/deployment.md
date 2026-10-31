# Build and Deployment


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
