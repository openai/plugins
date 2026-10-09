---
name: ncbi-entrez-skill
description: Submit compact NCBI Entrez E-Utilities requests for PubMed, Gene, Protein, Nucleotide, PMC metadata, and GEO metadata workflows. Use for concise Entrez search, fetch, summary, or link results and for bounded target-evidence research paired with ClinicalTrials.gov.
---

## Target-evidence workflow
When asked for target biology, prior programs, and safety, especially when this
skill is paired with `clinicaltrials-skill`:

1. Plan the complete cross-source retrieval before invoking either wrapper.
2. Create these evidence slots for each target:
   - human biology or pharmacodynamic target validation;
   - normal adult-tissue expression or translational safety;
   - the most mature positive clinical program;
   - one negative, terminated, or inconclusive program with outcome evidence
     when available;
   - observed human safety;
   - preclinical mechanism, efficacy, or safety.
3. Run the bounded ClinicalTrials.gov search first and reuse its intervention
   names and aliases in the PubMed clinical-program query.
4. Run at most two PubMed `esearch` calls per target: one for biology,
   expression, normal tissue, and preclinical safety; one for named clinical
   programs, efficacy, pharmacodynamics, and observed safety.
5. Prefer primary studies with outcomes. Exclude editorials and comments from
   the clinical query when possible.
6. Select at most six papers per target. Across all targets, fetch selected
   PMIDs in one batched `efetch`; do not add `esummary` when `efetch` supplies
   the needed citation metadata.
7. Keep NCBI calls sequential. Use compact `retmax`, `max_items`, and
   `max_depth` values and avoid returning full objects or large abstract sets.
8. Stop when every available evidence slot is filled. State unavailable slots
   explicitly instead of expanding into open-ended searches.

For one target, budget one ClinicalTrials.gov wrapper call, two PubMed
`esearch` calls, and one batched `efetch`. For multiple targets, add one
registry call and two searches per target but keep one shared `efetch`. Do not
rerun an identical request to change formatting or selected fields. If fuller
local inspection is needed, set `save_raw=true` on the first call and inspect
the saved response without calling the network wrapper again. Wrapper failure
is the only exception.

For PubMed XML fetches, pair `retmode=xml` with `response_format=xml`, set
`save_raw=true`, and parse the saved XML in one local pass. Do not inspect
wrapper source, probe Python environments, or use web search to re-verify
PubMed results unless the documented invocation fails, records conflict, or
the user explicitly requests current regulatory status.

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
- In final user-facing summaries, never display a bare PMID or DOI. Render every PMID as a Markdown link in the form `[PMID <PMID>](https://pubmed.ncbi.nlm.nih.gov/<PMID>/)` and every DOI as `[<DOI>](https://doi.org/<DOI>)`, including in tables, bullets, parentheticals, and source lists.
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
