# Protein Screen — Payload Reference

Covers the `protein:library-screen` endpoint. Prefer a single merged top-level `--input` payload. Field names are **API body field names**.

Minimal CLI pattern:

```bash
boltz-api protein:library-screen estimate-cost --input @yaml:///absolute/path/payload.yaml
boltz-api protein:library-screen start --idempotency-key "<run-name>" --input @yaml:///absolute/path/payload.yaml --raw-output --transform id
```

In permission-gated agents, keep the submit command as a top-level `boltz-api ... start` invocation. Read the printed job ID from stdout and paste it into the later `download-results` command.

Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win. Direct object flags still work as overrides, such as `--target @yaml:///absolute/path/target.yaml` or repeated `--protein @json:///absolute/path/protein-1.json` entries. Piped YAML / JSON on stdin remains supported when you need it, but the body must use API field names.

## Contents

- [Top-level request](#top-level-request)
- [`proteins` (candidate library)](#proteins-candidate-library)
- [`target` — variant 1: `structure_template`](#target--variant-1-structure_template)
- [`target` — variant 2: `no_template`](#target--variant-2-no_template)
- [`bonds` and `constraints`](#bonds-and-constraints)
- [Cost](#cost)
- [Outputs (after `download-results`)](#outputs-after-download-results)
- [Escape hatch](#escape-hatch)

## Top-level request

```yaml
# payload.yaml
proteins:
  - entities:
      - type: protein
        chain_ids: [B]
        value: "MKTAYIAKQRQISFVKSHFSRQ"
  - entities:
      - type: protein
        chain_ids: [B]
        value: "AVGRHEAVGTYCR"
target:
  type: no_template
  entities:
    - type: protein
      chain_ids: [A]
      value: "QRTVEKATLLPNMPGQVLGHSSVLA"
  epitope_residues:
    A: [42, 43, 44]
```

Top-level fields:

- `proteins` (required) — list of candidate binder complexes. Each entry is a mini-complex with its own `entities` list.
- `target` (required) — discriminated union: `structure_template` or `no_template`.

Also passed as separate `start` flags:

- `--idempotency-key <slug>`
- `--workspace-id <id>` (admin keys only)

## `proteins` (candidate library)

Each entry represents one candidate binder complex to score against the target. For a simple sequence library each entry contains one protein entity:

```yaml
proteins:
  - entities:
      - type: protein
        chain_ids: [B]
        value: "MKTAYIAKQRQISFVKSHFSRQ"
    id: binder-001                 # optional; returned as external_id
```

Multi-chain candidates (e.g. antibody heavy + light) put multiple entities in one entry:

```yaml
proteins:
  - entities:
      - type: protein
        chain_ids: [H]
        value: "EVQLVES...QVTVSS"
      - type: protein
        chain_ids: [L]
        value: "DIQMTQ...VEIKR"
```

Supported entity types inside `proteins[].entities`:

- `protein`
- `rna`
- `dna`
- `ligand_smiles`
- `ligand_ccd`

Entity fields: `type`, `value`, `chain_ids`, `modifications` (optional), `cyclic` (optional bool).

Each `proteins[]` entry may also include an optional client-side `id`. The server echoes it as `external_id` on the corresponding result; use it to map ranked hits back to FASTA records, CSV rows, or library IDs.

## `target` — variant 1: `structure_template`

Use when the user has a 3D structure (CIF/PDB file or URL).

```yaml
target:
  type: structure_template
  structure:
    type: url
    url: "https://example.com/target.cif"
  chain_selection:
    A:
      chain_type: polymer
      crop_residues: all                # or [0, 1, 2, ...] for specific 0-based indices
      epitope_residues: [42, 43, 44]    # optional; subset of crop_residues
      flexible_residues: [40, 41, 42]   # optional; subset of crop_residues
    B:
      chain_type: ligand
```

### `structure` source variants

URL:

```yaml
structure:
  type: url
  url: "https://example.com/target.cif"
```

Base64 (for a local file — use `@data://` in the CLI, which detects binary and encodes):

```yaml
structure:
  type: base64
  media_type: chemical/x-cif
  data: "@data:///abs/path/to/target.cif"
```

**Do not** use bare `@path/to/file.cif` here — automatic file-type detection has historically miscategorized CIF as plain text and broken the server parser. Prefer `@data://` explicitly.

### `chain_selection` values

Polymer chain:

```yaml
A:
  chain_type: polymer
  crop_residues: all                  # or [int, ...]
  epitope_residues: [int, ...]        # optional; must be subset of crop_residues
  flexible_residues: [int, ...]       # optional; must be subset of crop_residues
  non_binding_residues: [int, ...]    # optional; subset of crop_residues, must NOT overlap epitope_residues
```

Ligand chain:

```yaml
B:
  chain_type: ligand
```

All residue indices are 0-based.

## `target` — variant 2: `no_template`

Use when the user has only sequences.

```yaml
target:
  type: no_template
  entities:
    - type: protein
      chain_ids: [A]
      value: "QRTVEKATLLPNMPGQVLGHSSVLA"
      modifications: []               # optional
  epitope_residues:
    A: [42, 43, 44]                   # optional; 0-based
  epitope_ligand_chains: [C]          # optional
  bonds: []                           # optional
  constraints: []                     # optional
```

Optional fields:

- `epitope_residues` — `{chain_id: [0-based residue_index, ...]}`. Hints the binding epitope.
- `non_binding_residues` — `{chain_id: [0-based residue_index, ...]}`. Residues where binder contact is discouraged; must **not** overlap `epitope_residues` on the same chain.
- `epitope_ligand_chains` — list of ligand chain IDs if the epitope includes a ligand.
- `bonds`, `constraints` — same shapes as the structure-and-binding skill (see below).

## `bonds` and `constraints`

Only include when the user explicitly asks for geometry constraints.

### Bond shape

```yaml
bonds:
  - atom1:
      type: polymer_atom
      chain_id: A
      residue_index: 12       # 0-based
      atom_name: SG
    atom2:
      type: ligand_atom
      chain_id: D
      atom_name: C1
```

### Pocket constraint

```yaml
constraints:
  - type: pocket
    binder_chain_id: B
    contact_residues:
      A: [42]                 # 0-based
    max_distance_angstrom: 6.0
    force: false              # optional
```

### Contact constraint

```yaml
constraints:
  - type: contact
    max_distance_angstrom: 5.0
    token1:
      type: polymer_contact
      chain_id: A
      residue_index: 42       # 0-based
    token2:
      type: polymer_contact
      chain_id: B
      residue_index: 10
    force: false
```

Token variants: `polymer_contact {chain_id, residue_index}` or `ligand_contact {chain_id, atom_name}`.

**Atom-level ligand references (bonds and `ligand_contact`) support `ligand_ccd` only** — a `ligand_smiles` chain referenced by atom is rejected; use a `ligand_ccd` entity instead.

## Cost

Cost is tiered by **total complex length** (target + candidate), so there is no flat per-candidate rate to cite — it changes with size. Run `estimate-cost` on the full payload and quote only the `estimated_cost_usd` it returns; do not state or estimate a dollar figure yourself.

## Outputs (after `download-results`)

Under `<output-root>/<run-name>/`:

- `.boltz-run.json`
- `run.json` — sanitized remote run record
- `results/index.jsonl` — one scored candidate per line, copied from list-results metadata plus local artifact paths
- `results/<pres_*>/metadata.json` — per-result metadata copied from the list-results record
- `results/<pres_*>/archive.tar.gz` — one dir per scored candidate
- `results/<pres_*>/files/result/{metrics.json, <result-id>_predicted.cif, pae.npz}` (the CIF is named `<pres_*>_predicted.cif` — prefer the `paths.structure` field from `index.jsonl` over hard-coding the filename)

Per-result fields (available in `results/index.jsonl`, `results/<pres_*>/metadata.json`, and the `list-results` stream):

- `id` — server-assigned `pres_*` ID
- `external_id` — echoed from the optional `id` on your input `proteins[]` entry
- `entities` — echoed input entities for this candidate
- `metrics.binding_confidence` — **primary ranking metric**
- `metrics.structure_confidence`
- `metrics.iptm` (higher is better)
- `metrics.min_interaction_pae` (lower is better)
- `metrics.helix_fraction`, `metrics.sheet_fraction`, `metrics.loop_fraction`
- `artifacts.structure.url`, `artifacts.archive.url` (presigned, short-lived)
- `warnings` — optional array of `{code, message}` quality flags (e.g. `low_confidence`, `unusual_geometry`); empty or absent on clean results. Surface them when presenting top hits.

`optimization_score` is **not emitted** for `protein:library-screen`. Sorting by it returns an empty list.

Rank from `results/index.jsonl` after `download-results` by `binding_confidence` descending. Use `iptm` (higher better) and `min_interaction_pae` (lower better) as tiebreakers.

## Escape hatch

- <https://api.boltz.bio/docs/api/python/resources/protein/subresources/library_screen/methods/start>
- `boltz-api protein:library-screen start --help`
