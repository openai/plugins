# Structure and Binding — Payload Reference

This covers the `predictions:structure-and-binding` endpoint. The request body becomes the `--input` object passed via `@yaml:///absolute/path/payload.yaml`. Field names below are **API body field names** (what you write in the YAML) — not CLI flag names.

## Contents

- [Top-level request](#top-level-request)
- [Entity types](#entity-types)
- [`binding`](#binding)
- [`bonds`](#bonds)
- [`constraints`](#constraints)
- [`model_options`](#model_options)
- [`templates`](#templates)
- [MSA control](#msa-control)
- [Structure templates in a constraint / binding setup](#structure-templates-in-a-constraint--binding-setup)
- [Outputs (after `download-results`)](#outputs-after-download-results)
- [400 validation quirk](#400-validation-quirk)
- [Escape hatch](#escape-hatch)

## Top-level request

```yaml
# payload.yaml
entities:
  - type: protein
    chain_ids: [A]
    value: MKTAYIAKQRQISFVKSHFSRQ
  - type: ligand_smiles
    chain_ids: [B]
    value: CCO
binding:
  type: ligand_protein_binding
  binder_chain_id: B
num_samples: 1
model_options:
  recycling_steps: 3
  sampling_steps: 200
  step_scale: 1.638
```

Top-level fields:

- `entities` (required) — list of polymer / ligand entities. Chain IDs across entities must be unique.
- `binding` (optional) — include only when you want binding metrics. Two variants below.
- `num_samples` (optional, 1-10) — structure samples to generate. Omit for the server default.
- `bonds` (optional) — custom covalent bonds; see below.
- `constraints` (optional) — pocket / contact constraints; see below.
- `model_options` (optional) — see below.
- `templates` (optional) — up to **4** CIF/PDB templates to guide protein-chain geometry (Boltz-2.1); see [`templates`](#templates).

Also passed as separate `start` flags, not inside the body:

- `--model boltz-2.1` (currently the only option)
- `--idempotency-key <slug>`
- `--workspace-id <id>` (admin keys only)

## Entity types

All entities take `type`, `chain_ids`, `value`.

### `protein`

```yaml
- type: protein
  chain_ids: [A]
  value: MKTAYIAKQRQISFVKSHFSRQ
  cyclic: false              # optional
  modifications: []          # optional; server defaults to [] if omitted
  # msa: <optional>          # omit = automatic MSA generation; see "MSA control" below
```

### `rna`

```yaml
- type: rna
  chain_ids: [B]
  value: ACGUN
  cyclic: false
  modifications: []
```

### `dna`

```yaml
- type: dna
  chain_ids: [C]
  value: ACGTN
  cyclic: false
  modifications: []
```

### `ligand_smiles`

```yaml
- type: ligand_smiles
  chain_ids: [D]
  value: "CCO"
```

### `ligand_ccd`

```yaml
- type: ligand_ccd
  chain_ids: [E]
  value: ATP
```

### Polymer modifications

Each entry in `modifications`:

```yaml
modifications:
  - residue_index: 12           # 0-based
    type: ccd
    value: MSE
```

`type` must be `ccd` — SMILES polymer modifications are **not** supported (the API rejects them with `modifications[].type must be "ccd"`).

## `binding`

Include only when you want binding metrics.

### Ligand–protein

```yaml
binding:
  type: ligand_protein_binding
  binder_chain_id: D
```

Constraints:

- `binder_chain_id` must reference a single ligand chain.
- Binder ligand must have fewer than 50 atoms.
- The entity set may only contain proteins and ligands (no RNA / DNA).

### Protein–protein

```yaml
binding:
  type: protein_protein_binding
  binder_chain_ids: [B]
```

Returned binding metrics (under `output.binding_metrics`):

- For `ligand_protein_binding`: `{binding_confidence, optimization_score, type: "ligand_protein_binding_metrics"}`.
- For `protein_protein_binding`: `{binding_confidence, type: "protein_protein_binding_metrics"}` — **no `optimization_score`**.

What they mean:

- `binding_confidence` (0–1) — confidence that binding occurs; the primary signal for whether this complex binds.
- `optimization_score` — ranks **binding strength** for lead optimization (higher = stronger predicted binding). Emitted only for `ligand_protein_binding`, not `protein_protein_binding`.

## `bonds`

```yaml
bonds:
  - atom1:
      type: polymer_atom
      chain_id: A
      residue_index: 12        # 0-based
      atom_name: SG
    atom2:
      type: ligand_atom
      chain_id: D
      atom_name: C1
```

Atom variants:

- `{type: polymer_atom, chain_id, residue_index, atom_name}` — residue_index is 0-based.
- `{type: ligand_atom, chain_id, atom_name}`. **Atom-level ligand references support `ligand_ccd` only** — referencing a `ligand_smiles` chain by atom is rejected (`bad_request: … references SMILES ligand chain … Use ligand_ccd instead`). Use a `ligand_ccd` entity for any atom-level bond/contact.

## `constraints`

### Pocket constraint

```yaml
constraints:
  - type: pocket
    binder_chain_id: D
    contact_residues:
      A: [10, 11, 35]          # 0-based residue indices on each target chain
    max_distance_angstrom: 6.0
    force: false                # optional
```

### Contact constraint

```yaml
constraints:
  - type: contact
    max_distance_angstrom: 5.0
    token1:
      type: polymer_contact
      chain_id: A
      residue_index: 42        # 0-based
    token2:
      type: ligand_contact
      chain_id: D
      atom_name: C1
    force: false
```

Token variants:

- `{type: polymer_contact, chain_id, residue_index}` — residue_index is 0-based.
- `{type: ligand_contact, chain_id, atom_name}`. As with bonds, atom-level ligand contacts support `ligand_ccd` only — `ligand_smiles` chains cannot be referenced by atom.

## `model_options`

```yaml
model_options:
  recycling_steps: 3           # default 3 (per spec)
  sampling_steps: 200          # default 200 (per spec)
  step_scale: 1.638            # default 1.638 (per spec)
```

Hosted API Reference bounds:

- `recycling_steps >= 1`
- `sampling_steps >= 1`
- `1.3 <= step_scale <= 2`

## `templates`

Up to **4** CIF/PDB templates to guide protein-chain geometry (Boltz-2.1). Each template maps request chains to chains in the template file:

```yaml
templates:
  - template_structure:
      type: url                       # or base64 (use @data:/// for a local file)
      url: "https://files.rcsb.org/download/1ABC.cif"
    template_chains:
      - input_chain_id: A             # chain in THIS request
        template_chain_id: A          # corresponding chain in the template file
    force_threshold_angstroms: 10.0   # optional; omit to use the template without forcing
```

`template_chains` entries are **objects** (`{input_chain_id, template_chain_id}`), not bare chain-ID strings. This is distinct from embedding a CIF as raw structure bytes (see the next section).

## MSA control

By default (omit `msa` on every protein entity) Boltz generates an MSA automatically. To override per protein entity:

- `msa: {type: empty}` — single-sequence mode (no MSA).
- `msa: {type: custom, format: a3m|csv, source: {url: "..."}}` — user-provided MSA. Base64 uploads use media type `text/x-a3m` (A3M) or `text/csv` (CSV).

Custom and automatic MSAs cannot be mixed: if any protein entity uses a custom MSA, every other protein entity must use `custom` or `empty`.

## Structure templates in a constraint / binding setup

If you're embedding a CIF/PDB file as a source of structure coordinates (for example in a custom constraint body), use `@data://` in the CLI, not `@file://`:

```yaml
structure:
  type: base64
  media_type: chemical/x-cif
  data: "@data:///abs/path/template.cif"
```

Alternatively, use `{type: url, url: "https://..."}` to point at a presigned CIF URL.

## Outputs (after `download-results`)

Under `<output-root>/<run-name>/`:

- `.boltz-run.json` — run metadata, cursor, idempotency key, timing
- `outputs/archive.tar.gz` — contains `prediction/metrics.json`, `prediction/sample_*_predicted_structure.cif`, `prediction/sample_*_pae.npz`

Metrics in `metrics.json` are split across `best_sample.metrics`, each `all_sample_results[].metrics`, and a separate top-level `binding_metrics` object.

**Per-sample metrics** (nine lowercase keys, present on both `best_sample.metrics` and each entry in `all_sample_results[].metrics`):

- `structure_confidence` — aggregate confidence
- `ptm` — predicted TM-score
- `iptm` — interface predicted TM-score
- `ligand_iptm` — interface iptm restricted to ligand chains (**only when ligands are present**)
- `protein_iptm` — interface iptm restricted to protein chains (**only for multi-protein complexes**)
- `complex_plddt` — pLDDT averaged across the complex
- `complex_iplddt` — pLDDT restricted to interface residues
- `complex_pde` — predicted distance error across the complex
- `complex_ipde` — predicted distance error restricted to interface residues

**Binding metrics** (top-level `binding_metrics`, only present when `binding` was requested):

- `ligand_protein_binding` → `{binding_confidence, optimization_score, type: "ligand_protein_binding_metrics"}`
- `protein_protein_binding` → `{binding_confidence, type: "protein_protein_binding_metrics"}` — **no `optimization_score`**

Uppercase aliases like `pLDDT`, `pTM`, `ipTM`, `PDE`, `ipDE` are **not** what the server emits — use the lowercase keys above.

## 400 validation quirk

`predictions:structure-and-binding` is the one endpoint that may return `{"code": "VALIDATION_ERROR", "message": "Request validation failed"}` with **no `details` field**. If you hit this, inspect `entities`, `binding`, and `constraints` by hand — the other four endpoints surface a field-level path.

## Escape hatch

For any field not listed here:

- <https://api.boltz.bio/docs/api/python/resources/predictions/subresources/structure_and_binding/methods/start>
- `boltz-api predictions:structure-and-binding start --help` — flag names only; schema is not in the CLI help.
