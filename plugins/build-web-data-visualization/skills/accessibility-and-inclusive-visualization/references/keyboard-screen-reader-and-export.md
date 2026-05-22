# Keyboard, Screen Reader, and Export Considerations

## What Problem This Solves

This reference covers the interactive and exported behaviors that often break accessibility.

## When to Use It

Use this when a chart has hover, tooltips, focus states, or must work in PDFs or image exports.

## Key Takeaways

- Essential information should not depend on pointer hover.
- Keyboard focus order and state visibility matter for chart controls and coordinated views.
- Export formats need their own accessibility strategy because interactivity disappears.
- Mobile touch, on-screen keyboard, and permission-gated capabilities need accessible alternatives and visible state summaries.
- Streaming or remote visualizations should expose live, stale, offline, partial, and reconnecting state to assistive technology.

## Common Mistakes

- Treating tooltips as the only way to reveal values.
- Assuming web accessibility automatically carries into PDFs or slides.
- Making camera, AR, vibration, motion, or notifications the only path to evidence or alerts.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [W3C Complex Images Tutorial](https://www.w3.org/WAI/tutorials/images/complex/)
