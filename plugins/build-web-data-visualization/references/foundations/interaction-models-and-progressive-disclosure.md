# Interaction Models and Progressive Disclosure

## What Problem This Solves

This reference keeps analytical interaction purposeful so charts and dashboards stay understandable before the user starts hovering, clicking, filtering, or drilling down.

## When to Use It

Use this when choosing interaction patterns for charts, dashboards, or maps, especially when deciding what should be visible by default versus revealed on demand.

## Key Takeaways

- Start from the default state: the main comparison or status should be legible before any interaction.
- Use hover for preview, click or selection for commitment, and details on demand for secondary facts.
- Overview first, zoom and filter, then details on demand is a dependable default for exploratory analytical interfaces.
- Put controls near the views they affect and make reset or clear-selection paths obvious.
- Prefer a few high-value interactions over a pile of widgets that compete for attention.
- Make meaningful selections and changes URL-driven when they affect what evidence the user is seeing. Filters, time ranges, selected entities, comparison groups, zoom/map bounds, camera targets, tabs, and drill-down paths usually deserve deep-link support.
- Keep transient hover, pointer position, drag-in-progress, and animation frame out of the URL. Commit state on selection, release, step change, or explicit apply actions.
- Use copy-link, saved-view, and reset affordances for configured views that users are likely to share or revisit.
- Collapse secondary configuration, filter builders, inspectors, and drill-down panels by default when the main visualization can stand on its own. Keep active state summaries visible outside the collapsed panel.
- Use details-on-demand for secondary facts, not for the main conclusion, source caveat, selected value, or active filter context.
- On mobile, replace hover-only discovery with tap, focus, selection, direct labels, or step-through controls; keep the main visualization visible when settings open; and return to it after Apply, Cancel, Reset, or close.
- If an interaction captures drag, wheel, pinch, or map panning, define browser gesture ownership and provide alternate controls.
- Treat AR, camera, motion, vibration, notifications, and geolocation as permission-gated interaction modes with fallbacks, not as default controls.

## Common Mistakes

- Hiding essential values, labels, or categories only in tooltips.
- Requiring multiple filter or mode changes before the user can understand the screen.
- Adding zoom, cross-filtering, or drill-down just because the library supports it.
- Keeping important analysis state only in memory, making it disappear on refresh or impossible to share.
- Persisting a private last-used view in a way that overrides a URL someone intentionally opened.
- Hiding active filters or selected drill-down context inside closed configuration panels.
- Letting mobile controls, filter builders, or keyboard-open states hide the main evidence without a clear return path.
- Depending on hover, vibration, camera, AR, or motion as the only way to access evidence.

## Adjacent Skills

- `../../skills/visualization-strategy-and-critique/SKILL.md`
- `../../skills/dashboards-and-real-time-visualization/SKILL.md`
- `../../skills/geospatial-and-cartographic-visualization/SKILL.md`
- `../../skills/accessibility-and-inclusive-visualization/SKILL.md`
- `./shareable-state-and-persistence.md`
- `./mobile-first-responsive-visualization.md`

## Source Links

- [The Eyes Have It](https://drum.lib.umd.edu/items/95af2c8e-0d1e-48cc-a954-c9301d7bf618)
- [Visualization Analysis and Design](https://mitpressbookstore.mit.edu/book/9781466508910)
- [Perceptual Edge](https://www.perceptualedge.com/)
- [Datawrapper Academy](https://academy.datawrapper.de/)
