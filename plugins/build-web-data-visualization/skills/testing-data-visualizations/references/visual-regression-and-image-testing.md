# Visual Regression and Image Testing

## What Problem This Solves

This reference gives the skill a stable playbook for screenshot tests, image diffs, and other layout-sensitive verification paths for charts and dashboards.

## When to Use It

Use this when the regression risk is visual: overlap, clipping, label collision, annotation placement, color drift, missing marks, or layout changes that semantic assertions will miss.

## Key Takeaways

- Visual tests should target stable, intentional states rather than every possible interaction frame.
- Freeze viewport, container dimensions, theme, locale, timezone, fonts, and motion so the baseline reflects chart changes instead of environment noise.
- Capture desktop, mobile portrait, and mobile landscape baselines when the approved contract includes those states.
- Include keyboard-open, settings-open, stale/offline, and permission-denied states when they materially affect the mobile visualization.
- Capture the smallest useful region first, such as the chart component or one dashboard panel, before relying on full-page baselines.
- Pair image assertions with a few semantic assertions so failures are easier to diagnose.
- Mask, freeze, or replace volatile regions such as live timestamps, cursors, or rotating badges when those are not the feature under test.
- Review baseline updates like product artifacts; do not auto-accept them without understanding the diff.

## Common Mistakes

- Snapshotting the whole application when only one panel matters.
- Capturing while fonts, async labels, or transitions are still settling.
- Using screenshots for logic that could be proven faster and more clearly with a pure function test.
- Updating only the desktop baseline after a concept or layout change.

## Adjacent Skills

- `../SKILL.md`
- `../../react-and-nextjs-data-visualization/SKILL.md`
- `../../reports-pdfs-and-slide-automation/SKILL.md`
- `../../../references/foundations/mobile-first-responsive-visualization.md`

## Source Links

- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)
- [Pixelmatch](https://github.com/mapbox/pixelmatch)
