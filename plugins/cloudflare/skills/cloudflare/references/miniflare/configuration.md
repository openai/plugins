# Miniflare Configuration

Direct Miniflare does not read Wrangler configuration. Configure its bindings explicitly and build TypeScript or bundled Workers before starting tests; see [writing tests](https://developers.cloudflare.com/workers/testing/miniflare/writing-tests/index.md).

Match the Worker's intended compatibility date and flags when testing its behavior. Consult [compatibility dates](https://developers.cloudflare.com/workers/testing/miniflare/core/compatibility/index.md) rather than substituting a fixed date from a sample.

| Configure | Documentation |
|-----------|---------------|
| Script source, HTTP server, request metadata, or reloading | [Get started](https://developers.cloudflare.com/workers/testing/miniflare/get-started/index.md) |
| Module format and resolution rules | [Modules](https://developers.cloudflare.com/workers/testing/miniflare/core/modules/index.md) |
| Values and file-backed bindings | [Variables and secrets](https://developers.cloudflare.com/workers/testing/miniflare/core/variables-secrets/index.md) |
| Service bindings, shared storage, and several Workers | [Multiple Workers](https://developers.cloudflare.com/workers/testing/miniflare/core/multiple-workers/index.md) |
| Storage bindings and documented persistence options | [KV](https://developers.cloudflare.com/workers/testing/miniflare/storage/kv/index.md), [R2](https://developers.cloudflare.com/workers/testing/miniflare/storage/r2/index.md), [D1](https://developers.cloudflare.com/workers/testing/miniflare/storage/d1/index.md), [Durable Objects](https://developers.cloudflare.com/workers/testing/miniflare/storage/durable-objects/index.md), [Cache](https://developers.cloudflare.com/workers/testing/miniflare/storage/cache/index.md) |
| Queue producers and consumers | [Queues](https://developers.cloudflare.com/workers/testing/miniflare/core/queues/index.md) |

If the task is to run tests from the project's build and Wrangler configuration, consider the [integration test harness](https://developers.cloudflare.com/workers/testing/test-harness/index.md) or [Workers Vitest setup](https://developers.cloudflare.com/workers/testing/vitest-integration/write-your-first-test/index.md).
