Read when configuring Tailwind CSS v4 (CSS-first config, @theme tokens), replacing tailwind.config.js, or migrating from v3.

## Tailwind CSS v4 Key Changes

- **CSS-first config**: No more `tailwind.config.js` — configure in CSS with `@theme`
- **New import**: Use `@import "tailwindcss"` instead of `@tailwind` directives
- **Native CSS variables**: Theme values are CSS custom properties by default
- **Automatic content detection**: No need to configure `content` paths
- **New default color palette**: Updated colors with OKLCH

## v3 → v4 Migration Checklist

1. `npm install tailwindcss @tailwindcss/vite` and add the plugin (see Vite plugin below)
2. Replace `@tailwind base/components/utilities` with `@import "tailwindcss";`
3. Move `tailwind.config.js` theme values into a CSS `@theme { ... }` block; delete the config and `content` paths
4. Dark mode: add `@custom-variant dark (&:is(.dark *));`
5. In `components.json`, set `tailwind.config` to `""`

## Vite Plugin

```bash
npm install tailwindcss @tailwindcss/vite
```

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* app.css */
@import "tailwindcss";
```

## Theme Customization (CSS-first)

```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.6 0.25 260);
  --color-secondary: oklch(0.7 0.15 180);
  --font-sans: "Inter", sans-serif;
  --radius-lg: 0.75rem;
  --breakpoint-3xl: 1920px;
}
```

## Responsive Design

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Cards */}
</div>
```

## Tips

- Use CSS variables from `@theme` for consistent design tokens
- Use `@apply` sparingly — prefer utility classes in markup
- Leverage v4 features: container queries (`@container`), `@starting-style`

## Dependencies

```json
{
  "tailwindcss": "^4",
  "@tailwindcss/vite": "^4",
  "class-variance-authority": "^0.7",
  "clsx": "^2",
  "tailwind-merge": "^3"
}
```
