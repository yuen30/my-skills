Read when running the shadcn CLI, editing components.json, laying out component folders, extending a ui component, or debugging a shadcn setup.

## CLI Commands

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

## Structure and Extending

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

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot find `@/components/ui/button` | Check `tsconfig.json` paths match `components.json` aliases |
| Components look unstyled | Verify Tailwind CSS config + CSS variables in `:root` |
| Dark mode not working | Add `dark` class to `<html>` + use theme provider |
| TypeScript errors with forms | Install `@hookform/resolvers` and `zod` |
| Components not found after install | Restart dev server |
