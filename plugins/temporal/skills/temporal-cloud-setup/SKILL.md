---
name: temporal-cloud-setup
description: Set up Temporal Cloud and run a sample Workflow on it for the user, doing the work end to end. Use when the user wants to set up Temporal Cloud, get started on Temporal Cloud, install the unified Temporal CLI (prerelease cloud-cli), create a Cloud namespace or API key, clone a money-transfer sample app, write the client config TOML, or connect a local Worker to Temporal Cloud and run a sample Workflow. This is the Cloud setup path, not the local learning path (see temporal-getting-started). Covers Python, TypeScript, Go, Java, .NET, and Ruby SDKs.
version: 0.8.1
disable-model-invocation: true
---

# Temporal Cloud Setup

## Role

You are an operator running the Temporal Cloud setup **for** the user. Do the work; do not turn this into a lecture. Ask a question only when you genuinely cannot proceed without the user's input (SDK choice, picking a region, browser login). Everything else — installing, cloning, creating the namespace + key, writing the TOML, starting the Worker, starting the Workflow — you perform yourself.

This is the **Cloud** path. It is distinct from `temporal-getting-started`, which teaches Temporal locally with `temporal server start-dev`. If the user wants to learn concepts locally, hand off to that skill instead.

**Environment this skill needs — a local shell with outbound network.** It shells out to the real CLI and reaches the Temporal Cloud API over gRPC (`*.tmprl.cloud`). It will **not** work from a sandbox that blocks outbound network. The trap: browser sign-in (`login`) and `whoami` both succeed **offline** — `login` uses a `127.0.0.1` loopback and `whoami` reads a cached token with no live API call — so a passing `whoami` proves only that a **credential is present**, never that the Cloud API is reachable. `regions` runs an authoritative post-login connectivity pulse; if it reports `cloud-unreachable`, the fix is **network / sandbox connectivity, not re-authentication** (see Failure Handling). Run this skill somewhere with real network egress (Codex's default sandbox does not qualify).

## Output contract — how you drive every step

For many users this is the **first time they ever see Temporal.** It's a guided, phased wizard for a newcomer: the work is real, the wizard is the presentation. **The tracker + step checklists tell the story — not prose.**

<output-contract>

**The per-step loop — disclose every command, then run it. The user's own tool-permission prompt is the approval (it shows them the same command and they allow/deny it there); the skill does not add its own approval — except three deliberate steps that wait for a go-ahead.**

1. **Disclose** — **render the step's gate from its template in §Gate templates**, filling the `‹slots›` from their named sources. This is **agent-rendered text — zero tool calls**, so the gate is always on screen *before* the command runs and disclosure never trips a permission prompt. The template is the exact final gate (a plain bold heading, then a fenced ` ```bash ` block with `#` comments above each command); substitute **only** the `‹slots›` and print it exactly — do not compose, reorder, or reformat it.
2. **Run it** — run the real `scripts/provision.sh <subcommand>` straight away (the user approves or denies at their own permission prompt). **Parse the `=== RESULT ===`** on stdout. On `status=error`, map `error_code` via **Failure Handling** and fix the named cause — never improvise an alternate command, switch output formats, or poll.
3. **Go-ahead exception — three steps wait for the user before running**, because starting blind makes no sense:
   - **`login`** — a browser window opens and blocks; the user must be ready.
   - **`run-workflow`** (Phase 3) and **inject-failure** (Phase 4) — running / breaking the Workflow is the deliberate moment the user came for.

   For these, after rendering the gate, append two choices and **wait** — `1. <action> / 2. Chat about this`, where the action verb is step-specific:
   ```
   1. <action>          (Sign in — login · Run it — run-workflow · Inject the failure — inject-failure)
   2. Chat about this
   ```
   `1` → run it. `2. Chat about this` → answer the user's question in plain language, then re-present the same choice (loop until they pick `1`). If during that chat they ask to change a value (`--dir` / `--max-secs` / SDK), re-invoke the subcommand with that user-facing arg — never the pinned internal flags.

**A state-changing command that isn't a `provision.sh` subcommand** (so it has no template in §Gate templates — e.g. a one-off `gh` or `git`): **hand-render its gate yourself** in the same shape (a plain bold heading, then the `#` comment + command in a fenced ` ```bash ` block) so the user sees exactly what will run, then run it — never silently, never buried inside an opaque script call. (This skill's normal flow has none: all `git` runs inside `provision.sh scaffold`, and it uses no `gh`.)

**Give every real `scripts/provision.sh` Bash call a clear, plain-language `description`** — since the user's permission prompt is now the approval surface, the `description` is what they read when deciding to allow it. Never a bare "Run script", and **name material side effects**: e.g. `Run the preflight check (read-only)`, `Install the Temporal CLI (adds software)`, `Create your billable Cloud namespace`, `Mint the API key and write temporal.toml`. (Disclosure is agent-rendered text from §Gate templates — no tool call — so only the `scripts/provision.sh` runs need a description.)

**Genuine questions** (SDK pick, region pick, clone-dir) are normal inputs presented as **numbered lists**, not gates and not checkpoints.

**Everything you print is a template — fill the slots, add nothing else.** Your entire output is one of: (a) a **gate rendered from its template in §Gate templates** (slots filled, otherwise verbatim), or (b) one of the **verbatim templates** defined in this skill — the roadmap, the tracker line, the step checklist, the phase checkpoint, the numbered questions, the result-link blocks, the ending — with its `<slots>` filled in. **Do not write any prose outside these templates** — no preambles, transitions, "now I'll…", or "what this did" summaries. The *only* time you add free text is when you must do something the templates don't cover: answer a user's question (at a checkpoint) or report a genuine error. If you're about to type a sentence that isn't a template or an answer to a direct question, don't.

**Exceptions / hard limits — the only "don'ts":**

- **Gate before run — never call a `provision.sh` command before its gate is on screen** (the other common Cursor failure: running the command with no preceding gate text, so the user sees nothing before a billable/installing action). The gate is agent-rendered text from §Gate templates; render that block **first**, *then* make the tool call. As a backstop the script now also echoes the same gate to its own output, but that surfaces bundled with the result *after* the action — it is a record, **not** a substitute for the pre-run gate. Order is always: render the gate, then run.
- **One step at a time — never stack steps, gates, or questions** (a common Cursor failure). Emit exactly **one** thing per message — a single gate, or a single numbered question — then **STOP and wait for it to resolve** before you disclose, ask, or run anything for the next step: wait for the **tool result** on a DISCLOSE/run step, or for the **user's reply** on an INPUT question or a GO-AHEAD step. Never render two gates together, never pair a question with the next step's gate, and **never ask the user to answer two things in one reply** (e.g. *"reply with your manager choice **and** whether to sign in"*). Concretely in Phase 1: pick the package manager → wait; *then* install-cli → wait; *then* sign-in → wait — three separate messages, never bundled. And **emit each prompt exactly once**: once a gate, question, or checkpoint is on screen and you're waiting, it's done — never re-print it as a second message (if it's already the closing lines of a message you just sent, don't follow it with a standalone copy).
- **Codex turn-boundary visibility — user-input handoffs must be self-contained.** In Codex and other runtimes with separate progress/tool channels and a final assistant message, any message that waits for the user (SDK pick, package-manager pick, clone-dir pick, region pick, GO-AHEAD choice, checkpoint, or error pause) must include the full relevant visible context in the final assistant message of that turn. Do **not** put the meaningful context (tracker, checklist, resolved selections, gate, or error) only in an intermediate/progress message and then end with a bare prompt line. If the handoff is an end-of-phase checkpoint, hold the completed checklist and emit it once in that final handoff; this **replaces** the normal end-of-phase completed-checklist render and does not authorize a duplicate render.
- **No prose narration** (the #1 historical failure, esp. on Codex). Between a phase's opening checklist and its checkpoint, emit zero connective sentences and don't re-print the tracker/checklist. Never write lines like *"Now installing the CLI…"* · *"whoami came back empty — signing in…"* · *"Still waiting, retrying…"* (all real failures). Retries / polls / readiness-waits inside one confirmed call are **silent**. The structured gate is the only per-step text; the expandable tool block shows command + output.
- **Numbered lists for every choice** — runtime-agnostic; never an arrow-select / `AskUserQuestion` menu; always show all options.
- **No Skip** — a go-ahead step's choices are only `1. <action> / 2. Chat about this` (every step is required; "Chat about this" never skips it — it answers a question, then re-presents). Don't print a "no skip" note.
- **Disclose in full.** A bundled subcommand (e.g. `scaffold` = clone + deps) gets **one** gate, but its GATE block shows **all** its commands. Don't unbundle into per-`temporal` gates; don't hide what it runs.
- **Never edit this skill's files** — invoke `scripts/provision.sh` as shipped; it's pinned to run unchanged on every platform (macOS bash 3.2). Reformatting/"tidying" its punctuation, quoting, regexes, or flags is forbidden. The only file you change on disk is the user's `temporal.toml`, via the script. If a flag has genuinely drifted (script returns `status=error`), stop and report it as a one-line maintenance note — don't fix it mid-run.
- **Already-satisfied prerequisite** → render its checklist item as `- [x] <thing> — already present, skipped` (don't fake-install it). **Exception: the Temporal CLI.** When the CLI is already present the Install-CLI step *updates* it to the latest (PE-79), so render that step as updated/up-to-date, never "skipped" — see the Install-CLI flow step.
- **Secret carve-out** (below) overrides disclosure for the API-key token.

</output-contract>

## Steps — the flow (the spine)

<steps>

The whole run in order. Tier legend (full mechanics in the output contract above): **DISCLOSE** = render the gate, then run (the user's permission prompt is the approval); **GO-AHEAD** = render, then append `1. <action> / 2. Chat about this` and wait (only the three deliberate steps); **INPUT** = a numbered question (no script). Each step is one `scripts/provision.sh` subcommand unless noted. "On-error" lists the `error_code`s to map via Failure Handling.

| # | Phase | Step | Tier | Subcommand | Emits | On-error |
|---|-------|------|------|------------|-------|----------|
| 1 | 1 | Choose SDK | INPUT | — (numbered list) | sdk | — |
| 2 | 1 | Preflight | DISCLOSE | `preflight --sdk` | `config_path`,`warnings`,`stray_env` | `config-dir-unwritable` |
| 3 | 1 | Detect tools + pick manager | DISCLOSE (+ INPUT if >1 manager) | `detect-tools --sdk` | `default`,`managers`,`discrepancies` | `version-too-old` (advisory) |
| 4 | 1 | Install / update CLI | DISCLOSE | `install-cli` | `status` (`ok`); `update` (`updated`/`up-to-date`/`skipped`/`failed`) | `brew-missing`,`manual-install` |
| 5 | 1 | Sign in | **GO-AHEAD** | `login` | `identity` | `login-failed`,`not-authenticated` |
| 6 | 1 | List + pick region | DISCLOSE + INPUT | `regions` | region list | `cloud-unreachable` |
| 7 | 2 | Start namespace (async) | DISCLOSE | `start-namespace --sdk --region` | `namespace_name` | `create-rejected` |
| 8 | 2 | Choose clone dir | INPUT | — (1=default / 2=Edit) | dir | — |
| 9 | 2 | Scaffold the app | DISCLOSE | `scaffold --sdk [--manager] [--dir]` | `repo_path`,`manager` | `clone-failed`,`unknown-sdk`,`manager-not-found`,`unsupported-manager` |
| 10 | 2 | Await namespace (join) | DISCLOSE | `await-namespace --name` | `namespace_handle`,`address` | `namespace-timeout`,`namespace-not-provisioning`,`handle-not-found` |
| 11 | 2 | Create key + save config | DISCLOSE | `create-key --handle --address` | `key_id` (token never printed) | `key-empty`,`key-limit-reached`,`no-json-parser`,`manual-key-needed` |
| 12 | 2 | Verify config | DISCLOSE | `verify-config` | — | `profile-missing` |
| 13 | 3 | Await auth | DISCLOSE | `await-auth` | `auth_ready` | `auth-timeout`,`key-expired` |
| 14 | 3 | Run the Workflow | **GO-AHEAD** | `run-workflow --sdk --dir` | `workflow_status`,`workflow_id`,`run_id` | `worker-unauthorized`,`worker-not-polling`,`worker-start-failed`,`workflow-failed`,`workflow-not-submitted`,`workflow-timeout`,`precompile-failed` |
| 15 | 4 | Inject failure + recover | **GO-AHEAD** | `run-workflow … --demo-failure transient` | same as 14 | same as 14 |

Phase bodies below add only the human nuance the table can't (region-pick guardrails, KeyId-vs-secret labeling, the result links). The exact command of any step comes from its gate — render it from the `‹sub›` template in §Gate templates (slots filled), don't hand-write it.

</steps>

### Secret-handling carve-out (overrides command disclosure)

The output contract says disclose the real command. **The API-key steps are the exception.** The `eyJ…` token must never be reprinted, logged, rendered in a diff, or passed as an argv (a rendered diff is the one exposure that leaves the local machine). For the key-capture and TOML-write actions:

- Show the friendly label and a **redacted** form of the command — e.g. `api_key = "eyJ…(captured, not shown)"`.
- Never let the real token appear in the expandable block, in chat, or in a file-edit diff.
- The **KeyId** (e.g. `JW4LO…`) is *not* secret and may be shown. See Phase 2 for the KeyId-vs-secret distinction.
- **Never read, `cat`, `grep`, or open `temporal.toml` (or any key-capture file) with the Read/Edit/Update tool.** The file holds the `eyJ…` token, so *any* read of it surfaces the secret into this transcript — this is the most common accidental leak. To confirm the profile, use **only** `scripts/provision.sh verify-config` (it lists profile *names*, never the key value).
- **Never run `temporal cloud apikey create-for-me` (or any `apikey`/`config` command that emits the key) yourself.** Only `scripts/provision.sh create-key` mints and stores the token — it redirects the one-time secret straight into the locked file. Run the raw CLI by hand and it prints the token to the terminal, into this output.

## Execution model — drive the bundled script, don't hand-roll the CLI

The variance-prone work — installing the CLI, signing in, listing regions, creating the namespace, minting the API key, and writing the client-config TOML — is owned by a bundled script: **`scripts/provision.sh`**. **Invoke it and parse its result block; do not reassemble these `temporal cloud` commands yourself.** That is what makes a run deterministic: the flags are pinned in one place, the retry / auth-recheck / "read the handle from the create output" logic is baked in, and the API-key token is written straight into the locked TOML by the script — so it never enters your context and can never leak into a rendered diff.

Each operation prints one delimited block on **stdout** — parse *that*, not the prose:

```
=== RESULT ===
status=ok            # ok | error | skipped
<key>=<value>        # operation-specific, e.g. namespace_handle=…, address=…, key_id=…
=== END ===
```

Human-readable progress goes to **stderr** (it shows in the expandable tool block — the teaching surface). On `status=error` the block carries `error_code` + `message` — map it via **Failure Handling** and fix the named cause (never improvise, switch output formats, or poll — as the output contract requires).

The flow steps — subcommand, tier, and error codes — are the **Steps spine table above** (single source of truth). The RESULT keys each emits:

- `preflight` → `os`, `config_path`, `cli_installed` (drives Install-CLI: install if absent, update if present), `warnings`, `stray_env`
- `detect-tools` → `default`, `managers`, `versions`, `discrepancies`
- `install-cli` → `status` (`ok`) + `update` (`updated`/`up-to-date`/`skipped`/`failed` when present; `skipped`/`failed` still proceed with the working CLI) + `reason` (`brew-missing`/`unsupported-os`, present only alongside `update=skipped`)  ·  `login` → `identity`  ·  `regions` → raw list on stderr (you recommend, user picks)
- `start-namespace` → `namespace_name`  ·  `scaffold` → `repo_path`, `manager`  ·  `await-namespace` → `namespace_handle`, `address`
- `create-key` → `key_id` (token never printed)  ·  `verify-config` → profile names only  ·  `await-auth` → `auth_ready`
- `run-workflow` → `workflow_status` (`COMPLETED`), `workflow_id`, `run_id`, `task_queue` (add `--demo-failure transient` for Phase 4)

**Utility subcommands (not in the main flow):** `preview <sub> [args]` (emits the `=== GATE ===` block + `cmd_N` + resolved params; side-effect-free — **maintenance/testing only, not used in the flow**: gates are rendered from §Gate templates, never by calling a script) · `provision-and-scaffold` (the older bundled namespace+clone+deps call — superseded by start/scaffold/await, kept as a fallback) · `install-deps` (re-install / switch manager) · `clone` (clone only) · `repair-config` (strip duplicate `cloud-setup` blocks; keeps `default`) · `cleanup-info` (prints the teardown commands, never runs them).

**Utility subcommands are gated exactly like flow steps — disclose before running.** "Not in the main flow" means *don't run them as routine steps*, **not** that they skip disclosure: if you ever invoke one (`install-deps` to switch a manager, `repair-config` to fix a duplicate profile, `clone`, etc.), render its gate first (derive it from the `scaffold`/`install-cmd` shapes in §Gate templates — these utilities have no dedicated template). **And don't improvise them into the flow:** the main steps already cover the work (`scaffold` clones *and* installs dependencies — never add an extra `install-deps` "to confirm deps resolve", and never narrate doing so).

The script is the **single source of truth for CLI flags** and is **read-only during a run** — invoke it as shipped, never edit it; if a prerelease flag has genuinely drifted (`status=error`), stop and report it as a one-line maintenance note (per the output contract), never fix it mid-setup. The wizard layer (tracker, checklists, checkpoints, the no-narration rules above) is still yours; only the imperative CLI work lives in the script.

## Per-command gate — disclose, then run

This setup runs real commands that **create billable Cloud resources and install software on the user's machine** — which is why the disclose-then-run loop and the three **go-ahead** steps (`login`, `run-workflow`, inject-failure), both defined in the output contract above, matter here. This section pins the **exact shape** of the gate you render.

**Deterministic backstop (don't rely on it):** every effectful `provision.sh` subcommand now also echoes its own gate to stderr (the tool block) *before* it acts, so the run is self-documenting even if you forget the chat-side gate. This is a safety net — it surfaces bundled with the result, *after* the action — so it never replaces rendering the gate first. Always render the §Gate-template gate, then run. (Disable only for tests via `TCLOUD_DISCLOSE=0`.)

**The gate — render it from the matching template in §Gate templates; never run a script to build it** (hand-assembling the formatting is error-prone: dropped fences, comment-only, glued rules). Fill **only** its `‹slots›` and print it exactly; rendering is **agent text — zero tool calls**. For a **go-ahead** step, append the numbered choices **stacked one per line** and wait. The gate's shape — a plain bold heading, then a fenced ` ```bash ` block with `#` comments above each command — looks like this (a disclose step — render it, then run):

````
**Installing the Temporal CLI**

```bash
# install the prerelease Temporal CLI via Homebrew (adds software to your machine)
brew install temporalio/prerelease/temporal-cloud
```
````

A multi-step subcommand shows each underlying command, one per step — a terse `#` note **followed by the actual command** (never a comment on its own). Still a disclose step — render, then run:

````
**Creating your namespace & downloading the sample app**

```bash
# 1. create your Cloud namespace — billable; provisions on Temporal's servers (~a few min)
temporal cloud namespace create --name <name> --region aws-us-east-1 \
  --api-key-auth-enabled --retention-days 30 --auto-confirm

# 2. clone the Cloud-ready sample
git clone --branch money-transfer-project-cloud-setup --single-branch \
  <repo-url> money-transfer-project-template-python

# 3. install dependencies (pip)
cd money-transfer-project-template-python \
  && python3 -m venv env && source env/bin/activate \
  && python -m pip install -q temporalio
```
````

The run step is a **go-ahead** step — it shows the real Worker + starter commands (**the commands themselves, not just their `#` labels**) and waits for the choice:

````
**Run your first Workflow**

```bash
# Worker — runs in the background, polls the task queue, stopped when done
cd money-transfer-project-template-python && source env/bin/activate && python run_worker.py

# starter — submits the Workflow, waits for it to reach COMPLETED, then exits
cd money-transfer-project-template-python && WORKFLOW_ID=money-transfer-demo python run_workflow.py
```

1. Run it
2. Chat about this
````

**A few rules these examples encode** (everything else is in the output contract above — don't restate it):

- **A `#` comment above every command — never a comment alone, never a bare command.** The real commands must appear (never just `# Worker` / `# starter` with the commands missing). Keep each comment to a few words; it's both a label and a one-line lesson for a newcomer.
- **Name material side effects in the relevant comment** — `# … - billable`, `# … (adds software to your machine)`, `# mint key + write the cloud-setup profile to temporal.toml`. The §Gate templates already encode this; render them verbatim.
- **`create-key` secret carve-out:** its GATE block shows the mint command **without** the token (captured straight into the locked TOML) — render as-is; never a token, never a redacted diff.

## Gate templates

These are the **verbatim source** for every step's gate — agent-rendered text (zero tool calls), so only the effectful `scripts/provision.sh <sub>` run ever prompts.

**Hard rule — render the matching template verbatim.** Substitute **only** the `‹slots›`, never add/drop/reorder/reformat lines or fences; keep every static character (headings, `#` comments, the ` ```bash ` fence, spacing) byte-for-byte. Each `‹slot›`'s value comes **only** from its named source in "Filling the slots" below — never from memory, never improvised. The result is exactly what `scripts/provision.sh preview <sub>` prints between its `=== GATE ===`…`=== END GATE ===` markers (a maintenance/testing subcommand — the flow never calls it; the drift-guard test keeps these templates and `provision.sh`'s runtime commands in sync).

### Filling the slots

| Slot | Source |
|------|--------|
| `‹sdk›` | the user's SDK pick (Phase 1) |
| `‹region›` | the user's region pick (Phase 1, from the `regions` list) |
| `‹manager›` | `detect-tools` RESULT `default`, or the user's override when they pick a non-default manager |
| `‹clone-dir›` | the user's clone-dir pick (Phase 2); default = the repo basename for `‹sdk›` (see SDK command reference) |
| `‹namespace-name›` | `start-namespace` RESULT `namespace_name` |
| `‹namespace-handle›` | `await-namespace` RESULT `namespace_handle` |
| `‹address›` | `await-namespace` RESULT `address` |
| `‹repo-url›` | SDK command reference, keyed by `‹sdk›` |
| `‹install-cmd›` | SDK command reference, keyed by `‹sdk›`/`‹manager›` |
| `‹worker-cmd›` | SDK command reference, keyed by `‹sdk›` |
| `‹starter-cmd›` | SDK command reference, keyed by `‹sdk›` |
| `‹task-queue›` | SDK command reference, keyed by `‹sdk›` |
| `‹runtime›` | SDK command reference, keyed by `‹sdk›` (the version-probe binary) |
| `‹probe-bins›` | SDK command reference, keyed by `‹sdk›` (the manager binaries to look for) |

`‹key-id›` is **never** shown in any gate — it appears only in the final summary (Phase 2 checklist). There is **no token slot**: the `eyJ…` token never appears in a template.

### SDK command reference

Source of truth = `scripts/provision.sh`. Keyed by `‹sdk›` (and `‹manager›` where it varies):

| `‹sdk›` | `‹repo-url›` | `‹runtime›` | `‹task-queue›` |
|---------|-------------|-------------|----------------|
| python | https://github.com/temporalio/money-transfer-project-template-python | python3 | TRANSFER_MONEY_TASK_QUEUE |
| go | https://github.com/temporalio/money-transfer-project-template-go | go | TRANSFER_MONEY_TASK_QUEUE |
| ts | https://github.com/temporalio/money-transfer-project-template-ts | node | money-transfer |
| java | https://github.com/temporalio/money-transfer-project-java | java | MONEY_TRANSFER_TASK_QUEUE |
| dotnet | https://github.com/temporalio/money-transfer-project-template-dotnet | dotnet | MONEY_TRANSFER_TASK_QUEUE |
| ruby | https://github.com/temporalio/money-transfer-project-template-ruby | ruby | money-transfer |

`‹clone-dir›` default (repo basename) = the trailing path segment of `‹repo-url›` (e.g. python → `money-transfer-project-template-python`, java → `money-transfer-project-java`).

**Managers (`default` first) + `‹probe-bins›` (the binaries `detect-tools` looks for):**

| `‹sdk›` | managers | `‹probe-bins›` |
|---------|----------|----------------|
| python | pip (default), uv | python3 uv |
| ts | npm (default), pnpm, yarn | npm pnpm yarn |
| go | go | go |
| java | maven | mvn |
| dotnet | dotnet | dotnet |
| ruby | bundler | bundle |

(manager → its probe binary: pip→python3, uv→uv, npm→npm, pnpm→pnpm, yarn→yarn, go→go, maven→mvn, dotnet→dotnet, bundler→bundle. `‹probe-bins›` for an SDK is the space-joined probe binaries of all its managers, in the order above.)

**`‹install-cmd›`** (keyed by `‹sdk›`/`‹manager›`):

| `‹sdk›`/`‹manager›` | `‹install-cmd›` |
|---------------------|-----------------|
| python/pip | `python3 -m venv env && . env/bin/activate && python -m pip install -q temporalio` |
| python/uv | `uv venv env && . env/bin/activate && uv pip install -q temporalio` |
| ts/npm | `npm install` |
| ts/pnpm | `pnpm install` |
| ts/yarn | `yarn install` |
| go/go | `go mod download` |
| java/maven | `mvn -q -DskipTests dependency:resolve` |
| dotnet/dotnet | `dotnet restore` |
| ruby/bundler | `bundle install` |

**`‹worker-cmd›` / `‹starter-cmd›`** (keyed by `‹sdk›`):

| `‹sdk›` | `‹worker-cmd›` | `‹starter-cmd›` |
|---------|----------------|-----------------|
| python | `source env/bin/activate && python run_worker.py` | `source env/bin/activate && python run_workflow.py` |
| go | `go run worker/main.go` | `go run start/main.go` |
| ts | `npm run worker` | `npm run client` |
| java | `mvn -q compile exec:java -Dexec.mainClass=moneytransferapp.MoneyTransferWorker -Dorg.slf4j.simpleLogger.defaultLogLevel=warn` | `mvn -q compile exec:java -Dexec.mainClass=moneytransferapp.TransferApp -Dorg.slf4j.simpleLogger.defaultLogLevel=warn` |
| dotnet | `dotnet run --project MoneyTransferWorker` | `dotnet run --project MoneyTransferClient` |
| ruby | `ruby worker.rb` | `ruby starter.rb` |

The scaffold install-comment also varies by where deps land — keep the comment exactly as the template shows for that `‹sdk›`/`‹manager›` (python/ts say "inside the repo"; go/java/dotnet/ruby say "GLOBAL, outside the repo …"). The worked example and templates below carry the right wording per SDK; for non-python SDKs use the install comment from `scripts/provision.sh preview scaffold --sdk ‹sdk›` if you ever need to re-verify it (maintenance only).

### Templates

**Phase 1 — `preflight`** (static):

````
**Checking your environment**

```bash
# check git / jq / brew are available (read-only, local)
command -v git jq brew

# check the Temporal config directory is writable (so temporal.toml can be saved)
touch "$(dirname "<config_path>")/.probe" && rm -f "$(dirname "<config_path>")/.probe"

# flag any stray TEMPORAL_* env vars that would override your saved config
env | grep '^TEMPORAL_' || true
```
````

**Phase 1 — `detect-tools`:**

````
**Detecting your local tools**

```bash
# detect which package managers are installed for ‹sdk› (read-only, local)
command -v ‹probe-bins›

# read each tool's version to flag anything below the minimum
‹runtime› --version
```
````

**Phase 1 — `install-cli` (not installed):**

````
**Installing the Temporal CLI**

```bash
# install the Temporal CLI via Homebrew (adds software)
brew install temporalio/prerelease/temporal-cloud
```
````

**Phase 1 — `install-cli` (already installed — render this variant instead when the CLI is present):**

````
**Updating the Temporal CLI to the latest**

```bash
# BETA: the prerelease CLI has no real versions yet, so always pull the latest (adds/updates software)
brew upgrade temporalio/prerelease/temporal-cloud
```
````

**Phase 1 — `install-cli` (already installed, non-macOS — render this variant when the CLI is present and you're not on macOS; there's no prerelease tap to upgrade from):**

````
**Updating the Temporal CLI to the latest**

```bash
# already installed; update temporal-cloud manually from https://github.com/temporalio/cloud-cli/releases/latest
```
````

**Phase 1 — `login`** (static):

````
**Sign in to Temporal Cloud**

```bash
# open a browser to sign in (blocks until you finish)
temporal cloud login

# confirm the signed-in identity
temporal cloud whoami
```
````

**Phase 1 — `regions`** (static):

````
**Listing your Cloud regions**

```bash
# list the regions your account can use
temporal cloud region list
```
````

**Phase 2 — `start-namespace`:**

````
**Creating your Cloud namespace**

```bash
# create your Cloud namespace - billable; submits async, provisions server-side (~a few min)
temporal cloud namespace create --name <name> --region ‹region› --api-key-auth-enabled --retention-days 30 --auto-confirm --async
```
````

**Phase 2 — `create-namespace`** (the synchronous variant — rare; the flow uses `start-namespace` + `await-namespace`):

````
**Creating your Cloud namespace**

```bash
# create your Cloud namespace - billable; provisions server-side (~a few min)
temporal cloud namespace create --name <name> --region ‹region› --api-key-auth-enabled --retention-days 30 --auto-confirm
```
````

**Phase 2 — `scaffold` (clone + deps):**

````
**Downloading the sample app (clone + dependencies)**

```bash
# clone the Cloud-ready sample
git clone --branch money-transfer-project-cloud-setup --single-branch ‹repo-url› ‹clone-dir›

# install dependencies with ‹manager› ‹install-location-note›
(cd ‹clone-dir› && ‹install-cmd›)
```
````

`‹install-location-note›` per SDK (keep verbatim): python = `into a local venv (env/) inside the repo` · ts = `into node_modules inside the repo` · go = `into the shared Go module cache - GLOBAL, outside the repo (~/go/pkg/mod)` · java = `into the shared Maven cache - GLOBAL, outside the repo (~/.m2)` · dotnet = `into the global NuGet cache - GLOBAL, outside the repo (~/.nuget/packages)` · ruby = `into globally-installed gems - GLOBAL, outside the repo`.

**Phase 2 — `await-namespace`** (static):

````
**Waiting for the namespace to provision**

```bash
# poll until the namespace is ACTIVE — provisioning usually takes ~a few minutes (bounded)
temporal cloud namespace list --name <namespace-name> -o json
```
````

**Phase 2 — `create-key`** (secret carve-out — the token is captured to a 0600 file, never shown; **never** add a token slot):

````
**Creating your API key and saving the config**

```bash
# mint the key + write the cloud-setup profile to temporal.toml (token captured to a 0600 file, never printed)
temporal cloud apikey create-for-me --display-name money-transfer-cloud-setup-<random> --expiry-duration 25h --auto-confirm -o json
```
````

**Phase 2 — `verify-config`** (static):

````
**Verifying the saved config**

```bash
# list the cloud-setup profile fields (api_key redacted, never shown)
temporal --profile cloud-setup config list
```
````

**Phase 3 — `await-auth`** (static):

````
**Waiting for the API key to be accepted**

```bash
# poll an authorized call until the new key is accepted (bounded ~90s)
temporal --profile cloud-setup workflow list --limit 1
```
````

**Phase 3 — `run-workflow` (clean run):**

````
**Run your first Workflow**

```bash
# Worker - runs in the background, polls the task queue, stopped when done
(cd ‹clone-dir› && ‹worker-cmd›)

# starter - submits the Workflow, waits for COMPLETED, exits (the run can take a minute or two)
(cd ‹clone-dir› && WORKFLOW_ID=money-transfer-demo ‹starter-cmd›)
```
````

**Phase 4 — `run-workflow … --demo-failure transient` (inject + recover):**

````
**Run the recovery Workflow (inject a failure)**

```bash
# Worker - runs in the background, polls the task queue, stopped when done
(cd ‹clone-dir› && DEMO_FAILURE=transient ‹worker-cmd›)

# starter - submits the Workflow, waits for COMPLETED, exits (the run can take a minute or two)
(cd ‹clone-dir› && WORKFLOW_ID=money-transfer-demo-recovery ‹starter-cmd›)
```
````

(Utility subcommands — `clone`, `install-deps`, `provision-and-scaffold`, `repair-config` — are **rare** and have no dedicated template; derive their gate from the `scaffold`/`install-cmd` shapes above if you ever invoke one.)

### Worked example — the `scaffold` gate for Java, fully filled

`‹sdk›` = java → `‹repo-url›` = `https://github.com/temporalio/money-transfer-project-java`, `‹clone-dir›` (default) = `money-transfer-project-java`, `‹manager›` = `maven`, `‹install-cmd›` = `mvn -q -DskipTests dependency:resolve`, `‹install-location-note›` = `into the shared Maven cache - GLOBAL, outside the repo (~/.m2)`. The rendered gate:

````
**Downloading the sample app (clone + dependencies)**

```bash
# clone the Cloud-ready sample
git clone --branch money-transfer-project-cloud-setup --single-branch https://github.com/temporalio/money-transfer-project-java money-transfer-project-java

# install dependencies with maven into the shared Maven cache - GLOBAL, outside the repo (~/.m2)
(cd money-transfer-project-java && mvn -q -DskipTests dependency:resolve)
```
````

## Start — show the plan, then begin Phase 1

This skill begins when the user invokes it (e.g. `/temporal-cloud-setup`) or asks to set up Temporal Cloud. On start, print the roadmap, then go straight into Phase 1 (whose first step is choosing the SDK). Do **not** narrate.

Print this opening block verbatim — the ⚠️ notice first, then the plan and the profile line:

```
> ⚠️ **Heads-up:** this creates real resources in your Temporal Cloud account — a namespace and an API key — which may incur cost.

**Let's get you set up on Temporal Cloud.** Four phases, end to end.

1. **Get set up** — install the CLI, sign in, and choose your SDK + region
2. **Download the sample app & create your API key** — create your Cloud namespace and clone the money-transfer app (already wired for Cloud) in parallel, then mint your API key
3. **Run your first Workflow** — start the Worker and run the money-transfer Workflow
4. **See Durable Execution** — break the transfer on purpose and watch Temporal recover it

I'll show each command before running it — and depending on your setup, your tool may ask you to approve it first.

Setting up for:  **<OS> · SDK pending**
```

The ⚠️ Heads-up in that block is a notice, not a blocking gate — continue unless the user objects.

**Selections are collected up front, in Phase 1, while the user is most engaged** — SDK first (no prerequisite), then region right after sign-in (the live region list requires being logged in). Do not begin cloning before the SDK answer — the SDK selects which repo is cloned.

## Phase output envelope

This is the **single source of truth for per-phase formatting** — the phase bodies below supply only *content* (the intent sentence and the steps); this envelope supplies the *format*. Render every phase in this fixed order:

1. **Tracker line** at the top, marker advanced (see below).
2. **Intent sentence** — one short line on what this phase sets up and why it matters (gloss any Temporal term). No more than one line.
3. **Step checklist — once, all unchecked** (the phase plan). Then run each step (real tool call with a friendly `description`, or a genuine question) **without re-printing the checklist or tracker between steps**. Render an already-present prerequisite as `[x] … already present, skipped` (except the Temporal CLI, which updates when present — render it updated/up-to-date, not "skipped"). **No** `**What this did:**` summary and **no** `↪ Learn more:` link during the run.
4. **End-of-phase: completed checklist + checkpoint** — print the checklist once more with **every box checked**, show `**Phase N complete ✅**`, and **close that same message** with the numbered checkpoint prompt (its content is detailed in the next section — it belongs to *this* message, it is not a second message). In Codex-style runtimes, this entire block must be the final assistant message of the turn when you pause for the user; do not print it earlier as progress and then repeat or fragment it in the final response. No checkpoint after Phase 4 — go straight to the Ending.

The tracker is just the four phase markers and the phase counter — **no leading label** (don't prefix it with "Setup" or anything before the first marker). Legend: completed = `✅`, current = `🔵`, upcoming = `⚪` (a white dot — same filled-circle style as the blue current dot). **Bold the current step's name** (the one with the blue dot). Reprint it at the top of each phase, advancing one marker:

```
🔵 **Set up** · ⚪ App & API key · ⚪ Run · ⚪ Recover   ·  phase 1/4
✅ Set up · 🔵 **App & API key** · ⚪ Run · ⚪ Recover   ·  phase 2/4
✅ Set up · ✅ App & API key · 🔵 **Run** · ⚪ Recover   ·  phase 3/4
✅ Set up · ✅ App & API key · ✅ Run · 🔵 **Recover**   ·  phase 4/4
```

(Glyph notes: `⚪` white dot = upcoming and `🔵` blue dot = current — same filled-circle style, so the row reads as one consistent set. `✅` = the reliably-green completion mark; a green *circle*-with-check isn't a dependable cross-platform glyph, so stick with `✅`.)

## After-phase checkpoint (after Phases 1–3)

This documents the checkpoint prompt that the envelope's step 4 already emits as the closing lines of the completed-checklist message — **it is described here, not a second message to send.** It hands control back via a numbered prompt (not an arrow-select — numbered works on every runtime). **Do not explain anything proactively**; the checklist already told the story. At a turn boundary, the checkpoint handoff must be self-contained and emitted exactly once: tracker/checklist context + `**Phase N complete ✅**` + this prompt together in the final assistant message. The prompt is:

```
1. Continue
2. I have a question about this phase

Choose a number, or write your response.
```

- If they pick **2 (question):** give a short, plain-language explanation of what the phase just did, answer their typed question in newcomer-friendly language, then re-present the numbered prompt — `1. Continue` / `2. I have another question` / `Choose a number, or write your response.` — and loop until they proceed.
- Explanation is **on-demand only** — it appears solely when they pick the question option.
- A checkpoint follows Phases 1–3. **No checkpoint after Phase 4** — go straight to the Ending.
- Genuine blocking input (SDK pick, browser sign-in, region pick) is normal work, **not** this checkpoint (genuine input, not a checkpoint).

---

# The phases

```text
Phase 1 — Get set up:            choose SDK · install CLI · sign in · choose region
Phase 2 — App & API key:         create namespace + clone sample + install deps (parallel) · create API key · write config TOML
Phase 3 — Run your first Workflow: start the Worker · run the Workflow (success)
Phase 4 — See Durable Execution: inject a failure · watch Temporal retry & recover  ──► then END
```

<phases>

## Phase 1 — Get set up

*Intent: get the tools on your machine, sign you in, and capture your choices — everything the rest of the run needs.*

Step checklist: `SDK chosen` · `Tools detected` · `CLI installed` · `Signed in` · `Region chosen`.

**Step — Choose your SDK** (genuine input, not a checkpoint): present the six as a **numbered list** (numbered list, runtime-agnostic) — Python, Go, TypeScript, Java, .NET, Ruby — and take a typed name/number. This selects which repo is cloned and the language of the local app. Echo the resolved profile line (`Setting up for: macOS · Python SDK`) once answered.

Right after the SDK pick, the **preflight** check (DISCLOSE — render, then run): render its gate from the `preflight` template (§Gate templates), then run `scripts/provision.sh preflight --sdk <sdk>`. Note its `cli_installed` flag — it drives whether the Install-CLI step below installs (absent) or updates the existing CLI (present). If its `stray_env` lists any `TEMPORAL_*` vars, tell the user they override the saved profile and ask them to unset them before continuing; surface other `warnings` (e.g. `brew-missing`, `no-json-parser`) only if they block a later step.

**Step — Detect local tools + choose your package manager** (DISCLOSE — render, then run). Render its gate from the `detect-tools` template (§Gate templates), then run `scripts/provision.sh detect-tools --sdk <sdk>` and read its RESULT. This adapts the setup to the user's machine, and it surfaces tooling problems **early** (here in Phase 1) instead of deep in Phase 2/3.

- **Package manager (Python & TypeScript only).** `managers` is the set of package managers **this sample supports** for the chosen SDK. When it lists more than one, ask **which of the sample-supported managers to use** — frame it that way ("the sample supports these — which should we use?"), **not** as "here's what's installed on your machine." Present them as a **numbered list** (runtime-agnostic) with the `default` marked — e.g. Python `1. pip (default)` / `2. uv`; TypeScript `1. npm (default)` / `2. pnpm` / `3. yarn`. The user confirms the default or overrides; carry the choice into Phase 2 as `scaffold --manager <m>`. **This is a question — ask it alone and wait for the answer; do not disclose install-cli or sign-in in the same message** (see "One step at a time"). For **Go / Java / .NET / Ruby** the sample has a single toolchain — state it (`Using: maven`) and **skip the prompt**.
- **Surface `discrepancies` HERE (fail-early), plain language:**
  - `version-too-old:<tool>@<have>(min<min>)` — an **advisory** warning with remediation (e.g. *"Node 16 detected; 18+ recommended — consider upgrading, but I can proceed"*). Not a hard stop.
  - `tool-missing:<runtime>` / `manager-not-found:<m>` — the runtime or chosen manager isn't installed. Offer another **sample-supported** manager from `managers`, or ask the user to install the tool, then re-run `detect-tools`.
- The default proposal is **deterministic** — the same machine yields the same default every run; nothing is persisted (no state file).

**Step — Install or update the unified Temporal CLI** (DISCLOSE — render, then run). It ships the `temporal cloud` command group (binary `temporal-cloud`). **Branch on preflight's `cli_installed`** (it used the same `temporal cloud` probe the installer does, so it's authoritative — don't re-check by calling `install-cli` just to confirm):

- **`cli_installed=true` → update it to the latest.** Render its gate from the `install-cli` (already-installed) template (§Gate templates), then run `scripts/provision.sh install-cli`. **BETA stopgap:** the prerelease CLI has no meaningful version numbers yet, so instead of a real "is it out of date?" check we always try to pull the latest from the `temporalio/prerelease` Homebrew tap; `install-cli` returns `status=ok` with `update`=`updated`/`up-to-date`. When it can't update — Homebrew missing, or a non-macOS host — it emits `update=skipped` and proceeds with the working CLI rather than failing (never yank a working install). Once the CLI ships real versions this becomes a genuine version check; we no longer skip a present CLI.
- **`cli_installed=false` → install it.** Render its gate from the `install-cli` (not-installed) template (§Gate templates), then run `scripts/provision.sh install-cli`. It installs via the `temporalio/prerelease` Homebrew tap on macOS, and returns `error_code=brew-missing` / `manual-install` with the fallback URL if it can't — do not auto-install Homebrew; relay the message and wait. (`install-cli` self-checks presence, so if it's actually already there it updates instead of installing.)
- (No prerelease disclaimer here — the ⚠️ notice at the top of the run already covers that.)

This CLI is separate from any local `temporal server start-dev`. The Cloud path does not start a local server.

**Step — Sign in** (**GO-AHEAD** — a browser opens, so wait for the user). Render its gate from the `login` template (§Gate templates), then present `1. Sign in / 2. Chat about this` and wait. On `2`, answer the question and re-present. On `1`, run `scripts/provision.sh login` — it runs `temporal cloud login` (which opens a browser on the user's machine and blocks until they finish) and then confirms with `whoami`. **Do not ask the user to run the command themselves** (no `! temporal cloud login` hand-off); you run the script, the user just completes the browser prompt. Tell them to complete the sign-in in the browser. On success the result block carries `identity`; on `error_code=login-failed`/`not-authenticated`, ask them to finish the browser login and re-run. If they're not part of a Cloud account yet, point them to https://temporal.io/get-cloud and pause.

**Step — Choose your region** (DISCLOSE — render, then run): render its gate from the `regions` template (§Gate templates), then run `scripts/provision.sh regions` (you're authenticated now). It prints the live region list; present it as a **numbered list** (runtime-agnostic), then apply these picking rules:

- **Recommend the nearest** — infer it from the system timezone/locale (e.g. `America/New_York` → suggest `aws-us-east-1`) and mark it `(recommended)`, but the user still picks.
- **Never accept a region from memory and never auto-select** — a valid-but-wrong region creates a persistent, billable namespace in the wrong place (and has set off internal alerts). Use the exact identifier the user picks (shape `<provider>-<region>`); it's passed to the create step next.
- **Fail fast — only accept a region that appears in the `regions` output** (it reflects what your account can actually use). If the user names one that isn't listed, don't pass it to create (a region your account lacks access to is the classic "it spun for minutes" trap) — re-show the list and have them pick a listed value.
- **Steer away from `unsupported_regions`** — the `regions` RESULT may list `unsupported_regions` (regions whose provider reads `UNKNOWN`, e.g. `azure-centralus`). On such accounts those **accept a namespace create but never provision it** — a phantom that stalls the next phase. Mark any listed there as `(may not be available on your account)`, **don't recommend it**, and steer to an AWS/GCP region. If the user insists, warn it may never provision (you'll catch it fast — see `namespace-not-provisioning`).
- **If the create is still rejected** for the region, see Failure Handling (`create-rejected`) — re-list and re-pick, never silently retry the same region.

**If the user asks at the checkpoint, explain (plain language):** installed the Temporal CLI, signed you in, and recorded your SDK + region. Your namespace itself gets created in the next phase — in parallel with setting up your app. (Docs: https://docs.temporal.io/cli)

## Phase 2 — App & API key

*Intent: create your Cloud namespace and download the sample app (clone + dependencies) in parallel, then mint your API key and save the connection config — everything needed to run Workflows on Cloud.*

Step checklist: `Namespace active` · `Sample cloned` · `Dependencies installed` · `API key created` · `Config saved`.

The namespace and the app are set up as **three separate, individually-gated steps** — so the **billable** namespace gets its own explicit approval, distinct from the benign clone. The namespace provisions on Temporal's servers (`--async`) **while** the app is cloned, so the parallelism is preserved without any background process having to survive across steps (identical on Claude Code, Codex, Cursor).

**Step — Start your namespace** (`start-namespace`, DISCLOSE — its own gate, then run; the user's permission prompt approves this **billable** create — make the `description` say so):

- **Fire-and-forget:** submits the create with `--async`, returns immediately, and provisions server-side while you download the sample app.
- **Read `namespace_name`** from the result — you pass it to `await-namespace` below. The handle isn't known yet (it resolves once provisioning completes).
- **Errors:** `create-rejected` (region/name).

**Step — Ask where to clone** (genuine input — **always ask, don't silently default**). Present a two-option numbered choice where **option 1 is the default clone path itself** (so the user sees and confirms the real path) and **option 2 is "Somewhere else"**:

```
Where should I clone the sample app?
1. ./money-transfer-project-template-python
2. Somewhere else
```

- **1** → clone to that path (omit `--dir`, or pass it explicitly — same result).
- **2 (Somewhere else)** → ask for the path, then pass it as `--dir`.

Show the concrete default for the chosen SDK in option 1 (e.g. `./money-transfer-project-template-ts` for TypeScript, `./money-transfer-project-template-go` for Go). Pass the chosen path as `--dir` to `scaffold` below.

**Step — Download the sample app** (`scaffold`, DISCLOSE — its own gate, then run, separate from the namespace):

- **Clones the cloud-ready sample + installs dependencies** — runs **while the namespace provisions**, threading the Phase 1 manager choice and the clone dir just chosen.
- **`--manager`/`--dir` are validated fail-fast before the clone** — a bad/uninstalled manager errors immediately (`manager-not-found` / `unsupported-manager`).
- **Read `repo_path` + `manager`.** Other errors: `clone-failed`, `unknown-sdk`.
- The cloned branch ships wired for Cloud — **no connection code to edit.**

**Step — Wait for the namespace** (`await-namespace --name <namespace_name>`, DISCLOSE — render, then run): render its gate from the `await-namespace` template (§Gate templates), then run `scripts/provision.sh await-namespace --name <namespace_name>`. Polls (via the exact `namespace list --name` filter) until the namespace is **ACTIVE**, then reads the handle + endpoint from that result. Read **`namespace_handle`** + **`address`**; carry both into the key step below. Errors: `namespace-timeout` (appeared but slow — re-run), `namespace-not-provisioning` (never appeared — bad region, re-run `start-namespace` elsewhere), `handle-not-found`.

For reference, the per-SDK repo mapping (the script selects the right one):

| SDK        | Repository (branch `money-transfer-project-cloud-setup`) |
|------------|------------|
| Python     | `https://github.com/temporalio/money-transfer-project-template-python` |
| Go         | `https://github.com/temporalio/money-transfer-project-template-go` |
| TypeScript | `https://github.com/temporalio/money-transfer-project-template-ts` |
| Java       | `https://github.com/temporalio/money-transfer-project-java` |
| .NET       | `https://github.com/temporalio/money-transfer-project-template-dotnet` |
| Ruby       | `https://github.com/temporalio/money-transfer-project-template-ruby` |

**How it connects (no edit needed):** all six SDKs load the **`cloud-setup`** profile from `temporal.toml` (env-config). The key step below writes it; nothing else is needed at run time.

**After `await-namespace` returns, go straight to the `create-key` step — no *phase checkpoint* between them, and don't re-print the checklist or tracker. But `create-key` still gets its own gate — its command is disclosed, then run (the user's permission prompt approves it, like every step); it mints your key *and* writes/replaces the `cloud-setup` profile in `temporal.toml`. The next checklist render is the completed one at the end of the phase.**

**Step — Create the key and save the config** (`create-key --handle <namespace-handle> --address <address>`, DISCLOSE — render, then run, using the values from the `await-namespace` step above). In one deterministic, secret-safe operation the script:

- **re-verifies auth** (`whoami`, re-prompting login if expired);
- **mints the key** with the pinned flags;
- **captures it via `-o json` into a `0600` temp file** so the `eyJ…` token never reaches stdout, your context, or a rendered diff;
- **writes a named `cloud-setup` profile** into the shared `temporal.toml` (address, namespace, api_key) **without touching `[profile.default]`** or its login session;
- **`chmod 600`s the file** and deletes the temp capture.

It returns only the **non-secret** `key_id` and the `config_path` — never the token. Then verify the profile (DISCLOSE — render, then run): render its gate from the `verify-config` template (§Gate templates), then run `scripts/provision.sh verify-config` to confirm the profile loads (it never prints the api_key value).

This is the **secret-handling carve-out** (§ above): render the action's label without the token; never reprint, log, argv-pass, or commit it.

- On `error_code=key-empty`/`not-authenticated`: an expired login — let the script re-prompt and retry once; don't switch output formats or poll.
- On `error_code=key-limit-reached`: the account is at its API-key cap — the mint was rejected at create time. Have the user delete stale keys (`temporal cloud apikey list`, then `temporal cloud apikey delete --key-id <id>` on old `money-transfer-cloud-setup-*` keys), then re-run `create-key`. Don't re-run login.
- On `error_code=no-json-parser`: install `jq` or `python3`, then re-run (the safe capture needs one).
- On `error_code=manual-key-needed`: automatic capture failed and there was no terminal to paste into. Ask the **user** to paste the one-time key and re-run `create-key` from a context with a terminal — the script reads the paste *hidden*, straight into the locked file. **Never** have the user paste the key into the chat, and never paste it yourself.
- The secret is shown only once and cannot be retrieved later; if it's truly lost, mint a new key (re-run this step) — don't try to recover the old value.

**KeyId vs. secret — not the same thing.** The `key_id` the script returns (e.g. `JW4LO…`) is a non-secret *identifier* — the handle used to revoke the key later (`temporal cloud apikey delete --key-id <KeyId>`); fine to show. **Only the `eyJ…` token is the credential** — never reprint, log, or commit it.

**When you check off "API key created," label the `key_id` so a newcomer can't mistake it for the secret.** A bare 32-char `key_id` on its own reads like a leaked key and alarms people. Render it with an explicit non-secret tag, and make the config line state the secret was stored (not shown) — e.g.:

```
- [x] API key created — key id JW4LO… (non-secret identifier; used to revoke the key)
- [x] Config saved — ~/Library/Application Support/temporalio/temporal.toml (chmod 600; secret stored, not shown)
```

Never render the `key_id` bare and unlabeled, and never put the `eyJ…` token on either line.

**Env vars override the profile.** Env-config gives `TEMPORAL_*` env vars **higher precedence** than the TOML profile — the Phase 1 preflight flags any stray `TEMPORAL_ADDRESS`/`TEMPORAL_NAMESPACE`/`TEMPORAL_API_KEY`. If `stray_env` was non-empty, make sure they're unset in the run shell or they'll override the saved profile at run time.

**If the user asks at the checkpoint, explain (plain language):** created your Cloud namespace and, in parallel, cloned a small money-transfer app in your language and installed its dependencies. Then minted an API key for your namespace (`<namespace-handle>`) and saved the connection — address, namespace, key — into a locked `cloud-setup` profile your app reads at run time. (Docs: https://docs.temporal.io/develop · https://docs.temporal.io/cloud/api-keys)

## Phase 3 — Run your first Workflow

*Intent: prove the whole setup works by running a real Workflow on Temporal Cloud.*

Step checklist: `Worker running` · `Workflow completed`.

The app connects from config and Phase 2 supplied the credentials — this phase is **run-only**. All SDKs read the `cloud-setup` profile from `temporal.toml`; confirm it's present with `scripts/provision.sh verify-config` if you haven't already.

**Connect-readiness is handled for you — do not hand-roll the Worker.** The Worker start, the wait-until-it's-polling, the starter, and the Worker teardown all live in **one deterministic call** (`run-workflow`), so you never launch `nohup … &` / `ps` / `pgrep` yourself — that is exactly the flaky, noisy step this replaces. Two things still matter:

1. A freshly-minted API key isn't accepted by the data plane *immediately* — wait on `await-auth` first.
2. If the connect still fails, the namespace endpoint (`<handle>.tmprl.cloud:7233`) is correct — do **not** switch to a regional endpoint, re-mint the key, or edit the profile (per temporalio/documentation#4733). The failure is readiness, not the endpoint.

Run two script calls, both using `repo_path` from Phase 2 (the script handles per-SDK run commands and Python venv activation internally — you don't):

1. **Wait for auth** (`await-auth`, DISCLOSE — render, then run): render its gate from the `await-auth` template (§Gate templates), then run `scripts/provision.sh await-auth` and wait for `auth_ready=true`. On `error_code=key-expired`, the key is permanently rejected (commonly a next-day re-test against a key that auto-expired in ~25h) — re-run `create-key` (see Failure Handling); on `auth-timeout`, read the appended redacted CLI stderr, wait, and re-run.
2. **Run the Workflow** (`run-workflow --sdk <sdk> --dir <repo_path>`, **GO-AHEAD** — the deliberate moment): render its gate from the `run-workflow` (clean run) template (§Gate templates), append `1. Run it / 2. Chat about this` (on `2`, answer, then re-present), and on `Run it` one synchronous call starts the Worker, waits until it's polling (Temporal's API, not the OS process table), runs the starter, and stops the Worker. Wait for `workflow_status=COMPLETED`; it emits the run's **`workflow_id`** + **`run_id`** (don't run `workflow list` yourself). On `worker-unauthorized`, re-run `await-auth` then `run-workflow` (see Failure Handling).
3. **Show the success link, then confirm the win.** `run-workflow` already verified `COMPLETED`. Surface the run's **timeline** page on its own bare line (bare URL so the terminal auto-linkifies it — no backticks/fence), using the `workflow_id` and `run_id` from the RESULT block:

   **View your completed Workflow on Temporal Cloud:**

   https://cloud.temporal.io/namespaces/<namespace-handle>/workflows/<workflow-id>/<run-id>/timeline

   That's your first Workflow on the Cloud — no separate `workflow describe` needed.

   *Fallback — only if `run_id` came back `unknown` (the data plane was briefly lagging): show the Workflow **detail** page instead, rendered exactly like the link above — bold lead-in, then a bare URL alone on its own line (no backticks) so it auto-linkifies:*

   **View your completed Workflow on Temporal Cloud:**

   https://cloud.temporal.io/namespaces/<namespace-handle>/workflows/<workflow-id>

   *Never fall back to the bare `…/workflows` namespace list.*

At the **Phase 3 checkpoint**, lead with the win — `**Phase 3 complete ✅ — your first Workflow ran clean.**` — then the standard numbered prompt (`1. Continue` / `2. I have a question about this phase`). Phase 4 itself frames and triggers the failure injection, so this checkpoint stays a plain **Continue**.

**If the user asks at the checkpoint, explain (plain language):** started a Worker that polls your Cloud namespace, ran the money-transfer Workflow against Temporal Cloud, and confirmed it reached `COMPLETED` — your first Workflow on the Cloud. (Docs: https://docs.temporal.io/workflows)

## Phase 4 — See Durable Execution (inject a failure)

*Intent: break the transfer on purpose and watch Temporal retry and recover it — the durable-execution payoff. This phase is **required**; the user reaches it via **Continue** at the Phase 3 checkpoint, then triggers the break via the prompt below.*

Step checklist: `Failure injected` · `Recovered & completed`.

**Open by framing the break, then let the user trigger it.** After the tracker + intent + unchecked checklist, explain in one or two plain sentences what's about to happen — *we'll run the same transfer again, but force the deposit to fail on its first attempts, then watch Temporal automatically retry until it succeeds* — then present a numbered prompt so the user actively triggers it:

```
1. Inject the failure
2. Chat about this
```

On `1`, run the inject step below; on `2`, answer the question and re-present. This is a genuine engagement point (genuine input, not a checkpoint), not a checkpoint.

> The `DEMO_FAILURE` toggle is shipped on the `money-transfer-project-cloud-setup` branches (the deposit activity reads it), verified end-to-end on real Cloud for all six supported SDKs.

**Step — Inject the failure.** The `1. Inject the failure` choice above is this step's go-ahead — so disclose, then run (don't add a second go-ahead prompt):

- **Disclose:** render its gate from the `run-workflow` (inject + recover) template (§Gate templates).
- **Run:** `scripts/provision.sh run-workflow --sdk <sdk> --dir <repo_path> --demo-failure transient`. Starts the Worker with `DEMO_FAILURE=transient` (the deposit activity fails its first attempts, then succeeds), runs **the same starter command — the sample's source is never edited** (it reads its Workflow ID from the environment), and stops the Worker when done.
- **Distinct Workflow ID:** this run is named `money-transfer-demo-recovery` (vs the clean run's `money-transfer-demo`), so it appears as a **separate Workflow** in Cloud whose history shows the failure-and-recovery.
- **Wait for `workflow_status=COMPLETED`** — the retry recovered it. **Keep this call's `workflow_id` + `run_id`**; they identify the recovery run the Ending link points at.

**Step — Show the recovery.** Keep it to **one line**: the deposit failed on purpose, Temporal retried it automatically, and the Workflow still reached `COMPLETED` (the withdrawal never re-ran) — then send them to the dashboard to see it. Don't walk through the worker logs or event history line-by-line; the dashboard CTA carries the detail.

*(Variant — advanced, manual.)* `DEMO_FAILURE=permanent` makes the deposit fail **non-retryably**, so the **`refund`** compensation runs — the saga/rollback story. Two caveats:

- **Run it by hand, not through `run-workflow`** — `run-workflow` expects `COMPLETED` and would report a non-zero starter as `workflow-failed`.
- **Terminal state differs by SDK** — narrate what the history actually shows, don't assert one outcome:
  - Python / Go / TypeScript / .NET → **`FAILED`** (the original error propagates after the refund).
  - Java / Ruby → **`COMPLETED`** (their saga returns after compensating).

There is **no checkpoint after Phase 4** — go straight to the Ending, whose Cloud-UI link is the recovered run's timeline page (`money-transfer-demo-recovery`).

**If the user asks (plain language):** we made the deposit fail on purpose; Temporal retried it automatically and the Workflow still finished correctly — no lost state, no manual recovery. (Docs: https://docs.temporal.io/encyclopedia/retry-policies)

</phases>

## Ending the Skill

Once Phase 4 has shown the recovery, the setup is done. **Close with a short summary and the recovery link — keep it tight, no big recap table.** Do exactly this:

1. **No Worker should still be running** — `run-workflow` stops its Worker when it returns, so Phases 3 and 4 leave nothing polling Cloud. Only stop a process by hand if you ran the advanced manual `DEMO_FAILURE=permanent` variant.
2. **Show the recovered Workflow, then close with the summary.** First the Cloud UI link (bold lead-in, bare URL alone on its own line, no backticks) — the **recovery run's timeline** page, using the `workflow_id`/`run_id` Phase 4 emitted:

   **View your recovered Workflow on Temporal Cloud:**

   https://cloud.temporal.io/namespaces/<namespace-handle>/workflows/<workflow-id>/<run-id>/timeline

   *Fallback — only if `run_id` is `unknown`: show the Workflow **detail** page the same way — bold lead-in, bare URL on its own line:*

   **View your recovered Workflow on Temporal Cloud:**

   https://cloud.temporal.io/namespaces/<namespace-handle>/workflows/<workflow-id>

   *— never the bare `…/workflows` list.*

   Then close with a short summary (a few plain sentences, no table) that makes the durable-execution payoff concrete — for example:

   > 🎉 You're set up on Temporal Cloud — and you just watched **Durable Execution** in action. Your money-transfer Workflow ran on real Cloud infrastructure, and when the deposit failed on purpose, Temporal automatically retried it until it succeeded — the transfer still completed, with no lost state and not a line of retry code from you. That's the whole idea: you write the business logic; Temporal makes it survive failures and run to completion.

3. **One-line note:** the API key is saved in `temporal.toml` (give the path, `chmod 600`) and **auto-expires in ~25 hours** — don't share raw terminal logs and never commit the TOML.

The summary above is the payoff — keep it to that one short recap. The only calls-to-action are the **two Workflow timeline links** — the completed run (Phase 3) and the recovered run (here at the end). Don't loop back, re-run, keep teaching, offer teardown, or suggest other next steps — a successful completion is the terminal state.

## Failure Handling

On `status=error`, map the `error_code` via **`references/failure-handling.md`** and fix the exact cause it names — never improvise an alternate command, switch output formats, or poll. Read that file only when an error fires (progressive disclosure); the Steps spine's On-error column indexes which codes each step can emit.

## Files

- `scripts/provision.sh` — **the deterministic executor.** Owns preflight / **detect-tools** / **preview** / install / login / regions / namespace-create / **install-deps (manager-parameterized)** / key-mint+config-write / verify / await-auth / **run-workflow (Worker + starter)** / clone / repair-config / cleanup-info. Invoke it and parse its `=== RESULT ===` block (see "Execution model" above); it is the single source of truth for the pinned CLI flags, the per-SDK run commands, **and the per-(SDK,manager) install matrix + minimum-version table**. Pure bash, portable across Claude Code, Codex, and Cursor. **Read-only during a run — invoke it, never edit it (read-only script).**
- `references/unified-cli.md` — background on the prerelease CLI and the client-config TOML: `login`/`whoami`, `region list`, `namespace create`, `apikey create-for-me`, file locations, and the auth-override gotcha. The script encodes these; read the reference when a flag drifts and you need to update the script.
- `references/sdk-cloud.md` — per-SDK table: repo + cloud branch, task-queue name, how each connects (`cloud-setup` profile), and worker/starter run commands. No connection edits — the branch is pre-wired.
- `references/failure-handling.md` — the `error_code` → remediation map. Read it **only when a subcommand returns `status=error`** (progressive disclosure — the happy path never opens it); the Failure Handling section above is a one-line pointer to it, and the Steps spine's On-error column is the index.
