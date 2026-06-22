# Small-Molecule Screen Results

Read this after `download-results` completes, when ranking hits, explaining missing molecules, or summarizing output files.

## Local Layout

Under `<output-root>/<run-name>/`:

- `.boltz-run.json` - run metadata
- `run.json` - sanitized remote run record; check `progress.rejection_summary` for filtered/invalid counts when present
- `results/index.jsonl` - one scored molecule per line, with `external_id`, `smiles`, `metrics`, a free `adme` block, and local `paths`
- `results/<pres_*>/metadata.json` - per-result metadata copied from the list-results record
- `results/<pres_*>/archive.tar.gz`
- `results/<pres_*>/files/result/{metrics.json, <pres_*>_predicted.cif, pae.npz}` (use the `paths.structure` field from `index.jsonl` rather than assuming a fixed CIF filename)

Use `results/index.jsonl` as the authoritative local scored list after download. The extracted per-hit `metrics.json` files do not include input-library mapping fields.

## Ranking

Sort by the metric matching the user's goal:

- `binding_confidence` for hit discovery
- `optimization_score` for lead optimization

These are parallel intents, not fallback metrics. Also available: `structure_confidence`, `complex_plddt`, `complex_iplddt`, `iptm`, and `ptm`.

## ADME (free, included)

Every scored molecule also carries a free Tier-1 ADME block (`adme`), a sibling of `metrics` in `index.jsonl` and each `metadata.json`:

- `adme.solubility` — categorical: `high-confidence`, `medium-confidence`, or `high-risk`
- `adme.permeability` — numeric score
- `adme.lipophilicity` — numeric LogD

No extra flag, no extra cost. Use it for developability triage alongside the binding metrics. These are approximate estimates for triage/ranking, not absolute measurements; may be absent on a failed molecule. For ADME on bare SMILES without a target (and without paying the per-molecule screen cost), use the `boltz-small-molecule-adme` skill instead.

## Filtered Inputs

The `results/<pres_*>/` directory count is often lower than `len(molecules)`. Default server-side `molecule_filters` can drop candidates before scoring. If the user needs to know which input IDs were dropped, compute `input_ids - seen(external_id)` from `results/index.jsonl`.
