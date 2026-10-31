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

### Color Tone Recipes

Use tone recipes as brand layers on top of the default shadcn/ui neutral base. Keep colors in OKLCH, expose them through CSS variables, and avoid hard-coded hex values in components.

| Tone | Best for | Direction |
|------|----------|-----------|
| `executive` | SaaS dashboards, admin panels, CRM | Zinc surfaces, cyan focus, restrained contrast |
| `fintech` | Billing, analytics, finance tools | Ink neutrals, emerald primary, mint feedback |
| `studio` | Portfolios, creative tools, media apps | Charcoal base, violet primary, coral accent |
| `commerce` | Product, booking, marketplace UI | Warm neutral base, amber primary, rose accent |

```css
/* Apply on the root element: <html data-tone="executive"> */
:root[data-tone="executive"] {
  --primary: oklch(0.34 0.045 255);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.96 0.006 255);
  --secondary-foreground: oklch(0.25 0.035 255);
  --accent: oklch(0.9 0.07 215);
  --accent-foreground: oklch(0.23 0.04 255);
  --ring: oklch(0.68 0.13 215);
}

.dark[data-tone="executive"] {
  --primary: oklch(0.78 0.12 215);
  --primary-foreground: oklch(0.16 0.025 255);
  --secondary: oklch(0.25 0.018 255);
  --secondary-foreground: oklch(0.96 0.004 255);
  --accent: oklch(0.32 0.07 220);
  --accent-foreground: oklch(0.94 0.04 215);
  --ring: oklch(0.74 0.13 215);
}

:root[data-tone="fintech"] {
  --primary: oklch(0.46 0.14 155);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.96 0.02 160);
  --secondary-foreground: oklch(0.22 0.05 160);
  --accent: oklch(0.9 0.08 175);
  --accent-foreground: oklch(0.2 0.045 165);
  --ring: oklch(0.64 0.15 155);
}

.dark[data-tone="fintech"] {
  --primary: oklch(0.76 0.16 155);
  --primary-foreground: oklch(0.16 0.035 160);
  --secondary: oklch(0.24 0.035 165);
  --secondary-foreground: oklch(0.95 0.02 160);
  --accent: oklch(0.32 0.075 175);
  --accent-foreground: oklch(0.91 0.06 170);
  --ring: oklch(0.72 0.16 155);
}

:root[data-tone="studio"] {
  --primary: oklch(0.48 0.18 300);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.96 0.014 300);
  --secondary-foreground: oklch(0.24 0.055 300);
  --accent: oklch(0.88 0.1 25);
  --accent-foreground: oklch(0.23 0.05 25);
  --ring: oklch(0.66 0.17 300);
}

.dark[data-tone="studio"] {
  --primary: oklch(0.74 0.18 300);
  --primary-foreground: oklch(0.18 0.045 300);
  --secondary: oklch(0.25 0.04 300);
  --secondary-foreground: oklch(0.95 0.018 300);
  --accent: oklch(0.33 0.1 25);
  --accent-foreground: oklch(0.92 0.07 25);
  --ring: oklch(0.72 0.18 300);
}

:root[data-tone="commerce"] {
  --primary: oklch(0.6 0.16 70);
  --primary-foreground: oklch(0.18 0.035 70);
  --secondary: oklch(0.96 0.025 80);
  --secondary-foreground: oklch(0.25 0.045 65);
  --accent: oklch(0.9 0.075 20);
  --accent-foreground: oklch(0.24 0.055 20);
  --ring: oklch(0.68 0.15 65);
}

.dark[data-tone="commerce"] {
  --primary: oklch(0.78 0.15 70);
  --primary-foreground: oklch(0.18 0.035 70);
  --secondary: oklch(0.25 0.035 75);
  --secondary-foreground: oklch(0.95 0.025 80);
  --accent: oklch(0.34 0.09 20);
  --accent-foreground: oklch(0.93 0.055 25);
  --ring: oklch(0.76 0.14 65);
}
```

For data-heavy apps, start with `executive` or `fintech`. For public-facing product pages, start with `commerce` or `studio`, then keep the rest of the UI neutral so the tone does not dominate every surface.
