---
name: deep-security-scan
description: Use when the user asks for a deep, exhaustive, multi-pass, or variance-reducing repository-wide or scoped-path Codex Security scan. Run repeated independent discovery passes over one resolved scope with worker-specific threat models, semantically merge candidates, synthesize one canonical validation threat model, then run validation, attack-path analysis, canonical JSON completion, and generated reporting once. Do not use for PRs, commits, branch diffs, or working-tree diffs.
metadata:
  short-description: Run a deeper Codex Security scan
  capability-profile: deep_security_scan
---

# Deep Security Scan

## Setup Workspace Routing

When this skill is the active top-level workflow, use the setup workspace only when the host context explicitly says it is running inside the Codex desktop app and both required setup continuation tools are available. Tool availability alone does not identify the app host. Otherwise, including Codex CLI interactive and headless runs, use the prompt-only terminal/chat workflow: do not call Codex Security app setup tools, ask the user to press Start scan, or wait for an app-generated `scanId`.

Treat goal creation as scan execution, not setup. In the app setup path, do not create or adopt scan goals before the user presses Start scan, the authoritative scan context has been loaded from a `status: "started"` wait result or a direct continuation with a `scanId`, and the capability preflight has returned `ready`. This includes coordinator and worker-local goals.

For an app continuation that already includes a `scanId` and optional `handoffClaimToken`, do not open another workspace: call `get_codex_security_scan_context` with the `scanId`, pass its `handoffClaimToken` when present, route elsewhere only if its validated mode differs, and use its target, optional `userContext`, and `scanDir`.

The top-level coordinator must inspect `otherRunningDeepScans` only once for each newly launched scan: immediately after the first scan context load for that handoff and before preflight, goal creation, worklist creation, or worker creation. Treat this gate as passed for the current scan when the list is empty or the user chooses `Continue`. Do not repeat the check on later context loads, if another scan appears after the current scan already passed this gate, or after the current scan has progressed beyond preflight. Delegated workers do not perform this check.

- If it is empty, continue normally.
- If it is non-empty, show a compact warning. For each other scan, include only its target path, current phase in plain language, and human-friendly start time. Do not include scan IDs, raw timestamps, update times, or commentary about stale records or interrupted threads. Add one short sentence that running Deep Security Scans concurrently can increase CPU, memory, and token consumption and slow both scans.
- After showing those details in an interactive Codex session, optimistically call `request_user_input` so the user can choose without typing:

```text
request_user_input(
  questions=[
    {
      "header": "Deep scan?",
      "id": "concurrent_deep_scan",
      "question": "Another Deep Security Scan is running. Continue this one?",
      "options": [
        {
          "label": "Cancel (Recommended)",
          "description": "Stop this new scan before preflight or substantive work."
        },
        {
          "label": "Continue",
          "description": "Proceed even though both scans may run more slowly and use more resources."
        }
      ]
    }
  ]
)
```

- If `request_user_input` is unavailable or errors, ask the user to choose `Continue` or `Cancel` in chat. In either case, stop for the answer. Do not run preflight, create or adopt goals, create shared worklists, or create workers while waiting.
- Continue only after explicit confirmation. If the user chooses `Cancel`, call `fail_codex_security_scan` for the new scan with a concise cancellation reason and perform no substantive scan work. Do not modify or fail any previously running scan.

Otherwise, in a host that renders MCP Apps and exposes the Codex Security setup continuation tools:

1. Resolve setup arguments directly from the user's initial prompt and known thread context: local `targetPath` (for scoped-path requests, use the scoped directory itself as `targetPath`), `mode: "deep"`, `scope: "."`, and only user-supplied security focus as `userContext`.
2. Perform only the minimal path resolution needed to construct those arguments. Do not run capability preflight, inspect the repository, threat model, discover findings, or create workers before setup opens.
3. Immediately call `open_codex_security_workspace` with the resolved arguments. Do not search for or substitute a separate scan command.
4. Immediately call `await_codex_security_scan_start` with the `sessionId` from the workspace returned by `open_codex_security_workspace`. A returned workspace with `setup.submitted=false` is the expected wait state. Keep the tool call pending while waiting for the user to review setup and press Start scan; do not create or adopt coordinator or worker-local goals, run preflight, or pivot to terminal/chat fallback while waiting.
5. If the wait returns `status: "started"`, require its `scanId`, call `get_codex_security_scan_context` with that `scanId`, and pass its `handoffClaimToken` when present. Apply the `otherRunningDeepScans` confirmation above, then run the preflight in `../../references/config-preflight.md` for the selected target and `deep_security_scan` profile before goal setup, threat modeling, worker creation, or other substantive scan work.
6. If the wait returns `status: "already_delivered"`, end the current turn without loading scan context or starting scan work. Another continuation already owns the scan.
7. If the wait returns `status: "timed_out"`, end the current turn and tell the user to finish setup and use **Continue in Codex** after pressing Start scan. Do not run preflight, create or adopt coordinator or worker-local goals, open another workspace, or pivot to terminal/chat fallback.
8. Continue after a `ready` result, explaining material warn or suggest limitations. If preflight is `blocked` or `incomplete` with actionable remediation, present the exact reasons and config delta, ask whether to apply the remediation, and stop for the user's answer before creating or adopting coordinator or worker-local goals or calling `fail_codex_security_scan`. Do not fail automatically for declined or unavailable remediation, helper errors, or a non-ready rerun. Preserve the running scan and retry or hand off while recovery may still be possible. If the user declines required remediation, ask whether to cancel or leave the scan running for a later retry. Call `fail_codex_security_scan` with the exact reason only after documented recovery is exhausted and the blocker is confirmed unrecoverable, or when the user explicitly cancels.

In Codex CLI, including interactive and headless runs, or hosts without those capabilities, use the existing prompt-only terminal/chat preflight and scan workflow and shared artifact paths. Do not call `open_codex_security_workspace` or `await_codex_security_scan_start` on this path. The terminal/chat fallback cannot use this app-backed concurrency check; continue its existing workflow unchanged. Once `open_codex_security_workspace` succeeds in an MCP Apps-capable host, remain on the app path: immediately call `await_codex_security_scan_start`; a `status: "timed_out"` result means end the turn and point the user to **Continue in Codex**, while `status: "already_delivered"` means stop because another continuation owns the scan. Do not start a terminal/chat fallback for either result.

## Overview

Deep Security Scan is a higher-recall wrapper around Codex Security's repository-wide and scoped-path scan modes. It preserves the ordinary Codex Security phase model and final report shape, but repeats the most variance-sensitive phase, finding discovery, before centralized judgment.

The wrapper owns orchestration only:

1. resolve one repository-wide or scoped-path scan target using Codex Security's exhaustive-scan semantics
2. run repeated independent discovery workers, each of which generates its own target-specific threat model before `$codex-security:finding-discovery`
3. semantically merge discovery outputs into one canonical candidate inventory
4. synthesize one canonical validation threat model from the worker threat models after discovery reaches a terminal state
5. run `$codex-security:validation`, `$codex-security:attack-path-analysis`, canonical JSON completion, and generated report finalization once

Do not replace Codex Security's established scan rules with custom shortcuts.

## Required Capabilities

Read `../../references/config-preflight.md` and dispatch and await the preflight execution described there with the `deep_security_scan` capability profile before evaluating the workflow-specific requirements below, including after an app wait or direct continuation has produced a `scanId` and loaded its authoritative scan context. Follow the returned block/warn/suggest results. For an app-generated scan, ask before applying actionable remediation and wait without creating coordinator or worker-local goals or calling `fail_codex_security_scan`. Do not fail automatically for declined or unavailable remediation, helper errors, or a non-ready rerun; preserve the running scan and retry or hand off while recovery may still be possible. Call `fail_codex_security_scan` only after documented recovery is exhausted and the blocker is confirmed unrecoverable, or when the user explicitly cancels. Do not treat a config value that differs from a suggested patch as a warning unless the capability requirement itself is unmet.

Before starting substantive scan phases, confirm that the Codex Security plugin skills needed by this workflow are available:

- `$codex-security:security-scan`
- `$codex-security:threat-model`
- `$codex-security:finding-discovery`
- `$codex-security:validation`
- `$codex-security:attack-path-analysis`

If any required skill is unavailable, stop and say that this Codex Security installation does not include the required scan skills. Do not silently degrade into a different workflow.

This workflow also requires parallel delegated workers for repeated discovery. Treat explicit invocation of Deep Security Scan as the user's request for this delegated-worker workflow. If delegation is unavailable in the current environment, do not claim Deep Security Scan ran; explain the limitation and offer an ordinary Codex Security scan as the fallback path.

When delegated discovery workers are spawned from the current scan thread, use the host's default `agent_type`, model, and reasoning effort. The canonical worker brief below is self-contained; on native v2, spawn each discovery worker with `fork_turns=none` so coordinator history is not inherited.

## Goal Setup

After the app wait or direct continuation has provided a `scanId`, the authoritative scan context has been loaded, and the `deep_security_scan` capability preflight has returned `ready`, or after the same preflight is `ready` in Codex CLI or terminal/chat hosts without the setup app, create or adopt a Codex goal for the full Deep Security Scan if the runtime exposes `/goal` or goal tools and no active goal already covers this scan. The objective should state that the scan must not stop until the shared exhaustive worklists exist, discovery either reaches a terminal state or records the first-round no-plausible-candidates path, canonical discovery artifacts and any candidate ledgers are assembled, centralized validation and attack-path receipts are complete or explicitly deferred when those phases are required, and the final markdown report is written.

Use objective wording shaped like:

`Run the Codex Security Deep Security Scan for <resolved repository target>; do not stop until the shared exhaustive worklists exist, discovery is saturated, capped, or on the first-round no-plausible-candidates path, canonical discovery artifacts and any candidate ledgers are assembled, centralized validation and attack-path receipts are complete or explicitly deferred when those phases are required, and the final markdown report is written.`

If a compatible active goal already exists in the coordinator thread, continue under it instead of creating a duplicate. If goal tools are unavailable, state the same coverage objective in the first visible scan update and continue.

Every delegated discovery worker must also create or adopt a worker-local Codex goal before substantive worker discovery if the worker runtime exposes `/goal` or goal tools. Use objective wording shaped like:

`Run Deep Security Scan discovery worker <round id>/<worker id> for <resolved repository target>; do not stop until the worker-specific threat model and discovery artifact set are written, every assigned shared worklist row has a worker-local completion receipt or explicit deferred closure, and the worker summary is returned to the coordinator.`

If a compatible active goal already exists in the worker thread, continue under it instead of creating a duplicate. If goal tools are unavailable inside the worker, the worker must state the same objective in its first visible update and continue.

Worker goals are discovery-worker scoped only. A worker must not mark its worker-local goal complete until its threat model, discovery report, repository-wide ledgers, candidate ledgers, and coordinator-facing summary are saved or returned for the assigned worker artifact paths. The coordinator owns the top-level Deep Security Scan goal and must not mark it complete until:

- the shared `rank_input.jsonl` and exhaustive `deep_review_input.jsonl` exist at the standard discovery paths
- every completed round has exactly six usable worker outputs, all workers idle, merge records, candidate inventories, and novelty comparison artifacts
- the discovery loop has a recorded terminal state of `saturated` or `capped`
- the canonical merged discovery report, deduped candidates, repository coverage ledger, and per-candidate ledgers are aligned
- for scans that enter the centralized tail, centralized validation and attack-path analysis have written required receipts or explicit deferred reasons for every canonical candidate or closure row that requires them
- the final markdown report has been written to the resolved final scan path

When this skill is the active top-level workflow, keep the setup and scan execution boundaries separate. Follow `Setup Workspace Routing` above for a new app workspace, immediately call `await_codex_security_scan_start`, and keep that call pending while the user reviews setup and presses Start scan. Do not enter `Goal Setup` until a `status: "started"` wait result or direct continuation provides a `scanId`, the authoritative scan context has been loaded, and the capability preflight has returned `ready`. If the wait returns `status: "timed_out"`, end the current turn and direct the user to **Continue in Codex**. If it returns `status: "already_delivered"`, end the turn because another continuation owns the scan. A workspace with `setup.submitted=false` is still the app path and must not be treated as terminal/chat fallback. In Codex CLI or hosts without the required app capabilities, use the existing terminal/chat workflow and shared artifact paths.

## User-Facing Contract

- The final answer should feel like an ordinary Codex Security result.
- Do not expose discovery rounds, recurrence counts, worker-by-worker results, or merge bookkeeping in the final report unless the user explicitly asks.
- Preserve Codex Security's normal canonical JSON, generated-report, and review-directive contract by using `../../references/final-report.md`.
- Keep intermediate artifacts for auditability, but do not dump them into the user-facing result.

## Non-Negotiable Orchestration Invariants

These invariants are part of the workflow contract. Do not relax, reinterpret, or replace them with coordinator improvisation.

- exactly `6` usable discovery workers per completed round
- the same canonical discovery brief for every worker, except for mechanical substitutions such as target metadata, round id, worker id, and worker-specific artifact paths
- no themed lanes, candidate-family hints, prior-round novelty hints, or coordinator-added framing around worker prompts
- no shared pre-discovery threat model; each worker must generate and use its own worker-specific threat model for the resolved target
- the coordinator must create one shared authoritative `<discovery_dir>/rank_input.jsonl` plus one exhaustive shared `<discovery_dir>/deep_review_input.jsonl` before the first discovery round, and every discovery worker must consume that same shared worklist pair without regenerating, reranking, or overwriting it
- collect all round outputs before merge
- wait for every worker in the round to complete and become idle before any later round is spawned
- merge only preserved artifacts from completed workers, never live worker state
- during an active discovery round, the coordinator is orchestration-only: it may resolve paths, create shared worklists, monitor worker progress, verify artifact existence, and check parseability or schema conformance, but it must not perform repository-specific security discovery, sink hunting, candidate generation, or validation prep grounded in target code
- before all six workers in a round have completed and become idle, the coordinator may inspect worker artifacts only for existence, completeness, parseability, and schema conformance; it must not read substantive candidate content or infer emerging vulnerability families from partial-round outputs
- the canonical candidate inventory, novelty comparison, and semantic merge may be derived only from preserved completed worker artifacts collected after a round closes; coordinator-originated repo analysis, side notes, or pre-merge hypotheses are not discovery inputs
- merge candidates only when the merged candidate's remediation would remediate every upstream candidate being merged; if fixing the merged issue would leave any upstream issue independently exploitable, independently reportable, or otherwise materially unresolved, keep them separate
- maintain Codex Security's standard `finding_discovery_report.md` candidate shape through every merge pass; the merged report is the canonical candidate inventory, not a later summary derived from some other inventory
- every canonical merged candidate must remain present in the merged discovery report passed to validation unless validation itself later rejects it; no candidate may disappear during artifact synthesis or support-artifact consolidation
- every canonical merged candidate must have a standard canonical `findings/<candidate_id>/candidate_ledger.jsonl` record that names the absorbed worker candidates and ledgers it subsumes before centralized validation begins
- do not spawn a later round until the prior round has fully completed its output collection, worker idle transition, merge, and novelty comparison
- stop only after a fully completed round produces zero new canonical merged discovery candidates
- an incomplete round, failed spawn, or partial merge is never evidence of saturation
- if the initial worker spawn batch fails before any worker has started because the host cannot resolve the current sender thread, treat that as a transient orchestration failure and retry the full round cleanly rather than treating it as worker failure or partial progress

## Shared Setup

Start this setup only after `Setup Workspace Routing` has either loaded the app-generated scan context with a `scanId`, or determined that the host is using the non-app terminal/chat workflow, and the `deep_security_scan` capability preflight has returned `ready`.

1. Read `$codex-security:security-scan` first and follow its repository-wide or scoped-path scan semantics exactly.
2. Resolve one target once: either the full checked-out repository or a user-specified path, package, folder, or submodule-like scope within it. Deep Security Scan does not support PR diffs, commits, branch diffs, or working-tree diffs; direct those requests to ordinary `$codex-security:security-diff-scan`. Never silently widen a scoped-path target to the repository root.
3. Create or adopt the coordinator scan goal described in `Goal Setup` for that active scan context.
4. Resolve the ordinary Codex Security scan paths once using its shared artifact-path rules:
   - `repo_name`
   - `security_scans_dir`
   - `scan_id`
   - `scan_dir`
   - `artifacts_dir`
   - `context_dir`
   - `discovery_dir`
   - `coverage_dir`
   - `reconciliation_dir`
   - `findings_dir`
5. Do not generate a shared pre-discovery threat model in the coordinator.
6. Reserve Codex Security's standard per-scan `<context_dir>/threat_model.md` path for the later canonical validation threat model that will be synthesized only after the discovery loop reaches a terminal state.
7. Create the fixed parent-provided coverage scope before any discovery worker starts:
   - generate `<discovery_dir>/rank_input.jsonl` once using Codex Security's ordinary deterministic exhaustive-scan worklist helper: `<python_command> <plugin_dir>/scripts/generate_rank_input.py make-repo-rank-input --repo <repo_root> --scope <scope> --out <discovery_dir>/rank_input.jsonl`
   - use the repository root as `<scope>` for a repository-wide target and the exact resolved relative or absolute scoped path for a scoped-path target
   - treat Deep Security Scan as exhaustive for this version: run `<python_command> <plugin_dir>/scripts/generate_rank_input.py copy-deep-review-input --rank-input <discovery_dir>/rank_input.jsonl --out <discovery_dir>/deep_review_input.jsonl` and declare that worklist pair authoritative and exhaustive for every worker
   - do not create or require `rank_output.jsonl`; Deep Security Scan does not use ranked truncation in this version
   - every worker must consume those shared standard-path worklists as parent-provided inputs while writing its own worker-local ledgers, candidates, coverage ledger, and discovery report

Do not let individual discovery workers reinterpret or widen the scan target, but do let them independently generate their own target-specific threat models at worker-specific paths before discovery begins.

## Deep Discovery Loop

Run discovery in synchronous rounds:

- `6` independent discovery workers per round
- maximum `10` rounds total
- stop after the first full round that adds no new canonical merged discovery candidates of any kind

For an app workspace scan with a `scanId` and the Codex Security progress tool available, record the one-based `deepReviewPass` at the start of each round, reset completed review items to zero, and update them as that round's file-review receipts close.

Always run at least one round.

After each round:

1. collect that round's discovery outputs
2. confirm every completed discovery worker from that round is idle after its artifacts and summary have been collected
3. merge the completed round's outputs with every prior round's discovery outputs
4. update the canonical candidate inventory
5. compare the canonical inventory against the previous round's canonical inventory
6. stop if no new canonical candidate clusters of any kind were added

Do not reuse completed discovery workers across rounds. Later rounds should consume only the preserved artifacts, not prior worker state. Before spawning any later round, confirm that every worker from the prior round has completed and become idle; do not interrupt an already completed worker.

While a discovery round is active, keep the coordinator neutral. It may perform orchestration bookkeeping and artifact-health checks, but it must not run its own target-specific discovery lane, form candidate hypotheses, queue likely finding families, or do repository-grounded validation preparation before the round closes.

This stop rule measures discovery saturation only. It does not claim that validated findings or final reportable findings have saturated; validation, canonical JSON completion, and report projection still happen once after the discovery loop completes.

If the first round finds no plausible candidates, write the appropriate canonical no-findings discovery artifact and continue directly to the final Codex Security no-findings assembly path.

### Required Round-Transition Checklist

Execute this checklist in order for every completed round. Do not skip steps.

1. confirm the round has exactly six usable completed discovery workers
2. confirm every worker artifact needed for this scan type has been collected under its worker-specific path
3. confirm all six completed workers from the round are idle
4. confirm no worker from that round remains running
5. merge the round's preserved artifacts with prior preserved artifacts into Codex Security's standard discovery-report shape
6. write the merge record, the round-specific candidate inventory, and the canonical merged `finding_discovery_report.md`
7. compute novelty against the prior canonical candidate inventory
8. choose exactly one next action:
   - stop, only if the completed round added zero new canonical clusters of any kind
   - spawn the next six-worker round, only after every prior checklist step is complete

## Worker Isolation

Each discovery worker must be independent:

- same resolved scan target
- its own worker-local Codex goal when the worker runtime exposes `/goal` or goal tools
- its own independently generated threat model for the resolved target written to its worker-specific artifact path
- same Codex Security discovery rules
- same canonical worker brief except for mechanical substitutions such as target metadata, round id, worker id, and output paths
- the same parent-provided authoritative `<discovery_dir>/rank_input.jsonl` and exhaustive `<discovery_dir>/deep_review_input.jsonl` inputs
- no access to prior workers' findings or merge outputs
- no top-level `$codex-security:validation`, no top-level `$codex-security:attack-path-analysis`, and no canonical finalization
- no file edits

The goal is not shallow parallelism; the goal is independent high-quality discovery diversity from repeated same-brief stochastic passes.

## Discovery Worker Brief

Use this canonical brief for every discovery worker. Do not prepend or append extra coordinator prose, skill-path boilerplate, themed emphasis, candidate-family hints, prior-round novelty hints, or coordinator-invented specialty lanes. Only substitute the resolved target details, round id, worker id, and worker-specific output paths required for the run.

```text
You are a discovery worker, not the top-level scan coordinator. Follow this self-contained worker-specific assignment as your task. If you cannot complete it, report the problem to the coordinator rather than taking over or terminating the overall scan.

Run the Codex Security threat-model phase and then the finding-discovery phase only.

Before substantive worker work, create or adopt one worker-local Codex goal if your runtime exposes `/goal` or goal tools. Use this objective:
`Run Deep Security Scan discovery worker <round id>/<worker id> for <resolved repository target>; do not stop until the worker-specific threat model and discovery artifact set are written, every assigned shared worklist row has a worker-local completion receipt or explicit deferred closure, and the worker summary is returned to the coordinator.`

If a compatible active goal already exists in this worker thread, continue under it instead of creating a duplicate. If goal tools are unavailable, state the same objective in your first visible update and continue. Do not mark the worker-local goal complete until the threat model, finding discovery report, repository-wide ledgers, candidate ledgers, and coordinator-facing summary for your assigned artifact paths are saved or returned.

Use the provided resolved scan target exactly as given.
First generate your own threat model for that resolved target using the ordinary `$codex-security:threat-model` rules, but write it only to your worker-specific threat-model output path. Do not read, reuse, overwrite, or infer a shared coordinator threat model.
Then run `$codex-security:finding-discovery` using your own worker-specific target threat model as the threat-model source of truth.
Do not reinterpret the target, run the top-level `$codex-security:validation` phase, run the top-level `$codex-security:attack-path-analysis` phase, author canonical final artifacts, or edit repository files.

Your task is to enumerate technically plausible, distinct security finding candidates as comprehensively as possible for this scope.

Apply the ordinary `$codex-security:finding-discovery` rules in full:
- stay grounded in the code and your worker-specific threat model
- preserve separate root causes rather than cosmetic variants
- keep independently reachable instances separate
- preserve concrete source, closest-control, sink, impact, and affected-location evidence
- consume the parent-provided authoritative `<discovery_dir>/rank_input.jsonl` and exhaustive `<discovery_dir>/deep_review_input.jsonl` exactly as supplied; do not regenerate, rerank, overwrite, or reinterpret them
- treat those standard-path worklists as shared inputs while writing every worker output only to the explicit worker-specific artifact paths supplied for this discovery pass
- for repository-wide and scoped-path scans, perform the normal Codex Security exhaustive deep-review, seed-research, work-ledger, raw-candidate, candidate-ledger, dedupe, repository-coverage-ledger, and frontier-pass work required by finding discovery
- for repository-wide and scoped-path scans, preserve any candidate-local validation evidence and candidate-local attack-path facts that the current Codex Security discovery workflow requires before dedupe; those receipts are discovery support artifacts, not permission to run the later centralized top-level phases
- for repository-wide and scoped-path worker candidate JSONL, use one canonical machine-readable affected-location shape only:
  - `affected_locations` must be an array of objects
  - every object must contain `label`, `path`, and `lines`
  - `detail` may be included when it materially helps later merge or validation
  - use `lines` as a string even for one line, such as `"154"`
  - do not emit string-only locations such as `"src/file.py:154"`, alternate `file` or `line` keys, or separate-only `source_locations` / `root_locations` / `sink_locations` fields without also materializing the unified `affected_locations` array

Return your worker-specific threat model plus the normal discovery artifact set for your worker-specific artifact paths, with enough detail for later centralized semantic merging and validation.
```

## Worker Artifact Layout

Keep the canonical Codex Security scan paths for the final merged pipeline. Put repeated discovery worker artifacts under the canonical `artifacts_dir` without overwriting one another:

```text
<artifacts_dir>/
  02_discovery/
    rank_input.jsonl
    deep_review_input.jsonl
  deep_discovery/
    round-01/
      worker-01/
        threat_model.md
        finding_discovery_report.md
        seed_research.md
        work_ledger.jsonl
        raw_candidates.jsonl
        dedupe_report.md
        deduped_candidates.jsonl
        repository_coverage_ledger.md
        findings/
          <candidate_id>/
            candidate_ledger.jsonl
      worker-02/
        ...
    round-02/
      ...
```

Workers write their worker-local exhaustive discovery artifact set to their assigned paths while sharing only the standard-path `<discovery_dir>/rank_input.jsonl` and exhaustive `<discovery_dir>/deep_review_input.jsonl`.

Give each worker explicit worker-specific output paths so the discovery reports and exhaustive-scan ledgers do not overwrite one another.

For repository-wide and scoped-path workers, the machine-readable candidate streams must use this canonical affected-location contract in both `raw_candidates.jsonl` and `deduped_candidates.jsonl`:

```json
{
  "affected_locations": [
    {
      "label": "root_control",
      "path": "src/example.py",
      "lines": "154",
      "detail": "Optional concise reason this location matters"
    }
  ]
}
```

Treat this as a schema contract, not presentation guidance:

- `affected_locations` is always an array of objects
- `label`, `path`, and `lines` are required on every item
- `detail` is optional
- `lines` is always a string, including single-line locations
- do not substitute string-only locations, `file`, `line`, or parallel source/root/sink-only arrays in place of the canonical array

## Semantic Merge After Each Round

Merge at the level of the underlying actionable candidate, not at the level of title similarity.

Treat two candidates as the same cluster only when a careful security reviewer would consider them the same underlying issue, or when one is a narrower or more specific restatement of the other and keeping both would double-count the same candidate.

Do not merge merely because candidates:

- mention the same subsystem
- share a broad CWE or vulnerability family
- involve the same route family, file family, or helper family
- reuse similar attack language
- have overlapping but materially different exploit paths, broken controls, or affected instances

Remediation-subsumption is required for merge eligibility:

- a merge is valid only when fixing the merged candidate would also fix every upstream candidate being merged
- a merge is invalid when any upstream source/control/sink/impact tuple would remain materially unresolved after the proposed merged fix
- related findings may be cross-referenced or grouped thematically later, but they must remain separate canonical candidates unless they share remediation closure
- example: an authentication bypass and an unsafe path-construction or file-impact bug remain separate if the auth fix does not eliminate the file-impact issue and the file-impact fix does not eliminate the auth bypass

When candidates truly merge:

- keep the strongest title or synthesize a better one
- preserve complementary evidence from every merged member
- preserve distinct affected locations that are part of the same proof tuple
- preserve source/control/sink distinctions that make the claim legible
- keep uncertainty explicit rather than inflating confidence
- produce one stronger canonical candidate than any single member when possible

Use a preserving merge, not a lossy summary:

- the merged candidate should retain any materially useful non-redundant detail from each upstream candidate, including narrower exploit framings, affected subpaths, meaningful preconditions, distinct source/control/sink nuances, and remediation-relevant subcases
- do not reduce dimensionality merely because the topline title becomes broader; if an upstream framing helps validation, advisory/CVE matching, or the later final report, keep that detail visible inside the merged candidate
- synthesize the upstream evidence into one coherent candidate rather than concatenating raw worker prose
- omit only detail that is genuinely duplicative, superseded by a more precise shared framing, or irrelevant after the remediation-subsumption test
- when useful, make the merged candidate explicit that the broader root issue also includes narrower implicated behaviors or subcases inherited from the upstream candidates

When candidates overlap but remain materially distinct, keep them separate.

## Canonical Discovery Outputs

After each merge pass, retain:

- a merge record showing which worker candidates were grouped
- the current canonical candidate inventory
- the canonical merged `finding_discovery_report.md` in Codex Security's normal discovery-report shape
- the novelty comparison against the previous canonical inventory
- the canonical merged candidate set at Codex Security's standard `<reconciliation_dir>/deduped_candidates.jsonl` path
- a canonical dedupe report at Codex Security's standard `<reconciliation_dir>/dedupe_report.md` path
- one standard canonical `<findings_dir>/<candidate_id>/candidate_ledger.jsonl` per merged candidate, recording the discovery provenance, absorbed worker candidate ids, and absorbed worker-ledger paths that justify that canonical candidate
- per-candidate internal provenance:
  - first-seen round
  - contributing workers and source candidate ids
  - later rounds that repeated the same canonical candidate
  - whether later evidence strengthened, narrowed, contradicted, or merely repeated the canonical candidate

Suggested placement:

```text
<artifacts_dir>/deep_merge/
  round-01_merge_record.md
  round-01_candidate_inventory.md
  round-02_merge_record.md
  round-02_candidate_inventory.md
  canonical_candidate_inventory.md
```

Also write and continuously update the canonical merged discovery report at Codex Security's standard final discovery path:

```text
<discovery_dir>/finding_discovery_report.md
```

This report is not a selective promotion list, triage summary, or second consolidation layer. It is the lossless canonical merged candidate set in the same artifact shape that ordinary `$codex-security:finding-discovery` would hand to validation.

Validation and later phases must consume this canonical merged discovery report, not the raw per-worker discovery outputs and not a hand-pruned rewrite of the merged set.

Invariant:

- every candidate present in `canonical_candidate_inventory.md` must also appear substantively in `finding_discovery_report.md`
- every candidate present in `canonical_candidate_inventory.md` must also appear in `<reconciliation_dir>/deduped_candidates.jsonl` and have a canonical `<findings_dir>/<candidate_id>/candidate_ledger.jsonl`
- `finding_discovery_report.md` may improve wording, synthesize complementary evidence, and normalize candidate formatting, but it may not drop, suppress, or silently collapse a canonical candidate
- a canonical merged candidate ledger may consolidate worker provenance, but it may not erase the absorbed worker candidate ids, worker-ledger references, or remediation-subsumption decision that explains why the canonical candidate exists
- if the merge layer determines that a prior candidate was semantically subsumed, that merge must already be represented in the canonical merge artifacts; it may not be re-decided during final discovery-report assembly

## Exhaustive Scan Support Artifact Assembly

For repository-wide and scoped-path scans, assemble the worker discovery support artifacts into canonical artifacts before validation. This is exhaustive-scan workflow plumbing for Codex Security's normal downstream phases, not a second semantic merge, candidate triage layer, or reportability filter.

- `<discovery_dir>/rank_input.jsonl`
  - preserve the shared parent-provided deterministic in-scope source inventory without worker rewrite
- `<discovery_dir>/deep_review_input.jsonl`
  - preserve the shared parent-provided exhaustive review scope without worker rewrite
- `<context_dir>/seed_research.md`
  - merge authoritative sources searched, candidate anchors, and failed lookup attempts when seed research applies
- `<discovery_dir>/work_ledger.jsonl`
  - aggregate worker file-review receipts conservatively while preserving worker provenance; do not claim a file was reviewed without an actual worker receipt
- `<discovery_dir>/raw_candidates.jsonl`
  - aggregate worker-local raw candidate objects with round, worker, and source-candidate provenance intact
- `<reconciliation_dir>/dedupe_report.md`
  - record the canonical Deep Security Scan dedupe outcome in Codex Security's standard reconciliation location
- `<reconciliation_dir>/deduped_candidates.jsonl`
  - write the Deep Security Scan canonical merged candidate set in Codex Security's standard post-dedupe location
- `<findings_dir>/<candidate_id>/candidate_ledger.jsonl`
  - write one canonical merged ledger per canonical candidate, preserving absorbed worker candidate ids and worker-ledger references so later centralized phases can append validation and attack-path receipts to the canonical record
- `<coverage_dir>/repository_coverage_ledger.md`
  - merge semantically equivalent ledger rows conservatively
  - preserve distinct shards and families separately
  - if worker dispositions disagree, keep the more conservative unresolved or open state for centralized validation to settle

Write the canonical consolidated versions back to the numbered standard paths above so `$codex-security:validation` receives the normal exhaustive-scan inputs it expects.

These support-artifact assemblies are mechanical context assembly only:

- they may union, deduplicate, normalize, and conservatively reconcile support-state metadata
- they may preserve open or unresolved coverage rows for validation to settle
- they must not add a second candidate-selection stage
- they must not suppress, downgrade, or silently omit candidates from the canonical merged `finding_discovery_report.md`
- they must not treat a support-ledger omission or weaker worker disposition as permission to remove a canonical discovery candidate
- if the assembled exhaustive-scan support artifacts conflict with the canonical merged `finding_discovery_report.md`, treat that as a consistency problem to repair before validation, not as authority to drop the candidate

## Centralized Tail

Enter the centralized tail only after the discovery loop has a recorded terminal state:

- **saturated**: a fully completed round added zero new canonical clusters of any kind
- **capped**: the maximum round count was reached while novelty was still appearing

It is not valid to continue into validation, attack-path analysis, or canonical finalization merely because:

- the first round produced a strong-looking candidate set
- the coordinator believes the merged inventory is "good enough"
- validation work has already started opportunistically
- the final report would be useful even without a terminal discovery-loop state

Before the centralized tail begins, ensure the discovery artifacts contain the terminal evidence needed to justify it:

- the final completed round's merge record
- the final completed round's candidate inventory
- the canonical candidate inventory after that round
- the canonical merged `finding_discovery_report.md`, with a one-to-one substantive correspondence to the final canonical candidate inventory
- the canonical `<reconciliation_dir>/deduped_candidates.jsonl` plus canonical `<findings_dir>/<candidate_id>/candidate_ledger.jsonl` records aligned one-to-one with the final canonical candidate inventory
- an explicit internal note that the loop ended because it was `saturated` or `capped`

If those artifacts or that terminal state are missing, resume the discovery loop and repair the missing evidence. Do not finalize or fail the scan merely because discovery is incomplete.

Once the recorded terminal state is present:

1. sanity-check the canonical candidate inventory and canonical merged `finding_discovery_report.md` against the underlying discovery evidence
   - remove accidental overclaims
   - repair merges that collapsed distinct issues
   - ensure affected locations and proof tuples remain concrete
   - confirm no canonical candidate disappeared while producing the standard discovery artifact
   - confirm `<reconciliation_dir>/deduped_candidates.jsonl` and the canonical per-candidate ledgers match the same merged candidate set and preserve worker provenance
2. synthesize one canonical validation threat model from the worker threat models and write it to Codex Security's standard per-scan `<context_dir>/threat_model.md` path
   - preserve distinct attacker models, trust boundaries, privileged surfaces, and risk framings that remain relevant to canonical merged candidates
   - normalize contradictions conservatively rather than erasing plausible but materially useful threat-model distinctions
   - treat this canonical validation threat model as downstream context for validation and attack-path analysis, not as a retroactive filter over the discovery candidate set
3. confirm `<context_dir>/threat_model.md` exists, then run `$codex-security:validation` once over the canonical merged discovery inputs
4. run `$codex-security:attack-path-analysis` once over the surviving validated findings and closure rows that require it
5. populate the complete canonical manifest, findings, and coverage JSON once using `../../references/final-report.md`, then complete the scan so finalization generates the markdown report projection; in the terminal/chat workflow without `complete_codex_security_scan`, run `python <plugin_dir>/scripts/finalize_scan_contract.py --scan-dir <scan_dir> --source-root <repo_root>` directly

Do not bypass validation simply because a candidate recurred across multiple discovery workers. Recurrence is search evidence, not reportability proof.

## Final Output Rules

- Emit only the ordinary Codex Security generated report output and review directives expected for the resolved scan target.
- Do not author `report.md`. Populate all report semantics in canonical JSON using `../../references/final-report.md`, call scan completion, and include the generated markdown report path in the response.
- Populate the optional structured details in `../../references/finding-detail-fields.md` from the same validated evidence used in the generated report.
- Keep priorities, severities, confidence, affected locations, validation reasoning, reachability, attack paths, and remediation in the normal Codex Security style.
- Do not mention:
  - number of discovery workers
  - number of rounds
  - candidate recurrence
  - semantic cluster ids
  - raw novelty metrics
- If no findings survive the centralized pipeline, produce the ordinary Codex Security no-findings report.

## Failure Handling

- Incomplete discovery and preserved partial artifacts are resumable conditions. Do not call `fail_codex_security_scan` because a round, turn, context window, or goal run ends with work remaining. Record meaningful progress, leave the durable scan running, and continue or hand off from the saved artifacts. Reserve terminal failure for an unrecoverable blocker after the recovery steps below are exhausted or for an explicit cancellation path.
- If Codex Security dependencies are missing, stop early and explain the dependency.
- If delegated workers are unavailable, stop early and explain that Deep Security Scan requires the parallel delegated-worker workflow.
- If a worker fails, preserve its partial artifacts when available, note the failure internally, and retry or replace only that worker until the round has six usable completed discovery passes.
- Do not count an incomplete round as a no-novelty round.
- Do not reduce the round below six usable workers to keep moving.
- Do not proceed to merge or novelty comparison on partial worker completion.
- Do not reinterpret failed spawning, worker crashes, or missing artifacts as evidence that the candidate space is exhausted.
- Do not enter validation, attack-path analysis, or canonical finalization until the discovery loop has recorded a terminal state of `saturated` or `capped`.
- If the first discovery round adds any new canonical clusters, a later round is mandatory unless the maximum round cap has already somehow been reached.
- Do not stop simply because a new candidate looks weak, low-confidence, non-reportable, or likely to close in validation. Any genuinely new canonical discovery candidate keeps the loop open until the next merge determines whether novelty persists.
- Missing or inconsistent discovery artifacts are recoverable workflow defects, not terminal scan failures. Repair them before merge, validation, or finalization. If repair cannot finish in the current turn, preserve the artifacts, leave the durable scan running, and hand off. Do not call `fail_codex_security_scan` for these defects.
- Treat missing per-round merge records, missing per-round candidate inventories, or missing terminal-state bookkeeping as a repairable bookkeeping defect, not as permission to finalize early.
- Treat any mismatch between `canonical_candidate_inventory.md` and `finding_discovery_report.md` as a repairable consistency defect. Align them before validation; the discovery report may refine merged prose, but it may not omit canonical candidates.
- Treat any mismatch among `canonical_candidate_inventory.md`, `<discovery_dir>/finding_discovery_report.md`, `<reconciliation_dir>/deduped_candidates.jsonl`, and canonical per-candidate ledgers as a repairable consistency defect. Centralized validation must receive one coherent canonical candidate set.
- For repository-wide and scoped-path scans, treat malformed worker `affected_locations` output as a worker-artifact defect that must be repaired before semantic merge. Lossless mechanical normalization is acceptable only for trivial equivalent variants such as `line` -> `lines` or `file` -> `path`; string-only locations or alternate location inventories that cannot be mapped without interpretation are incomplete worker outputs, not merge inputs.
- Treat coordinator-authored target-specific candidate hypotheses, sink hunts, or partial-round substantive worker-result interpretation as orchestration drift to stop and correct before merge; those outputs are not eligible discovery evidence and must not influence novelty, dedupe, or validation inputs.
- Do not mutate later worker prompts based on prior findings, suspected blind spots, or earlier novelty observations.
- If the first worker-spawn batch fails before any worker starts with a sender-thread lookup error such as `no thread with id`, preserve the clean pre-round state, retry the full round once with the same canonical worker brief, and do not count the failed attempt toward round progress.
- If a later round cannot spawn because worker-thread capacity is exhausted, first wait for running workers to finish and collect their artifacts, then retry the spawn once. Completed native-v2 workers are idle and do not need interruption; use `interrupt_agent` only to stop a still-running worker that must be abandoned before retrying.
- If the thread-capacity retry still cannot produce a complete six-worker round, preserve the gathered state and explain that Deep Security Scan could not complete the configured discovery loop normally. Do not silently reduce the round size or claim novelty collapse occurred.
- If the maximum of ten rounds is reached while new candidate clusters are still appearing, continue to the centralized validation pipeline with the best canonical inventory gathered so far. Do not claim novelty collapse occurred.

## Guardrails

- Do not edit repository files during scanning.
- After any app setup handoff has provided a `scanId`, or in the non-app terminal/chat workflow, create or adopt the coordinator goal and worker-local discovery goals described in `Goal Setup` only after the capability preflight has returned `ready` and when goal tools are available. Keep their completion boundaries separate.
- Do not widen or reinterpret a scoped-path target after it has been resolved.
- Do not collapse the Codex Security phases together.
- Do not let discovery workers see one another's results.
- Do not let repeated speculative phrasing turn into a reportable issue without centralized validation.
- Do not merge away independently reachable vulnerable instances that Codex Security would normally keep separate.
