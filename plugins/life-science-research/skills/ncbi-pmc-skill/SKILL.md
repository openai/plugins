---
name: ncbi-pmc-skill
description: Submit compact NCBI PMC Open Access requests for article/file availability metadata. Use when a user wants concise PMC Open Access summaries; save raw XML only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `ncbi-pmc-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

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
- Keep runtime imports limited to this file, `scripts/ncbi_pmc.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
