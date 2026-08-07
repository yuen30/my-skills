---
name: Next.js View Transitions
description: Expert guidance on view transitions in Next.js — shared element morphs, Suspense reveals, directional navigation, crossfades, and CSS animations.
---

# Next.js View Transitions

Expert guidance on view transitions in Next.js — shared element morphs, Suspense reveals, directional navigation, crossfades, and CSS animations.

@doc-version: 16.2.6

## Core Concepts

View Transitions ใช้ browser's View Transitions API ผ่าน React `<ViewTransition>` component:
- **Shared element morph** — same element animates between routes
- **Suspense reveal** — skeleton → content with animation
- **Directional slide** — forward/back navigation direction
- **Crossfade** — content swap within same route

## Setup

```ts
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  experimental: {
    viewTransition: true,
  },
}

export default nextConfig
```

```tsx
import { ViewTransition } from 'react'
```

> View Transitions activate during Transitions (route navigations), `<Suspense>`, and `useDeferredValue` — ไม่ใช่ regular `setState`

## Guidelines

### 1. Shared Element Morph

ให้ element เดียวกัน animate ระหว่าง 2 routes ด้วย `name` prop เดียวกัน:

```tsx
// Grid page — thumbnail
<Link href={`/photo/${photo.id}`}>
  <ViewTransition name={`photo-${photo.id}`}>
    <Image src={photo.src} alt={photo.title} />
  </ViewTransition>
</Link>
```

```tsx
// Detail page — hero image
<ViewTransition name={`photo-${photo.id}`}>
  <Image src={photo.src} alt={photo.title} fill />
</ViewTransition>
```

- `name` สร้าง identity — React animate ระหว่าง old/new positions
- ไม่ต้อง CSS เพิ่ม — morph ทำงานอัตโนมัติ
- Navigate back → reverse morph

#### Custom Morph Animation

```tsx
<ViewTransition name={`photo-${photo.id}`} share="morph">
  <Image src={photo.src} alt={photo.title} />
</ViewTransition>
```

```css
::view-transition-group(.morph) {
  animation-duration: 400ms;
}

::view-transition-image-pair(.morph) {
  animation-name: via-blur;
}

@keyframes via-blur {
  30% { filter: blur(3px); }
}
```

### 2. Suspense Reveals (Loading → Content)

```tsx
// app/photo/[id]/page.tsx
import { Suspense, ViewTransition } from 'react'

export default async function PhotoPage({ params }) {
  const { id } = await params

  return (
    <Suspense
      fallback={
        <ViewTransition exit="slide-down">
          <PhotoContentSkeleton />
        </ViewTransition>
      }
    >
      <ViewTransition enter="slide-up" default="none">
        <PhotoContent id={id} />
      </ViewTransition>
    </Suspense>
  )
}
```

```css
:root {
  --duration-exit: 150ms;
  --duration-enter: 210ms;
}

::view-transition-old(.slide-down) {
  animation:
    var(--duration-exit) ease-out both fade reverse,
    var(--duration-exit) ease-out both slide-y reverse;
}

::view-transition-new(.slide-up) {
  animation:
    var(--duration-enter) ease-in var(--duration-exit) both fade,
    400ms ease-in both slide-y;
}

@keyframes fade {
  from { filter: blur(3px); opacity: 0; }
  to { filter: blur(0); opacity: 1; }
}

@keyframes slide-y {
  from { transform: translateY(10px); }
  to { transform: translateY(0); }
}
```

**Timing:** Exit fast (150ms) → Enter slow (210ms) with delay — old leaves before new arrives

### 3. Directional Navigation

#### Tag Links with `transitionTypes`

```tsx
// Forward navigation
<Link href={`/photo/${photo.id}`} transitionTypes={['nav-forward']}>
  View Photo
</Link>

// Back navigation
<Link href="/" transitionTypes={['nav-back']}>
  ← Gallery
</Link>
```

#### Map Types to Animations

```tsx
<ViewTransition
  enter={{
    'nav-forward': 'nav-forward',
    'nav-back': 'nav-back',
    default: 'none',
  }}
  exit={{
    'nav-forward': 'nav-forward',
    'nav-back': 'nav-back',
    default: 'none',
  }}
  default="none"
>
  {/* page content */}
</ViewTransition>
```

```css
::view-transition-old(.nav-forward) {
  --slide-offset: -60px;
  animation: 150ms ease-in both fade reverse, 400ms ease-in-out both slide reverse;
}

::view-transition-new(.nav-forward) {
  --slide-offset: 60px;
  animation: 210ms ease-out 150ms both fade, 400ms ease-in-out both slide;
}

::view-transition-old(.nav-back) {
  --slide-offset: 60px;
  animation: 150ms ease-in both fade reverse, 400ms ease-in-out both slide reverse;
}

::view-transition-new(.nav-back) {
  --slide-offset: -60px;
  animation: 210ms ease-out 150ms both fade, 400ms ease-in-out both slide;
}

@keyframes slide {
  from { translate: var(--slide-offset); }
  to { translate: 0; }
}
```

#### Anchor the Header (Don't Slide)

```tsx
<header style={{ viewTransitionName: 'site-header' }}>
  {/* navigation */}
</header>
```

```css
::view-transition-group(site-header) {
  animation: none;
  z-index: 100;
}

::view-transition-old(site-header) {
  display: none;
}

::view-transition-new(site-header) {
  animation: none;
}
```

### 4. Same-route Crossfade

Content swap ภายใน route เดียวกัน (tabs, filters):

```tsx
// app/collection/[slug]/page.tsx
import { Suspense, ViewTransition } from 'react'

export default async function CollectionPage({ params }) {
  const { slug } = await params

  return (
    <Suspense fallback={<CollectionGridSkeleton />}>
      <ViewTransition
        key={slug}
        name="collection-content"
        share="auto"
        enter="auto"
        default="none"
      >
        <CollectionGrid slug={slug} />
      </ViewTransition>
    </Suspense>
  )
}
```

- `key={slug}` change triggers transition
- `share="auto"` + `enter="auto"` = default crossfade
- Tab bar stays fixed, only grid content transitions

### 5. Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(*),
  ::view-transition-new(*),
  ::view-transition-group(*) {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
  }
}
```

## Pattern Summary

| Pattern | Communicates | Trigger |
|---------|-------------|---------|
| Shared element (morph) | "Same thing, going deeper" | Same `name` on both routes |
| Suspense reveal | "Data loaded" | Suspense boundary resolves |
| Directional slide | "Going forward / coming back" | `transitionTypes` on Link |
| Same-route crossfade | "Same place, different content" | `key` change |

## `<ViewTransition>` Props

| Prop | Type | Purpose |
|------|------|---------|
| `name` | string | Identity for shared element matching |
| `share` | string / object | Class for shared element animation |
| `enter` | string / object | Class for enter animation |
| `exit` | string / object | Class for exit animation |
| `default` | string | Default animation (use `"none"` to opt out) |
| `key` | any | Trigger transition on change |

## CSS Pseudo-elements

| Selector | Targets |
|----------|---------|
| `::view-transition-group(.class)` | Container (size, position) |
| `::view-transition-old(.class)` | Outgoing snapshot |
| `::view-transition-new(.class)` | Incoming snapshot |
| `::view-transition-image-pair(.class)` | Old + new pair |

## Quick Reference

| API | Purpose |
|-----|---------|
| `<ViewTransition name="x">` | Shared element identity |
| `<Link transitionTypes={['nav-forward']}>` | Tag navigation direction |
| `router.push(url, { transitionTypes: ['x'] })` | Programmatic with type |
| `viewTransition: true` in next.config | Enable feature |
| `default="none"` | Prevent unrelated animations |

## สรุป

1. **Enable:** `experimental.viewTransition: true` in next.config
2. **Shared morph:** same `name` prop on both routes → auto animate
3. **Suspense reveal:** `exit` on fallback + `enter` on content
4. **Directional:** `transitionTypes` on Link + CSS per direction
5. **Crossfade:** `key` change + `share="auto"` + `enter="auto"`
6. **Anchor elements:** `viewTransitionName` + `animation: none`
7. **Reduced motion:** disable all durations with `@media`
8. **`default="none"`** — prevent animations during unrelated transitions
