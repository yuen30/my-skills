## Common Violations & Smells

### Smell #1: Business Logic Inline in JSX

```tsx
// ❌ WRONG
function OrderDetail() {
  return (
    <div>
      {/* Discount calculation inline in JSX */}
      <p>Subtotal: ${order.total * (1 - order.discountPercent / 100)}</p>
    </div>
  )
}

// ✅ CORRECT
function OrderDetail() {
  const discountedTotal = calculateDiscount(order.total, order.discountPercent)
  return <p>Subtotal: ${formatCurrency(discountedTotal)}</p>
}
```

**Fix:** Extract to `helpers/` and call from component.

---

### Smell #2: Hook Doing Raw fetch()

```tsx
// ❌ WRONG
function useOrder(orderId: string) {
  const [order, setOrder] = useState(null)
  useEffect(() => {
    fetch(`/api/orders/${orderId}`)  // Raw fetch
      .then(r => r.json())
      .then(setOrder)
  }, [orderId])
  return order
}

// ✅ CORRECT
function useOrder(orderId: string) {
  const [order, setOrder] = useState(null)
  useEffect(() => {
    ;(async () => {
      const data = await fetchOrder(orderId)  // Delegate to lib/api
      setOrder(data)
    })()
  }, [orderId])
  return order
}
```

**Fix:** Move fetch logic to `lib/api/` and have the hook call that function.

---

### Smell #3: Helper Importing React Hooks

```tsx
// ❌ WRONG
// helpers/myHelper.ts
import { useState } from 'react'  // ❌ Should not import React

export function useMyLogic() {
  const [state, setState] = useState(null)  // ❌ This is a hook, not a helper
  return state
}

// ✅ CORRECT
// hooks/useMyLogic.ts
import { useState } from 'react'

export function useMyLogic() {
  const [state, setState] = useState(null)
  return state
}
```

**Fix:** Move to `hooks/` if it needs React state.

---

### Smell #4: components/ui/ Importing Business Types

```tsx
// ❌ WRONG
// components/ui/DiscountBadge.tsx
import { OrderStatus } from '@/types/order'  // ❌ Business type

export function DiscountBadge({ status }: { status: OrderStatus }) {
  return <span>{status}</span>
}

// ✅ CORRECT
// components/ui/Badge.tsx
export function Badge({ children }: { children: React.ReactNode }) {
  return <span className="badge">{children}</span>
}

// components/orders/OrderStatusBadge.tsx
import { OrderStatus } from '@/types/order'
import { Badge } from '@/components/ui/Badge'

export function OrderStatusBadge({ status }: { status: OrderStatus }) {
  return <Badge>{status}</Badge>
}
```

**Fix:** Keep UI primitives truly generic; put business logic in feature components.

---

### Smell #5: Type Definitions Scattered

```tsx
// ❌ WRONG — Defined in multiple places
// components/orders/OrderDetail.tsx
interface Order { id: string; number: string }

// hooks/useOrder.ts
interface Order { id: string; number: string }

// ✅ CORRECT — Single source of truth
// types/order.ts
export interface Order { id: string; number: string }

// components/orders/OrderDetail.tsx
import { Order } from '@/types/order'

// hooks/useOrder.ts
import { Order } from '@/types/order'
```

**Fix:** Move shared types to `types/` and import from there.

---

### Smell #6: Direct API Calls from Components

```tsx
// ❌ WRONG
function CustomerList() {
  const [customers, setCustomers] = useState([])
  
  const loadCustomers = async () => {
    // ❌ Direct API call in component
    const res = await fetch('/api/customers')
    const data = await res.json()
    setCustomers(data)
  }
  
  useEffect(() => loadCustomers(), [])
  return <div>{customers.map(c => <div key={c.id}>{c.name}</div>)}</div>
}

// ✅ CORRECT
function CustomerList() {
  const { customers } = useCustomers()  // Delegate to hook
  return <div>{customers.map(c => <div key={c.id}>{c.name}</div>)}</div>
}

// hooks/useCustomers.ts
export function useCustomers() {
  const [customers, setCustomers] = useState<Customer[]>([])
  
  useEffect(() => {
    ;(async () => {
      const data = await fetchCustomers()  // Delegate to lib/api
      setCustomers(data)
    })()
  }, [])
  
  return { customers }
}

// lib/api/customers.ts
export async function fetchCustomers(): Promise<Customer[]> {
  const response = await apiFetch('/customers')
  return response.data.map(normalizeCustomer)
}
```

**Fix:** Extract state/effect logic to a hook, extract API logic to lib/.

---

### Smell #7: Duplicate Skeleton/Loading Components

```tsx
// ❌ WRONG — same skeleton markup recreated per page/feature
// components/orders/OrderDetailSkeleton.tsx
function OrderDetailSkeleton() {
  return <div className="animate-pulse h-24 rounded bg-gray-200" />
}

// components/customers/CustomerListSkeleton.tsx
function CustomerListSkeleton() {
  return <div className="animate-pulse h-24 rounded bg-gray-200" />  // same markup, copy-pasted
}

// ✅ CORRECT
// components/ui/Skeleton.tsx
export interface SkeletonProps {
  variant?: 'text' | 'card' | 'avatar'
  className?: string
}

export function Skeleton({ variant = 'text', className }: SkeletonProps) {
  return <div className={cn('animate-pulse rounded bg-gray-200', variantClass[variant], className)} />
}

// components/orders/OrderDetail.tsx
import { Skeleton } from '@/components/ui/Skeleton'
if (isLoading) return <Skeleton variant="card" />
```

**Fix:** Keep one shared `<Skeleton />` (or feature-parameterized `<XSkeleton />`) component in `components/ui/`, imported wherever a loading state is needed, and drive variant differences via props instead of copy-pasting markup per feature.

---

### Smell #8: Business Logic Inlined in Component Instead of `lib/`

```tsx
// ❌ WRONG — normalization + business rule scattered inline in the component
function OrderDetail({ rawOrder }) {
  // ❌ Mapping snake_case API shape to domain shape, inline
  const order = {
    id: rawOrder.id,
    number: rawOrder.order_number,
    isEditable: rawOrder.status !== 'SHIPPED' && rawOrder.status !== 'DELIVERED', // ❌ business rule inline
  }

  return <div>{order.number}</div>
}

// ✅ CORRECT
// lib/normalizers/order.ts
export function normalizeOrder(raw: RawOrder): Order {
  return {
    id: raw.id,
    number: raw.order_number,
    isEditable: !['SHIPPED', 'DELIVERED'].includes(raw.status),
  }
}

// components/orders/OrderDetail.tsx
import { normalizeOrder } from '@/lib/normalizers/order'

function OrderDetail({ rawOrder }: { rawOrder: RawOrder }) {
  const order = normalizeOrder(rawOrder)
  return <div>{order.number}</div>
}
```

**Fix:** Move normalization/business-rule code to `lib/` (not `helpers/` — it carries domain meaning, not a pure generic utility) and call it from the component or the hook that feeds the component. Do not scatter the same rule across multiple components.

---
