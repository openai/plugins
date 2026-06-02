---
name: threat-model
description: Use when Codex is already in the threat-modeling phase of a security scan, the user explicitly invokes $threat-model, or the user explicitly asks to create, update, or persist a repository threat model. Do not use as the primary trigger for full PR, commit, branch, patch, or repository scans.
metadata:
  short-description: Build a repository threat model
---

# Security Threat Model

## Objective

Establish the repository-scoped threat model at the path defined in `../../references/scan-artifacts.md`. If this already exists, stop here. If a threat model or clearly authoritative security scan guidance is provided or already exists, persist it unchanged to this file, then stop here.

`AGENTS.md` can be that authoritative source when it is sufficiently specific about the repository's product surfaces, trust boundaries, attacker-controlled inputs, assumptions, or security scan guidance to serve as the threat model.

If no threat model is provided, generate a repository-scoped threat model to be used in future bug discovery. The threat model should holistically cover the entire repository and should make it obvious:

- what assets or privileges matter
- what trust boundaries exist
- what inputs are attacker-controlled
- what invariants the code must preserve
- what repository-wide failure modes would matter most

## Artifact Resolution

The path references in this skill are the default locations for this phase.
If the user explicitly provides a different path for a required input or output, use the user-provided path instead of the corresponding default path referenced in this skill.
If a required input is still missing, stop and ask the user for it before continuing.
Use the shared scan artifact path conventions in `../../references/scan-artifacts.md`.

## Workflow

1. Resolve `repo_name`, `security_scans_dir`, and the repository-scoped threat model path using `../../references/scan-artifacts.md`.
2. If the repository-scoped threat model already exists, stop here.
3. If a threat model or authoritative security scan guidance is provided or referenced:
   - write it exactly to the repository-scoped threat model path
   - treat that file as the only threat model source of truth
   - do not expand, summarize, or reinterpret it
   - `AGENTS.md` is acceptable here when it is clearly being used as the security scan guidance or threat model source for this scan and is sufficiently repository-specific to stand in for a threat model
4. Otherwise, generate a repository-scoped threat model using the checklist below.
5. Before finalizing this phase, sanity-check that:
   - the threat model is repository-scoped rather than being centered around any specific scan target
   - it describes repository-wide primary product or runtime surfaces and trust boundaries before covering any narrower examples
   - any vulnerability-class discussion is about repository-context classes, not findings about any current diff
6. Write the exact threat model to the repository-scoped threat model path.

## Threat Model Generation Guidance

Generate and structure the threat model using `references/threat-model-guidance.md`.

## Hard Rules

- A provided threat model or authoritative security scan guidance is authoritative.
- Threat model generation must stay at repository scope unless the user explicitly asks for narrower scope.
- Do not turn this phase into findings about any current diff.
- Do not let the current scan target, touched subsystem, or changed directories become the center of gravity for this phase unless the user explicitly asks for that narrower scope.
- In large monorepos, avoid centering `personal/`, `test/`, `tests/`, `docs/`, `examples/`, or one-off developer tooling unless repository evidence shows those are real deployed or privileged workflow surfaces.
- Call out trust boundaries and assumptions explicitly.
- Keep references to vulnerability types at the level of repository-context classes, rather than any diff findings.
- Persist the threat model output to the repository-scoped threat model path from `../../references/scan-artifacts.md`.
