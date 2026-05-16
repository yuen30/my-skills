---
name: shadcn/ui Component Library
description: Complete reference for shadcn/ui — CLI, installation, components, theming (OKLCH), forms (React Hook Form + Zod), dark mode, MCP server, registry, and best practices.
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

### Vite + React + TypeScript (Recommended)

```bash
# 1. Create project
npm create vite@latest my-app -- --template react-ts

# 2. Add Tailwind CSS
npm install tailwindcss @tailwindcss/vite

# 3. Configure vite.config.ts
```

```ts
// vite.config.ts
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

```json
// tsconfig.json — add paths
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

```bash
# 4. Initialize shadcn/ui
npx shadcn@latest init

# 5. Add components
npx shadcn@latest add button card
```

### Next.js (App Router)

```bash
npx shadcn@latest init
# Select: New York style, Neutral base color, CSS variables: Yes
```

### TanStack Router

```bash
npx create-tsrouter-app@latest my-app --template file-router --tailwind --add-ons shadcn
```

---

## Theming — CSS Variables (OKLCH)

```css
/* src/index.css */
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.625rem;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.396 0.141 25.723);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### Using Theme Colors

```tsx
<div className="bg-background text-foreground" />
<div className="bg-primary text-primary-foreground" />
<div className="bg-secondary text-secondary-foreground" />
<div className="bg-muted text-muted-foreground" />
<div className="bg-accent text-accent-foreground" />
<div className="bg-destructive text-destructive-foreground" />
<div className="border-border" />
```

---

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

### Form & Input

| Component | Install | Description |
|-----------|---------|-------------|
| Form | `add form` | React Hook Form + Zod |
| Field | `add field` | Form field with label/error |
| Button | `add button` | Multiple variants |
| Input | `add input` | Text input |
| Input OTP | `add input-otp` | One-time password |
| Textarea | `add textarea` | Multi-line |
| Checkbox | `add checkbox` | Checkbox |
| Radio Group | `add radio-group` | Radio buttons |
| Select | `add select` | Dropdown |
| Switch | `add switch` | Toggle switch |
| Slider | `add slider` | Range slider |
| Calendar | `add calendar` | Date selection |
| Date Picker | `add date-picker` | Input + calendar |
| Combobox | `add combobox` | Searchable select |

### Layout & Navigation

| Component | Install | Description |
|-----------|---------|-------------|
| Accordion | `add accordion` | Collapsible sections |
| Breadcrumb | `add breadcrumb` | Navigation trail |
| Navigation Menu | `add navigation-menu` | Accessible nav |
| Sidebar | `add sidebar` | Collapsible sidebar |
| Tabs | `add tabs` | Tabbed interface |
| Separator | `add separator` | Visual divider |
| Scroll Area | `add scroll-area` | Custom scrollbar |
| Resizable | `add resizable` | Resizable panels |

### Overlay & Dialog

| Component | Install | Description |
|-----------|---------|-------------|
| Dialog | `add dialog` | Modal |
| Alert Dialog | `add alert-dialog` | Confirmation |
| Sheet | `add sheet` | Slide-out panel |
| Drawer | `add drawer` | Mobile drawer (Vaul) |
| Popover | `add popover` | Floating content |
| Tooltip | `add tooltip` | Hover info |
| Dropdown Menu | `add dropdown-menu` | Dropdown |
| Context Menu | `add context-menu` | Right-click |
| Command | `add command` | Command palette (cmdk) |

### Feedback & Status

| Component | Install | Description |
|-----------|---------|-------------|
| Alert | `add alert` | Messages |
| Toast | `add toast` | Notifications (Sonner) |
| Progress | `add progress` | Progress bar |
| Spinner | `add spinner` | Loading |
| Skeleton | `add skeleton` | Loading placeholder |
| Badge | `add badge` | Labels/status |

### Display & Data

| Component | Install | Description |
|-----------|---------|-------------|
| Avatar | `add avatar` | Profile images |
| Card | `add card` | Card container |
| Table | `add table` | Data table |
| Data Table | `add data-table` | TanStack Table |
| Chart | `add chart` | Charts (Recharts) |
| Carousel | `add carousel` | Carousel (Embla) |

---

## Common Patterns

### Form with React Hook Form + Zod

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form, FormControl, FormField, FormItem, FormLabel, FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", password: "" },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="email@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

### Button Variants

```tsx
<Button variant="default">Default</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

<Button size="default">Default</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><IconName /></Button>
```

### Installing Components for Features

```bash
# Authentication flow
npx shadcn@latest add button input form label card

# Dashboard layout
npx shadcn@latest add sidebar navigation-menu breadcrumb avatar dropdown-menu

# Data display
npx shadcn@latest add table data-table pagination skeleton

# Forms
npx shadcn@latest add form field input select checkbox radio-group switch calendar date-picker combobox

# Feedback
npx shadcn@latest add alert toast dialog alert-dialog
```

---

## Dark Mode

### Vite (next-themes)

```bash
npm install next-themes
```

```tsx
// src/components/theme-provider.tsx
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  )
}
```

```tsx
// src/main.tsx
import { ThemeProvider } from "@/components/theme-provider"

<ThemeProvider>
  <App />
</ThemeProvider>
```

---

## MCP Server (AI Integration)

```json
// .mcp.json (Claude Code)
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

```json
// .cursor/mcp.json (Cursor)
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

```json
// .vscode/mcp.json (VS Code / Kiro)
{
  "servers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

Quick setup: `npx shadcn@latest mcp init --client vscode`

---

## Registry System

### Custom Registries

```json
// components.json
{
  "registries": {
    "@acme": "https://acme.com/r/{name}.json",
    "@internal": {
      "url": "https://internal.company.com/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}"
      }
    }
  }
}
```

```bash
npx shadcn@latest add @acme/hero
npx shadcn@latest add @internal/auth-form
```

---

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

---

## สรุป

1. **Open Code** — components อยู่ใน project (แก้ไขได้เต็มที่)
2. **CLI** — `npx shadcn@latest add` สำหรับ install
3. **Theming** — CSS variables (OKLCH) + `@theme inline`
4. **`cn()` utility** — clsx + tailwind-merge
5. **Forms** — React Hook Form + Zod + Form components
6. **Dark mode** — next-themes + `.dark` class
7. **MCP Server** — AI assistants browse/search/install
8. **Registry** — custom/private component sources
9. **Customize** — แก้ไข `components/ui/` ได้เต็มที่
10. **Dependencies** — `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`
