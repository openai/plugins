# Small Molecule ADME — Payload Reference

Covers the `predictions:adme` endpoint. Prefer a single merged top-level `--input` payload for `estimate-cost` / `run` / `start`. Field names below are **API body field names**, not CLI flag names.

Minimal CLI pattern:

```bash
boltz-api predictions:adme estimate-cost --model adme-v1 --input @yaml:///absolute/path/payload.yaml
boltz-api predictions:adme run --model adme-v1 --idempotency-key "<run-name>" \
  --input @yaml:///absolute/path/payload.yaml --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments" --poll-interval-seconds 5
```

`--model adme-v1` is required on every call. Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win.

## Contents

- [Top-level request](#top-level-request)
- [`molecules`](#molecules)
- [Batch limit](#batch-limit)
- [Cost](#cost)
- [Outputs](#outputs)
- [Errors](#errors)
- [`start` + `retrieve` (async)](#start--retrieve-async)
- [Escape hatch](#escape-hatch)

## Top-level request

```yaml
# payload.yaml
molecules:
  - smiles: "CC(=O)Oc1ccccc1C(=O)O"
    id: aspirin
  - smiles: "CCO"
    id: ethanol
```

Top-level fields:

- `molecules` (required) — list of molecules to score. No target, pocket, or reference ligands — ADME is structure-free.

Also passed as separate flags:

- `--model adme-v1` (required)
- `--idempotency-key <slug>`
- `--workspace-id <id>` (admin keys only)

## `molecules`

Fields:

- `smiles` (required) — SMILES string (min length 1).
- `id` (optional) — client-supplied identifier (1–128 chars); echoed back as `external_id` on each result. Results are returned in the same order as this list.

## Batch limit

**At most 128 molecules per request.** 129+ is rejected:

```
400 VALIDATION_ERROR: input.molecules must contain at most 128 items
```

For larger libraries, split into batches of ≤128 and submit one request per batch, then merge the per-batch outputs.

## Cost

Cost is quoted by `estimate-cost` on the exact payload:

```bash
boltz-api --format json predictions:adme estimate-cost --model adme-v1 --input @yaml:///absolute/path/payload.yaml
# -> { "estimated_cost_usd": "...", "breakdown": { "application": "adme", "num_units": <n>, "cost_per_unit_usd": "..." } }
```

ADME is priced at **$0.01 per molecule** (size-independent). `estimate-cost` returns the authoritative total — always report it.

## Outputs

`run` waits for completion and persists to `<root-dir>/<run-name>/`:

- `.boltz-run.json` — local checkpoint (`run_type: "adme"`, remote `run_id`, status, request fingerprint).
- `run.json` — full remote record. The results live in `output.molecules[]`.

There are **no structure files or archives** — ADME returns scalar/categorical values only.

Per-molecule fields in `run.json` → `output.molecules[]`:

- `id` — server-assigned `adme_mol_*` ID
- `external_id` — your input `id`
- `smiles` — the scored SMILES
- `status` — `succeeded` or `failed`
- `error` — `null` on success; on failure an object `{code, message}` (e.g. `{"code": "adme_enumeration_failed", "message": "Invalid SMILES"}`)
- `adme` — present on success:
  - `solubility` — categorical: `high-confidence`, `medium-confidence`, or `high-risk`
  - `permeability` — numeric score
  - `lipophilicity` — numeric LogD

ADME values are approximate estimates intended for triage and ranking, not absolute measurements.

## Errors

Failures are per-molecule, not per-batch: one invalid SMILES yields `status: "failed"` (with `adme: null`) and an `error` object `{code, message}` — e.g. `{"code": "adme_enumeration_failed", "message": "Invalid SMILES"}` — for that molecule while the rest succeed. Always check each molecule's `status` before reporting its `adme`.

## `start` + `retrieve` (async)

`run` is the simplest path (submit + wait + persist). If you need to submit without blocking, use `start` then poll `retrieve`:

```bash
PREDICTION_ID=$(boltz-api --format raw predictions:adme start --model adme-v1 \
  --input @yaml:///absolute/path/payload.yaml | jq -r '.id')
boltz-api predictions:adme retrieve --id "$PREDICTION_ID"   # rerun until status is succeeded
```

`retrieve` returns the same record shape as `run.json`, with `output.molecules[]` once `status` is `succeeded`. Use `boltz-api predictions:adme list` to find prior predictions when no local run dir exists.

## Escape hatch

- <https://api.boltz.bio/docs/api/resources/predictions/subresources/adme/methods/start/>
- <https://api.boltz.bio/docs/guides/small-molecule-adme/>
- `boltz-api predictions:adme run --help`
