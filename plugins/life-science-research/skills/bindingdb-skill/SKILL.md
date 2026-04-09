---
name: bindingdb-skill
description: Submit compact BindingDB REST API requests for ligand-target binding lookups by PDB, UniProt, or similarity search. Use when a user wants concise BindingDB summaries; save raw payloads only on request.
---

## Operating rules
- Use `scripts/rest_request.py` for all BindingDB API calls.
- Use `base_url=https://bindingdb.org`.
- Add `response=application/json` in `params` when you want structured output; some empty-result cases may still return an empty body.
- For broad lookup endpoints, start around `max_items=10`; similarity-style queries are better with `5-10`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer these paths: `rest/getLigandsByPDBs`, `rest/getLigandsByUniprots`, `rest/getLigandsBySmiles`, and `rest/getTargetsByCompound`.
- If the user needs the full payload, set `save_raw=true` and report the saved file path instead of pasting large response bodies into chat.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common BindingDB patterns:
  - `{"base_url":"https://bindingdb.org","path":"rest/getLigandsByPDBs","params":{"pdb":"1Q0L","cutoff":100,"identity":92,"response":"application/json"},"max_items":10}`
  - `{"base_url":"https://bindingdb.org","path":"rest/getLigandsBySmiles","params":{"smiles":"CC(=O)OC1=CC=CC=C1C(=O)O","cutoff":0.9,"response":"application/json"},"max_items":5}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://bindingdb.org","path":"rest/getLigandsByPDBs","params":{"pdb":"1Q0L","cutoff":100,"identity":92,"response":"application/json"},"max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
