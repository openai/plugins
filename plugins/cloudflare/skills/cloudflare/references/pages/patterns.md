# Pages Project Decisions

Keep project-specific choices here; fetch framework adapters, configuration, and code examples from the docs.

| Task | Documentation |
| --- | --- |
| Maintain a framework deployment | [Framework guides](https://developers.cloudflare.com/pages/framework-guides/index.md) |
| Deploy from an external build pipeline | [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/index.md) |
| Manage multiple apps in one repository | [Monorepos](https://developers.cloudflare.com/pages/configuration/monorepos/index.md) |
| Evaluate backend locality | [Smart Placement](https://developers.cloudflare.com/pages/functions/smart-placement/index.md) |
| Plan a move to Workers | [Migrate from Pages to Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/index.md) |

Check the existing build command, adapter, and output ownership together. Evaluate placement using the application’s backend dependencies and measured latency. For a migration, inventory routes, middleware, bindings, static rules, and deployment settings before following the migration guide.

See [Pages Functions patterns](../pages-functions/patterns.md) for request-level decisions.
