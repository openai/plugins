---
name: finngen-phewas-skill
description: Fetch compact FinnGen PheWAS summaries for single variants by accepting rsID, GRCh37, or GRCh38 input and resolving to the required GRCh38 query. Use when a user wants concise FinnGen association results for one variant
---

## Operating rules
- Use `scripts/finngen_phewas.py` for all FinnGen PheWAS lookups.
- Accept exactly one of `rsid`, `grch37`, `grch38`, or `variant`; resolve to the canonical GRCh38 `chr:pos-ref-alt` query before calling FinnGen.
- The script accepts `max_results`; start with `max_results=10` and only increase it if the first slice is insufficient.
- Re-run the lookup in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.
- If the user needs the full association payload, set `save_raw=true` and report `raw_output_path` instead of pasting large arrays into chat.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the JSON verbatim only if the user explicitly asks for machine-readable output.
- Surface the canonical queried variant, total association count, truncation status, and any returned `regions`.
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
- Success returns `ok`, `source`, `input`, `query_variant`, `max_results_applied`, `association_count`, `association_count_total`, `truncated`, `associations`, `variant`, `regions`, `variant_url`, `raw_output_path`, and `warnings`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"grch38":"10:112998590-C-T","max_results":10}' | python scripts/finngen_phewas.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/finngen_phewas.py`.
