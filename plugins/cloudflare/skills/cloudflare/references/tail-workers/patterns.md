# Tail Workers Processing Decisions

Define the destination contract and required event coverage before writing transformations.

| Task | Documentation |
| --- | --- |
| Export supported telemetry without a custom consumer | [OpenTelemetry export](https://developers.cloudflare.com/observability/export/opentelemetry/index.md) |
| Process and forward custom execution events | [Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md) |
| Aggregate metrics rather than retain individual events | [Analytics Engine from Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md#use-analytics-engine-for-aggregated-metrics) |
| Choose filters based on execution and request fields | [Tail handler](https://developers.cloudflare.com/workers/runtime-apis/handlers/tail/index.md) |
| Review sensitive request data handling | [TailRequest](https://developers.cloudflare.com/workers/runtime-apis/handlers/tail/index.md#tailrequest) |

Decide which producers, routes, failures, and successful requests each destination needs. If sampling is appropriate, specify how it affects the questions the data must answer. Minimize retained fields, test transformation and serialization against representative events, and check destination rejection behavior.

Keep producer identity when combining events from multiple Workers. Define how delivery failures become visible before adding fallback storage or batching infrastructure. See [configuration.md](./configuration.md) for deployment ownership.
