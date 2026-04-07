---
name: packaging-notarization
description: Prepare and troubleshoot packaging, signing, and notarization workflows for macOS distribution. Use when asked to archive a Mac app, validate bundle structure, reason about notarization readiness, or explain distribution-only failures.
---

# Packaging & Notarization

## Quick Start

Use this skill when the work is about shipping the app rather than merely
running it locally: archives, exported app bundles, notarization readiness,
hardened runtime, or distribution validation.

## Workflow

1. Confirm the distribution goal.
   - Local archive validation
   - Signed distributable app
   - Notarization troubleshooting

2. Inspect the artifact.
   - Validate app bundle structure.
   - Check nested frameworks, helper tools, and entitlements.

3. Inspect signing and runtime prerequisites.
   - Hardened runtime
   - Signing identity
   - Nested code signatures
   - Required entitlements

4. Explain notarization readiness or failure.
   - Separate packaging issues from trust-policy symptoms.
   - Point to the minimum follow-up validation commands.

## Guardrails

- Do not present notarization as required for ordinary local debug runs.
- Call out when you lack the actual exported artifact and are inferring from project settings.
- Keep advice concrete and verifiable.

## Output Expectations

Provide:
- what artifact or settings were inspected
- whether the app looks distribution-ready
- the top missing prerequisite or failure mode
- the next validation or repair step
