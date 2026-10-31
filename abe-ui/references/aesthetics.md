Read when designing a new look, landing page, or anything that should feel distinctive rather than default — typography, color, motion, layout.

# Frontend Aesthetics & Creative UI

Guide for creating distinctive, production-grade frontend interfaces that avoid generic AI aesthetics — bold design thinking, typography, color, motion, spatial composition, and visual details.

## 🎯 Core Philosophy

สร้าง UI ที่ **unforgettable** — ไม่ใช่ generic "AI slop" ที่ดูเหมือนกันทุกที่ ทุก design ต้องมี **clear conceptual direction** และ execute ด้วย **precision**

**Bold maximalism** และ **refined minimalism** ทั้งคู่ใช้ได้ — key คือ **intentionality** ไม่ใช่ intensity

---

## ⚠️ Strict Rules — NEVER Do These

### ❌ Generic AI Aesthetics (BANNED)

| Banned | Why |
|--------|-----|
| Inter, Roboto, Arial, system fonts | Overused, zero personality |
| Purple gradients on white backgrounds | Cliché AI-generated look |
| Predictable card grids with rounded corners | Cookie-cutter, no context |
| Space Grotesk as default | Converging on same choice |
| Evenly-distributed pastel palettes | Timid, forgettable |
| Generic hero + 3-column features layout | Template aesthetic |

### ✅ Instead — Be Intentional

Every design must answer: **"What's the ONE thing someone will remember?"**

---

## 🧠 Design Thinking Process (Before Coding)

### Step 1: Understand Context

- **Purpose:** What problem does this interface solve?
- **Audience:** Who uses it? What do they expect/not expect?
- **Constraints:** Framework, performance, accessibility requirements

### Step 2: Commit to a BOLD Aesthetic Direction

Pick an extreme and commit fully:

| Direction | Characteristics |
|-----------|----------------|
| Brutally minimal | Extreme whitespace, single typeface, monochrome |
| Maximalist chaos | Layered, dense, colorful, overwhelming intentionally |
| Retro-futuristic | CRT effects, neon, monospace, dark backgrounds |
| Organic/natural | Flowing shapes, earth tones, hand-drawn elements |
| Luxury/refined | Serif fonts, gold accents, generous spacing, restraint |
| Playful/toy-like | Rounded, bouncy animations, bright primaries |
| Editorial/magazine | Strong grid, dramatic typography scale, pull quotes |
| Brutalist/raw | System fonts at extremes, borders, no decoration |
| Art deco/geometric | Symmetry, gold lines, angular patterns |
| Soft/pastel | Gentle gradients, rounded, light, airy |
| Industrial/utilitarian | Monospace, yellow/black, functional, no frills |
| Cyberpunk/glitch | Neon on dark, glitch effects, scanlines |

### Step 3: Define Differentiation

What makes this **UNFORGETTABLE**? Commit to ONE signature element:
- A dramatic typographic moment
- An unexpected color combination
- A surprising interaction pattern
- An unconventional layout structure
- A distinctive texture or atmosphere

---

## 🔤 Typography

### Rules

- **NEVER** use generic fonts (Inter, Roboto, Arial, system-ui)
- **ALWAYS** pair a distinctive display font with a refined body font
- **Vary** between projects — never converge on the same choice

### Approach

```css
/* ✅ CORRECT — Distinctive, intentional pairing */
:root {
  --font-display: 'Playfair Display', serif;    /* Editorial luxury */
  --font-body: 'Source Serif 4', serif;
}

/* ✅ CORRECT — Bold geometric */
:root {
  --font-display: 'Clash Display', sans-serif;  /* Sharp, modern */
  --font-body: 'Satoshi', sans-serif;
}

/* ✅ CORRECT — Retro-futuristic */
:root {
  --font-display: 'Space Mono', monospace;      /* Technical */
  --font-body: 'JetBrains Mono', monospace;
}

/* ❌ WRONG — Generic, forgettable */
:root {
  --font-display: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
}
```

### Typography Scale

```css
/* Dramatic scale creates hierarchy */
.hero-title {
  font-size: clamp(3rem, 8vw, 8rem);
  font-weight: 900;
  line-height: 0.9;
  letter-spacing: -0.03em;
}

.section-title {
  font-size: clamp(2rem, 4vw, 4rem);
  font-weight: 700;
  line-height: 1.1;
}

.body {
  font-size: clamp(1rem, 1.2vw, 1.25rem);
  line-height: 1.6;
}
```

---

## 🎨 Color & Theme

### Rules

- **Commit** to a cohesive palette — not scattered colors
- **Dominant colors** with sharp accents outperform timid, evenly-distributed palettes
- **Vary** between light and dark themes across projects

### Approach

```css
/* ✅ Bold, intentional palette */
:root {
  --color-bg: #0a0a0a;
  --color-surface: #141414;
  --color-text: #fafafa;
  --color-text-muted: #737373;
  --color-accent: #ff3d00;        /* ONE dominant accent */
  --color-accent-subtle: #ff3d0020;
}

/* ✅ Refined, restrained palette */
:root {
  --color-bg: #fdf6e3;
  --color-surface: #fff;
  --color-text: #1a1a1a;
  --color-text-muted: #6b6b6b;
  --color-accent: #c41e3a;        /* Deep, intentional red */
  --color-border: #e8e0d4;
}
```

