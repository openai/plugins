---
name: ukb-topmed-phewas-skill
description: Fetch compact UKB-TOPMed PheWAS summaries for single variants by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query. Use when a user wants concise UKB-TOPMed association results for one variant
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `ukb-topmed-phewas-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/ukb_topmed_phewas.py` for all UKB-TOPMed PheWAS lookups.
- Accept exactly one of `rsid`, `grch37`, `grch38`, or `variant`; resolve to the canonical GRCh38 `chr:pos-ref-alt` query before calling UKB-TOPMed.
- The script accepts `max_results`; start with `max_results=10` and only increase it if the first slice is insufficient.
- Re-run the lookup in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.
- If the user needs the full association payload, set `save_raw=true` and report `raw_output_path` instead of pasting large arrays into chat.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the JSON verbatim only if the user explicitly asks for machine-readable output.
- Surface the canonical queried variant, total association count, and whether the results were truncated.
- Increase `max_results` gradually instead of asking for large association dumps in one call.

## Input
- Read one JSON object from stdin, or a single JSON string containing the variant.
- Required input: exactly one of `rsid`, `grch37`, `grch38`, or `variant`
- Optional fields: `max_results`, `save_raw`, `raw_output_path`, `timeout_sec`
- Common patterns:
  - `{"grch38":"10:112998590-C-T","max_results":10}`
  - `{"grch37":"10:114758349-C-T","max_results":10}`
  - `{"rsid":"rs7903146","max_results":10}`
  - `{"variant":"10:112998590:C:T","max_results":25,"save_raw":true}`

## Output
- Success returns `ok`, `source`, `input`, `query_variant`, `max_results_applied`, `association_count`, `association_count_total`, `truncated`, `associations`, `variant`, `variant_url`, `raw_output_path`, and `warnings`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"grch38":"10:112998590-C-T","max_results":10}' | python scripts/ukb_topmed_phewas.py
```

## References
- Keep runtime imports limited to this file, `scripts/ukb_topmed_phewas.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
