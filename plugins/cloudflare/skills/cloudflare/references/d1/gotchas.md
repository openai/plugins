# D1 Gotchas & Troubleshooting

Use current documentation to diagnose the failure before changing query or database configuration.

| Symptom or question | What to check |
| --- | --- |
| Missing table, query exception, or constraint error | [Debug D1](https://developers.cloudflare.com/d1/observability/debug-d1/index.md); verify the target binding, environment, and applied [migrations](https://developers.cloudflare.com/d1/reference/migrations/index.md) |
| Boolean, date, or other binding type mismatch | [Workers Binding API type conversion](https://developers.cloudflare.com/d1/worker-api/index.md) and [SQL support](https://developers.cloudflare.com/d1/sql-api/sql-statements/index.md) |
| Foreign key failure during writes or migrations | [Foreign key enforcement and deferral](https://developers.cloudflare.com/d1/sql-api/foreign-keys/index.md) |
| Slow or expensive database, excessive rows read or written, or finding which databases and queries cost the most | [Find slow and expensive queries](https://developers.cloudflare.com/d1/observability/find-expensive-queries/index.md) with `cf sql query` or `wrangler d1 insights` (API tokens need **Account Analytics Read**); then [indexes and query plans](https://developers.cloudflare.com/d1/best-practices/use-indexes/index.md) |
| Query duration, statement, storage, or account limits | [Current limits](https://developers.cloudflare.com/d1/platform/limits/index.md) |
| Unexpected usage charges or plan assumptions | [Pricing](https://developers.cloudflare.com/d1/platform/pricing/index.md); [find the databases and queries that cost the most](https://developers.cloudflare.com/d1/observability/find-expensive-queries/index.md) |
| Stale reads after a write | [Sessions, bookmarks, and read replication](https://developers.cloudflare.com/d1/best-practices/read-replication/index.md) |
| Transient query failures | [Retry guidance](https://developers.cloudflare.com/d1/best-practices/retry-queries/index.md); check idempotency before retrying writes |
| Import/export failure or unsupported data | [Import/export behavior and limitations](https://developers.cloudflare.com/d1/best-practices/import-export-data/index.md) |
| Local and deployed databases differ | [Local development](https://developers.cloudflare.com/d1/best-practices/local-development/index.md) and [environment configuration](https://developers.cloudflare.com/d1/configuration/environments/index.md) |

Continue to bind untrusted SQL values as described in [api.md](./api.md). Do not treat SQL injection as a recoverable database error or assume retries correct invalid queries.
