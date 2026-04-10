---
name: mgnify-skill
description: Submit compact MGnify API requests for microbiome studies, samples, and biome metadata. Use when a user wants concise MGnify summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all MGnify calls.
- Use `base_url=https://www.ebi.ac.uk/metagenomics/api/v1`.
- MGnify uses JSON:API-style responses. Prefer `record_path=data` for collection endpoints.
- Keep requests narrow by study accession, sample accession, or biome whenever possible.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON only if the user explicitly asks for machine-readable output.
- Prefer these paths: `studies`, `samples`, and `biomes`.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common MGnify patterns:
  - `{"base_url":"https://www.ebi.ac.uk/metagenomics/api/v1","path":"studies","params":{"page_size":10},"record_path":"data","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/metagenomics/api/v1","path":"biomes","params":{"page_size":10},"record_path":"data","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/metagenomics/api/v1","path":"studies","params":{"page_size":10},"record_path":"data","max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
