## Adapter Pattern: Mock vs. Real

When backend API, external service, or feature is not yet ready, use **swappable adapters** to unblock frontend development.

### Setup in Next.js Webapp

```typescript
// lib/api/adapters/types.ts (shared interface)
export interface OrderAdapter {
  list(filter?: OrderFilter): Promise<Order[]>;
  getById(id: string): Promise<Order | null>;
  create(data: CreateOrderInput): Promise<Order>;
  update(id: string, data: UpdateOrderInput): Promise<Order>;
  delete(id: string): Promise<void>;
}

// lib/api/adapters/mock.ts (behavior-equivalent)
export const mockAdapter: OrderAdapter = {
  async list(filter?: OrderFilter) {
    // Return hardcoded or in-memory data matching real schema
    return [
      { id: 'order-1', customerId: 'cust-1', total: 100, status: 'pending', ... },
      // ...
    ];
  },
  // ... other methods
};

// lib/api/adapters/real.ts (talks to backend)
export const realAdapter: OrderAdapter = {
  async list(filter?: OrderFilter) {
    const params = new URLSearchParams();
    if (filter?.customerId) params.set('customerId', filter.customerId);
    const res = await apiFetch(`/api/orders?${params}`);
    if (!res.ok) throw new Error(`Orders list failed: ${res.status}`);
    const data = await res.json();
    return data.map(normalizeOrder); // normalize backend shape to shared type
  },
  // ... other methods
};

// lib/api/client.ts (selector)
const dataSource = process.env.NEXT_PUBLIC_API_DATA_SOURCE || 'mock';
export const orderAdapter = dataSource === 'real' ? realAdapter : mockAdapter;
```

### Environment Variable

```bash
# .env.local
NEXT_PUBLIC_API_DATA_SOURCE=mock     # development before backend ready
NEXT_PUBLIC_API_DATA_SOURCE=real     # once backend is deployed

# .env.production
NEXT_PUBLIC_API_DATA_SOURCE=real
```

### Rules for Mock Adapters

✅ **DO:**
- Match the real adapter's response shape, status codes, error messages exactly
- Implement filtering, sorting, pagination with the same logic as real (if applicable)
- Return realistically structured data (use ULIDs, valid dates, etc.)
- Throw errors matching real adapter error handling (timeout, 400, 404, 500, etc.)

❌ **DON'T:**
- Return empty arrays/stubs without behavior
- Skip validation that real adapter would do
- Use hardcoded, unfiltered data when filter is provided
- Ignore pagination parameters

**Test coverage:** When mock and real both exist, run the same test suite against both adapters to ensure behavior equivalence.
