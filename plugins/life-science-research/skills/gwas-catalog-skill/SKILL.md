---
name: gwas-catalog-skill
description: Submit compact GWAS Catalog REST API v2 requests for studies, associations, SNPs, EFO traits, genes, publications, loci, and metadata. Use when a user wants concise GWAS Catalog summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `gwas-catalog-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

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
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
