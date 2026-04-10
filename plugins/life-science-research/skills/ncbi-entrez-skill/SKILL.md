---
name: ncbi-entrez-skill
description: Submit compact NCBI Entrez E-Utilities requests for PubMed, Gene, Protein, Nucleotide, PMC metadata, and GEO metadata workflows. Use when a user wants concise Entrez search, fetch, summary, or link results; save raw JSON or XML only on request.
---

## Operating rules
- Use `scripts/ncbi_entrez.py` for all Entrez calls in this package.
- Use explicit `endpoint` values such as `esearch`, `esummary`, `efetch`, `elink`, or `einfo`.
- Search-style Entrez calls are better with `retmax=10` and `max_items=10`.
- GEO is nested under this skill. Use `db=gds` or `db=geoprofiles` for GEO metadata and load `references/geo.md` only when the user is specifically asking about GEO.
- BLAST workflows belong in `ncbi-blast-skill`. PMC Open Access workflows belong in `ncbi-pmc-skill`. Datasets v2 workflows belong in `ncbi-datasets-skill`.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script output by default.
- Return raw JSON or XML only if the user explicitly asks for machine-readable output.
- Prefer targeted endpoint calls instead of broad unfiltered dumps.
- If the user needs the full raw response, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required field: `endpoint`
- Optional fields: `params`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common Entrez patterns:
  - `{"endpoint":"esearch","params":{"db":"pubmed","term":"KRAS AND colorectal cancer","retmode":"json","retmax":10},"max_items":10}`
  - `{"endpoint":"esummary","params":{"db":"gene","id":"7157","retmode":"json"},"max_items":10}`
  - `{"endpoint":"efetch","params":{"db":"protein","id":"NP_000537.3","retmode":"xml"},"response_format":"xml","max_items":10}`
  - `{"endpoint":"elink","params":{"dbfrom":"gds","db":"pubmed","id":"200000001","retmode":"json"},"max_items":10}`

## Output
- Success returns `ok`, `source`, endpoint metadata, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"endpoint":"esearch","params":{"db":"gene","term":"TP53[gene] AND human[orgn]","retmode":"json","retmax":10},"max_items":10}' | python scripts/ncbi_entrez.py
```

## References
- Load `references/geo.md` only when the user specifically needs GEO query patterns.
- Keep the import package limited to this file, `references/geo.md`, and `scripts/ncbi_entrez.py`.
