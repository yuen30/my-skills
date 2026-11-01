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

- Copy skill folder ทุกตัวที่มี `SKILL.md` (ค้นหาแบบ dynamic ไม่ hardcode รายชื่อ) ไปที่ `~/.agents/skills/<name>/` แล้วสร้าง symlink `~/.claude/skills/<name>` ชี้ไปที่นั่น
- Copy persona agent config (`my-agent/agents/*.md`) ไปที่ `~/.claude/agents/`
- แทนที่ skill folder ทั้งโฟลเดอร์ (ไฟล์ที่ลบใน repo จะหายจากเครื่องด้วย) และลบ skill ที่ repo เคยติดตั้งแต่เลิกใช้แล้วทั้งสองที่ (จดรายชื่อไว้ที่ `~/.claude/skills/.my-skills-installed`; ไม่แตะ plugin, `synced/` หรือ skill ที่ติดตั้งเองผ่าน `find-skills`)
- Persona ที่พักไว้ (`my-agent/agents-disabled/`: nine, fah, bank, khun-abe) ถูกคัดลอกไป `~/.claude/agents-disabled/` เท่านั้น ไม่เปิดใช้ — เปิดด้วย `mv ~/.claude/agents-disabled/<name>.md ~/.claude/agents/`
- ตั้ง `core.hooksPath=.githooks` ให้ repo นี้ — ก่อน commit จะรัน `scripts/check.py` (name/description, ลิงก์ references, `index.json`, persona อ้าง skill ที่มีจริง, ไฟล์ใน skill folder ที่ยังไม่ได้ `git add`)
- Idempotent — รันซ้ำได้ปลอดภัย ไม่มี prompt

แก้ `index.json` อัตโนมัติ: `python3 scripts/check.py --write-index` · skill จาก plugin ที่ persona อ้างได้: `scripts/external-skills.txt`

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
| [abe-ui](./abe-ui/) | UI kit skill on Tailwind CSS v4 — shadcn/ui or daisyUI (auto-detect), theming, dark mode, MCP/registry, visual design/aesthetics |
| [ci-cd](./ci-cd/) | CI/CD to AWS ECR/EC2/ECS — GitHub Actions and Bitbucket Pipelines, smoke test, rollback |
| [abe-data](./abe-data/) | ORM skill — Prisma, Drizzle, Eloquent, SQLAlchemy/Alembic: detect ORM, schema, migrations, queries, transactions, repository layer |
| [project-structure](./project-structure/) | Where code and folders go across stacks — Next.js/React layers, Go Fiber, monorepo, Astro, Django, Odoo, Frappe |
| [monorepo-scaffold-nextjs-go](./monorepo-scaffold-nextjs-go/) | Monorepo scaffold for Next.js 16+ App Router + Go 1.20+ microservices with shared infrastructure and swappable API adapters |

### Frameworks

`abe-framework` รวม framework ทุกตัวไว้ใน skill เดียว: ตรวจ stack ของโปรเจคก่อน แล้วอ่านเฉพาะ reference ที่ตรง (Next.js อ่าน docs ที่ bundle มากับแพ็กเกจเป็นหลัก)

| Skill | Description |
|-------|-------------|
| [abe-framework](./abe-framework/) | Next.js, React, Angular, Astro, React Three Fiber, Go Fiber v3, Hono, Laravel, Filament, Django, Odoo, Frappe — stack detection + per-framework references |

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
