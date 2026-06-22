# Protein Design Results

Read this after `download-results` completes, when ranking designed protein-family binders or summarizing output files.

## Local Layout

Under `<output-root>/<run-name>/`:

- `.boltz-run.json`
- `run.json` - sanitized remote run record
- `results/index.jsonl` - one generated design per line, with sequence, metrics, and local paths
- `results/<pres_*>/metadata.json` - per-result metadata copied from list-results
- `results/<pres_*>/archive.tar.gz`
- extracted result files such as predicted complex structure and metrics

## Ranking

Rank by `binding_confidence` descending. Use `iptm` (higher is better) and `min_interaction_pae` (lower is better) as tiebreakers.

`optimization_score` is not emitted for `protein:design`; do not sort by it.

## Generated Binder Entity

The generated binder entity comes back as `type: "protein"` rather than `type: "designed_protein"`, with the sequence DSL resolved to a real amino-acid sequence in `value`. Select the binder by `chain_ids` (the ID assigned at submit time), not by `type == "designed_protein"`.
