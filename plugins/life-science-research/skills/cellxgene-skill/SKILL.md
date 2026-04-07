---
name: cellxgene-skill
description: Submit compact CELLxGENE Discover API requests for public collection and dataset metadata. Use when a user wants concise single-cell collection summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all CELLxGENE Discover calls.
- Use `base_url=https://api.cellxgene.cziscience.com/curation/v1`.
- Prefer targeted collection detail lookups rather than full archive dumps by default.
- The public `collections` list can be large and may require a higher `timeout_sec`; collection detail lookups are usually the better first call.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON only if the user explicitly asks for machine-readable output.
- Prefer these paths: `collections/<collection_id>` first, then `collections` when the user explicitly wants broad archive discovery.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common CELLxGENE patterns:
  - `{"base_url":"https://api.cellxgene.cziscience.com/curation/v1","path":"collections/db468083-041c-41ca-8f6f-bf991a070adf","max_items":5}`
  - `{"base_url":"https://api.cellxgene.cziscience.com/curation/v1","path":"collections","timeout_sec":60,"max_items":5}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://api.cellxgene.cziscience.com/curation/v1","path":"collections/db468083-041c-41ca-8f6f-bf991a070adf","max_items":5}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
