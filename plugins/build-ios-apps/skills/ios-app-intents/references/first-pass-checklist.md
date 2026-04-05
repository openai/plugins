# First-pass checklist

Use this checklist when deciding what to expose in the first App Intents release.

## Pick the first actions

Choose actions that are:

- useful without browsing the full app first
- easy to describe in one sentence
- valuable in Shortcuts, Siri, Spotlight, or widgets
- backed by existing app logic instead of requiring a major rewrite

Good first candidates:

- compose something
- open a destination or object
- find or filter a known object
- continue an existing workflow
- start a focused action

Avoid as a first pass:

- giant setup flows
- actions that only make sense after many in-app taps
- low-value screens exposed only because they exist

## Pick the first entities

Use app entities when the system needs to identify or display app objects.

Good first entities:

- account
- list
- filter
- destination
- draft
- media item

Keep each entity focused on:

- identifier
- display representation
- the few fields the system needs for routing or disambiguation

Do not mirror the entire persistence model if a much smaller system-facing type will do.

## Decide the handoff model

For each intent, ask:

- Can this finish directly from the system surface?
- Should this open the app to a specific place?
- If it opens the app, what is the single clean route back into the main scene?

Prefer one explicit routing or handoff service over many feature-specific side channels.
