---
name: boltz-protein-screen
description: Screen existing protein binders with Boltz. Use when ranking a supplied protein, peptide, antibody, nanobody, or binder library against a target. Not for designing new proteins or screening small molecules.
---

## Workflow

If `boltz-api` is missing from `PATH`, use `boltz-cli-setup` for install/update guidance before retrying.
If a command reports missing or expired authentication, use `boltz-cli-setup` to start `boltz-api auth login --device-code` before retrying; do not ask permission first.
If the agent host sandbox blocks `boltz-api` install/auth/API calls, use `boltz-cli-setup` to request the host sandbox bypass/escalation needed for user-wide CLI install, browser login, credential storage, temp files, or API access before retrying.

Use this skill when the user already has candidate proteins / peptides / antibodies / nanobodies.

1. Normalize the binder library into `proteins` — a list of candidate complexes. For a simple sequence library each entry has one protein entity; multi-chain candidates (antibody heavy+light) are also allowed.
2. Pick the target variant:
   - `structure_template` — user has a CIF/PDB file or URL; select which chains are polymer vs ligand, which residues to keep (`crop_residues`), and optionally `epitope_residues` / `flexible_residues`.
   - `no_template` — user has only sequences; pass them as `target.entities` plus optional `epitope_residues`.
3. Don't add `bonds` / `constraints` unless the user asks for geometry constraints.
4. Author the payload YAML or JSON, run `estimate-cost`, show the USD cost, wait for explicit confirmation.
5. `start` to submit. Capture the ID.
6. Launch `download-results` with the agent runtime's background/non-blocking command facility. In Claude Code, use Bash with `run_in_background: true`. In Codex, run `download-results` as a foreground shell command with `yield_time_ms: 1000`; if Codex returns a `session_id`, keep it for optional same-thread polling, but treat `download-status` plus the run directory as the durable source of truth. In Codex app/desktop runtimes that expose same-thread heartbeat automations, create a heartbeat that checks `download-status` periodically and posts a concise completion or failure update when the download reaches a terminal state. After launching the downloader, always report the job ID, run name, and output directory. Include the next check cadence if the heartbeat was created; otherwise include the `download-status` command.
7. Rank hits from `<output-root>/<run-name>/results/index.jsonl` by `binding_confidence` descending. Use `iptm` and `min_interaction_pae` as tiebreakers. `optimization_score` is not emitted for this endpoint. Read [references/results.md](references/results.md) for output layout and metric details.

## Command Pattern

```bash
# Replace placeholders with concrete absolute paths before running.
# Use a short descriptive run name, for example: protein-screen-<target>-<library>-v1

boltz-api protein:library-screen estimate-cost \
  --input @yaml:///absolute/path/payload.yaml

boltz-api protein:library-screen start \
       --idempotency-key "<run-name>" \
       --input @yaml:///absolute/path/payload.yaml \
       --raw-output --transform id

# Copy the printed job ID into this command, then launch it in the agent
# runtime's background/non-blocking mode.
# Claude Code: Bash with run_in_background=true.
# Codex: foreground shell command with yield_time_ms=1000; keep the returned session_id if one is provided.
# Do not append "&" or use nohup in Codex.
boltz-api download-results \
  --id "<job-id-from-start>" --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments" \
  --poll-interval-seconds 30
```

Payload keys are `proteins`, `target` — API body field names.

## Always Do This

- For `structure_template`, embed CIF/PDB bytes with `@data:///abs/path/target.cif` inside the `structure.data` field. Don't use bare `@path` (automatic file-type detection once sent CIF as plain text into a base64 field and broke the server parser).
- Residue indices are 0-based. `epitope_residues` and `flexible_residues` must be subsets of `crop_residues`.
- Keep payload field names exactly as the API body names shown in `references/api.md`.
- Use absolute paths for the output root, payload files, and embedded target files. Do not `cd` into the run directory for follow-up commands; pass the same `--root-dir` and use absolute paths so later relative paths do not drift.
- Prefer one merged top-level payload via `--input @yaml:///absolute/path/payload.yaml` or `@json:///absolute/path/payload.json` for `estimate-cost` and `start`. Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win.
- Direct object flags still work as overrides, such as `--target @yaml:///absolute/path/target.yaml` or repeated `--protein @json:///absolute/path/protein-1.json` entries. Piped YAML / JSON on stdin also works, but it must use API body field names. Never use `@file://` or `@./`.
- Use the same slug as both `--idempotency-key` and `--name`.
- In permission-gated agents such as Claude Code, keep each Boltz call as a top-level command that starts with `boltz-api`. Prefer concrete arguments over `sh -c`, inline environment assignments, aliases, wrapper scripts, loops, or pipelines around the `boltz-api` invocation unless the user already allowed that exact command form. Use `--raw-output --transform id`, read the printed ID, then paste that literal ID into the next `download-results` command.
- Prefer the agent runtime's background/non-blocking command mode for `download-results`. In Codex specifically, keep `download-results` in the foreground and set the shell tool yield to 1000 ms; Codex will return a `session_id` if the command is still running. Do not append `&` or use `nohup` in Codex because the tool runner may clean up shell-backgrounded descendants before `.boltz-run.json` is fully written.
- After the background/session starts, do not manually wait on it or run ad hoc polling loops. Wall-clock time scales roughly with the number of candidates in the library: under 100 often finishes in a few minutes, 100-1,000 may take several minutes to tens of minutes, and larger screens can take longer or hours depending on inputs and system load. Don't quote a fixed duration. `--poll-interval-seconds 30` is a reasonable downloader default. `download-results` emits JSONL progress on stderr by default; add `--progress-format text --verbose` only when you explicitly want human-readable logs.
- In Codex app/desktop runtimes with same-thread heartbeat automation support, schedule a heartbeat after launching `download-results`. The heartbeat should run `boltz-api --format json download-status --name "<run-name>" --root-dir "/absolute/path/boltz-experiments"` and stop once terminal. Choose cadence by candidate count: under 100 -> every 1-2 minutes; 100-1,000 -> every 5 minutes; over 1,000 -> every 15 minutes. Post only material status changes or terminal completion/failure. Poll the saved `session_id` with an empty `write_stdin` only for interactive, user-requested progress checks. Never run a manual poll loop in the current turn.
- If the current host has no heartbeat automation support, do not claim an automatic next check. Report the job ID, run name, output directory, and the command needed to check `download-status`.
- If detached download needs to be restarted, re-run `boltz-api download-results` with the same `--name "<run-name>"` and the same `--root-dir`.
- Cost is tiered by total complex length (target + candidate); the combined length sets the tier. Do not state or estimate a dollar figure yourself — to say anything about cost, run `estimate-cost` and quote only the number it returns.

## Escape Hatch

- Payload reference: <https://api.boltz.bio/docs/api/python/resources/protein/subresources/library_screen/methods/start>
- CLI flag names: `boltz-api protein:library-screen start --help`

Read [references/api.md](references/api.md) for the `proteins` list shape and both `target` variants (structure_template with `chain_selection`, and no_template with epitope hints). Read [references/results.md](references/results.md) after download when ranking screened binders or explaining outputs.

## Outputs

Rank from `results/index.jsonl` after `download-results`; use [references/results.md](references/results.md) for local file layout and metric meanings.
