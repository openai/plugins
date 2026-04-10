---
name: metabolights-skill
description: Submit compact MetaboLights requests for study discovery and study-level metabolomics metadata. Use when a user wants concise MetaboLights summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all MetaboLights calls.
- Use `base_url=https://www.ebi.ac.uk/metabolights/ws`.
- Start with `studies` for archive browsing and `studies/<MTBLS accession>` for targeted records.
- Keep study discovery narrow and paged rather than pulling very large pages.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON only if the user explicitly asks for machine-readable output.
- Prefer these paths: `studies` and `studies/<MTBLS accession>`.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common MetaboLights patterns:
  - `{"base_url":"https://www.ebi.ac.uk/metabolights/ws","path":"studies","record_path":"content","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/metabolights/ws","path":"studies/MTBLS1"}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/metabolights/ws","path":"studies","record_path":"content","max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
