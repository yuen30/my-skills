---
name: Eloquent ORM
description: Expert guidance on Laravel Eloquent ORM — model definition, casts, relationships, eager loading, query builder, schema migrations, scopes, observers, soft deletes, repository pattern, factories and seeders.
---

# Eloquent ORM

Expert guidance on Laravel Eloquent — models (`$fillable`/`casts`), relationships, eager loading เพื่อเลี่ยง N+1, migrations ด้วย schema builder, local/global scopes, model events/observers, soft deletes, repository pattern ใน infrastructure layer และ factories/seeders สำหรับเทส

## Project Structure

```
app/
├── Models/
│   ├── Product.php
│   └── Category.php
├── Domain/
│   └── Product/
│       └── ProductRepositoryInterface.php   # Port (inward-owned)
├── Infrastructure/
│   └── Persistence/
│       └── EloquentProductRepository.php    # Adapter
├── Observers/
│   └── ProductObserver.php
database/
├── migrations/
├── factories/
└── seeders/
```

## Common Commands

```bash
php artisan make:model Product -mfs      # model + migration + factory + seeder
php artisan make:migration add_status_to_products_table
php artisan make:observer ProductObserver --model=Product

php artisan migrate                      # apply
php artisan migrate --pretend            # dry-run: ดู SQL ที่จะรัน
php artisan migrate:status
php artisan migrate:rollback --step=1    # rollback batch ล่าสุด
php artisan db:seed --class=ProductSeeder
```

> `migrate:fresh` / `migrate:refresh` เป็น destructive (drop ทุกตาราง) — ห้ามรันบน staging/production

---

## Model Definition

```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Product extends Model
{
    use HasFactory, SoftDeletes;

    protected $table = 'products';

    // ใช้ $fillable (allowlist) เสมอ — $guarded = [] เปิดช่อง mass-assignment
    protected $fillable = ['name', 'description', 'price', 'status', 'category_id'];

    protected $hidden = ['internal_note'];

    // Laravel 10+ : casts() method (ยังรองรับ $casts array แบบเดิม)
    protected function casts(): array
    {
        return [
            'price'        => 'decimal:2',
            'is_active'    => 'boolean',
            'meta'         => 'array',
            'status'       => ProductStatus::class,   // backed enum
            'published_at' => 'immutable_datetime',
        ];
    }
}
```

### ULID primary key

```php
use Illuminate\Database\Eloquent\Concerns\HasUlids;

class Product extends Model
{
    use HasUlids;

    public $incrementing = false;
    protected $keyType = 'string';
}
```

---

## Relationships

```php
// hasOne / hasMany
public function profile(): HasOne { return $this->hasOne(Profile::class); }
public function orderItems(): HasMany { return $this->hasMany(OrderItem::class); }

// belongsTo (FK อยู่ฝั่งนี้)
public function category(): BelongsTo { return $this->belongsTo(Category::class); }

// belongsToMany + pivot columns
public function tags(): BelongsToMany
{
    return $this->belongsToMany(Tag::class, 'product_tag')
        ->withPivot('position')
        ->withTimestamps();
}

// hasManyThrough
public function orders(): HasManyThrough
{
    return $this->hasManyThrough(Order::class, OrderItem::class);
}

// polymorphic
public function images(): MorphMany { return $this->morphMany(Image::class, 'imageable'); }
// ใน Image: public function imageable(): MorphTo { return $this->morphTo(); }
```

---

## Query Builder vs Eloquent

```php
// Eloquent (คืน Model / Collection)
Product::query()
    ->where('status', ProductStatus::Published)
    ->whereBetween('price', [10, 100])
    ->whereHas('category', fn ($q) => $q->where('slug', 'clothing'))
    ->orderByDesc('created_at')
    ->paginate(20);

// Query Builder (คืน stdClass — เร็วกว่าสำหรับ report/aggregate)
DB::table('products')
    ->selectRaw('category_id, count(*) as total, avg(price) as avg_price')
    ->groupBy('category_id')
    ->get();
```

> เริ่มด้วย `::query()` เสมอเพื่อให้ chain type-safe และ static analysis อ่านออก

### Eager loading — เลี่ยง N+1

```php
// ❌ N+1: query 1 ครั้ง + N ครั้งต่อสินค้า
foreach (Product::all() as $p) { echo $p->category->name; }

// ✅ eager load
$products = Product::with(['category', 'tags'])->get();

// เลือกเฉพาะคอลัมน์ที่ใช้ (ต้องมี FK ด้วยเสมอ)
Product::with('category:id,name')->get();

// nested + constrained
Product::with(['orderItems' => fn ($q) => $q->where('qty', '>', 1)])->get();

// นับโดยไม่โหลด rows
Product::withCount(['orderItems', 'tags'])->get();   // -> $p->order_items_count

// aggregate อื่น ๆ
Product::withSum('orderItems', 'qty')->withExists('images')->get();

// lazy eager load หลังโหลดมาแล้ว
$products->load('category');
```

> เปิด `Model::preventLazyLoading(! app()->isProduction());` ใน `AppServiceProvider::boot()` เพื่อให้ N+1 ระเบิดตอน dev

---

## Migrations

```php
// database/migrations/2026_09_05_000000_create_products_table.php
public function up(): void
{
    Schema::create('products', function (Blueprint $table) {
        $table->ulid('id')->primary();
        $table->string('name');
        $table->text('description')->nullable();
        $table->decimal('price', 10, 2);
        $table->string('status')->default('draft');
        $table->foreignUlid('category_id')->constrained()->restrictOnDelete();
        $table->json('meta')->nullable();
        $table->timestamps();
        $table->softDeletes();

        $table->index(['category_id', 'status']);
        $table->unique('slug');
    });
}

public function down(): void
{
    Schema::dropIfExists('products');
}
```

### Additive migration (backward-compatible)

```php
public function up(): void
{
    Schema::table('products', function (Blueprint $table) {
        $table->string('sku')->nullable()->after('name');   // nullable ก่อนเสมอ
        $table->index('sku');
    });
}

public function down(): void
{
    Schema::table('products', function (Blueprint $table) {
        $table->dropIndex(['sku']);
        $table->dropColumn('sku');
    });
}
```

> เขียน `down()` ให้ครบเสมอ และแยก deploy เป็น: (1) เพิ่มคอลัมน์ nullable → (2) backfill → (3) ตั้ง `NOT NULL` / ลบคอลัมน์เก่า คนละ migration

---

## Scopes

```php
// Local scope
public function scopePublished(Builder $query): void
{
    $query->where('status', ProductStatus::Published)->whereNotNull('published_at');
}
// ใช้: Product::published()->get();

// Global scope (Laravel 11+ attribute)
#[ScopedBy(TenantScope::class)]
class Product extends Model {}

class TenantScope implements Scope
{
    public function apply(Builder $builder, Model $model): void
    {
        $builder->where('tenant_id', app(TenantContext::class)->id());
    }
}
// ข้าม: Product::withoutGlobalScope(TenantScope::class)->get();
```

---

## Model Events / Observers

```php
#[ObservedBy(ProductObserver::class)]
class Product extends Model {}

class ProductObserver
{
    public function creating(Product $product): void
    {
        $product->slug ??= Str::slug($product->name);
    }

    public function updated(Product $product): void
    {
        if ($product->wasChanged('price')) {
            PriceChanged::dispatch($product->id, $product->getOriginal('price'));
        }
    }
}
```

> Observer ต้องเป็น side-effect เบา ๆ (slug, audit, event dispatch) — business rule จริงอยู่ที่ Domain/Application ไม่ใช่ใน model event และ observer **ไม่ทำงาน** กับ bulk update (`Product::query()->update(...)`)

---

## Soft Deletes

```php
$product->delete();          // set deleted_at
Product::withTrashed()->get();
Product::onlyTrashed()->get();
$product->restore();
$product->forceDelete();     // ลบจริง — destructive
```

---

## Repository Pattern

Port อยู่ที่ Domain/Application, adapter อยู่ Infrastructure — controller ห้ามเรียก Eloquent ตรง

```php
// app/Domain/Product/ProductRepositoryInterface.php
interface ProductRepositoryInterface
{
    public function findById(string $id): ?ProductEntity;
    public function save(ProductEntity $product): void;
}

// app/Infrastructure/Persistence/EloquentProductRepository.php
final readonly class EloquentProductRepository implements ProductRepositoryInterface
{
    public function findById(string $id): ?ProductEntity
    {
        $row = Product::query()->with('category')->find($id);

        return $row ? ProductMapper::toDomain($row) : null;   // อย่าปล่อย Model ออกนอก layer
    }

    public function save(ProductEntity $product): void
    {
        Product::query()->updateOrCreate(
            ['id' => $product->id],
            ProductMapper::toRow($product),
        );
    }
}

// AppServiceProvider (composition root)
$this->app->bind(ProductRepositoryInterface::class, EloquentProductRepository::class);
```

### Transactions — orchestrate จาก Application layer

```php
DB::transaction(function () use ($command) {
    $this->orders->save($order);
    $this->inventory->decrement($command->productId, $command->qty);
}, attempts: 3);   // retry เมื่อ deadlock
```

---

## Factories & Seeders

```php
class ProductFactory extends Factory
{
    protected $model = Product::class;

    public function definition(): array
    {
        return [
            'name'        => fake()->words(3, true),
            'price'       => fake()->randomFloat(2, 10, 500),
            'status'      => ProductStatus::Draft,
            'category_id' => Category::factory(),
        ];
    }

    public function published(): static
    {
        return $this->state(fn () => [
            'status' => ProductStatus::Published,
            'published_at' => now(),
        ]);
    }
}

// ใช้ในเทส
Product::factory()->count(3)->published()->for($category)->create();

// Seeder — idempotent ด้วย updateOrCreate
Category::query()->updateOrCreate(['slug' => 'electronics'], ['name' => 'Electronics']);
```

---

## Best Practices

1. **`$fillable` allowlist** — อย่าใช้ `$guarded = []`
2. **Eager loading** — `with()`/`withCount()` + `preventLazyLoading()` ตอน dev
3. **Additive migrations** — nullable ก่อน, backfill แยก, `down()` ครบเสมอ
4. **Indexes** — FK และ composite ตาม query pattern จริง
5. **Repository + mapper** — ไม่ปล่อย Eloquent Model เข้า Domain/Presentation
6. **Transactions** — `DB::transaction()` ใน Application layer พร้อม `attempts`
7. **Chunk สำหรับข้อมูลใหญ่** — `chunkById()` / `lazyById()` แทน `all()`

---

## สรุป

1. **Model** — `$fillable`, `casts()`, `HasUlids`, `SoftDeletes`
2. **Relationships** — hasOne/hasMany/belongsTo/belongsToMany/morphMany
3. **N+1** — `with()`, `withCount()`, `preventLazyLoading()`
4. **Migrations** — schema builder, foreign keys, additive-first, `--pretend` + rollback
5. **Scopes** — local scope + global scope (multi-tenant)
6. **Observers** — side-effect เบา ๆ, ไม่ทำงานกับ bulk update
7. **Repository** — port ที่ Domain, adapter ที่ Infrastructure, map เป็น entity
8. **Testing** — factories + states, seeder แบบ idempotent
