---
name: fix-finding
description: Use when the user explicitly asks to fix and verify a validated or plausible security finding. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.
metadata:
  short-description: Fix and verify security findings
---

# Fix Finding

## Objective

Turn a security finding into a minimal, validated code change when the issue still exists. If the issue is already fixed, prove that with focused validation and report that no code change was needed. The result should include the fix if one was needed, focused regression tests or another repeatable validation check, proof that normal behavior still works, and proof that the original issue no longer reproduces.

## Inputs

Start by extracting any available finding details:

- title and affected component
- vulnerable source, sink, or broken control
- attacker-controlled input
- expected security invariant
- impact and required preconditions
- existing PoC, reproducer, test, or validation evidence
- files and line references

If a critical field is missing, inspect the repository to fill it from code evidence. Ask the user only when the fix would otherwise require guessing a product policy or security invariant.

## Note on Runtime Validation

Use this guidance whenever reproducing the finding, running tests, or validating the fix:

- Try hard to make runtime validation run before falling back to code inspection.
- First consult the repository instructions such as `AGENTS.md`, `README.md`, setup docs, test docs, build files, or package-manager metadata for the necessary requirements.
- If dependencies, generated files, services, or local setup are missing, use the repository's documented setup, package manager, build system, or existing test commands to install or generate what is needed.
- Treat setup errors as intermediate blockers to investigate and repair with targeted commands, not as an immediate reason to abandon runtime validation.
- Do not abandon a reproduction, build, test, or validation command just because it takes time when there is output, resource usage, generated artifacts, or other evidence of progress and no hard evidence of failure.
- If a long-running command appears inconclusive, run targeted checks such as process status, recent logs, output file timestamps, resource usage, or test runner status to distinguish progress from a hang before stopping or weakening validation.

## Workflow

1. Scope the fix.
   - Inspect the affected files and the smallest set of supporting files needed to understand the vulnerable path.
   - Identify the narrowest code boundary where the security invariant should be enforced.
   - Check for existing helpers, validators, permission checks, sanitizers, policy objects, and test patterns before adding new ones.
2. Reproduce or encode the issue before fixing when feasible.
   - Prefer a failing regression test, unit test, integration test, property test, or realistic-interface reproduction.
   - Follow the runtime validation guidance above before deciding runtime reproduction is not feasible.
   - If runtime reproduction is not feasible, create the strongest bounded static or harness-based validation artifact available and document the proof gap.
   - Do not keep a test that exercises unsafe behavior unless it is safe, deterministic, and appropriate for the repository.
   - If the issue no longer reproduces before any code changes, investigate whether it was already fixed and preserve the validation evidence.
3. Generate the fix.
   - Make the smallest behavior change that enforces the intended invariant.
   - Avoid broad refactors; prefer local, established abstractions unless a larger change is required to enforce the security invariant.
   - Preserve existing APIs unless changing the API is the security fix.
   - Handle error paths explicitly and avoid silently accepting unsafe input.
   - Skip code changes when repository evidence and validation show the finding is already fixed.
4. Add repeatable validation.
   - Add focused regression coverage that fails on the vulnerable behavior and passes after the fix.
   - Include positive coverage for legitimate behavior that should still work.
   - Add tests at the lowest level that proves the invariant, plus an interface-level test when the vulnerable path is externally reachable and feasible.
5. Validate the fix works.
   - Run the focused tests that cover the changed code.
   - Run the original PoC or reproducer, if one exists, and confirm it no longer succeeds.
   - Follow the runtime validation guidance above before falling back to code inspection.
   - Re-check the original source-to-sink or broken-control path in the fixed code.
   - Search nearby call sites or variants that might bypass the new control.
   - Confirm the regression test would fail if the fix were removed, when practical.
   - Run any relevant unit tests, integration tests, formatter, linter, type checker, package-specific dependency check, and other repository checks normally required for the touched files.
6. Report the outcome with exact commands, results, changed files, and remaining risk.

## Completion Checklist

Use this checklist before calling the fix complete:

- The original finding is restated in concrete source/sink/control terms.
- The fix enforces the security invariant at the right boundary.
- A focused regression test or validation artifact covers the exploit condition.
- Legitimate behavior remains covered.
- The original PoC, failing test, or reproduction no longer succeeds.
- Focused tests pass after the fix.
- Runtime validation followed the guidance in "Note on Runtime Validation", including setup repair and long-running command checks when applicable.
- If no code change was made, evidence shows the issue was already fixed or not reproducible in the current code.
- Relevant unit tests, integration tests, formatters, linters, type checks, dependency checks, and other required repository checks were run when appropriate.
- Nearby bypasses and equivalent call paths were checked.
- Any unvalidated claim is explicitly labeled as a proof gap.

## Output Contract

In the final response, include:

- summary of the fix
- files changed
- tests or validation artifacts added
- commands run and their pass/fail results
- explicit statement of how the original issue was shown not to reproduce
- whether code changes were needed or the issue was already fixed
- remaining uncertainty or skipped validation, if any

If using a scan artifact directory, resolve it using `../../references/scan-artifacts.md`, then write a visible report to the fix report path. If there is no existing scan directory, a final chat summary is sufficient unless the user asks for a file.

## Hard Rules

- Do not claim the issue is fixed until the changed code and the original vulnerable path have both been checked.
- Do not rely only on code inspection when a focused test or reproducer is feasible.
- Do not give up on runtime validation at the first missing dependency, generated file, or setup error; make a bounded, evidence-driven effort to repair the validation path.
- Do not treat a slow build or test as failed without hard failure evidence; if progress is unclear, verify with targeted status, log, artifact, or resource checks before deciding it is blocked.
- Do not broaden scope into unrelated cleanup.
- Do not remove user changes or unrelated local modifications.
- Do not weaken authentication, authorization, tenant isolation, input validation, sandboxing, or logging to make tests pass.
- Do not hide proof gaps. If the environment blocks validation, say exactly which command or setup failed and what evidence is still missing.
