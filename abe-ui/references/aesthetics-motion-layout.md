Read when designing a new look, landing page, or anything that should feel distinctive rather than default — motion, spatial composition, backgrounds, final checklist.

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
