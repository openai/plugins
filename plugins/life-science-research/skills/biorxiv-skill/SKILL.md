---
name: biorxiv-skill
description: Submit compact bioRxiv and medRxiv API requests for details, publication-linkage, and DOI lookups. Use when a user wants concise preprint metadata summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `biorxiv-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all bioRxiv and medRxiv API calls.
- Use `base_url=https://api.biorxiv.org`.
- The script accepts `max_items`; for `details` and `pubs` pages, start around `max_items=10`.
- Prefer one cursor page at a time instead of increasing page size or pasting long collections into chat.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not part of the true request.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the raw script JSON only if the user explicitly asks for machine-readable output.
- Prefer these paths: `details/<server>/<start>/<end>/<cursor>/json`, `details/<server>/<doi>/na/json`, `pubs/<server>/<start>/<end>/<cursor>`, and `pubs/<server>/<doi>/na/json`.
- If the user needs full page contents, set `save_raw=true` and report the saved file path rather than pasting large collections into chat.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common biorxiv patterns:
  - `{"base_url":"https://api.biorxiv.org","path":"details/biorxiv/2025-03-21/2025-03-28/0/json","record_path":"collection","max_items":10}`
  - `{"base_url":"https://api.biorxiv.org","path":"details/medrxiv/10.1101/2020.09.09.20191205/na/json","record_path":"collection","max_items":10}`
  - `{"base_url":"https://api.biorxiv.org","path":"pubs/medrxiv/2020-03-01/2020-03-30/0","record_path":"collection","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://api.biorxiv.org","path":"details/biorxiv/2025-03-21/2025-03-28/0/json","record_path":"collection","max_items":10}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
