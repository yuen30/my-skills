---
name: redis
description: "Redis as a cache layer: cache-aside, TTL, invalidation, distributed locks, pub/sub, client setup for Node, Python, Go. Use when adding Redis caching, ioredis/redis-py/go-redis, locks, cache stampede issues, or Redis in docker-compose."
---

# Redis (Cache Layer)

Cache in front of the primary datastore (PostgreSQL etc.) — never the source of truth (AOF `everysec` can lose ~1s; no relational integrity).

## Rules

- Node: use **ioredis** over node-redis (cluster/sentinel support); set `maxRetriesPerRequest: 3`, `enableAutoPipelining: true`, and an `error` listener. Always set client timeouts (py `socket_timeout`, go `Dial/ReadTimeout`) and ping at startup.
- Cache-aside: read cache -> miss -> DB -> `SET ... EX`; on write, update DB then `DEL` the key (invalidate, never update in place).
- Always set a TTL unless every write path invalidates. Add jitter (+0-20%) to bulk-populated keys.
- No native tags: emulate with a `SET tag:<name>` of member keys (`SADD` + `EXPIRE ttl+60` in a pipeline); invalidate = `SMEMBERS` -> `DEL` keys -> `DEL` tag.
- Locks: `SET lock:<k> <uuid> PX <ttl> NX`; release via Lua compare-token-then-`DEL` (never plain `DEL`). Beyond single-node mutual exclusion, use Redlock, don't hand-roll.
- Pub/sub is fire-and-forget (no persistence/queue semantics); use RabbitMQ when you need durability/retry. Subscribers need a `redis.duplicate()` connection.
- Never `KEYS *` or unbounded `SMEMBERS`/`LRANGE` — use `SCAN`/`SSCAN`, cap collection sizes.

## Pitfalls

- Stampede on expiry: lock-based single-flight rebuild, stale-while-revalidate, or TTL jitter.
- Hot key: local in-memory cache, or replicate under random suffixes and read one.
- Unbounded keys: audit with `redis-cli --bigkeys`; set `maxmemory` + `allkeys-lru` as a safety net.

## docker-compose

```yaml
redis:
  image: redis:7-alpine
  command: ["redis-server", "--appendonly", "yes", "--requirepass", "${REDIS_PASSWORD}"]
  volumes: [redisdata:/data]
  healthcheck: {test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"], interval: 5s, timeout: 3s, retries: 5}
  restart: unless-stopped
```

- Always `requirepass`/ACL, even on internal networks.
- `--appendonly yes` only if Redis holds state you can't lose (locks, rate counters); pure cache can skip persistence (restart = cold cache).
