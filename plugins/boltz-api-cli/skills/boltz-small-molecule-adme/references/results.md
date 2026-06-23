# Small-Molecule ADME Results

Read this after an ADME `run` (or `retrieve`) completes, when reporting per-molecule scores.

ADME is the **lightweight** endpoint: it returns scalar/categorical values only — no structure files, no archives, no per-hit directories, no ranking. Everything lands in one `run.json`.

## Local Layout

`run` persists to `<output-root>/<run-name>/`:

- `.boltz-run.json` — local checkpoint (`run_type: "adme"`, `request_fingerprint`, and a `remote` object with the run id/status). No result cursor/pagination — ADME is single-shot.
- `run.json` — the full remote record. Results live under `output.molecules[]`.

There is **no** `outputs/` or `results/` tree, no archives, no CIF, no `pae.npz` — ADME predicts properties, not structures.

## Per-molecule output (`run.json` → `output.molecules[]`)

Entries are returned in the same order as the input `molecules`. Each entry:

- `id` — server-assigned `adme_mol_*` id
- `external_id` — your input `id` (use it to map results back to inputs)
- `smiles` — the scored SMILES (echoed from the request)
- `status` — `succeeded` or `failed`
- `error` — `null` on success; on failure an object `{code, message}` (e.g. `{"code": "adme_enumeration_failed", "message": "Invalid SMILES"}`)
- `adme` — the scores; present on success, **`null` on failure**:
  - `solubility` — categorical: `high-confidence`, `medium-confidence`, or `high-risk`
  - `permeability` — numeric score
  - `lipophilicity` — numeric LogD

The three ADME values live under `output.molecules[].adme`, not at the top of the molecule entry.

ADME values are approximate estimates for triage and ranking, not absolute measurements.

## Reporting

For each molecule, report `external_id` (or `smiles`) with its `solubility`, `permeability`, and `lipophilicity`. Failures are **per-molecule, not per-batch**: one bad SMILES yields `status: "failed"` with `adme: null` for just that molecule while the rest succeed — always check `status` before reading `adme`. When a library was split across batches (>128 molecules → ≤128 per request), merge the per-batch `run.json` `output.molecules[]` lists when reporting.
