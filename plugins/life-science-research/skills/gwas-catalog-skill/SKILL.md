---
name: gwas-catalog-skill
description: Submit compact GWAS Catalog REST API v2 requests for studies, associations, SNPs, EFO traits, genes, publications, loci, and metadata. Use when a user wants concise GWAS Catalog summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all GWAS Catalog API calls.
- Use `base_url=https://www.ebi.ac.uk/gwas/rest/api/v2`.
- The script accepts `max_items`; for collection endpoints, start with API `size=10` and `max_items=10`.
- Single-resource endpoints such as `studies/<accession>` generally do not need `max_items`.
- Use `record_path` to target `_embedded.<resource>` lists.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the script JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer these paths: `metadata`, `studies`, `studies/<accession>`, `associations`, `snps`, `efoTraits`, `genes`, `publications`, and `loci`.
- Use `save_raw=true` if the user needs the full HATEOAS payload or pagination links.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common GWAS Catalog patterns:
  - `{"base_url":"https://www.ebi.ac.uk/gwas/rest/api/v2","path":"metadata"}`
  - `{"base_url":"https://www.ebi.ac.uk/gwas/rest/api/v2","path":"studies","params":{"efo_trait":"asthma","size":10},"record_path":"_embedded.studies","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/gwas/rest/api/v2","path":"associations","params":{"mapped_gene":"BRCA1","size":10},"record_path":"_embedded.associations","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/gwas/rest/api/v2","path":"studies","params":{"efo_trait":"asthma","size":10},"record_path":"_embedded.studies","max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
