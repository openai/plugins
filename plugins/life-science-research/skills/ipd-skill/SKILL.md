---
name: ipd-skill
description: Submit compact IPD REST requests for HLA allele and cell-level metadata using the public IPD query API. Use when a user wants concise IPD summaries; save raw JSON or text only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `ipd-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/rest_request.py` for all IPD calls.
- Use `base_url=https://www.ebi.ac.uk/cgi-bin/ipd/api`.
- The most stable public routes are `allele` and `cell`.
- For HLA allele browsing, pass `project=HLA` and keep `limit` modest.
- Re-run requests in long conversations instead of relying on older tool output.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON or text only if the user explicitly asks for machine-readable output.
- Prefer these paths: `allele`, `cell`, and `allele/download`.

## Input
- Read one JSON object from stdin.
- Required fields: `base_url`, `path`
- Optional fields: `method`, `params`, `headers`, `json_body`, `form_body`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common IPD patterns:
  - `{"base_url":"https://www.ebi.ac.uk/cgi-bin/ipd/api","path":"allele","params":{"project":"HLA","limit":10},"record_path":"data","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/cgi-bin/ipd/api","path":"allele","params":{"project":"HLA","query":"contains(name,\"A*01\")","limit":10},"record_path":"data","max_items":10}`
  - `{"base_url":"https://www.ebi.ac.uk/cgi-bin/ipd/api","path":"cell","params":{"limit":10},"record_path":"data","max_items":10}`

## Output
- Success returns `ok`, `source`, `path`, `method`, `status_code`, `warnings`, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"base_url":"https://www.ebi.ac.uk/cgi-bin/ipd/api","path":"allele","params":{"project":"HLA","limit":10},"record_path":"data","max_items":10}' | python scripts/rest_request.py
```

## References
- Keep runtime imports limited to this file, `scripts/rest_request.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
