# Skills Collection

คอลเลกชัน skills ส่วนตัวของ Taweechai Yuenyang

## Installation

```bash
npx skills add yuen30/my-skills
```

## Fresh Machine Setup

หลังลง macOS/OS ใหม่ หรือย้ายเครื่อง ให้ restore Claude Code setup ทั้งหมดด้วยคำสั่งเดียว:

```bash
git clone https://github.com/yuen30/my-skills.git
cd my-skills
./install.sh
```

`install.sh` จะ:

- Copy skill folder ทุกตัวที่มี `SKILL.md` (ค้นหาแบบ dynamic ไม่ hardcode รายชื่อ) ไปที่ `~/.claude/skills/<name>/`
- Copy persona agent config (`my-agent/agents/*.md`) ไปที่ `~/.claude/agents/`
- Idempotent — รันซ้ำได้ปลอดภัย ไม่มี prompt

Plugin ที่ persona เรียกใช้ (`install.sh` ไม่ได้ติดตั้งให้) — ติดตั้งครั้งเดียวต่อเครื่อง:

```bash
claude plugin marketplace add DietrichGebert/ponytail
claude plugin install ponytail@ponytail
```

`ponytail` เปิดโหมด "smallest complete change" อัตโนมัติทุก session/subagent; persona boss/toey/safe เรียก `ponytail:ponytail-review` และ `ponytail:ponytail-audit`

Mirror ของ codex/opencode ใน `my-agent/codex/` และ `my-agent/opencode/` เป็น reference เท่านั้น ไม่ได้อยู่ใน scope ของสคริปต์นี้ (คนละ path/format กับ Claude Code) — ต้อง restore เอง ถ้าต้องใช้

## รายการ Skills

### General

| Skill | Description |
|-------|-------------|
| [docker](./docker/) | Docker & Docker Compose best practices, templates, and troubleshooting |
| [redis](./redis/) | Redis as a cache layer — connection setup (Node/Python/Go), cache-aside, TTL, invalidation, distributed locks, pub/sub, docker-compose |
| [rabbitmq](./rabbitmq/) | RabbitMQ as a message broker — exchange types, ack/prefetch, dead-letter exchanges, docker-compose, idempotent consumers |
| [http-status-codes](./http-status-codes/) | HTTP Status Codes — 1xx-5xx reference, REST API conventions, frontend/backend error handling |
| [react-three-fiber](./react-three-fiber/) | React Three Fiber (R3F), Three.js, and Drei helpers |
| [abe-ui](./abe-ui/) | UI kit skill on Tailwind CSS v4 — shadcn/ui or daisyUI (auto-detect), CLI, components, theming, dark mode, MCP/registry |
| [go-fiber-v3](./go-fiber-v3/) | Go Fiber v3 — migration, Binding, Context interface, routing, client, services |
| [hono](./hono/) | Hono backend framework — routing, middleware, Context API, runtime target selection (Workers, Deno, Bun, Node.js), zod validation, type-safe RPC |
| [laravel](./laravel/) | Laravel (any recent major version) — patterns, breaking changes, and conventions across versions |
| [ci-cd](./ci-cd/) | CI/CD to AWS ECR/EC2/ECS — GitHub Actions and Bitbucket Pipelines, smoke test, rollback |
| [astro](./astro/) | Astro Framework — islands architecture, content collections, image optimization, hydration |
| [frontend-aesthetics](./frontend-aesthetics/) | Frontend Aesthetics — bold design thinking, typography, color, motion, spatial composition |
| [django](./django/) | Django Expert — Django 5.0, DRF, models, serializers, viewsets, ORM, JWT, testing |
| [prisma](./prisma/) | Prisma ORM — schema design, migrations, repository pattern, transactions, PostGIS |
| [drizzle-orm](./drizzle-orm/) | Drizzle ORM — schema definition, drizzle-kit migrations, relational + SQL-like queries, type inference, relations, repository pattern |
| [eloquent-orm](./eloquent-orm/) | Laravel Eloquent ORM — models, casts, relationships, eager loading, schema migrations, scopes, observers, soft deletes, repository pattern, factories |
| [sqlalchemy](./sqlalchemy/) | SQLAlchemy 2.0 for FastAPI — typed declarative models, loader strategies, async sessions, Alembic migrations, repository pattern, unit of work |
| [filament-ai-agents](./filament-ai-agents/) | Filament PHP workflow — resolve installed versions and read local bundled docs before implementing or reviewing code |
| [project-structure](./project-structure/) | Where code and folders go across stacks — Next.js/React layers, Go Fiber, monorepo, Astro, Django, Odoo, Frappe |
| [monorepo-scaffold-nextjs-go](./monorepo-scaffold-nextjs-go/) | Monorepo scaffold for Next.js 16+ App Router + Go 1.20+ microservices with shared infrastructure and swappable API adapters |
| [angular](./angular/) | Angular framework — standalone components, signals, control flow syntax, dependency injection, version detection across major releases |
| [react](./react/) | Plain (non-Next.js) React development — client-rendered SPA patterns, hooks, state management, and common anti-patterns |
| [odoo-addons](./odoo-addons/) | Odoo addon/module development — models, views, security, wizards, version detection across major Odoo releases |
| [frappe-framework](./frappe-framework/) | Frappe Framework and ERPNext — DocTypes, hooks.py, ORM, whitelisted API methods, bench CLI |

### Next.js และ React

Next.js skills ชุดนี้ไม่ทำหน้าที่เป็นสำเนาเอกสาร framework อีกต่อไป ก่อนแก้โค้ดให้ resolve แพ็กเกจ `next` จาก app ที่เกี่ยวข้อง แล้วอ่านคู่มือใน `node_modules/next/dist/docs/` ให้ตรงกับเวอร์ชันที่ติดตั้ง โดยเฉพาะใน monorepo ที่ Next.js อาจไม่ได้อยู่ที่ repository root

| Skill | Description |
|-------|-------------|
| [nextjs](./nextjs/) | Next.js workflow — bundled docs เป็น source of truth; AI-agent rules, data security, production checklist, upgrading, Pages Router |

### Meta / Internal Tooling

Tools and systems for managing this user's own Claude Code setup, agent configuration, and development workflow — not application frameworks or libraries.

| Skill | Description |
|-------|-------------|
| [my-agent](./my-agent/) | Backup and restore persona systems — Claude Code subagents, Codex CLI config, and opencode editor personas |
| [project-memory](./project-memory/) | Per-project work progress — what is in flight and how far it has got |
| [find-skills](./find-skills/) | Find the right skill — installed first, then skills.sh registry via `npx skills find`; install only with approval |
| [web-research](./web-research/) | Web research — pick bundled docs/Context7/WebSearch/browser/Exa, source priority, fetch budget, prompt-injection safety, sourced report |
| [ship](./ship/) | Shipping workflow — /ship slash command for commit + push + close GitHub issue automation |
| [context7-auto-research](./context7-auto-research/) | Auto-fetch current library/framework docs via the Context7 API before implementing — avoids outdated/hallucinated API usage |
