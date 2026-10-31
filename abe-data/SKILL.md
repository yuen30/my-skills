---
name: abe-data
description: "ORM and database-layer skill for Prisma (schema.prisma), Drizzle ORM, Laravel Eloquent and SQLAlchemy/Alembic. Use when adding or changing a model, column, relation or migration, writing queries or transactions, or reviewing the repository layer in a TypeScript, Laravel or Python/FastAPI project."
---

# ABE Data

One skill for every supported ORM. Detect the ORM, then read ONLY the matching reference; do not load references for ORMs the project does not use.

## Step 1: Detect the ORM

| Marker in the project | Read |
|---|---|
| `prisma/schema.prisma` or `"@prisma/client"` dependency | [prisma.md](references/prisma.md) |
| `drizzle.config.*` or `"drizzle-orm"` dependency | [drizzle.md](references/drizzle.md) |
| `artisan` + `app/Models` (Laravel) | [eloquent.md](references/eloquent.md) |
| `sqlalchemy` / `alembic` in pyproject.toml or requirements | [sqlalchemy.md](references/sqlalchemy.md) |

Monorepos: detect per app/package from the file being changed, not from the repo root.

## Shared rules (apply to every ORM)

- Detect the installed version first (lockfile / resolved package, not just the constraint) and state it before giving version-specific guidance. If detection is impossible, say so instead of guessing.
- Migrations must be reversible (or ship explicit rollback SQL) and be reviewed before they are applied. Never edit a migration that has already been applied; add a new one.
- Destructive changes (drop/rename) go in separate steps: add nullable, backfill, then tighten or drop.
- Avoid N+1: eager load relations explicitly instead of lazy loading inside loops.
- Wrap multi-write operations in a transaction; the application layer owns the boundary, repositories do not commit on their own.
- Access data through a repository layer (not directly from controllers/handlers); layout follows `project-structure`.
- Do not invent APIs or config keys; verify against the docs for the detected version.

## Sibling skills

- `project-structure` — where files and folders go (layout, layering) for every stack.
- `abe-framework` — framework code around the data layer (Laravel, Django, Hono, Next.js, ...).

## Reference routing

| File | Read when |
|---|---|
| [prisma.md](references/prisma.md) | Prisma schema, `prisma migrate`, PrismaClient, `$transaction`, `$queryRaw`, PostGIS, seeding |
| [drizzle.md](references/drizzle.md) | Drizzle schemas, `drizzle-kit` migrations, `db.query` / SQL-like builder, relations, type inference |
| [eloquent.md](references/eloquent.md) | Eloquent models, casts, relationships, scopes, observers, soft deletes, migrations, factories, N+1 |
| [sqlalchemy.md](references/sqlalchemy.md) | SQLAlchemy 2.0 models, loader strategies, AsyncSession, Alembic revisions, FastAPI `Depends` repositories |
