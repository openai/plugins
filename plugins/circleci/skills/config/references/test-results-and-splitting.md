# Test Results And Splitting Reference

Use this reference when configuring test metadata, test splitting, flaky-test visibility, or rerun-failed-tests support.

Sources:
- [Collect test data](https://circleci.com/docs/collect-test-data/)
- [Use the CircleCI environment CLI to split tests](https://circleci.com/docs/guides/optimize/use-the-circleci-cli-to-split-tests/)
- [Rerun failed tests](https://circleci.com/docs/guides/test/rerun-failed-tests/)

## Goals

- Upload valid JUnit XML so CircleCI can power the Tests tab, flaky test detection, timing-based splitting, and rerun failed tests.
- Make test parallelism measurable before increasing it.
- Keep test execution commands compatible with `circleci tests run`.

## Baseline Requirements

- Use `store_test_results` to upload XML test results.
- Ensure the generated JUnit XML includes `file` or `classname` attributes.
- When enabling rerun failed tests, run tests through `circleci tests run`.
- Keep a copy of the raw XML as an artifact when debugging test metadata issues.

## Split-Test Guidance

- Prefer `circleci tests run --split-by=timings` after test results are already uploading reliably.
- Use `xargs` to pass test files or class names from stdin into the actual test command.
- Match the input type to the framework: file paths for file-based runners, class names when the runner expects class identifiers.
- Do not increase `parallelism` until there is enough test volume and timing data to justify it.

## Setup Heuristics

- Start by making one job produce clean JUnit XML before adding split logic.
- If split timing data is missing or poor, verify XML upload quality before changing test commands.
- Keep the `glob` or test-discovery command narrow and deterministic.
- If the runner cannot be invoked directly inside `circleci tests run`, use it to output the selected file list and run the test command afterward from that list.

## Failure Modes To Check

- `store_test_results` points at the wrong path or an empty directory.
- The XML uploads, but lacks `file` and `classname`, so rerun/splitting features behave unexpectedly.
- Test discovery outputs file names, but the test runner expects class names.
- Parallel reruns leave some nodes with no tests; create required directories before persistence so downstream steps do not fail on empty reruns.
- Teams rely on artifacts only and never enable `store_test_results`, which blocks Test Insights and timing-based features.

## Common Fixes To Suggest

- Add or fix `store_test_results`.
- Upload the same XML with `store_artifacts` while debugging metadata issues.
- Switch from `circleci tests split` to `circleci tests run` when enabling rerun failed tests.
- Add `--verbose` to `circleci tests run` when debugging reruns or split input.
- Reduce or pause test parallelism until timing data becomes trustworthy.
