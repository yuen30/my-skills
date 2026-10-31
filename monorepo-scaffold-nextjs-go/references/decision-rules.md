## Architecture Decision Rules

### 1. Dependency Direction (Non-Negotiable)

```
Presentation ──→ Application ──→ Domain
   (pages,          (hooks,         (types,
   components)      adapters)       helpers)
       ↑                ↑
       └────────────────┘
Infrastructure implements ports
(Database, MQ, SFTP, external APIs)
      ↑
      │ (inward-owned interfaces)
   Domain / Application
```

**Rules:**
- Inner layers (Domain, Application) **never import** outer layers (Presentation, Infrastructure, Composition Root).
- Outer layers **import** inner layers.
- Infrastructure implements inward-owned **ports** (interfaces defined in Domain/Application).
- No cycles, no hidden global state, no leaky ORM objects across boundaries.

### 2. New Primary Keys

Use **ULIDs** for new primary keys by default unless an external contract (SAP, ERP, customer database) mandates otherwise.

```go
// Go example using google/uuid or similar ULID library
id := ulid.Make()  // or uuid.NewString()
```

```typescript
// TypeScript: export as string
export type ID = string;
export function generateId(): ID {
  return crypto.randomUUID(); // or ulid library
}
```

### 3. Error Handling Across Boundaries

**Domain:** Define domain-specific error types (not generic strings).
```go
// shared/common/models/errors.go
type ValidationError struct {
  Field   string
  Message string
}

type NotFoundError struct {
  Entity string
  ID     string
}
```

**Application:** Catch domain errors, map to use-case errors (DTOs, API contracts).
```go
// services/download/internal/app/download.go
case *models.ValidationError:
  return &app.DownloadError{
    Code:    "INVALID_FILE",
    Message: err.Message,
    Status:  http.StatusBadRequest,
  }
```

**Delivery:** Translate to HTTP status, client error responses.
```typescript
// webapp lib/api/adapters/real.ts
if (!res.ok) {
  const err = await res.json();
  if (err.code === 'NOT_FOUND') throw new NotFoundError(...);
  if (err.code === 'INVALID_FILE') throw new ValidationError(...);
  throw new UnknownError(...);
}
```

### 4. TypeScript `any` Forbidden

- No `any` type (enforce via ESLint as error)
- Use explicit types and `import type` for type-only imports
- Generic types with constraints, not unconstrained generics

```typescript
// ❌ WRONG
const data: any = response;

// ✅ CORRECT
const data: OrderListResponse = response;
import type { OrderListResponse } from '@/types/orders';
```

### 5. Secrets & Sensitive Data

**Never commit:**
- `.env` files (use `.env.example` as template)
- API keys, passwords, database credentials
- Production data, logs with sensitive fields
- Mock data with real customer/financial information

**Store safely:**
- GitHub Secrets for CI/CD
- AWS Secrets Manager / HashiCorp Vault for production
- `.env.local` (gitignored) for local development

### 6. Database Migrations

- Use ORM-native migrations (GORM auto-migration for Go, etc.) or custom versioned SQL scripts
- Store migrations in `shared/common/store/migrations/`
- Never run destructive migrations without data backup
- Test migrations on a copy of production data before running on live

### 7. Configuration & Environment

All config loaded **once at startup** from environment variables, then passed to services as dependency-injected values.

```go
// shared/common/config/config.go
type Config struct {
  PostgresURL  string
  RabbitMQURL  string
  LogLevel     string
  // ...
}

func LoadConfig() (*Config, error) {
  return &Config{
    PostgresURL: os.Getenv("POSTGRES_URL"),
    RabbitMQURL: os.Getenv("RABBITMQ_URL"),
    LogLevel:    os.Getenv("LOG_LEVEL"),
  }, nil
}

// services/download/internal/app/app.go
func New(cfg *config.Config) *App {
  return &App{
    db:     store.NewStore(cfg.PostgresURL),
    mq:     mq.NewClient(cfg.RabbitMQURL),
    logger: logger.New(cfg.LogLevel),
  }
}
```

No runtime config changes or environment variable lookups inside handlers.
