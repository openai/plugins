---
name: ncbi-entrez-skill
description: Submit compact NCBI Entrez E-Utilities requests for PubMed, Gene, Protein, Nucleotide, PMC metadata, and GEO metadata workflows. Use when a user wants concise Entrez search, fetch, summary, or link results; save raw JSON or XML only on request.
---

## Source presentation
<!-- source-presentation-contract:v2 -->
- Follow `../../references/source-presentation.md` for every final user-facing answer.
- Use the `ncbi-entrez-skill` entry in `../../references/source-links.json` for authoritative source names and canonical record URL templates.
- Preserve structured `sources` metadata for provenance, but add claim-adjacent Markdown links only for substantive external claims supported by the response.
- Do not force evidence links for connectivity or schema checks, source metadata, empty results, failures, routing-only answers, or sources that returned no supporting evidence.
- Prefer canonical record pages, fall back to sanitized `sources[].request_url` or authoritative `sources[].url` values, and never invent unsupported deep links.
- Preserve explicitly requested raw or machine-readable output without injecting Markdown links.

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
- Apply the source registry templates to every PMID, DOI, NCBI Gene ID, or GEO accession that appears in the summary, including in tables, bullets, parentheticals, and source lists.
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
- Keep runtime imports limited to this file, `references/geo.md`, `scripts/ncbi_entrez.py`, `../../references/source-presentation.md`, and `../../references/source-links.json`.
