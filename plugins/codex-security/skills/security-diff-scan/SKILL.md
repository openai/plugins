---
name: security-diff-scan
description: "Use when the user asks for a security review of a pull request, commit, branch diff, working-tree patch, or other Git-backed change set."
metadata:
  short-description: Run security diff scan
---

# Security Diff Scan

Used when a user wants to review a Git-backed change set for security regressions. Keep the scan phases separate and produce final HTML and markdown reports.

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

## Goal Setup

Before substantive scan work, create a Codex goal for the scan if the runtime exposes goal tools and no active goal already covers this scan. The objective should state that the scan must not stop until the resolved diff-scoped files have been covered and the required coverage artifacts prove that closure.

Use objective wording shaped like:

`Run the Codex Security diff scan for <resolved target>; do not stop until every diff-scoped file/worklist row has a completion receipt or explicit deferred closure, every candidate has required ledger receipts, and the final report is written.`

If a compatible active goal already exists, continue under it instead of creating a duplicate. If goal tools are unavailable, state the same coverage objective in the first visible scan update and continue.

Do not mark the goal complete until:

- every `deep_review_input.csv` row has a completion receipt in `work_ledger.jsonl`, or an explicit `deferred`, `not_applicable`, or `suppressed` closure with exact reason
- every candidate that reached discovery has the required discovery, validation, and attack-path ledger receipts, or an explicit deferred reason for the missing proof
- the final markdown and HTML reports have been written to the resolved scan paths

## Artifact Resolution

The path references in this skill are the default locations for this phase.
If the user explicitly provides a different path for a required input or output, use the user-provided path instead of the corresponding default path referenced in this skill.
If a required input is still missing, stop and ask the user for it before continuing.
Use the shared scan artifact path conventions in `../../references/scan-artifacts.md`.

## Execution Plan

Follow this plan in order. Do not skip ahead to a later phase until the current phase has produced its intended output.

1. Resolve the Git-backed scan target, `repo_name`, `security_scans_dir`, `scan_id`, `scan_dir`, and `artifacts_dir` using `../../references/scan-artifacts.md`.
2. Create or adopt the scan goal described in `Goal Setup`.
3. Run `$threat-model` first.
  - Copy the repository-scoped threat model to the per-scan threat model path without alteration for auditability.
  - Treat the per-scan threat model path as the source of truth threat model for later phases.
4. Run `$finding-discovery` as the second step, against the resolved diff and using the per-scan threat model as context.
  - If discovery produces no technically plausible candidates, stop there, skip validation and attack-path analysis, and assemble the final markdown report immediately.
5. Run `$validation` as the third step, for each candidate that came out of discovery.
  - Pass the resolved diff scope, discovery notes, and candidate inventory to validation. Validation should preserve or suppress the provided instances; it should not independently broaden the review into a repository-wide scan.
  - Each candidate finding's `findings/<candidate_id>/candidate_ledger.jsonl` is part of the validation input. Every candidate finding that came out of discovery must have a discovery receipt before validation starts and a validation receipt before the scan can proceed to final reporting.
6. Run `$attack-path-analysis` as the fourth step, for findings that still need reportability, attack-path, and severity analysis after validation.
  - Each candidate finding's `findings/<candidate_id>/candidate_ledger.jsonl` is part of the attack-path input. Every candidate finding that reaches attack-path analysis must have an attack-path receipt before final reporting, even when the final decision is `ignore`, suppressed, or deferred.
7. Assemble the final output last using `../../references/final-report.md` and the outputs of the earlier phases: finding discovery plus each candidate finding's validation and attack-path reports.

## Phase Scope

- Phase 1 (threat model generation) is repository-scope by default, unless the user explicitly asks for narrower scope or provides an authoritative threat model or sufficiently repository-specific security scan guidance such as `AGENTS.md`.
- Phase 2 onward (finding discovery, validation, attack path analysis) are diff-focused and should follow the changed code and its supporting files.

Treat this asymmetry as intentional:

- use the diff to locate the scan target for later phases
- do not let the diff bias Phase 1 threat model generation, if applicable
- do not let the touched subsystem become the repository threat model unless the user explicitly asks for that narrower scope

## Scan Target

Resolve the exact Git-backed diff before starting:

- PR: compare base branch against current `HEAD`
- commit: scan the target commit against its parent or requested baseline
- branch diff: scan the requested merge-base to head range
- local patch: scan staged and unstaged working-tree changes against the requested base

## Diff-Scoped Discovery

Use `../security-scan/references/scan-artifacts-and-ledger.md` for the shared scoped file-review, candidate-ledger, subagent, and dedupe rules.

Diff scans should:

- generate `rank_input.csv` deterministically from changed source-like files with `python3 <plugin_dir>/scripts/generate_rank_input.py make-diff-rank-input --repo <repo_root> --base <base> --mode revisions --head <head> --out <artifacts_dir>/rank_input.csv` for PR, commit, and branch diffs, or `python3 <plugin_dir>/scripts/generate_rank_input.py make-diff-rank-input --repo <repo_root> --base <base> --mode local-patch --out <artifacts_dir>/rank_input.csv` for a local patch
- copy every diff row into `deep_review_input.csv` with `python3 <plugin_dir>/scripts/generate_rank_input.py copy-deep-review-input --rank-input <artifacts_dir>/rank_input.csv --out <artifacts_dir>/deep_review_input.csv`
- deep-review every file in `deep_review_input.csv`
- add directly supporting files only when repository evidence shows they are needed to understand the changed security behavior
- stay anchored to the changed code and directly supporting files rather than broadening into unrelated repository-wide enumeration

## Diff-Scoped Sibling Coverage

For PR, commit, branch, and local-patch scans, stay diff-focused but preserve repeated vulnerable instances that are created or affected by the same changed pattern.

Diff scans should:

- start from the changed files and the supporting files needed to understand the changed behavior
- expand from a changed route, handler, shared helper, guard, template pattern, query builder, serializer/deserializer, filesystem/network sink, config block, or wrapper to sibling instances that the diff also changes, newly reaches, or affects through the same modified shared dependency
- when the diff adds, removes, or reshapes a guard around an existing parser, deserializer, expression evaluator, filesystem/path helper, archive utility, or auth/authz helper, use the adjacent pre-existing sink/control as supporting context for the changed behavior; keep the candidate anchored to the changed guard or newly exposed path unless the user explicitly asks for wider instance expansion
- when a changed wrapper, guard, or API delegates to a shared parser/deserializer/path/archive/auth helper, keep both the wrapper call site and the underlying shared sink/control line addressable; do not replace the root sink/control evidence with wrapper-only evidence
- carry each vulnerable sibling instance through discovery and validation with its own affected location, source, closest control, sink, impact, and suppression evidence
- use unchanged siblings as context and negative controls, but report them only when the diff makes them newly vulnerable or changes the shared control or sink they depend on
- stop when the diff-linked pattern family is exhausted, rather than broadening into repository-wide enumeration

This keeps diff scans precise while avoiding the common failure mode where one representative route or sink hides additional vulnerable siblings introduced by the same patch.

## Final Output

Assemble the final markdown report, final HTML report, and Codex app review directives using `../../references/final-report.md`. Commit scans use this same final-output contract because they are a diff-scan target type.

## Hard Rules

Read `../../references/shared-hard-rules.md` before applying scan-mode-specific hard rules.

- Create or adopt the scan goal before substantive scan work, and do not complete it until the resolved diff-scoped files/worklist rows, candidate ledgers, and final report meet the `Goal Setup` closure criteria.
- Do not claim diff coverage until every `deep_review_input.csv` row has a completion receipt in `work_ledger.jsonl`.
