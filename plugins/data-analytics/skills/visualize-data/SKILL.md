---
name: visualize-data
description: "Design, build, revise, or QA quantitative charts and figures. Use when an analytical answer needs visual judgment, whether for an inline answer, report, dashboard, notebook, or artifact."
---

## Related Skills

Use $metric-diagnostics when the visual needs an explanation of a metric movement.

Use $build-report when the visual is part of a durable analytical report.

# Data Visualization

Create quantitative visuals that are analytically sound, immediately readable, and polished enough to ship in a report, memo, slide, dashboard, notebook, widget, or HTML artifact. Treat charts as evidence for a takeaway. Redesign charts that are visually attractive but analytically weak, and revise charts that are technically correct but hard to interpret.

## Runtime Delivery Routing

Whenever `mode = work_mode` is positively identified, regardless of surface, do not render with Data Analytics MCP chart or table widgets, do not call `render_chart` or `render_table` for inline delivery, and do not select a visible MCP artifact as the visual surface. This branch applies only after another workflow has already selected inline delivery; it does not choose inline over a report, dashboard, HTML, notebook, or other surface. For an already-selected inline visual, prefer native Work Mode rendering and read [native-inline-visualizations.md](references/native-inline-visualizations.md) to choose and invoke `charts_widget_v2` or `app_block`. For one supported `bar`, `line`, `pie`, or `scatter` chart, treat `charts_widget_v2` as directly surfaced in this runtime and emit its live `genui` content reference before considering fallback; do not self-declare it unavailable or search for it. The complete outer shape is `genui{"charts_widget_v2":{"content":{...}}}`: replace `{...}` with the real chart spec and emit the reference without Markdown backticks. The inner chart spec alone is not a response; do not print bare JSON, plain HTML, or a code fence. Keep `app_block` conditional on the host surfacing it. When a durable report or dashboard workflow automatically selects `sites-app`, shape visuals with the MCP artifact chart contract so the validated runtime can be exported to Sites, but skip the visible MCP render. If the Visualize plugin is installed, also consult and follow its current visualization guidance for native chart or app-block authoring, while keeping this skill's delivery gate and fallback order authoritative. If an emitted native visual is rejected or fails to render, use a reproducible static/Matplotlib chart that fits a non-MCP surface; use a compact table only if no visual renderer can be delivered. Use static or Matplotlib charting for this native-render failure fallback or when the user explicitly asks for Python, a static image/file, notebook-oriented output, or export. A successful Data Analytics MCP tool result is not delivery confirmation in Work Mode, so do not say a visual was plotted or rendered above unless the selected native or non-MCP surface actually rendered. MCP servers and other callable tools remain valid data sources.

Whenever the selected report or dashboard delivery surface is HTML, define each visual as a native chart in the canonical `artifact.json` accepted by `validate_artifact`, backed by reviewed `snapshot.datasets` rows and canonical source metadata. The portable builder in `$build-report` uses the shared artifact-app chart renderer and produces the semantic no-script/print/conversion representation. This applies to ChatGPT Desktop explicit HTML, Work Mode fallback HTML on any surface, and HTML used for PDF, Google Docs, or Google Slides conversion.

Outside positively identified Work Mode, keep the existing surface selection rules unchanged.

## Chart Selection

Common surface forms should be named in the chart contract when the final surface is a report, dashboard, slide, notebook, widget, or HTML artifact.

| Data relationship | Best chart | Use it well |
|---|---|---|
| Trend over time or ordered axis | `line` | Show enough points to reveal shape; use `area` only when filled magnitude helps, and `sparkline` only in dense KPI cards |
| Composition over time | `stackedArea` | Use when parts should read as one total; switch to `line` when comparing component trajectories matters more |
| Comparison across categories | `bar` | Sort when order is not semantic; use horizontal bars for long labels; avoid redundant legends |
| Ranking or top-N | `leaderboard` | Keep it compact and single-measure; switch to ranked `bar` when comparison needs more chart context |
| Part-to-whole composition | stacked `bar` | Keep the denominator explicit; use `pie` only for a rough read with few slices |
| Distribution or spread | `histogram` | Use numeric bins that reveal shape; switch to `boxPlot` when comparing groups is the point |
| Distribution across groups | `boxPlot` | Use when median and spread matter more than full shape; switch to `histogram` when shape needs space |
| Relationship between two numeric variables | `scatter` | Use numeric x and y at a meaningful observation grain with enough distinct points to show a pattern; retain point labels, sample/volume fields, and one useful grouping candidate when safe |
| Dense two-dimensional pattern or cohort matrix | `heatmap` | Use for matrix shape or intensity; switch to `scatter` when point-level variation matters |
| Additive bridge from start to end | `waterfall` | Use only when drivers sum cleanly to the end value; otherwise use ranked `bar` |
| Ordered stage progression or drop-off | `funnel` | Use only for ordered single-series stages; prefer stage `bar` when funnel geometry distorts comparison |

## Workflow

1. Define the analytical question and one-sentence takeaway before choosing a chart. Identify the final surface, the intended comparison, and the context needed to make the visual honest.
2. Choose the simplest defensible family and variant from `Chart Selection`. Coordinate with `$build-dashboard` or `$build-report` when the visual belongs to those artifacts, and use `$validate-data` when the supporting analysis needs validation.
3. Write a compact chart contract before plot code, dashboard configuration, or renderer-specific implementation work. Include:
   - analytical question and takeaway
   - canonical family and concrete variant
   - data sufficiency for the chosen visual: expected row count, temporal point count for trend views, scatter observation count and grain, requested date range and grain, and fallback if the first query is too sparse
   - surface-native chart type, canonical artifact chart type, or explicit static renderer when a concrete renderer has been selected
   - delivery-specific constraints only after the delivery surface is chosen; for MCP widgets or app artifacts, use the shared MCP specification
   - palette policy, approved palette roots, and non-color distinction plan
   - output footprint, final container, export paths or delivery target, and the final QA surface
4. Select the delivery path that matches the final surface.
   - In positively identified Work Mode on any surface, only after the active workflow has already selected inline or chat-visible delivery, read `references/native-inline-visualizations.md` and prefer native Work Mode rendering; do not call `render_chart` or `render_table` for inline delivery. For one supported `bar`, `line`, `pie`, or `scatter` chart, emit the directly surfaced `charts_widget_v2` live content reference before fallback. If the durable artifact workflow automatically selected `sites-app`, reserve artifact charts for that hosted surface and skip visible MCP rendering. Use a reproducible static/Matplotlib chart only after the native reference is rejected or fails to render, or when no suitable native renderer exists for the requested chart family; use a compact table only if no visual renderer can be delivered, and do not describe a Data Analytics MCP tool result as rendered above. Use static or Matplotlib charting for this native-render failure fallback or for an explicit Python, static image/file, notebook, or export request.
   - Outside Work Mode, default to Data Analytics MCP chart widgets for ad hoc, inline, chat-visible, or otherwise unspecified chart requests. Treat "make/show/render this chart" as an MCP widget request unless the user explicitly asks for Python, a static image/file, notebook code, HTML, BI/dashboard editing, slides/docs export, or no rendered artifact.
   - Use the selected report, dashboard, BI, notebook, slide, or static HTML surface's native chart primitives only when the user explicitly selected that surface or the active report/dashboard workflow selected it before chart rendering.
   - Whenever the selected report or dashboard surface is HTML, use the canonical artifact chart, dataset, and source contract in `../../src/analytics-app-core.md`, then let `$build-report`'s portable builder create the final reader and semantic representation.
   - Outside the Work Mode native-render failure fallback, use static Python charting only when the user explicitly asks for Python, a standalone static image/file, or notebook-oriented output. Choose a reproducible local renderer, export the requested format, and inspect the output. Do not use that path as the default for HTML reports or dashboards.
- Use governed BI or dashboard-native widgets when that surface owns rendering; this skill should supply the visual spec and QA bar.
- Implement bespoke local HTML/CSS/SVG/canvas/JavaScript only for an explicitly selected non-report, non-dashboard output whose required interaction cannot be represented by the native artifact chart contract. Report, dashboard, and inline-chart HTML—including offline portable delivery—must use a canonical one-artifact report/dashboard plus `$build-report`'s packaged portable builder; never create a parallel HTML chart runtime.
5. Build in this order: format, structure, color, then QA. Choose the family, variant, and delivery surface first; decide labels, annotations, benchmarks, and retained information second; choose palette policy and explicit colors last.
6. Render or export the chart in its real context. For HTML reports and dashboards, inspect both the enhanced portable reader and the builder-generated semantic representation. For explicit standalone static output, save and inspect the image format the user requested.
7. Inspect the visual in the final report, slide, dashboard, notebook, widget, or HTML layout. Revise before delivery when the chart, labels, color system, or container fails final-context QA.
8. For shipped reports or dashboards with multiple visuals, maintain a compact chart map in notes or source material. Name the section, analytical question, selected family and chart type, fields, supported takeaway, palette policy, and delivery artifact, image path, or provenance source.

## Standards

### Selection Rules

Start from the analytical question and comparison the reader needs to make, not from a favorite chart type. Keep the top-level set small:

- `Tables & Scorecards`
- `Trend`
- `Comparison & Ranking`
- `Composition`
- `Distribution`
- `Relationship`
- `Uncertainty & Benchmark`
- `Matrix & Cohort`
- `Decomposition & Progression`

Concrete forms such as `highlighted multi-series line`, `Likert`, `pie`, `Pareto`, `waterfall`, `faceted dot & interval`, and `cohort heatmap` are variants inside these families, not peer families.

- Use charts for shape and comparison; use tables for exact lookup. If a table would show 3-8 comparable entities with one dominant numeric measure, prefer a bar, dot, lollipop, leaderboard, or other chart unless exact row lookup is the point.
- When reviewed evidence contains many comparable values, rows, categories, segments, or time points, default to rendering a simple chart on the selected delivery surface when that surface is available and safe. Skip rendering only when exact row lookup is the main task, the data is too sparse for an honest chart, the user asked for table/prose only, or the selected surface cannot support a useful visual.
- Do not choose `line` merely because the prompt says "trend" or "trending". Decide first whether the reader needs current status, movement, variance to plan, mix, concentration, drivers, progression, or distribution.
- Do not ship underpowered trend charts. For line, area, sparkline, indexed-trend, or other time-series views, first try to expose either a finer time grain or a longer date range so the displayed series has enough observed points to show shape. As a default, aim for at least 8-12 temporal points for a trend visual; if the available evidence has only a few anchor periods, query daily or weekly rows, extend the lookback, or add a meaningful segment/comparator before rendering. Use a KPI strip, grouped bar, slope chart, table, or narrative callout instead when the question is really a small set of discrete period comparisons.
- Do not ship underpowered scatter charts. A useful scatter needs enough comparable observations to reveal shape, clustering, outliers, or exceptions; as a default, aim for at least 12-20 meaningful points and treat fewer than 8 points as a likely table, bar, dot/lollipop, or narrative comparison unless each point is intentionally important and labeled. If the first result only has a few segment aggregates, make one targeted attempt to query a finer analytical grain such as account, workspace, user cohort, customer, model, endpoint, route, geography, or segment-by-period. Keep all plotted rows at the same grain, and do not mix totals, averages, and detail rows in one scatter.
- For scatter charts, choose x and y measures that can plausibly vary independently and share the same denominator, time window, population, and filters. Include the denominator, sample size, or volume metric used to judge reliability, and use a size encoding only when that third metric materially changes interpretation. Add a point-label field for small or executive-facing scatters, and retain a meaningful categorical field such as segment, plan, route, product line, model family, or region for optional color or filtering. Avoid coloring by a unique row id; use labels or the table for exact identity instead.
- Use horizontal bars for long labels and sorted bars when order has no semantic meaning.
- Use compact leaderboard-style ranked bars only for top-N previews with one numeric value and 3-8 visible rows. Default to 5-6 rows in compact dashboard cards. Use a paginated table for long-tail browsing or exact lookup, Pareto for cumulative concentration, and waterfall for additive start-to-end driver bridges.
- Do not use leaderboards to rank KPI definitions or time-window definitions against each other, such as latest DAU versus WAU versus MAU. Use KPI cards or a compact table for latest values; use trends, indexed trends, share trends, or ratio charts for movement or relationship questions.
- When a bar chart compares one measure across categories, use one categorical axis and one quantitative axis. Do not set a `color`, `series`, or grouped-bar encoding to the same category field just to color each bar; that creates a redundant legend and implies an extra grouping dimension. Use a palette/style option or direct labels if the surface supports per-category color without a legend; otherwise use a single mark color.
- When a bar chart compares same-unit movement across distinct KPI categories, such as latest week-over-week percent change by metric, categorical bar colors can help scanning, but they should be styling, not a visible grouping/legend, unless a second categorical dimension is present.
- When a bar chart compares unrelated business entities or components, such as products, model families, segments, or seat-support areas, do not encode every row with one fixed color when category identity matters. Prefer categorical styling and direct labels; reserve a single color for one measure repeated across a single semantic entity. Avoid adding a color legend when the axis labels already name the categories.
- For active-user dashboards, use KPI cards for latest DAU, WAU, MAU, Plus DAU, and Plus WAU values; trend or indexed-trend charts for movement over time; share or stickiness views when the question is mix or ratios; and categorical horizontal bars for unrelated week-over-week metric movements.
- Prefer variant escalation inside a family before inventing a new chart type: line to small multiples, bar to dot/lollipop, scatter to density, stacked bar to pie only when the circular read is explicitly useful.
- Keep pie, Pareto, waterfall, and Likert as variants, not defaults.
- Avoid bubble charts unless the third variable materially changes the interpretation.
- Include volume, denominator, sample size, or cohort context when omission could mislead.
- In multi-area executive reports, repeated line charts are a smell. Use line charts only where the main question is continuous movement over time. Consider dot/lollipop or bar with reference for plan variance, stacked area or 100% stacked bar for mix, ranked bars or leaderboards for category comparisons, waterfall for additive drivers, heatmaps for cohort or matrix structure, and stage bars for ordered progression.
- For one-slide-per-area executive reports, do a chart-family pass before writing the visual plan. Audit repeated families and require a rationale when multiple sections use the same family despite asking different questions.
- If every visual in a report uses the same family, document the reason in the chart map and verify that no section is actually asking for status, mix, variance, or drivers.
- Four or more all-line visuals fail the multi-chart report contract unless the report is redesigned with data-compatible alternatives or fewer visuals.

### Surface And Implementation

- For data visualization requests outside Work Mode where the user has not chosen a file, notebook, BI/dashboard, report, slide, docs, HTML, or no-render output surface, render with Data Analytics MCP chart widgets by default when the MCP widget tools are available. In Work Mode on any surface, only after inline delivery has already been selected, read `references/native-inline-visualizations.md` and prefer native Work Mode rendering; for one supported `bar`, `line`, `pie`, or `scatter` chart, emit the directly surfaced `charts_widget_v2` live content reference before fallback. Use a reproducible static/Matplotlib chart before a compact table fallback only after that emitted reference is rejected or fails to render, or when no suitable native renderer exists for the requested chart family. Do not call `render_chart` or `render_table` for Work Mode delivery, do not treat an `ok:true` Data Analytics MCP tool result as proof that the visual rendered, and use static or Matplotlib charting only for that native-render failure fallback or when the user explicitly asks for Python, a static image/file, notebook-oriented output, or export. When the user explicitly chooses another surface, keep this skill's output to chart selection, data planning, implementation guidance, and QA for that surface.
- When the selected delivery surface is an MCP Apps widget or Data Analytics MCP report/dashboard artifact, read `../../src/analytics-app-core.md` after selecting the chart family. Do not let an MCP-supported type list drive general chart selection for non-MCP surfaces.
- When rendering an MCP inline chart from reviewed query results, call `render_chart` with source metadata, an exploration-ready table, chart encodings, and display settings. Do not create an intermediate Python chart image for the same result unless the user explicitly asked for Python/static output or the widget renderer is unavailable.
- Any table that powers a chart must be richer than the minimum fields needed to draw that chart. Do not ship source-data tables containing only `x`, `y`, and optional series/color fields when the reviewed result can safely include contextual dimensions, numerator/denominator fields, date or cohort fields, ranks, benchmarks, comparison-period values, or adjacent measures. If privacy, query cost, source limits, or metric definitions prevent a richer table, state that limitation in the chart/report notes.
- Before rendering or exporting, inspect the reviewed result table for information density. If the chart would render fewer than 8 temporal points, fewer than 4 meaningful categories, fewer than 8 scatter observations, or a nearly straight two/three-point path, make one targeted attempt to improve the supporting data by querying a finer grain, extending the time range, or adding a relevant breakdown that supports the same claim. If that is blocked by source limits, query cost, privacy, or metric definition, record the limitation and switch to a more honest form such as KPI cards, grouped bars for discrete periods, a table, or prose with exact values.
- Include more than one meaningful quantitative field when the user may reasonably compare measures, swap axes, inspect target versus actual, or choose a relationship view. Do not fabricate auxiliary measures or ship raw detail rows merely to make extra chart types appear possible.
- Shape chart-ready data for realistic alternatives, not arbitrary ones. A trend chart should usually retain its temporal field, value field, and meaningful segment/comparator fields; a category comparison should retain the category, value, useful grouping candidates, and rank/sort context; composition charts should retain the denominator or share context when available. A scatter chart should retain a stable point identity or label, numeric x and y measures, any denominator or sample-size fields, a useful volume/size candidate, and one or two interpretable grouping or filter fields. Do not promote a retained grouping candidate into a color/series encoding unless it adds information not already carried by the axis, facet, or table labels.
- Treat custom local visual implementations as report-complete only after they match the selected delivery mode and pass final-context QA.
- Use the selected surface's native chart block when one is available. Do not add an extra decorative outline shell around charts.
- For every HTML report or dashboard, use the canonical artifact contract and packaged portable builder. Do not install a second chart runtime, hand-code a parallel HTML chart, or rely on remote scripts.
- For explicit standalone static/Python output, use a reproducible local renderer and inspect the exported result. Do not let a static-image path replace the portable artifact default for HTML reports and dashboards.
- Assume local environments can be minimal or offline. Do not assume network installs will succeed.

### Visual Design

- Default every chart title to a neutral, descriptive label that identifies what is plotted, such as the metric, comparison, dimension, or time scope. Do not infer a narrative takeaway, claim, clever headline, or new jargon for the title. Use a takeaway-led title only when the user explicitly requests one; otherwise put supported interpretation in the subtitle or adjacent narrative text.
- Put metric details, units, denominator, date range, cohort, filters, sample size, or volume in the subtitle when needed. Notes can add caveats, but do not replace the subtitle.
- Use a single font family across charts and surrounding output when possible. Prefer white or near-white backgrounds, quiet grey grid lines, deep charcoal text, and restrained approved palette roots centered on blue, gold, orange, olive, and pink.
- Do not rely on color alone. Use tone, open fill, marker fill, line style, direct labels, ordering, or faceting when series or states need separation.
- Only set color or series encodings for meaningful grouping dimensions such as `segment`, `product_line`, or `series` when they are not already the sole axis category. Omit color for single-series charts and do not manufacture or duplicate a grouping field just to produce a legend.
- Choose one palette policy before plotting:
  - `single-root preferred`: one non-neutral root plus shades, open fills, and neutral references for simple trends, ranks, distributions, relationships, matrices, and repeated panels.
  - `hard two-root cap`: at most two non-neutral roots plus neutrals for binary, signed, focal-vs-context, benchmark, comparator, waterfall, Pareto, diverging, highlighted trend, and ordered line-dot charts.
  - `relaxed multi-category`: up to five approved roots when category identity is the point, such as pie, stacked bars, stacked area, grouped bars, and stage bars. If more are needed, group to top-N plus Other or change forms.
- Use each selected root's `base` tone as the default non-neutral mark color. Reserve `mid` for deliberate higher-contrast exceptions, use `dark` for keylines, outlines, labels, or reference strokes, and use `light`, `xlight`, or `open` for supporting fills.
- Generate explicit palette maps from declared colors. Do not let plotting library categorical defaults choose shipped chart colors.
- For signed values, avoid green/red by default. Use dark versus open/light fills, direct signed labels, and clear zero-line context unless documented domain semantics require an exception.
- For waterfall charts, use matched neutral start and end anchors plus exactly two non-neutral delta colors: one positive and one negative. Do not introduce extra hues or darker/lighter non-neutral keylines for individual drivers.
- For waterfall, bridge, variance, and other delta-focused charts where the takeaway is movement against a large base, do not force the value axis to zero when zero would materially compress the intended movement. Use a focused value-axis domain around the cumulative path or delta range with padding; preserve honesty with exact start/end/change labels, visible units, and an explicit focused-scale cue in the subtitle, caption, or axis when needed. Keep zero in view when values cross zero or the question is absolute magnitude.
- Keep one stroke-width system for marks, keylines, guides, and reference lines. Use dark-neutral styling for benchmark, calibration, or ideal lines.
- Keep left and bottom axis anchors visible when labels depend on them. Remove ticks, guides, or connectors that do not improve the intended comparison.
- Prefer direct labels when they reduce legend lookups; use a compact top legend when direct labels create clutter.
- Reserve explicit left and right space for horizontal or diverging bars with long labels or negative values. Do not shrink typography to force a narrow card.
- Do not use gradients inside chart marks, arbitrary colored chart backgrounds, inconsistent or ad hoc corner radii, or thickness as an emphasis channel.
- For HTML artifacts, use the same native artifact chart footprints and layout options as the MCP app: `8 columns` by default, `6` minimum, `10` or `12` for complex charts, stacked vertically on mobile. Align multi-chart rows from the left/start edge.
- Let the portable reader apply the shared Data Viz System tokens to chart containers, legends, KPI strips, and notes. Express intentional palette choices in the artifact chart spec instead of creating HTML-only CSS variables.
- Use dark chart variants only when the containing artifact is dark. Inspect both light and dark variants for shipped branded web outputs.
- For research charts, lock the blossom to the header's top-right corner. Omit it for third-party, partnership, and non-research charts.

### Quality Bar

- Chart choice should follow `Chart Selection`.
- Choose and honor an explicit delivery surface. Use MCP widgets only when that surface is available, safe, useful, and not contrary to the user's requested output mode.
- Keep chart contracts, omitted-chart explanations, validator notes, and QA rationale out of visible executive report bodies unless the user asks for methodology or the detail changes the reader-facing takeaway.
- Explicit standalone static/Python plotting code should be reproducible and visibly adapted to the requested chart contract. Generic ad hoc snippets are acceptable only for exploratory charts.
- The form must match the analytical comparison, and scales must stay honest and consistent across comparable charts.
- Standard bar charts that compare absolute magnitude should start at zero. Delta-focused waterfalls, bridges, variance bars, and small-multiple movement charts may use non-zero or narrowed domains only when the zero baseline would materially hide the intended change and the chart carries exact labels plus a clear scale cue.
- Data grain, filters, date range, denominator, and units must match the claim the chart supports.
- Every shipped chart must have a visible title appropriate to its surface and a subtitle that carries needed units, time/cohort context, denominator, sample size, or volume.
- Labels, ticks, titles, legends, callouts, benchmark labels, and annotations must not collide, clip, or detach from the evidence in the exported chart or final container.
- Long labels, negative values, outside-end labels, zero-line context, and direct value labels need explicit layout space.
- Multi-series filled marks need distinct tones, open fills, keylines, marker fills, line styles, direct labels, or faceting. Visually identical adjacent or overlapping fills fail QA.
- Line styles, marker fills, open fills, keylines, ordering, faceting, and direct labels should remain legible in grayscale when they carry distinction.
- Positive and negative states should use tone, open fill, zero-line context, and signed labels rather than default green/red semantics unless the exception is documented.
- Exported SVG or HTML colors should match declared palette roots plus neutrals; remove unused multi-hue tokens unless documenting an intentional exception.
- Chart scaffolding should stay quiet: no arbitrary colored backgrounds, gradients, decorative guides, inconsistent stroke widths, or decorative mark fills. Filled marks should keep keylines, and benchmark, calibration, and reference lines should use dark-neutral styling.
- Titles, legends, and primary labels should use dark ink and share a clear header anchor. Numeric ticks and direct value labels should use mono styling where the template system calls for it.
- Research charts should use the locked top-right blossom placement; third-party, partnership, and non-research charts should omit it.
- Before handoff, inspect the visual in the artifact readers will open and verify that it answers the stated analytical question, signs and scales are honest, labels fit at laptop and mobile widths, the color and non-color encoding is understandable, and the caption states metric, time window, and source when those are part of the visual.
- Inspect the final report, slide, dashboard, notebook, widget, or HTML layout before handoff. Revise before delivery when any requirement above fails.
