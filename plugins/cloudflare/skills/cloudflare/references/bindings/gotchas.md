# Binding Gotchas and Troubleshooting

Start by checking the binding name, selected environment, and actual target resource. Regenerating types alone does not fix a missing runtime binding.

| Symptom or question | What to check |
| --- | --- |
| A binding is undefined or points to unexpected data | [Binding configuration](https://developers.cloudflare.com/workers/wrangler/configuration/index.md#bindings) and [environment inheritance](https://developers.cloudflare.com/workers/wrangler/environments/index.md) |
| TypeScript cannot find a binding or runtime type | [Current type generation and TypeScript setup](https://developers.cloudflare.com/workers/languages/typescript/index.md) |
| Updated credentials are not reflected in a client | [Binding changes and retained global state](https://developers.cloudflare.com/workers/runtime-apis/bindings/index.md#making-changes-to-bindings); verify the [secret's environment and deployment](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |
| Binding calls fail outside a handler | [Environment access and global-scope restrictions](https://developers.cloudflare.com/workers/runtime-apis/bindings/index.md#how-to-access-env) |
| A service target is unavailable or incorrect | [Service bindings](https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/index.md) and [multi-Worker development](https://developers.cloudflare.com/workers/local-development/multi-workers/index.md) |
| Local data, secrets, or available bindings differ from deployment | [Development mode support](https://developers.cloudflare.com/workers/local-development/bindings-per-env/index.md), [local data](https://developers.cloudflare.com/workers/local-development/local-data/index.md), and [local secrets](https://developers.cloudflare.com/workers/local-development/environment-variables/index.md) |
| KV reads appear stale or return no value | [How KV works](https://developers.cloudflare.com/kv/concepts/how-kv-works/index.md); verify the namespace and handle missing values |
| Resource-specific API errors or limits | Follow the product from the [binding catalog](https://developers.cloudflare.com/workers/runtime-apis/bindings/index.md) to its troubleshooting and limits documentation |
| Worker resource limits or unexpected charges | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/index.md) and [pricing](https://developers.cloudflare.com/workers/platform/pricing/index.md); check each bound product's limits and pricing separately |
| Need to inspect configuration, resources, deployments, or logs | [Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/index.md) and [real-time logs](https://developers.cloudflare.com/workers/observability/logs/real-time-logs/index.md) |

Never log secret values or return the environment object in a response. Inspect names and configuration without exposing credentials. Check the selected resource and development mode before issuing debugging commands that could mutate remote data.
