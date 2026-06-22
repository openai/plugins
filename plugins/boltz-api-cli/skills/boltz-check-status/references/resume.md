# Resume and Recovery

Read this when the user wants to resume a dropped session, recover results by job ID, inspect local downloader state, or understand job ID routing.

## Job ID Prefixes

Use these observed prefixes to route `retrieve` calls. If a prefix is unfamiliar, fall back to probing all six resources.

- `sab_pred_*` -> `predictions:structure-and-binding` (legacy `pred_*` IDs are still supported)
- `adme_pred_*` -> `predictions:adme` (`list` / `retrieve` only — no `download-results`; results in `output.molecules[]`)
- `prot_des_*` -> `protein:design`
- `prot_scr_*` -> `protein:library-screen`
- `sm_des_*` -> `small-molecule:design`
- `sm_scr_*` -> `small-molecule:library-screen`

The right-hand side is the CLI resource you pass to `retrieve` — this table matches the one in `api.md`. Prefixes are verified against the live API but are not a guaranteed contract; if one is unfamiliar, probe all six resources.

## Local Downloader State

When the user knows the original run name or local run directory, prefer local checkpoint inspection before remote API calls:

```bash
boltz-api --format json download-status \
  --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments"
```

## Resume Download

If the user knows the original slug/run name or local run directory:

```bash
boltz-api download-results \
  --id "<job-id>" --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments" \
  --poll-interval-seconds 30
```

Run this through the agent runtime's managed long-running command mode:

- Claude Code: Bash with `run_in_background=true`
- Codex: foreground shell command with `yield_time_ms=1000`; keep the returned `session_id` if one is provided

Do not append `&` or use `nohup` in Codex.

If the run directory exists, `--id` can be omitted because the CLI can read the ID from metadata.

## Only Job ID Is Known

Run `retrieve` first and capture `idempotency_key`, then use that as `--name` for `download-results`. If the original submit did not pass an idempotency key, pick a fresh slug and download from scratch. Server-side the job is fine; only incremental local resume is lost.

Never run `start` again to resume an existing job.
