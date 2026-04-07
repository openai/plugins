---
name: test-triage
description: Triage failing macOS tests across Xcode and SwiftPM workflows. Use when asked to run macOS tests, narrow failing scopes, explain assertion or crash failures, or separate real test regressions from setup and environment problems.
---

# Test Triage

## Quick Start

Use this skill to run the smallest meaningful test scope first, classify
failures precisely, and avoid treating every test failure like a product bug.

## Workflow

1. Detect the test harness.
   - Use `xcodebuild test` for Xcode-based projects.
   - Use `swift test` for SwiftPM packages.

2. Narrow the scope.
   - If the user gave a target, product, or test filter, use it.
   - If not, prefer the smallest likely failing target before a full suite.

3. Classify the result.
   - Build failure
   - Assertion failure
   - Crash or signal
   - Async timing or flake
   - Environment or fixture setup issue
   - Missing entitlement or host app issue

4. Rerun intelligently.
   - Use focused reruns when a specific case fails.
   - Avoid burning time on full-suite reruns without new information.

5. Summarize clearly.
   - What command ran
   - Which tests failed
   - What kind of failure it was
   - The best next proof step or fix path

## Guardrails

- Distinguish compilation failures from test execution failures.
- Call out when a test appears to assume iOS-only or simulator-only behavior.
- Mark likely flakes as such instead of overstating confidence.

## Output Expectations

Provide:
- the command used
- the smallest failing scope
- the top failure category
- a concise explanation of the likely cause
- the next rerun or fix step
