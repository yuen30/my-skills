---
name: Next.js MCP Server
description: Expert guidance on enabling Next.js MCP Server for AI coding agents — real-time error detection, live state queries, route inspection, and development tools.
---

# Next.js MCP Server

Expert guidance on enabling Next.js MCP Server for AI coding agents — real-time error detection, live state queries, route inspection, and development tools.

@doc-version: 16.2.6

## Core Concepts

Next.js 16+ includes MCP (Model Context Protocol) support ที่ให้ AI coding agents เข้าถึง application internals แบบ real-time ผ่าน built-in endpoint `/_next/mcp`

ใช้ package `next-devtools-mcp` เป็น bridge ระหว่าง agents กับ dev server

## Guidelines

### 1. Getting Started

**Requirements:** Next.js 16+

สร้างไฟล์ `.mcp.json` ที่ root ของโปรเจกต์:

```json
{
  "mcpServers": {
    "next-devtools": {
      "command": "npx",
      "args": ["-y", "next-devtools-mcp@latest"]
    }
  }
}
```

เมื่อ start dev server — `next-devtools-mcp` จะ discover และ connect อัตโนมัติ

### 2. Development Workflow

```bash
# 1. Start dev server
npm run dev

# 2. Agent connects อัตโนมัติผ่าน next-devtools-mcp
# 3. เปิด browser ดูหน้าเว็บ
# 4. ถาม agent เกี่ยวกับ errors, routes, state
```

### 3. Available Tools

#### Application Runtime Access

| Tool | Purpose |
|------|---------|
| `get_errors` | ดึง build errors, runtime errors, type errors จาก dev server |
| `get_logs` | ดึง path ไปยัง log file (browser console + server output) |
| `get_page_metadata` | ดึง metadata ของหน้าเฉพาะ (routes, components, rendering info) |
| `get_project_metadata` | ดึง project structure, configuration, dev server URL |
| `get_routes` | ดึง routes ทั้งหมด (appRouter + pagesRouter) |
| `get_server_action_by_id` | ค้นหา Server Actions ตาม ID (source file + function name) |

#### Development Tools

| Capability | Description |
|-----------|-------------|
| Next.js Knowledge Base | Query documentation และ best practices |
| Migration Tools | Automated helpers สำหรับ upgrade + codemods |
| Caching Guide | Setup assistance สำหรับ Cache Components |
| Browser Testing | Playwright MCP integration สำหรับ verify pages |

### 4. Capabilities in Detail

#### Error Detection

Agent สามารถ:
- ดึง build errors, runtime errors, type errors แบบ real-time
- วิเคราะห์ errors และแนะนำ fixes
- ตรวจจับ hydration mismatches

```
User: "What errors are currently in my application?"

Agent จะ:
1. Query dev server ผ่าน get_errors
2. ดึง errors ทั้งหมด (build, runtime, type)
3. วิเคราะห์และแนะนำ actionable fixes
```

#### Route Inspection

```
User: "Show me all routes in my app"

Agent จะ:
1. เรียก get_routes
2. แสดง routes grouped by router type
3. Dynamic segments แสดงเป็น [param] หรือ [...slug]
```

#### Page Metadata

```
User: "What components render on /dashboard?"

Agent จะ:
1. เรียก get_page_metadata สำหรับ /dashboard
2. แสดง layout hierarchy, components, rendering mode
```

#### Upgrade Assistance

```
User: "Help me upgrade to Next.js 16"

Agent จะ:
1. วิเคราะห์ current version
2. แนะนำ automated migrations + codemods
3. ให้ step-by-step instructions สำหรับ breaking changes
```

### 5. How It Works (Architecture)

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  AI Agent       │────▶│  next-devtools-mcp   │────▶│  Next.js Dev    │
│  (Claude, etc.) │◀────│  (MCP Bridge)        │◀────│  Server         │
└─────────────────┘     └──────────────────────┘     │  /_next/mcp     │
                                                      └─────────────────┘
```

- Next.js dev server expose MCP endpoint ที่ `/_next/mcp`
- `next-devtools-mcp` discover และ communicate กับ endpoints
- รองรับ multiple Next.js instances บน different ports
- Forward tool calls ไปยัง appropriate dev server

### 6. Benefits for Agent-Assisted Development

Agents สามารถ:
- **Context-aware suggestions** — แนะนำตำแหน่งที่ถูกต้องสำหรับ features ใหม่
- **Query live state** — เช็ค configuration, routes, proxy ขณะ develop
- **Understand layout hierarchy** — รู้ว่า page/layout ไหน render อยู่
- **Accurate implementations** — generate code ตาม patterns ของโปรเจกต์

### 7. Multi-Instance Support

`next-devtools-mcp` รองรับหลาย Next.js instances:

```json
{
  "mcpServers": {
    "next-devtools": {
      "command": "npx",
      "args": ["-y", "next-devtools-mcp@latest"]
    }
  }
}
```

- Auto-discover instances บน different ports
- Unified interface สำหรับ agents
- ไม่ต้อง config port เอง

### 8. Troubleshooting

| ปัญหา | วิธีแก้ |
|--------|---------|
| MCP server not connecting | ตรวจสอบว่าใช้ Next.js v16+ |
| Agent ไม่เห็น tools | ตรวจสอบ `.mcp.json` ที่ project root |
| ไม่ได้ข้อมูล | Start dev server ก่อน: `npm run dev` |
| ข้อมูลเก่า | Restart dev server |
| Agent ไม่ load config | Restart agent/IDE |

## Example: Complete Setup

```
project/
├── .mcp.json           # MCP server configuration
├── AGENTS.md           # Agent instructions (bundled docs)
├── CLAUDE.md           # Claude Code specific
├── app/
│   ├── layout.tsx
│   └── page.tsx
├── next.config.ts
└── package.json
```

`.mcp.json`:
```json
{
  "mcpServers": {
    "next-devtools": {
      "command": "npx",
      "args": ["-y", "next-devtools-mcp@latest"]
    }
  }
}
```

`AGENTS.md`:
```md
<!-- BEGIN:nextjs-agent-rules -->
# Next.js: ALWAYS read docs before coding

Before any Next.js work, find and read the relevant doc in `node_modules/next/dist/docs/`. Your training data is outdated — the docs are the source of truth.
<!-- END:nextjs-agent-rules -->
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `/_next/mcp` | Built-in MCP endpoint ใน dev server |
| `next-devtools-mcp` | Bridge package ระหว่าง agents กับ dev server |
| `.mcp.json` | Configuration file สำหรับ MCP servers |
| `AGENTS.md` | Instructions ให้ agents อ่าน bundled docs |

## สรุป

1. **เพิ่ม `.mcp.json`** ที่ project root — config `next-devtools-mcp`
2. **Start dev server** — `npm run dev`
3. **Agent connects อัตโนมัติ** — ไม่ต้อง setup เพิ่ม
4. **Tools ที่ได้:** errors, logs, routes, page metadata, server actions
5. **รองรับ multi-instance** — auto-discover different ports
6. **ใช้ร่วมกับ AGENTS.md** — agents ได้ทั้ง docs + live state
