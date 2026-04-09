---
name: hmdb-skill
description: Submit compact HMDB search requests for metabolites, proteins, diseases, and pathways. Use when a user wants concise HMDB summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all HMDB calls.
- Use `base_url=https://hmdb.ca`.
- Search endpoints are better with `per_page=10` and `max_items=10`.
- Keep category-specific requests narrow instead of broad searches across multiple categories at once.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer `unearth/q` with explicit `query`, `category`, and `format=json`.
- If the user needs the full payload, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common HMDB patterns:
  - `{"base_url":"https://hmdb.ca","path":"unearth/q","params":{"query":"serotonin","category":"metabolites","format":"json","per_page":10},"record_path":"metabolites","max_items":10}`
  - `{"base_url":"https://hmdb.ca","path":"unearth/q","params":{"query":"glycolysis","category":"pathways","format":"json","per_page":10},"max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://hmdb.ca","path":"unearth/q","params":{"query":"serotonin","category":"metabolites","format":"json","per_page":10},"record_path":"metabolites","max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
