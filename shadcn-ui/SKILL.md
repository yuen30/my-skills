---
name: shadcn/ui
description: Expert guidance on using shadcn/ui — CLI commands, component installation, theming, customization, registry, MCP server, and composition patterns.
---

# shadcn/ui

Expert guidance on using shadcn/ui — CLI commands, component installation, theming, customization, registry, MCP server, and composition patterns.

## Core Concepts

shadcn/ui ไม่ใช่ component library แบบ npm package — เป็น **collection of reusable components** ที่ copy เข้า project:
- Components อยู่ใน source code ของคุณ (แก้ไขได้เต็มที่)
- ใช้ Radix UI primitives + Tailwind CSS
- CLI สำหรับ add/update components
- Theming ด้วย CSS variables

## Guidelines

### 1. Installation

```bash
npx shadcn@latest init
```

เลือก options:
- Style: New York (แนะนำ)
- Base color: Neutral / Zinc / Slate
- CSS variables: Yes
- Base library: Radix (default) หรือ Base

สร้าง `components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
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

### 2. CLI Commands

```bash
# Add components
npx shadcn@latest add button card dialog input

# Search components
npx shadcn@latest search "login"

# View component docs
npx shadcn@latest docs button

# Check project info
npx shadcn@latest info

# Diff (check updates)
npx shadcn@latest diff

# Add from registry
npx shadcn@latest add https://acme.com/r/hero.json

# Dry run (preview without installing)
npx shadcn@latest add button --dry-run

# Override existing files
npx shadcn@latest add button --overwrite
```

### 3. Using Components

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function LoginForm() {
  return (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Login</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="m@example.com" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" />
          </div>
          <Button type="submit" className="w-full">
            Sign In
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
```

### 4. Theming (CSS Variables)

```css
/* app/globals.css */
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

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

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
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
```

### 5. `cn()` Utility

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

ใช้สำหรับ conditional class merging:

```tsx
<Button className={cn("w-full", isLoading && "opacity-50")}>
  Submit
</Button>
```

### 6. Component Variants (CVA)

```tsx
// components/ui/button.tsx
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-white hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### 7. Common Component Patterns

#### Form with Validation

```tsx
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export function SettingsForm() {
  return (
    <form className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input id="name" placeholder="Your name" />
      </div>
      <div className="space-y-2">
        <Label htmlFor="role">Role</Label>
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Select a role" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="user">User</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <Button type="submit">Save Changes</Button>
    </form>
  )
}
```

#### Dialog

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function ConfirmDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="destructive">Delete</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Are you sure?</DialogTitle>
          <DialogDescription>
            This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline">Cancel</Button>
          <Button variant="destructive">Delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

#### Data Table

```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

export function UsersTable({ users }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id}>
            <TableCell className="font-medium">{user.name}</TableCell>
            <TableCell>{user.email}</TableCell>
            <TableCell>
              <Badge variant={user.active ? "default" : "secondary"}>
                {user.active ? "Active" : "Inactive"}
              </Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

### 8. Dark Mode

```tsx
// components/theme-provider.tsx
'use client'

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
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
```

### 9. MCP Server (AI Assistant Integration)

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

**Quick setup:**
```bash
npx shadcn@latest mcp init --client vscode
# or: --client cursor, --client claude, --client codex
```

MCP Server ให้ AI assistants:
- Browse components จาก registries
- Search components ตามชื่อ/functionality
- Install components ด้วย natural language

### 10. Custom Registries

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
# Install from custom registry
npx shadcn@latest add @acme/hero
npx shadcn@latest add @internal/auth-form
```

### 11. Customizing Components

Components อยู่ใน `components/ui/` — แก้ไขได้เต็มที่:

```tsx
// components/ui/button.tsx — customize ได้เลย
// เพิ่ม variant ใหม่
const buttonVariants = cva("...", {
  variants: {
    variant: {
      // ... existing variants
      gradient: "bg-gradient-to-r from-blue-500 to-purple-500 text-white",
    },
  },
})
```

### 12. Semantic Colors

| Variable | Usage |
|----------|-------|
| `--background` | Page background |
| `--foreground` | Default text |
| `--primary` | Primary buttons, links |
| `--secondary` | Secondary buttons |
| `--muted` | Muted backgrounds |
| `--muted-foreground` | Muted text |
| `--accent` | Hover states |
| `--destructive` | Error/delete actions |
| `--border` | Borders |
| `--input` | Input borders |
| `--ring` | Focus rings |
| `--radius` | Border radius base |

## Available Components

| Category | Components |
|----------|-----------|
| Layout | Card, Separator, ScrollArea, Sheet, Resizable |
| Forms | Input, Textarea, Select, Checkbox, RadioGroup, Switch, Slider, DatePicker |
| Buttons | Button, Toggle, ToggleGroup |
| Navigation | NavigationMenu, Tabs, Breadcrumb, Pagination, Sidebar |
| Feedback | Alert, Toast, Sonner, Progress, Skeleton, Badge |
| Overlay | Dialog, AlertDialog, Popover, Tooltip, HoverCard, DropdownMenu, ContextMenu |
| Data | Table, DataTable, Command, Combobox |
| Typography | Typography (prose styles) |

## Quick Reference

| Command | Purpose |
|---------|---------|
| `npx shadcn@latest init` | Initialize project |
| `npx shadcn@latest add [component]` | Add component(s) |
| `npx shadcn@latest add --all` | Add all components |
| `npx shadcn@latest search [query]` | Search components |
| `npx shadcn@latest docs [component]` | View docs |
| `npx shadcn@latest diff` | Check for updates |
| `npx shadcn@latest info` | Project info (JSON) |
| `npx shadcn@latest mcp init` | Setup MCP server |

## สรุป

1. **ไม่ใช่ npm package** — components copy เข้า project (แก้ไขได้)
2. **CLI** — `npx shadcn@latest add` สำหรับ install components
3. **Theming** — CSS variables (OKLCH) + dark mode
4. **`cn()` utility** — conditional class merging (clsx + tailwind-merge)
5. **CVA** — component variants (variant + size)
6. **Customize** — แก้ไข `components/ui/` ได้เต็มที่
7. **MCP Server** — AI assistants browse/search/install components
8. **Custom registries** — private/third-party component sources
