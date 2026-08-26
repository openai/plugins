# Temporal CLI conventions and command index

Cross-cutting conventions for the `temporal` data-plane CLI (`workflow`, `batch`,
`schedule`, `activity`), plus an index that routes each operation to the file
that owns its judgment.

> **Scope.** Data-plane commands are documented across several files (see the
> [command index](#operation--command-index) below); this file is *not* the home
> for any single command. It holds the cross-command rules that don't belong to
> one operation, and points at the owner file for everything else.

## Use `--help` for flags

This file does not reproduce full flag tables — run `temporal <command> --help`
for the exhaustive, version-current flag set:

```bash
temporal <command> --help          # e.g. temporal workflow reset --help
```

It *does* curate the behaviors that are destructive, non-obvious, or buried in
`--help`'s description prose, plus the cross-command rules that belong to no
single command. (When a curated fact is version-volatile, the *behavior* is
stated here and the exact flag spelling/values are left to `--help`.)

## Connection and identity

Every `temporal` command reads the same connection settings from three
sources, checked in this order (first match wins): flag, env var, then
config-file profile.

| Env var | Flag | Purpose |
|---|---|---|
| `TEMPORAL_ADDRESS` | `--address` | Frontend `host:port` (default `localhost:7233`). |
| `TEMPORAL_NAMESPACE` | `--namespace`, `-n` | Namespace (default `default`). |
| `TEMPORAL_API_KEY` | `--api-key` | API-key auth (implies TLS). |

- **Config-file profile** (Environment Configuration) supplies a value only
  when no flag or env var sets it: `[profile.<name>]` in a TOML file at
  `$CONFIG_PATH/temporalio/temporal.toml` (OS-specific path; run `temporal
  config --help`). Pick the profile with `--profile` / `TEMPORAL_PROFILE`
  (default `default`); point at a different file with `--config-file` /
  `TEMPORAL_CONFIG_FILE`. Docs:
  [Environment Configuration](https://docs.temporal.io/develop/environment-configuration).
- mTLS uses `TEMPORAL_TLS_CERT` / `TEMPORAL_TLS_KEY` (`--tls-cert-path` /
  `--tls-key-path`). The endpoint form differs by auth method — see
  [../triage/connectivity.md](../triage/connectivity.md).
- `--identity` records who ran a mutating command (default
  `temporal-cli:$USER@$HOST`) and shows up in Event History and audit logs. Set
  it explicitly in shared automation.

Full env-var list: [docs.temporal.io/cli/setup-cli](https://docs.temporal.io/cli/setup-cli).

## Output and formatting

- `--output`, `-o` — `text` (default), `json`, `jsonl`, `none`. Use `json`/`jsonl`
  for scripting and pipe to `jq`; the triage/health runbooks recommend JSON
  output whenever a step fans out over many results.
- `--time-format` — `relative` (default), `iso`, `raw`.
- Payload shorthand: JSON output renders payloads inline by default; pass
  `--no-json-shorthand-payloads` to emit the raw payload envelope instead.

## The `--query` ⇒ batch-job bridge

The one cross-command rule worth memorizing. Passing `--query` (a
[List Filter](workflow-health.md#1-list-filter-fundamentals)) in place of
`--workflow-id` to `temporal workflow cancel | terminate | signal | delete` does
**not** act inline — it starts an asynchronous **batch job** over every matching
Execution. (The `--query` form of `temporal activity reset | unpause` behaves the
same way.)

### Count before you mutate

The mutating form does not report how many Executions it matched until the job is
already running. Run the query through `count` first and put that number in front
of the user:

```bash
temporal workflow count --query 'ExecutionStatus="Running" AND WorkflowType="<YourType>"'
```

Use the byte-identical query string in both commands — a predicate dropped between
the `count` and the `terminate` silently widens the blast radius. A filter with no
narrowing term beyond `ExecutionStatus="Running"` matches every open Execution in
the Namespace.

### Running an approved batch

```bash
temporal workflow terminate \
    --query 'ExecutionStatus="Running" AND WorkflowType="<YourType>"' \
    --reason "<why>" \
    --rps <n> \        # throttle the batch; only valid with --query
    --yes              # proceed without the interactive prompt
```

Without `--yes` the command prompts `Start batch against approximately N
workflow(s)? y/N`. That prompt needs a terminal: with no terminal attached it
reads EOF, reports `user denied confirmation`, exits non-zero, and touches
nothing. So `--yes` is how an already-approved batch actually runs — and it is
also what suppresses the `N`, which is why the `count` above is not optional.
Get the user's approval on the scope, then run it with `--yes`; do not discover
the flag by retrying a command that failed the prompt.

### Inspecting and aborting a running job

A batch job drains asynchronously, so one started against too broad a query can
still be stopped before it reaches the rest of its matches:

```bash
temporal batch list
temporal batch describe --job-id <JobId>   # progress; how far it has drained
temporal batch terminate --job-id <JobId> --reason "<why>"
```

`batch terminate` stops the job, **not** the Executions it already acted on —
those are already terminated, cancelled, or deleted and stopping the job does not
bring them back.

`--reason`, `--rps`, and `--yes` are accepted only when `--query` is present. For
*which* List Filter to run, see [workflow-health.md](workflow-health.md).

### Single-target commands have no prompt at all

A single-target `workflow cancel | terminate | delete | signal` (with
`--workflow-id`) executes immediately — there is no confirmation and no `--yes`
to skip, because the prompt exists **only** on the `--query` batch form above.
The scope is one Execution, but nothing between the command and the effect will
catch a wrong Workflow ID or a wrong Namespace, so confirm both before running.

`workflow delete` in a multi-region (global) Namespace removes the Execution from
**all replicas**; requests to a passive cluster are forwarded to the active one by
default — pass `--grpc-meta xdc-redirection=false` to target a passive cluster.

## Schedule time-spec forms

`temporal schedule create` (and `update`) accept any combination of three spec
flags (run `temporal schedule create --help` for the rest):

- `--interval` — shorthand duration, e.g. `45m`, or `6h/5h` (every 6h, offset 5h).
- `--calendar` — JSON, e.g. `{"dayOfWeek":"Fri","hour":"3","minute":"30"}`.
- `--cron` — Unix cron or robfig (`@daily`, `@every 1h`), e.g. `"30 12 * * Fri"`.

`--overlap-policy` takes one of six values (`Skip`, `BufferOne`, `BufferAll`,
`CancelOther`, `TerminateOther`, `AllowAll`); their semantics and the backfill
workflow live in [../triage/schedule-missed.md](../triage/schedule-missed.md).
Concept page: [docs.temporal.io/schedule](https://docs.temporal.io/schedule).

**Update/delete gotchas** (`--help` buries these in the command description):
`temporal schedule update` **fully replaces** the schedule spec — options you don't
pass reset to defaults, so `describe` first and re-specify everything; `memo` and
search attributes can't be changed after creation. `temporal schedule delete` does
**not** stop already-running Executions — terminate those separately (e.g.
`temporal workflow terminate` by `TemporalScheduledById`).

**`backfill` is a fan-out.** It replays the Schedule's actions across a past
window, so the Executions it starts scale with the window divided by the interval —
a month backfilled onto a 15-minute schedule is roughly 2,880 of them, and under
`--overlap-policy AllowAll` they start together rather than queueing. Compute that
number from the window and interval and put it in front of the user before running
one, the same way `count` precedes a `--query` mutation. The overlap policy is the
difference between a backfill that drains and one that stampedes the Worker fleet;
see [../triage/schedule-missed.md](../triage/schedule-missed.md).

## Operation → command index

One row per common data-plane operation. The linked file owns the judgment (when
to run it, how to read the output); run `temporal <cmd> --help` for flags.

| Operation | Skeleton | Owner |
|---|---|---|
| Find / list / count unhealthy workflows | `temporal workflow list --query '<filter>'` | [workflow-health.md](workflow-health.md) |
| Inspect one workflow | `temporal workflow describe -w <id>` / `show` / `stack` | [workflow-health.md](workflow-health.md), [../triage/workflow-stuck.md](../triage/workflow-stuck.md) |
| Recover a stuck workflow (signal / cancel / terminate / reset) | `temporal workflow signal\|cancel\|terminate\|reset ...` | [../triage/workflow-stuck.md](../triage/workflow-stuck.md#recovery-commands) |
| Reset past a non-determinism divergence | `temporal workflow reset -w <id> --event-id <n>` | [../triage/non-determinism.md](../triage/non-determinism.md) |
| Bulk cancel / terminate / signal / delete | `--query` form → [batch bridge](#the---query--batch-job-bridge) | this file + [workflow-health.md](workflow-health.md) |
| Pause / unpause / reset a stuck activity | `temporal activity pause\|unpause\|reset ...` | [../triage/workflow-stuck.md](../triage/workflow-stuck.md#temporal-activity-pause--unpause--reset) |
| Complete / fail an activity externally | `temporal activity complete\|fail -a <id> -w <id>` | `temporal activity --help` |
| Schedule CRUD (create / update / toggle / trigger / delete) | `temporal schedule <sub> -s <id> ...` | this file ([spec forms](#schedule-time-spec-forms)) |
| Backfill / diagnose missed schedule actions | `temporal schedule backfill -s <id> ...` | [../triage/schedule-missed.md](../triage/schedule-missed.md) |

`activity complete | fail` inject a result the Activity never produced. The
Workflow resumes on that outcome as if the Activity had really succeeded or
failed, and the Event History records the supplied result with no undo. They are
for an Activity genuinely completing asynchronously outside the Worker — propose
rather than run. To stop a retry loop rather than answer it, use
[`activity pause`](../triage/workflow-stuck.md#temporal-activity-pause--unpause--reset).
