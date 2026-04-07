---
name: eqtl-catalogue-skill
description: Submit compact eQTL Catalogue API requests for association retrieval and documented metadata endpoints. Use when a user wants concise public eQTL Catalogue summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all eQTL Catalogue calls.
- Use `base_url=https://www.ebi.ac.uk/eqtl/api`.
- Prefer targeted association endpoints over broad list endpoints.
- The public API currently appears strict about query validation, and live smoke tests returned intermittent `400`/`500`/timeout failures even with documented parameter sets; treat this source as usable but upstream-fragile.
- For association endpoints, the script now backfills compatibility defaults for `quant_method`, `p_lower`, `p_upper`, and blank filter strings because the live API is currently rejecting omitted optional filters.
- Prefer `variant_id` in requests; the script mirrors it to the legacy `snp` query key to accommodate the current server-side validator.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON only if the user explicitly asks for machine-readable output.
- Prefer documented association paths such as `genes/<gene_id>/associations`, `studies/<study>/associations`, or tissue/study-scoped association routes with explicit filters, and surface upstream `400`/`500` errors verbatim when they occur.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common eQTL Catalogue patterns:
  - `{"base_url":"https://www.ebi.ac.uk/eqtl/api","path":"genes/ENSG00000141510/associations","params":{"study":"<study>","tissue":"<tissue_ontology_id>","variant_id":"rs7903146","size":10},"max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/eqtl/api","path":"studies/<study>/associations","params":{"tissue":"<tissue_ontology_id>","variant_id":"rs7903146","size":10},"max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/eqtl/api","path":"associations/rs7903146","params":{"size":10},"max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/eqtl/api","path":"genes/ENSG00000141510/associations","params":{"study":"<study>","tissue":"<tissue_ontology_id>","variant_id":"rs7903146","size":10},"max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
