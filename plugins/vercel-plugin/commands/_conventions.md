# Command Conventions

Every slash command in this plugin follows a consistent structure so that the AI agent produces reliable, verifiable results. When authoring or updating a command file, include **all** of the sections below.

## Required Sections

### 1. Preflight

Check prerequisites before doing any work:

- **Project linked?** — Verify `.vercel/project.json` exists. If not, guide the user through `vercel link`.
- **CLI available?** — Confirm `vercel` CLI is on PATH.
- **Repo state** — Note uncommitted changes, dirty working tree, or detached HEAD when relevant.
- **Scope** — Detect monorepo (e.g., `turbo.json` or `pnpm-workspace.yaml`) and confirm which package is targeted.

Preflight failures should produce clear, actionable guidance — never silently skip.

### 2. Plan

Before executing, state what will happen:

- List the commands or MCP calls that will run.
- Flag destructive or production-impacting operations and require explicit user confirmation.
- If multiple strategies exist (MCP-first vs CLI-fallback), state which path was chosen and why.

### 3. Commands

The operational core. Follow these conventions:

- **MCP-first, CLI-fallback** — Prefer the Vercel MCP server for reads; use CLI for writes or when MCP lacks coverage.
- **Structured output** — Request `--format=json` where available; parse and present results in a readable summary.
- **No secrets in output** — Never echo environment variable values. Show names and metadata only.
- **Confirmation for destructive ops** — Production deploys, env removal, cache purge, and domain changes require an explicit "yes" from the user.

### 4. Verification

After execution, confirm the outcome:

- Re-read state (e.g., `vercel ls`, `vercel env ls`) to confirm the operation took effect.
- Compare before/after where possible (e.g., deployment count, env var count).
- Surface errors or warnings from command output.

### 5. Summary

Present a concise result block:

```
## Result
- **Action**: what was done
- **Status**: success | partial | failed
- **Details**: key output (URL, counts, config changes)
```

### 6. Next Steps

Suggest logical follow-ups:

- After deploy → check logs, inspect build, verify preview URL.
- After env change → pull to local, redeploy if production.
- After status → fix any flagged issues, run deploy if stale.

## File Naming

- Command files live in `commands/` and end in `.md`.
- Files prefixed with `_` (like this one) are meta-documents, not slash commands. They are excluded from `plugin.json` enumeration and not presented as user-invocable commands.

## Frontmatter

Every command file must include YAML frontmatter with at least a `description` field:

```yaml
---
description: One-line summary of what the command does.
---
```

## Validation

`scripts/validate.ts` enforces these conventions. Every non-underscore command file is checked for the required sections: Preflight, Plan, Commands, Verification, Summary, Next Steps.
