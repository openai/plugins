# Gantt Performance And Rendering

## What Problem This Solves

This reference helps choose a renderer and architecture for Gantt charts that remain responsive at realistic project sizes.

## When To Use It

Use this before implementing a Gantt surface with hundreds or thousands of tasks, many dependencies, editable interactions, repeated instances, or export requirements.

## Scale Questions

Ask these before picking a library or renderer:

- How many total tasks, visible rows, dependencies, resources, baselines, and labels?
- How wide is the visible time range and how many zoom levels are needed?
- Is the chart read-only, lightly interactive, or editable?
- How many Gantt instances can appear on one page?
- Are bars, links, labels, and grid cells all visible at once?
- Does the view need print, PDF, SVG, PNG, or spreadsheet export?
- Does the product need scheduling calculations or just rendering?
- How frequent are updates: static import, manual edits, live sync, or streaming portfolio changes?

## Renderer Choices

- DOM/HTML grid plus SVG timeline works well for small to moderate schedules where labels, accessibility, and export matter.
- Declarative chart libraries work for simple read-only timelines but often struggle with enterprise editing, hierarchy, and dependency semantics.
- Enterprise Gantt components are appropriate when scheduling rules, resources, import/export, baselines, and editing are core product requirements.
- Hybrid HTML grid plus Canvas bars/links is strong for large dense schedules because text stays semantic while dense marks are batched.
- SVG is good for annotation-rich, editorial, or export-heavy schedules with modest row counts.
- Canvas is good for thousands of visible bars, dense dependency links, frequent hover redraws, and virtualized row windows.
- WebGL is a last resort for extremely dense schedules or custom GPU picking. It usually adds more complexity than Gantt interfaces need.

## Virtualization

- Virtualize rows for large task lists.
- Keep a single scroll model synchronized across task grid and timeline.
- Use fixed or measured row heights and cache them.
- Render dependency links only for visible rows, selected chains, or current viewport.
- Do not mount all row controls, labels, and tooltips for offscreen tasks.
- Keep keyboard focus stable when rows are virtualized.

## Time-Window Culling

- Do not draw bars fully outside the visible time range.
- Clip long bars to the viewport but preserve visual cues that they continue.
- Render milestones only when they fall in or near the visible range.
- Recompute screen positions only when scale, range, row order, or data version changes.
- Cache tick labels and text measurements by zoom level and locale.

## Dependency Rendering

- Full dependency graphs can become unreadable and expensive.
- Default to muted links, selected-chain links, critical-path links, problem links, or links for visible rows only.
- Precompute link endpoints after row layout and scale computation.
- Rebuild link geometry only when dependencies, row order, collapse state, or time scale changes.
- Avoid curved or elaborate link paths for dense schedules unless they materially improve readability.

## Interaction Performance

- Throttle pointer-move hover work to `requestAnimationFrame`.
- During drag or resize, render a lightweight preview and validate expensive schedule effects on commit or debounced preview.
- Keep source-system writes out of the pointer loop.
- Separate layers: static grid, bars, dependency links, hover/selection, drag preview, and labels.
- Avoid measuring text, computing critical path, or recalculating rollups in render loops.
- Use immutable or versioned data structures so layers know what changed.

## Large Data Defaults

- Up to a few hundred visible tasks: DOM/SVG or enterprise component is usually fine.
- Thousands of total tasks with dozens to hundreds visible: row virtualization is mandatory.
- Thousands of visible bars or many link redraws: consider Canvas for bars and dependency layers.
- Tens of thousands of tasks: use server-side filtering/search, lazy hierarchy expansion, and summaries before drawing every task.
- Portfolio schedules: aggregate by phase, team, resource, or milestone first; let users drill into details.

## Export Performance

- Do not assume the interactive viewport is the export.
- For full-project PDF/image export, paginate by date range and row range.
- For SVG export, keep mark counts reasonable and avoid embedding huge hidden DOM.
- For Canvas export, provide deterministic pixel ratio, fonts, dimensions, and render-ready signals.
- For spreadsheet export, export normalized data and diagnostics, not just visible rows unless the user asks for current view.

## Common Mistakes

- Rendering every task and dependency as DOM nodes in a 10,000-task schedule.
- Redrawing labels, grid, links, and bars on every hover.
- Running critical-path calculation on pointer move.
- Ignoring backing-store memory for many Canvas layers and high device pixel ratios.
- Choosing a generic charting library for an editable scheduling product.
- Measuring text and dates during every animation frame.
- Treating a single demo schedule as proof the page-level instance count will hold.

## Source Links

- [MDN: Optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas)
- [MDN: OffscreenCanvas](https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas)
- [DHTMLX Gantt docs](https://docs.dhtmlx.com/gantt/)
- [Bryntum Gantt features](https://bryntum.com/products/gantt/features/)
- [Highcharts Gantt docs](https://www.highcharts.com/docs/gantt/getting-started-gantt)
- [Apache ECharts features and large-scale data](https://echarts.apache.org/feature.html)
