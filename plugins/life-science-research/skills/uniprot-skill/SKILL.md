---
name: uniprot-skill
description: Submit compact UniProt REST API requests for UniProtKB, UniRef, UniParc, and FASTA stream endpoints. Use when a user wants concise UniProt summaries; save raw JSON or FASTA only on request.
---

## Operating rules
- Use `scripts/rest_request.py` for all UniProt API calls.
- Use `base_url=https://rest.uniprot.org`.
- The script accepts `max_items`; for search endpoints, start with API `size=10` and `max_items=10`.
- Single accession or cluster lookups usually do not need `max_items`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not part of the real request.
- If the user asks for full JSON or FASTA, set `save_raw=true` and report the saved file path instead of pasting the payload into chat.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the script JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer these paths: `uniprotkb/search`, `uniprotkb/<accession>`, `uniref/<cluster>`, `uniparc/search`, and `uniprotkb/stream`.
- For `stream`, use `response_format=text` so the script returns only a short `text_head` unless raw output is requested.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common UniProt patterns:
  - `{"base_url":"https://rest.uniprot.org","path":"uniprotkb/search","params":{"query":"gene:TP53 AND organism_id:9606","fields":"accession,gene_names","size":10,"format":"json"},"record_path":"results","max_items":10}`
  - `{"base_url":"https://rest.uniprot.org","path":"uniprotkb/P04637","params":{"format":"json"}}`
  - `{"base_url":"https://rest.uniprot.org","path":"uniprotkb/stream","params":{"query":"organism_id:562","format":"fasta","size":2},"response_format":"text"}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://rest.uniprot.org","path":"uniprotkb/search","params":{"query":"gene:TP53 AND organism_id:9606","fields":"accession,gene_names","size":10,"format":"json"},"record_path":"results","max_items":10}' | python scripts/rest_request.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/rest_request.py`.
