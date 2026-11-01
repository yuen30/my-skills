---
name: rabbitmq
description: "RabbitMQ message broker: exchanges, queues, manual ack/prefetch, dead-letter retry, idempotent consumers, docker-compose setup. Use when adding async jobs or event fan-out with RabbitMQ, amqp consumers/publishers, DLX, or unacked-message issues."
---

# RabbitMQ (Message Broker)

## Rules

- Default `channel.prefetch(10)` — our standard is 10, not 1 or 2; go lower only for slow/heavy messages and say why.
- Exchange choice: direct for point-to-point tasks, topic for selective fan-out (default over headers), fanout for broadcast.
- Durability needs BOTH `durable: true` (exchange/queue) AND `persistent: true` (message) — either alone still loses messages on restart.
- Consumers: manual ack (`noAck: false`), never `noAck: true` where loss matters; set `channel.prefetch` so a stuck consumer can't hold unlimited messages; ack/nack on every path (incl. exceptions outside try/catch).
- Failure: `nack(msg, false, false)` (no requeue, avoids poison-message loops) and always declare + bind a DLX first — without one the message is silently dropped.
- Retry: dead-letter into a delay queue (`x-message-ttl`) whose own DLX routes back to the original exchange; count attempts in a header and dead-letter to a final `*.dead` queue after N tries (otherwise infinite loop).
- Delivery is at-least-once: consumers must be idempotent (upsert/unique constraint on a dedupe id, not plain insert).

```ts
await channel.assertQueue("orders.process", {
  durable: true,
  arguments: { "x-dead-letter-exchange": "orders.dlx" },
});
await channel.prefetch(10);
channel.consume("orders.process", async (msg) => {
  if (!msg) return;
  try { await handle(msg); channel.ack(msg); }
  catch { channel.nack(msg, false, false); }
}, { noAck: false });
```

## docker-compose

- Image `rabbitmq:3.13-management-alpine` for dev; plain `rabbitmq:3.13-alpine` in prod unless UI needed.
- Credentials via `RABBITMQ_DEFAULT_USER/PASS` from env; volume `/var/lib/rabbitmq`; healthcheck `rabbitmq-diagnostics -q ping` (interval 10s); `restart: unless-stopped`.
- Never expose `15672` publicly without reverse proxy + auth.
