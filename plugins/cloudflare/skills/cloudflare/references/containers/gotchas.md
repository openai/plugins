# Containers troubleshooting

Use the current documentation to diagnose behavior instead of relying on copied timeout values, resource limits, or lifecycle recipes.

| Symptom or concern | Documentation to read |
| --- | --- |
| Startup timeout or unavailable port | [Start and stop](https://developers.cloudflare.com/containers/api/container-class/index.md#start-and-stop), [Container properties](https://developers.cloudflare.com/containers/api/container-class/index.md#properties), and [first-deploy provisioning](https://developers.cloudflare.com/containers/get-started/index.md) |
| WebSocket forwarding fails | [WebSocket example](https://developers.cloudflare.com/containers/examples/websocket/index.md) and [request methods](https://developers.cloudflare.com/containers/api/container-class/index.md#request-methods) |
| Background work stops on idle expiry | [Activity renewal](https://developers.cloudflare.com/containers/api/container-class/index.md#renewactivitytimeout) and [idle expiry hook](https://developers.cloudflare.com/containers/api/container-class/index.md#onactivityexpired) |
| Scheduled callbacks do not run | [Scheduling and alarm ownership](https://developers.cloudflare.com/containers/api/container-class/index.md#scheduling) |
| Shutdown cleanup or filesystem data loss | [Container shutdown and disk lifecycle](https://developers.cloudflare.com/containers/concepts/architecture/index.md#container-shutdown) |
| Out-of-memory errors or resource exhaustion | [FAQ](https://developers.cloudflare.com/containers/faq/index.md) and [limits and instance types](https://developers.cloudflare.com/containers/platform/limits/index.md) |
| Instance count exceeded or unexpected request distribution | [Wrangler configuration](https://developers.cloudflare.com/workers/wrangler/configuration/index.md#containers) and [scaling and routing](https://developers.cloudflare.com/containers/configuration/scaling-and-routing/index.md) |
| Worker and container image versions differ after deployment | [Deployment behavior](https://developers.cloudflare.com/containers/guides/deploy/index.md) and [rollouts](https://developers.cloudflare.com/containers/configuration/rollouts/index.md) |
| Local behavior differs from deployed behavior | [Local development](https://developers.cloudflare.com/containers/guides/local-dev/index.md) |
| Logs, cold starts, or runtime availability questions | [FAQ](https://developers.cloudflare.com/containers/faq/index.md) |
