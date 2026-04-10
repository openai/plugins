# /fix-codesign-error

Inspect a macOS signing or entitlement failure and explain the minimum fix path.

## Arguments

- `app`: path to `.app` bundle or binary (optional)
- `identity`: signing identity hint (optional)
- `mode`: `inspect` or `repair-plan` (optional, default: `inspect`)

## Workflow

1. Inspect the app bundle, executable, signing info, and entitlements.
2. Determine whether the problem is identity, provisioning, hardened runtime, sandboxing, or trust policy.
3. Summarize the exact failure class in plain language.
4. Provide the minimal repair sequence or validation command.

## Guardrails

- Never invent entitlements; read them from the binary or source files.
- Distinguish local development signing problems from distribution or notarization failures.
- Prefer verifiable commands like `codesign -d`, `spctl`, and `plutil` over guesswork.
