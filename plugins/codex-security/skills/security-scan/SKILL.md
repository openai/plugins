---
name: security-scan
description: "Use when the user asks for a repository-wide or scoped-path security scan."
metadata:
  short-description: Run security scan
---

# Security Scan

Used when a user wants to audit an entire repository or a user-specified path, package, folder, or submodule-like scope for security vulnerabilities. Keep the scan phases separate and produce final HTML and markdown reports.

## Phase Sequence

Keep these phases distinct and run them in linear order:

1. `$threat-model`
2. `$finding-discovery`
3. `$validation`
4. `$attack-path-analysis`
5. Generate final output

Treat this skill as the top-level orchestrator for the four skills plus the final report assembly step. Do not collapse the phases together.

For each phase:
1. Read that phase's skill.
2. Load only the inputs required for that phase.
3. Complete that phase's workflow and checklist.
4. Only then read the next phase's skill.

Do not read ahead into later-phase skills until the current phase has completed.
Do not amortize effort across phases: complete each phase to the full depth expected by that phase before moving on.
If user requests a repo-side scan or a scoped scan, stop and ask for authorization for subagents now before setting up the goal.

## Goal Setup

Before substantive scan work, create a Codex goal for the scan if the runtime exposes goal tools and no active goal already covers this scan. The objective should state that the scan must not stop until the resolved files in scope have been covered and the required coverage artifacts prove that closure.

Use objective wording shaped like:

`Run the Codex Security repository/scoped-path scan for <resolved target>; do not stop until every in-scope file/worklist row has a completion receipt or explicit deferred closure, every candidate has required ledger receipts, and the final report is written.`

If a compatible active goal already exists, continue under it instead of creating a duplicate. If goal tools are unavailable, state the same coverage objective in the first visible scan update and continue.

Do not mark the goal complete until:

- every file or worklist row in the resolved scope has a completion receipt, or an explicit `deferred`, `not_applicable`, or `suppressed` closure with exact reason
- every candidate that reached discovery has the required discovery, validation, and attack-path ledger receipts, or an explicit deferred reason for the missing proof
- the final markdown and HTML reports have been written to the resolved scan paths

## Artifact Resolution

The path references in this skill are the default locations for this phase.
If the user explicitly provides a different path for a required input or output, use the user-provided path instead of the corresponding default path referenced in this skill.
If a required input is still missing, stop and ask the user for it before continuing.
Use the shared scan artifact path conventions in `../../references/scan-artifacts.md`.

## Execution Plan

Follow this plan in order. Do not skip ahead to a later phase until the current phase has produced its intended output.

1. Resolve the scan target, `repo_name`, `security_scans_dir`, `scan_id`, `scan_dir`, and `artifacts_dir` using `../../references/scan-artifacts.md`.
2. Create or adopt the scan goal described in `Goal Setup`.
3. Run `$threat-model` first.
  - Copy the repository-scoped threat model to the per-scan threat model path without alteration for auditability.
  - Treat the per-scan threat model path as the source of truth threat model for later phases.
4. Run `$finding-discovery` as the second step, against the resolved repository or scoped path and using the per-scan threat model as context.
  - Stop at discovery only when the ranked runtime-surface worklist exists and the coverage ledger has closed every applicable high-impact and seeded root-control row as `suppressed`, `not_applicable`, or `deferred` with exact reasons. Open, reportable, or unresolved seeded rows continue to validation even when they are not yet numbered as findings.
5. Run `$validation` as the third step, for each candidate that came out of discovery and each open, reportable, or deferred seeded/root-control ledger row that still needs closure.
  - Pass the resolved scan scope, discovery notes, and candidate inventory to validation. Validation should preserve or suppress the provided instances; it should not independently broaden or narrow the requested repository or scoped-path scan.
  - Each candidate finding's candidate-ledger path from `../../references/scan-artifacts.md` is part of the validation input for every scan scope. Every candidate finding that came out of discovery must have a discovery receipt before validation starts and a validation receipt before the scan can proceed to final reporting.
  - For repository-wide and scoped-path scans, the discovery worklists, work ledger, raw candidates, per-finding candidate ledgers, deduped candidates, and discovery coverage ledger from `../../references/scan-artifacts.md` are part of the validation input; the ledger is a coverage artifact, not just a findings tracker. Raw candidates should already include the discovering file-review subagent's or parent agent's candidate-local validation evidence and attack-path facts before dedupe, and each per-finding candidate ledger should prove that its raw candidate finding received both checks or has an explicit deferred reason. Validation should preserve checked surfaces with not_applicable, suppressed, deferred, and reportable dispositions, reconcile cross-file proof gaps, and continue the ledger's high-impact sibling checks when needed rather than narrowing to one representative finding.
  - When multiple candidates or coverage-ledger rows need validation and subagents are available and approved, divide validation across validation subagents by candidate, deduped candidate, or ledger row. Each validation subagent must receive the candidate or row, discovery evidence, artifact paths, and candidate-ledger path it owns, then write or return the validation report update and validation receipt for that assignment.
  - As coverage-ledger rows are validated, keep the saved per-finding validation reports current enough that reportable, suppressed, not_applicable, and deferred closure rows survive interruption or later phase summarization, including exact root-control file:line and seed-anchor file:line when distinct.
6. Run `$attack-path-analysis` as the fourth step, for findings and validation closure rows that still need reportability, attack-path, and severity analysis after validation.
  - Each candidate finding's candidate-ledger path from `../../references/scan-artifacts.md` is part of the attack-path input for every scan scope. Every candidate finding that reaches attack-path analysis must have an attack-path receipt before final reporting, even when the final decision is `ignore`, suppressed, or deferred.
  - When multiple validated candidates or validation closure rows need attack-path analysis and subagents are available and approved, divide attack-path work across attack-path subagents by candidate or row. Each attack-path subagent must receive the validation evidence, affected root-control and sink lines, artifact paths, and candidate-ledger path it owns, then write or return attack-path facts, severity/policy analysis, and the attack-path receipt for that assignment.
7. Assemble the final output last using `../../references/final-report.md` and the outputs of the earlier phases: finding discovery plus each candidate finding's validation and attack-path reports.

## Scan Scope

- Phase 1 (threat model generation) is repository-scope by default, unless the user explicitly asks for narrower scope or provides an authoritative threat model or sufficiently repository-specific security scan guidance such as `AGENTS.md`.
- Phase 2 onward (finding discovery, validation, attack path analysis) remain within the resolved repository or scoped path. For repository-wide scans, the entire checked-out repository is in scope. For scoped-path scans, the requested path, package, folder, or submodule-like boundary is in scope together with directly supporting files needed to understand concrete findings.
- Before the `$finding-discovery` phase, read `references/repository-wide-scan.md` and every required reference it lists, then use them for finding discovery, validation, and attack path analysis.

## Scan Target

Resolve the requested audit scope before starting:

- repository-wide: scan the entire checked-out repository
- scoped path: scan the user-specified path, package, folder, or submodule-like boundary inside the checked-out repository

Treat the resolved repository or scoped path as the in-scope codebase for the later phases of this workflow.

## Scoped Exhaustive Mode

For repository-wide and scoped-path scans, follow `references/repository-wide-scan.md` and every required reference it lists.

If the user doesn't explicitly authorize subagents, stop and ask for the permission because the use of subagents is vital to the performance of exhaustive repository or scoped-path scans. If you are pursuing a goal and authorization for subagents is needed, block the goal and ask for authorization first, or the scan will not work.

Use the per-scan artifact directory layout from `../../references/scan-artifacts.md`.

## Final Output

Assemble the final markdown report, final HTML report, and Codex app review directives using `../../references/final-report.md`.

## Hard Rules

Read `../../references/shared-hard-rules.md` before applying scan-mode-specific hard rules.

- Create or adopt the scan goal before substantive scan work, and do not complete it until the resolved in-scope files/worklist rows, candidate ledgers, and final reports meet the `Goal Setup` closure criteria.
- For repository-wide and scoped-path scans, do not equate broad sink counts with completed coverage. The coverage ledger must close each applicable high-impact shard row as `reportable`, `suppressed`, `not_applicable`, or `deferred`.
- For every scan scope, candidate-finding coverage is required. Do not finalize a candidate finding until its candidate-ledger path from `../../references/scan-artifacts.md` shows discovery, validation, and attack-path receipts for that exact candidate, or an explicit deferred reason for the missing proof.
- For repository-wide and scoped-path scans, subagent dispatch must have explicit ownership: ranking subagents own one `rank_input.csv` row and return only ranking JSON; file-review subagents own one assessed file or tiny shard and return full-file receipts plus pre-dedupe finding objects with candidate-local validation evidence and attack-path facts; validation subagents own one candidate or ledger row that needs validation closure; attack-path subagents own one validated candidate or validation closure row; the parent agent owns orchestration, ledger reconciliation, aggregation, cross-file dedupe, and final closure.
- For repository-wide and scoped-path scans, candidate-finding coverage is separate from file coverage. Do not dedupe or finalize a raw candidate finding until its candidate-ledger path from `../../references/scan-artifacts.md` shows candidate-local validation and candidate-local attack-path receipts, or an explicit deferred reason for missing proof.
- Candidate ids are optional links from coverage rows to findings; a not_applicable, suppressed, or deferred row is still required when the surface was in scope.
- For repository-wide and scoped-path scans, the ranked runtime-surface worklist must exist before discovery is considered complete, and the coverage ledger must be materially broader than the promoted candidate list.
- For repository-wide and scoped-path scans with CVE, GHSA, advisory, issue, release, or package-version identifiers, `seed_research.md` must exist before discovery is considered complete. It should record authoritative sources searched, candidate files/functions/classes/hunks, and failed lookup attempts. Missing seed research means advisory-led discovery is incomplete unless the scan explicitly states that no network/local-history source was available.
- In large repository-wide scans, checkpoint the ranked runtime-surface worklist and initial coverage ledger to disk before deep sink review or validation. A run that is interrupted after frontier mapping should still leave auditable coverage artifacts.
- In large monorepos, top product/runtime areas by file count or deployment significance must appear as ledger shards or be explicitly excluded with repository evidence; global sink counts and `no top candidate surfaced` do not close coverage.
- User/advisory/tag-seeded packages, class families, or vulnerability families remain open until the exact seeded row is closed as `reportable`, `suppressed`, `not_applicable`, or `deferred`. A neighboring same-family finding does not close the seeded row.
- For large repository-wide scans, make one reachability pass across every applicable high-impact shard before prolonged validation of any single shard. A row becomes a validation candidate only when it has a concrete entrypoint or privileged boundary, closest relevant control, sink or broken control, and plausible impact.
- Discovery is incomplete when a shard has a promoted finding but still has unclosed sibling packages, concrete implementations, or reusable root-control rows that could be independently vulnerable. Finish those rows or mark them explicitly deferred before final reporting.
- Final assembly must start from reportable validation closure rows and surviving candidates. Do not drop a reportable seeded/root-control row because attack-path analysis or discovery spent more prose on a neighboring same-family finding.
- Final reporting is incomplete when a promoted high-impact finding's affected lines omit the concrete root-control file/line discovered or seeded during discovery, such as a codec, converter, parser feature setup, class filter, resource-path control, protocol state transition, or self-service update guard. Add the root-control affected line or explicitly suppress/defer it with exact counterevidence before finalizing.
- In repository-wide and scoped-path scans, preserve independently reachable sibling instances through final reporting. Repeated vulnerable templates, query builders, parser operations, auth/object endpoints, or shared-helper callers need separate finding entries, affected lines, and dispositions; put grouping in summary prose only after the individual instances are emitted.
- For query/parser injection, do not suppress syntax-control evidence solely because a later business check appears to limit impact. Carry the injection candidate until validation proves the exact query API and post-query guard defeat semantic change for that instance.
- If large-repository scope forces deferral, make the final report explicit about which deployed or privileged areas and vulnerability families remain deferred.
