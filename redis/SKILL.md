---
name: Redis (Cache Layer)
description: Redis as a cache layer — connection setup for Node (ioredis/node-redis), Python (redis-py), Go (go-redis), cache-aside pattern, TTL strategy, invalidation/tagging, distributed locks, pub/sub, docker-compose setup, and common pitfalls (stampede, hot keys, unbounded growth).
---

# Redis (Cache Layer)

Redis as a cache layer in front of a primary datastore (PostgreSQL, etc.) — not as a
source of truth.

## Connection Setup

### Node.js — ioredis (recommended over node-redis for cluster/sentinel support)

```ts
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL ?? "redis://localhost:6379", {
  maxRetriesPerRequest: 3,
  enableAutoPipelining: true,
});

redis.on("error", (err) => console.error("[redis] connection error", err));
```

### Node.js — node-redis (official client)

```ts
import { createClient } from "redis";

const redis = createClient({ url: process.env.REDIS_URL });
redis.on("error", (err) => console.error("[redis] connection error", err));
await redis.connect();
```

### Python — redis-py

```python
import redis.asyncio as redis

client = redis.Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True,
    socket_timeout=3,
)
```

### Go — go-redis

```go
rdb := redis.NewClient(&redis.Options{
    Addr:         os.Getenv("REDIS_ADDR"), // "localhost:6379"
    Password:     os.Getenv("REDIS_PASSWORD"),
    DB:           0,
    DialTimeout:  3 * time.Second,
    ReadTimeout:  1 * time.Second,
})
if err := rdb.Ping(ctx).Err(); err != nil {
    log.Fatalf("redis ping failed: %v", err)
}
```

## Cache-Aside Pattern (most common)

Read: check cache → miss → read source of truth → populate cache → return.
Write: write source of truth → invalidate (or update) cache key.

```ts
async function getUser(id: string) {
  const cacheKey = `user:${id}`;
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const user = await db.user.findUnique({ where: { id } });
  if (!user) return null;

  await redis.set(cacheKey, JSON.stringify(user), "EX", 300); // 5 min TTL
  return user;
}

async function updateUser(id: string, data: Partial<User>) {
  const user = await db.user.update({ where: { id }, data });
  await redis.del(`user:${id}`); // invalidate, don't try to update in place
  return user;
}
```

## TTL Strategy

- Always set a TTL on cache entries — never cache without expiry unless the key is
  actively invalidated on every write path.
- Use short TTLs (seconds–minutes) for frequently-changing data, longer TTLs
  (hours) for rarely-changing reference data.
- Add jitter to TTLs for keys populated in bulk to avoid synchronized mass expiry:

```ts
const ttl = 300 + Math.floor(Math.random() * 60); // 300-360s
await redis.set(cacheKey, value, "EX", ttl);
```

## Invalidation & Tagging

Redis has no native cache tags. Emulate with a `SET` per tag holding member keys:

```ts
async function setWithTags(key: string, value: string, tags: string[], ttl: number) {
  const pipeline = redis.pipeline();
  pipeline.set(key, value, "EX", ttl);
  for (const tag of tags) {
    pipeline.sadd(`tag:${tag}`, key);
    pipeline.expire(`tag:${tag}`, ttl + 60);
  }
  await pipeline.exec();
}

async function invalidateTag(tag: string) {
  const keys = await redis.smembers(`tag:${tag}`);
  if (keys.length) await redis.del(...keys);
  await redis.del(`tag:${tag}`);
}
```

## Distributed Locks — `SET NX PX`

Use for preventing duplicate work across instances (e.g. one worker rebuilding a
cache entry). For anything beyond simple mutual exclusion, use a maintained
implementation (Redlock) instead of hand-rolling multi-node consensus.

```ts
async function withLock<T>(key: string, ttlMs: number, fn: () => Promise<T>) {
  const token = crypto.randomUUID();
  const acquired = await redis.set(`lock:${key}`, token, "PX", ttlMs, "NX");
  if (!acquired) throw new Error("could not acquire lock");

  try {
    return await fn();
  } finally {
    // release only if we still own it (Lua for atomicity)
    await redis.eval(
      `if redis.call("get", KEYS[1]) == ARGV[1] then return redis.call("del", KEYS[1]) else return 0 end`,
      1,
      `lock:${key}`,
      token,
    );
  }
}
```

## Pub/Sub Basics

Fire-and-forget messaging — no persistence, no delivery guarantee, no queue
semantics. Use RabbitMQ (see `rabbitmq` skill) when you need durability, retry, or
guaranteed delivery.

```ts
// Subscriber
const sub = redis.duplicate();
await sub.subscribe("events:user-updated");
sub.on("message", (channel, message) => {
  console.log(`[${channel}]`, JSON.parse(message));
});

// Publisher
await redis.publish("events:user-updated", JSON.stringify({ id: "123" }));
```

## Redis in docker-compose

```yaml
services:
  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes", "--requirepass", "${REDIS_PASSWORD}"]
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped

volumes:
  redisdata:
```

- `--appendonly yes` enables AOF persistence — needed if Redis also holds
  short-lived state you can't afford to lose on restart (locks, rate-limit
  counters). Pure cache-only deployments can skip persistence entirely and let a
  restart mean a cold cache.
- Always set `requirepass` (or ACLs) — don't expose Redis with no auth, even on an
  internal network.

## Common Pitfalls

| Pitfall | Cause | Mitigation |
|---|---|---|
| Cache stampede | TTL expiry + high concurrent traffic → many requests miss simultaneously and hit the DB at once | Lock-based single-flight rebuild, or serve stale-while-revalidate, or TTL jitter |
| Hot keys | One key (e.g. a viral post) receives disproportionate traffic, saturating a single Redis shard | Client-side/local in-memory cache for the hottest keys, or replicate the key under random suffixes and read one at random |
| Unbounded key growth | Keys created without TTL or without a bound (e.g. per-session, per-request keys) | Always set TTL; use `SCAN` + monitoring (`redis-cli --bigkeys`) to audit; set `maxmemory` + eviction policy (`allkeys-lru`) as a safety net |
| Blocking commands on shared instance | `KEYS *`, unbounded `SMEMBERS`/`LRANGE` on large collections | Use `SCAN` instead of `KEYS`; cap collection sizes; use `LPOS`/`SSCAN` for large sets |

## When NOT to Use Redis as Source of Truth

- No durability guarantee comparable to a relational DB even with AOF (`appendfsync
  everysec` can lose up to 1s of writes on crash).
- No relational integrity, foreign keys, or transactional joins across entities.
- Redis persistence config (RDB/AOF) is for recovery speed, not for treating Redis
  as the primary datastore for business-critical records — use PostgreSQL for that
  and Redis only as an accelerator/derived cache.

## สรุป

1. Cache-aside: read cache → miss → read DB → populate cache → return
2. Always set TTL (with jitter for bulk-populated keys) — never cache forever
3. Invalidate on write, don't try to keep cache in sync in place
4. `SET NX PX` for distributed locks; release only if token matches (Lua)
5. Pub/sub is fire-and-forget — use RabbitMQ when you need durability
6. docker-compose: `requirepass` + healthcheck + volume for persistence if state matters
7. Watch for cache stampede, hot keys, unbounded key growth
8. Redis accelerates a source of truth — it is not one
