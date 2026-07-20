---
name: Drizzle ORM
description: Expert guidance on Drizzle ORM — schema definition, migrations with drizzle-kit, relational + SQL-like query APIs, type inference, relations, transactions, and repository pattern.
---

# Drizzle ORM

Expert guidance on Drizzle ORM — schema definition (`pg-core` / `sqlite-core` / `mysql-core`), migrations with `drizzle-kit`, relational queries vs SQL-like builder, type inference, `relations()`, transactions, and the repository pattern.

@doc-version: drizzle-orm@0.44

> หมายเหตุ: เวอร์ชันเป็นค่าประมาณ ณ กลางปี 2026 (Drizzle ORM `^0.44`, `drizzle-kit ^0.31`) โปรดตรวจกับ `package.json` ของโปรเจกต์จริงเสมอ

## Project Structure

```
packages/db/
├── drizzle.config.ts        # drizzle-kit config (dialect, schema, out)
├── drizzle/
│   └── migrations/          # Generated SQL migrations + meta/
└── src/
    ├── schema/
    │   ├── index.ts         # Re-export ทุก table + relations
    │   ├── product.ts       # Table + relations ต่อ feature
    │   └── category.ts
    ├── client.ts            # drizzle() instance + pool
    └── repositories/
        └── product-repository.ts  # Repository (infrastructure layer)
```

## Common Commands

```bash
# Generate SQL migration จาก schema diff
pnpm drizzle-kit generate

# Apply migrations ที่ค้างอยู่ (production-safe)
pnpm drizzle-kit migrate

# Push schema ตรงเข้า DB — ใช้เฉพาะ prototype/dev เท่านั้น
pnpm drizzle-kit push

# ตรวจสอบ schema กับ migration state
pnpm drizzle-kit check

# เปิด Drizzle Studio
pnpm drizzle-kit studio
```

> `push` ข้าม migration history — **ห้ามใช้กับ production** เพราะไม่มี rollback path ที่ตรวจสอบได้ ใช้ `generate` + `migrate` เสมอ

---

## Client Setup

```typescript
// src/client.ts
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// ส่ง schema เข้าไปเพื่อเปิดใช้ relational queries API (db.query.*)
export const db = drizzle(pool, { schema });
export type DB = typeof db;
```

---

## Schema Patterns

### Basic Table (`pg-core`)

```typescript
// src/schema/product.ts
import { pgTable, text, numeric, timestamp, index } from 'drizzle-orm/pg-core';
import { ulid } from 'ulid';
import { categories } from './category';

export const products = pgTable(
  'products',
  {
    id: text('id').primaryKey().$defaultFn(() => ulid()),
    name: text('name').notNull(),
    description: text('description'),
    price: numeric('price', { precision: 10, scale: 2 }).notNull(),
    categoryId: text('category_id')
      .notNull()
      .references(() => categories.id),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true })
      .defaultNow()
      .notNull()
      .$onUpdate(() => new Date()),
  },
  (table) => [index('products_category_id_idx').on(table.categoryId)],
);
```

> Primary key ใหม่ใช้ ULID (`$defaultFn(() => ulid())`) เว้นแต่ external contract บังคับเป็นอย่างอื่น สอดคล้องกับ convention ของ repo

### Enums

```typescript
import { pgEnum } from 'drizzle-orm/pg-core';

export const orderStatus = pgEnum('order_status', [
  'PENDING',
  'PROCESSING',
  'SHIPPED',
  'DELIVERED',
  'CANCELLED',
]);

// ใช้งานใน table
// status: orderStatus('status').default('PENDING').notNull(),
```

### Dialect อื่น

```typescript
// sqlite-core
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull(),
});

// mysql-core
import { mysqlTable, varchar, decimal } from 'drizzle-orm/mysql-core';

export const items = mysqlTable('items', {
  id: varchar('id', { length: 26 }).primaryKey(),
  price: decimal('price', { precision: 10, scale: 2 }).notNull(),
});
```

---

## Relations

`relations()` เป็น relational metadata สำหรับ query API — ไม่สร้าง FK เอง (FK มาจาก `.references()`)

```typescript
// src/schema/category.ts
import { pgTable, text } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { products } from './product';

export const categories = pgTable('categories', {
  id: text('id').primaryKey().$defaultFn(() => ulid()),
  name: text('name').notNull(),
  slug: text('slug').notNull().unique(),
});

export const categoriesRelations = relations(categories, ({ many }) => ({
  products: many(products),
}));

// ใน product.ts
export const productsRelations = relations(products, ({ one }) => ({
  category: one(categories, {
    fields: [products.categoryId],
    references: [categories.id],
  }),
}));
```

---

## Type Inference

```typescript
import type { products } from './schema/product';

// Row type ที่ select ออกมา
export type Product = typeof products.$inferSelect;
// Payload สำหรับ insert (optional fields ที่มี default จะเป็น optional)
export type NewProduct = typeof products.$inferInsert;
```

> ใช้ type ที่ infer เหล่านี้เป็น boundary type ภายใน infrastructure layer แล้ว map เป็น domain entity ก่อนส่งออก — อย่าปล่อย Drizzle row type รั่วเข้า application/domain

---

## Query API

Drizzle มี 2 API — เลือกตามความเหมาะสม:

### 1. Relational Queries (`db.query.*`) — อ่านข้อมูลพร้อม relations

```typescript
const list = await db.query.products.findMany({
  where: (product, { eq, and, gte, lte, ilike }) =>
    and(ilike(product.name, '%shirt%'), gte(product.price, '10'), lte(product.price, '100')),
  orderBy: (product, { desc }) => desc(product.createdAt),
  limit: 20,
  offset: 0,
  with: { category: true },
});

const one = await db.query.products.findFirst({
  where: (product, { eq }) => eq(product.id, id),
  with: { category: true },
});
```

### 2. SQL-like Builder (`db.select().from()`) — ควบคุมละเอียด / join เอง

```typescript
import { eq, and, gte, ilike, desc } from 'drizzle-orm';

const rows = await db
  .select()
  .from(products)
  .innerJoin(categories, eq(products.categoryId, categories.id))
  .where(and(ilike(products.name, '%shirt%'), gte(products.price, '10')))
  .orderBy(desc(products.createdAt))
  .limit(20)
  .offset(0);
```

> เลือก `db.query.*` เมื่อต้องการ nested relations แบบ typed สะดวก; เลือก `db.select()` เมื่อต้องการ aggregate, custom join, partial select หรือ raw expression

### Insert / Update / Delete

```typescript
import { eq } from 'drizzle-orm';

const [created] = await db.insert(products).values(data).returning();

const [updated] = await db
  .update(products)
  .set({ price: '99.00' })
  .where(eq(products.id, id))
  .returning();

await db.delete(products).where(eq(products.id, id));
```

---

## Transactions

Transaction orchestration ควรถูกเรียกจาก application layer แต่ implement ผ่าน repository/unit-of-work ใน infrastructure

```typescript
await db.transaction(async (tx) => {
  const [order] = await tx.insert(orders).values(orderData).returning();

  await tx
    .update(inventory)
    .set({ quantity: sql`${inventory.quantity} - ${qty}` })
    .where(eq(inventory.productId, productId));

  // throw ที่ใดก็ได้ = rollback อัตโนมัติ
  return order;
});
```

---

## Repository Pattern

Repository อยู่ใน infrastructure layer เท่านั้น — implement port ที่ application/domain owned และ map เป็น domain entity ก่อนคืนค่า

```typescript
// src/repositories/product-repository.ts
import { eq } from 'drizzle-orm';
import type { DB } from '../client';
import { products } from '../schema/product';

type Product = typeof products.$inferSelect;
type NewProduct = typeof products.$inferInsert;

// Port นี้ถูก define ไว้ใน application layer จริง ๆ (แสดงไว้ที่นี่เพื่อความครบถ้วน)
export interface ProductRepository {
  findById(id: string): Promise<Product | null>;
  findAll(params?: { limit?: number; offset?: number }): Promise<Product[]>;
  create(data: NewProduct): Promise<Product>;
  update(id: string, data: Partial<NewProduct>): Promise<Product>;
  delete(id: string): Promise<void>;
}

export class DrizzleProductRepository implements ProductRepository {
  constructor(private readonly db: DB) {}

  async findById(id: string): Promise<Product | null> {
    const row = await this.db.query.products.findFirst({
      where: (p, { eq }) => eq(p.id, id),
      with: { category: true },
    });
    return row ?? null;
  }

  async findAll(params?: { limit?: number; offset?: number }): Promise<Product[]> {
    return this.db.query.products.findMany({
      limit: params?.limit ?? 20,
      offset: params?.offset ?? 0,
      orderBy: (p, { desc }) => desc(p.createdAt),
    });
  }

  async create(data: NewProduct): Promise<Product> {
    const [created] = await this.db.insert(products).values(data).returning();
    return created;
  }

  async update(id: string, data: Partial<NewProduct>): Promise<Product> {
    const [updated] = await this.db
      .update(products)
      .set(data)
      .where(eq(products.id, id))
      .returning();
    return updated;
  }

  async delete(id: string): Promise<void> {
    await this.db.delete(products).where(eq(products.id, id));
  }
}
```

---

## Migration Workflow

1. แก้ schema ใน `src/schema/*.ts` — **additive-first** (คอลัมน์/ตารางใหม่เป็น nullable ก่อน)
2. Generate: `pnpm drizzle-kit generate --name descriptive_name`
3. Review ไฟล์ SQL ใน `drizzle/migrations/`
4. ทดสอบ up path บน local/staging: `pnpm drizzle-kit migrate`
5. Deploy production: `pnpm drizzle-kit migrate`

> destructive change (drop/rename) ต้องแยกเป็นหลาย migration และแจ้ง risk + ขอ approval ก่อน; Drizzle ไม่ generate down migration ให้อัตโนมัติ ต้องเตรียม rollback SQL เอง

### drizzle.config.ts

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  dialect: 'postgresql',
  schema: './src/schema/index.ts',
  out: './drizzle/migrations',
  dbCredentials: { url: process.env.DATABASE_URL! },
  strict: true,
  verbose: true,
});
```

---

## Best Practices

1. **Repository layer** — ไม่เรียก `db` ตรงใน handlers/use cases
2. **`generate` + `migrate`** — ห้าม `push` บน production
3. **Additive migrations** — เพิ่ม nullable column/table ก่อน destructive
4. **Indexes** — ประกาศ `index()` ให้ fields ที่ query บ่อยและ FK
5. **Type inference** — `$inferSelect`/`$inferInsert` เป็น boundary type, map เป็น domain entity
6. **Transactions** — orchestrate จาก application, throw = rollback
7. **`relations()`** — สำหรับ query API เท่านั้น, FK จริงมาจาก `.references()`

---

## สรุป

1. **Schema** — `pgTable`/`sqliteTable`/`mysqlTable`, ULID PK, `index()`, `pgEnum`
2. **Client** — `drizzle(pool, { schema })` เพื่อเปิด relational queries
3. **Query** — `db.query.*` (relational) vs `db.select().from()` (SQL-like)
4. **Types** — `$inferSelect` / `$inferInsert`
5. **Relations** — `relations()` + `.references()`
6. **Transactions** — `db.transaction()` atomic + auto rollback
7. **Repository** — infrastructure layer, implement inward-owned ports
8. **Migrations** — `generate` → review → test → `migrate`, additive-first
