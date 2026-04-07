# /test-macos-app

Run the smallest meaningful macOS test scope first and explain failures by category.

## Arguments

- `scheme`: Xcode scheme name (optional)
- `target`: test target or product name (optional)
- `filter`: test filter expression (optional)
- `configuration`: `Debug` or `Release` (optional, default: `Debug`)

## Workflow

1. Detect whether the repo uses `xcodebuild test` or `swift test`.
2. Prefer focused test execution when a target or filter is provided.
3. Classify failures as compile, assertion, crash, env/setup, or flake.
4. Summarize the top blocker and the narrowest sensible next step.

## Guardrails

- Avoid rerunning the full suite if a focused rerun is possible.
- Distinguish build failures from actual failing tests.
- Note when host app setup or simulator-only test assumptions leak into a macOS run.
