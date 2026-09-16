---
name: clinicaltrials-skill
description: Submit compact ClinicalTrials.gov API v2 requests for study search, metadata, enums, search areas, and field statistics. Use for concise registry summaries and bounded target-program research paired with PubMed.
---

## Target-program workflow
When asked for target biology, prior programs, and safety, especially when this
skill is paired with `ncbi-entrez-skill`:

1. Run one `action=studies` wrapper call per target with `max_pages=1` and no
   more than ten compact records. Set `save_raw=true` with a unique temporary
   output path on this first call.
2. Search target names and aliases in interventional studies. Keep completed
   and terminated programs rather than filtering to currently recruiting
   studies.
3. Rank records by evidence value: posted results or mature outcome-bearing
   programs first, then a negative or inconclusive program, then active
   no-results programs.
4. Retain at most five distinct programs per target. Do not treat termination
   for business, accrual, or reprioritization as evidence of toxicity or target
   failure.
5. Extract intervention names, aliases, NCT IDs, phase, enrollment, status,
   outcome signal, and safety signal. Feed intervention aliases into the
   companion PubMed clinical-program search.
6. Do not rerun the same registry query with a larger `max_depth` or a
   different output projection. When compact output lacks a needed field,
   reshape the saved response locally in one pass. Project only NCT ID, title,
   status, stop reason, phase, enrollment, intervention names, `hasResults`,
   primary outcome values, and compact serious-adverse-event terms or counts.
7. Do not make direct-study follow-up requests in this bounded pass. Mark a
   field unavailable when the saved response cannot support it.
8. Stop when the mature positive, negative or inconclusive, and observed-safety
   slots are covered or explicitly unavailable.

Do not inspect wrapper source, probe Python environments, or use web search to
re-verify registry results unless the documented invocation fails, records
conflict, or the user explicitly requests current regulatory status.

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
- No additional runtime references are required; keep the import package limited to this file and `scripts/clinicaltrials_client.py`.
