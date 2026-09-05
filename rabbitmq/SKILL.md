---
name: RabbitMQ (Message Broker)
description: RabbitMQ as a message broker — exchange types (direct/topic/fanout/headers), queues/bindings/routing keys, publisher/consumer patterns with manual ack and prefetch/QoS, dead-letter exchanges for retry, docker-compose setup with management UI, idempotent consumer design, and common pitfalls (unacked pileup, missing DLX, durability vs persistence).
---

# RabbitMQ (Message Broker)

RabbitMQ as the message broker for async work, event fan-out, and decoupling
producers from consumers.

## Core Concepts

| Concept | Meaning |
|---|---|
| Exchange | Receives messages from producers, routes them to queues based on type + routing key |
| Queue | Buffer that holds messages until a consumer acks them |
| Binding | Rule connecting an exchange to a queue (optionally with a routing key pattern) |
| Routing key | String attached to a message, matched against bindings to decide delivery |

### Exchange Types

- **direct** — routes to queues whose binding key exactly matches the routing key.
  Use for point-to-point task routing (e.g. `order.created` → one queue).
- **topic** — routes by pattern (`*` = one word, `#` = zero or more words), e.g.
  binding `order.*.created` matches routing key `order.eu.created`. Use for
  selective fan-out by category.
- **fanout** — broadcasts to every bound queue, ignores routing key entirely. Use
  for "notify all interested consumers" (cache invalidation broadcast, etc.).
- **headers** — routes by message header match instead of routing key. Rare;
  prefer topic exchanges unless headers are genuinely more natural.

```
producer --routing_key--> [exchange] --binding--> [queue] --> consumer
```

## Publisher

```ts
import amqplib from "amqplib";

const conn = await amqplib.connect(process.env.RABBITMQ_URL!);
const channel = await conn.createChannel();

const EXCHANGE = "orders";
await channel.assertExchange(EXCHANGE, "topic", { durable: true });

function publishOrderEvent(routingKey: string, payload: unknown) {
  channel.publish(
    EXCHANGE,
    routingKey, // e.g. "order.created"
    Buffer.from(JSON.stringify(payload)),
    { persistent: true, contentType: "application/json" },
  );
}
```

- `durable: true` on the exchange/queue survives broker restart (definitions only).
- `persistent: true` on the message tells RabbitMQ to write it to disk — required
  in addition to `durable` queues, otherwise messages are lost on broker restart
  even though the queue itself survives (see pitfalls below).

## Consumer with Manual Ack + Prefetch

Never use `noAck: true` for anything where losing a message on crash matters.
Manual ack + prefetch (QoS) is the default-safe pattern.

```ts
const QUEUE = "orders.process";
await channel.assertQueue(QUEUE, { durable: true });
await channel.bindQueue(QUEUE, EXCHANGE, "order.*");

// Prefetch limits how many unacked messages this consumer can hold at once —
// prevents one slow consumer from being flooded and running out of memory.
await channel.prefetch(10);

channel.consume(QUEUE, async (msg) => {
  if (!msg) return;
  try {
    const payload = JSON.parse(msg.content.toString());
    await processOrder(payload);
    channel.ack(msg);
  } catch (err) {
    console.error("[consumer] processing failed", err);
    // requeue=false sends it to DLX instead of looping forever on the same message
    channel.nack(msg, false, false);
  }
}, { noAck: false });
```

## Dead-Letter Exchange (DLX) for Retry/Failure Handling

Without a DLX, `nack`/`reject` with `requeue: false` silently drops the message.
Always attach a DLX so failed messages land somewhere inspectable instead of
disappearing.

```ts
// 1. Dead-letter exchange + queue (where failed messages go)
await channel.assertExchange("orders.dlx", "fanout", { durable: true });
await channel.assertQueue("orders.dead", { durable: true });
await channel.bindQueue("orders.dead", "orders.dlx", "");

// 2. Main queue declares the DLX as its dead-letter target
await channel.assertQueue(QUEUE, {
  durable: true,
  arguments: {
    "x-dead-letter-exchange": "orders.dlx",
    // optional: delay before retry via a second hop back to the main exchange
    "x-message-ttl": 30000,
  },
});
```

Retry pattern: dead-lettered message sits in a delay queue with a TTL, and once it
expires it dead-letters *again* back into the original exchange — giving a
"retry after N seconds" without a external scheduler. Cap retry count using a
header counter to avoid infinite retry loops.

## RabbitMQ in docker-compose

```yaml
services:
  rabbitmq:
    image: rabbitmq:3.13-management-alpine
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI (http://localhost:15672)
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmqdata:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  rabbitmqdata:
```

- The `-management` image tag ships the web UI/HTTP API plugin — use the plain
  `rabbitmq:3.13-alpine` tag in production if you don't need the UI exposed.
- Never expose `15672` publicly without a reverse proxy + auth in front — it's a
  full admin UI over your broker.

## Idempotent Consumer Design

At-least-once delivery is the default guarantee — a message can be redelivered
(consumer crash after processing but before ack, network blip, etc.). Consumers
must tolerate processing the same message twice.

```ts
async function processOrder(payload: { orderId: string }) {
  // Use a unique constraint / upsert keyed on a dedupe id, not a plain insert
  await db.processedEvent.upsert({
    where: { orderId: payload.orderId },
    create: { orderId: payload.orderId, processedAt: new Date() },
    update: {}, // no-op if already processed
  });
}
```

## Common Pitfalls

| Pitfall | Cause | Mitigation |
|---|---|---|
| Unacked message pileup | Consumer never acks/nacks (crash, unhandled exception outside try/catch, no prefetch limit) | Always ack/nack in a `finally`-equivalent path; set `prefetch` so a stuck consumer can't hold unlimited messages |
| Missing DLX → message loss | `nack(msg, false, false)` with no DLX configured silently discards the message | Always assert + bind a DLX before rejecting without requeue |
| Durability vs persistence confusion | Queue declared `durable: true` but messages published without `persistent: true` — messages still lost on broker restart | Both flags are required together: durable queue AND persistent message |
| Infinite retry loop | DLX retry hop back to original queue with no retry counter | Track attempt count in a message header; dead-letter to a final "failed" queue after N attempts |
| Consumer processes duplicate messages | At-least-once delivery redelivers on crash/requeue | Design consumers to be idempotent (dedupe key / upsert) |

## สรุป

1. Exchange types: direct (exact match), topic (pattern), fanout (broadcast), headers (rare)
2. Manual ack + `prefetch` — never `noAck: true` for anything that matters
3. Durable queue + persistent message — both required to survive broker restart
4. Always attach a DLX before `nack(..., false)` — otherwise failed messages vanish
5. DLX + TTL hop = retry-with-delay pattern; cap attempts via header counter
6. Consumers must be idempotent — at-least-once delivery means duplicates happen
7. docker-compose: management image for UI, healthcheck via `rabbitmq-diagnostics ping`, never expose 15672 publicly unprotected
