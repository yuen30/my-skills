---
name: daisyui
description: Use when a project uses daisyUI semantic component classes (btn, card, modal, etc.) on top of Tailwind CSS. daisyUI and shadcn/ui are alternative, usually-not-combined approaches — before applying either, check which one the project already uses (tailwind.config.*/CSS `@plugin "daisyui"` vs components.json/@radix-ui) and flag the choice rather than silently mixing both.
---

# daisyUI

daisyUI is a Tailwind CSS plugin that adds semantic component class names (`btn`, `card`, `modal`, `navbar`, ...) styled via CSS variables and swappable themes. This is a fundamentally different approach from shadcn/ui (unstyled Radix primitives copy-pasted into `components/ui/` and styled with raw utility classes) — the two are usually not combined in the same project.

## Decision Point — Check Before Applying

Before writing any daisyUI class or adding the plugin, determine which component approach the project already uses:

```shell
# daisyUI signals
grep -r '@plugin "daisyui"' --include='*.css' .
grep '"daisyui"' package.json
grep -r 'data-theme' --include='*.tsx' --include='*.html' -l .

# shadcn/ui signals
test -f components.json && cat components.json
grep '"@radix-ui' package.json
```

- If the project already has `components.json` / `@radix-ui/*` dependencies / a `components/ui/` folder of copy-pasted primitives — it's on shadcn/ui. Do not introduce daisyUI classes; use the `tailwind-v4-shadcn`/`shadcn-ui` skills instead.
- If the project already registers `@plugin "daisyui"` and uses `data-theme` — it's on daisyUI. Follow this skill.
- If neither exists yet (greenfield), surface the decision to the user/orchestrating agent explicitly rather than silently picking one — the two have very different component philosophies (semantic classes vs. owned/customizable source) and switching later is costly.

## Core Concepts (daisyUI v5)

### Installation (Tailwind v4)

daisyUI v5 targets Tailwind CSS v4 and registers as a CSS `@plugin`, not a `tailwind.config.js` entry:

```shell
npm install -D daisyui@latest
```

```css
/* app.css */
@import "tailwindcss";
@plugin "daisyui";
```

Optional config (theme list, base styles, logs) is passed inline in CSS:

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake;
  logs: false;
}
```

### Semantic component classes

Instead of composing raw utilities for every component, apply a semantic class and optional style/color/size modifiers:

```html
<button class="btn btn-primary btn-sm">Save</button>
<div class="card bg-base-100 shadow-md">
  <div class="card-body">
    <h2 class="card-title">Title</h2>
    <p>Body text</p>
  </div>
</div>
<input type="text" class="input input-bordered w-full" placeholder="Email" />
```

Common component classes to know: `btn`, `card`, `modal`, `navbar`, `drawer`, `dropdown`, `input`, `select`, `checkbox`, `toggle`, `badge`, `alert`, `tabs`, `table`, `avatar`, `menu`, `steps`, `loading`, `progress`, `tooltip`. Full list: `https://daisyui.com/components/`.

Modifier conventions:
- Color: `-primary`, `-secondary`, `-accent`, `-neutral`, `-info`, `-success`, `-warning`, `-error`
- Size: `-xs`, `-sm`, `-md`, `-lg`, `-xl`
- Style: e.g. `btn-outline`, `btn-ghost`, `btn-link` for buttons

Semantic classes are just Tailwind utility groups under the hood — regular Tailwind utilities (`flex`, `gap-4`, `p-4`) still compose fine alongside them.

### Theming

Themes are CSS variable sets (`base-100`, `primary`, `secondary`, etc.) selected via `data-theme` on `<html>` or any ancestor element — no `darkMode` config or `.dark` class wiring required (daisyUI handles it if a `--prefersdark` theme is registered):

```html
<html data-theme="light">
```

```html
<!-- Scoped theme override on a subtree -->
<div data-theme="cupcake">...</div>
```

Switch themes at runtime by setting the `data-theme` attribute via JS — no rebuild needed since themes are pure CSS.

Built-in themes: `light`, `dark`, `cupcake`, `bumblebee`, `emerald`, `corporate`, `synthwave`, `retro`, `cyberpunk`, and more — full list and a live picker at `https://daisyui.com/docs/themes/`. Custom themes can be defined as CSS variable blocks; see docs for the token list (`--color-primary`, `--radius-box`, `--size-field`, etc.).

### Accessibility notes

daisyUI provides styling only, not JS behavior/ARIA wiring for interactive components (`modal`, `dropdown`, `tabs`) — verify the markup pattern in the docs example includes correct roles/`aria-*`/keyboard handling (e.g. the `modal` component relies on a `<dialog>` element with native focus-trap behavior); do not assume a semantic class name alone makes a component accessible.

## Best Practices

- Prefer daisyUI semantic classes over hand-rolled utility compositions for standard components (buttons, cards, forms, alerts) — that's the point of the library.
- Use theme CSS variables (`bg-base-100`, `text-base-content`, etc.) rather than hardcoded Tailwind colors so components respect theme switching.
- Don't fight the plugin by overriding every daisyUI class with `!important`-style utility overrides — if heavy customization is needed on most components, shadcn/ui's copy-in-source model may be a better fit for that project; raise it as a decision point rather than layering both.
- Keep custom theme definitions in the CSS `@plugin "daisyui" { ... }` block or a dedicated theme CSS file, not scattered inline styles.

## Canonical Source

`https://daisyui.com/docs` — verify component class names, modifiers, and theme tokens here; daisyUI has changed conventions between v4 (`tailwind.config.js` plugin registration) and v5 (`@plugin` CSS directive) — confirm the installed major version before assuming installation syntax:

```shell
npm ls daisyui
```
