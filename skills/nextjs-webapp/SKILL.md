---
name: nextjs-webapp
description: "TOA E-Ordering webapp conventions — directory layout, component patterns, import aliases, route structure, mock data strategy. Use when building or modifying pages, components, or understanding project layout."
---

# TOA E-Ordering Webapp Conventions

## 1. Directory Structure

```
webapp/
├── app/                    # Next.js 16 App Router (pages + API)
├── components/             # React components (grouped by feature)
├── types/                  # Shared TypeScript type definitions
├── helpers/                # Pure utility functions
├── hooks/                  # Custom React hooks
├── lib/                    # Shared logic (api, auth, mock, stores)
├── public/
│   ├── mockdata/           # Static JSON mock files + CSV imports
│   └── assets/ banners/ products/ promotions/
├── tests/e2e/              # Playwright E2E tests
├── auth.ts                 # NextAuth.js configuration
├── proxy.ts                # Development proxy
├── next.config.ts
├── tsconfig.json
├── eslint.config.mjs
└── Dockerfile
```

## 2. Import Path Convention

Single alias `@/*` → `webapp/*` (defined in `tsconfig.json`):

| Import | Resolves to |
|--------|------------|
| `@/types/orders` | `webapp/types/orders.ts` |
| `@/helpers/utils` | `webapp/helpers/utils.ts` |
| `@/hooks/use-cart` | `webapp/hooks/use-cart.ts` |
| `@/components/ui/button` | `webapp/components/ui/button.tsx` |
| `@/lib/api/client` | `webapp/lib/api/client.ts` |
| `@/app/layout` | `webapp/app/layout.tsx` |

## 3. Component Architecture

### File Naming Conventions

| Suffix | Role | Example |
|--------|------|---------|
| (none) | Wiring: calls hook → passes props into view | `orders-list.tsx` |
| `.view.tsx` | UI view: pure JSX, receives ready-to-render props | `orders-list.view.tsx` |
| `use-*.ts` | Custom hook: state, effects, callbacks | `use-orders-list.ts` |
| `.constants.ts` | Component-scoped constants | `orders.constants.ts` |

### Where Files Live

| Directory | Contents | Import via |
|-----------|----------|------------|
| `types/*.ts` | All type/interface/union declarations | `@/types/<feature>` |
| `helpers/*.ts` | Pure functions (no React dependency) | `@/helpers/<feature>` |
| `hooks/use-*.ts` | Custom React hooks | `@/hooks/use-<feature>` |
| `components/<feature>/` | Component files (wiring, views, sub-components) | `@/components/<feature>/...` |

### Separation Pattern

1. **Types** → `types/<feature>.ts` — all interfaces, types, unions for the feature
2. **Helpers** → `helpers/<feature>.ts` — pure functions: format, map, filter, sort
3. **Hooks** → `hooks/use-<feature>.ts` — state management, effects, callbacks
4. **View** → `<feature>.view.tsx` — JSX only, receives props + emits events
5. **Wiring** → `<feature>.tsx` — minimal file: calls hook → renders view with context

### UI Primitives

All Radix-based, located in `components/ui/`:
`button`, `badge`, `card`, `dialog`, `drawer`, `input`, `label`, `select`, `table`, `breadcrumb`, `hover-card`, `skeleton`, `sonner`, `customer-dropdown`

Import: `import { Button } from "@/components/ui/button"`

## 4. Route Structure

### Page Routes

| Route | File | Type |
|-------|------|------|
| `/` | `app/page.tsx` | Dashboard/home |
| `/cart` | `app/cart/page.tsx` | Client |
| `/checkout` | `app/checkout/page.tsx` | Mixed |
| `/login` | `app/login/page.tsx` | Mixed |
| `/orders` | `app/orders/page.tsx` | Server → Client |
| `/orders/[orderId]` | `app/orders/[orderId]/page.tsx` | Server |
| `/orders/[orderId]/print` | `app/orders/[orderId]/print/page.tsx` | Server |
| `/orders/purchase-report` | `app/orders/purchase-report/page.tsx` | Client |
| `/orders/thank-you/[orderId]` | `app/orders/thank-you/[orderId]/page.tsx` | Client |
| `/products` | `app/products/page.tsx` | TBD |
| `/products/[sku]` | `app/products/[sku]/page.tsx` | TBD |
| `/profile` | `app/profile/page.tsx` | Client |
| `/tracking` | `app/tracking/page.tsx` | TBD |
| `/admin/*` | `app/admin/*/page.tsx` | Admin pages |

### API Routes

| Endpoint | File | Type |
|----------|------|------|
| `/api/auth/[...nextauth]` | `api/auth/[...nextauth]/route.ts` | NextAuth handler |
| `/api/cart` | `api/cart/route.ts` | Cart operations |
| `/api/mock/*` | `api/mock/*/route.ts` | Mock data endpoints |
| `/api/profile/*` | `api/profile/*/route.ts` | Profile CRUD |

### Key Route Patterns

- **Locale prefix required**: All user-facing routes expect prefix (`/th`, `/en`, `/vi`) — no fallback
- **Param pattern**: Dynamic routes use `[param]` convention (e.g., `[orderId]`)
- **Server components first**: Pages start as server components, add `"use client"` only when needed
- **Auth guard**: Most pages check `auth()` and `redirect()` unauthenticated users

## 5. Mock Data Strategy

Two parallel systems:

### Static JSON (public/mockdata/)

23 JSON files served as static assets. Loaded via:
- **Server**: `readFile(path.join(process.cwd(), "public/mockdata/..."))`
- **Client**: `fetch("/mockdata/...")`

### Mock API Routes (app/api/mock/)

REST endpoints under `/api/mock/` that simulate backend:
- `orders`, `pricing`, `rdd`, `notifications`, `customer-master`, `customer-products`, `promotions-structured`, `sales-performance`

### Mock Adapters (lib/api/adapters/mock/)

Strategy pattern for data access:
- `lib/api/adapters/mock/auth.ts`, `customers.ts`, `orders.ts`, `products.ts`, `promotions.ts`
- Called via `lib/api/client.ts`

## 6. Key Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 16.x | Framework (turbopack dev, webpack build) |
| React | 19.x | UI library (compiler enabled) |
| next-auth | 5.x | Authentication |
| motion | 12.x | Animations |
| lucide-react | 1.x | Icons |
| sonner | 2.x | Toast notifications |
| tailwind-merge + clsx | — | Class merging (`cn()`) |
| Zustand | — | State management (profile store) |
| Playwright | — | E2E tests |

## 7. Dev Commands

```bash
bun run dev          # :3000 (--turbopack)
bun run build        # :3000 (--webpack)*
bun run lint         # ESLint
bun run tsc --noEmit # TypeScript check
bun run test:e2e     # Playwright tests
```

*Build uses `--webpack` due to Turbopack module resolution issues with `@/*` aliases.

## 8. Critical Quirks

- **React Compiler enabled**: Functions passed to `children`/`footer` props MUST be wrapped in `useMemo` to avoid stale closures
- **`.env` escape**: `$` → `$$` (e.g., `SFTP_PASSWORD=$ecret` → `SFTP_PASSWORD=$$ecret`)
- **Locale required**: All user routes need prefix (`/th`, `/en`, `/vi`) — no fallback
- **PostgreSQL external**: NOT in docker-compose.yml; configure `POSTGRES_HOST` in `.env`
- **`bun run typecheck` NOT available**: Use `tsc --noEmit` directly
