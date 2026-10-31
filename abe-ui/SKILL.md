---
name: abe-ui
description: "Tailwind CSS v4 UI with shadcn/ui or daisyUI: setup, components, theming, dark mode, visual design/aesthetics. Use for components.json, components/ui/, @radix-ui, daisyui, Tailwind v4 @theme, or building, styling or art-directing UI."
---

# abe-ui

UI work on Tailwind CSS v4 (CSS-first config) with either shadcn/ui or daisyUI. Detect the kit first, then read only the references you need.

## Step 1 — Detect the UI kit

```shell
test -f components.json && cat components.json
grep '"@radix-ui' package.json; ls components/ui 2>/dev/null
grep '"daisyui"' package.json; grep -r '@plugin "daisyui"' --include='*.css' .
```

| Signal | Kit | Read |
|--------|-----|------|
| `components.json`, `@radix-ui/*` dependency, or `components/ui/` folder | shadcn/ui | shadcn references below |
| `daisyui` in package.json or `@plugin "daisyui"` in CSS | daisyUI | [references/daisyui.md](references/daisyui.md) |
| Neither (greenfield) | undecided | Ask the user; recommend shadcn/ui by default. Do not pick silently, switching later is costly |

Never mix daisyUI classes into a shadcn/ui project or the reverse. They are alternatives: semantic classes (`btn`, `card`) vs owned source in `components/ui/` styled with utilities. If heavy daisyUI overrides are needed everywhere, raise shadcn/ui as a decision point instead of layering both.

## Shared Rules (both kits)

- **CSS-first Tailwind v4**: configure with `@import "tailwindcss"` plus `@theme`/`@plugin` in CSS; no `tailwind.config.js` (details in the Tailwind v4 reference).
- Use theme tokens (`bg-background`, `text-foreground` in shadcn; `bg-base-100`, `text-base-content` in daisyUI), not hardcoded colors, so theme and dark mode keep working.
- Prefer the kit's component over hand-rolled markup; compose, don't fork.
- Accessibility is not automatic: check roles, `aria-*`, focus and keyboard behavior on interactive parts.
- Confirm installed versions (`npm ls tailwindcss daisyui`) before using version-specific syntax.
- Design direction/aesthetics (distinctive look, typography, color, motion): [references/aesthetics.md](references/aesthetics.md).

## shadcn/ui Rules

- Components are copied into the project (open code); edit `components/ui/` directly and prefer shadcn components over building from scratch.
- Use `cn()` for conditional classes:

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs))
```

- Add components with `npx shadcn@latest add <name>` (full CLI in the CLI reference).

## Where to Read More

| Topic | Reference | Read when |
|-------|-----------|-----------|
| Tailwind v4 | [references/tailwind-v4.md](references/tailwind-v4.md) | Configuring `@theme`, the Vite plugin, or migrating v3 to v4 (either kit) |
| daisyUI | [references/daisyui.md](references/daisyui.md) | Project uses daisyUI: install, classes, `data-theme` themes |
| shadcn setup | [references/setup.md](references/setup.md) | Installing shadcn/ui in a new Next.js, Vite or TanStack project |
| shadcn CLI | [references/shadcn-cli.md](references/shadcn-cli.md) | CLI commands, `components.json`, folder layout, extending components, troubleshooting |
| shadcn theming | [references/theming.md](references/theming.md) | Changing colors, OKLCH variables, `@theme inline`, creating themes |
| shadcn components | [references/components.md](references/components.md) | Looking up usage of a specific component |
| shadcn patterns | [references/patterns.md](references/patterns.md) | Building forms, data tables, dialogs, composite UI |
| shadcn dark mode | [references/dark-mode.md](references/dark-mode.md) | Wiring dark mode / next-themes |
| shadcn MCP and registry | [references/mcp-registry.md](references/mcp-registry.md) | Using the shadcn MCP server, publishing or consuming a registry |
| aesthetics | [references/aesthetics.md](references/aesthetics.md) | Designing a distinctive look: art direction, typography, color |
| aesthetics (motion, layout) | [references/aesthetics-motion-layout.md](references/aesthetics-motion-layout.md) | Motion, spatial composition, backgrounds, final design checklist |
