# System surfaces

Think in system entry points, not just in shortcuts.

## Shortcuts

- Good for direct actions and automation chains.
- Expose the actions that users would actually want to reuse.
- Add `AppShortcutsProvider` entries for the first high-value intents.

## Siri

- Good for clear verbs and deep-linkable actions.
- Phrase titles and parameters so the system can present and disambiguate them clearly.

## Spotlight

- Good for discoverability of both actions and entities.
- Use strong display representations and clear type names.

## Widgets, Live Activities, and controls

- Good when the same actions already make sense as intent-driven entry points.
- Reuse the same intent surface where practical instead of inventing separate action models.

## General guidance

- Design one small action layer that can serve several surfaces.
- Keep action names concrete and user-facing.
- Prefer structured entities and parameters over trying to encode everything in free-form text.
- Start narrow, ship a useful set, then expand based on real use.
