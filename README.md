# Skills Collection

คอลเลกชัน skills ส่วนตัวของ Taweechai Yuenyang

## โครงสร้าง

```
skills/
├── <skill-name>/
│   ├── SKILL.md          # คำอธิบายและคำสั่งหลักของ skill
│   ├── references/       # เอกสารอ้างอิงเพิ่มเติม
│   ├── examples/         # ตัวอย่างการใช้งาน
│   ├── scripts/          # สคริปต์ที่เกี่ยวข้อง
│   └── templates/        # เทมเพลตสำหรับใช้งาน
└── README.md
```

## การสร้าง Skill ใหม่

1. สร้างโฟลเดอร์ใหม่ด้วยชื่อ skill (ใช้ kebab-case)
2. สร้างไฟล์ `SKILL.md` ที่อธิบายว่า skill ทำอะไร และมีคำสั่งอะไรบ้าง
3. เพิ่ม references, examples, scripts ตามต้องการ

## Installation

```bash
npx skills add yuen30/my-skills
```

## รายการ Skills

| Skill | Description |
|-------|-------------|
| [docker](./docker/) | Docker & Docker Compose best practices, templates, and troubleshooting |
| [react-three-fiber](./react-three-fiber/) | React Three Fiber (R3F), Three.js, and Drei helpers |
| [tailwind-v4-shadcn](./tailwind-v4-shadcn/) | Tailwind CSS v4 + shadcn/ui components |
| [nextjs-core-system](./nextjs-core-system/) | Next.js 16 App Router — Server Components, caching, data fetching, deployment |
| [nextjs-pages-router](./nextjs-pages-router/) | Next.js Pages Router — SSR, SSG, ISR, API Routes, getStaticProps/getServerSideProps |
| [nextjs-layouts-and-pages](./nextjs-layouts-and-pages/) | Next.js Layouts and Pages — file-system routing, nested layouts, dynamic segments, navigation |
| [nextjs-linking-and-navigating](./nextjs-linking-and-navigating/) | Next.js Linking and Navigating — prefetching, streaming, client-side transitions, optimization |
| [nextjs-server-and-client-components](./nextjs-server-and-client-components/) | Next.js Server and Client Components — rendering boundaries, interleaving patterns, hydration |
| [nextjs-fetching-data](./nextjs-fetching-data/) | Next.js Fetching Data — Server Components, Streaming, Suspense, parallel/sequential patterns |
| [nextjs-mutating-data](./nextjs-mutating-data/) | Next.js Mutating Data — Server Actions, forms, revalidation, security best practices |
| [nextjs-caching](./nextjs-caching/) | Next.js Caching — Cache Components, "use cache" directive, Streaming, PPR |
| [nextjs-revalidating](./nextjs-revalidating/) | Next.js Revalidating — cacheLife, cacheTag, revalidateTag, updateTag, revalidatePath |
| [nextjs-error-handling](./nextjs-error-handling/) | Next.js Error Handling — error boundaries, notFound, useActionState, catchError |
| [nextjs-css](./nextjs-css/) | Next.js CSS — Tailwind CSS, CSS Modules, Global CSS, ordering best practices |
| [nextjs-images](./nextjs-images/) | Next.js Image Optimization — local/remote images, lazy loading, blur placeholders, responsive |
| [nextjs-fonts](./nextjs-fonts/) | Next.js Font Optimization — Google Fonts self-hosting, local fonts, variable fonts, zero CLS |
| [nextjs-metadata](./nextjs-metadata/) | Next.js Metadata and OG Images — SEO, static/dynamic metadata, OG images, sitemap, robots.txt |
| [nextjs-route-handlers](./nextjs-route-handlers/) | Next.js Route Handlers — API endpoints, HTTP methods, caching, request/response helpers |
| [nextjs-proxy](./nextjs-proxy/) | Next.js Proxy (Middleware) — redirects, rewrites, headers, auth checks, route matching |
| [nextjs-deploying](./nextjs-deploying/) | Next.js Deploying — Node.js server, Docker, static export, platform adapters |
| [nextjs-upgrading](./nextjs-upgrading/) | Next.js Upgrading — upgrade commands, version migration guides, codemods |
| [nextjs-project-structure](./nextjs-project-structure/) | Next.js Project Structure — file conventions, routing, route groups, private folders, organization |
| [nextjs-ai-agents](./nextjs-ai-agents/) | Next.js AI Coding Agents — AGENTS.md, bundled docs, MCP Server for AI agent configuration |
| [nextjs-mcp-server](./nextjs-mcp-server/) | Next.js MCP Server — real-time error detection, route inspection, live state for AI agents |
| [nextjs-analytics](./nextjs-analytics/) | Next.js Analytics — Web Vitals, useReportWebVitals, client instrumentation, external services |
| [nextjs-authentication](./nextjs-authentication/) | Next.js Authentication — sign-up/login, session management, authorization, DAL pattern |
| [nextjs-backend-for-frontend](./nextjs-backend-for-frontend/) | Next.js Backend for Frontend — Route Handlers, Proxy, content negotiation, webhooks, security |
| [nextjs-caching-previous-model](./nextjs-caching-previous-model/) | Next.js Caching Previous Model — fetch options, unstable_cache, route segment configs |
| [nextjs-cdn-caching](./nextjs-cdn-caching/) | Next.js CDN Caching — Cache-Control headers, Vary, static assets, pathname-based keying |
| [nextjs-ci-build-caching](./nextjs-ci-build-caching/) | Next.js CI Build Caching — GitHub Actions, GitLab CI, CircleCI, and other providers |
| [nextjs-content-security-policy](./nextjs-content-security-policy/) | Next.js Content Security Policy — nonces, Proxy, SRI, third-party scripts |
| [nextjs-css-in-js](./nextjs-css-in-js/) | Next.js CSS-in-JS — styled-components, styled-jsx, style registry pattern |
| [nextjs-custom-server](./nextjs-custom-server/) | Next.js Custom Server — programmatic control, Express, WebSocket, existing backends |
| [nextjs-data-security](./nextjs-data-security/) | Next.js Data Security — DAL, DTOs, taint APIs, Server Actions security, audit checklist |
| [nextjs-debugging](./nextjs-debugging/) | Next.js Debugging — VS Code, Chrome DevTools, Firefox, server-side and client-side |
| [nextjs-deploying-to-platforms](./nextjs-deploying-to-platforms/) | Next.js Deploying to Platforms — feature requirements, CDN compatibility, adapters |
| [nextjs-draft-mode](./nextjs-draft-mode/) | Next.js Draft Mode — preview draft content, headless CMS, Cache Components integration |
| [nextjs-environment-variables](./nextjs-environment-variables/) | Next.js Environment Variables — .env files, NEXT_PUBLIC_, load order, runtime vs build-time |
| [nextjs-forms](./nextjs-forms/) | Next.js Forms — Server Actions, validation, pending states, optimistic updates, useActionState |
| [nextjs-how-revalidation-works](./nextjs-how-revalidation-works/) | Next.js How Revalidation Works — tag system, multi-instance, cache handlers, graceful degradation |
| [nextjs-isr](./nextjs-isr/) | Next.js ISR — time-based revalidation, on-demand, generateStaticParams, multi-instance |
| [nextjs-instrumentation](./nextjs-instrumentation/) | Next.js Instrumentation — server startup code, OpenTelemetry, runtime-specific imports |
| [nextjs-internationalization](./nextjs-internationalization/) | Next.js Internationalization — locale routing, Proxy, dictionaries, static rendering |
| [nextjs-json-ld](./nextjs-json-ld/) | Next.js JSON-LD — structured data, schema.org, SEO rich results, TypeScript typing |
| [nextjs-lazy-loading](./nextjs-lazy-loading/) | Next.js Lazy Loading — next/dynamic, code splitting, SSR skip, external libraries |
| [nextjs-local-development](./nextjs-local-development/) | Next.js Local Development — Turbopack, antivirus, imports, Tailwind, Docker, tracing |
| [nextjs-mdx](./nextjs-mdx/) | Next.js MDX — @next/mdx setup, custom components, remark/rehype plugins, frontmatter |
