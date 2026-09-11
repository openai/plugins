---
name: human-protein-atlas-skill
description: Submit compact Human Protein Atlas requests for gene JSON, search downloads, and page-level tissue or cell-line lookups. Use when a user wants concise Human Protein Atlas summaries; save raw JSON or HTML only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `human-protein-atlas-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

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
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
