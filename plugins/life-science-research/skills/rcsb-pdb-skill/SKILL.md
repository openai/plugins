---
name: rcsb-pdb-skill
description: Submit compact RCSB PDB requests for core metadata, Search API queries, and FASTA downloads. Use when a user wants concise RCSB summaries; save raw JSON or FASTA only on request.
---

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
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
