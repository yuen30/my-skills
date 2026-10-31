---
name: frontend-layer
description: Layer-separation rules for React/Next.js code across components/, components/ui/, hooks/, helpers/, lib/, types/. Use when placing new code, reviewing layering, or splitting a fat component. Not for project scaffolding (see nextjs-clean-code).
---

# Frontend Layer Separation

A reusable decision-rule skill for React/Next.js projects: where does new code belong, and why? Enforces strict separation between presentation, state orchestration, business logic, pure utilities, and type definitions.

## Why Layer Separation Matters

Without clear boundaries:
- Business logic scatters across components, making it untestable without mocking React
- Types duplicate in multiple files, creating sync nightmares
- API calls and state management hide inside JSX, tangling concerns
- Refactoring becomes risky because dependencies are implicit
- Mock vs. real implementations diverge

With clear layers:
- Components focus on render logic (props in, JSX out)
- Hooks handle state/effects orchestration without rendering
- Pure helpers are testable without any framework
- API adapters are swappable (mock/real, old/new endpoints)
- Types are single sources of truth

---

## The Five Layers + Decision Table

Layers: `components/ui/` (dumb primitives), `components/<feature>/` (feature presentation), `hooks/` (state/effect orchestration), `helpers/` (pure functions), `types/` (shared types), `lib/` (business rules, API clients, adapters).

See [references/layers.md](references/layers.md) — read when deciding what a layer may contain, or writing code for a specific layer.

---

## Dependency Direction

```
app/pages/routes (thin routing, layout)
         ↓
    components/
         ↓
       hooks/
         ↓
        lib/
         ↓
     helpers/, types/
```

**Golden Rule:**
- Lower layers (helpers, types, lib) NEVER import from upper layers (components, hooks, app)
- No cycles — if A imports B, then B must not import A
- Components call hooks, hooks call lib, lib uses helpers and types

**Valid imports:**
```tsx
// components/orders/OrderDetail.tsx
import { useOrder } from '@/hooks/useOrder'        // ✅ OK — component calls hook
import { formatCurrency } from '@/helpers/currency' // ✅ OK — component uses helper
import { Order } from '@/types/order'              // ✅ OK — component uses type
import { Button } from '@/components/ui/button'    // ✅ OK — component uses primitive

// hooks/useOrder.ts
import { fetchOrder } from '@/lib/api/orders'      // ✅ OK — hook calls lib
import { Order } from '@/types/order'              // ✅ OK — hook uses type

// lib/api/orders.ts
import { Order } from '@/types/order'              // ✅ OK — lib uses type
import { formatDate } from '@/helpers/date'        // ✅ OK — lib uses helper
// ❌ NEVER import { useOrder } from '@/hooks/useOrder'  — lib cannot import hooks
// ❌ NEVER import { OrderDetail } from '@/components/orders/OrderDetail'  — lib cannot import components
```

---

## Decision Flowchart

Given a new piece of code, ask these questions **in order**:

1. **Does it render JSX or have a React.ReactNode return type?**
   - YES → `components/`
   - NO → Next question

2. **Is it a generic, reusable UI primitive with zero business meaning?**
   - YES → `components/ui/`
   - NO → Next question (back to components/ for feature components)

3. **Does it manage React state, effects, or subscribe to data sources, but returns no JSX?**
   - YES → `hooks/`
   - NO → Next question

4. **Does it make network calls (fetch, axios, API client)?**
   - YES → `lib/` (specifically lib/api/)
   - NO → Next question

5. **Does it hold business rules or external-service logic?**
   - YES → `lib/`
   - NO → Next question

6. **Is it a pure function with zero React/DOM/framework dependency, testable without mocking?**
   - YES → `helpers/`
   - NO → Next question

7. **Is it a TypeScript interface/type used in 2+ places?**
   - YES → `types/`
   - NO → **Keep it local** to the file where it's used

---

## Common Violations & Smells

See [references/violations.md](references/violations.md) — read when reviewing code or diagnosing smells (inline business logic, hook doing fetch, helper importing hooks, ui importing business types, scattered types, direct API calls, duplicate skeletons).

---

## Refactor Recipe: Breaking Apart a Fat Component

See [references/refactor-recipe.md](references/refactor-recipe.md) — read when a component exceeds ~150-200 lines and must be split into helpers/hooks/lib/types.

---

## Review Checklist

When reviewing code, ask:

- [ ] **components/ui/** — Does this use business types or logic? (Should be generic)
- [ ] **components/<feature>/** — Does it call `fetch()` directly? (Should delegate to hooks/lib)
- [ ] **hooks/** — Does it render JSX or call `fetch()` inline? (Should call lib/api instead)
- [ ] **helpers/** — Does it import React, hooks, or components? (Should be pure, framework-free)
- [ ] **types/** — Is this type only used in one file? (Should be local, not in types/)
- [ ] **lib/** — Does it import from components or hooks? (Dependency inversion — lib must never know about UI)
- [ ] **Overall** — Could the same parsing/formatting/validation logic be unit-tested without mocking anything? (If no, move it to lib/ or helpers/)

---

## Common Hook Recipes

**When to extract to a hook:** the state/effect logic is reused in 2+ components, OR a single component combines 2+ pieces of state/effect logic (e.g. a subscription + a derived value + a cleanup) that would otherwise clutter the component body. Below that threshold, keep `useState`/`useEffect` inline.

Senior React/Next.js devs reach for these often — extract on first real need, don't pre-build a library of them:

- **`useDebounce(value, delayMs)`** — delays reflecting a fast-changing value (search input) until it settles. `function useDebounce<T>(value: T, delayMs: number): T`
- **`useLocalStorage(key, initialValue)`** — syncs state with `localStorage`, SSR-safe (guard `typeof window`). `function useLocalStorage<T>(key: string, initialValue: T): [T, (v: T) => void]`
- **`useMediaQuery(query)`** — subscribes to a CSS media query for responsive logic in JS. `function useMediaQuery(query: string): boolean`
- **`usePrevious(value)`** — returns the value from the previous render, via a ref updated in `useEffect`. `function usePrevious<T>(value: T): T | undefined`
- **`useToggle(initial?)`** — boolean state with a stable toggle callback. `function useToggle(initial = false): [boolean, () => void]`
- **`useIntersectionObserver(ref, options?)`** — reports whether an element is in viewport (lazy-load, infinite scroll, animation triggers). `function useIntersectionObserver(ref: RefObject<Element>, options?: IntersectionObserverInit): boolean`
- **`useClickOutside(ref, onOutside)`** — fires a callback when a click/touch happens outside the referenced element (dropdowns, modals). `function useClickOutside(ref: RefObject<HTMLElement>, onOutside: () => void): void`

These are shape sketches, not full implementations — write the minimal version each project actually needs.

---

## Type Guards & Colocated Types Naming

**Type predicates (`isX`):** narrowing functions of the form `function isX(value: unknown): value is X` live next to the type they narrow — same file as the type definition (`types/order.ts` exports both `Order` and `isOrder`). If a component/feature accumulates several unrelated guards, consolidate into `types/guards.ts` rather than scattering them across feature files.

**Naming convention for where types live** (extends the 2+/1 rule above):
- Used in exactly 1 file → keep local, no separate file.
- Used only within one component but the inline definition clutters the component (props + several derived shapes) → colocate as `ComponentName.types.ts` next to `ComponentName.tsx`.
- Used across 2+ files/components → shared `types/domain.ts` (e.g. `types/order.ts`), never duplicated per-file.

Never mix the two: a type that has grown a second consumer must move out of `Component.types.ts` and into the shared `types/` file, updating both call sites to import from the new location.

---

## Cross-Reference

- **For a full Next.js project bootstrap** matching this layering from day one, see the [`new-nextjs`](../new-nextjs/) skill in this same repo.
- **For the Next.js+Go monorepo pairing pattern**, see [`monorepo-scaffold-nextjs-go`](../monorepo-scaffold-nextjs-go/).

Both of these skills assume and build on the layer separation defined here.
