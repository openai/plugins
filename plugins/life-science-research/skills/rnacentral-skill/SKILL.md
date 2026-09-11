---
name: rnacentral-skill
description: Submit compact RNAcentral API requests for RNA entry browsing, single-entry lookup, and cross-reference retrieval. Use when a user wants concise RNAcentral summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `rnacentral-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all RNAcentral calls.
- Use `base_url=https://rnacentral.org/api/v1`.
- Keep the trailing slash on collection and record paths to avoid redirects.
- Start with targeted lookups such as `rna/<URS>/<taxid>` because broad `rna/` browsing can be slow or time out.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON only if the user explicitly asks for machine-readable output.
- Prefer these paths: `rna/<URS>/<taxid>`, `rna/<URS>/`, `rna/<URS>/xrefs/`, and targeted `rna/` searches with `q` plus small `page_size`.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common RNAcentral patterns:
  - `{"base_url":"https://rnacentral.org/api/v1","path":"rna/URS000075C808/9606","max_items":10}`
  - `{"base_url":"https://rnacentral.org/api/v1","path":"rna/","params":{"q":"TP53","page_size":10},"record_path":"results","max_items":10}`
  - `{"base_url":"https://rnacentral.org/api/v1","path":"rna/URS0000000001/"}`
  - `{"base_url":"https://rnacentral.org/api/v1","path":"rna/URS0000000001/xrefs/","record_path":"results","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://rnacentral.org/api/v1","path":"rna/URS000075C808/9606","max_items":10}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
