---
name: rcsb-pdb-skill
description: Submit compact RCSB PDB requests for core metadata, Search API queries, and FASTA downloads. Use when a user wants concise RCSB summaries; save raw JSON or FASTA only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `rcsb-pdb-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all RCSB PDB and Search API calls.
- Use `base_url=https://data.rcsb.org/rest/v1` for core metadata, `https://search.rcsb.org/rcsbsearch/v2` for Search API, and `https://www.rcsb.org` for FASTA downloads.
- Core entry or assembly lookups usually do not need `max_items`; Search API results are better with query pager rows around `10` and `max_items=10`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer core metadata endpoints for focused lookups and Search API POST requests for discovery.
- For FASTA downloads, use `response_format=text` so the script returns a short `text_head` unless raw output is requested.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common RCSB patterns:
  - `{"base_url":"https://data.rcsb.org/rest/v1","path":"core/entry/4hhb"}`
  - `{"base_url":"https://search.rcsb.org/rcsbsearch/v2","path":"query","method":"POST","json_body":{"query":{"type":"terminal","service":"full_text","parameters":{"value":"hemoglobin"}},"return_type":"entry","request_options":{"pager":{"start":0,"rows":10}}},"record_path":"result_set","max_items":10}`
  - `{"base_url":"https://www.rcsb.org","path":"fasta/entry/4HHB/download","response_format":"text"}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://data.rcsb.org/rest/v1","path":"core/entry/4hhb"}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
