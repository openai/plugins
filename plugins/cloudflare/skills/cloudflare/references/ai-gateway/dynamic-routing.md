# AI Gateway Dynamic Routing

Use a dynamic route when model selection, traffic splitting, quotas, or fallbacks should be controlled in the gateway. For a simple retry or fallback sequence, check the request-handling and fallback guides before introducing a routing flow.

| Task | Current documentation |
|------|-----------------------|
| Design conditional routes, A/B splits, quotas, model fallbacks, and version rollbacks | [Dynamic routing](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/index.md) |
| Invoke a route from an SDK, HTTP request, or Worker; inspect route response metadata | [Using a dynamic route](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/usage/index.md) |
| Define route elements and connections programmatically | [JSON configuration](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/json-configuration/index.md) |
| Provide metadata used by routing conditions | [Custom metadata](https://developers.cloudflare.com/ai-gateway/observability/custom-metadata/index.md) |
| Configure model/provider fallbacks | [Fallbacks](https://developers.cloudflare.com/ai-gateway/configuration/fallbacks/index.md) |
| Configure retries, backoff, and timeouts | [Request handling](https://developers.cloudflare.com/ai-gateway/configuration/request-handling/index.md) |
| Inspect request outcomes, costs, and errors | [Analytics](https://developers.cloudflare.com/ai-gateway/observability/analytics/index.md) and [logging](https://developers.cloudflare.com/ai-gateway/observability/logging/index.md) |

Check the usage guide's authentication and stored-key prerequisites. Dynamic routes still use the [Unified API compatibility endpoint](https://developers.cloudflare.com/ai-gateway/usage/chat-completion/index.md); its single-model deprecation does not make the REST inference endpoint a replacement for route invocation.
