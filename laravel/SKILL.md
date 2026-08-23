---
name: laravel
description: Use when developing on Laravel (any recent major version), deciding between old vs new patterns across versions, or reviewing whether code follows current Laravel conventions. Detects installed version and derives applicable guidance.
---

# Laravel

Use this skill to navigate Laravel across major versions. The skill detects your project's installed Laravel version and derives applicable patterns and breaking changes for that version — not just from memory. Laravel evolves fast; your training data may be stale. When in doubt, derive from the official laravel/docs repo for the detected version — see Detect Version & Derive Guidance below.

**Precondition — do not skip:** Before making any claim about Laravel patterns, breaking changes, or reviewing code against 'current' Laravel conventions, you MUST first run Step 1 below to detect the actual installed version in this project. Never assume the version from the user's phrasing, training data, or the presence of the 'Laravel 13 Reference' section in this file. State the detected version explicitly before giving version-specific guidance. If detection is impossible (e.g. no project context, greenfield question), say so explicitly instead of guessing a version.

## Detect Version & Derive Guidance

When a question touches on Laravel patterns, breaking changes, or version-specific features, follow this procedure to ensure you're giving guidance for the *actual installed version*, not guessing:

### Step 1: Detect the installed Laravel version

Run one or more of these commands in the project root:

```shell
php artisan --version          # simplest; outputs "Laravel Framework X.Y.Z"
composer show laravel/framework | grep versions   # detailed output
grep '"laravel/framework"' composer.json           # constraint, not runtime version
php -v                         # verify PHP version meets the major version requirement (8.3+ for Laravel 13, 8.2+ for 12, etc.)
```

Note the detected **major version** (e.g., 13, 12, 11).

### Version Support Matrix

| Version | PHP Required | Released | Bug Fixes Until | Security Fixes Until |
|---------|-------------|----------|------------------|----------------------|
| 10 | 8.1 - 8.3 | Feb 14, 2023 | Aug 6, 2024 | Feb 4, 2025 |
| 11 | 8.2 - 8.4 | Mar 12, 2024 | Sep 3, 2025 | Mar 12, 2026 |
| 12 | 8.2 - 8.5 | Feb 24, 2025 | Aug 13, 2026 | Feb 24, 2027 |
| 13 | 8.3 - 8.5 | Mar 17, 2026 | Q3 2027 | Mar 17, 2028 |

This table is a snapshot from releases.md at the time this skill was written — always re-verify with `https://laravel.com/framework/docs/<major>.x/releases#support-policy` or the GitHub repo if the detected version isn't listed or dates seem stale (Laravel releases new majors annually).

### Step 2: Fetch docs for the detected major version

Canonical source: `https://github.com/laravel/docs` repository, with a separate branch per major version (`13.x`, `12.x`, `11.x`, etc.).

Choose one approach:

**Option A: Use an existing local clone (if you have one)**
```shell
cd <path-to-your-local-laravel-docs-clone>
git fetch origin
git diff origin/<major-1>.x origin/<major>.x -- <file>.md    # to see breaking changes
```

**Option B: Clone on demand**
```shell
# Clone just the detected major version branch to a temporary location:
git clone --branch <major>.x --depth 1 https://github.com/laravel/docs.git /tmp/laravel-docs-<major>

# Then diff against the previous major version:
git -C /tmp/laravel-docs-<major> fetch origin <major-1>.x:<major-1>.x
git -C /tmp/laravel-docs-<major> diff <major-1>.x origin/<major>.x -- <file>.md
```

**Option C: Fetch via GitHub raw URL (no clone)**
- Latest file on the detected major version: `https://raw.githubusercontent.com/laravel/docs/<major>.x/<file>.md`
- To compare in browser: `https://github.com/laravel/docs/compare/<major-1>.x...<major>.x -- <file>.md`

### Step 3: Find breaking changes for the detected version

If upgrading *to* the detected version, diff the `upgrade.md` file between the previous major version and the current:

```shell
# From your local clone or temp clone from Step 2:
git diff origin/<major-1>.x origin/<major>.x -- upgrade.md

# Or in browser:
https://github.com/laravel/docs/compare/<major-1>.x...<major>.x#files -- upgrade.md
```

### Step 4: Use pre-derived Laravel 13 reference (if applicable) or derive fresh

- **If the detected version is Laravel 13**, the "Laravel 13 Reference (historical)" section below contains pre-derived facts and breaking changes for the 12→13 transition. You can cite it directly without re-deriving from GitHub.
- **For any other version**, apply Steps 1–3 above to derive facts from the official docs for that version. Do not assume the Laravel 13 reference applies.

## Laravel 13 Reference (historical — do not assume still current)

Pre-derived reference for the Laravel 12→13 transition. Do not treat as current for other versions — re-derive per the Detect Version & Derive Guidance procedure above.

### What's New in Laravel 13 vs 12

### PHP 8.3 required
Laravel 13.x requires a minimum PHP version of 8.3. Confirm the project's `composer.json` `"php"` constraint and actual runtime version before assuming compatibility.

### Laravel AI SDK (`laravel/ai`)
First-party, provider-agnostic API for text generation, tool-calling agents, embeddings, audio, and images.

```php
use App\Ai\Agents\SalesCoach;
$response = SalesCoach::make()->prompt('Analyze this sales transcript...');

use Laravel\Ai\Image;
$image = Image::of('A donut on a counter')->generate();

use Illuminate\Support\Str;
$embeddings = Str::of('Napa Valley has great wine.')->toEmbeddings();
```
Docs: `ai-sdk.md` (largest file, ~1056 lines changed — read this in full when building AI features), `mcp.md` for MCP server integration.

### JSON:API Resources
First-party `Illuminate\Http\Resources\JsonApi\JsonApiResource`, extending `JsonResource`. Handles resource-object serialization, relationships, sparse fieldsets, includes, links, and sets `Content-Type: application/vnd.api+json`.

```shell
php artisan make:resource PostResource --json-api
```
```php
class PostResource extends JsonApiResource
{
    public $attributes = [/* ... */];
    public $relationships = [/* ... */];
}
```
Also new: `PreserveKeys` and `Collects` attributes replace the old `$preserveKeys` / `$collects` public properties on plain resources/collections. Docs: `eloquent-resources.md` (`#jsonapi-resources` section).

### Request Forgery Protection (renamed + origin-aware)
`VerifyCsrfToken` → `Illuminate\Foundation\Http\Middleware\PreventRequestForgery` (old class kept as deprecated alias). Adds `Sec-Fetch-Site` header origin verification before falling back to token validation.

```php
->withMiddleware(function (Middleware $middleware): void {
    $middleware->preventRequestForgery(originOnly: true);   // 403 instead of 419, no token fallback
    // or: allowSameSite: true, except: ['stripe/*']
})
```
Update any code referencing `VerifyCsrfToken::class` or calling `validateCsrfTokens(...)`. Docs: `csrf.md`.

### Queue Routing by class
```php
use Illuminate\Support\Facades\Queue;

// in a service provider's boot()
Queue::route(ProcessPodcast::class, connection: 'redis', queue: 'podcasts');
Queue::route(RequiresVideo::class, queue: 'video');
Queue::route([JobA::class, JobB::class], queue: 'batch'); // also accepts interfaces/traits/parent classes
```

### Expanded PHP attributes (replacing static properties/methods)
- Controllers: `#[Middleware(...)]`, `#[WithoutMiddleware(...)]`, `#[Authorize('ability', [Model::class, 'param'])]` (shortcut for `can` middleware).
- Queue jobs: `#[Tries(5)]`, `#[MaxExceptions(3)]`, `#[Backoff(3)]` / `#[Backoff([1,5,10])]`, `#[Timeout(120)]`, `#[FailOnTimeout]`, `#[DeleteWhenMissingModels]`, `#[UniqueFor(...)]`, `#[DebounceFor(...)]`.
- Resources: `#[PreserveKeys]`, `#[Collects(Member::class)]`.
- Attribute-based class/job config generally takes precedence over CLI flags (e.g. `#[Tries]` beats `--tries`).

```php
#[Middleware('auth')]
class CommentController
{
    #[Middleware('subscribed')]
    #[Authorize('create', [Comment::class, 'post'])]
    public function store(Post $post) { /* ... */ }
}
```
Docs: `controllers.md` (`#middleware-attributes`, `#authorization-attributes`), `queues.md` (attribute list, `#queue-routing`).

### `Cache::touch()`
Extend a cache item's TTL without re-fetching/re-storing its value.
```php
Cache::touch('key', 3600);
Cache::touch('key', now()->addHours(2));
```
Returns `false` if the key doesn't exist. If you maintain a custom cache store, add `touch($key, $seconds)` to satisfy the updated `Store`/`Repository` contracts.

### Semantic / vector search
Native vector query support (PostgreSQL + `pgvector`), embedding generation from strings, and query-builder similarity search:
```php
$documents = DB::table('documents')
    ->whereVectorSimilarTo('embedding', 'Best wineries in Napa Valley')
    ->limit(10)->get();
```
Docs: `search.md` (`#semantic-vector-search`), `queries.md` (`#vector-similarity-clauses`), `ai-sdk.md` (`#embeddings`).

### Breaking Changes from 12.x

Pulled directly from `upgrade.md` diff (12.x → 13.x). Full estimated upgrade time: ~10 minutes; most apps need little/no code change.

**High impact**
- `PreventRequestForgery` middleware rename + `Sec-Fetch-Site` origin verification (see above). Anywhere excluding/referencing `VerifyCsrfToken` must be updated.

**Medium impact**
- `cache.serializable_classes` config now defaults to `false` — hardens against PHP deserialization gadget-chain attacks if `APP_KEY` leaks. If the app caches PHP objects, explicitly allow-list classes: `'serializable_classes' => [App\Data\Foo::class]`.
- `upsert()` on MySQL/MariaDB now throws `InvalidArgumentException` if `uniqueBy` is empty (previously silently generated bad SQL).

**Low impact (worth a grep before upgrading)**
- Default cache/session-cookie prefix generation is now hyphenated (`app-cache-` vs `app_cache_`) when no explicit config value is set — set `CACHE_PREFIX` / `REDIS_PREFIX` / `SESSION_COOKIE` explicitly to avoid cache/session invalidation on deploy.
- `session.serialization` now defaults to `json` in fresh skeletons — switching an existing app from `php` to `json` invalidates all active sessions. Keep `php` if you need seamless migration.
- `Container::call()` now respects nullable class parameter defaults (matches Laravel 12's constructor-injection behavior) — a nullable typed param with no binding now resolves to `null` instead of an instance.
- MySQL `DELETE ... JOIN` queries now compile `ORDER BY`/`LIMIT` fully — can turn a previously-ignored clause into a `QueryException` on unsupported syntax.
- Domain-scoped routes now match before non-domain routes regardless of registration order.
- `QueueBusy->connection` renamed to `connectionName`; `JobAttempted->exceptionOccurred` (bool) replaced by `->exception` (exception object or `null`).
- `Queue` contract gained `pendingSize`, `delayedSize`, `reservedSize`, `creationTimeOfOldestPendingJob` — implement these on custom queue drivers.
- Model instantiation during `boot()`/trait `boot*()` now throws `LogicException` (previously silently allowed nested booting).
- Polymorphic pivot table name inference with custom pivot classes now pluralizes — set an explicit `$table` if you relied on the old singular name.
- `Manager::extend()` closures are now bound to the manager instance (`$this` changed) — capture prior objects via `use (...)`.
- Deserialized Eloquent collections (e.g. from queued jobs) now restore eager-loaded relations.
- `Str` custom factories (UUID/ULID/random) reset between tests automatically.
- Default password-reset mail subject changed from "Reset Password Notification" to "Reset your password" — update string-matching tests/translations.
- Queued notifications now honor `#[DeleteWhenMissingModels]` / `$deleteWhenMissingModels`.
- `symfony/polyfill-php85` may define global `array_first()`/`array_last()` on PHP < 8.5 — check for conflicts with `laravel/helpers` or custom globals; prefer `Illuminate\Support\Arr` methods.

Full list with code samples: laravel/docs repo, `upgrade.md`, "Upgrading To 13.0 From 12.x" section (see Source of truth below for how to fetch). Laravel also ships an AI-assisted upgrade path via Laravel Boost ^2.0 (`/upgrade-laravel-v13` slash command) if the project already uses Boost.

### When to Use New Patterns vs Old

Mapped to this project's layered architecture (Presentation → Application → Domain, Infrastructure at the edges):

- **Attribute-based controller middleware/authorization (`#[Middleware]`, `#[Authorize]`)** — Presentation layer only. These attributes replace `Route::middleware(...)` chains and the static `middleware()` method on controllers, colocating cross-cutting HTTP concerns with the action. `#[Authorize]` is sugar for the `can` middleware and still delegates to a Policy (Domain/Application boundary) — do not put authorization *logic* in the attribute, only the policy ability reference. Prefer attributes when the middleware/policy check is fixed per-route; keep dynamic/conditional authorization in an explicit use case call if the ability depends on runtime state not expressible as a route parameter.
- **JSON:API resources (`JsonApiResource`)** — Presentation layer, same tier as existing `JsonResource` classes. Use when the consumer explicitly expects JSON:API (sparse fieldsets, `included`, relationship links) — typically public/partner APIs. For internal-only or simple REST responses, keep plain `JsonResource`/`ResourceCollection` to avoid the added envelope overhead. Never let `JsonApiResource` attribute/relationship maps reach into Domain — map from Eloquent models (Infrastructure) or DTOs (Application) at construction, same as any other resource.
- **Queue attributes (`#[Tries]`, `#[Backoff]`, `#[Timeout]`, `#[FailOnTimeout]`, `#[UniqueFor]`, `#[DebounceFor]`)** — belong on the Job class itself (Infrastructure/Application boundary for dispatch mechanics), not Domain. They replace public properties/methods (`$tries`, `backoff()`, `$timeout`) — prefer attributes for new jobs for consistency; leave existing property-based jobs as-is unless touching the file anyway (avoid drive-by refactors).
- **`Queue::route(...)`** — Composition Root concern (register in a service provider's `boot()`), not scattered per-dispatch-site `onQueue()`/`onConnection()` calls. Use it when a job class should *always* route to a given queue/connection regardless of call site; keep per-call `onQueue()` for one-off overrides.
- **AI SDK (`Laravel\Ai\*`)** — treat as an external integration: wrap calls behind an Application-layer port (e.g. `AiAgentPort`) with Infrastructure adapter implementing it, so Domain/Application stay testable without hitting a real provider. Don't call `SalesCoach::make()` or `Image::of()` directly from controllers if the project already has ports/adapters conventions for other external services.
- **`Cache::touch()`** — fine to call directly from Application/Infrastructure services wherever cache TTL extension is needed; it's a low-level primitive like `Cache::put()`, no wrapping needed.
- **`PreventRequestForgery` origin-only mode** — Composition Root (`bootstrap/app.php`) decision. Only enable `originOnly: true` after confirming the app is HTTPS-only in all environments (the header requires TLS) and after auditing any legitimate cross-site POST flows (webhooks should already be excluded via `except`).
- **Vector/semantic search (`whereVectorSimilarTo`, embeddings)** — Infrastructure/query concern. Keep raw vector query builder calls inside a Repository or dedicated search service; expose a plain Domain-friendly method (e.g. `SearchRepository::findSimilar(string $query): Collection`) rather than leaking `DB::table()->whereVectorSimilarTo()` into Application/Domain code.

### Verification (for Laravel 13)

Do not trust memorized Laravel version behavior — confirm against the actual project before relying on any of the above:

```shell
php artisan --version
composer show laravel/framework | grep versions
grep '"laravel/framework"' composer.json
php -v   # must be >= 8.3 for Laravel 13
```

If the installed version is `^12.x` or lower, none of the "What's New" section applies — diff the laravel/docs repo against branch `12.x` instead of assuming (see Source of truth below for retrieval).

### Source of truth (Laravel 13 reference only)

Canonical source for Laravel 13: `https://github.com/laravel/docs` repository, branch `13.x`. Relevant files by topic:

- `releases.md` — `## Laravel 13` section, one-paragraph summaries of every headline feature.
- `upgrade.md` — full 12.x → 13.x breaking-change list with code samples and "Likelihood Of Impact" ratings.
- `ai-sdk.md` — Laravel AI SDK (text, agents, tools, embeddings, audio, images, vector stores).
- `mcp.md` — first-party MCP server support.
- `eloquent-resources.md` — JSON:API resources (`#jsonapi-resources`), `PreserveKeys`/`Collects` attributes.
- `controllers.md` — `#[Middleware]`, `#[WithoutMiddleware]`, `#[Authorize]` attributes.
- `queues.md` — `Queue::route()`, all new job attributes (`Tries`, `Backoff`, `Timeout`, `FailOnTimeout`, `UniqueFor`, `DebounceFor`, `MaxExceptions`, `DeleteWhenMissingModels`).
- `csrf.md` — `PreventRequestForgery`, `Sec-Fetch-Site` origin verification, `preventRequestForgery()` config method.
- `cache.md` — `Cache::touch()`, `serializable_classes` hardening.
- `search.md`, `queries.md` — semantic/vector search (`whereVectorSimilarTo`, embeddings-backed search).
- `validation.md`, `events.md`, `broadcasting.md`, `container.md`, `notifications.md`, `mail.md`, `redis.md`, `vite.md` — check for additional attribute-based or config changes when working in those areas; diff against branch `12.x` first.

#### Fetching docs (Laravel 13 reference)

Choose one approach:

**Option A: Use an existing local clone (if you have one)**
```shell
# If you already have a local clone of laravel/docs, update it and diff:
cd <path-to-your-local-laravel-docs-clone>
git fetch origin
git diff origin/12.x origin/13.x -- <file>.md
```

**Option B: Clone on demand**
```shell
# Clone just the 13.x branch to a temporary location:
git clone --branch 13.x --depth 1 https://github.com/laravel/docs.git /tmp/laravel-docs-13

# Then diff against 12.x:
git -C /tmp/laravel-docs-13 fetch origin 12.x:12.x
git -C /tmp/laravel-docs-13 diff 12.x origin/13.x -- <file>.md
```

**Option C: Fetch via GitHub raw URL (no clone)**
- Latest file on branch 13.x: `https://raw.githubusercontent.com/laravel/docs/13.x/<file>.md`
- To compare in browser, use GitHub's compare UI: `https://github.com/laravel/docs/compare/12.x...13.x -- <file>.md`

**Option D: Browse rendered HTML docs**
- Rendered page on laravel.com: `https://laravel.com/framework/docs/13.x/<page>` (e.g. `https://laravel.com/framework/docs/13.x/releases`, `https://laravel.com/framework/docs/13.x/upgrade`)
- Anchor fragments (e.g. `#jsonapi-resources`, `#semantic-vector-search`) work the same way as in the `.md` file.
- **Best for:** Direct human-readable reading and citation of a single page. **For diffing:** Prefer Option C (raw markdown / GitHub compare) since HTML is not ideal for version diffs.
