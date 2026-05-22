# Shareable State and Persistence

## What Problem This Solves

Visualization work is often collaborative. People need to send a link to the exact view they mean, return to a configured analysis later, and recover context after refreshes without rebuilding the view by hand.

## When to Use It

Use this for interactive charts, dashboards, maps, diagrams, Gantt views, scrollytelling side controls, exploratory analysis tools, saved report builders, and any visualization where filters, selections, zoom, camera, metric choice, or drill-down materially changes the evidence being shown.

## Key Takeaways

- Treat the URL as the first persistence surface for meaningful, shareable visualization state whenever the state is stable, non-sensitive, and compact enough to encode.
- Encode selected dataset or saved-view id, metric, filters, time range, comparison group, sort, grouping, zoom, map bounds, camera target, selected entity, drill-down path, and active tab when those choices change the claim or evidence.
- Do not encode transient hover, pointer position, animation frame, drag-in-progress values, private notes, secrets, credentials, or large raw data payloads in the URL.
- Use canonical, minimal URL state: stable ids over labels, short keys over verbose payloads, omitted defaults, deterministic parameter order, and a schema/version key when the state contract may evolve.
- Validate and normalize incoming URL state before rendering. Unknown ids, stale schema versions, missing data, or invalid ranges should fall back visibly and preserve as much of the intended view as possible.
- Let incoming URL state override local persistence. A link someone sends should open the linked view, not the recipient's last private state.
- Use browser history intentionally: replace history entries while the user drags a slider or pans a map, and push a history entry when they commit a filter, selection, drill-down, or saved comparison.
- Use localStorage only for tiny, user-specific preferences such as collapsed panels, last-opened tabs, theme, recent view ids, or lightweight defaults.
- Use IndexedDB for larger structured state, cached data slices, offline drafts, custom annotations, long saved-view specs, or user-built workspaces that would make the URL fragile.
- Use remote storage when users need cross-device continuity, team sharing, named saved views, permissions, audit history, or links that reference a server-side snapshot.
- Put saved-view ids or slugs in the URL when the full state is remote or too large. The saved view should still resolve to an inspectable state object, not an opaque mystery.
- Provide an explicit copy-link or share action for important configured views. A user should not have to know which controls are URL-backed to share the result.
- Keep collapsible configuration, drill-down, and detail areas from crowding the evidence. Collapse secondary controls by default when the default visualization is understandable without them, but keep active filter chips, selected entities, and summary state visible.
- Make collapsed areas accessible: use real disclosure controls, preserve keyboard order, expose expanded state, keep focus predictable, and avoid hiding the only explanation of the current view.

## State Ownership Checklist

| State | URL | LocalStorage | IndexedDB | Remote |
| --- | --- | --- | --- | --- |
| Filter, time range, metric, sort, tab, selected entity | usually | optional default | rarely | when named or shared |
| Map bounds, zoom, camera target, drill-down path | usually | optional default | rarely | when saved as a view |
| Collapsed panel, sidebar width, personal theme | no | usually | rarely | only for account preferences |
| Long custom config, annotations, drafts, cached slices | saved-view id only | no | usually | when cross-device or shared |
| Private notes, secrets, credentials, raw sensitive data | no | no | only if appropriate and protected | only with explicit security model |

## Common Mistakes

- Building a beautiful exploratory visualization whose meaningful state disappears on refresh or cannot be linked.
- Persisting everything locally and making shared links open a different view on each person's machine.
- Encoding private or high-cardinality state into enormous, brittle URLs.
- Letting URL query parsing silently accept impossible ranges, missing entities, or stale schema versions.
- Updating browser history on every pointer move and making the Back button unusable.
- Hiding active filters or selected drill-down context inside a collapsed panel.
- Treating saved views as screenshots instead of state that can be inspected, updated, exported, and regenerated.

## Adjacent Skills

- `../../skills/react-and-nextjs-data-visualization/SKILL.md`
- `../../skills/typescript-data-visualization-engineering/SKILL.md`
- `../../skills/dashboards-and-real-time-visualization/SKILL.md`
- `../../skills/accessibility-and-inclusive-visualization/SKILL.md`
- `./interaction-models-and-progressive-disclosure.md`
- `./implementation-design-and-tradeoffs.md`

## Source Links

- [MDN: Working with the History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API)
- [MDN: URLSearchParams](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)
- [MDN: Window localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [MDN: IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [W3C WAI-ARIA Authoring Practices: Disclosure Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/)
