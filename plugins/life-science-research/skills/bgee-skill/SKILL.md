---
name: bgee-skill
description: Submit compact Bgee SPARQL requests for healthy wild-type expression metadata and ontology-aware lookup patterns. Use when a user wants concise Bgee summaries; save raw results only on request.
---

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
- No additional runtime references are required; keep the import package limited to this file and `scripts/sparql_request.py`.
