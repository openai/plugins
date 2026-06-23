---
name: boltz-structure-and-binding
description: Predict structures and binding for one defined complex with Boltz. Use when folding a protein, RNA, DNA, or ligand complex, docking one ligand, predicting an interface, or scoring binding. Not for screening libraries or design.
---

## Workflow

If `boltz-api` is missing from `PATH`, use `boltz-cli-setup` for install/update guidance before retrying.
If a command reports missing or expired authentication, use `boltz-cli-setup` to start `boltz-api auth login --device-code` before retrying; do not ask permission first.
If the agent host sandbox blocks `boltz-api` install/auth/API calls, use `boltz-cli-setup` to request the host sandbox bypass/escalation needed for user-wide CLI install, browser login, credential storage, temp files, or API access before retrying.

Use this skill for one defined complex, not a library workflow.

1. Normalize the inputs into `entities`. Each entity is **`{type, chain_ids, value}`** — note plural `chain_ids` (an array, even for one chain) and the field is `value`, **not** `sequence`:

   ```json
   {"entities": [{"type": "protein", "chain_ids": ["A"], "value": "MKTAYIAKQRQISFVKSHFSRQ"}]}
   ```

   `type` is one of `protein | rna | dna | ligand_smiles | ligand_ccd`. Chain IDs go in entity order (`A`, `B`, `C`, …) unless the user specifies otherwise. Read `references/api.md` for per-type field variants (`cyclic`, `modifications`, ligand CCD codes, etc.) **before** authoring your first payload — agent guesses like `sequence:` or `chain_id: "A"` (singular) fail with unclear 400 errors.
2. If the user wants binding metrics, add a flat `binding` block with an explicit `type` field. For ligand-protein binding use:

   ```yaml
   binding:
     type: ligand_protein_binding
     binder_chain_id: B
   ```

   For protein-protein binding use:

   ```yaml
   binding:
     type: protein_protein_binding
     binder_chain_ids: [B]
   ```

   Do not nest the variant name under `binding` (for example, no `binding.ligand_protein_binding` object).
3. Supported optional features include `constraints`, `bonds`, `modifications`, `model_options`, and binding metrics; only add them if the user asks. Read [references/api.md](references/api.md) for exact shapes and examples.
4. Author the payload YAML or JSON, run `estimate-cost`, show the USD cost, wait for explicit confirmation.
5. `start` to submit (synchronous). Capture the ID.
6. Launch `download-results` with the agent runtime's background/non-blocking command facility so polling + download continue without blocking the agent session. In Claude Code, use Bash with `run_in_background: true`. In Codex, run `download-results` as a foreground shell command with `yield_time_ms: 1000`; if Codex returns a `session_id`, keep it for optional same-thread polling, but treat `download-status` plus the run directory as the durable source of truth. In Codex app/desktop runtimes that expose same-thread heartbeat automations, create a heartbeat that checks `download-status` periodically and posts a concise completion or failure update when the download reaches a terminal state. After launching the downloader, always report the job ID, run name, and output directory. Include the next check cadence if the heartbeat was created; otherwise include the `download-status` command.

## Command Pattern

```bash
# Replace placeholders with concrete absolute paths before running.
# Use a short descriptive run name, for example: sab-<target>-<ligand>-v1

# 1. estimate
boltz-api predictions:structure-and-binding estimate-cost \
  --model boltz-2.1 \
  --input @yaml:///absolute/path/payload.yaml

# 2. confirm with user, then submit
boltz-api predictions:structure-and-binding start \
       --model boltz-2.1 \
       --idempotency-key "<run-name>" \
       --input @yaml:///absolute/path/payload.yaml \
       --raw-output --transform id

# 3. Copy the printed job ID into this command, then launch it in the agent
# runtime's background/non-blocking mode.
# Claude Code: Bash with run_in_background=true.
# Codex: foreground shell command with yield_time_ms=1000; keep the returned session_id if one is provided.
# Do not append "&" or use nohup in Codex.
boltz-api download-results \
  --id "<job-id-from-start>" --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments" \
  --poll-interval-seconds 10
# -> /absolute/path/boltz-experiments/<run-name>/outputs/archive.tar.gz, .boltz-run.json
```

## Always Do This

- Keep payload field names exactly as the API body names shown in `references/api.md`; then pass the merged payload with `--input @yaml:///absolute/path/payload.yaml` or `@json:///absolute/path/payload.json`. Never use `@./payload.yaml` or `@file://` for object-typed payloads.
- Use absolute paths for the output root, payload files, and embedded structure files. Do not `cd` into the run directory for follow-up commands; pass the same `--root-dir` and use absolute paths so later relative paths do not drift.
- Residue indices are 0-based wherever the payload asks for residue positions (constraints, modifications, contact tokens).
- For CIF/PDB bytes embedded in `--target` / `structure.data`, use `@data:///absolute/path/file.cif` — it detects binary and base64-encodes. Don't use bare `@path` for binary data.
- Use the same slug as both `--idempotency-key` at submit time and `--name` at download time so re-runs are idempotent and resume from `.boltz-run.json`.
- In permission-gated agents such as Claude Code, keep each Boltz call as a top-level command that starts with `boltz-api`. Prefer concrete arguments over `sh -c`, inline environment assignments, aliases, wrapper scripts, loops, or pipelines around the `boltz-api` invocation unless the user already allowed that exact command form. Use `--raw-output --transform id`, read the printed ID, then paste that literal ID into the next `download-results` command.
- Prefer the agent runtime's background/non-blocking command mode for `download-results`. In Codex specifically, keep `download-results` in the foreground and set the shell tool yield to 1000 ms; Codex will return a `session_id` if the command is still running. Do not append `&` or use `nohup` in Codex because the tool runner may clean up shell-backgrounded descendants before `.boltz-run.json` is fully written.
- After the background/session starts, do not manually wait on it or run ad hoc polling loops. `download-results` emits JSONL progress on stderr by default; add `--progress-format text --verbose` only when you explicitly want human-readable logs.
- In Codex app/desktop runtimes with same-thread heartbeat automation support, schedule a heartbeat after launching `download-results`. The heartbeat should run `boltz-api --format json download-status --name "<run-name>" --root-dir "/absolute/path/boltz-experiments"` on a sensible cadence, post only material status changes or terminal completion/failure, and stop once terminal. Poll the saved `session_id` with an empty `write_stdin` only for interactive, user-requested progress checks. Do not loop `retrieve` yourself.
- If the current host has no heartbeat automation support, do not claim an automatic next check. Report the job ID, run name, output directory, and the command needed to check `download-status`.
- If detached download needs to be restarted, re-run `boltz-api download-results` with the same `--name "<run-name>"` and the same `--root-dir`.
- Poll interval: keep `--poll-interval-seconds 10` for SAB — predictions usually finish in under a few minutes.
- Cost: there is no published per-unit rate to cite for SAB — run `estimate-cost` and state only the figure it returns. Don't estimate or comment on cost.

## Escape Hatch

For anything not covered in `references/api.md`:

- Payload reference: <https://api.boltz.bio/docs/api/python/resources/predictions/subresources/structure_and_binding/methods/start>
- CLI flag names: `boltz-api predictions:structure-and-binding start --help` (schema details aren't there — just flag names and types)

Read [references/api.md](references/api.md) for entity shapes, binding variants, bonds, constraints, model options, and input examples. Read [references/results.md](references/results.md) when summarizing downloaded outputs, metrics, or validation quirks.

## Outputs

Summarize `metrics.json` and point the user at the downloaded CIF path. Read [references/results.md](references/results.md) for the local layout, nested metrics, binding metric variants, and SAB validation quirks.

## SAB 400 validation quirk

If the server rejects a payload with only `{"code":"VALIDATION_ERROR","message":"Request validation failed"}`, inspect `entities`, `binding`, and `constraints`; read [references/results.md](references/results.md) for details.
