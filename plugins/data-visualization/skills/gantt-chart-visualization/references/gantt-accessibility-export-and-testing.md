# Gantt Accessibility, Export, And Testing

## What Problem This Solves

This reference keeps Gantt charts usable, exportable, and testable despite their complex grid, timeline, and interaction behavior.

## When To Use It

Use this for Gantt accessibility review, PDF/image export, keyboard behavior, fixtures, visual regression, and release gates.

## Accessibility Defaults

- Provide a non-visual summary of the schedule: project date range, task count, milestones, overdue tasks, critical-path status, and major risks.
- Keep essential task name, start, finish, status, owner, and warnings available outside hover.
- Use table or grid semantics for the task grid where possible.
- Provide keyboard navigation for rows, columns, expand/collapse, selection, details, and timeline controls.
- Use focus states that align with both grid row and timeline bar.
- Do not rely on color alone for critical path, overdue status, progress, or dependency problems.
- Use shape, icons, line style, labels, and ordering as redundant encodings.
- Keep touch targets large enough for bars, handles, toggles, and dependency anchors when editing is enabled.
- Provide reduced-motion behavior for animated scroll, zoom, dependency highlighting, or auto-rescheduling transitions.
- Keep screen-reader fallbacks focused on schedule facts rather than trying to narrate every pixel.

## Keyboard Interaction

- Arrow keys move through task rows and grid cells.
- Enter or Space selects a task or opens details.
- Left and Right can collapse or expand hierarchy when focus is on a summary row.
- Timeline zoom and date range controls are reachable without pointer input.
- Drag alternatives must exist for date edits, such as date fields in the detail panel.
- Dependency editing should have a form alternative for predecessor, successor, type, and lag.
- Escape clears transient hover, drag preview, or selection mode.

## Export Requirements

- Define whether export means current viewport, selected tasks, selected date range, full project, or normalized data.
- PDF/image export should include title, date range, source, export timestamp, visible filters, timezone, caveats, and legend.
- Data export should include normalized fields, source IDs, provenance, and diagnostics where useful.
- Static exports need labels and values that do not depend on hover.
- For full schedules, paginate rows and time ranges rather than shrinking everything to unreadable scale.
- For stakeholder snapshots, use milestone or phase summaries when full detail would be counterproductive.
- For Canvas or WebGL layers, use deterministic dimensions, pixel ratio, fonts, and render-ready signals.

## Test Fixtures

Maintain small fixtures that cover:

- tiny valid schedule
- one milestone-only roadmap
- one dependency cycle
- one missing predecessor target
- one date-only timezone edge
- one invalid date range
- one parent rollup with children outside parent range
- one custom-field Jira or GitHub Projects mapping
- one dense 10,000-task schedule or generated equivalent
- one baseline comparison
- one resource overallocation case
- one static export snapshot

## Unit And Data Tests

- Parse dates with fixed locale and timezone assumptions.
- Validate start/end/duration consistency.
- Validate dependency types, lag, missing targets, and cycles.
- Validate hierarchy rollups and parent/child relationships.
- Validate milestone detection.
- Validate source adapter mappings and provenance fields.
- Validate confidence notes for inferred custom fields.
- Validate sorting, filtering, grouping, and visible-row derivation.

## Component And Interaction Tests

- Render empty, loading, error, unscheduled, dense, and filtered states.
- Verify task grid and timeline row alignment.
- Verify selection opens detail without hover.
- Verify keyboard navigation and focus states.
- Verify expand/collapse preserves selection and row alignment.
- Verify dependency and baseline toggles.
- Verify drag/resize preview, commit, validation failure, undo, and sync failure.
- Verify no source writes occur during pointer move.

## Visual Regression And E2E

- Capture stable screenshots for representative zoom levels and viewport sizes.
- Include high-contrast and reduced-motion states.
- Use visual baselines for selected task, highlighted dependency chain, critical path, baseline variance, and resource overload.
- Use E2E tests for import, field mapping, filter/search, edit commit, export, deep link, and source sync flows.
- For Canvas layers, include canvas-pixel sanity checks and data-contract tests rather than brittle DOM snapshots.

## Release Gates

- No known dependency cycles unless deliberately shown as errors.
- No unmapped date fields silently used as schedule truth.
- No essential values hidden only in hover.
- Keyboard can select a task and open details.
- Static export preserves task labels, date range, source, filters, timezone, and caveats.
- Dense fixture stays responsive within the product's target frame budget.
- Current-view and full-data exports are clearly distinguished.

## Common Mistakes

- Treating accessibility as impossible because the timeline is visual.
- Exporting a screenshot without filters, date range, or source context.
- Shrinking an entire 2,000-row schedule into one unreadable PDF page.
- Testing only the happy path with complete dates and no dependencies.
- Asserting exact generated SVG path strings instead of product-visible behavior.
- Forgetting date-only timezone fixtures until users see one-day shifts.

## Source Links

- [W3C WAI: Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)
- [W3C WCAG: Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions)
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/%40media/prefers-reduced-motion)
- [Highcharts accessibility module](https://www.highcharts.com/docs/accessibility/accessibility-module)
- [DHTMLX Gantt keyboard navigation](https://docs.dhtmlx.com/gantt/guides/keyboard-navigation/)
- [Bryntum accessibility guide](https://bryntum.com/products/gantt/docs-llm/guide/Gantt/advanced/a11y.md)
