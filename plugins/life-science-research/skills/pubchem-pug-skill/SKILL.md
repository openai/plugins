---
name: pubchem-pug-skill
description: Submit compact PubChem PUG REST requests for compound properties, descriptions, assay summaries, and substance metadata. Use when a user wants concise PubChem summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all PubChem PUG calls.
- Use `base_url=https://pubchem.ncbi.nlm.nih.gov/rest/pug`.
- Property and description endpoints usually return a single focused record; assay or broader list endpoints are better with `max_items=10`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer property, description, assay summary, and substance paths instead of broad record dumps.
- If the user needs the full payload, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common PubChem patterns:
  - `{"base_url":"https://pubchem.ncbi.nlm.nih.gov/rest/pug","path":"compound/name/aspirin/property/MolecularFormula,MolecularWeight/JSON","record_path":"PropertyTable.Properties"}`
  - `{"base_url":"https://pubchem.ncbi.nlm.nih.gov/rest/pug","path":"compound/cid/2244/description/JSON","record_path":"InformationList.Information","max_items":10}`
  - `{"base_url":"https://pubchem.ncbi.nlm.nih.gov/rest/pug","path":"assay/aid/1706/summary/JSON","record_path":"AssaySummaries","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://pubchem.ncbi.nlm.nih.gov/rest/pug","path":"compound/name/aspirin/property/MolecularFormula,MolecularWeight/JSON","record_path":"PropertyTable.Properties"}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
