# Durable Objects Rules & Best Practices

Choose one object per entity that needs coordinated state. Keep essential data in durable storage; in-memory state must be reconstructible. Prefer SQLite for new classes, and inspect the backend of existing classes before selecting APIs. For idle WebSocket servers, prefer hibernation and plan for state restoration.

Fetch the relevant current documentation before implementing or reviewing changes.

| Task | Documentation |
|------|---------------|
| Choose object boundaries, deterministic routing, parent-child relationships, or initialization | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/index.md) |
| Choose SQLite or maintain an existing KV-backed class | [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md); [Legacy KV storage API](https://developers.cloudflare.com/durable-objects/api/legacy-kv-storage-api/index.md) |
| Review storage gates, external I/O races, transactions, or schema initialization | [Rules of Durable Objects](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/index.md); [SQLite storage API](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/index.md); [Durable Object State](https://developers.cloudflare.com/durable-objects/api/state/index.md) |
| Configure class lifecycle changes | [Class exports](https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/index.md); [Legacy class migrations](https://developers.cloudflare.com/durable-objects/reference/durable-object-class-migrations-legacy/index.md) |
| Set placement hints or jurisdiction constraints | [Data location](https://developers.cloudflare.com/durable-objects/reference/data-location/index.md) |
| Create stubs, invoke RPC, or use HTTP handlers | [Invoke methods](https://developers.cloudflare.com/durable-objects/best-practices/create-durable-object-stubs-and-send-requests/index.md); [Namespace API](https://developers.cloudflare.com/durable-objects/api/namespace/index.md) |
| Schedule per-object work and handle retries | [Alarms](https://developers.cloudflare.com/durable-objects/api/alarms/index.md) |
| Restore WebSocket connection state after hibernation | [Use WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/index.md) |
| Handle exceptions, restarts, and shutdowns | [Error handling](https://developers.cloudflare.com/durable-objects/best-practices/error-handling/index.md); [Object lifecycle](https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/index.md) |

For verification, use [Testing Durable Objects](testing.md). Keep API signatures, configuration, limits, and implementation examples in the linked docs.
