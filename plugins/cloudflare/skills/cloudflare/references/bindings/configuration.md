# Binding Configuration

Confirm the target account, environment, and resource before adding or changing a binding. Keep staging and production resources separate where their data or permissions must be isolated.

| Task | Current documentation |
| --- | --- |
| Configure storage, compute, platform, and service bindings | [Wrangler binding configuration](https://developers.cloudflare.com/workers/wrangler/configuration/index.md#bindings) |
| Create or inspect resources and manage deployments | [Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/index.md) (select the product's commands) |
| Configure named environments and non-inheritable bindings | [Wrangler environments](https://developers.cloudflare.com/workers/wrangler/environments/index.md) |
| Set non-sensitive configuration | [Environment variables](https://developers.cloudflare.com/workers/configuration/environment-variables/index.md) |
| Set or rotate credentials in a chosen environment | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |
| Configure text, data, and Wasm modules in existing projects | [Wrangler bundling](https://developers.cloudflare.com/workers/wrangler/bundling/index.md) and [configuration](https://developers.cloudflare.com/workers/wrangler/configuration/index.md) |
| Choose locally simulated resources or remote bindings | [Local development](https://developers.cloudflare.com/workers/local-development/index.md) and [supported bindings per development mode](https://developers.cloudflare.com/workers/local-development/bindings-per-env/index.md) |
| Supply local variables and secrets | [Local environment variables and secrets](https://developers.cloudflare.com/workers/local-development/environment-variables/index.md) |
| Seed or persist local resource data | [Adding local data](https://developers.cloudflare.com/workers/local-development/local-data/index.md) |
| Generate types after configuring bindings | [Workers TypeScript](https://developers.cloudflare.com/workers/languages/typescript/index.md) |

Bindings and variables are not inherited automatically by named environments. Configure the required values for the environment being used, including its secrets. Binding names used in code must match configuration; the target resource's ID or name is a separate value.

Keep credentials out of committed variables and local secret files out of version control. Remote development can access real resources: verify the target rather than assuming that running locally isolates writes.
