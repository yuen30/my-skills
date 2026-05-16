---
name: Frontend Aesthetics & Creative UI
description: Guide for creating distinctive, production-grade frontend interfaces that avoid generic AI aesthetics — bold design thinking, typography, color, motion, spatial composition, and visual details.
---

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
- Use **CSS variables** for consistency
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

---

## ✨ Motion & Animation

### Rules

- **Prioritize CSS-only** solutions for HTML
- Use **Motion library** (Framer Motion) for React when available
- **One well-orchestrated page load** with staggered reveals > scattered micro-interactions
- Focus on **high-impact moments**

### Page Load — Staggered Reveals

```css
/* ✅ Orchestrated entrance */
@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.reveal {
  animation: reveal 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.reveal:nth-child(1) { animation-delay: 0.1s; }
.reveal:nth-child(2) { animation-delay: 0.2s; }
.reveal:nth-child(3) { animation-delay: 0.3s; }
.reveal:nth-child(4) { animation-delay: 0.4s; }
```

### Hover States That Surprise

```css
/* ✅ Unexpected, delightful hover */
.card {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.4s ease;
}

.card:hover {
  transform: translateY(-8px) rotate(-1deg);
  box-shadow: 0 20px 60px -10px rgba(0, 0, 0, 0.3);
}

/* ✅ Text reveal on hover */
.link {
  position: relative;
  overflow: hidden;
}

.link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--color-accent);
  transform: translateX(-101%);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.link:hover::after {
  transform: translateX(0);
}
```

### React (Motion Library)

```tsx
import { motion } from 'motion/react'

function HeroSection() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
    >
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        Bold Statement
      </motion.h1>
    </motion.div>
  )
}
```

---

## 📐 Spatial Composition

### Rules

- **Unexpected layouts** — asymmetry, overlap, diagonal flow
- **Grid-breaking elements** — items that escape their containers
- **Generous negative space** OR **controlled density** (not in-between)

### Techniques

```css
/* ✅ Asymmetric grid */
.layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
}

/* ✅ Overlapping elements */
.overlap-card {
  margin-top: -4rem;
  position: relative;
  z-index: 10;
}

/* ✅ Breaking the grid */
.breakout {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
}

/* ✅ Dramatic whitespace */
.hero {
  padding: 12rem 0;
  min-height: 100vh;
  display: flex;
  align-items: center;
}
```

---

## 🖼️ Backgrounds & Visual Details

### Rules

- **Create atmosphere and depth** — never default to solid white/gray
- Add **contextual effects** that match the aesthetic
- Layer transparencies, textures, patterns

### Techniques

```css
/* ✅ Gradient mesh background */
.bg-mesh {
  background:
    radial-gradient(at 20% 80%, rgba(255, 61, 0, 0.1) 0%, transparent 50%),
    radial-gradient(at 80% 20%, rgba(0, 102, 255, 0.08) 0%, transparent 50%),
    var(--color-bg);
}

/* ✅ Noise texture overlay */
.bg-noise::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,..."); /* noise SVG */
  opacity: 0.03;
  pointer-events: none;
}

/* ✅ Geometric pattern */
.bg-dots {
  background-image: radial-gradient(circle, var(--color-border) 1px, transparent 1px);
  background-size: 24px 24px;
}

/* ✅ Dramatic shadow depth */
.elevated {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 4px 8px rgba(0, 0, 0, 0.04),
    0 16px 32px rgba(0, 0, 0, 0.08),
    0 32px 64px rgba(0, 0, 0, 0.08);
}

/* ✅ Glass morphism (when appropriate) */
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

---

## 🎯 Implementation Complexity Rule

**Match code complexity to aesthetic vision:**

| Vision | Implementation |
|--------|---------------|
| Maximalist | Elaborate code, extensive animations, layered effects, many elements |
| Minimalist | Restraint, precision, careful spacing, subtle details, fewer elements done perfectly |
| Editorial | Strong typography system, dramatic scale, precise grid |
| Brutalist | Raw HTML, system extremes, intentional ugliness |

---

## ✅ Checklist Before Delivering

```
□ Does it have a clear, BOLD aesthetic direction?
□ Is the typography distinctive (not Inter/Roboto)?
□ Is the color palette intentional (not generic purple gradient)?
□ Is there at least ONE unforgettable visual moment?
□ Are animations orchestrated (not scattered)?
□ Does the layout have spatial interest (not just stacked cards)?
□ Is the background creating atmosphere (not plain white)?
□ Does it feel genuinely DESIGNED for this specific context?
□ Would a human designer be proud of this?
□ Is it different from the last thing generated?
```

---

## สรุป

1. **NEVER generic** — no Inter, no purple gradients, no cookie-cutter layouts
2. **Commit to a direction** — pick an extreme aesthetic and execute fully
3. **Typography is identity** — distinctive fonts, dramatic scale
4. **Color with conviction** — dominant + sharp accent, not scattered
5. **Motion with purpose** — orchestrated reveals > random micro-interactions
6. **Spatial interest** — asymmetry, overlap, generous whitespace
7. **Atmosphere** — textures, gradients, depth, not flat solid colors
8. **Match complexity to vision** — maximalist = elaborate, minimal = precise
9. **Every design is unique** — vary themes, fonts, aesthetics between projects
10. **One unforgettable moment** — what will someone remember?
