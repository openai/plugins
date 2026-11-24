# Static Assets Gotchas

Compare the deployed build output and effective configuration with the exact request that failed. Test browser navigation separately from client-side fetches when investigating SPA routing.

| Symptom or decision | Documentation |
|---------------------|---------------|
| Asset missing or unexpected files uploaded | [Asset directory](https://developers.cloudflare.com/workers/static-assets/binding/index.md#directory) and [ignore rules](https://developers.cloudflare.com/workers/static-assets/binding/index.md#ignoring-assets) |
| Worker is bypassed for an asset or protected path | [Worker-first routing](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/index.md#run-your-worker-script-first) |
| Browser navigation returns HTML for an API path | [SPA navigation requests](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/index.md#navigation-requests) and [advanced routing](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/index.md#advanced-routing-control) |
| Unexpected redirects or trailing slashes | [HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/index.md) |
| A missing route serves the wrong fallback | [SPA routing](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/index.md) or [SSG custom 404 pages](https://developers.cloudflare.com/workers/static-assets/routing/static-site-generation/index.md#custom-404-pages) |
| Cache behavior or custom headers differ from expectations | [Default and custom headers](https://developers.cloudflare.com/workers/static-assets/headers/index.md) |
| Vite development and deployment behave differently | [Vite asset configuration and output](https://developers.cloudflare.com/workers/vite-plugin/reference/static-assets/index.md) |
| Worker-first requests return 429 or affect cost | [Billing and limitations](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/index.md) |
| Asset count or file size exceeds deployment limits | [Static asset platform limits](https://developers.cloudflare.com/workers/platform/limits/index.md#static-assets) |
| Placement adds latency to asset requests | [Worker routing and placement caveat](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/index.md#run-your-worker-script-first) |

Verify a public asset, API endpoint, protected path, and missing URL against the routing intent. Inspect response status, redirect location, and cache headers before changing fallback or cache configuration. Return to [configuration.md](configuration.md) and [api.md](api.md) for the relevant settings and binding behavior.
