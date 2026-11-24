# AI Gateway Troubleshooting

Identify the request path and whether the failure comes from gateway access, upstream provider authentication, or request policy before changing credentials or retry behavior. A status code alone does not establish the failing layer.

| Symptom or task | Current documentation |
|-----------------|-----------------------|
| Authentication or provider errors, timeouts, DLP failures, or unexpected cache behavior | [Troubleshooting](https://developers.cloudflare.com/ai-gateway/reference/troubleshooting/index.md) |
| Gateway authentication failure | [Authenticated Gateway](https://developers.cloudflare.com/ai-gateway/configuration/authentication/index.md) and [REST API authentication](https://developers.cloudflare.com/ai-gateway/usage/rest-api/index.md#authentication) |
| Provider key or billing mismatch | [BYOK](https://developers.cloudflare.com/ai-gateway/configuration/bring-your-own-keys/index.md), [Unified Billing](https://developers.cloudflare.com/ai-gateway/features/unified-billing/index.md), and the [provider guide](https://developers.cloudflare.com/ai-gateway/usage/providers/index.md) |
| Rate limits or repeated failures | [Rate limiting](https://developers.cloudflare.com/ai-gateway/features/rate-limiting/index.md) and [request handling](https://developers.cloudflare.com/ai-gateway/configuration/request-handling/index.md) |
| Unexpected cache hit or miss, including streaming behavior | [Caching](https://developers.cloudflare.com/ai-gateway/features/caching/index.md) |
| Missing logs, collection overrides, or storage limits | [Logging](https://developers.cloudflare.com/ai-gateway/observability/logging/index.md) and [limits](https://developers.cloudflare.com/ai-gateway/reference/limits/index.md) |
| Inspect headers, request metadata, usage, or export logs | [Header glossary](https://developers.cloudflare.com/ai-gateway/glossary/index.md), [custom metadata](https://developers.cloudflare.com/ai-gateway/observability/custom-metadata/index.md), [analytics](https://developers.cloudflare.com/ai-gateway/observability/analytics/index.md), and [Logpush](https://developers.cloudflare.com/ai-gateway/observability/logging/logpush/index.md) |
| Dynamic route failure | [Dynamic route usage](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/usage/index.md) |

Check the existing SDK and gateway retry settings together before adding another retry loop. Follow [SDK integration](./sdk-integration.md) when an endpoint or model format is suspect.
