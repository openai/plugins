# Observability Configuration

Fetch the relevant guide before configuring the selected Worker and deployment environment.

| Task | Maintained documentation |
| --- | --- |
| Enable persisted logs, structured JSON logging, and sampling | [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/index.md) |
| Enable traces and set their sampling independently of logs | [Workers Traces](https://developers.cloudflare.com/workers/observability/traces/index.md) |
| Configure a named deployment environment | [Wrangler environments](https://developers.cloudflare.com/workers/wrangler/environments/index.md) and the environment example in [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/index.md) |
| Bind an Analytics Engine dataset and write its first data point | [Analytics Engine get started](https://developers.cloudflare.com/analytics/analytics-engine/get-started/index.md) |
| Connect a producer to a Tail Worker | [Configure Tail Workers](https://developers.cloudflare.com/workers/observability/logs/tail-workers/index.md) |
| Create a Logpush job, configure access, and enable Worker log delivery | [Workers Logpush](https://developers.cloudflare.com/workers/observability/logs/logpush/index.md) |
| Configure OTLP destinations, authentication, and local persistence | [OpenTelemetry export](https://developers.cloudflare.com/observability/export/opentelemetry/index.md) for destinations and authentication, and [Workers OpenTelemetry export](https://developers.cloudflare.com/workers/observability/opentelemetry-export/index.md) for Wrangler destinations and `persist` |

## Setup decisions

- Confirm which account, Worker, and environment will emit telemetry, then deploy that configuration and generate representative traffic.
- Decide log and trace sampling separately. Increasing sampling during an investigation changes volume and cost; restore the intended operational settings afterwards.
- For Tail Workers, configure the consumer relationship on the producer Worker; use the guide for deployment order and the handler contract.
- Choose whether to persist data in Cloudflare as well as exporting it. Verify destination names, supported signal types, and credentials using the export guides above.
- Use stable structured fields and redact secrets and unnecessary personal data before emission. Configure development and production collection intentionally.

See [gotchas.md](gotchas.md) when configured telemetry is missing.
