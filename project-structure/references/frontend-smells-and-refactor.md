Read when reviewing React/Next.js code for layering smells, or splitting a fat component (soft threshold ~150-200 lines) into helpers/hooks/lib/types.

# Frontend Smells and Refactor Recipe

## Smells → fix

| # | Smell | Fix |
|---|---|---|
| 1 | Business calculation inline in JSX (`order.total * (1 - pct / 100)`) | Extract to a pure function in `helpers/`, call it from the component |
| 2 | Hook calls raw `fetch()` | Move fetch to `lib/api/`; hook calls that function |
| 3 | Helper imports `useState` / React | It is a hook: move to `hooks/` |
| 4 | `components/ui/` primitive imports a business type (`OrderStatus`) | Keep primitive generic (`Badge`); wrap it in `components/<feature>/OrderStatusBadge` |
| 5 | Same type defined in several files | One definition in `types/<domain>.ts`, import everywhere |
| 6 | Component calls `fetch()` directly | State/effect → hook; API call + normalization → `lib/api/` |
| 7 | Same skeleton/loading markup copy-pasted per feature | One `components/ui/Skeleton` with variant props |
| 8 | API-shape mapping or business rule (`isEditable` from status) inline in a component | Move to `lib/` (e.g. `lib/normalizers/order.ts`), not `helpers/` — it carries domain meaning; never scatter the same rule across components |

Example of #4:

```tsx
// components/ui/Badge.tsx — generic
export function Badge({ children }: { children: React.ReactNode }) {
  return <span className="badge">{children}</span>
}
// components/orders/OrderStatusBadge.tsx — business-aware wrapper
import type { OrderStatus } from '@/types/order'
import { Badge } from '@/components/ui/Badge'
export function OrderStatusBadge({ status }: { status: OrderStatus }) {
  return <Badge>{status}</Badge>
}
```

## Refactor recipe: breaking apart a fat component

Extract in this order:

1. **Pure calculations → `helpers/`.** Anything not depending on React, the DOM, or state (e.g. `calculateDiscountedTotal(total, pct)`, `formatCurrency`).
2. **State and effects → `hooks/`.** Move `useState`/`useEffect` orchestration into `useX()` returning `{ data, isLoading, error }`.
3. **API logic → `lib/`.** Move `fetch()` and response normalization (snake_case → domain shape) into `lib/api/<resource>.ts`; the hook calls it.
4. **Shared types → `types/`.** Any type used in 2+ files moves to `types/<domain>.ts`.
5. **What remains is props in, JSX out.**

```text
Before: components/orders/OrderDetail.tsx  (fetch + normalize + calc + state + JSX)
After:  helpers/order.ts           calculateDiscountedTotal()
        hooks/useOrder.ts          useOrder(orderId) -> { order, isLoading, error }
        lib/api/orders.ts          fetchOrder(orderId): Promise<Order>  (fetch + normalize)
        types/order.ts             Order
        components/orders/OrderDetail.tsx  useOrder + helpers + JSX only
```

Result: helpers are unit-testable without rendering, the hook is testable with fake adapters, the API function is testable via mock/real adapter swap, and the component is a thin composition layer.
