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
