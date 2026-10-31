Read when placing code in a Go Fiber v3 API project (controllers, application services, policies, repositories, models, migrations).

# Go Fiber v3 Layered Structure

Convention codified from the `new-sales/api` reference project.

## Layout

```text
app.go                                   # Composition root: config, DB, middleware, routes
controllers/  routes/  middleware/       # Presentation (thin)
  <feature>_controller.go                # snake_case file names
helpers/
  <feature>/
    application/                         # package application
      service.go                         # use cases
      ports.go                           # Repository / UnitOfWork interfaces (owned here)
      dto.go                             # DTOs, typed sentinel errors
    infrastructure/
      gorm_repository.go                 # <orm>_repository.go — sole ORM-import point per feature
  <concept>/
    policy/                              # Pure domain rules, stdlib only
models/                                  # Flat, one snake_case file per table
database/
  migrate.go                             # GORM AutoMigrate
  partial_indexes.go                     # Hand-written raw SQL the ORM can't express
```

## Layer rules

| Layer | Path | Rules |
|---|---|---|
| Presentation | `controllers/`, `routes/`, `middleware/` | Thin. Identity/role read from middleware context, never the request body. One Application call per controller action. Map sentinel errors to HTTP via a local `mapXxxError`. |
| Application | `helpers/<feature>/application/` | `service.go`, `ports.go`, `dto.go`. No ORM, HTTP, or vendor types. Owns the ports; defines typed sentinel errors. Transaction orchestration lives here. |
| Domain | `helpers/<concept>/policy/` | Pure business rules, stdlib only. No framework, DB, network, filesystem, or env dependency. |
| Infrastructure | `helpers/<feature>/infrastructure/<orm>_repository.go` | The only place per feature that imports the ORM package and model types. Implements Application's Repository/UnitOfWork ports. Maps vendor errors (`gorm.ErrRecordNotFound`, Postgres `23505`) to Application sentinels. Returns DTOs/snapshots, never raw ORM structs. |
| Composition root | `app.go` | Wires config, DB, middleware, routes. Controllers self-wire their own service from the DB handle. |

## Persistence placement

- Models: flat in `models/`, one snake_case file per table.
- Migrations: GORM AutoMigrate in `database/migrate.go`, plus raw SQL for what the ORM can't express (e.g. partial unique indexes in `database/partial_indexes.go`). Raw-SQL fallback is accepted, not a smell.
- Race-safe approval flows: `ExpectedCycle` row-version + `SELECT ... FOR UPDATE` at the Infrastructure transaction boundary, never in the HTTP layer.

## When NOT to split

Plain CRUD / master-data entities with no business rules get no application/infrastructure package: use the generic reflective `CRUDController[T]` engine directly. Reserve the full split for features with real business rules (approval workflows, imports, auth, generators, shared policies).

## Review checklist

- Does any controller import the ORM or contain business rules?
- Does `application/` import GORM, Fiber, or vendor types?
- Is the ORM imported anywhere other than `infrastructure/<orm>_repository.go` (and `models/`, `database/`)?
- Do repositories return DTOs and map vendor errors to sentinels?
- Is a plain CRUD entity over-engineered with a full split?
