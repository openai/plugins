---
name: string-skill
description: Submit compact STRING API requests for network, interaction partner, and enrichment endpoints. Use when a user wants concise STRING summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all STRING API calls.
- Use `base_url=https://string-db.org/api/json`.
- Use `method=POST` with `form_body` for STRING endpoints.
- Include `caller_identity` in `form_body`; keep it stable within a session when possible.
- The script accepts `max_items`; for `network` and `interaction_partners`, start with API `limit=10` and `max_items=10`.
- For `enrichment`, summarize the top `5` to `10` rows unless the user asks for more.
- Re-run requests in long conversations instead of relying on prior tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the script JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer these paths: `network`, `interaction_partners`, and `enrichment`.
- For long identifier lists, keep the request small and paged; if full results are needed, use `save_raw=true`.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common STRING patterns:
  - `{"base_url":"https://string-db.org/api/json","path":"network","method":"POST","form_body":{"identifiers":"TP53","species":9606,"caller_identity":"chatgpt-skill","limit":10},"max_items":10}`
  - `{"base_url":"https://string-db.org/api/json","path":"interaction_partners","method":"POST","form_body":{"identifier":"TP53","species":9606,"caller_identity":"chatgpt-skill","limit":10},"max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://string-db.org/api/json","path":"network","method":"POST","form_body":{"identifiers":"TP53","species":9606,"caller_identity":"chatgpt-skill","limit":10},"max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
