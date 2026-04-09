---
name: ncbi-pmc-skill
description: Submit compact NCBI PMC Open Access requests for article/file availability metadata. Use when a user wants concise PMC Open Access summaries; save raw XML only on request.
---

## Operating rules
- Use `scripts/ncbi_pmc.py` for all PMC Open Access calls in this package.
- This skill is intentionally narrow: it currently covers the PMC Open Access service rather than the full PMC API surface.
- Pass endpoint-specific query parameters under `params`, typically `id` for a PMCID or DOI-style lookup supported by the OA service.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script output by default.
- Return raw XML only if the user explicitly asks for machine-readable output.
- Prefer targeted endpoint calls instead of broad unfiltered dumps.
- If the user needs the full raw response, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Optional fields: `params`, `record_path`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common PMC Open Access patterns:
  - `{"params":{"id":"PMC3257301"},"max_items":10}`
  - `{"params":{"id":"10.1093/nar/gkr1184"},"max_items":10}`

## Output
- Success returns `ok`, `source`, and a compact `summary`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"params":{"id":"PMC3257301"},"max_items":10}' | python scripts/ncbi_pmc.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/ncbi_pmc.py`.
