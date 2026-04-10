---
name: ncbi-datasets-skill
description: Submit compact NCBI Datasets v2 requests for assembly, genome, taxonomy, and related metadata endpoints. Use when a user wants concise NCBI Datasets summaries; save raw JSON or text only on request.
---

## Operating rules
- Use `scripts/ncbi_datasets.py` for all Datasets v2 calls in this package.
- Use explicit REST `path` values relative to `https://api.ncbi.nlm.nih.gov/datasets/v2`.
- Prefer targeted metadata paths instead of broad unfiltered pulls.
- Re-run requests in long conversations instead of relying on older tool output.
- Treat displayed `...` in tool previews as UI truncation, not literal request content.

## Execution behavior
- Return concise markdown summaries from the script output by default.
- Return raw JSON or text only if the user explicitly asks for machine-readable output.
- Prefer targeted endpoint calls instead of broad unfiltered dumps.
- If the user needs the full raw response, set `save_raw=true` and report the saved file path.

## Input
- Read one JSON object from stdin.
- Required field: `path`
- Optional fields: `params`, `record_path`, `response_format`, `max_items`, `max_depth`, `timeout_sec`, `save_raw`, `raw_output_path`
- Common Datasets patterns:
  - `{"path":"genome/taxon/assembly_descriptors","params":{"taxons":"9606"}}`
  - `{"path":"genome/accession/GCF_000001405.40/dataset_report"}`
  - `{"path":"taxonomy/taxon/9606"}`

## Output
- Success returns `ok`, `source`, path metadata, and either compact `records`, a compact `summary`, or `text_head`.
- Use `raw_output_path` when `save_raw=true`.
- Failure returns `ok=false` with `error.code` and `error.message`.

## Execution
```bash
echo '{"path":"genome/taxon/assembly_descriptors","params":{"taxons":"9606"}}' | python scripts/ncbi_datasets.py
```

## References
- No additional runtime references are required; keep the import package limited to this file and `scripts/ncbi_datasets.py`.
