---
name: user-context
description: Initialize, inspect, save, update, forget, export, or explicitly reset the Public Equity Investing plugin's local user context, source setup, or optional automation setup. Use only when the user explicitly asks to manage Public Equity Investing saved preferences, source pointers, context storage, or recurring automation.
---

# Public Equity Investing User Context

This skill owns the Public Equity Investing plugin's local user-context storage foundation and explicit-only onboarding contract. It is intentionally narrow: it can initialize, inspect, save, update, forget, export, or explicitly reset local context, interpret the next onboarding action, guide the four-step intro/defaults -> connectors/plugins -> automation -> hero-workflow flow, and configure user-approved automations. Ordinary Public Equity Investing workflows do not invoke this skill by default; saved context and source setup are optional accelerators, not a pre-answer gate.

## State Files

Store Public Equity Investing state under:

```text
$CODEX_HOME/state/plugins/openai-monorepo/public-equity-investing/
```

The storage foundation owns only:

```text
user-context.md
onboarding-state.json
```

Do not create `category-state.json`.

## Initialize

When the user explicitly asks to initialize Public Equity Investing user context, run `python3 skills/user-context/scripts/init_user_context_state.py` with the shell working directory set to this plugin's root. Set the working directory before the first attempt; do not probe alternate relative paths.

The initializer creates missing state files from bundled templates and preserves existing files unless the user explicitly requests overwrite behavior.

## Inspect

When the user explicitly asks to inspect saved Public Equity Investing context, run `python3 skills/user-context/scripts/user_context_preflight.py` with the shell working directory set to this plugin's root. Set the working directory before the first attempt; do not probe alternate relative paths.

Use the returned read-only JSON envelope to summarize initialization status, onboarding status, the deterministic `next_action`, the lightweight `onboarding_progress`, and empty memory categories. Treat `user-context.md` as user-editable durable context and `onboarding-state.json` as operational scaffolding.

## Save Update Or Forget

When the user explicitly asks to remember, save, update, forget, export, or apply durable Public Equity Investing preferences or source pointers, follow `skills/user-context/references/plugin-memory.md` from the plugin root. Store reusable user-approved context in `user-context.md`; keep live company updates and operational connector state out. Initialize missing state only when a save needs persistence.

## Onboarding

When the user explicitly asks to set up, resume, defer, quiet, or complete Public Equity Investing onboarding, follow `skills/user-context/references/onboarding.md` from the plugin root. Use the inspection helper's `next_action` as the current step and render its `copy_ref` template substantially verbatim. Keep the visible flow to four steps: intro and lightweight defaults, connectors and plugins, one optional automation, then a three-option hero-workflow chooser. Capture broader durable preferences only when the user explicitly asks or supplies them naturally.

## Source Category Vocabulary

`skills/user-context/plugin-author-config/source-category-config.json` reserves static Public Equity Investing source category ids, labels, and preference hints for explicit setup/status work. The inspection helper exposes those categories as `source_category_plan` and echoes any setup-owned routes already saved under `onboarding-state.json` `connector_confirmation`. Ordinary workflow skills use the router's cross-skill runtime contract and `.app.json` categories instead of reading this helper first. Use `skills/user-context/references/source-category-runtime.md` from the plugin root for the source-setup boundary. Inspection does not prove source readiness, select routes, inspect connectors, or create `category-state.json`.

## Optional Automations

`skills/user-context/plugin-author-config/automation-config.md` defines the small author-owned automation menu. When the user explicitly asks for a recurring Public Equity Investing workflow or accepts the optional onboarding automation step, follow `skills/user-context/references/automation.md` from the plugin root. Do not create, update, pause, resume, or remove automations during ordinary workflow work.

## Reset

When the user explicitly asks to reset Public Equity Investing user context, run `python3 skills/user-context/scripts/reset_user_context_state.py` with the shell working directory set to this plugin's root. Set the working directory before the first attempt; do not probe alternate relative paths.

The reset helper moves active state files into a timestamped sibling backup directory before clearing them from the active state directory.

## Current Boundary

- The Public Equity Investing router and focused workflow skills do not run `scripts/user_context_preflight.py` during ordinary workflow work.
- Do not initialize state merely because another Public Equity Investing skill runs.
- Do not mutate state when running the read-only inspection helper.
- Do not inspect apps, connectors, plugins, `.app.json`, or source readiness during saved-context inspection.
- During user-approved explicit Source Setup, follow `skills/user-context/references/source-category-runtime.md` from the plugin root.
- During user-approved explicit automation setup or maintenance, follow `skills/user-context/references/automation.md` from the plugin root.
- Do not invoke onboarding unless the user explicitly asks for saved-context setup or management.
- Do not create or modify automations unless the user explicitly asks or accepts the optional automation setup step.
- Do not add, read, or migrate `category-state.json`. The reset helper may back up and clear an older copy during an explicit reset.
