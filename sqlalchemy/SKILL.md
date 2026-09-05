---
name: SQLAlchemy
description: Expert guidance on SQLAlchemy 2.0 with FastAPI — typed declarative models, relationships and loader strategies, async engine/session, Alembic migrations, repository pattern with Depends, Pydantic mapping, and unit-of-work transactions.
---

# SQLAlchemy

Expert guidance on SQLAlchemy 2.0 สำหรับ FastAPI — declarative models แบบ typed (`Mapped`/`mapped_column`), `relationship()` + loader strategies เพื่อเลี่ยง N+1, `AsyncSession`/`async_sessionmaker`, Alembic migrations, repository pattern ผ่าน `Depends`, การ map ORM ↔ Pydantic ที่ boundary และ unit-of-work

## Project Structure

```
app/
├── domain/
│   └── product.py            # Entity / port (pure, ไม่มี SQLAlchemy)
├── application/
│   └── use_cases/
├── infrastructure/
│   └── db/
│       ├── base.py           # DeclarativeBase
│       ├── session.py        # engine + async_sessionmaker + get_session()
│       ├── models/
│       │   └── product.py
│       └── repositories/
│           └── product_repository.py
├── api/
│   ├── routers/
│   └── schemas/              # Pydantic DTO
alembic/
├── env.py
└── versions/
```

## Common Commands

```bash
alembic init -t async alembic          # async template
alembic revision --autogenerate -m "add products table"
alembic upgrade head
alembic downgrade -1
alembic current                        # revision ปัจจุบันของ DB
alembic history --verbose
alembic upgrade head --sql             # dry-run: ดู SQL โดยไม่รัน
```

> `--autogenerate` ตรวจไม่เจอ: rename column/table, `CHECK` constraint, enum value ใหม่, server default บางแบบ — ต้อง review และแก้ไฟล์ migration ด้วยมือเสมอ

---

## Declarative Models (2.0 style)

```python
# infrastructure/db/base.py
from datetime import datetime
from sqlalchemy import String, ForeignKey, Numeric, Index, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass
```

```python
# infrastructure/db/models/product.py
from decimal import Decimal
from ulid import ULID

def new_ulid() -> str:
    return str(ULID())

class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, default=new_ulid)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000))       # Optional -> nullable
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[ProductStatus] = mapped_column(default=ProductStatus.DRAFT)  # python Enum
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    category: Mapped["Category"] = relationship(back_populates="products", lazy="raise")

    __table_args__ = (Index("ix_products_category_status", "category_id", "status"),)
```

> `Mapped[X | None]` = nullable, `Mapped[X]` = `NOT NULL` — type annotation คือ source of truth ของ schema

---

## Relationships & Loader Strategies

```python
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, default=new_ulid)
    name: Mapped[str]

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="raise",        # กัน implicit lazy load (สำคัญมากใน async)
    )
```

`lazy="raise"` ทำให้ N+1 หรือ lazy load หลัง session ปิด กลายเป็น error ทันทีแทนที่จะเงียบ — ใน async ต้องระบุ loader ชัดเจนทุกครั้ง

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, subqueryload

# selectin: query แยก 1 ครั้ง (IN ...) — ดีที่สุดสำหรับ collection (one-to-many)
stmt = select(Category).options(selectinload(Category.products))

# joined: LEFT JOIN ครั้งเดียว — ดีสำหรับ many-to-one / one-to-one
stmt = select(Product).options(joinedload(Product.category))

# subquery: correlated subquery — legacy, มักถูกแทนด้วย selectin
stmt = select(Category).options(subqueryload(Category.products))

# nested
stmt = select(Order).options(
    selectinload(Order.items).joinedload(OrderItem.product)
)
```

| กรณี | เลือก |
|---|---|
| many-to-one / one-to-one | `joinedload` |
| one-to-many / many-to-many | `selectinload` |
| ต้อง filter บน relation | `.join()` + `contains_eager()` |

> `joinedload` บน collection ทำให้แถวคูณกัน ต้องใช้ `.unique()` บนผลลัพธ์ — เลี่ยงด้วย `selectinload`

---

## Async Engine & Session

```python
# infrastructure/db/session.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    settings.database_url,          # postgresql+asyncpg://...
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,         # ให้ object ใช้ต่อได้หลัง commit
    autoflush=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session               # commit/rollback ให้ use case เป็นคนสั่ง
```

> `expire_on_commit=False` จำเป็นใน async ไม่งั้น attribute หลัง commit จะ trigger lazy refresh แล้ว error

---

## Repository Pattern + Depends

```python
# infrastructure/db/repositories/product_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

class SqlAlchemyProductRepository(ProductRepositoryPort):      # port อยู่ที่ application/domain
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, product_id: str) -> ProductEntity | None:
        stmt = (
            select(ProductModel)
            .options(joinedload(ProductModel.category))
            .where(ProductModel.id == product_id)
        )
        row = await self._session.scalar(stmt)
        return to_domain(row) if row else None                 # map ก่อนคืนค่าเสมอ

    async def list_by_category(self, category_id: str, limit: int = 20, offset: int = 0):
        stmt = (
            select(ProductModel)
            .where(ProductModel.category_id == category_id)
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.scalars(stmt)).all()
        return [to_domain(r) for r in rows]

    async def add(self, product: ProductEntity) -> None:
        self._session.add(to_model(product))                   # ไม่ commit ที่นี่ — UoW เป็นคนสั่ง
```

```python
# api/deps.py
def get_product_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProductRepositoryPort:
    return SqlAlchemyProductRepository(session)

ProductRepo = Annotated[ProductRepositoryPort, Depends(get_product_repository)]
```

---

## Unit of Work / Transactions

Repository ไม่ commit เอง — Application layer คุมขอบเขต transaction

```python
class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.products = SqlAlchemyProductRepository(session)
        self.inventory = SqlAlchemyInventoryRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, *_) -> None:
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()

# use case
async def place_order(cmd: PlaceOrder, uow: UnitOfWork) -> str:
    async with uow:
        await uow.products.reserve(cmd.product_id, cmd.qty)
        await uow.inventory.decrement(cmd.product_id, cmd.qty)
    return order_id
```

หรือใช้ nested transaction แบบสั้น: `async with session.begin(): ...` (commit อัตโนมัติเมื่อออกจาก block)

---

## Pydantic ↔ ORM ที่ Boundary

```python
# api/schemas/product.py
from pydantic import BaseModel, ConfigDict

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # v2 (แทน orm_mode)

    id: str
    name: str
    price: Decimal
    category_name: str

class ProductCreate(BaseModel):
    name: str
    price: Decimal
    category_id: str
```

```python
@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, repo: ProductRepo) -> ProductRead:
    product = await repo.find_by_id(product_id)      # -> domain entity
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead.model_validate(product)
```

> ห้ามคืน ORM model ตรงจาก endpoint — เสี่ยง lazy load นอก session, leak คอลัมน์ภายใน และผูก API contract เข้ากับ schema

---

## Alembic (async)

```python
# alembic/env.py (ส่วนสำคัญ)
from app.infrastructure.db.base import Base
import app.infrastructure.db.models        # import ทุก model ให้ metadata ครบ

target_metadata = Base.metadata

async def run_async_migrations() -> None:
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda c: context.configure(
                connection=c, target_metadata=target_metadata, compare_type=True
            )
        )
        async with connection.begin():
            await connection.run_sync(lambda _: context.run_migrations())
```

### Additive migration

```python
def upgrade() -> None:
    op.add_column("products", sa.Column("sku", sa.String(64), nullable=True))
    op.create_index("ix_products_sku", "products", ["sku"])

def downgrade() -> None:
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_column("products", "sku")
```

> Deploy destructive change เป็นหลายขั้น: (1) เพิ่มคอลัมน์ nullable → (2) backfill (`op.execute`) → (3) `alter_column(nullable=False)` / drop คอลัมน์เก่า และเขียน `downgrade()` ให้ครบทุก revision

---

## Best Practices

1. **`lazy="raise"`** ทุก relationship — บังคับให้ระบุ loader ชัดเจน
2. **`selectinload` สำหรับ collection, `joinedload` สำหรับ many-to-one**
3. **`expire_on_commit=False`** ใน `async_sessionmaker`
4. **Repository ไม่ commit** — UoW/Application คุม transaction
5. **Map ORM → domain/Pydantic ที่ boundary** ไม่ปล่อยรั่ว
6. **Review ทุก autogenerate** — Alembic ตรวจ rename/enum/check ไม่ครบ
7. **Session ต่อ request เดียว** ผ่าน `Depends` — ห้าม global session

---

## สรุป

1. **Models** — `Mapped`/`mapped_column`, ULID PK, `Index` ใน `__table_args__`
2. **Relationships** — `relationship()` + `back_populates` + `lazy="raise"`
3. **N+1** — `selectinload` (collection) vs `joinedload` (many-to-one)
4. **Async** — `create_async_engine` + `async_sessionmaker(expire_on_commit=False)`
5. **DI** — `get_session` → repository ผ่าน FastAPI `Depends`
6. **Transactions** — Unit of Work, commit/rollback ที่ Application
7. **Boundary** — Pydantic `from_attributes`, ไม่คืน ORM model ออก API
8. **Alembic** — `revision --autogenerate` → review → `upgrade head`, additive-first + `downgrade()`
