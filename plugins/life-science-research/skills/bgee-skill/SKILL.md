---
name: bgee-skill
description: Submit compact Bgee SPARQL requests for healthy wild-type expression metadata and ontology-aware lookup patterns. Use when a user wants concise Bgee summaries; save raw results only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `bgee-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/sparql_request.py` for all Bgee SPARQL work.
- Start with small `SELECT` or `ASK` queries and add `LIMIT` early.
- Prefer ontology-aware, healthy wild-type expression questions over broad triple dumps.
- Use `query_path` for longer SPARQL documents instead of pasting large inline queries.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the SPARQL JSON by default.
- Return raw results only if the user explicitly asks for machine-readable output.
- Default to JSON result format unless the user explicitly asks for text output.

## Input
- Read one JSON object from stdin.
- Required field: `query` or `query_path`
- Optional fields: `method`, `params`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common Bgee patterns:
  - `{"query":"ASK {}"}`
  - `{"query":"SELECT * WHERE { ?s ?p ?o } LIMIT 3","max_items":3}`

## Output
- Success returns `ok`, `source`, a compact `summary`, and `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` such as `invalid_json`, `invalid_input`, `network_error`, or `invalid_response`.

## Execution
```bash
echo '{"query":"ASK {}"}' | python scripts/sparql_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/sparql_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
