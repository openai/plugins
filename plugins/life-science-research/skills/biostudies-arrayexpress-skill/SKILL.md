---
name: biostudies-arrayexpress-skill
description: Submit compact BioStudies and ArrayExpress API requests for free-text search and accession-based study retrieval. Use when a user wants concise BioStudies summaries
---

## Operating rules
- Use `scripts/rest_request.py` for all BioStudies and ArrayExpress calls.
- Use `base_url=https://www.ebi.ac.uk/biostudies/api/v1`.
- Search pages are better with `pageSize=10` and `max_items=10`; accession lookups usually do not need `max_items`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer these paths: `search`, `ArrayExpress/search`, `studies/<accession>`, and `studies/<accession>/info`.
- If the user needs the full payload, set `save_raw=true` and report the saved file path instead of pasting large study records into chat.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common BioStudies patterns:
  - `{"base_url":"https://www.ebi.ac.uk/biostudies/api/v1","path":"search","params":{"query":"rna","page":1,"pageSize":10},"record_path":"hits","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/biostudies/api/v1","path":"ArrayExpress/search","params":{"query":"single cell","page":1,"pageSize":10},"record_path":"hits","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/biostudies/api/v1","path":"studies/E-MTAB-6701"}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/biostudies/api/v1","path":"search","params":{"query":"rna","page":1,"pageSize":10},"record_path":"hits","max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
