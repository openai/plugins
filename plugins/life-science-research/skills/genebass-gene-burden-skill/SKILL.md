---
name: genebass-gene-burden-skill
description: Submit compact Genebass gene burden requests for one Ensembl gene ID and one burden set. Use when a user wants concise Genebass PheWAS summaries
---

## Operating rules
- Use `scripts/genebass_gene_burden.py` for all Genebass calls.
- This skill accepts one Ensembl gene ID per invocation.
- `max_results` is flexible; start around `25` for broad summaries and increase only if the user explicitly wants more associations.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script JSON by default.
- Return raw JSON only if the user explicitly asks for machine-readable output.
- Supported burden sets are `pLoF`, `missense|LC`, and `synonymous`, with the aliases already handled by the script.
- If the user needs the full result set, increase `max_results` deliberately instead of dumping everything by default.

## Input
- Read JSON from stdin as either a string Ensembl ID or an object.
- String form:
  - `"ENSG00000173531"`
- Object form:
  - `{"ensembl_gene_id":"ENSG00000173531","burden_set":"pLoF","max_results":25}`

## Output
- Success returns `ok`, `source`, input metadata, `gene`, association counts, `truncated`, and compact `associations`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"ensembl_gene_id":"ENSG00000173531","burden_set":"pLoF","max_results":25}' | python scripts/genebass_gene_burden.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/genebass_gene_burden.py`.
