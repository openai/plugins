# AI Search Pattern Routes

Choose retrieval-only search when your application displays chunks or handles generation itself; choose chat completions when AI Search should also generate the answer. Read [Search Workers binding](https://developers.cloudflare.com/ai-search/api/search/workers-binding/index.md) for both paths and streaming behavior.

| Task | Documentation |
|------|---------------|
| Isolate tenants using separate instances or a shared filtered instance | [Multitenancy](https://developers.cloudflare.com/ai-search/how-to/per-tenant-search/index.md) |
| Define built-in or custom metadata | [Metadata attributes](https://developers.cloudflare.com/ai-search/configuration/indexing/metadata/index.md) |
| Filter by metadata, combine conditions, or match a folder and subfolders | [Filtering](https://developers.cloudflare.com/ai-search/configuration/retrieval/filtering/index.md) |
| Tune result count and relevance thresholds | [Result controls](https://developers.cloudflare.com/ai-search/configuration/retrieval/result-controls/index.md) |
| Resolve follow-up queries using conversation context | [Query rewriting](https://developers.cloudflare.com/ai-search/configuration/retrieval/query-rewriting/index.md) |
| Improve result ordering with a second model | [Reranking](https://developers.cloudflare.com/ai-search/configuration/retrieval/reranking/index.md) |
| Customize generation and query-rewriting instructions | [System prompt](https://developers.cloudflare.com/ai-search/configuration/retrieval/system-prompt/index.md) |

For tenant isolation, read the full multitenancy guide before choosing an approach. A lower-bound folder comparison alone does not establish a tenant boundary; use the documented filtering semantics.
