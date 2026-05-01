# Command Conventions

Every slash command in this plugin follows a consistent structure so Codex produces reliable, verifiable Zoom workflow results. Every non-underscore file in `commands/` must include all required sections below.

## Required Sections

### 1. Preflight

Check prerequisites before doing any work:

- Inspect the current repo for the relevant Zoom surface, framework, and existing integration code.
- Confirm required local tools are available before relying on them.
- Note missing credentials, env vars, callback routes, or endpoint URLs before attempting setup or debugging.
- Flag dirty working tree or risky production-impacting changes when they matter to the requested workflow.

Preflight failures should produce clear next actions. Do not silently skip them.

### 2. Plan

State what will happen before execution:

- List the files, commands, and external checks the workflow will use.
- Call out any destructive or production-impacting step and require explicit user confirmation.
- If there are multiple viable paths, state which one was chosen and why.

### 3. Commands

The operational core. Follow these conventions:

- Prefer read-first inspection before making code or config changes.
- Never print secret values. Show env var names, scope names, file paths, and metadata only.
- Use structured output when available.
- Prefer the narrowest Zoom surface that actually solves the task.
- Do not claim OAuth, webhook, or SDK setup succeeded without checking the relevant evidence.

### 4. Verification

After execution, confirm the outcome:

- Re-read the changed files or live state.
- Verify the exact auth, signature, endpoint, or config path that was modified.
- Surface errors, warnings, and unresolved blockers explicitly.

### 5. Summary

Present a concise result block:

```text
## Result
- Action: what was done
- Status: success | partial | failed
- Details: key files, env vars, endpoints, or findings
```

### 6. Next Steps

Suggest the logical follow-up:

- setup flows -> test auth or live API connectivity
- debug flows -> rerun the failing path with the fix applied
- review flows -> apply the recommended fixes or narrow the scope

## File Naming

- Command files live in `commands/` and end in `.md`.
- Files prefixed with `_` are conventions or meta docs, not user-facing commands.

## Frontmatter

Every command file must include YAML frontmatter with at least a `description` field.
