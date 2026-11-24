# Vectorize pattern routes

| Task | Current documentation |
|------|-----------------------|
| Generate and query Workers AI embeddings | [Vectorize and Workers AI](https://developers.cloudflare.com/vectorize/get-started/embeddings/index.md) |
| Query with embeddings from OpenAI | [OpenAI integration](https://developers.cloudflare.com/vectorize/best-practices/query-vectors/index.md#openai) |
| Choose embedding dimensions and distance metric | [Create indexes](https://developers.cloudflare.com/vectorize/best-practices/create-indexes/index.md) |
| Build a retrieval-augmented generation application | [Workers AI RAG tutorial](https://developers.cloudflare.com/workers-ai/guides/tutorials/build-a-retrieval-augmented-generation-ai/index.md) |
| Link search results to source documents | [Vector metadata](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/index.md#metadata) |
| Partition vectors by tenant | [Namespaces](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/index.md#namespaces) and [namespace versus metadata filtering](https://developers.cloudflare.com/vectorize/reference/metadata-filtering/index.md#namespace-versus-metadata-filtering) |
| Combine similarity search with categorical or range filters | [Metadata filtering](https://developers.cloudflare.com/vectorize/reference/metadata-filtering/index.md) |
| Ingest or update vectors in batches | [Insert vectors](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/index.md) and [limits](https://developers.cloudflare.com/vectorize/platform/limits/index.md) |

## Embedding and retrieval decisions

Keep ingestion and query embeddings compatible: use the same model and preprocessing, and extract the individual vector from the provider's documented response shape. Fetch the selected model's current documentation for dimensions and input requirements.

For RAG, store a reliable reference to the source content and request the metadata needed to resolve it. Handle missing or deleted source documents before passing retrieved context to generation.

## Tenant scope

Namespaces and metadata filters narrow searches; they do not authenticate the caller. Derive the permitted tenant scope from trusted identity and enforce it on every relevant read and write, including ID-based retrieval and deletion. Do not assume a namespace query option protects other operations.

Choose namespace or metadata partitioning based on the required query scope and current limits. Both narrow the search space; avoid assuming metadata filtering happens after vector search. If tenant IDs are stored in metadata, create the corresponding metadata index before ingestion.
