# E2E Dashboard and Export Strategies

## What Problem This Solves

This reference covers when visualization work truly needs end-to-end tests and how to keep those tests focused on user workflows instead of low-value repetition.

## When to Use It

Use this when the user needs dashboard QA, export verification, live-data testing, or cross-chart interaction coverage that spans routing, network behavior, and product state.

## Key Takeaways

- Reserve E2E tests for workflows: filters updating multiple views, drill-down, brush-and-link coordination, URL state, downloads, print or export flows, and refresh or stale-data handling.
- Use deterministic backend states, intercepted responses, or replayable event streams instead of live services whenever possible.
- Assert both what the user sees and the product contract behind it, such as URL params, request payloads, or emitted files.
- Include empty, slow, partial, stale, and failed states for operational dashboards, not just the healthy stream.
- Include mobile portrait and optional mobile landscape workflows for main-visualization visibility, settings return, touch/pinch behavior, keyboard-open states, spotty connections, and capability permission fallbacks when relevant.
- Prefer one golden path plus a few high-risk failure modes over a combinatorial matrix of mostly repeated interactions.

## Common Mistakes

- Turning E2E into the primary place where formatters, sort logic, and other cheap unit concerns are tested.
- Running dashboard tests against volatile live data and then normalizing the flakiness as unavoidable.
- Ignoring exports, downloads, and print views even though those are often release-critical deliverables.
- Treating mobile behavior as covered by a desktop screenshot.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`
- `../../reports-pdfs-and-slide-automation/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [Playwright downloads](https://playwright.dev/docs/downloads)
- [Playwright events](https://playwright.dev/docs/events)
