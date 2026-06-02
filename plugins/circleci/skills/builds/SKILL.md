---
name: circleci-builds
description: Diagnose and fix failing CircleCI builds quickly and safely. Use when users ask to investigate failed CircleCI jobs, triage flaky pipelines, identify root causes from logs, and implement minimal fixes in configuration, test setup, or build-related code paths.
---

# CircleCI Builds

## Overview

Use this skill to turn failing CircleCI pipelines into actionable fixes with clear evidence. Prioritize fast root-cause isolation, minimal safe patches, and explicit validation criteria.

Read `references/transient-vs-deterministic.md` when deciding whether a failure should be fixed in code/config, retried, mitigated with rerun behavior, or reported as external/transient.
Read `../config/references/test-results-and-splitting.md` when the failure involves missing test metadata, flaky test reruns, test splitting, or JUnit XML setup.

## Inputs To Gather

- Failing pipeline/workflow/job identifier
- Branch and commit SHA
- First failing step and key log lines
- Whether rerun on same commit reproduces failure

## Workflow

1. Identify the primary failing signal.
   - Record the first failing job and step, not every downstream failure.
2. Classify issue type.
   - Config syntax/reference issue
   - Environment/toolchain mismatch
   - Dependency/cache issue
   - Test or build regression
   - External/transient failure
3. Apply the smallest viable fix.
   - Patch only files tied to confirmed root cause.
   - Keep workaround scope narrow.
4. Validate.
   - Run highest-signal local checks when possible.
   - Define expected CircleCI success signals for the rerun.
5. Report residual risk.
   - Call out unverified assumptions and likely follow-up checks.

## Guardrails

- Do not hide deterministic failures with blanket retries.
- Avoid mixing unrelated refactors into incident fixes.
- Treat external service outages as report-and-mitigate unless user asks for deeper redesign.
- Keep confidence levels explicit when logs are incomplete.
- Do not recommend automatic reruns or flaky-test workflows until the failure is classified as plausibly transient.

## Output Contract

Provide:

1. Failure summary (pipeline/workflow/job/step).
2. Root-cause hypothesis with confidence.
3. Applied changes with file list.
4. Validation plan and expected pass signal.
5. Remaining risk.
