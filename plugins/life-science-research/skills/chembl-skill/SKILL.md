---
name: chembl-skill
description: Submit compact ChEMBL API requests for activity, molecule, target, mechanism, and text-search endpoints. Use when a user wants concise ChEMBL summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `chembl-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all ChEMBL API calls.
- Use `base_url=https://www.ebi.ac.uk/chembl/api/data`.
- The script accepts `max_items`; for activity, mechanism, and text-search collections, start with API `limit=10` and `max_items=10`.
- Single molecule or target lookups usually do not need `max_items`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the script JSON verbatim only if the user explicitly asks for machine-readable output.
- Prefer these paths: `activity.json`, `molecule/<id>.json`, `target/<id>.json`, `mechanism.json`, and `molecule/search.json`.
- Use `record_path` to target list fields like `activities`, `mechanisms`, or `molecules`.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common ChEMBL patterns:
  - `{"base_url":"https://www.ebi.ac.uk/chembl/api/data","path":"activity.json","params":{"molecule_chembl_id":"CHEMBL25","limit":10},"record_path":"activities","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/chembl/api/data","path":"molecule/CHEMBL25.json"}`
  - `{"base_url":"https://www.ebi.ac.uk/chembl/api/data","path":"molecule/search.json","params":{"q":"imatinib","limit":10},"record_path":"molecules","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/chembl/api/data","path":"activity.json","params":{"molecule_chembl_id":"CHEMBL25","limit":10},"record_path":"activities","max_items":10}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
