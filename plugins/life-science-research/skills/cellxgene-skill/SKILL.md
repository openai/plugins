---
name: cellxgene-skill
description: Submit compact CELLxGENE Discover API requests for public collection and dataset metadata. Use when a user wants concise single-cell collection summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `cellxgene-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

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
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
