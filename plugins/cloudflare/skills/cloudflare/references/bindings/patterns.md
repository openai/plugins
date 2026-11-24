# Binding Patterns

Choose the interaction and lifecycle first, then retrieve the implementation guide.

| Task | Current documentation |
| --- | --- |
| Choose HTTP forwarding or RPC between Workers | [Service bindings](https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/index.md) |
| Forward Requests and Responses through a service binding | [Service bindings over HTTP](https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/http/index.md) |
| Expose callable methods with `WorkerEntrypoint` | [Service bindings over RPC](https://developers.cloudflare.com/workers/runtime-apis/bindings/service-bindings/rpc/index.md) and [RPC TypeScript](https://developers.cloudflare.com/workers/runtime-apis/rpc/typescript/index.md) |
| Run connected Workers during development | [Developing with multiple Workers](https://developers.cloudflare.com/workers/local-development/multi-workers/index.md) |
| Test handlers against configured bindings and mock dependencies | [Workers Vitest configuration](https://developers.cloudflare.com/workers/testing/vitest-integration/configuration/index.md) and [test APIs](https://developers.cloudflare.com/workers/testing/vitest-integration/test-apis/index.md) |
| Select KV, D1, R2, or Durable Objects | [Storage options](https://developers.cloudflare.com/workers/platform/storage-options/index.md) |
| Keep clients current when bindings change | [Binding lifecycle](https://developers.cloudflare.com/workers/runtime-apis/bindings/index.md#making-changes-to-bindings) |
| Manage credentials used by external API clients | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |

Use service bindings for internal Worker calls when appropriate, and choose HTTP or RPC based on the interface being exposed. A service binding does not replace application-level authorization for the caller's requested operation.

Choose storage based on access patterns and consistency requirements, not copied size or latency thresholds. Parallelize independent binding operations when useful; preserve ordering where one operation depends on another's result.

Avoid retaining clients derived from mutable bindings across requests without accounting for binding updates. Importing `env` is supported, but binding I/O still requires an appropriate execution context; follow the lifecycle guide rather than assuming all global access is forbidden.
