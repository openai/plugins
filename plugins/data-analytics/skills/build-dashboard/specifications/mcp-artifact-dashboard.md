# MCP Artifact Dashboard Specification

Use this when the dashboard should be rendered by the Data Analytics MCP app in ChatGPT Desktop using `render_artifact`, or when `sites-app` should package the same bounded, reviewed dashboard runtime for Sites.

When `mode = work_mode` is positively identified on any surface, select this specification automatically for a durable dashboard when the full Sites create, checkpoint, and deployment lifecycle is callable. Build and validate the full artifact, skip visible `render_artifact`, and publish the exported runtime through Sites. Use the HTML dashboard specification automatically, or an explicitly selected BI destination, when that lifecycle is unavailable, publishing fails, or the user explicitly declines Sites.

## When To Use

- The user wants a ChatGPT Desktop dashboard, quick analytical artifact, prototype, or source-backed dashboard readout without creating a Tableau, Databricks, Looker, Power BI, or other BI-platform asset.
- The dashboard can be represented as a manifest plus bounded snapshot, with compact reviewed datasets. Customer, account, company, segment, and product names are valid analytical dimensions when they are relevant.
- The primary value is reader handoff and exploration inside ChatGPT Desktop, not long-lived BI governance, platform permissions, or scheduled platform refresh.

Prefer a BI platform dashboard for broadly shared production dashboards, third-party platform edits, managed refresh, or platform-specific publishing. Use Streamlit only when the user explicitly asks for Streamlit or an existing Streamlit app must be changed.

## Build Shape

- Build a dashboard manifest with `version: 1`, `surface: "dashboard"`, a reader-facing `title`, and top-level `blocks`. `cards`, `charts`, and `tables` define reusable renderable assets; `blocks` establish the dashboard reading and layout order. Do not emit a shorthand dashboard that declares cards/charts/tables without blocks.
- Read `../../../src/analytics-app-core.md` for shared MCP payload safety, source provenance, manifest/snapshot, rendering, and chart encoding rules. In particular, do not bind color, series, grouped, or stacked behavior to the same category already used for an axis just to color bars.
- Follow the current `render_artifact` and `validate_artifact` MCP chart schema instead of duplicating chart-field rules here. Validate the manifest before rendering.
- Validate the complete manifest and snapshot first with `validate_artifact` and fix validator errors there. For a ChatGPT Desktop MCP app outside Work Mode, make only one visible `render_artifact` call after validation succeeds. For `sites-app` in Work Mode, never call `render_artifact`; call `export_artifact_package` after validation and continue through the current Sites hosting workflow.
- Default to built-in artifact blocks for dashboards: `metric-strip`, `chart`, `table`, and `markdown`. Use these native blocks for ordinary KPI strips, trends, bars, rankings, tables, caveats, source notes, and dashboard structure even when custom HTML would be faster to hand-author.
- Every card referenced by a `metric-strip` must attach canonical provenance through inline `source` or `sourceId`, just like native charts and tables, so its data-source action always opens a complete query and evidence view.
- Pair it with a compact bounded snapshot containing reviewed aggregate datasets. Avoid row-level payloads unless a small detail table is essential. Use the canonical snapshot shape: `snapshot.datasets` is an object keyed by dataset id, and each value is a plain array of reviewed row objects. Do not put `{columns, rows}` table objects inside `snapshot.datasets`; keep column metadata in `manifest.tables[].columns`.
- If a required source is blocked by permissions, set the snapshot status to `partial` or `blocked`, populate `snapshot.accessIssues`, put a clean access notice above the dashboard header, and state the exact missing role/table. Do not bury the blocker inside a chart card.
- Keep the shared hierarchy: hero metrics first, then trend, then diagnosis, then detail.
- Render the editable dashboard title from `manifest.title`, the last-refresh date, and a Refresh action in the top bar. Treat the top-bar title as canonical.
- Keep snapshot freshness quiet in the top bar. Render a compact status pill only when the snapshot is fixture, partial, or blocked.
- KPI cards render as individual cards from one `metrics[]` list. The first metric is the card's only headline and renders as the large value. Later metrics may render as concise badges only when they compare that same headline with its prior period, target, or delta. Each metric declares `label`, `field`, optional `format`, and `signed: true` for signed changes.
- Choose all and only decision-relevant hero metrics. Do not pad or truncate a strip to reach four cards—or any preferred count. Each card must answer one distinct monitoring or decision question; use supporting badges only for direct comparison context, and split independent secondary metrics into their own cards, charts, narrative, semantic strips, or a detail table. Keep card labels and badge labels concise enough to remain on one line. Odd card counts are valid; the renderer balances rows responsively.
- When a metric label is not self-defining, include a card description or nearby markdown that explains the metric in reader terms, and include the exact calculation in `source.query.metric_definitions`.
- Back every chart with a dataset that remains useful beyond the visible chart encoding when safe reviewed context is available. Retain useful dimensions, time/cohort fields, candidate grouping columns, numerators, denominators, benchmarks, ranks, comparison-period values, and adjacent measures so the expanded table supports inspection, filtering, and realistic chart switching.
- Percent values rendered with `format: "percent"` or `valueFormat: "percent"` must use the same numeric scale consistently in the provided data. Use decimal rates for computed numeric fields, such as `0.149` for `14.9%`, or pass preformatted reader-facing strings where exact display text matters.
- Use the shared analytics app Recharts v3 chart system for generated app chart types, and keep card width/order persistence, source dialogs, copy actions, table sorting, pagination, and responsive drag behavior aligned with the shared artifact app and validator instead of reimplementing local variants.
- Generate manifest and snapshot data first. Do not generate bespoke React unless a requested visualization cannot fit the contract.
- Use `type: "html"` blocks only when the user requests customization, interaction, or a bespoke visual treatment that is not possible with the built-in artifact blocks. Before choosing HTML, verify that native cards, charts, tables, markdown, filters, chart options, or table formatting cannot satisfy the request. Put the raw markup in `html`; HTML blocks auto-size to their content in the MCP artifact renderer.
- Outside Work Mode, use `render_artifact` as the default ChatGPT Desktop reader handoff when the payload is safe and within bounds. In Work Mode, skip `render_artifact`; for `sites-app`, publish the exported package through the current Sites hosting workflow.
- If the payload is unsafe, too large, or the MCP artifact tool is unavailable after exact discovery, record the blocker and choose another delivery surface.

## App Visual System

- Use the Data Analytics artifact app's design system, chart renderer, and interaction model.
- Chart and table panels use the shared two-column grid above the stack breakpoint and full-width cards below it.
- Tables default to dense full-width lookup surfaces, avoid nested inset containers, allow horizontal overflow for wide rows, and paginate bounded detail data instead of vertically scrolling the table body.
- Movement columns should be explicitly marked with `movement: true`, `semantic: "movement"`, or `role: "movement"`; render signed positive values with `+` and color only movement cells, not neutral current values or shares.
- Keep generated app styles theme-aware: component styles should consume `--ds-*` aliases, and those aliases should resolve to Figma-backed PUIK/design-system semantic variables such as `--color-surface`, `--color-text-primary`, and `--color-border` before falling back to standalone values.
- For the outer page canvas and top bar, prefer Codex artifact window surface tokens `--color-token-main-surface-primary` / `--color-background-surface`; dark mode should fall back to Codex `#181818` while cards and charts continue using Figma surface tokens.

## App Controls And Interaction

- Render filters, chart overflow menus, table overflow menus, and the top-bar Share menu with the shared dashboard menu surface.
- Menu surfaces and item states should use Codex dropdown/list palette aliases: `--ds-menu-bg`, `--ds-menu-text`, `--ds-menu-border`, and `--ds-menu-hover-bg`, not card surface tokens.
- For menus, prefer Codex dropdown tokens `--color-token-dropdown-background`, `--color-token-dropdown-foreground`, `--color-token-dropdown-border`, and `--color-token-list-hover-background` so hover/open states match Codex chrome.
- Menus should support smooth open/close motion, click-outside dismissal, Escape dismissal, and keyboard-friendly navigation.
- Filter controls should hug their label/value content and avoid native OS select styling. Show filters only when they materially control the visible dashboard surfaces.
- Chart and table cards should expose lightweight card actions without turning the dashboard into a full editor.
- Non-interactive card surfaces may be draggable; controls, links, inputs, textareas, and menu surfaces should cancel dragging.
- Drag preview placeholders should remain visible in dark mode by using `--ds-drag-preview-bg` and `--ds-drag-preview-border`, not card surface tokens that can match the artifact background.
- Inline chart titles and optional descriptions should wrap, avoid clipping, and stay visually part of the card header. Descriptions should be absent by default; include one only when the title is ambiguous or the note materially changes how to read the chart. If the surface exposes `showDescription`, leave it off unless the description is needed.

## App Chart Rendering

- Box plots and waterfalls may require custom shapes or the app's closest supported equivalent. Use custom panels only for deliberate non-native mark systems such as heatmaps and compact leaderboards.
- Render compact centered legends outside Recharts for multi-series charts so the plot resizes around them.
- Size standard Recharts charts with the v3 `responsive` chart prop and CSS sizing, not `ResponsiveContainer` wrappers or measured width/height props. The chart body should flex to fill the vertical space left by the header, with `min-height: 0` and bounded max height so it never grows past the card.
- Use full-space blue-shade cell heatmaps when a dense row-by-column comparison is needed: right-aligned row labels on the left, adaptive column labels below the grid, and hover tooltips for exact values.
- For complex custom chart types such as heatmaps, leaderboards, funnels, waterfalls, and box plots, let marks stretch when there are only a few rows; when marks would fall below their readable minimum, grow the chart block height instead of introducing vertical scrolling inside the chart body.
- Let Recharts v3 auto-size Y-axis gutters from formatted visible tick labels with `width="auto"`; use explicit nice ticks when the data domain needs stable labels.
- When a non-stacked multi-series chart omits explicit colors, use the runtime fallback order blue, orange, green, purple, red, pink, yellow, neutral. Stacked bars use the generated app's blue/purple token-shade fallback set.
- Disable chart intro animation when deterministic screenshots or hosted previews matter.

## Handoff

- Lead with the MCP artifact result, the Sites URL, or the exact blocker. For Sites, include the snapshot timestamp and say that the dashboard is a published snapshot rather than a live-connected view.
- Include source/freshness caveats, query or notebook references, and any omitted filters or datasets. For native artifact charts and tables, use the canonical `source` shape: runnable SQL in `source.query.sql`, plain-English summary in `source.query.description`, source predicates in `source.query.filters`, tables in `source.query.tables_used`, and metric formulas in `source.query.metric_definitions`.
- Do not ask the user to open a localhost server or static file as the primary dashboard handoff when the MCP artifact app can render the payload.
