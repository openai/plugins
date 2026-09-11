---
name: ensembl-skill
description: Submit compact Ensembl REST API requests for lookup, overlap, cross-reference, and variation endpoints. Use when a user wants concise Ensembl summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `ensembl-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all Ensembl API calls.
- Use `base_url=https://rest.ensembl.org`.
- The script accepts `max_items`; object lookups usually do not need it, but `overlap` and `xrefs` are better with `max_items=10`.
- Send JSON-friendly headers such as `Accept: application/json` and `Content-Type: application/json`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not part of the true request.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the script JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer these paths: `lookup/id/<id>`, `overlap/region/<species>/<region>`, `xrefs/id/<id>`, and `variation/<species>/<id>`.
- Use `save_raw=true` when the user needs the full payload.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common Ensembl patterns:
  - `{"base_url":"https://rest.ensembl.org","path":"lookup/id/ENSG00000141510","headers":{"Accept":"application/json","Content-Type":"application/json"}}`
  - `{"base_url":"https://rest.ensembl.org","path":"overlap/region/homo_sapiens/1:1000000-1002000","params":{"feature":"gene"},"headers":{"Accept":"application/json","Content-Type":"application/json"},"max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://rest.ensembl.org","path":"lookup/id/ENSG00000141510","headers":{"Accept":"application/json","Content-Type":"application/json"}}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
