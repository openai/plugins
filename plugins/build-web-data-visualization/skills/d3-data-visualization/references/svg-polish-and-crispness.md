# SVG Polish and Crispness

## What Problem This Solves

This reference gives concrete defaults for professional SVG-based visualizations. Use it when charts look vaguely amateur because text, icons, strokes, axes, gridlines, outlines, or zoom behavior are out of proportion.

The goal is a calm, crisp figure where data marks are dominant, labels are readable, axes are quiet, and every stroke looks intentional at desktop, mobile, and export sizes.

## When to Use It

Use this for D3, hand-authored SVG, SVG overlays on Canvas or WebGL, exported vector figures, annotation-heavy editorial graphics, small multiples, maps, diagrams, and product dashboards where SVG owns axes, labels, legends, callouts, or icons.

## Key Takeaways

- Start from a visual token set before drawing marks. Do not let browser defaults, library defaults, or copied snippets define font sizes and stroke weights.
- Keep chart text in a narrow range. Most SVG labels should sit between 10 and 13 px; very few figure elements need to exceed 18 px inside the SVG.
- Keep non-data strokes quiet. Gridlines, borders, and axis domains should usually be 0.5 to 1 px and low contrast.
- Use `shape-rendering: crispEdges` for straight gridlines, axes, and rectangular bands; avoid it on curves, circles, symbols, and diagonal data paths where antialiasing should stay smooth.
- Use `vector-effect: non-scaling-stroke` for zoomed maps, diagrams, axes, annotation connectors, icons, and outlines when their perceived stroke width should remain screen-stable.
- Use fewer ticks and better formatting before shrinking text below 10 px or rotating labels.

## Baseline SVG Tokens

These defaults are conservative for a 600 to 900 px wide chart embedded in an article, report, dashboard, or app page:

| Element | Default | Range | Notes |
|---|---:|---:|---|
| Figure title outside SVG | 18 px | 16-24 px | Prefer HTML text unless export needs a single SVG. |
| Subtitle outside SVG | 13 px | 12-15 px | Put unit, denominator, and date here. |
| Axis tick labels | 11 px | 10-12 px | Use 10 px only for dense small multiples. Avoid going below 10 px. |
| Axis title or unit label | 11.5 px | 11-13 px | Slightly stronger than ticks, not larger than direct labels. |
| Direct labels | 12 px | 11-13.5 px | Usually 1 px larger or heavier than tick labels. |
| Annotation body | 12.5 px | 12-14 px | Use 1.25 to 1.35 line-height if rendered in HTML or foreignObject. |
| Annotation kicker/value | 13 px | 12-15 px | Use weight or color, not a huge size jump. |
| Source note | 10 px | 9.5-11 px | Keep readable in export; do not hide method caveats. |
| Gridline stroke | 0.75 px | 0.5-1 px | Low-contrast neutral; never visually outrank data marks. |
| Axis domain stroke | 0 or 1 px | 0-1 px | Remove when gridlines or labels already define the frame. |
| Tick mark stroke | 0.75 px | 0.5-1 px | Often unnecessary when gridlines are present. |
| Tick mark length | 4 px | 3-6 px | Keep short; use padding for separation. |
| Data line stroke | 1.75 px | 1.5-2.25 px | Focus line can be 2.5-3 px; comparisons should recede. |
| Area or band outline | 1 px | 0-1.25 px | Often better as fill plus boundary label. |
| Connector or leader line | 1 px | 0.75-1.25 px | Use direct, short connectors with enough whitespace. |
| In-chart glyph icon | 14 px | 12-16 px | Use with text or a legend; do not make icons carry meaning alone. |
| Annotation icon | 18 px | 16-20 px | Keep subordinate to the annotation text. |
| UI/control icon | 20 or 24 px | 20-24 px | Use 20 px for dense desktop, 24 px for normal controls. |

For compact dashboard cards and small multiples, reduce tick count and annotation density first. Use 10 px ticks, 11 px direct labels, 0.5 to 0.75 px gridlines, and 1 to 1.5 px data lines. Do not solve crowding by making everything tiny.

## Axis Defaults

D3 axes are intentionally plain; style them every time.

- Use 4 to 7 ticks on a normal desktop axis and 3 to 5 on mobile. Prefer approximately 4 to 6 y-axis ticks for quantitative charts.
- Start with `.tickSizeOuter(0)` so square axis ends do not read as extra ticks.
- Use `.tickPadding(6)` to `.tickPadding(8)` for normal charts. D3's default 3 px padding is often too tight for polished figures.
- Use separate gridline groups instead of asking one axis to do every job. Style gridlines at 0.5 to 0.75 px with low-contrast neutral color.
- Remove the domain path when a baseline, grid, or plot boundary already provides orientation.
- Align y-axis tick text with `text-anchor: end` on left axes and `text-anchor: start` on right axes. Keep x-axis ticks centered unless using long categorical labels.
- Do not rotate tick labels by default. If labels collide, reduce tick count, abbreviate, wrap category labels into two lines, widen the label lane, or switch to horizontal bars.
- Put units in the subtitle, a small axis title, or direct labels. Repeating units on every tick is usually visual noise.
- Use tabular numbers for ticks and aligned value labels when the typeface supports it.
- For band scales, center ticks on bands, add enough inner padding for labels, and avoid vertical category labels.

Example D3 axis baseline:

```ts
const tickCount = width < 480 ? 4 : 6;

const xAxis = d3
  .axisBottom(x)
  .ticks(tickCount)
  .tickSizeOuter(0)
  .tickPadding(width < 480 ? 6 : 7);

gx.call(xAxis)
  .call((g) => g.select(".domain").attr("stroke", "none"))
  .call((g) =>
    g
      .selectAll(".tick line")
      .attr("stroke", "#cbd5df")
      .attr("stroke-width", 0.75)
      .attr("shape-rendering", "crispEdges")
  )
  .call((g) =>
    g
      .selectAll(".tick text")
      .attr("font-size", 11)
      .attr("fill", "#5f6b7a")
      .attr("font-variant-numeric", "tabular-nums")
  );
```

## Typography Defaults

- Prefer one sans-serif family for SVG chart text unless the surrounding article or product style has a strong type system.
- Use no more than four text sizes in one figure: title, subtitle or annotations, labels or ticks, notes.
- Keep axis tick text smaller and quieter than direct data labels. If ticks are visually louder than the mark labels, the chart will feel backwards.
- Keep direct labels close to the mark they name and aligned to the reading direction: line ends, bar ends, map regions, or panel headers.
- Use sentence case for titles and annotations unless product style requires otherwise.
- Avoid all-caps labels except for very short panel tags. All-caps at small sizes becomes noisy.
- Use `paint-order: stroke fill` and a 2 to 3 px background-colored text stroke only when labels sit over marks or imagery. Prefer reserved label lanes when possible.
- Measure label bounding boxes or reserve label lanes for dense labels. Eyeballing text placement is where many SVG charts become sloppy.

## Stroke and Mark Defaults

- Data should have the strongest useful stroke. Context and structure should recede.
- Use neutral gridlines such as `#d7dee8` or an equivalent low-contrast token. On dark backgrounds, use low-opacity light gridlines rather than saturated color.
- Keep heavy outlines rare. A 3 px outline should mean selection, focus, or a primary path, not "default line."
- Use round line caps and joins for trend lines when they improve polish, but keep axes, gridlines, and rectangles square and crisp.
- Do not outline every filled mark. For bars, areas, and map regions, prefer clean fills, gaps, direct labels, or one quiet boundary.
- Keep symbol sizes related to text: dots of 3 to 4 px radius pair well with 11 to 12 px labels; 6 px radius dots already feel emphatic.
- Keep annotation leader lines short, light, and straight or gently elbowed. Avoid spaghetti connectors.

## Crisp Rendering Rules

- Use integer SVG dimensions and a stable `viewBox`. Let responsive layout scale the outer container, then recompute scales and labels from measured container width.
- For 1 px horizontal or vertical strokes on low-DPI displays, place lines on half pixels or use D3's axis offset behavior so the stroke lands cleanly.
- Use `shape-rendering: crispEdges` only on axis domains, tick lines, gridlines, rectangular heatmap cells, and other orthogonal geometry.
- Use `shape-rendering: geometricPrecision` or the default behavior for curves, circles, arcs, diagonal lines, and symbols.
- For transformed or zoomed layers, separate world geometry from screen-stable overlays. Data geometry may scale; labels, axes, icons, callouts, and selection outlines usually should not.
- Apply `vector-effect: non-scaling-stroke` to strokes that should preserve perceived thickness during zoom or non-uniform transforms.
- Avoid scaling a group that contains text. Recompute text positions at the new scale or place text in a separate overlay layer.
- Keep raster images and generated textures out of the label layer. SVG or HTML should own exact numbers, labels, notes, and source text.

## Icon and Glyph Defaults

- Treat icons as 100% scale assets with a known viewBox, usually 20 or 24 px. Do not stretch them to arbitrary widths and heights.
- Use 12 to 16 px icons inside chart marks, 16 to 20 px icons in annotations, and 20 or 24 px icons for controls.
- Pair icons with text or direct labels when they encode data status. Icons alone are fragile for accessibility and interpretation.
- Keep icon strokes visually consistent with nearby text and lines. At 16 px, 1.25 to 1.5 px icon strokes often read cleaner than 2 px. At 20 to 24 px, 1.75 to 2 px is usually acceptable.
- Apply `vector-effect: non-scaling-stroke` to icon strokes inside zoomable SVGs.
- Align icons optically with text baselines. Centering the viewBox is not always visually centered if the glyph has uneven weight.

## Responsive and Export Checks

Before calling an SVG visualization finished, check:

- 375 px, 768 px, and 1200 px wide containers.
- Browser zoom at 100% and 200%.
- Light and dark themes if supported.
- PNG export or screenshot at the target report, slide, or social size.
- Longest labels, largest values, empty states, and outliers.
- Whether any chart text drops below 10 px.
- Whether any non-data line is thicker than a data line.
- Whether labels, icons, and selection outlines stay usable during zoom or pan.
- Whether the chart still reads in grayscale.

## Common Mistakes

- Leaving D3's default 10 px font and 3 px tick padding in a chart that otherwise uses a polished product type scale.
- Making SVG title text 28 to 40 px inside a normal chart while ticks remain 10 px.
- Using 2 to 4 px gridlines, borders, map outlines, or node strokes by default.
- Scaling an entire SVG group during zoom so text and icons balloon.
- Applying `shape-rendering: crispEdges` globally and making curved marks look jagged.
- Shrinking axis text to 8 px instead of reducing ticks or changing layout.
- Rotating x-axis labels when a horizontal bar chart, fewer ticks, or wrapped labels would read better.
- Letting legends, icons, axes, and annotations all compete at the same visual weight.

## Adjacent Skills

- `../SKILL.md`
- `../../visualization-strategy-and-critique/SKILL.md`
- `../../accessibility-and-inclusive-visualization/SKILL.md`
- `../../testing-data-visualizations/SKILL.md`

## Source Links

- [D3 axis API](https://d3js.org/d3-axis)
- [MDN: SVG shape-rendering](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/shape-rendering)
- [MDN: SVG vector-effect](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/vector-effect)
- [W3C WAI: Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum)
- [Material Design: Icons](https://m1.material.io/style/icons.html)
