---
name: chunk
description: Use CircleCI Chunk for AI-assisted CI/CD work through either the Chunk web UI or the chunk-cli. Trigger this skill when users ask to set up Chunk, troubleshoot or fix failing builds with Chunk, configure Chunk environments, schedule/proactively run Chunk tasks, or use chunk-cli commands such as init, validate, build-prompt, auth, sandbox, task, and skill install.
---

# Chunk

## Overview

Use this skill to choose the best Chunk workflow (UI or CLI), then execute it with clear prechecks and safe defaults. Keep responses action-oriented and grounded in verified commands and setup requirements.

## Workflow

1. Classify the request path.
- Use UI path for org setup, model-provider onboarding, fix buttons, or environment selection in the CircleCI app.
- Use CLI path for terminal-based project setup, validation hooks, prompt/context generation, sandbox operations, or scripted task execution.
- Use mixed path when users want UI setup plus CLI execution in the same flow.
2. Gather minimum context.
- Confirm repository/project, branch, and whether GitHub integration is in place.
- Confirm whether the user is using CircleCI-managed model provider or bring-your-own keys.
- For CLI operations, confirm local OS compatibility and required tokens/auth.
3. Execute using the matching reference.
- For UI/setup flows, load [chunk-ui.md](references/chunk-ui.md).
- For CLI flows, load [chunk-cli.md](references/chunk-cli.md).
4. Close with verification.
- State what was configured or run, what remains blocked, and the next safest command or UI action.

## Guardrails

- Treat Chunk features as beta unless the user confirms otherwise.
- Never expose or log secret values (API keys, tokens, bearer credentials).
- Do not invent `chunk` subcommands or flags; stick to documented command families.
- If sandbox features are requested, call out private preview status and any access gate.
- If a task depends on org-level prerequisites (GitHub App install, org toggles, contexts), verify those first.

## Reference Map

- [chunk-ui.md](references/chunk-ui.md): CircleCI app setup, provider onboarding, fix buttons, environment file/setup, and operational troubleshooting.
- [chunk-cli.md](references/chunk-cli.md): Installation, command map, quick-start flows, auth/env variables, and platform constraints.

## Output Contract

Provide:

1. Path chosen (UI, CLI, or mixed) and why.
2. Steps executed with exact command/UI actions.
3. Required prerequisites not yet met.
4. Concrete next action to finish the user’s goal.
