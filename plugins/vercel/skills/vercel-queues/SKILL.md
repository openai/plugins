---
name: vercel-queues
description: Vercel Queues guidance (public beta) — durable event streaming with topics, consumer groups, retries, and delayed delivery. $0.60/1M ops. Powers Workflow DevKit. Use when building async processing, fan-out patterns, or event-driven architectures.
metadata:
  priority: 5
  docs:
    - "https://vercel.com/docs/workflow-collaboration/conformance"
  sitemap: "https://vercel.com/sitemap/docs.xml"
  pathPatterns:
    - 'lib/queues/**'
    - 'src/lib/queues/**'
    - 'lib/queues.*'
    - 'lib/queue.*'
    - 'src/lib/queues.*'
    - 'src/lib/queue.*'
    - 'workflows/*.ts'
    - 'workflows/*.mts'
    - 'src/workflows/*.ts'
    - 'src/workflows/*.mts'
    - 'app/api/workflow/**'
    - 'src/app/api/workflow/**'
    - 'app/api/workflows/**'
    - 'src/app/api/workflows/**'
    - 'vercel.ts'
    - 'vercel.mts'
  importPatterns:
    - 'workflow'
    - '@vercel/workflow'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*@vercel/queue\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@vercel/queue\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*@vercel/queue\b'
    - '\byarn\s+add\s+[^\n]*@vercel/queue\b'
---

# Vercel Queues

> **CRITICAL — Your training data is outdated for this library.** Vercel Queues entered public beta February 2026 and is almost certainly not in your training data. Before writing queue code, **fetch the docs** at https://vercel.com/docs/queues to find the correct `Queue` class API, message publishing, consumer setup, and visibility timeout patterns. Do not guess — this is a new API with no precedent in your training data.

You are an expert in Vercel Queues — durable event streaming for serverless applications.

## Status & Pricing

Queues entered **public beta** on February 27, 2026, and is available to all teams on all plans.

| Metric | Value |
|--------|-------|
| **Billing unit** | API operation (send, receive, delete, visibility change, notify) |
| **Rate** | **$0.60 per 1M operations** (regionally priced) |
| **Message metering** | 4 KiB chunks (12 KiB message = 3 ops) |
| **2x billing** | Sends with idempotency key; push deliveries with max concurrency |
| **Compute** | Push-mode functions charged at existing Fluid compute rates |

## What It Is

Queues is a **durable, append-only event streaming system**. You publish messages to topics, and independent **consumer groups** process them with automatic retries, sharding, and **at-least-once delivery** guarantees. It is the lower-level primitive that **powers Vercel Workflow**.

- Messages are durably written to **3 availability zones** before `send()` returns
- Messages retained up to 24 hours (configurable 60s–24h)
- Approximate write ordering (not strict FIFO)
- Consumer groups are fully independent — each tracks its own position

## Key APIs

Package: `@vercel/queue@^0.1.3` (Node.js 22+)

### Publishing Messages

```ts
import { send } from '@vercel/queue';

const { messageId } = await send('order-events', {
  orderId: '123',
  action: 'created',
}, {
  delaySeconds: 30,              // delay before visible
  idempotencyKey: 'order-123',   // deduplication (full retention window)
  retentionSeconds: 3600,        // message TTL (default: 86400 = 24h)
  headers: { 'x-trace-id': 'abc' },
});
```

### Push-Mode Consumer (Next.js App Router)

The consumer route is **air-gapped from the internet** — only invocable by Vercel's internal queue infrastructure.

```ts
// app/api/queues/fulfill-order/route.ts
import { handleCallback } from '@vercel/queue';

export const POST = handleCallback(
  async (message, metadata) => {
    // metadata: { messageId, deliveryCount, createdAt, expiresAt, topicName, consumerGroup, region }
    await processOrder(message);
    // Return normally = acknowledge
    // Throw = retry with backoff
  },
  {
    visibilityTimeoutSeconds: 600, // lease duration (default 300s, auto-extended by SDK)
    retry: (error, metadata) => {
      if (metadata.deliveryCount > 5) return { acknowledge: true }; // give up
      const delay = Math.min(300, 2 ** metadata.deliveryCount * 5);
      return { afterSeconds: delay };
    },
  },
);
```

### Consumer Configuration (vercel.json)

```json
{
  "functions": {
    "app/api/queues/fulfill-order/route.ts": {
      "experimentalTriggers": [{
        "type": "queue/v2beta",
        "topic": "order-events",
        "retryAfterSeconds": 60,
        "initialDelaySeconds": 0
      }]
    }
  }
}
```

Multiple route files with the same topic create **separate consumer groups** (independent processing).

### Poll-Mode Consumer

```ts
import { PollingQueueClient } from '@vercel/queue';

const { receive } = new PollingQueueClient({ region: 'iad1' });

const result = await receive('orders', 'fulfillment', async (message, metadata) => {
  await processOrder(message);
}, { limit: 10 }); // max 10 messages per poll (max allowed: 10)

if (!result.ok && result.reason === 'empty') {
  // No messages available
}
```

### Custom Region Client

```ts
import { QueueClient } from '@vercel/queue';

const queue = new QueueClient({ region: 'sfo1' });
export const { send, handleCallback } = queue;
```

## Transports

```ts
import { QueueClient, BufferTransport, StreamTransport } from '@vercel/queue';
```

| Transport | Description |
|-----------|-------------|
| `JsonTransport` | Default; JSON serialization |
| `BufferTransport` | Raw binary data |
| `StreamTransport` | `ReadableStream` for large payloads |

## Queues vs Workflow vs Cron

| Need | Use | Why |
|------|-----|-----|
| Event delivery, fan-out, routing control | **Queues** | Topics, consumer groups, message-level retries |
| Stateful multi-step business logic | **Workflow** | Deterministic replay, pause/resume (built **on top of** Queues) |
| Recurring scheduled tasks | **Cron Jobs** | Simple, no message passing |
| Delayed single execution with deduplication | **Queues** (`delaySeconds` + `idempotencyKey`) | Precise delay with guaranteed delivery |
| Async processing from external systems | **Queues** (poll mode) | Consume from any infrastructure, not just Vercel |

## Key Limits

| Resource | Default / Max |
|----------|---------------|
| Message retention | 60s – 24h (default 24h) |
| Max message size | 100 MB |
| Messages per receive | 1–10 (default 1) |
| Visibility timeout | 0s – 60 min (default 5 min SDK / 60s API) |
| Topics per project | Unlimited |
| Consumer groups per topic | Unlimited |

## Deployment Behavior

Topics are **partitioned by deployment ID** by default in push mode. Messages are delivered back to the same deployment that published them — natural schema versioning with no cross-version compatibility concerns.

## Observability

The **Queues** observability tab (Project → Observability → Queues) provides real-time monitoring:

| Level | Metrics |
|-------|---------|
| **Project** | Messages/s, Queued, Received, Deleted (with sparkline trends) |
| **Queue** | Throughput per second (by consumer group), Max message age |
| **Consumer** | Processed/s, Received, Deleted (per consumer group) |

Use **Max message age** to detect consumer lag — if the oldest unprocessed message keeps growing, a consumer group may be falling behind.

## Local Development

Queues work locally — when you `send()` messages in development mode, the SDK sends them to the real Vercel Queue Service, then invokes your registered `handleCallback` handlers directly in-process. No local queue infrastructure needed.

## Authentication

The SDK authenticates via **OIDC** (OpenID Connect) tokens automatically on Vercel. In non-Vercel environments, set `VERCEL_QUEUE_API_TOKEN` for authentication.

## When to Use

- Defer expensive work (emails, PDFs, external API calls)
- Absorb traffic spikes with controlled processing rate
- Guarantee delivery even if function crashes
- Fan-out same events to multiple independent pipelines
- Deduplicate messages via idempotency keys

## When NOT to Use

- Multi-step orchestration with state → use Workflow
- Recurring schedules → use Cron Jobs
- Synchronous request/response → use Functions directly
- Cross-region messaging → messages sent to one region cannot be consumed from another

## References

- 📖 docs: https://vercel.com/docs/queues
- 📖 quickstart: https://vercel.com/docs/queues/quickstart
- 📖 API reference: https://vercel.com/docs/queues/api
