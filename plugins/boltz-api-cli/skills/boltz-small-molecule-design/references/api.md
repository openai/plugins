# Small Molecule Design — Payload Reference

Covers the `small-molecule:design` endpoint. Prefer a single merged top-level `--input` payload. Field names below are **API body field names**, not CLI flag names.

Minimal CLI pattern:

```bash
boltz-api small-molecule:design estimate-cost --input @yaml:///absolute/path/payload.yaml
boltz-api small-molecule:design start --idempotency-key "<run-name>" --input @yaml:///absolute/path/payload.yaml --raw-output --transform id
```

In permission-gated agents, keep the submit command as a top-level `boltz-api ... start` invocation. Read the printed job ID from stdout and paste it into the later `download-results` command.

Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win. Direct object flags still work as overrides, such as `--target @yaml:///absolute/path/target.yaml` or `--molecule-filters @json:///absolute/path/filters.json`. Piped YAML / JSON on stdin remains supported when you need it, but the body must use API field names.

## Contents

- [Top-level request](#top-level-request)
- [`num_molecules` minimum](#num_molecules-minimum)
- [Cost](#cost)
- [`chemical_space`](#chemical_space)
- [`target`](#target)
- [`molecule_filters`](#molecule_filters)
- [Outputs (after `download-results`)](#outputs-after-download-results)
- [Escape hatch](#escape-hatch)

## Top-level request

```yaml
# payload.yaml
num_molecules: 10
target:
  entities:
    - type: protein
      chain_ids: [A]
      value: MKTAYIAKQRQISFVKSHFSRQ
  pocket_residues:
    A: [42, 43, 44]         # 0-based
  reference_ligands:
    - "CC(=O)Oc1ccccc1C(=O)O"
chemical_space: enamine_real
molecule_filters:
  boltz_smarts_catalog_filter_level: recommended
```

Top-level fields:

- `num_molecules` (required) — number to generate. **Must be between 10 and 1,000,000** (server rejects outside this range).
- `target` (required) — protein target object (same shape as the screen endpoint).
- `chemical_space` (optional) — generation space constraint. Currently `"enamine_real"` is the documented value. Omit for default.
- `molecule_filters` (optional) — filter candidates before they're scored. Same schema as the screen endpoint.

Also passed as separate `start` flags:

- `--idempotency-key <slug>`
- `--workspace-id <id>` (admin keys only)

## `num_molecules` minimum

The server rejects `num_molecules < 10` or `> 1000000` with `VALIDATION_ERROR`. Validate client-side before submitting.

## Cost

Cost is a flat **$0.025 per molecule** (size-independent — verified against `estimate-cost`: the per-unit rate does not change with target or molecule size). `estimate-cost` returns the authoritative total — always report `estimated_cost_usd`.

## `chemical_space`

Optional. Documented value: `"enamine_real"` — restricts generation to synthesizable molecules from the Enamine REAL library. Omit unless the user explicitly wants this.

## `target`

Identical shape to `small-molecule:library-screen`. Only protein entities are supported.

```yaml
target:
  entities:
    - type: protein
      chain_ids: [A]
      value: MKTAYIAKQRQISFVKSHFSRQ
      cyclic: false           # optional
      modifications: []       # optional; defaults to []
  pocket_residues:
    A: [42, 43, 44]           # 0-based
  reference_ligands:
    - "CC(=O)Oc1ccccc1C(=O)O"
```

Entity fields:

- `type: protein` (required)
- `chain_ids` (required)
- `value` (required)
- `modifications` (optional)
- `cyclic` (optional, bool)

Optional target fields:

- `pocket_residues` — `{chain_id: [0-based residue_index, ...]}`.
- `reference_ligands` — list of SMILES to help locate the pocket.

### Polymer modifications

```yaml
modifications:
  - residue_index: 12         # 0-based
    type: ccd
    value: MSE
```

`type` must be `ccd` — SMILES polymer modifications are **not** supported (the API rejects them with `modifications[].type must be "ccd"`).

## `molecule_filters`

Same schema as the screen endpoint. Applied during generation so candidates that fail are never scored.

Top-level:

- `boltz_smarts_catalog_filter_level` — `"recommended"` (default), `"extra"`, `"aggressive"`, `"disabled"`.
- `custom_filters` — list, AND-combined.

### `lipinski_filter`

```yaml
custom_filters:
  - type: lipinski_filter
    max_mw: 500
    max_logp: 5
    max_hbd: 5
    max_hba: 10
    allow_single_violation: true
```

All four caps (`max_mw`, `max_logp`, `max_hbd`, `max_hba`) are **required together** — only `allow_single_violation` is optional. For a partial cap (e.g. MW + logP only), use `rdkit_descriptor_filter`, whose descriptor keys are independently optional; a partial `lipinski_filter` is rejected with a confusing union error.

### `rdkit_descriptor_filter`

```yaml
custom_filters:
  - type: rdkit_descriptor_filter
    mol_wt: {min: 250, max: 550}
    mol_logp: {min: 1, max: 5}
    num_h_donors: {max: 5}
    num_h_acceptors: {max: 10}
    num_rotatable_bonds: {max: 10}
    num_rings: {min: 1, max: 6}
    num_aromatic_rings: {max: 3}
    num_heteroatoms: {min: 1, max: 15}
    fraction_csp3: {min: 0.2, max: 1.0}
    tpsa: {min: 20, max: 140}
```

Descriptor keys: `mol_wt`, `mol_logp`, `num_h_donors`, `num_h_acceptors`, `num_rotatable_bonds`, `num_rings`, `num_aromatic_rings`, `num_heteroatoms`, `fraction_csp3`, `tpsa`. Each takes `{min?, max?}`.

### `smarts_catalog_filter`

```yaml
custom_filters:
  - type: smarts_catalog_filter
    catalog: PAINS
```

Catalogs: `PAINS`, `PAINS_A`, `PAINS_B`, `PAINS_C`, `BRENK`, `CHEMBL`, `CHEMBL_BMS`, `CHEMBL_Dundee`, `CHEMBL_Glaxo`, `CHEMBL_Inpharmatica`, `CHEMBL_LINT`, `CHEMBL_MLSMR`, `CHEMBL_SureChEMBL`, `NIH`.

### `smarts_custom_filter`

```yaml
custom_filters:
  - type: smarts_custom_filter
    patterns: ["[N+](=O)[O-]"]
```

### `smiles_regex_filter`

```yaml
custom_filters:
  - type: smiles_regex_filter
    patterns: ["Cl", "Br"]
```

## Outputs (after `download-results`)

Under `<output-root>/<run-name>/`:

- `.boltz-run.json`
- `run.json` — sanitized remote run record
- `results/index.jsonl` — one generated candidate per line, copied from list-results metadata plus local artifact paths
- `results/<pres_*>/metadata.json` — per-result metadata copied from the list-results record
- `results/<pres_*>/archive.tar.gz` — one dir per generated candidate
- `results/<pres_*>/files/result/{metrics.json, <result-id>_predicted.cif, pae.npz}` (the CIF is named `<pres_*>_predicted.cif` — prefer the `paths.structure` field from `index.jsonl` over hard-coding the filename)

Per-result fields (available in `results/index.jsonl`, `results/<pres_*>/metadata.json`, and the `list-results` stream):

- `id` — server-assigned `pres_*` ID
- `smiles` — generated SMILES
- `metrics.binding_confidence` — primary for **hit discovery**
- `metrics.optimization_score` — ranks by binding strength for **lead optimization**
- `metrics.structure_confidence`
- `metrics.complex_plddt`, `metrics.complex_iplddt`
- `metrics.iptm`, `metrics.ptm`
- `adme` — Tier-1 ADME triage returned **free** per generated molecule (sibling of `metrics`, not nested in it). Object with `solubility` (categorical: `high-confidence` / `medium-confidence` / `high-risk`), `permeability` (numeric score), and `lipophilicity` (numeric LogD). Approximate estimates for triage/ranking, not absolute measurements.
- `artifacts.structure.url`, `artifacts.archive.url` (presigned, short-lived)
- `warnings` — optional array of `{code, message}` quality flags (e.g. `low_confidence`, `unusual_geometry`); empty or absent on clean results. Surface them when presenting top hits.

Rank from `results/index.jsonl` after `download-results`. `binding_confidence` and `optimization_score` are parallel intents (hit discovery vs. lead optimization), not a primary/fallback hierarchy. Sort by whichever matches the user's goal.

## Escape hatch

- <https://api.boltz.bio/docs/api/python/resources/small_molecule/subresources/design/methods/start>
- `boltz-api small-molecule:design start --help`
