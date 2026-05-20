---
name: security-scan
description: "Use when the user asks for a full security scan or security code review of a pull request, commit, branch, patch, working-tree diff, or repository. Run distinct phases: threat modeling, finding discovery, validation, attack-path analysis, and final markdown output."
metadata:
  short-description: Run security scan
---

# Security Scan

Used when a user wants to scan a pull request, commit, branch diff, working-tree patch, or repository for security vulnerabilities. Keep the scan phases separate and produce a final markdown report.

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

## Artifact Resolution

The path references in this skill are the default locations for this phase.
If the user explicitly provides a different path for a required input or output, use the user-provided path instead of the corresponding default path referenced in this skill.
If a required input is still missing, stop and ask the user for it before continuing.
Use the shared scan artifact path conventions in `../../references/scan-artifacts.md`.

## Execution Plan

Follow this plan in order. Do not skip ahead to a later phase until the current phase has produced its intended output.

1. Resolve the scan target, `repo_name`, `security_scans_dir`, `scan_id`, `scan_dir`, and `artifacts_dir` using `../../references/scan-artifacts.md`.
2. Run `$threat-model` first.
  - Copy the repository-scoped threat model to the per-scan threat model path without alteration for auditability.
  - Treat the per-scan threat model path as the source of truth threat model for later phases.
3. Run `$finding-discovery` as the second step, against the resolved diff and using the per-scan threat model as context.
  - If discovery produces no technically plausible candidates in a diff-scoped scan, stop there, skip validation and attack-path analysis, and assemble the final markdown report immediately.
  - In repository-wide scans, stop at discovery only when the ranked runtime-surface worklist exists and the coverage ledger has closed every applicable high-impact and seeded root-control row as `suppressed`, `not_applicable`, or `deferred` with exact reasons. Open, reportable, or unresolved seeded rows continue to validation even when they are not yet numbered as findings.
4. Run `$validation` as the third step, for each candidate that came out of discovery and, in repository-wide scans, each open, reportable, or deferred seeded/root-control ledger row that still needs closure.
  - Pass the resolved scan scope, discovery notes, and candidate inventory to validation. Validation should preserve or suppress the provided instances; it should not independently decide whether a standalone single-candidate request should become diff-scoped or repository-wide.
  - Each candidate finding's `findings/<candidate_id>/candidate_ledger.jsonl` is part of the validation input for every scan scope. Every candidate finding that came out of discovery must have a discovery receipt before validation starts and a validation receipt before the scan can proceed to final reporting.
  - For repository-wide scans, `rank_input.csv`, `rank_output.csv` when ranking applies, `deep_review_input.csv`, `work_ledger.jsonl`, `raw_candidates.jsonl`, per-finding `findings/<candidate_id>/candidate_ledger.jsonl` files, `deduped_candidates.jsonl`, and the discovery coverage ledger are part of the validation input; the ledger is a coverage artifact, not just a findings tracker. Raw candidates should already include the discovering file-review subagent's or parent agent's candidate-local validation evidence and attack-path facts before dedupe, and each per-finding candidate ledger should prove that its raw candidate finding received both checks or has an explicit deferred reason. Validation should preserve checked surfaces with not_applicable, suppressed, deferred, and reportable dispositions, reconcile cross-file proof gaps, and continue the ledger's high-impact sibling checks when needed rather than narrowing to one representative finding.
  - When multiple candidates or repository coverage-ledger rows need validation and subagents are available and approved, divide validation across validation subagents by candidate, deduped candidate, or ledger row. Each validation subagent must receive the candidate or row, discovery evidence, artifact paths, and candidate-ledger path it owns, then write or return the validation report update and validation receipt for that assignment.
  - As repository-wide rows are validated, keep the saved per-finding validation reports current enough that reportable, suppressed, not_applicable, and deferred closure rows survive interruption or later phase summarization, including exact root-control file:line and seed-anchor file:line when distinct.
5. Run `$attack-path-analysis` as the fourth step, for findings and repository-wide validation closure rows that still need reportability, attack-path, and severity analysis after validation.
  - Each candidate finding's `findings/<candidate_id>/candidate_ledger.jsonl` is part of the attack-path input for every scan scope. Every candidate finding that reaches attack-path analysis must have an attack-path receipt before final reporting, even when the final decision is `ignore`, suppressed, or deferred.
  - When multiple validated candidates or validation closure rows need attack-path analysis and subagents are available and approved, divide attack-path work across attack-path subagents by candidate or row. Each attack-path subagent must receive the validation evidence, affected root-control and sink lines, artifact paths, and candidate-ledger path it owns, then write or return attack-path facts, severity/policy analysis, and the attack-path receipt for that assignment.
6. Assemble the final markdown report last using the final report path from `../../references/scan-artifacts.md` and the outputs of the earlier phases: finding discovery plus each candidate finding's validation and attack-path reports.

## Phase Scope

- Phase 1 (threat model generation) is repository-scope by default, unless the user explicitly asks for narrower scope or provides an authoritative threat model or sufficiently repository-specific security scan guidance such as `AGENTS.md`.
- For PR, commit, branch, and local-patch scans, Phase 2 onward (finding discovery, validation, attack path analysis) are diff-focused and should follow the changed code and its supporting files. Diff scans use `deep_review_input.csv` plus the shared scoped file-review rules in `references/scan-artifacts-and-ledger.md`; when the diff is too large for one parent-agent pass, use approved file-review subagents and aggregation without broadening the scan beyond changed files and directly supporting files.
- For repository-wide scans, Phase 2 onward remain repository-wide. Before the `$finding-discovery` phase, read `references/repository-wide-scan.md` and every required reference it lists, then use them for finding discovery, validation, and attack path analysis.

Treat this asymmetry as intentional:

- use the diff to locate the scan target for later phases
- do not let the diff bias Phase 1 threat model generation, if applicable
- do not let the touched subsystem become the repository threat model unless the user explicitly asks for that narrower scope

## Scan Target

Resolve the exact diff before starting:

- PR: compare base branch against current `HEAD`
- commit: scan the target commit against its parent or requested baseline
- branch diff: scan the requested merge-base to head range
- local patch: scan the working tree diff against the requested base
- repository-wide: scan the entire checked-out repository

For a repository-wide scan, treat the entire checked-out repository as the diff for the later phases of this workflow.

## Diff-Scoped Sibling Coverage

For normal PR, commit, branch, and local-patch scans, stay diff-focused but preserve repeated vulnerable instances that are created or affected by the same changed pattern.

Diff scans should:

- start from the changed files and the supporting files needed to understand the changed behavior
- expand from a changed route, handler, shared helper, guard, template pattern, query builder, serializer/deserializer, filesystem/network sink, config block, or wrapper to sibling instances that the diff also changes, newly reaches, or affects through the same modified shared dependency
- when the diff adds, removes, or reshapes a guard around an existing parser, deserializer, expression evaluator, filesystem/path helper, archive utility, or auth/authz helper, use the adjacent pre-existing sink/control as supporting context for the changed behavior; keep the candidate anchored to the changed guard or newly exposed path unless the user explicitly asks for wider instance expansion
- when a changed wrapper, guard, or API delegates to a shared parser/deserializer/path/archive/auth helper, keep both the wrapper call site and the underlying shared sink/control line addressable; do not replace the root sink/control evidence with wrapper-only evidence
- carry each vulnerable sibling instance through discovery and validation with its own affected location, source, closest control, sink, impact, and suppression evidence
- use unchanged siblings as context and negative controls, but report them only when the diff makes them newly vulnerable or changes the shared control or sink they depend on
- stop when the diff-linked pattern family is exhausted, rather than broadening into repository-wide enumeration

This keeps PR scans precise while avoiding the common failure mode where one representative route or sink hides additional vulnerable siblings introduced by the same patch.

## Repository-Wide Exhaustive Mode

When the scan target is repository-wide, follow `references/repository-wide-scan.md` and every required reference it lists.

Use the per-scan artifact directory layout from `../../references/scan-artifacts.md`.

Important:

Take any commit titles and descriptions with caution. They can be incomplete or misleading. Focus on the actual code and repository evidence.

## Final Output

Assemble the final markdown report and Codex app review directives using `references/final-report.md`.

## Hard Rules

- Keep the phases separate.
- Follow the execution plan in order.
- Use the tools to inspect the repository before making decisions.
- For repository-wide scans, do not equate broad sink counts with completed coverage. The coverage ledger must close each applicable high-impact shard row as `reportable`, `suppressed`, `not_applicable`, or `deferred`.
- For every scan scope, candidate-finding coverage is required. Do not finalize a candidate finding until `findings/<candidate_id>/candidate_ledger.jsonl` shows discovery, validation, and attack-path receipts for that exact candidate, or an explicit deferred reason for the missing proof.
- For diff-scoped scans, do not claim diff coverage until every `deep_review_input.csv` row has a completion receipt in `work_ledger.jsonl`.
- For repository-wide scans, subagent dispatch must have explicit ownership: ranking subagents own one `rank_input.csv` row and return only ranking JSON; file-review subagents own one assessed file or tiny shard and return full-file receipts plus pre-dedupe finding objects with candidate-local validation evidence and attack-path facts; validation subagents own one candidate or ledger row that needs validation closure; attack-path subagents own one validated candidate or validation closure row; the parent agent owns orchestration, ledger reconciliation, aggregation, cross-file dedupe, and final closure.
- For repository-wide scans, candidate-finding coverage is separate from file coverage. Do not dedupe or finalize a raw candidate finding until its `findings/<candidate_id>/candidate_ledger.jsonl` shows candidate-local validation and candidate-local attack-path receipts, or an explicit deferred reason for missing proof.
- Candidate ids are optional links from coverage rows to findings; a not_applicable, suppressed, or deferred row is still required when the surface was in scope.
- For repository-wide scans, the ranked runtime-surface worklist must exist before discovery is considered complete, and the coverage ledger must be materially broader than the promoted candidate list.
- For repository-wide scans with CVE, GHSA, advisory, issue, release, or package-version identifiers, `seed_research.md` must exist before discovery is considered complete. It should record authoritative sources searched, candidate files/functions/classes/hunks, and failed lookup attempts. Missing seed research means advisory-led discovery is incomplete unless the scan explicitly states that no network/local-history source was available.
- In large repository-wide scans, checkpoint the ranked runtime-surface worklist and initial coverage ledger to disk before deep sink review or validation. A run that is interrupted after frontier mapping should still leave auditable coverage artifacts.
- In large monorepos, top product/runtime areas by file count or deployment significance must appear as ledger shards or be explicitly excluded with repository evidence; global sink counts and `no top candidate surfaced` do not close coverage.
- User/advisory/tag-seeded packages, class families, or vulnerability families remain open until the exact seeded row is closed as `reportable`, `suppressed`, `not_applicable`, or `deferred`. A neighboring same-family finding does not close the seeded row.
- For large repository-wide scans, make one reachability pass across every applicable high-impact shard before prolonged validation of any single shard. A row becomes a validation candidate only when it has a concrete entrypoint or privileged boundary, closest relevant control, sink or broken control, and plausible impact.
- Discovery is incomplete when a shard has a promoted finding but still has unclosed sibling packages, concrete implementations, or reusable root-control rows that could be independently vulnerable. Finish those rows or mark them explicitly deferred before final reporting.
- Final assembly must start from reportable validation closure rows and surviving candidates. Do not drop a reportable seeded/root-control row because attack-path analysis or discovery spent more prose on a neighboring same-family finding.
- Final reporting is incomplete when a promoted high-impact finding's affected lines omit the concrete root-control file/line discovered or seeded during discovery, such as a codec, converter, parser feature setup, class filter, resource-path control, protocol state transition, or self-service update guard. Add the root-control affected line or explicitly suppress/defer it with exact counterevidence before finalizing.
- In repository-wide scans, preserve independently reachable sibling instances through final reporting. Repeated vulnerable templates, query builders, parser operations, auth/object endpoints, or shared-helper callers need separate finding entries, affected lines, and dispositions; put grouping in summary prose only after the individual instances are emitted.
- For query/parser injection, do not suppress syntax-control evidence solely because a later business check appears to limit impact. Carry the injection candidate until validation proves the exact query API and post-query guard defeat semantic change for that instance.
- If large-repository scope forces deferral, make the final report explicit about which deployed or privileged areas and vulnerability families remain deferred.
- Avoid destructive commands, interactive editors, and broad unbounded scans.
- Prefer targeted, reversible shell commands.
- For Phase 1 fallback threat model generation, produce a repository-level threat model that would still make sense for an unrelated diff in the same repository.
- Do not let the current scan target bias Phase 1 unless the user explicitly requests a target-scoped threat model.
- For later phases, stay grounded in repository evidence and the actual changed code.
- Do not emit a finding unless it survives the final policy-adjustment pass.
