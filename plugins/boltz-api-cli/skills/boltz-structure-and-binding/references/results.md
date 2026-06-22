# Structure and Binding Results

Read this after `download-results` completes, when summarizing output files, metrics, or validation failures.

## Local Layout

Under `<output-root>/<run-name>/`:

- `.boltz-run.json` - run metadata, cursor, idempotency key
- `outputs/archive.tar.gz` - archive containing `prediction/{metrics.json, sample_*_predicted_structure.cif, sample_*_pae.npz}`

Summarize the useful metrics and point the user at the CIF path.

## Metrics

Metrics in `metrics.json` are nested, not flat:

- `best_sample.metrics` and each `all_sample_results[].metrics` contain lowercase keys such as `structure_confidence`, `ptm`, `iptm`, `ligand_iptm`, `protein_iptm`, `complex_plddt`, `complex_iplddt`, `complex_pde`, and `complex_ipde`.
- `binding_metrics` is a separate top-level object present only when `binding` was requested.
- `ligand_protein_binding` binding metrics include `binding_confidence` and `optimization_score`.
- `protein_protein_binding` binding metrics include `binding_confidence` only.

`binding_confidence` (0–1) is the confidence that binding occurs — the primary signal for whether the complex binds. `optimization_score` ranks **binding strength** for lead optimization (higher = stronger predicted binding); it is emitted only for `ligand_protein_binding`.

## Validation Quirk

If the server rejects the payload with only `{"code": "VALIDATION_ERROR","message":"Request validation failed"}` and no field-level details, inspect `entities`, `binding`, and `constraints` carefully. `predictions:structure-and-binding` currently omits detailed validation paths more often than the other endpoints.
