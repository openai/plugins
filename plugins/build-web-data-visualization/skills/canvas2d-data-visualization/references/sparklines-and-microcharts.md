# Sparklines and Microcharts

## What Problem This Solves

This reference covers sparkline-style Canvas visualizations: tiny, repeated, context-dependent graphics used inside tables, lists, KPI grids, headlines, and dense monitoring surfaces.

## When to Use It

Use this when the user asks for sparklines, inline trend charts, tiny multiples, row-level trend indicators, dense KPI grids, or many repeated charts on the same page.

## Key Takeaways

- A sparkline is a small, high-resolution, word-like graphic embedded near the text or number it explains.
- Sparklines are useful when shape, direction, rhythm, or recent change matters more than precise reading from axes.
- Canvas is often the right renderer when a table or dashboard needs dozens, hundreds, or thousands of tiny charts.
- The surrounding row, column, label, inline value, or card supplies context; the sparkline should not carry the whole explanation alone.
- Consistent scale decisions matter more than decorative detail.

## What Sparklines Are For

Use sparklines to show compact temporal or ordered patterns:

- recent trend beside a current metric
- volatility, seasonality, or rhythm in a table row
- before/after movement across many entities
- distribution or range context in a KPI card
- small-multiple comparison when each chart is intentionally tiny

They work best when the user can scan many entities and decide where to inspect next. They are not a replacement for a full chart when the task is precise measurement, annotation-heavy explanation, or detailed comparison across multiple series.

## Design Guidance

- Place the sparkline next to the label or value it contextualizes.
- Keep marks minimal: one thin line, area, bar strip, dot strip, or range band.
- Consider marking the latest value, high/low, threshold crossing, or anomalous point when it helps scanning.
- Use shared scales within a comparable group when relative magnitude matters.
- Use per-row scales only when shape is the task; make that choice explicit because it hides magnitude differences.
- Avoid detached legends. Use nearby headers, row labels, inline values, or compact annotations.
- Keep color semantically sparse: neutral trend plus one accent for current, alert, target, or selected state.
- Do not overload a sparkline with multiple unrelated series.
- Provide a path to detail-on-demand: hover, focus, click, expanded row, side panel, or full chart.

## Canvas Implementation Patterns

For small counts, one Canvas per card or table cell can be acceptable. For large tables, prefer:

- one shared Canvas positioned behind or inside the visible table viewport
- virtualization so only visible rows are drawn
- a pooled set of Canvas elements reused by rows
- pre-rendered sparkline bitmaps for static rows
- HTML text for labels and values, Canvas only for the trace

Use CSS-pixel coordinates for each row rectangle and set the Canvas backing store with `devicePixelRatio`. A shared Canvas can draw each row's sparkline at `x`, `y`, `width`, and `height` from the table layout model.

## Interaction Patterns

- Hover: highlight the nearest sample or the whole row; show exact values in an HTML tooltip.
- Click: select the row or open a full-size detail chart.
- Keyboard: keep row focus and selection in HTML; mirror the focused row in the Canvas highlight layer.
- Drag: use only when the sparkline supports an explicit range brush, threshold handle, or inline editing task.
- Tooltip positioning: anchor from the same row rectangle and scale used by Canvas, not from duplicated layout math.
- Accessibility: expose the row label, current value, trend summary, and selected or alert state in surrounding HTML.

Do not make every pixel of every tiny chart independently interactive unless the task truly requires it. Dense microcharts usually need row-level or nearest-sample interaction, not full chart-tool behavior in every cell.

## Data and Scaling Choices

- Downsample long series to the available pixel width before drawing.
- Preserve extrema when downsampling so spikes do not disappear.
- Use consistent missing-data treatment: gaps, muted segments, or explicit markers.
- Clamp or annotate extreme outliers if they flatten the useful variation for every other row.
- Use domain padding deliberately; tiny charts can exaggerate noise when the domain hugs the min and max.
- Cache scaled coordinates while the table width, domain, and data version are stable.

## Common Mistakes

- Using sparklines without nearby text or values, forcing users to guess what the tiny shape means.
- Scaling each row independently when the user needs magnitude comparison.
- Using a global scale when the user only needs within-row shape, making most rows look flat.
- Rendering hundreds of independent Canvas elements without calculating backing-store memory.
- Redrawing every sparkline on every hover when a shared highlight layer would suffice.
- Adding axes, legends, labels, or decorations until the sparkline stops being a microchart.
- Treating the tiny graphic as the only accessible representation of the trend.

## Adjacent Skills

- `../SKILL.md`
- `../../dashboards-and-real-time-visualization/SKILL.md`
- `../../visualization-strategy-and-critique/SKILL.md`

## Source Links

- [Edward Tufte: Sparkline theory and practice](https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/)
- [MDN: Optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas)
