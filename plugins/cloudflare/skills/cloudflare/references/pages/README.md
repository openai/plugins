# Cloudflare Pages

Use this reference when maintaining an existing Pages project. For new applications, start with Workers as recommended in the [Pages framework guidance](https://developers.cloudflare.com/pages/framework-guides/index.md). Fetch current documentation before implementing.

| Task | Documentation |
| --- | --- |
| Configure the existing build | [Build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/index.md) |
| Manage automatic deployments from a repository | [Git integration](https://developers.cloudflare.com/pages/configuration/git-integration/index.md) |
| Deploy prebuilt output | [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/index.md) |
| Implement server-side requests | [Functions API reference](https://developers.cloudflare.com/pages/functions/api-reference/index.md) |
| Plan a move to Workers | [Migrate from Pages to Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/index.md) |

## In This Reference

- [configuration.md](./configuration.md) — build output, environments, and static rules
- [api.md](./api.md) — request handling and framework integration
- [patterns.md](./patterns.md) — project decisions and migration
- [gotchas.md](./gotchas.md) — build, routing, and deployment investigation

See [Pages Functions](../pages-functions/README.md) for handler-focused navigation. Identify the existing deployment method and framework before proposing changes.
