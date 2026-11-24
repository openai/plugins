# Tail Workers Configuration

Identify the producer Worker and consumer Worker as separate deployment resources before changing their configuration.

| Task | Documentation |
| --- | --- |
| Connect a producer to a Tail Worker | [Configure Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md#configure-tail-workers) |
| Configure environments and resource bindings | [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/index.md) |
| Configure destination credentials | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |
| Use built-in telemetry destinations instead | [OpenTelemetry export](https://developers.cloudflare.com/observability/export/opentelemetry/index.md) |
| Check availability and billing model | [Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md) |
| Check runtime capacity | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/index.md) |
| Check the handler required by the consumer | [Tail handler](https://developers.cloudflare.com/workers/runtime-apis/handlers/tail/index.md) |

Confirm which project owns each deployment and which environment the destination belongs to. Verify a known producer request reaches the intended destination before expanding coverage. See [api.md](./api.md) for payload handling and [gotchas.md](./gotchas.md) for investigation.
