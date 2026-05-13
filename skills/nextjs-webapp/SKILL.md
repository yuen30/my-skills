---
name: nextjs-webapp
description: "TOA E-Ordering webapp conventions — directory layout, component patterns, import aliases, route structure, mock data strategy. Use when building or modifying pages, components, or understanding project layout."
---

# TOA E-Ordering Webapp Conventions

## 1. Directory Structure

```
webapp/
├── app/
│   ├── [locale]/             # Pages under locale prefix (th/en/vi)
│   │   ├── admin/            # Admin pages
│   │   ├── cart/
│   │   ├── checkout/
│   │   ├── login/
│   │   ├── orders/
│   │   ├── products/
│   │   ├── profile/
│   │   ├── tracking/
│   │   └── page.tsx          # Dashboard/home
│   └── api/                  # API routes (no locale prefix)
│       ├── auth/[...nextauth]/
│       ├── cart/
│       ├── mock/
│       └── profile/
├── components/               # React components (grouped by feature)
├── types/                    # Shared TypeScript type definitions
├── helpers/                  # Pure utility functions
├── hooks/                    # Custom React hooks
├── lib/                      # Shared logic (api, auth, mock, stores)
├── i18n/                     # next-intl configuration
│   ├── routing.ts            # Locale routing config (locales, default)
│   ├── request.ts            # Request-time i18n setup (load messages)
│   └── navigation.ts         # Typed navigation helpers (Link, redirect, usePathname, useRouter)
├── messages/                 # Translation JSON files
│   ├── th.json               # Thai translations
│   ├── en.json               # English translations
│   └── vi.json               # Vietnamese translations
├── public/
│   ├── mockdata/             # Static JSON mock files + CSV imports
│   └── assets/ banners/ products/ promotions/
├── tests/e2e/                # Playwright E2E tests
├── auth.ts                   # NextAuth.js configuration
├── proxy.ts                  # Middleware: next-intl locale routing + next-auth auth guard
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
| `@/i18n/routing` | `webapp/i18n/routing.ts` |
| `@/i18n/navigation` | `webapp/i18n/navigation.ts` |

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

### Page Routes (all under `[locale]`)

| Route | File | Type |
|-------|------|------|
| `/th` (or `/en`, `/vi`) | `app/[locale]/page.tsx` | Dashboard/home |
| `/th/cart` | `app/[locale]/cart/page.tsx` | Client |
| `/th/checkout` | `app/[locale]/checkout/page.tsx` | Mixed |
| `/th/login` | `app/[locale]/login/page.tsx` | Mixed |
| `/th/orders` | `app/[locale]/orders/page.tsx` | Server → Client |
| `/th/orders/[orderId]` | `app/[locale]/orders/[orderId]/page.tsx` | Server |
| `/th/orders/[orderId]/print` | `app/[locale]/orders/[orderId]/print/page.tsx` | Server |
| `/th/orders/purchase-report` | `app/[locale]/orders/purchase-report/page.tsx` | Client |
| `/th/orders/thank-you/[orderId]` | `app/[locale]/orders/thank-you/[orderId]/page.tsx` | Client |
| `/th/products` | `app/[locale]/products/page.tsx` | TBD |
| `/th/products/[sku]` | `app/[locale]/products/[sku]/page.tsx` | TBD |
| `/th/profile` | `app/[locale]/profile/page.tsx` | Client |
| `/th/tracking` | `app/[locale]/tracking/page.tsx` | TBD |
| `/th/admin/*` | `app/[locale]/admin/*/page.tsx` | Admin pages |

### API Routes (no locale prefix)

| Endpoint | File | Type |
|----------|------|------|
| `/api/auth/[...nextauth]` | `api/auth/[...nextauth]/route.ts` | NextAuth handler |
| `/api/cart` | `api/cart/route.ts` | Cart operations |
| `/api/mock/*` | `api/mock/*/route.ts` | Mock data endpoints |
| `/api/profile/*` | `api/profile/*/route.ts` | Profile CRUD |

### Key Route Patterns

- **Locale prefix required**: All user-facing routes expect prefix (`/th`, `/en`, `/vi`) — no fallback. All pages live under `app/[locale]/`.
- **Param pattern**: Dynamic routes use `[param]` convention (e.g., `[orderId]`)
- **Server components first**: Pages start as server components, add `"use client"` only when needed
- **Auth guard**: Handled centrally in `proxy.ts` (Edge middleware), not per-page

## 5. Internationalization (i18n)

### Setup

Uses `next-intl` v4 with App Router integration:

| File | Purpose |
|------|---------|
| `i18n/routing.ts` | Defines `locales`, `localePrefix: "always"`, default locale |
| `i18n/request.ts` | Loads messages from `messages/{locale}.json` at request time |
| `i18n/navigation.ts` | Re-exports `createNavigation` with typed `Link`, `redirect`, `usePathname`, `useRouter` |

### Usage in Pages

```tsx
import { useTranslations } from "next-intl"
import { Link } from "@/i18n/navigation"

export default function Page() {
  const t = useTranslations("common")
  return <Link href="/orders">{t("viewOrders")}</Link>
}
```

### Translation Files

Located in `messages/`:
- `th.json` — Thai (primary)
- `en.json` — English
- `vi.json` — Vietnamese

Namespaces: `common`, `auth`, `nav`, `dashboard`, `orders`, `products`, `admin`, `promotions`, `profile`, `tracking`, `cart`, `audit`

### Locale Switcher

`components/locale-switcher.tsx` — dropdown in admin header using `<Select>` with `useRouter` + `usePathname` from `@/i18n/navigation`.

### Root Layout

- `app/layout.tsx` — minimal: just `<html>` + `<body>`
- `app/[locale]/layout.tsx` — wraps with `NextIntlClientProvider`, `AuthProvider`, `CustomerProvider`, `Toaster`

## 6. Middleware (proxy.ts)

`proxy.ts` serves as Edge Middleware combining:

1. **Locale routing** — uses `createMiddleware` from `next-intl/middleware` to detect/redirect locale
2. **Auth guard** — uses `getToken` from `next-auth/jwt` (NOT `auth()` wrapper, which imports `node:fs/promises` and breaks Edge Runtime):
   - Unauthenticated users → redirect to `/th/login`
   - Non-admin users accessing `/admin/*` → redirect to `/th`

Key: The function is named `proxy` (not `middleware`) per Next.js 16 convention (file named `proxy.ts`, not `middleware.ts`).

```ts
// proxy.ts — simplified structure
import { getToken } from "next-auth/jwt"
import createMiddleware from "next-intl/middleware"
import { NextRequest, NextResponse } from "next/server"

const intlMiddleware = createMiddleware({ /* routing config */ })

export default async function proxy(req: NextRequest) {
  // 1. Run intl middleware
  // 2. Check auth via getToken()
  // 3. Redirect if needed
}
```

## 7. Mock Data Strategy

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

## 8. Key Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Next.js | 16.x | Framework (turbopack dev, webpack build) |
| React | 19.x | UI library (compiler enabled) |
| next-auth | 5.x | Authentication |
| next-intl | 4.x | Internationalization (i18n) |
| motion | 12.x | Animations |
| lucide-react | 1.x | Icons |
| sonner | 2.x | Toast notifications |
| tailwind-merge + clsx | — | Class merging (`cn()`) |
| Zustand | — | State management (profile store) |
| Playwright | — | E2E tests |

## 9. Dev Commands

```bash
bun run dev          # :3000 (--turbopack)
bun run build        # :3000 (--webpack)*
bun run lint         # ESLint
bun run tsc --noEmit # TypeScript check
bun run test:e2e     # Playwright tests
```

*Build uses `--webpack` due to Turbopack module resolution issues with `@/*` aliases.

## 10. Critical Quirks

- **React Compiler enabled**: Functions passed to `children`/`footer` props MUST be wrapped in `useMemo` to avoid stale closures
- **`.env` escape**: `$` → `$$` (e.g., `SFTP_PASSWORD=$ecret` → `SFTP_PASSWORD=$$ecret`)
- **Locale required**: All user routes need prefix (`/th`, `/en`, `/vi`) — no fallback. Pages live under `app/[locale]/`, not `app/`.
- **postgresql external**: NOT in docker-compose.yml; configure `POSTGRES_HOST` in `.env`
- **`bun run typecheck` NOT available**: Use `tsc --noEmit` directly
- **Middleware in `proxy.ts`**: Function named `proxy` (not `middleware`). Uses `getToken` from `next-auth/jwt` (not `auth()`) to avoid Node.js native imports in Edge runtime.
- **`next-intl/navigation` instead of `next/link`**: Use `Link`, `redirect`, `useRouter`, `usePathname` from `@/i18n/navigation` for locale-aware navigation.
