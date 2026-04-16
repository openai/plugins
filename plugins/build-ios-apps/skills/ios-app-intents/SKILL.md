---
name: ios-app-intents
description: Design and implement App Intents, app entities, and App Shortcuts for iOS apps so useful actions and content are available to Shortcuts, Siri, Spotlight, widgets, controls, and other intent-driven system surfaces. Use when exposing app actions outside the UI, adding `AppEntity` and `EntityQuery` types, shaping shortcut phrases and display representations, or routing intent execution back into the main app.
---

# iOS App Intents

## Overview
Expose the smallest useful action and entity surface to the system. Start with the verbs and objects people would actually want outside the app, then implement a narrow App Intents layer that can deep-link or hand off cleanly into the main app when needed.

Read these references as needed:

- `references/first-pass-checklist.md` for choosing the first intent and entity surface
- `references/example-patterns.md` for concrete example shapes to copy and adapt
- `references/code-templates.md` for generalized App Intents code templates
- `references/system-surfaces.md` for how to think about Shortcuts, Siri, Spotlight, widgets, and other system entry points

## Core workflow

### 1) Start with actions, not screens
- Identify the 1-3 highest-value actions that should work outside the app UI.
- Prefer verbs like compose, open, find, filter, continue, inspect, or start.
- Do not mirror the entire app navigation tree as intents.

### 2) Define a small entity surface
- Add `AppEntity` types only for the objects the system needs to understand or route.
- Keep the entity shape narrower than the app's persistence model.
- Add `EntityQuery` or other query types only where disambiguation or suggestions are genuinely useful.

### 3) Decide whether the action completes in place or opens the app
- Use non-opening intents for actions that can complete directly from the system surface.
- Use `openAppWhenRun` or open-style intents when the user should land in a specific in-app workflow.
- When the app must react inside the main scene, add one clear runtime handoff path instead of scattering ad hoc routing logic.
- If the action can work in both modes, consider shipping both an inline version and an open-app version rather than forcing one compromise.

### 4) Make the actions discoverable
- Add `AppShortcutsProvider` entries for the first set of high-value intents.
- Choose titles, phrases, and symbols that make sense in Shortcuts, Siri, and Spotlight.
- Keep shortcut phrases direct and task-oriented.
- Reuse the same action model for widgets and controls when a widget configuration or intent-driven control already needs the same parameters.

### 5) Validate the runtime handoff
- Build the app and confirm the intents target compiles cleanly.
- Verify the app opens or routes to the expected place when an intent runs.
- Summarize which actions are now exposed, which entities back them, and how the app handles invocation.

## Strong defaults

- Prefer a dedicated intents target or module for the system-facing layer.
- Keep intent types thin; business logic should stay in app services or domain models.
- Keep app entities small and display-friendly.
- Use `AppEnum` for fixed app choices such as tabs, modes, or visibility levels before reaching for a full entity type.
- Prefer one predictable app-intent routing surface in the main app scene or root router.
- Treat App Intents as system integration infrastructure, not only as a Shortcuts feature.

## Anti-patterns

- Exposing every screen or tab as its own intent without a real user value.
- Mirroring the entire model graph as `AppEntity` types.
- Hiding runtime handoff in global side effects with no clear app entry path.
- Adding App Shortcuts with vague phrases or generic titles.
- Treating the first App Intents pass as a broad taxonomy project instead of a small useful release.

## Notes

- Apple documentation to use as primary references:
  - `https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-and-widely-available`
  - `https://developer.apple.com/documentation/appintents/creating-your-first-app-intent`
  - `https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences`
- In addition to the links above, use web search to consult current Apple Developer documentation when App Intents APIs or platform behavior may have changed.
- A good first pass often includes one open-app intent, one action intent, one or two entity types, and a small `AppShortcutsProvider`.
- Good example families to cover are:
  - open a destination or editor in the app
  - perform a lightweight action inline without opening the app
  - choose from a fixed enum such as a tab or mode
  - resolve one or more entities through `EntityQuery`
  - power widget configuration or controls from the same entity surface
