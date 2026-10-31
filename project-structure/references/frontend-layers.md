Read when deciding which React/Next.js layer (`components/ui`, `components/<feature>`, `hooks`, `helpers`, `lib`, `types`) a piece of frontend code belongs to.

# Frontend Layer Rules (React / Next.js)

## Dependency direction

```text
app/ pages/ routes   (thin routing, layout)
        ↓
   components/
        ↓
      hooks/
        ↓
       lib/
        ↓
  helpers/, types/
```

- Lower layers (helpers, types, lib) never import upper layers (components, hooks, app).
- No cycles. Components call hooks, hooks call lib, lib uses helpers and types.

```tsx
// components/orders/OrderDetail.tsx
import { useOrder } from '@/hooks/useOrder'          // component -> hook
import { formatCurrency } from '@/helpers/currency'  // component -> helper
import type { Order } from '@/types/order'           // component -> type
import { Button } from '@/components/ui/button'      // component -> primitive
// hooks/useOrder.ts
import { fetchOrder } from '@/lib/api/orders'        // hook -> lib
// lib/api/orders.ts — never imports hooks/ or components/
```

## Decision flowchart (ask in order)

1. Renders JSX / returns `React.ReactNode`? → `components/` (go to 2), else 3.
2. Generic UI primitive with zero business meaning? → `components/ui/`, else `components/<feature>/`.
3. Manages React state/effects/subscriptions, returns no JSX? → `hooks/`.
4. Makes network calls (fetch, axios, API client)? → `lib/api/`.
5. Holds business rules, normalization, or external-service logic? → `lib/` (or `features/<feature>/` when the project uses feature modules).
6. Pure function, no React/DOM/framework dependency, no domain meaning, testable without mocks? → `helpers/`.
7. Type used in 2+ files? → `types/`. Otherwise keep it local.

## Layer rules

### `components/ui/` — dumb primitives
- Belongs: generic building blocks (Button, Input, Dialog, Card, Badge, Skeleton), prop-driven variants, local UI state like `isOpen`, used across 2+ features, no app-specific naming (`Button`, not `OrderButton`).
- Never: data fetching, business logic (discounts, filtering, role-based visibility), feature types/constants, route/auth knowledge, imports from `lib/`/`helpers/`/`hooks/` that carry domain logic.

### `components/<feature>/` — feature presentation
- Belongs: feature layout/composition (OrderDetail, CheckoutForm), wiring primitives + hooks, receiving data via props/callbacks, feature constants (column configs, form schemas), browser APIs like `window.print()`.
- Never: direct `fetch()`/`axios` (delegate to hooks/lib), independently testable parsing/validation/calculation (move to helpers/lib), server-only utilities, routing logic. Components never call adapters directly.

### `hooks/` — client state orchestration
- Belongs: custom hooks managing state, effects, subscriptions (WebSocket, event bus, form library); calling lib functions and returning state + callbacks.
- Never: inline `fetch()`/`axios` (delegate to `lib/`), JSX, raw untransformed backend responses (normalize in lib first), server-only code or client-forbidden env vars, logic with no React dependency (move to helpers).
- Extract a hook when the logic is reused in 2+ components, or one component combines 2+ pieces of state/effect logic. Below that, keep `useState`/`useEffect` inline.

### `helpers/` — pure functions
- Belongs: parsing, formatting, validation, calculation with zero framework dependency; same input → same output (`formatCurrency`, `parseISO8601`, `validateEmail`, `groupByCustomer`).
- Never: React imports, JSX, hooks, network calls, browser APIs (`window`, `localStorage`, DOM), imports from components/hooks, environment variables.

### `lib/` — API clients, adapters, integrations
- Belongs: API client functions (`fetchOrder`, `submitOrder`), mock/real adapters, normalization of API responses to domain types, business rules with domain meaning, auth config, server-only utilities, config loaders and env access, external service clients (Stripe, SendGrid).
- Never: React components, hooks, JSX, imports from `components/`, generic utilities with no domain meaning (those go to helpers).
- Mock and real adapters must be behavior-equivalent (same filtering, sorting, pagination, error codes, response shape).

### `types/` — shared contracts
- Belongs: types used in 2+ files — domain entities, API contract types (map to domain types before exposing to components), shared enums (OrderStatus, UserRole), unions, branded/utility types, and type guards for those types.
- Never: types used in exactly one file, server-only types in client code, business logic or helper functions, React types unless defining a component-library interface.

## Where types live

- Used in exactly 1 file → keep local, no separate file.
- Used only within one component but cluttering it → colocate as `ComponentName.types.ts` next to `ComponentName.tsx`.
- Used across 2+ files → shared `types/<domain>.ts` (e.g. `types/order.ts`), never duplicated.
- A type in `Component.types.ts` that gains a second consumer moves to `types/`; update both call sites.
- Type predicates (`function isX(value: unknown): value is X`) live in the same file as the type they narrow. Several unrelated guards → `types/guards.ts`.

## Review checklist

- `components/ui/` uses business types or logic? → make generic.
- `components/<feature>/` calls `fetch()` directly? → delegate to hooks/lib.
- `hooks/` renders JSX or calls `fetch()` inline? → call lib/api.
- `helpers/` imports React, hooks, or components? → must be framework-free.
- `types/` entry used in one file only? → make local.
- `lib/` imports components or hooks? → lib must never know about UI.
- Could parsing/formatting/validation be unit-tested without mocking? If not, move it to lib/ or helpers/.

## Common hook recipes

Extract to a hook when state/effect logic is reused in 2+ components, or one component combines 2+ pieces of state/effect logic. Below that, keep `useState`/`useEffect` inline. Extract these on first real need; don't pre-build a library:

- `useDebounce<T>(value: T, delayMs: number): T` — settle a fast-changing value (search input).
- `useLocalStorage<T>(key: string, initialValue: T): [T, (v: T) => void]` — SSR-safe (guard `typeof window`).
- `useMediaQuery(query: string): boolean` — responsive logic in JS.
- `usePrevious<T>(value: T): T | undefined` — ref updated in `useEffect`.
- `useToggle(initial = false): [boolean, () => void]` — stable toggle callback.
- `useIntersectionObserver(ref: RefObject<Element>, options?: IntersectionObserverInit): boolean` — lazy-load, infinite scroll.
- `useClickOutside(ref: RefObject<HTMLElement>, onOutside: () => void): void` — dropdowns, modals.

Shape sketches only — write the minimal version the project needs.
