# D1 Patterns & Best Practices

Use these guides to design the operation, then fetch [api.md](./api.md) for implementation references.

| Task | Current documentation |
| --- | --- |
| Design pagination, filters, joins, and aggregations | [Query a database](https://developers.cloudflare.com/d1/best-practices/query-d1/index.md) and [supported SQL](https://developers.cloudflare.com/d1/sql-api/sql-statements/index.md) |
| Reduce scans and inspect query plans | [Use indexes](https://developers.cloudflare.com/d1/best-practices/use-indexes/index.md) |
| Find queries in production to index or cache | [Find slow and expensive queries](https://developers.cloudflare.com/d1/observability/find-expensive-queries/index.md) |
| Batch writes or transform data | [Database API](https://developers.cloudflare.com/d1/worker-api/d1-database/index.md) and [limits](https://developers.cloudflare.com/d1/platform/limits/index.md) |
| Store and query event metadata | [Query JSON](https://developers.cloudflare.com/d1/sql-api/query-json/index.md) |
| Evaluate a cache in front of D1 | [How KV works](https://developers.cloudflare.com/kv/concepts/how-kv-works/index.md) |
| Choose shared or per-tenant databases | [D1 FAQs](https://developers.cloudflare.com/d1/reference/faq/index.md) and [limits](https://developers.cloudflare.com/d1/platform/limits/index.md) |
| Reduce read latency while preserving required consistency | [Read replication](https://developers.cloudflare.com/d1/best-practices/read-replication/index.md) |
| Plan point-in-time recovery or portable backups | [Time Travel](https://developers.cloudflare.com/d1/reference/time-travel/index.md) and [import/export](https://developers.cloudflare.com/d1/best-practices/import-export-data/index.md) |

Keep result sets bounded and pagination ordering deterministic. Choose indexes from actual query plans. When splitting a large operation into batches, account for the loss of whole-operation atomicity across batches.

Authorize a tenant before selecting its database or rows; a request header alone is not proof of tenant membership. Application login sessions stored in tables are separate from D1's Sessions API.

Before caching reads, decide how stale data may be and how writes invalidate cached results. For replicated reads, choose session constraints and bookmark propagation based on read-after-write requirements rather than assuming every read sees the latest primary state.
