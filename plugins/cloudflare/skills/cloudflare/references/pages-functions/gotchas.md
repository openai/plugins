# Pages Functions Troubleshooting

Start with the request path, deployment environment, and generated output that actually handled the request.

| Task | Documentation |
| --- | --- |
| A Function does not run or receives unexpected parameters | [Routing](https://developers.cloudflare.com/pages/functions/routing/index.md) |
| Middleware is skipped or static fallback fails | [Advanced mode](https://developers.cloudflare.com/pages/functions/advanced-mode/index.md) |
| Middleware order or scope is incorrect | [Middleware](https://developers.cloudflare.com/pages/functions/middleware/index.md) |
| Bindings or secrets differ between environments | [Bindings](https://developers.cloudflare.com/pages/functions/bindings/index.md) |
| Runtime or environment types do not match | [TypeScript](https://developers.cloudflare.com/pages/functions/typescript/index.md) |
| A local request behaves differently | [Local development](https://developers.cloudflare.com/pages/functions/local-development/index.md) |
| Inspect exceptions and deployment logs | [Debugging and logging](https://developers.cloudflare.com/pages/functions/debugging-and-logging/index.md) |
| Check runtime quotas | [Workers limits](https://developers.cloudflare.com/workers/platform/limits/index.md) |
| Check request costs | [Functions pricing](https://developers.cloudflare.com/pages/functions/pricing/index.md) |

Reproduce a failing path through the actual application rather than only calling a handler with a hand-built context. Check the deployed configuration and generated output before changing application code. See [Pages troubleshooting](../pages/gotchas.md) for build, asset, and framework issues.
