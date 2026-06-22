# Protein Screen Results

Read this after `download-results` completes, when ranking screened protein-family binders or summarizing output files.

## Local Layout

Under `<output-root>/<run-name>/`:

- `.boltz-run.json`
- `run.json` - sanitized remote run record
- `results/index.jsonl` - one scored candidate per line, with candidate identity, metrics, and local paths
- `results/<pres_*>/metadata.json` - per-result metadata copied from list-results
- `results/<pres_*>/archive.tar.gz`
- extracted result files such as predicted complex structure and metrics

## Ranking

Rank by `binding_confidence` descending. Use `iptm` (higher is better) and `min_interaction_pae` (lower is better) as tiebreakers.

`optimization_score` is not emitted for `protein:library-screen`; do not sort by it.
