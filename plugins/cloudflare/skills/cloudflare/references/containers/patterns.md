# Containers patterns

Choose instance identity based on the workload: per-user/session or per-job identities for affinity, one shared identity for a singleton, and interchangeable instances for stateless requests. Read [scaling and routing](https://developers.cloudflare.com/containers/configuration/scaling-and-routing/index.md) for current helpers and scaling behavior before implementing that choice.

| Task | Documentation |
| --- | --- |
| Distribute requests across stateless instances | [Stateless instances example](https://developers.cloudflare.com/containers/examples/stateless/index.md) |
| Forward WebSocket connections | [WebSocket example](https://developers.cloudflare.com/containers/examples/websocket/index.md) |
| React to lifecycle changes | [Status hooks example](https://developers.cloudflare.com/containers/examples/status-hooks/index.md) |
| Handle shutdown and persist data across restarts | [Container lifecycle](https://developers.cloudflare.com/containers/concepts/architecture/index.md) and [Container interface](https://developers.cloudflare.com/containers/api/container-class/index.md) |
| Keep long operations active or schedule callbacks | [Activity renewal](https://developers.cloudflare.com/containers/api/container-class/index.md#renewactivitytimeout) and [scheduling](https://developers.cloudflare.com/containers/api/container-class/index.md#scheduling) |
| Start containers on a cron schedule | [Cron container example](https://developers.cloudflare.com/containers/examples/cron/index.md) |
| Route requests to multiple ports | [Request methods](https://developers.cloudflare.com/containers/api/container-class/index.md#request-methods) and [utility functions](https://developers.cloudflare.com/containers/api/container-class/index.md#utility-functions) |
| Access Workers bindings from the container | [Connect to Workers and bindings](https://developers.cloudflare.com/containers/configuration/workers-connections/index.md) |

## Workflows and Queues

For multi-step orchestration, combine the [Workflows Workers API](https://developers.cloudflare.com/workflows/build/workers-api/index.md) with the [Container API](api.md). For queue-driven jobs, read the [Queues consumer API](https://developers.cloudflare.com/queues/configuration/javascript-apis/index.md#consumer) and [acknowledgement and retry behavior](https://developers.cloudflare.com/queues/configuration/batching-retries/index.md#explicit-acknowledgement-and-retries) alongside the Container API. These pages document the component APIs; they are not end-to-end Container integration examples.
