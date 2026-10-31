---
name: shadcn-ui
description: shadcn/ui CLI, components.json, component usage, OKLCH theming, forms, dark mode, MCP server and registry. Use when running `npx shadcn add`, editing components.json or components/ui, theming shadcn components, or building a registry.
---

# shadcn/ui Component Library

Complete reference for shadcn/ui — CLI, installation, components, theming (OKLCH), forms (React Hook Form + Zod), dark mode, MCP server, registry, and best practices.

## Key Principles

- **Open Code** — Components copied into your project, not installed as dependencies
- **Composition** — Build complex UIs by composing simple components
- **Distribution** — CLI and registry system for easy component management
- **Beautiful Defaults** — Production-ready styling out of the box
- **AI-Ready** — Designed to work well with AI assistants

---

## Quick Reference — CLI Commands

```bash
# Initialize
npx shadcn@latest init

# Add components
npx shadcn@latest add button
npx shadcn@latest add button card dialog input
npx shadcn@latest add --all

# Search & browse
npx shadcn@latest add          # Interactive list
npx shadcn@latest search "login"
npx shadcn@latest docs button

# Update & diff
npx shadcn@latest diff

# Project info
npx shadcn@latest info

# From custom registry
npx shadcn@latest add @acme/hero

# Dry run
npx shadcn@latest add button --dry-run

# MCP server
npx shadcn@latest mcp init --client vscode
```

---

## Configuration (`components.json`)

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```

---

## Installation

See [references/setup.md](references/setup.md) — read when installing shadcn/ui in a new framework project (Next.js, Vite, etc.).

## Theming — CSS Variables (OKLCH)

See [references/theming.md](references/theming.md) — read when changing colors, OKLCH variables, @theme inline, or creating themes.

## `cn()` Utility

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Usage
<Button className={cn("w-full", isLoading && "opacity-50")} />
```

---

## Components Reference

See [references/components.md](references/components.md) — read when looking up usage of a specific component.

## Common Patterns

See [references/patterns.md](references/patterns.md) — read when building forms, data tables, dialogs or other composite UI.

## Dark Mode

See [references/dark-mode.md](references/dark-mode.md) — read when wiring dark mode / next-themes.

## MCP Server (AI Integration)

See [references/mcp-registry.md](references/mcp-registry.md) — read when using the shadcn MCP server.

## Registry System

See [references/mcp-registry.md](references/mcp-registry.md) — read when publishing or consuming a custom registry.

## Best Practices

### File Structure

```
src/components/
├── ui/                 # shadcn/ui components (customize freely)
│   ├── button.tsx
│   ├── card.tsx
│   └── ...
├── forms/              # Form compositions
│   ├── login-form.tsx
│   └── settings-form.tsx
├── layouts/            # Layout components
│   ├── header.tsx
│   └── sidebar.tsx
└── features/           # Feature-specific
    └── dashboard/
```

### Extending Components

```tsx
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"

interface LoadingButtonProps extends React.ComponentProps<typeof Button> {
  loading?: boolean
}

export function LoadingButton({ loading, children, ...props }: LoadingButtonProps) {
  return (
    <Button disabled={loading} {...props}>
      {loading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </Button>
  )
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot find `@/components/ui/button` | Check `tsconfig.json` paths match `components.json` aliases |
| Components look unstyled | Verify Tailwind CSS config + CSS variables in `:root` |
| Dark mode not working | Add `dark` class to `<html>` + use theme provider |
| TypeScript errors with forms | Install `@hookform/resolvers` and `zod` |
| Components not found after install | Restart dev server |
