---
name: cbioportal-skill
description: Submit compact cBioPortal API requests for studies, molecular profiles, mutations, clinical data, and samples. Use when a user wants concise cBioPortal summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `cbioportal-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all cBioPortal API calls.
- Use `base_url=https://www.cbioportal.org/api`.
- Collection endpoints are better with `pageSize=10` and `max_items=10`; single study or profile lookups usually do not need `max_items`.
- Use `method=POST` plus `json_body` for fetch-style endpoints such as mutation fetches.
- Send `Accept: application/json` in `headers`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer these paths: `studies`, `studies/<studyId>/molecular-profiles`, `molecular-profiles/<profileId>/mutations/fetch`, and study-level clinical or sample endpoints.
- If the user needs the full payload, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common cBioPortal patterns:
  - `{"base_url":"https://www.cbioportal.org/api","path":"studies","params":{"keyword":"breast","projection":"SUMMARY","pageSize":10},"headers":{"Accept":"application/json"},"max_items":10}`
  - `{"base_url":"https://www.cbioportal.org/api","path":"molecular-profiles/brca_tcga_mutations/mutations/fetch","method":"POST","json_body":{"sampleListId":"brca_tcga_all","entrezGeneIds":[7157]},"headers":{"Accept":"application/json"},"max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.cbioportal.org/api","path":"studies","params":{"keyword":"breast","projection":"SUMMARY","pageSize":10},"headers":{"Accept":"application/json"},"max_items":10}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
