---
name: new-nextjs
description: Bootstrap a standalone Next.js 16 frontend app with the exact structure, tooling, and conventions used in production—Bun runtime, React 19, TypeScript strict mode, Tailwind CSS v4, shadcn/ui, next-intl i18n, next-auth with Credentials + OAuth, drizzle-orm, Playwright e2e, ESLint no-any-as-error, multi-stage Docker, and organized layer boundaries (app/, components/, lib/, hooks/, helpers/, types/).
---

# new-nextjs

Bootstrap a standalone Next.js 16 frontend app with production-ready structure, tooling, and conventions. This skill covers the exact setup used in real-world projects: Bun package manager, strict TypeScript, Tailwind v4 + shadcn/ui, next-intl i18n, next-auth, drizzle-orm for optional database, Playwright e2e tests, ESLint no-`any`-as-error rule, and organized layer boundaries respecting dependency direction.

**When to use:** Starting a new Next.js project from scratch that will follow a proven structure and avoid common patterns. Not for migrating existing codebases or Next.js+Go monorepos (see `monorepo-scaffold-nextjs-go` for that pairing).

## Runtime & Package Manager

- **Runtime:** Node.js (production) and Bun (local development, CI, Docker)
- **Package manager:** Bun (all scripts use `bun run`, not `npm run`)
  - `bun install` — install dependencies from bun.lock
  - `bun run dev` — start dev server with Turbopack
  - `bun run build` — production build with webpack (NOT turbopack, due to alias resolution)
  - `bun run lint` — check code style via ESLint
  - `bun run typecheck` — verify types with `tsc --noEmit`
  - `bun run test:e2e` — run Playwright e2e tests
- **Why webpack for production build:** The project uses path aliases (`@/*`) that Turbopack doesn't fully support in standalone mode; webpack resolves them correctly. Dev uses Turbopack for speed.

## Core Dependencies & Versions

```
Next.js:           ^16.3.0
React:             ^19.2.8
TypeScript:        ~6
Bun:               (any recent stable; see package.json "scripts")
Tailwind CSS:      ^4
shadcn/ui:         (latest, via radix-ui + tailwindcss)
next-intl:         ^4.13.5
next-auth:         ^5.0.0-beta.30 (note: v5 beta)
drizzle-orm:       ^0.45.2 (optional, for database)
drizzle-kit:       ^0.31.10 (optional, for migrations)
postgres:          ^3.4.9 (optional, if using Drizzle + PostgreSQL)
@playwright/test:  ^1.62.1 (for e2e)
ESLint:            ^9.39.2 (with next/core-web-vitals, typescript configs)
```

**UI & Utility libraries:**
- Radix UI (via shadcn/ui)
- clsx, tailwind-merge (class composition)
- date-fns (date handling)
- lucide-react (icons)
- sonner (toast notifications)

## Full Folder Scaffold

Create these directories and purpose files:

```
project-root/
├── app/                          # Next.js App Router
│   ├── [locale]/                 # Locale-prefixed routes (/:lang/...)
│   │   ├── layout.tsx            # Root layout for locale segment
│   │   ├── page.tsx              # Home page
│   │   └── (feature)/            # Feature route groups (optional)
│   ├── api/                      # Route handlers (authentication, webhooks, etc.)
│   │   ├── auth/                 # next-auth endpoints
│   │   └── health/               # Health checks (e.g., /api/health or GET /healthz)
│   ├── layout.tsx                # Global layout (above locale)
│   └── sitemap.ts                # SEO sitemap
├── components/                   # Reusable UI components
│   ├── ui/                       # Shared primitives: Button, Input, Dialog, etc. (from shadcn/ui)
│   ├── forms/                    # Form components (optional)
│   ├── navigation/               # Header, footer, sidebar (optional)
│   └── [feature]/                # Feature-specific UI (e.g., ProductCard, OrderTable)
├── hooks/                        # Custom React hooks (client state, effects)
│   ├── use-locale.ts             # Next-intl locale access
│   ├── use-auth.ts               # Auth state hook
│   └── [feature-hooks]/          # Feature-specific hooks
├── helpers/                      # Pure utility functions (formatters, validators, etc.)
│   ├── format.ts                 # Date, currency, text formatting
│   ├── validate.ts               # Validation logic
│   └── [domain]/                 # Domain-specific helpers
├── lib/                          # Business logic, API clients, infrastructure
│   ├── api/                      # API client factory and adapters
│   │   ├── client.ts             # HTTP client setup (fetch wrapper, auth headers)
│   │   ├── adapters/             # Toggle between mock and real backends
│   │   │   ├── mock/             # Mock adapter (stub responses for testing/dev)
│   │   │   │   └── [feature].ts  # e.g., mock/orders.ts
│   │   │   └── real/             # Real adapter (calls actual backend API)
│   │   │       └── [feature].ts  # e.g., real/orders.ts
│   │   ├── orders.ts             # Order API facade (exports from selected adapter)
│   │   ├── products.ts           # Product API facade
│   │   ├── customers.ts          # Customer API facade
│   │   └── cart.ts               # Cart API facade
│   ├── auth/                     # Authentication logic (next-auth config, custom hooks)
│   │   ├── customer-login.ts     # Credentials provider login call
│   │   ├── redirect.ts           # Post-auth redirect logic
│   │   └── utils.ts              # Token refresh, validation
│   ├── db/                       # Database layer (Drizzle ORM, migrations)
│   │   ├── client.ts             # Drizzle database instance
│   │   ├── schema/               # Drizzle schemas
│   │   │   └── config.ts         # Config/settings table schema
│   │   ├── migrations/           # Auto-generated Drizzle migrations
│   │   └── seed/                 # Database seed scripts (optional)
│   ├── i18n-paths.ts             # Locale prefix helpers (getLocaleFromPathname, localizePath)
│   ├── security.ts               # CSRF, sanitization, CSP helpers
│   ├── normalization.ts          # Response normalization (backend schema → app schema)
│   └── [domain]/                 # Domain-specific services (profile, checkout, audit, etc.)
├── types/                        # TypeScript type definitions
│   ├── api.ts                    # API request/response types
│   ├── domain.ts                 # Domain entities and value objects
│   ├── auth.ts                   # Auth-related types (User, Session, etc.)
│   └── [feature].ts              # Feature-specific types
├── i18n/                         # next-intl configuration
│   ├── request.ts                # Create i18n instance from request context
│   ├── routing.ts                # Locale list, default locale, routing config
│   └── navigation.ts             # Client-side i18n navigation (Link, useRouter wrapper)
├── messages/                     # Translation JSON files
│   ├── en.json                   # English messages
│   ├── th.json                   # Thai messages
│   └── vi.json                   # Vietnamese messages (add as needed)
├── public/                       # Static assets (images, fonts, favicon)
│   ├── mockdata/                 # Mock JSON data files (languages.json, etc.)
│   └── uploads/                  # User uploads (symlinked in Docker)
├── tests/                        # Test files
│   ├── e2e/                      # Playwright end-to-end tests
│   │   ├── auth.spec.ts          # Authentication flows
│   │   ├── homepage.spec.ts      # Homepage and main flows
│   │   └── [feature].spec.ts     # Feature-specific tests
│   └── unit/                     # Unit tests (if using Jest, Vitest)
├── docs/                         # Project documentation
│   ├── API.md                    # API adapter documentation
│   ├── ARCHITECTURE.md           # Architecture and layer boundaries
│   └── SETUP.md                  # Local setup, environment variables
├── .env.example                  # Example environment variables
├── .env.local                    # Local env vars (git-ignored)
├── .env.production               # Production env vars (vault-managed, not committed)
├── auth.ts                       # next-auth configuration (root level)
├── proxy.ts                      # Middleware for route guards and i18n routing (root level)
├── middleware.ts                 # (Optional) If using separate middleware.ts instead of proxy.ts
├── instrumentation.ts            # Entry point for observability init (empty wrapper)
├── instrumentation-node.ts       # Node.js runtime observability (e.g., OpenTelemetry setup)
├── next.config.ts                # Next.js configuration with webpack alias, plugins
├── tsconfig.json                 # TypeScript strict config, path aliases
├── eslint.config.mjs             # ESLint configuration (no-any, type-imports, etc.)
├── drizzle.config.ts             # Drizzle configuration (schema path, migrations dir)
├── playwright.config.ts          # Playwright e2e test configuration
├── postcss.config.mjs            # PostCSS config for Tailwind
├── package.json                  # Dependencies and scripts
├── bun.lock                       # Bun lockfile (generated)
├── Dockerfile                    # Multi-stage Docker build
├── docker-entrypoint.sh          # Docker entrypoint script
├── .dockerignore                 # Docker build ignore patterns
└── README.md                     # Project overview
```

## Key Config Files

### `next.config.ts`

```typescript
import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";
import path from "path";

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

const nextConfig: NextConfig = {
  output: "standalone",  // Docker-friendly standalone build
  cacheComponents: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": path.resolve(__dirname),
    };
    return config;
  },
  experimental: {
    staleTimes: {
      dynamic: 0,  // No caching for dynamic content
      static: 30,  // 30s stale-time for static on client-side nav
    },
  },
  // Rewrite routes if proxying to a backend API
  rewrites: async () => [
    { source: "/api/auth/:path*", destination: "/api/auth/:path*" },
    { source: "/api/mock/:path*", destination: "/api/mock/:path*" },
    // ... add other internal API routes
    // Then catch-all proxy to backend if NEXT_PUBLIC_API_BASE_URL is set
  ],
};

export default withNextIntl(nextConfig);
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "strict": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### `eslint.config.mjs`

```javascript
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores([".next/**", "out/**", "build/**"]),
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "error",  // KEY: no `any`
      "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/consistent-type-imports": ["warn", { prefer: "type-imports" }],
    },
  },
]);

export default eslintConfig;
```

### `auth.ts` (next-auth skeleton)

```typescript
import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import AzureADProvider from "next-auth/providers/azure-ad";

const authSecret = process.env.AUTH_SECRET ?? 
  (process.env.NODE_ENV === "production" ? undefined : "dev-secret");

export const { handlers, auth, signIn, signOut } = NextAuth({
  secret: authSecret,
  providers: [
    Credentials({
      async authorize(credentials) {
        // Call backend login API with username/password
        // Return user object or null
      },
    }),
    AzureADProvider({
      clientId: process.env.AZURE_CLIENT_ID,
      clientSecret: process.env.AZURE_CLIENT_SECRET,
      tenantId: process.env.AZURE_AD_TENANT_ID ?? "common",
    }),
  ],
  callbacks: {
    jwt({ token, user }) {
      // Store user claims in JWT token
      return token;
    },
    session({ session, token }) {
      // Populate session from token
      return session;
    },
  },
});
```

### `proxy.ts` (middleware for locale routing & auth guards)

```typescript
import { createMiddleware } from "next-intl/middleware";
import { routing } from "@/i18n/routing";
import { getToken } from "next-auth/jwt";

const intlMiddleware = createMiddleware(routing);

export default async function middleware(request) {
  // next-intl routing (handle /:locale prefix)
  const response = intlMiddleware(request);
  
  // Optional: check auth for protected routes
  const token = await getToken({ req: request, secret: process.env.AUTH_SECRET });
  
  // Redirect to login if unauthenticated on protected paths
  const publicPaths = ["/login", "/forgot-password", "/reset-password"];
  const pathWithoutLocale = stripLocale(request.nextUrl.pathname);
  
  if (!token && !publicPaths.includes(pathWithoutLocale)) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  return response;
}

export const config = {
  matcher: ["/((?!api|static|.*\\..*|_next).*)"],
};
```

### `drizzle.config.ts` (optional, if using database)

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "postgresql",
  schema: "./lib/db/schema/*.ts",
  out: "./lib/db/migrations",
  dbCredentials: {
    url: process.env.DATABASE_URL || "...",
  },
  strict: true,
  verbose: true,
});
```

### `Dockerfile` (multi-stage: builder + lean runner)

```dockerfile
# Stage 1: Build
FROM oven/bun:1.3 AS builder

WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
ARG NEXT_PUBLIC_API_DATA_SOURCE=mock
ARG ORDERING_API_BASE_URL
ENV NEXT_PUBLIC_API_DATA_SOURCE=${NEXT_PUBLIC_API_DATA_SOURCE}
ENV ORDERING_API_BASE_URL=${ORDERING_API_BASE_URL}

RUN bun run build

# Stage 2: Runtime (lean alpine)
FROM oven/bun:1.3-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000

RUN apk add --no-cache su-exec
RUN addgroup -S app && adduser -S app -G app

COPY --from=builder --chown=app:app /app/public ./public
COPY --from=builder --chown=app:app /app/.next/standalone ./
COPY --from=builder --chown=app:app /app/.next/static ./.next/static/

EXPOSE 3000
USER app
CMD ["bun", "server.js"]
```

### `playwright.config.ts`

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  retries: 1,
  timeout: 60_000,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://localhost:3000/en",  // Adjust locale as needed
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  webServer: {
    command: "bun run dev",
    url: "http://localhost:3000/login",
    timeout: 120_000,
    reuseExistingServer: true,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
```

## Bootstrap Checklist

Follow these steps to scaffold a new project matching this structure:

1. **Create Next.js project:**
   ```bash
   bun create next-app@latest myapp -- \
     --typescript \
     --tailwind \
     --eslint \
     --no-app-router  # (we'll set up app router manually)
   cd myapp
   ```

2. **Add dependencies:**
   ```bash
   bun add next-intl next-auth drizzle-orm postgres
   bun add -d drizzle-kit @playwright/test
   ```

3. **Create folder structure:** Use the "Full Folder Scaffold" section above. Create empty directories and placeholder files (e.g., `lib/api/adapters/{mock,real}/` with stub exports).

4. **Set up root config files:** Copy/adapt the templates from "Key Config Files" above:
   - `next.config.ts` (with next-intl plugin)
   - `tsconfig.json` (strict mode)
   - `eslint.config.mjs` (no-any rule)
   - `auth.ts` (next-auth skeleton)
   - `proxy.ts` (middleware)
   - `drizzle.config.ts` (if using database)
   - `playwright.config.ts` (e2e tests)

5. **Set up i18n:**
   - Create `i18n/routing.ts` with supported locales and default locale.
   - Create `i18n/request.ts` to initialize next-intl from request.
   - Create `messages/{en,th,vi}.json` with sample translation keys.

6. **Create app structure:**
   - `app/layout.tsx` (global wrapper)
   - `app/[locale]/layout.tsx` (locale-scoped wrapper)
   - `app/[locale]/page.tsx` (home page)
   - `app/api/auth/[...nextauth]/route.ts` (next-auth handlers)

7. **Create sample components:**
   - `components/ui/` — add 2-3 shadcn/ui primitives (Button, Input, etc.) via `bunx shadcn-ui@latest add button`
   - `components/` — create a simple feature component (e.g., ProductCard)

8. **Create sample hooks:**
   - `hooks/use-locale.ts` — hook to access current locale from next-intl
   - `hooks/use-auth.ts` — hook to access auth session

9. **Set up API adapters:**
   - `lib/api/adapters/mock/products.ts` — stub product list response
   - `lib/api/adapters/real/products.ts` — real API call (with apiFetch, auth headers)
   - `lib/api/products.ts` — facade that exports from selected adapter based on `NEXT_PUBLIC_API_DATA_SOURCE` env var

10. **Verify configuration:**
    ```bash
    bun run typecheck
    bun run lint
    bun run build   # should produce .next/standalone
    ```

11. **Set up Docker:**
    - Copy `Dockerfile` and `docker-entrypoint.sh` to project root.
    - Test locally: `docker build -t myapp . && docker run -p 3000:3000 myapp`

12. **Add environment variables:**
    - Copy `.env.example` with documented vars (NEXT_PUBLIC_*, DATABASE_URL, AUTH_SECRET, etc.)
    - Create `.env.local` for local development

13. **Write first e2e test:**
    ```bash
    # tests/e2e/homepage.spec.ts
    import { test, expect } from "@playwright/test";
    
    test("homepage loads", async ({ page }) => {
      await page.goto("/");
      await expect(page).toHaveTitle(/Home|Welcome/);
    });
    ```

14. **Run dev server:**
    ```bash
    bun run dev
    # Visit http://localhost:3000/en (or your default locale)
    ```

## Reference

- **API Adapters Pattern:** The mock/real adapter pattern allows switching backend implementations via `NEXT_PUBLIC_API_DATA_SOURCE=mock|real` without changing component code. See `lib/api/adapters/` structure.
- **For Next.js+Go monorepo pairing:** See the `monorepo-scaffold-nextjs-go` skill in this library for setting up services, Go backend, shared infra, and coordination.
- **Strict TypeScript:** `strict: true` in tsconfig.json and `@typescript-eslint/no-explicit-any: "error"` in ESLint enforce type safety across the codebase.
- **Layer Boundaries:** Preserve dependency direction: Presentation (pages/components) → Application (lib/) → Domain (types/helpers). Never import from outer layers into inner layers.

