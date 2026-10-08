---
name: ncbi-clinicaltables-skill
description: Submit compact Clinical Tables NCBI Gene requests for human gene lookup, pagination, and field selection. Use when a user wants concise autocomplete-style human gene search results
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `ncbi-clinicaltables-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

## Operating rules
- Use `scripts/ncbi_gene_clinicaltables.py` for all Clinical Tables gene searches.
- The script accepts `max_items`; for search pages, start with `count=10` and `max_items=10`.
- Use `params` for endpoint options like `df`, `ef`, `sf`, `q`, `offset`, and `count`.
- Prefer `ncbi-entrez-skill` when the user wants general Entrez Gene records rather than autocomplete/search rows.
- Page with `offset` instead of asking for large pulls.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.
- If the user asks for the full payload, set `save_raw=true` and report the saved file path instead of pasting large response arrays into chat.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return the JSON verbatim only if the user explicitly asks for machine-readable output.
- Use `terms` for the primary search text.
- Keep `count` modest and page with `offset` instead of pulling large result sets at once.

## Input
- Read one JSON object from stdin.
- Required field: `terms`
- Optional fields: `params`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common NCBI Gene patterns:
  - `{"terms":"TP53","params":{"df":"GeneID,Symbol,description"}}`
  - `{"terms":"BRCA","params":{"count":10,"df":"chromosome,GeneID,Symbol,description,type_of_gene"},"max_items":10}`
  - `{"terms":"kinase","params":{"count":10,"offset":10,"df":"GeneID,Symbol,description"},"max_items":10}`

## Output
- Success returns `ok`, `source`, `terms`, `total`, `codes`, `display_rows`, `extra_fields`, and truncation metadata.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"terms":"TP53","params":{"count":10,"df":"GeneID,Symbol,description"},"max_items":10}' | python scripts/ncbi_gene_clinicaltables.py
```

## References
- Keep runtime imports limited to this file, `scripts/ncbi_gene_clinicaltables.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
