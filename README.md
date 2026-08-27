# Skills Collection

คอลเลกชัน skills ส่วนตัวของ Taweechai Yuenyang

## Installation

```bash
npx skills add yuen30/my-skills
```

## รายการ Skills

### General

| Skill | Description |
|-------|-------------|
| [docker](./docker/) | Docker & Docker Compose best practices, templates, and troubleshooting |
| [http-status-codes](./http-status-codes/) | HTTP Status Codes — 1xx-5xx reference, REST API conventions, frontend/backend error handling |
| [react-three-fiber](./react-three-fiber/) | React Three Fiber (R3F), Three.js, and Drei helpers |
| [tailwind-v4-shadcn](./tailwind-v4-shadcn/) | Tailwind CSS v4 + shadcn/ui components |
| [shadcn-ui](./shadcn-ui/) | shadcn/ui — CLI, components, theming, customization, MCP server, registries |
| [daisyui](./daisyui/) | daisyUI semantic component classes on Tailwind CSS — check project choice vs shadcn/ui before applying |
| [go-fiber-v3](./go-fiber-v3/) | Go Fiber v3 — migration, Binding, Context interface, routing, client, services |
| [hono](./hono/) | Hono backend framework — routing, middleware, Context API, runtime target selection (Workers, Deno, Bun, Node.js), zod validation, type-safe RPC |
| [laravel](./laravel/) | Laravel (any recent major version) — patterns, breaking changes, and conventions across versions |
| [github-actions-cicd](./github-actions-cicd/) | GitHub Actions CI/CD — AWS ECR, EC2 deploy, smoke test, multi-service, rollback |
| [astro](./astro/) | Astro Framework — islands architecture, content collections, image optimization, hydration |
| [frontend-aesthetics](./frontend-aesthetics/) | Frontend Aesthetics — bold design thinking, typography, color, motion, spatial composition |
| [django](./django/) | Django Expert — Django 5.0, DRF, models, serializers, viewsets, ORM, JWT, testing |
| [prisma](./prisma/) | Prisma ORM — schema design, migrations, repository pattern, transactions, PostGIS |
| [drizzle-orm](./drizzle-orm/) | Drizzle ORM — schema definition, drizzle-kit migrations, relational + SQL-like queries, type inference, relations, repository pattern |
| [filament-ai-agents](./filament-ai-agents/) | Filament PHP workflow — resolve installed versions and read local bundled docs before implementing or reviewing code |
| [frontend-layer](./frontend-layer/) | Frontend layer separation — components/, hooks/, helpers/, types/, lib/ organization and strict concern boundaries |
| [monorepo-scaffold-nextjs-go](./monorepo-scaffold-nextjs-go/) | Monorepo scaffold for Next.js 16+ App Router + Go 1.20+ microservices with shared infrastructure and swappable API adapters |
| [angular](./angular/) | Angular framework — standalone components, signals, control flow syntax, dependency injection, version detection across major releases |
| [react](./react/) | Plain (non-Next.js) React development — client-rendered SPA patterns, hooks, state management, and common anti-patterns |
| [odoo-addons](./odoo-addons/) | Odoo addon/module development — models, views, security, wizards, version detection across major Odoo releases |
| [frappe-framework](./frappe-framework/) | Frappe Framework and ERPNext — DocTypes, hooks.py, ORM, whitelisted API methods, bench CLI |

### Next.js และ React

Next.js skills ชุดนี้ไม่ทำหน้าที่เป็นสำเนาเอกสาร framework อีกต่อไป ก่อนแก้โค้ดให้ resolve แพ็กเกจ `next` จาก app ที่เกี่ยวข้อง แล้วอ่านคู่มือใน `node_modules/next/dist/docs/` ให้ตรงกับเวอร์ชันที่ติดตั้ง โดยเฉพาะใน monorepo ที่ Next.js อาจไม่ได้อยู่ที่ repository root

| Skill | Description |
|-------|-------------|
| [nextjs-ai-agents](./nextjs-ai-agents/) | Workflow สำหรับ AI agent: local bundled docs เป็น source of truth และดูแล generated agent rules |
| [nextjs-clean-code](./nextjs-clean-code/) | Clean Code Architecture สำหรับทั้ง Next.js และ React — components/ui, hooks, helpers, lib, types และ feature layers |
| [nextjs-data-security](./nextjs-data-security/) | Security review — trust boundaries, auth/authz, Server Actions, Route Handlers, secrets และ data exposure |
| [nextjs-production-checklist](./nextjs-production-checklist/) | Production review — correctness, security, performance, caching, accessibility, SEO และ operations |
| [nextjs-upgrading](./nextjs-upgrading/) | Upgrade workflow — bundled migration guides, codemods, regression checks และ rollback |
| [nextjs-pages-router](./nextjs-pages-router/) | Legacy/hybrid Pages Router maintenance และ incremental migration |

### Meta / Internal Tooling

Tools and systems for managing this user's own Claude Code setup, agent configuration, and development workflow — not application frameworks or libraries.

| Skill | Description |
|-------|-------------|
| [my-agent](./my-agent/) | Backup and restore persona systems — Claude Code subagents, Codex CLI config, and opencode editor personas |
| [project-memory](./project-memory/) | Per-project memory notes — avoid re-deriving facts, decisions, and learnings across sessions |
| [ship](./ship/) | Shipping workflow — /ship slash command for commit + push + close GitHub issue automation |
