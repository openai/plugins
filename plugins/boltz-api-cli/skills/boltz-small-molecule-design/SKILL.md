---
name: boltz-small-molecule-design
description: Design new small-molecule binders with Boltz. Use when generating novel ligands or hits for a target without a fixed compound library. Not for screening existing molecules or one-off docking.
---

## Workflow

If `boltz-api` is missing from `PATH`, use `boltz-cli-setup` for install/update guidance before retrying.
If a command reports missing or expired authentication, use `boltz-cli-setup` to start `boltz-api auth login --device-code` before retrying; do not ask permission first.
If the agent host sandbox blocks `boltz-api` install/auth/API calls, use `boltz-cli-setup` to request the host sandbox bypass/escalation needed for user-wide CLI install, browser login, credential storage, temp files, or API access before retrying.

Use this skill when the user wants de novo small-molecule binders (no existing library).

1. Normalize the target: one or more protein sequences into `target.entities`, plus optional `pocket_residues` (0-based) and/or `reference_ligands` (known binders to help locate the pocket).
2. Pick `num_molecules` — valid range **10 to 1,000,000** (server rejects outside it). If the user says fewer than 10, explain the floor and propose 10.
3. Only add `chemical_space` (e.g. `"enamine_real"`) if the user explicitly wants generation restricted to synthesizable molecules within that library.
4. Supported optional features include `chemical_space` and `molecule_filters`; only add them on explicit request. Read [references/api.md](references/api.md) for exact shapes and filter options.
5. Author the payload YAML or JSON, run `estimate-cost`, show the USD cost, wait for explicit confirmation. Cost is a flat $0.025 per molecule (size-independent); still quote `estimated_cost_usd` from the response as the authoritative total.
6. `start` to submit (synchronous). Capture the ID.
7. Launch `download-results` with the agent runtime's background/non-blocking command facility; it polls, paginates, downloads per-hit structures, and exits when terminal. In Claude Code, use Bash with `run_in_background: true`. In Codex, run `download-results` as a foreground shell command with `yield_time_ms: 1000`; if Codex returns a `session_id`, keep it for optional same-thread polling, but treat `download-status` plus the run directory as the durable source of truth. In Codex app/desktop runtimes that expose same-thread heartbeat automations, create a heartbeat that checks `download-status` periodically and posts a concise completion or failure update when the download reaches a terminal state. After launching the downloader, always report the job ID, run name, and output directory. Include the next check cadence if the heartbeat was created; otherwise include the `download-status` command.
8. Rank hits from `<output-root>/<run-name>/results/index.jsonl` by `binding_confidence` for hit discovery or `optimization_score` for lead optimization. Each generated molecule also carries a free `adme` block (`solubility`, `permeability`, `lipophilicity`) — surface it for developability triage when the user cares about ADME, or when a top hit looks risky. Read [references/results.md](references/results.md) for output layout and metric details.

## Command Pattern

```bash
# Replace placeholders with concrete absolute paths before running.
# Use a short descriptive run name, for example: sm-design-<target>-<batch>-v1

boltz-api small-molecule:design estimate-cost \
  --input @yaml:///absolute/path/payload.yaml

boltz-api small-molecule:design start \
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
  --poll-interval-seconds 60
# -> /absolute/path/boltz-experiments/<run-name>/results/<pres_*>/...
```

Payload keys are `num_molecules`, `target`, `chemical_space`, `molecule_filters` — the API body field names.

## Always Do This

- Enforce `10 <= num_molecules <= 1,000,000` before calling `estimate-cost`. The server rejects values outside that range.
- Cost is a flat $0.025 per molecule (size-independent). `estimate-cost` returns the authoritative total.
- Treat pocket residue indices as 0-based.
- Keep payload field names exactly as the API body names shown in `references/api.md`.
- Use absolute paths for the output root, payload files, and embedded target files. Do not `cd` into the run directory for follow-up commands; pass the same `--root-dir` and use absolute paths so later relative paths do not drift.
- Prefer one merged top-level payload via `--input @yaml:///absolute/path/payload.yaml` or `@json:///absolute/path/payload.json` for `estimate-cost` and `start`. Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win.
- Direct object flags still work as overrides: for example `--target @yaml:///absolute/path/target.yaml` or `--molecule-filters @json:///absolute/path/filters.json`. Piped YAML / JSON on stdin also works, but it must use API body field names. Never use `@file://`.
- Use the same slug as both `--idempotency-key` at submit and `--name` on `download-results`.
- In permission-gated agents such as Claude Code, keep each Boltz call as a top-level command that starts with `boltz-api`. Prefer concrete arguments over `sh -c`, inline environment assignments, aliases, wrapper scripts, loops, or pipelines around the `boltz-api` invocation unless the user already allowed that exact command form. Use `--raw-output --transform id`, read the printed ID, then paste that literal ID into the next `download-results` command.
- Prefer the agent runtime's background/non-blocking command mode for `download-results`. In Codex specifically, keep `download-results` in the foreground and set the shell tool yield to 1000 ms; Codex will return a `session_id` if the command is still running. Do not append `&` or use `nohup` in Codex because the tool runner may clean up shell-backgrounded descendants before `.boltz-run.json` is fully written.
- After the background/session starts, do not manually wait on it or run ad hoc polling loops. Wall-clock time scales roughly with `num_molecules`: under 100 often finishes in a few minutes, 100-1,000 may take several minutes to tens of minutes, and larger runs can take longer or hours depending on inputs and system load. Don't quote a fixed duration. `--poll-interval-seconds 60` is a sensible default for the downloader. `download-results` emits JSONL progress on stderr by default; add `--progress-format text --verbose` only when you explicitly want human-readable logs.
- In Codex app/desktop runtimes with same-thread heartbeat automation support, schedule a heartbeat after launching `download-results`. The heartbeat should run `boltz-api --format json download-status --name "<run-name>" --root-dir "/absolute/path/boltz-experiments"` and stop once terminal. Choose cadence by `num_molecules`: under 100 -> every 1-2 minutes; 100-1,000 -> every 5 minutes; over 1,000 -> every 15 minutes. Post only material status changes or terminal completion/failure. Poll the saved `session_id` with an empty `write_stdin` only for interactive, user-requested progress checks. Never run a manual poll loop in the current turn.
- If the current host has no heartbeat automation support, do not claim an automatic next check. Report the job ID, run name, output directory, and the command needed to check `download-status`.
- If detached download needs to be restarted, re-run `boltz-api download-results` with the same `--name "<run-name>"` and the same `--root-dir`.
- Do not invent filters; only add `molecule_filters` on user request.

## Escape Hatch

- Payload reference: <https://api.boltz.bio/docs/api/python/resources/small_molecule/subresources/design/methods/start>
- CLI flag names: `boltz-api small-molecule:design start --help`

Read [references/api.md](references/api.md) for the `target`, `chemical_space`, and `molecule_filters` shapes (filter catalog matches the screen endpoint). Read [references/results.md](references/results.md) after download when ranking generated molecules or explaining outputs.

## Outputs

Rank from `results/index.jsonl` after `download-results`; use [references/results.md](references/results.md) for local file layout and metric meanings.
