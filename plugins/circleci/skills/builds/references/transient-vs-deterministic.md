# Transient Vs Deterministic Failures Reference

Use this reference when deciding whether a failing CircleCI job should be fixed at the source, rerun automatically, rerun manually, or reported as an external/transient issue.

Sources:
- [Automatic reruns](https://circleci.com/docs/guides/orchestrate/automatic-reruns/)
- [Rerun failed tests](https://circleci.com/docs/guides/test/rerun-failed-tests/)

## Classification Goal

- Treat retries as a targeted mitigation for temporary failure modes.
- Treat deterministic failures as defects to fix in code, config, environment setup, or test data.
- Make the classification explicit before suggesting reruns, flaky-test workflows, or automatic retry behavior.

## Likely Transient Signals

- Network timeouts to external package registries or APIs.
- Temporary infrastructure instability.
- Spot/interruption-style executor loss.
- Flaky tests with a history of passing unchanged on rerun.
- A rerun on the same commit succeeds without any code or config change.

## Likely Deterministic Signals

- Config validation errors or missing keys.
- Repeatable dependency install failures caused by bad versions, paths, or credentials.
- Consistent test assertion failures on the same commit.
- Missing files, wrong working directories, or broken environment assumptions.
- Cache or workspace path mismatches that fail the same way every time.

## Rerun Guidance

- Prefer manual investigation first when the first occurrence is ambiguous.
- Recommend automatic step reruns only for steps with a well-understood transient failure pattern.
- Recommend automatic workflow reruns only when rerunning failed jobs is materially cheaper than re-executing the entire workflow and the failure mode is plausibly temporary.
- For flaky tests, prefer `circleci tests run` plus rerun failed tests over rerunning entire workflows.

## Guardrails

- Do not use retries to mask deterministic test or deploy failures.
- Do not introduce blanket reruns across a whole workflow without evidence that the dominant failures are transient.
- Keep retry counts low and explain what symptom they are targeting.
- If the same commit fails repeatedly after reruns, stop escalating retries and fix the root cause.

## Diagnostic Workflow

1. Check whether the failure reproduces on the same commit.
2. Identify whether the first failing step points to config, environment, dependency, test, or external service instability.
3. If tests are involved, check whether rerun-failed-tests prerequisites are configured before recommending that feature.
4. If proposing auto-reruns, scope them to the smallest failing unit that matches the observed transient pattern.

## Common Fixes To Suggest

- Add low-count step reruns for a flaky external dependency fetch step.
- Use rerun failed tests for known flaky test suites once JUnit metadata and `circleci tests run` are configured.
- Remove retries and fix environment parity when failures are deterministic.
- Report external outages clearly when the pipeline itself is healthy but a dependency is not.
