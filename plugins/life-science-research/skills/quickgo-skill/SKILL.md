---
name: quickgo-skill
description: Submit compact QuickGO requests for GO terms, annotations, and ontology traversal. Use when a user wants concise QuickGO summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `quickgo-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all QuickGO API calls.
- Use `base_url=https://www.ebi.ac.uk/QuickGO/services`.
- GO term lookups usually do not need `max_items`; annotation and traversal endpoints are better with `limit=10` and `max_items=10`.
- Send `Accept: application/json` in `headers`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer these paths: `ontology/go/terms/<id>`, `annotation/search`, and ontology child or ancestor endpoints.
- Treat `annotation/search` as upstream-fragile when QuickGO's annotation Solr backend is unavailable; fall back to ontology term lookup or UniProt GO annotations when appropriate.
- If the user needs the full payload, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common QuickGO patterns:
  - `{"base_url":"https://www.ebi.ac.uk/QuickGO/services","path":"ontology/go/terms/GO:0008150,GO:0003674","headers":{"Accept":"application/json"},"record_path":"results","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/QuickGO/services","path":"annotation/search","params":{"geneProductId":"P04637","limit":10},"headers":{"Accept":"application/json"},"record_path":"results","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/QuickGO/services","path":"ontology/go/terms/GO:0006915","headers":{"Accept":"application/json"},"record_path":"results","max_items":10}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
