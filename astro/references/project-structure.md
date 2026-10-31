# Project Structure


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
