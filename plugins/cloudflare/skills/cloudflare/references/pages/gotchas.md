# Pages Troubleshooting

Identify whether the failure occurs during the build, asset serving, or Function execution before changing configuration.

| Task | Documentation |
| --- | --- |
| Build output is missing or incorrect | [Build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/index.md) |
| A static URL redirects or returns an unexpected 404 | [Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/index.md) |
| Static response headers are not applied | [Headers](https://developers.cloudflare.com/pages/configuration/headers/index.md) |
| A redirect rule does not match | [Redirects](https://developers.cloudflare.com/pages/configuration/redirects/index.md) |
| Investigate a failed Function request | [Debugging and logging](https://developers.cloudflare.com/pages/functions/debugging-and-logging/index.md) |
| Check deployment and file capacity | [Pages limits](https://developers.cloudflare.com/pages/platform/limits/index.md) |
| Understand Function versus static request billing | [Functions pricing](https://developers.cloudflare.com/pages/functions/pricing/index.md) |

Compare the same route in local, preview, and production environments; record the build output and configuration used by each. See [Pages Functions troubleshooting](../pages-functions/gotchas.md) for handler and binding issues.

## Framework-Specific

Fetch the relevant [framework guide](https://developers.cloudflare.com/pages/framework-guides/index.md) before changing adapters or recommending another host. For a move to Workers, follow the [migration guide](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/index.md).
