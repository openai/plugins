---
name: clinicaltrials-skill
description: Submit compact ClinicalTrials.gov API v2 requests for study search, metadata, enums, search areas, and field statistics. Use when a user wants concise ClinicalTrials.gov summaries
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `clinicaltrials-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/clinicaltrials_client.py` for all ClinicalTrials.gov v2 calls.
- Study searches are better with `max_items=10` and `max_pages=1`; only increase pages when the user explicitly wants more than the first page.
- Use targeted `params` instead of broad unfiltered study dumps.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Prefer `action=studies` for search and `action=metadata|search_areas|enums|stats_size|field_values|field_sizes` for API introspection and field stats.
- If the user needs full pages or aggregated responses, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required field: `action`
- Supported actions: `studies`, `metadata`, `search_areas`, `enums`, `stats_size`, `field_values`, `field_sizes`, `request`
- Optional fields: `path` for `action=request`, `params`, `max_items`, `max_depth`, `max_pages`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common ClinicalTrials.gov patterns:
  - `{"action":"studies","params":{"query.cond":"prostate cancer","filter.overallStatus":"RECRUITING","pageSize":10},"max_items":10,"max_pages":1}`
  - `{"action":"metadata"}`
  - `{"action":"field_values","params":{"field":"protocolSection.identificationModule.organization.fullName"}}`

## Output
- `action=studies` returns `pages_fetched`, `next_page_token`, count metadata, and compact `records`.
- Other actions return either compact `records` or a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"action":"studies","params":{"query.cond":"prostate cancer","filter.overallStatus":"RECRUITING","pageSize":10},"max_items":10,"max_pages":1}' | python scripts/clinicaltrials_client.py
```

## References
- Keep runtime imports limited to this file, `scripts/clinicaltrials_client.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
