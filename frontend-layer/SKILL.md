---
name: frontend-layer
description: Decision rules for organizing React/Next.js code across components/, components/ui/, hooks/, helpers/, types/, and lib/ — enforce strict separation of concerns and prevent business logic from leaking into presentation layers.
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

### 1. `components/ui/` — Shared, Dumb UI Primitives

**What belongs here:**
- Generic, reusable UI building blocks (Button, Input, Dialog, Card, Badge, etc.)
- No business meaning; purely visual and behavioral
- Used across 2+ features
- Typically inspired by `shadcn/ui`, Headless UI, or similar component libraries
- Style variants (color, size, state) driven by props
- No app-specific naming (not `OrderButton` — just `Button`)
- No form validation, no data transformation, no business rules

**What must NEVER be here:**
- API calls or data fetching
- Business logic (discount calculations, order filtering, role-based visibility)
- Feature-specific types or constants
- Knowledge of routes, auth state, or app-specific concepts
- Inline `useState` tied to business state (local UI state like "isOpen" is OK)
- Direct imports from `lib/`, `helpers/`, or `hooks/` that carry domain logic

**Example: Button (✅ CORRECT)**
```tsx
// components/ui/button.tsx
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
}

export function Button({ variant = 'primary', size = 'md', isLoading, ...props }: ButtonProps) {
  return (
    <button
      className={cn('px-4 py-2 rounded', {
        'bg-blue-600 text-white': variant === 'primary',
        'bg-gray-200 text-gray-800': variant === 'secondary',
        'opacity-50 cursor-not-allowed': isLoading,
      })}
      disabled={isLoading}
      {...props}
    />
  )
}
```

**Example: SubmitOrder Button (❌ WRONG — belongs in `components/<feature>/`)**
```tsx
// ❌ NOT in components/ui/ — this has business logic
function SubmitOrderButton({ orderId }: { orderId: string }) {
  const { submitOrder } = useOrderSubmission(orderId)  // business logic hook
  const { isAuthorized } = useAuthPermissions()        // role-based visibility
  
  if (!isAuthorized('SUBMIT_ORDER')) return null       // business rule
  
  return <Button onClick={submitOrder}>Submit</Button>
}
// This belongs in components/orders/ instead
```

---

### 2. `components/<feature>/` — Feature-Specific Presentation Components

**What belongs here:**
- Page/feature layout and composition (OrderDetail, CustomerList, CheckoutForm, etc.)
- Feature-specific UI that ties multiple primitives and hooks together
- Receives data via props and callbacks
- Calls custom hooks to manage feature state/effects
- Renders JSX, passes props down to UI primitives
- Feature-specific constants (column configs, form schemas, etc.)

**What must NEVER be here:**
- Direct `fetch()`, `axios.get()`, or raw API calls (delegate to hooks or lib/api)
- Parsing, validation, or calculation logic that could be unit-tested independently (move to helpers/ or lib/)
- Types used only in one file (keep local); types shared across 2+ files go to types/
- Server-only utilities (those belong in lib/)
- Routes or navigation logic (keep in app/layout.tsx or app/pages.tsx)

**Example: OrderDetail (✅ CORRECT)**
```tsx
// components/orders/OrderDetail.tsx
import { useState, useEffect } from 'react'
import { useOrder } from '@/hooks/useOrder'          // State orchestration
import { formatCurrency } from '@/helpers/currency'  // Pure utility
import { Order } from '@/types/order'                 // Shared type
import { Button } from '@/components/ui/button'      // Primitive
import { OrderItemList } from './OrderItemList'      // Feature component

export interface OrderDetailProps {
  orderId: string
}

export function OrderDetail({ orderId }: OrderDetailProps) {
  const { order, isLoading, error } = useOrder(orderId)  // hook handles fetching + state
  const [isPrinting, setIsPrinting] = useState(false)
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!order) return <div>Not found</div>
  
  const handlePrint = async () => {
    setIsPrinting(true)
    try {
      await window.print()  // browser API OK here
    } finally {
      setIsPrinting(false)
    }
  }
  
  return (
    <div>
      <h1>{order.number}</h1>
      <p>Total: {formatCurrency(order.total)}</p>  {/* helper, not inline calc */}
      <OrderItemList items={order.items} />         {/* feature sub-component */}
      <Button onClick={handlePrint} disabled={isPrinting}>
        Print
      </Button>
    </div>
  )
}
```

**Example: OrderDetail with Inline Logic (❌ WRONG)**
```tsx
// ❌ DO NOT DO THIS
function OrderDetail({ orderId }: { orderId: string }) {
  // ❌ Direct API call — should be in hook
  const [order, setOrder] = useState(null)
  useEffect(() => {
    fetch(`/api/orders/${orderId}`)  // ❌ WRONG
      .then(r => r.json())
      .then(setOrder)
  }, [orderId])
  
  // ❌ Calculation inline — should be helper
  const discountedTotal = order.total * (1 - order.discount / 100)  // ❌ WRONG
  
  return <div>Total: {discountedTotal}</div>
}
```

---

### 3. `hooks/` — Client-Side State Orchestration

**What belongs here:**
- Custom React hooks that manage state, effects, or subscriptions
- Calling lib/ functions (API adapters, auth, formatters) and exposing results to components
- Managing component lifecycle concerns (fetch-on-mount, cleanup, re-fetch on dependency change)
- Subscribing to external data sources (WebSocket, event bus, form library)
- Returning both state and callbacks for components to use
- Testing: these should be unit-testable with `react-hooks` testing library

**What must NEVER be here:**
- `fetch()` or `axios()` calls inline; always delegate to lib/adapters
- JSX or React.ReactNode (these are hooks, not components)
- Raw, untransformed backend responses (normalize in lib/ first, then return clean data)
- Server-only code or environment variables forbidden on the client
- Business logic that has no React dependency (move to helpers/ instead)

**Example: useOrder (✅ CORRECT)**
```tsx
// hooks/useOrder.ts
import { useState, useEffect } from 'react'
import { fetchOrder } from '@/lib/api/orders'  // Delegate to lib
import { normalizeOrder } from '@/lib/normalizers/order'
import { Order } from '@/types/order'

interface UseOrderResult {
  order: Order | null
  isLoading: boolean
  error: Error | null
}

export function useOrder(orderId: string): UseOrderResult {
  const [order, setOrder] = useState<Order | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  
  useEffect(() => {
    let isMounted = true
    
    ;(async () => {
      try {
        const raw = await fetchOrder(orderId)  // Call lib, not fetch()
        if (isMounted) {
          setOrder(normalizeOrder(raw))  // Normalize in lib, not here
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err : new Error('Unknown error'))
        }
      } finally {
        if (isMounted) setIsLoading(false)
      }
    })()
    
    return () => {
      isMounted = false
    }
  }, [orderId])
  
  return { order, isLoading, error }
}
```

**Example: Hook with Inline Fetch (❌ WRONG)**
```tsx
// ❌ DO NOT DO THIS
function useOrder(orderId: string) {
  const [order, setOrder] = useState(null)
  
  useEffect(() => {
    // ❌ WRONG — fetch inline, should be delegated to lib/
    fetch(`/api/orders/${orderId}`)
      .then(r => r.json())
      .then(setOrder)
  }, [orderId])
  
  return order
}
```

---

### 4. `helpers/` — Pure, Framework-Free Functions

**What belongs here:**
- Parsing, formatting, validation, calculation functions with zero framework dependency
- Pure functions (same input always produces same output, no side effects)
- Math, string manipulation, date/time formatting, enum lookups, etc.
- Business logic that can be unit-tested with plain `assert` statements
- Used by components, hooks, lib, tests without any special mocking
- Examples: `formatCurrency()`, `parseISO8601()`, `calculateDiscount()`, `validateEmail()`, `groupByCustomer()`

**What must NEVER be here:**
- React imports or JSX
- Hooks (custom or built-in)
- `fetch`, `axios`, or any network calls
- Browser APIs (DOM manipulation, `window`, `localStorage`, etc.) — those belong in lib or hooks
- Imports from `components/` or `hooks/`
- Environment variables (those belong in lib config)

**Example: helpers/currency.ts (✅ CORRECT)**
```tsx
// helpers/currency.ts — Pure functions, no dependencies except built-ins
export function formatCurrency(amount: number, locale: string = 'en-US'): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

export function parseCurrency(text: string): number {
  // Remove common currency symbols and parse
  const cleaned = text.replace(/[$,]/g, '')
  const num = parseFloat(cleaned)
  return isNaN(num) ? 0 : num
}

export function calculateDiscount(basePrice: number, discountPercent: number): number {
  if (discountPercent < 0 || discountPercent > 100) {
    throw new Error('Discount must be 0-100')
  }
  return basePrice * (1 - discountPercent / 100)
}

export function groupByCustomer(orders: Order[]) {
  return orders.reduce((acc, order) => {
    const customerId = order.customerId
    if (!acc[customerId]) acc[customerId] = []
    acc[customerId].push(order)
    return acc
  }, {} as Record<string, Order[]>)
}
```

**Example: Helper Using fetch (❌ WRONG)**
```tsx
// ❌ DO NOT DO THIS
export function getOrderPrice(orderId: string): Promise<number> {
  // ❌ WRONG — network call, should be in lib/api/
  return fetch(`/api/orders/${orderId}`)
    .then(r => r.json())
    .then(data => data.price)
}
```

---

### 5. `types/` — Shared TypeScript Types

**What belongs here:**
- Interfaces and types used across 2 or more files
- Domain entities (Order, Customer, Product, etc.)
- API request/response contract types (careful: map to domain types before exposing to components)
- Enums for shared constants (OrderStatus, UserRole, etc.)
- Union types, branded types, utility types

**What must NEVER be here:**
- Runtime values or code (interfaces only)
- Types used in exactly one file (keep local to that file)
- Server-only types in client code
- Business logic or helper functions
- React-specific types (ReactNode, ReactElement) unless defining a component library interface

**Example: types/order.ts (✅ CORRECT)**
```tsx
// types/order.ts — Pure types, no runtime values
export interface Order {
  id: string
  number: string
  customerId: string
  status: OrderStatus
  items: OrderItem[]
  total: number
  createdAt: Date
  updatedAt: Date
}

export interface OrderItem {
  id: string
  productId: string
  quantity: number
  unitPrice: number
  discount: number
}

export enum OrderStatus {
  Draft = 'DRAFT',
  Submitted = 'SUBMITTED',
  Confirmed = 'CONFIRMED',
  Shipped = 'SHIPPED',
  Delivered = 'DELIVERED',
  Cancelled = 'CANCELLED',
}

export type OrderFilter = {
  status?: OrderStatus
  customerId?: string
  dateFrom?: Date
  dateTo?: Date
}
```

**Example: Type Only Used In One File (❌ WRONG PLACE)**
```tsx
// ❌ DO NOT in types/ if only used here
// This should be local to the component:

// components/orders/OrderForm.tsx
interface OrderFormData {
  items: { productId: string; quantity: number }[]
}

export function OrderForm() {
  const [data, setData] = useState<OrderFormData>({ items: [] })
  // ...
}
```

---

### 6. `lib/` — Business Rules, API Clients, and Adapters

**What belongs here:**
- API client functions (e.g., `fetchOrder()`, `submitOrder()`, `deleteCustomer()`)
- Adapter pattern for mock vs. real backends
- Business rules and normalization (e.g., mapping API responses to domain types)
- Auth configuration and client setup
- Server-only utilities (should use `'use server'` or be in server-only modules)
- Configuration loaders, environment variable access
- External service clients (Stripe, SendGrid, etc.)
- Data transformation and normalization functions that depend on types/structure

**What must NEVER be here:**
- React components (those are in components/)
- Hooks or JSX
- Direct imports from `components/` (would create dependency inversion)
- Dumb helper functions that have no business meaning (those belong in helpers/)

**Example: lib/api/orders.ts (✅ CORRECT)**
```tsx
// lib/api/orders.ts — API client
import { Order, OrderFilter } from '@/types/order'
import { apiFetch } from '@/lib/api/client'

// Real adapter delegates to backend
export async function fetchOrder(orderId: string): Promise<Order> {
  const response = await apiFetch(`/orders/${orderId}`)
  return normalizeOrderResponse(response)
}

export async function searchOrders(filter: OrderFilter): Promise<Order[]> {
  const response = await apiFetch('/orders/search', {
    method: 'POST',
    body: JSON.stringify(filter),
  })
  return response.data.map(normalizeOrderResponse)
}

export async function submitOrder(orderId: string): Promise<Order> {
  const response = await apiFetch(`/orders/${orderId}/submit`, {
    method: 'POST',
  })
  return normalizeOrderResponse(response)
}

// Normalization: map raw API response to domain type
function normalizeOrderResponse(raw: any): Order {
  return {
    id: raw.id,
    number: raw.order_number,  // API uses snake_case
    customerId: raw.customer_id,
    status: raw.status as OrderStatus,
    items: raw.items.map((item: any) => ({
      id: item.id,
      productId: item.product_id,
      quantity: item.quantity,
      unitPrice: item.unit_price,
      discount: item.discount_pct,
    })),
    total: raw.total_amount,
    createdAt: new Date(raw.created_at),
    updatedAt: new Date(raw.updated_at),
  }
}
```

**Example: lib/api/adapters/orders.mock.ts (✅ CORRECT — Mock Pattern)**
```tsx
// lib/api/adapters/orders.mock.ts — Mock adapter, must match real adapter behavior
import { Order, OrderFilter, OrderStatus } from '@/types/order'

const MOCK_ORDERS: Order[] = [
  {
    id: '1',
    number: 'ORD-001',
    customerId: 'cust-1',
    status: OrderStatus.Submitted,
    items: [
      { id: 'item-1', productId: 'prod-1', quantity: 5, unitPrice: 100, discount: 10 },
    ],
    total: 450,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-02'),
  },
]

export async function fetchOrder(orderId: string): Promise<Order> {
  const order = MOCK_ORDERS.find(o => o.id === orderId)
  if (!order) throw new Error(`Order not found: ${orderId}`)
  return order
}

export async function searchOrders(filter: OrderFilter): Promise<Order[]> {
  let results = MOCK_ORDERS
  
  if (filter.status) {
    results = results.filter(o => o.status === filter.status)
  }
  if (filter.customerId) {
    results = results.filter(o => o.customerId === filter.customerId)
  }
  // IMPORTANT: Mock must match real adapter's filtering/pagination behavior
  
  return results
}
```

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
