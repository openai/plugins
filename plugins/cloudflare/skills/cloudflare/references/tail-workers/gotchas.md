# Tail Workers Troubleshooting

Trace one known producer invocation through consumer execution and destination receipt to locate the failure.

| Task | Documentation |
| --- | --- |
| Consumer receives no events or producer setup fails | [Configure Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md#configure-tail-workers) |
| Async processing or event interpretation is incorrect | [Tail handler](https://developers.cloudflare.com/workers/runtime-apis/handlers/tail/index.md) |
| Filters confuse HTTP responses with execution failures | [TailItems](https://developers.cloudflare.com/workers/runtime-apis/handlers/tail/index.md#tailitems) |
| Request data is missing or unexpectedly retained | [TailRequest](https://developers.cloudflare.com/workers/runtime-apis/handlers/tail/index.md#tailrequest) |
| Inspect producer and consumer execution | [Real-time logs](https://developers.cloudflare.com/workers/observability/logs/real-time-logs/index.md) |
| Reconsider a custom exporter at higher volume | [OpenTelemetry export](https://developers.cloudflare.com/observability/export/opentelemetry/index.md) |

Verify producer configuration, consumer identity, and destination credentials independently. Include both handled error responses and thrown exceptions when checking filters. Make destination failures observable without exposing the payload or credentials in diagnostic logs. Do not infer retention, retries, or batch guarantees from an example.

See [api.md](./api.md) for data contracts and [patterns.md](./patterns.md) for destination decisions.
