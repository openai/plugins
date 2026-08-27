---
name: intake
description: Use when Creative Production is explicitly invoked or mentioned without a concrete request, when the user asks what Creative Production can do, or when the user wants help getting started without enough context to choose a workflow.
---

# Intake

Open the Creative Production app in its zero state.

This skill owns the no-brief entry point. It does not generate images, choose a production mode, or ask structured questions.

## Workflow

1. Call `creative_production_board` exactly once with:

```json
{
  "action": "open",
  "title": "Creative Production",
  "summary": "Start with an idea"
}
```

   Preserve the returned `boardId`; it is the only target for later actions.
2. Let the app show its starter grid.
3. Do not ask a chat question before the app appears.
4. Do not call any structured intake tool.
5. When the user selects a starter, let the app open an editable follow-up prompt. Opening the prompt must not create a placeholder.
6. After submission, hand off to `produce` with the existing `boardId`. Call `begin_generation` only when generation actually starts, then call `complete_generation` for each generated file. Never call `open` again for that workflow.

## Exit

Stop after the zero-state app is visible. The next user turn or starter follow-up owns the concrete creative request and updates this same board.
