---
name: boltz-check-status
description: Boltz job status and result recovery. Use when listing jobs, checking progress, resuming downloads, recovering results, or downloading an existing job ID. Not for starting new jobs.
---

## Workflow

If `boltz-api` is missing from `PATH`, use `boltz-cli-setup` for install/update guidance before retrying.
If a command reports missing or expired authentication, use `boltz-cli-setup` to start `boltz-api auth login --device-code` before retrying; do not ask permission first.
If the agent host sandbox blocks `boltz-api` install/auth/API calls, use `boltz-cli-setup` to request the host sandbox bypass/escalation needed for user-wide CLI install, browser login, credential storage, temp files, or API access before retrying.

Use this skill to recover state across sessions and to inspect or download results for prior Boltz jobs. No payload authoring — this skill only calls `list` / `retrieve` / `download-results` / `download-status`.

Use four modes:

1. Local progress: if the user knows the run name / run dir, prefer `download-status` before remote API calls.
2. List recent jobs: enumerate all six resources, merge, and sort by `created_at` descending.
3. Retrieve one job: use the job ID prefix when known; otherwise probe resources until one succeeds.
4. Resume/download results: run `download-results` with the original run name when possible. Never run `start` again to resume.

ADME jobs use the prefix `adme_pred_*` and show up in Modes 1-2 (`list` / `retrieve`) like the others. ADME has **no** `download-results`/archive step, so Modes 3-4 don't apply — recover its scores by re-running `retrieve` (read `output.molecules[]`) or from the local `run.json`.

Read [references/resume.md](references/resume.md) before recovering a dropped session, mapping job ID prefixes, or choosing a run name for `download-results`. Read [references/api.md](references/api.md) for per-resource `list` columns, `retrieve` fields, and result semantics.

## Command Pattern

```bash
# Replace placeholders with concrete absolute paths before running.

# Local helper: inspect local checkpoint state without API calls.
boltz-api --format json download-status \
  --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments"

# Mode 1: list recent jobs across all 6 resources.
# Note: the CLI emits one JSON object per record (streamed, no {data:[]} wrapper).
# --limit is per-page and the CLI auto-paginates, so cap each explicit command with head.
boltz-api predictions:structure-and-binding list --limit 20 --format jsonl | head -20
boltz-api predictions:adme list --limit 20 --format jsonl | head -20
boltz-api small-molecule:library-screen list --limit 20 --format jsonl | head -20
boltz-api small-molecule:design list --limit 20 --format jsonl | head -20
boltz-api protein:library-screen list --limit 20 --format jsonl | head -20
boltz-api protein:design list --limit 20 --format jsonl | head -20

# Mode 2: retrieve by ID. Pick the resource from the ID prefix in the workflow
# notes above. If the prefix is unknown, run these one at a time until one succeeds.
boltz-api predictions:structure-and-binding retrieve --id "<job-id>" --format json
boltz-api predictions:adme retrieve --id "<job-id>" --format json
boltz-api small-molecule:library-screen retrieve --id "<job-id>" --format json
boltz-api small-molecule:design retrieve --id "<job-id>" --format json
boltz-api protein:library-screen retrieve --id "<job-id>" --format json
boltz-api protein:design retrieve --id "<job-id>" --format json

# Mode 3: resume download. Use the agent runtime's managed long-running command mode.
boltz-api download-results \
  --id "<job-id>" --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments" \
  --poll-interval-seconds 30
```

## Always Do This

- If the user has a run name / slug or run dir and only wants local downloader state, prefer `download-status` before `retrieve`.
- Use an absolute output root and keep passing it through `--root-dir`. Do not `cd` into the run directory; that makes later relative paths point at the run directory instead of the user's workspace.
- On an unfamiliar job ID, run Mode 2 (retrieve) before Mode 3 (download) so you capture `idempotency_key`.
- Prefer the original run-name slug over the job ID as `--name` — it resumes into the existing dir with cursor.
- In permission-gated agents such as Claude Code, keep each Boltz call as a top-level command that starts with `boltz-api`. Prefer running the six `list` / `retrieve` commands explicitly over generating them from a shell loop; a fixed `| head -20` cap is okay when listing to avoid runaway streamed output.
- Prefer the agent runtime's background/non-blocking command mode for `download-results`. In Codex specifically, keep `download-results` in the foreground and set the shell tool yield to 1000 ms; Codex will return a `session_id` if the command is still running. Do not append `&` or use `nohup` in Codex because the tool runner may clean up shell-backgrounded descendants before `.boltz-run.json` is fully written.
- After the background/session starts, do not manually wait on it or run ad hoc polling loops. In Codex app/desktop runtimes with same-thread heartbeat automation support, schedule a heartbeat that checks `download-status` periodically, posts only material status changes or terminal completion/failure, and stops once terminal. If the current host has no heartbeat automation support, do not claim an automatic next check; report the job ID, run name, output directory, and the command needed to check `download-status`.
- `download-results` now emits machine-readable JSONL progress on stderr by default. Add `--progress-format text --verbose` only when you explicitly want human-readable logs.
- Prefer `download-status` for local checkpoint state. In Codex hosts with heartbeat automation support, use it for automatic follow-up and poll the saved session with an empty `write_stdin` only for interactive, user-requested progress checks. Don't loop `retrieve` unless the user wants fresh remote status.
- If `retrieve` surfaces only `{"code":"VALIDATION_ERROR","message":"Request validation failed"}` with no `details`, that's expected for `predictions:structure-and-binding` failures — other endpoints include field paths.
- Never run `start` again on a failed or interrupted job. Fix the payload and submit with a new `idempotency-key`, or just resume with `download-results`.

## Escape Hatch

- Python SDK reference (per-resource `list` / `retrieve` methods): <https://api.boltz.bio/docs/api/python>
- CLI flag names: `boltz-api <resource> list --help`, `boltz-api <resource> retrieve --help`, `boltz-api download-results --help`, `boltz-api download-status --help`

## Outputs

- Local helper / Mode 1 / Mode 2 print structured data to stdout; present as a table.
- Mode 3 writes recovered artifacts under `<output-root>/<run-name>/` — same layout as a fresh run. Read [references/resume.md](references/resume.md) for resume behavior.
