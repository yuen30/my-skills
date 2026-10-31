## Refactor Recipe: Breaking Apart a Fat Component

**Size threshold (soft, not a hard block):** once a component file exceeds ~150-200 lines, treat it as a signal to look for extraction candidates using the recipe below, rather than continuing to grow it.

**Scenario:** You have a component doing too much — rendering, fetching, calculating, and managing complex state.

**Step-by-step extraction order:**

### Step 1: Extract Pure Calculations to `helpers/`

Find any logic that doesn't depend on React, the DOM, or state changes. Move it to a pure helper.

```tsx
// Before
function OrderDetail({ order }) {
  const discountedTotal = order.total * (1 - order.discountPercent / 100)
  const formattedTotal = `$${discountedTotal.toFixed(2)}`
  return <p>{formattedTotal}</p>
}

// After
// helpers/order.ts
export function calculateDiscountedTotal(total: number, discountPercent: number) {
  return total * (1 - discountPercent / 100)
}

// components/orders/OrderDetail.tsx
import { calculateDiscountedTotal } from '@/helpers/order'
import { formatCurrency } from '@/helpers/currency'

function OrderDetail({ order }) {
  const discountedTotal = calculateDiscountedTotal(order.total, order.discountPercent)
  return <p>{formatCurrency(discountedTotal)}</p>
}
```

### Step 2: Extract State & Effects to `hooks/`

Move any `useState`, `useEffect`, or state orchestration into a custom hook.

```tsx
// Before
function OrderDetail({ orderId }) {
  const [order, setOrder] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    fetch(`/api/orders/${orderId}`)
      .then(r => r.json())
      .then(setOrder)
      .catch(setError)
      .finally(() => setIsLoading(false))
  }, [orderId])
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return <div>{order.number}</div>
}

// After
// hooks/useOrder.ts
export function useOrder(orderId: string) {
  const [order, setOrder] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    ;(async () => {
      try {
        const data = await fetchOrder(orderId)
        setOrder(data)
      } catch (err) {
        setError(err)
      } finally {
        setIsLoading(false)
      }
    })()
  }, [orderId])
  
  return { order, isLoading, error }
}

// components/orders/OrderDetail.tsx
function OrderDetail({ orderId }) {
  const { order, isLoading, error } = useOrder(orderId)
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return <div>{order.number}</div>
}
```

### Step 3: Extract API Logic to `lib/`

Move any `fetch()` or external-service calls into lib/api/adapters.

```tsx
// Before (in hook)
useEffect(() => {
  fetch(`/api/orders/${orderId}`)
    .then(r => r.json())
    .then(data => {
      // Normalize: map snake_case API response to camelCase domain types
      setOrder({
        id: data.id,
        number: data.order_number,
        total: data.total_amount,
      })
    })
}, [orderId])

// After
// lib/api/orders.ts
export async function fetchOrder(orderId: string): Promise<Order> {
  const response = await apiFetch(`/orders/${orderId}`)
  return {
    id: response.id,
    number: response.order_number,
    total: response.total_amount,
  }
}

// hooks/useOrder.ts
useEffect(() => {
  ;(async () => {
    const data = await fetchOrder(orderId)
    setOrder(data)
  })()
}, [orderId])
```

### Step 4: Extract Shared Types to `types/`

Identify any types used in 2+ files and move them to types/.

```tsx
// Before (scattered)
// hooks/useOrder.ts
interface Order { id: string; number: string }

// components/orders/OrderDetail.tsx
interface Order { id: string; number: string }

// After
// types/order.ts
export interface Order {
  id: string
  number: string
  total: number
}

// hooks/useOrder.ts
import { Order } from '@/types/order'

// components/orders/OrderDetail.tsx
import { Order } from '@/types/order'
```

### Step 5: Component Is Now Clean

What remains should be **props in, JSX out** — the component's only job is composition and rendering.

```tsx
// Final component: clean, testable, focused
function OrderDetail({ orderId }: { orderId: string }) {
  const { order, isLoading, error } = useOrder(orderId)
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!order) return null
  
  const discountedTotal = calculateDiscountedTotal(order.total, order.discountPercent)
  
  return (
    <div>
      <h1>{order.number}</h1>
      <p>Total: {formatCurrency(discountedTotal)}</p>
      <OrderItemList items={order.items} />
    </div>
  )
}
```

**Benefits of this approach:**
- `calculateDiscountedTotal()` is unit-testable without rendering
- `useOrder()` is testable with `@testing-library/react` and fake adapters
- `fetchOrder()` is testable with mock/real adapter swap
- Component is a thin, readable composition layer

---
