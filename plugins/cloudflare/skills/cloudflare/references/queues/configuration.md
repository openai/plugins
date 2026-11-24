# Queues Configuration

Fetch the relevant guide before writing configuration or running CLI commands. Check the project's Wrangler version and compatibility date when adapting examples.

| Task | Documentation |
|------|---------------|
| Create a queue and connect producer and consumer Workers | [Getting started](https://developers.cloudflare.com/queues/get-started/index.md) |
| Configure producer bindings, Worker consumers, retention, and concurrency settings | [Configure Queues](https://developers.cloudflare.com/queues/configuration/configure-queues/index.md) |
| Configure an external HTTP consumer and its visibility timeout | [Pull consumers](https://developers.cloudflare.com/queues/configuration/pull-consumers/index.md) |
| Choose batching, retry policy, or delivery delays | [Batching, retries, and delays](https://developers.cloudflare.com/queues/configuration/batching-retries/index.md) |
| Preserve messages that exhaust retries | [Dead Letter Queues](https://developers.cloudflare.com/queues/configuration/dead-letter-queues/index.md) |
| Set consumer scaling for downstream capacity | [Consumer concurrency](https://developers.cloudflare.com/queues/configuration/consumer-concurrency/index.md) |
| Choose content types and type Worker messages | [JavaScript APIs](https://developers.cloudflare.com/queues/configuration/javascript-apis/index.md) |
| Create, update, attach, remove, or delete queues and consumers | [Wrangler commands](https://developers.cloudflare.com/queues/reference/wrangler-commands/index.md) |
| Pause delivery, resume it, or purge messages | [Pause and purge](https://developers.cloudflare.com/queues/configuration/pause-purge/index.md) |
| Develop and test producers and consumers locally | [Local development](https://developers.cloudflare.com/queues/configuration/local-development/index.md) |

Choose push or pull based on where processing runs, then select an encoding supported by that consumer. Tune batching for acceptable latency and downstream write capacity. Decide how failed messages will be inspected and replayed before configuring a dead-letter queue.

Fetch [limits](https://developers.cloudflare.com/queues/platform/limits/index.md) and [pricing](https://developers.cloudflare.com/queues/platform/pricing/index.md) for the account's plan before selecting retention, delays, or capacity. Do not reuse numeric settings from unrelated examples.
