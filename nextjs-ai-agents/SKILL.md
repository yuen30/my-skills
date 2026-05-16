---
name: Next.js AI Coding Agents
description: Expert guidance on configuring Next.js projects for AI coding agents using AGENTS.md and bundled documentation for accurate, version-matched references.
---

# Next.js AI Coding Agents

Expert guidance on configuring Next.js projects for AI coding agents using AGENTS.md and bundled documentation for accurate, version-matched references.

@doc-version: 16.2.6

## Core Concepts

Next.js ships version-matched documentation inside the `next` package ที่ `node_modules/next/dist/docs/` — AI agents สามารถอ้างอิง APIs และ patterns ที่ถูกต้องตาม version ที่ติดตั้ง แทนที่จะใช้ training data ที่อาจ outdated

ไฟล์ `AGENTS.md` ที่ root ของโปรเจกต์บอก agents ให้อ่าน bundled docs ก่อนเขียน code

## Guidelines

### 1. How It Works

เมื่อติดตั้ง `next` — documentation ถูก bundle ไว้ที่:

```
node_modules/next/dist/docs/
├── 01-app/
│   ├── 01-getting-started/
│   ├── 02-guides/
│   └── 03-api-reference/
├── 02-pages/
├── 03-architecture/
└── index.mdx
```

**ข้อดี:**
- Docs ตรงกับ version ที่ติดตั้ง — ไม่ต้อง network request
- Agents ได้ข้อมูลที่ถูกต้อง ไม่ใช่ training data ที่ outdated
- ทำงาน offline ได้

### 2. New Projects (อัตโนมัติ)

`create-next-app` สร้าง `AGENTS.md` และ `CLAUDE.md` ให้อัตโนมัติ:

```bash
npx create-next-app@canary
```

ถ้าไม่ต้องการ:

```bash
npx create-next-app@canary --no-agents-md
```

### 3. Existing Projects (v16.2.0-canary.37+)

สร้าง 2 ไฟล์ที่ root ของโปรเจกต์:

#### AGENTS.md

```md
<!-- BEGIN:nextjs-agent-rules -->
# Next.js: ALWAYS read docs before coding

Before any Next.js work, find and read the relevant doc in `node_modules/next/dist/docs/`. Your training data is outdated — the docs are the source of truth.
<!-- END:nextjs-agent-rules -->
```

#### CLAUDE.md

```md
@AGENTS.md
```

> `CLAUDE.md` ใช้ `@` import syntax เพื่อ include `AGENTS.md` — Claude Code users ได้ instructions เดียวกันโดยไม่ duplicate content

### 4. For Earlier Versions (v16.1 and below)

ใช้ codemod:

```bash
npx @next/codemod@latest agents-md
```

- Output docs ไปที่ `.next-docs/` ใน project root (แทน `node_modules`)
- Generated agent files จะชี้ไปที่ directory นั้น

### 5. Understanding AGENTS.md

**โครงสร้าง:**
- `<!-- BEGIN:nextjs-agent-rules -->` / `<!-- END:nextjs-agent-rules -->` — ส่วนที่ Next.js จัดการ
- เพิ่ม project-specific instructions **นอก** markers ได้โดยไม่ถูก overwrite

**หลักการ:**
- Minimal instruction: "อ่าน bundled docs ก่อนเขียน code"
- Redirect agents จาก stale training data → accurate version-matched docs
- Bundled docs ครอบคลุม: guides, API references, file conventions (App Router + Pages Router)

### 6. Customizing AGENTS.md

เพิ่ม project-specific rules นอก markers:

```md
<!-- BEGIN:nextjs-agent-rules -->
# Next.js: ALWAYS read docs before coding

Before any Next.js work, find and read the relevant doc in `node_modules/next/dist/docs/`. Your training data is outdated — the docs are the source of truth.
<!-- END:nextjs-agent-rules -->

## Project-specific rules

- Use Tailwind CSS for all styling
- Use Server Components by default
- All data fetching must use "use cache" with cacheTag
- Forms must use Server Actions with useActionState
- Always validate input with Zod in Server Actions
- Use the /app/(marketing) group for public pages
- Use the /app/(dashboard) group for authenticated pages
```

### 7. Supported AI Agents

`AGENTS.md` ถูกอ่านอัตโนมัติโดย:
- Claude Code
- Cursor
- GitHub Copilot
- Kiro
- และ agents อื่นๆ ที่รองรับ `AGENTS.md` convention

### 8. Next.js MCP Server

นอกจาก bundled docs ยังใช้ Next.js MCP Server ให้ agents เข้าถึง application state ได้:

```json
{
  "mcpServers": {
    "nextjs": {
      "command": "npx",
      "args": ["next", "mcp"]
    }
  }
}
```

MCP Server ให้ agents:
- เข้าถึง dev server logs
- ดู build errors
- ตรวจสอบ route structure
- อ่าน runtime information

## File Structure

```
project/
├── AGENTS.md           # Instructions for all AI agents
├── CLAUDE.md           # Claude Code specific (imports AGENTS.md)
├── app/
├── next.config.ts
├── package.json
└── node_modules/
    └── next/
        └── dist/
            └── docs/   # Bundled version-matched documentation
```

## Quick Reference

| File | Purpose | Created by |
|------|---------|-----------|
| `AGENTS.md` | Instructions for AI agents | `create-next-app` or manual |
| `CLAUDE.md` | Claude Code specific | `create-next-app` or manual |
| `node_modules/next/dist/docs/` | Bundled documentation | `npm install next` |
| `.next-docs/` | Docs for v16.1 and below | `npx @next/codemod agents-md` |

## สรุป

1. **Next.js bundles docs** ใน `node_modules/next/dist/docs/` — ตรงกับ version ที่ติดตั้ง
2. **`AGENTS.md`** บอก agents ให้อ่าน bundled docs แทน training data
3. **New projects** — `create-next-app` สร้างให้อัตโนมัติ
4. **Existing projects** — สร้าง `AGENTS.md` + `CLAUDE.md` เอง
5. **Customize** ได้นอก `<!-- BEGIN/END -->` markers
6. **MCP Server** — ให้ agents เข้าถึง application state เพิ่มเติม
