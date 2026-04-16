---
name: circleci-cli
description: Operate and troubleshoot CircleCI using the CircleCI CLI. Use when users ask to authenticate CLI access, inspect pipeline/workflow/job status, validate configuration locally, rerun pipelines/jobs, trigger pipelines, or gather actionable diagnostics from CLI outputs.
---

# CircleCI CLI

## Overview

Use this skill when the fastest path is CircleCI CLI-driven operations rather than editing config first. Prioritize safe, read-first diagnostics, then run targeted mutating commands only after confirming scope.

## Inputs To Gather

- Repository path and target branch
- CircleCI project slug (if needed)
- Whether objective is inspect, rerun, trigger, or validate
- Required token/auth state and org permissions

## Workflow

1. Verify CLI and auth state.
   - Confirm `circleci` is installed and version is available.
   - Confirm token/auth before issuing remote CircleCI commands.
2. Run read-only diagnostics first.
   - Inspect available pipeline/project/trigger state and capture concrete identifiers.
   - Extract first failing scope and step details from supported command output before rerun/trigger actions.
3. Validate config locally when relevant.
   - Run config validation/processing commands before committing risky edits.
4. Run targeted mutation commands.
   - Rerun only required workflow/job scope.
   - Trigger pipelines with explicit parameters and branch context.
5. Report results and next action.
   - Provide exact command results, remaining blockers, and safest follow-up.

## Guardrails

- Prefer read-only commands before rerun/trigger/cancel operations.
- Confirm organization/project scope before mutating pipeline state.
- Never print raw secret values from environment variables or tokens.
- If permissions fail, report exact auth/scope gap and safest remediation.
- Respect installed CLI capabilities and avoid inventing commands.
- Do not use `circleci api`, `circleci workflow`, or other unavailable legacy commands unless `circleci help` confirms they exist.

## Installed CLI Compatibility

For newer `circleci` builds that expose domain subcommands (for example `pipeline`, `project`, `trigger`) but not `api`:

- Verify available commands first with `circleci help`.
- Use only discovered subcommands from help output.
- Prefer `circleci pipeline list|create|run` and `circleci trigger ...` for pipeline operations.
- For cloud job logs, use supported platform tools (CircleCI app/UI or connected CircleCI MCP tooling) if the CLI does not expose a logs command.

## Output Contract

Provide:

1. Commands run and purpose.
2. Key outputs (pipeline/workflow/job ids, status, failing step).
3. Actions taken (rerun/trigger/validate) and why.
4. Remaining blockers and next recommended CLI command.
