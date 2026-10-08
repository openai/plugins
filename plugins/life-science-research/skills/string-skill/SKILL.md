---
name: string-skill
description: Submit compact STRING API requests for network, interaction partner, and enrichment endpoints. Use when a user wants concise STRING summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `string-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

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
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
