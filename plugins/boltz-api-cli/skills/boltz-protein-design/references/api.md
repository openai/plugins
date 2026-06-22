# Protein Design — Payload Reference

Covers the `protein:design` endpoint. Prefer a single merged top-level `--input` payload. Field names are **API body field names**.

Minimal CLI pattern:

```bash
boltz-api protein:design estimate-cost --input @yaml:///absolute/path/payload.yaml
boltz-api protein:design start --idempotency-key "<run-name>" --input @yaml:///absolute/path/payload.yaml --raw-output --transform id
```

In permission-gated agents, keep the submit command as a top-level `boltz-api ... start` invocation. Read the printed job ID from stdout and paste it into the later `download-results` command.

Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win. Direct object flags still work as overrides, such as `--target @yaml:///absolute/path/target.yaml` or `--binder-specification @json:///absolute/path/binder.json`. Piped YAML / JSON on stdin remains supported when you need it, but the body must use API field names.

## Contents

- [Top-level request](#top-level-request)
- [`num_proteins` minimum](#num_proteins-minimum)
- [Cost](#cost)
- [`binder_specification` — variant 1: `boltz_curated`](#binder_specification--variant-1-boltz_curated)
- [`binder_specification` — variant 2: `structure_template`](#binder_specification--variant-2-structure_template)
- [`binder_specification` — variant 3: `no_template`](#binder_specification--variant-3-no_template)
- [Sequence DSL (`designed_protein.value`)](#sequence-dsl-designed_proteinvalue)
- [`rules`](#rules)
- [`target` — variant 1: `structure_template`](#target--variant-1-structure_template)
- [`target` — variant 2: `no_template`](#target--variant-2-no_template)
- [`bonds` and `constraints` shapes](#bonds-and-constraints-shapes)
- [Outputs (after `download-results`)](#outputs-after-download-results)
- [Escape hatch](#escape-hatch)

## Top-level request

```yaml
# payload.yaml
num_proteins: 10
target:
  type: structure_template
  structure:
    type: base64
    media_type: chemical/x-cif
    data: "@data:///abs/path/target.cif"
  chain_selection:
    A:
      chain_type: polymer
      crop_residues: all
      epitope_residues: [42, 43, 44]
binder_specification:
  type: boltz_curated
  binder: boltz_nanobody
  rules:
    max_hydrophobic_fraction: 0.5
```

Top-level fields:

- `num_proteins` (required) — number to generate. **Must be between 10 and 1,000,000** (server rejects outside this range).
- `target` (required) — discriminated union: `structure_template` or `no_template`. Identical shape to protein-screen.
- `binder_specification` (required) — discriminated union: `boltz_curated`, `structure_template`, or `no_template`. See below.

Also passed as separate `start` flags:

- `--idempotency-key <slug>`
- `--workspace-id <id>` (admin keys only)

## `num_proteins` minimum

Server rejects `num_proteins < 10` or `> 1000000` with `VALIDATION_ERROR`. Validate client-side before submitting.

## Cost

Cost is tiered by **total complex length** (target crop + binder), not flat per design, and both the target crop and the designed binder count toward the length — so the tier is easy to misjudge. `estimate-cost` returns `breakdown.{application, cost_per_unit_usd, num_units}` — `num_units` equals `num_proteins`, and the complex-length effect rides in `cost_per_unit_usd` (small targets cost less per design, large ones materially more). It is the **only** source to use: quote `estimated_cost_usd` from it and never compute, estimate, or state a cost yourself.

## `binder_specification` — variant 1: `boltz_curated`

Recommended default for antibody and nanobody design. Boltz chooses from maintained antibody/nanobody scaffold template lists during design. In the API docs this shape appears as `BoltzCuratedBinderSpec` on requests and `BoltzCuratedBinderSpecResponse` on retrieved run records. Before using it, ask the user to confirm they want the curated default rather than a custom scaffold with explicit CDR/motif control.

Use `boltz_nanobody` for nanobody/VHH requests and `boltz_antibody` for antibody/Fab requests. Do not include `modality`, `entities`, `structure`, or `chain_selection` in this variant.

```yaml
binder_specification:
  type: boltz_curated
  binder: boltz_nanobody             # or boltz_antibody
  rules:
    excluded_sequence_motifs: [NXS]  # optional; only add rules on request
```

## `binder_specification` — variant 2: `structure_template`

Use when redesigning regions of an existing binder scaffold.

```yaml
binder_specification:
  type: structure_template
  modality: peptide                # or antibody | nanobody | custom_protein
  structure:
    type: url
    url: "https://example.com/binder.cif"
  chain_selection:
    B:
      chain_type: polymer
      crop_residues: all           # or [0, 1, 2, ...]
      design_motifs:
        - type: replacement
          start_index: 0           # 0-based, inclusive
          end_index: 5             # 0-based, **inclusive** — residues start_index..end_index are replaced
          design_length_range:
            min: 4
            max: 8
  rules:
    excluded_amino_acids: [C, P]
```

### `structure` source variants

URL or base64 — same as target:

```yaml
structure:
  type: base64
  media_type: chemical/x-cif
  data: "@data:///abs/path/binder.cif"   # prefer @data:// for local CIF/PDB bytes
```

### `chain_selection` values

Polymer chain:

```yaml
B:
  chain_type: polymer
  crop_residues: all               # or [int, ...]
  design_motifs:                    # see motif types below
    - ...
```

Ligand chain:

```yaml
B:
  chain_type: ligand
```

### Motif types

#### `replacement`

```yaml
- type: replacement
  start_index: 0                    # 0-based, inclusive
  end_index: 5                      # 0-based, **inclusive**
  design_length_range:
    min: 4
    max: 8
```

Residues from `start_index` to `end_index` inclusive are replaced with a new designed segment. Example: on a 17-mer scaffold with `start_index: 2, end_index: 15`, residues 2..15 (14 residues) are redesigned and residues 0..1 + 16 stay fixed. Verify sequence length on a test output before committing to a template.

#### `insertion`

```yaml
- type: insertion
  after_residue_index: 12           # 0-based; use -1 to insert before residue 0
  design_length_range:
    min: 3
    max: 6
```

All residue indices are 0-based.

## `binder_specification` — variant 3: `no_template`

Use when generating from sequence components + the DSL. For antibody or nanobody requests, prefer `boltz_curated` unless the user confirms they want direct sequence/scaffold control.

```yaml
binder_specification:
  type: no_template
  modality: custom_protein          # or peptide | antibody | nanobody
  entities:
    - type: designed_protein
      chain_ids: [B]
      value: "MKTAYI5..10VKSHFSRQ"
  bonds: []                          # optional
  rules:
    max_hydrophobic_fraction: 0.5
```

Constraints:

- At least one entity must be `type: designed_protein`.
- `modifications` on fixed `protein`/`rna`/`dna` entities is optional (defaults to `[]`).
- `designed_protein` does NOT take `modifications`.
- If `bonds` references an atom in a designed protein chain, residue indices are counted against the minimum designed length for each DSL segment. Example: in `1..3C1..2`, the fixed `C` is residue index 1 (0-based) because the first designed segment uses its minimum length of 1.

Allowed entity types in `binder_specification.entities` (for `no_template`):

- `designed_protein` — the sequence DSL target
- `protein`, `rna`, `dna` — fixed partners
- `ligand_smiles`, `ligand_ccd` — fixed cofactors

## Sequence DSL (`designed_protein.value`)

- Uppercase amino acid letters stay fixed.
- Bare integer `N` means a designed segment of exactly length `N`.
- `MIN..MAX` means a designed segment with variable length from `MIN` to `MAX`.

Examples:

- `"20"` — generate a 20-residue designed sequence
- `"5..10"` — variable-length designed segment
- `"ACDE8GHI"` — fixed `ACDE`, then 8 designed residues, then fixed `GHI`
- `"MKTAYI5..10VKSHFSRQ"` — fixed prefix and suffix with a variable-length designed middle

## `rules`

Optional, applies to all `binder_specification` variants. Any of:

- `excluded_amino_acids: [<one-letter codes>]` — never emit these residues in designed positions.
- `excluded_sequence_motifs: [<motif strings>]` — reject designs containing these patterns. Use `X` as a single-position wildcard (e.g. `"XPX"`).
- `max_hydrophobic_fraction: <float>` — cap hydrophobic content in designed regions.

## `target` — variant 1: `structure_template`

```yaml
target:
  type: structure_template
  structure:
    type: url
    url: "https://example.com/target.cif"
  chain_selection:
    A:
      chain_type: polymer
      crop_residues: all              # or [int, ...]
      epitope_residues: [42, 43, 44]  # optional; subset of crop_residues
      flexible_residues: [40, 41, 42] # optional; subset of crop_residues
      non_binding_residues: [50, 51]  # optional; subset of crop_residues, must NOT overlap epitope_residues
```

Same semantics as protein-screen: `epitope_residues` / `flexible_residues` must be subsets of `crop_residues`, all 0-based.

## `target` — variant 2: `no_template`

```yaml
target:
  type: no_template
  entities:
    - type: protein
      chain_ids: [A]
      value: "MKTAYIAKQRQISFVKSHFSRQ"
  epitope_residues:
    A: [42, 43, 44]                   # optional; 0-based
  non_binding_residues:
    A: [50, 51]                       # optional; 0-based; must NOT overlap epitope_residues
  epitope_ligand_chains: [L]          # optional
  bonds: []                           # optional
  constraints: []                     # optional
```

Optional fields: `epitope_residues`, `non_binding_residues` (residues where binder contact is discouraged — 0-based, within `crop_residues`, must not overlap `epitope_residues`), `epitope_ligand_chains`, `bonds`, `constraints`.

## `bonds` and `constraints` shapes

Same as the structure-and-binding skill — see `references/api.md` of that skill for full detail. Only include when the user explicitly asks for geometry constraints.

## Outputs (after `download-results`)

Under `<output-root>/<run-name>/`:

- `.boltz-run.json`
- `run.json` — sanitized remote run record
- `results/index.jsonl` — one generated design per line, copied from list-results metadata plus local artifact paths
- `results/<pres_*>/metadata.json` — per-result metadata copied from the list-results record
- `results/<pres_*>/archive.tar.gz` — one dir per generated design
- `results/<pres_*>/files/result/{metrics.json, <result-id>_predicted.cif, pae.npz}` (the CIF is named `<pres_*>_predicted.cif` — prefer the `paths.structure` field from `index.jsonl` over hard-coding the filename)

Per-result fields (available in `results/index.jsonl`, `results/<pres_*>/metadata.json`, and the `list-results` stream):

- `id` — server-assigned `pres_*` ID
- `entities` — generated designs. **Type-flip gotcha:** the binder entity comes back as `type: "protein"` (not `"designed_protein"`), with the DSL resolved to a real AA sequence in `value`. Select the binder by `chain_ids` (the ID assigned at submit time), **not** by `type == "designed_protein"` — the latter match returns zero results.
- `metrics.binding_confidence` — **primary ranking metric**
- `metrics.structure_confidence`
- `metrics.iptm` (higher is better)
- `metrics.min_interaction_pae` (lower is better)
- `metrics.helix_fraction`, `metrics.sheet_fraction`, `metrics.loop_fraction`
- `artifacts.structure.url`, `artifacts.archive.url` (presigned, short-lived)
- `warnings` — optional array of `{code, message}` quality flags (e.g. `low_confidence`, `unusual_geometry`); empty or absent on clean results. Surface them when presenting top designs.

`optimization_score` is **not emitted** for `protein:design`. Sorting by it yields an empty list.

Rank from `results/index.jsonl` after `download-results` by `binding_confidence` descending. Use `iptm` (higher better) and `min_interaction_pae` (lower better) as tiebreakers.

## Escape hatch

- <https://api.boltz.bio/docs/api/resources/protein/subresources/design/methods/start/>
- `boltz-api protein:design start --help`
