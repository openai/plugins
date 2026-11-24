# Cloudflare Observability

Use this reference to choose a telemetry signal and find the maintained implementation guide. Fetch the linked documentation before writing configuration, queries, or export code; it is the source of truth for APIs, availability, retention, limits, and pricing.

## Choose a signal

| Need | Start here |
| --- | --- |
| Store, search, and investigate historical Worker logs | [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/index.md) |
| Watch a deployment or reproduce an issue live | [Real-time logs and Wrangler tail](https://developers.cloudflare.com/workers/observability/logs/real-time-logs/index.md) |
| Understand request flows and dependency latency | [Workers Traces](https://developers.cloudflare.com/workers/observability/traces/index.md) |
| Monitor built-in request, error, and CPU metrics | [Metrics and analytics](https://developers.cloudflare.com/workers/observability/metrics-and-analytics/index.md) |
| Record custom events and tenant-level usage for SQL analysis | [Analytics Engine](https://developers.cloudflare.com/analytics/analytics-engine/get-started/index.md) |
| Export logs and traces to an observability provider | [OpenTelemetry export](https://developers.cloudflare.com/observability/export/opentelemetry/index.md) |
| Apply custom filtering, transformation, or delivery logic | [Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md) |
| Deliver Workers Trace Events to a supported log storage destination | [Workers Logpush](https://developers.cloudflare.com/workers/observability/logs/logpush/index.md) |

Workers Logs supports retained historical data; live tailing is a separate debugging workflow. Choose persistence, sampling, and export destinations deliberately rather than assuming that every signal is stored or included without usage charges.

## Load only what the task needs

- [configuration.md](configuration.md): enable collection, bindings, environments, and exports.
- [api.md](api.md): logging, telemetry types, SQL, GraphQL, and Logpush APIs.
- [patterns.md](patterns.md): billing, performance, errors, tenant tracking, and export decisions.
- [gotchas.md](gotchas.md): missing data, sampling, timing, privacy, and cost checks.

For broader product tasks, see [Analytics Engine docs](https://developers.cloudflare.com/analytics/analytics-engine/index.md), [GraphQL Analytics API docs](https://developers.cloudflare.com/analytics/graphql-api/index.md), and [Tail Workers](../tail-workers/README.md).
