---
name: human-protein-atlas-skill
description: Submit compact Human Protein Atlas requests for gene JSON, search downloads, and page-level tissue or cell-line lookups. Use when a user wants concise Human Protein Atlas summaries; save raw JSON or HTML only on request.
---

## Operating rules
- Use `scripts/rest_request.py` for all Human Protein Atlas calls.
- Use `base_url=https://www.proteinatlas.org`.
- The script accepts `max_items`; single gene entry lookups usually do not need it, while search and download endpoints are better with `max_items=10`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.
- If the user asks for full HTML or JSON, set `save_raw=true` and report the saved file path instead of pasting large payloads into chat.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the script JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer these paths: `<ENSG>.json`, `api/search_download.php`, `search/tissue/<symbol>`, and `search/cellline/<symbol>`.
- For page-level search endpoints, prefer `response_format=text` so the script returns only `text_head` unless raw output is requested.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common HPA patterns:
  - `{"base_url":"https://www.proteinatlas.org","path":"ENSG00000141510.json"}`
  - `{"base_url":"https://www.proteinatlas.org","path":"api/search_download.php","params":{"search":"TP53","format":"json","columns":"g,gs,tissue","compress":"no"},"max_items":10}`
  - `{"base_url":"https://www.proteinatlas.org","path":"search/tissue/TP53","response_format":"text"}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.proteinatlas.org","path":"ENSG00000141510.json"}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
