---
name: opentargets-skill
description: Submit compact Open Targets Platform GraphQL requests for target, disease, drug, variant, study, and search data, including associated-disease datasource heatmap matrices. Use when a user wants concise Open Targets summaries or per-datasource evidence context
---

## Operating rules
- Use `scripts/opentargets_graphql.py` for all Open Targets GraphQL work.
- Use `scripts/opentargets_disease_heatmap.py` when the user wants the associated-disease bubble grid or a disease-by-datasource evidence matrix.
- The script accepts `max_items`; for nested GraphQL results, start with `max_items=3` to `5`.
- Keep GraphQL selection sets narrow and page connection-style fields conservatively.
- Use `query_path` for long GraphQL documents instead of pasting large inline query strings.
- Re-run requests in long conversations instead of relying on earlier tool output.
- Treat displayed `...` in tool previews as UI truncation, not part of the real query.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer targeted GraphQL queries that select only the fields needed for the user task.
- Use schema introspection only when necessary; do not dump large schema payloads into chat.
- For the associated-disease heatmap, treat `datasourceScores` as evidence-source breadth/context. Do not treat heatmap breadth alone as proof of causal target assignment, mechanism, or direction of effect.

## Input
- Read one JSON object from stdin.
- Required field: `query` or `query_path`
- Optional fields: `variables`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common Open Targets patterns:
  - `{"query":"query { __typename }"}`
  - `{"query":"query searchAny($q: String!) { search(queryString: $q) { total hits { entity score object { ... on Target { id approvedSymbol } } } } }","variables":{"q":"MST1"},"max_items":3}`

## Output
- Success returns `ok`, `source`, `top_keys`, a compact `summary`, and `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` such as `invalid_json`, `invalid_input`, `network_error`, `invalid_response`, or `graphql_error`.

## Execution
```bash
echo '{"query":"query { __typename }"}' | python scripts/opentargets_graphql.py
```

Associated-disease heatmap helper:

```bash
echo '{
  "ensembl_id":"ENSG00000186868",
  "page_size":50,
  "max_pages":4,
  "disease_name_filter":"alzh"
}' | python scripts/opentargets_disease_heatmap.py
```

The helper paginates `associatedDiseases`, collects `datasourceScores`, and returns:

- `matrix.columns`: datasource IDs plus display labels
- `matrix.rows`: diseases with `datasource_scores`
- `summary.rows_preview`: top datasource signals per disease

Use the disease-name filter as a client-side substring filter similar to the UI. If you later need the overall association score column, inspect the GraphQL row type first before adding candidate fields such as `score` or `associationScore`.

## References
- No additional runtime references are required; keep the import package limited to this file and the bundled scripts in `scripts/`.
