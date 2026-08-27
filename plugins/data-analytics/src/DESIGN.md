---
name: Data Analytics Artifacts
description: Design contract for data analytics artifacts.
colors:
  bg-primary: { figma: "bg/primary", css: "--ds-surface", light: "#FFFFFF", dark: "#212121" }
  bg-secondary: { figma: "bg/secondary", css: "--ds-surface-secondary", light: "#E8E8E8", dark: "#303030" }
  bg-tertiary: { figma: "bg/tertiary", css: "--ds-surface-tertiary", light: "#F3F3F3", dark: "#414141" }
  border-light: { figma: "border/light", css: "--ds-border-subtle", light: "#0D0D0D / 5%", dark: "#FFFFFF / 5%" }
  border-default: { figma: "border/default", css: "--ds-border", light: "#0D0D0D / 10%", dark: "#FFFFFF / 15%" }
  border-heavy: { figma: "border/heavy", css: "--ds-border-strong", light: "#0D0D0D / 15%", dark: "#FFFFFF / 20%" }
  text-primary: { figma: "text/primary", css: "--ds-text-primary", light: "#0D0D0D", dark: "#FFFFFF" }
  text-secondary: { figma: "text/secondary", css: "--ds-text-secondary", light: "#5D5D5D", dark: "#CDCDCD" }
  text-tertiary: { figma: "text/tertiary", css: "--ds-text-tertiary", light: "#8F8F8F", dark: "#AFAFAF" }
  icon-accent: { figma: "icon/accent", css: "--ds-blue-bright", light: "#0285FF", dark: "#48AAFF" }
  warning-bg: { figma: "bg/status/warning", light: "#FFF5F0", dark: "#4A2206" }
  warning-text: { figma: "text/status/warning", light: "#E25507", dark: "#FF9E6C" }
  error-bg: { figma: "bg/status/error", light: "#FFF0F0", dark: "#4D100E" }
  error-text: { figma: "text/status/error", light: "#FF002A", dark: "#FF8583" }
  chart-blue-500: { figma: "blue/500", value: "#0169CC", use: "primary chart series in the reference artifact" }
  chart-blue-100: { figma: "blue/100", value: "#99CEFF", use: "light comparison or range fill" }
  chart-green-700: { figma: "green/700", value: "#00692A", use: "positive status or favorable delta" }
  chart-green-25: { figma: "green/25", value: "#EDFAF2", use: "positive status background" }
  chart-purple-500: { figma: "purple/500", value: "#8046D9", use: "secondary chart series family" }
typography:
  text-xs-normal: { figma: "text/xs/normal", fontFamily: "System Sans Variable", fontSize: "12px", lineHeight: "18px", fontWeight: 400 }
  text-xs-semibold: { figma: "text/xs/semibold", fontFamily: "System Sans Variable", fontSize: "12px", lineHeight: "18px", fontWeight: 600 }
  text-sm-normal: { figma: "text/sm/normal", fontFamily: "System Sans Variable", fontSize: "14px", lineHeight: "22px", fontWeight: 400, letterSpacing: "-1%" }
  text-sm-medium: { figma: "text/sm/medium", fontFamily: "System Sans Variable", fontSize: "14px", lineHeight: "22px", fontWeight: 500, letterSpacing: "-1%" }
  text-md-medium: { figma: "text/md/medium", fontFamily: "System Sans Variable", fontSize: "16px", lineHeight: "24px", fontWeight: 500 }
  heading-md-medium: { figma: "heading/md/medium", fontFamily: "System Sans Variable", fontSize: "20px", lineHeight: "26px", fontWeight: 500 }
  heading-2xl: { figma: "heading/2xl", fontFamily: "System Sans Variable", fontSize: "36px", lineHeight: "42px", fontWeight: 500, letterSpacing: "-2px" }
spacing:
  space-2: "4px"
  space-4: "8px"
  space-8: "16px"
  space-12: "24px"
  space-16: "32px"
  space-24: "48px"
rounded:
  control: { figma: "corner-radius/cr-8", value: "8px" }
  card: { figma: "corner-radius/cr-24", value: "24px" }
  pill: { figma: "corner-radius/cr-999", value: "999px" }
elevation:
  shell: { figma: "elevation/01", value: "0 4px 16px #0000000D" }
surfaces:
  report: { shell_width: "1140px", content_width: "800px", outer_padding_x: "48px", role: "narrative artifact" }
  dashboard: { shell_width: "1140px", content_width: "full", outer_padding_x: "24px", role: "visualization-first workspace" }
components:
  top-bar: { height: "48px", padding: "8px 12px", typography: "text/sm/medium" }
  metric-card: { min-width: "280px", padding: "20px", rounded: "corner-radius/cr-24", stroke: "border/light" }
  report-block: { width: "800px default", rounded: "corner-radius/cr-24", stroke: "border/light" }
  chart-block: { width: "full when needed", title: "text/sm/medium", body: "text/sm/normal" }
  table-list: { width: "800px in report context", cell: "text/sm/normal", header: "text/xs/semibold" }
  popover-menu: { row_height: "32px", rounded: "corner-radius/cr-8", surface: "bg/primary" }
implementation:
  app_runtime: "src/analytics-app"
  shared_components: "src/analytics-app"
  codex_baseline: "src/styles/codex-theme.css"
  runtime_tokens: "src/analytics-app/tokens.css"
---

# Data Analytics Artifacts

## Overview

Use this file as the portable design extension contract for generated Data Analytics reports and dashboards. The base visual system is the local Codex contract in `src/codex-style-contract.md` and `src/styles/codex-theme.css`. This file carries analytics-specific machine-readable tokens in YAML front matter and human-readable rationale below, so future agents can preserve chart, KPI, table, report, and dashboard roles without re-deriving the source design system for every edit.

This file is not runtime state. The React app loads the Codex baseline before `src/analytics-app/tokens.css`; the manifest and snapshot describe the data. `DESIGN.md` explains the analytics extensions, their design rationale, and what should remain customizable when a user edits an artifact.

The canonical analytics app lives in `src/analytics-app`. It renders both dashboard and report surfaces from the manifest. Charting, table, layout, font,
and token components are materialized inside `src/analytics-app` so plugin distributions do not contain runtime symlinks.

## Colors

Use semantic foundation tokens first. Use the reference artifact colors only for chart series and status accents that appear in the reference design.

- `bg/primary`: light `#FFFFFF`, dark `#212121`
- `bg/secondary`: light `#E8E8E8`, dark `#303030`
- `bg/tertiary`: light `#F3F3F3`, dark `#414141`
- `border/light`: light `#0D0D0D / 5%`, dark `#FFFFFF / 5%`
- `border/default`: light `#0D0D0D / 10%`, dark `#FFFFFF / 15%`
- `border/heavy`: light `#0D0D0D / 15%`, dark `#FFFFFF / 20%`
- `text/primary`: light `#0D0D0D`, dark `#FFFFFF`
- `text/secondary`: light `#5D5D5D`, dark `#CDCDCD`
- `text/tertiary`: light `#8F8F8F`, dark `#AFAFAF`
- `icon/accent`: light `#0285FF`, dark `#48AAFF`
- `bg/status/warning`: light `#FFF5F0`, dark `#4A2206`
- `text/status/warning`: light `#E25507`, dark `#FF9E6C`
- `bg/status/error`: light `#FFF0F0`, dark `#4D100E`
- `text/status/error`: light `#FF002A`, dark `#FF8583`
- Reference accents: `blue/500` = `#0169CC`, `blue/100` = `#99CEFF`,
  `green/700` = `#00692A`, `green/25` = `#EDFAF2`, and `purple/500` = `#8046D9`

Do not hardcode these hex values in components unless the token layer cannot express the role. Map semantic names into CSS variables in `src/analytics-app/tokens.css`.

Chart manifests can declare `palette.kind` to make color intent explicit:

- `categorical`: unrelated groups such as segment, region, model, or plan.
- `sequential`: ordered magnitude such as low-to-high density or intensity.
- `diverging`: movement around a meaningful midpoint such as zero, baseline,
  or target.
- `semantic`: analytical roles such as actual, comparison, forecast, plan,
  baseline, or target.
- `identity`: externally owned colors such as product colors or source-system labels.

Color must not be the only encoding for meaning. Use labels, ordering,
reference lines, line styles, direct annotation, or chart structure when the reader needs to understand status, change, or role without relying on color alone.

## Typography

Use the Codex host font through `--codex-font-sans`. `System Sans Variable` remains the local fallback for generated packages. Keep type compact, neutral, and scannable.

- `text/xs/normal`: 12px size, 18px line height, regular weight.
- `text/xs/semibold`: 12px size, 18px line height, semibold weight.
- `text/sm/normal`: 14px size, 22px line height, regular weight, -1% letter spacing.
- `text/sm/medium`: 14px size, 22px line height, medium weight, -1% letter spacing.
- `text/md/medium`: 16px size, 24px line height, medium weight.
- `heading/md/medium`: 20px size, 26px line height, medium weight.
- `heading/2xl`: 36px size, 42px line height, medium weight, -2px letter spacing.

Use `text/sm/medium` for the top bar, chart titles, and compact UI labels. Use `text/sm/normal` for report body copy and explanatory text. Use `text/xs/normal` or `text/xs/semibold` for table headers, legend labels, and supporting metadata.

## Layout

Reports are narrative artifacts. Preserve the 1140px shell, 800px reading column, 48px horizontal gutters, compact 48px top bar, and source-backed metadata path. Start with the answer, then evidence, then caveats or next steps. Use full-width blocks only when a chart, legend, or table needs more room than the reading column.

Dashboards are visualization-first workspaces. Preserve the same shell,
tokens, and app affordances, but let the content use the full width. The default order is KPI cards, primary trend, diagnostic charts, then detail tables. Global filters belong near the top only when they affect the full visible dashboard.

Both surfaces must be snapshot-first, locally previewable, and clear about freshness. If the data is blocked, partial, or fixture-only, show that through the manifest status and status surfaces instead of implying a live result.

## Elevation & Depth

Use depth sparingly. `elevation/01` (`0 4px 16px #0000000D`) belongs on the artifact shell and on real overlays such as popovers. Most component hierarchy should come from spacing, typography, borders, and subtle surface changes, not from stacked shadows.

Use `border/light` for row dividers, chart panels, metric cards, and report blocks. Use `border/default` or `border/heavy` only when a state or container needs stronger separation.

## Shapes

Use the Codex radius roles for shared UI. Keep these analytics recipes aligned with the mapped Foundations radius tokens.

- `corner-radius/cr-8`: controls, menus, compact inputs, and small buttons.
- `corner-radius/cr-24`: metric cards, chart panels, report blocks, and major artifact containers.
- `corner-radius/cr-999`: pills, badges, and compact filter chips.

Do not mix one-off radii into generated artifacts. If a generated package needs a new radius, add it to the token map before using it in components.

## Components

Shared buttons, menus, inputs, and modals should consume the Codex baseline roles. Extend components only where an analytics-specific visualization or layout needs it.

Top bar:

- Height: 48px.
- Padding: 8px vertical, 12px horizontal.
- Type: `text/sm/medium`, `text/primary`.
- Contents: artifact title, date/freshness affordance, share or overflow actions. Keep the title compact; do not turn the top bar into a hero.

Metric card:

- Use a 280px content-safe minimum width and match the tallest card in each row. Dashboard and report strips balance any declared card count responsively; four columns are allowed only when four cards fit without wrapping, and four is neither a target nor a maximum.
- Padding: 20px on all sides.
- Radius: `corner-radius/cr-24`.
- Stroke: `border/light`.
- Label: `text/xs/normal` or `text/xs/semibold`.
- Value: medium weight with tabular numerals.
- Use status color only for warning, error, or access states.

Report block:

- Default to the 800px content column.
- Use `bg/primary`, `border/light`, and `corner-radius/cr-24` for framed evidence blocks.
- Keep markdown narrative in editable markdown blocks. Keep visual titles neutral and put interpretation in adjacent narrative.

Chart block:

- Use the full available width when axis labels, legends, or comparisons need it.
- Header type should follow `text/sm/medium`; supporting text should follow `text/sm/normal` or `text/xs/normal`.
- Use `border/light` dividers and `bg/tertiary` only for subtle structure.

Table list:

- Report context width: 800px.
- Header type: `text/xs/semibold`.
- Cell type: `text/sm/normal`.
- Dividers: `border/light`.
- Dashboard tables should stay dense and scannable; short report tables may be slightly more spacious.

Popover menu:

- Radius: `corner-radius/cr-8`.
- Row height: 32px.
- Surface: `bg/primary` with `border/light` and `elevation/01` only when it is an actual overlay.
- Keep overflow controls out of copied chart/card images.

## Do's and Don'ts

Do choose the visual from the analytical comparison:

- Time trends: line or area.
- Ranked categories and top drivers: horizontal bar or compact leaderboard.
- Part-to-whole: stacked or 100% stacked bar only when the denominator is explicit.
- Distributions: histogram or box plot.
- Cohort, matrix, or two-dimensional intensity: heatmap.
- Additive bridge: waterfall.
- Stage progression: funnel or stage bars.

Do let complex chart blocks size to their marks before adding nested scroll.
For heatmaps, leaderboards, funnels, waterfalls, box plots, and similar custom renderers, marks should stretch when the dataset is small; once a row, stage,
or mark would fall below its readable minimum, grow the block height instead of making the chart body vertically scroll.

Do keep generated artifacts customizable. Users may change titles, markdown,
section order, card order, compatible chart type, table column widths, safe labels, and dashboard filter defaults. Preserve the manifest, snapshot, source notes, and this design contract as the audit path.

Do keep skill prose lean. Put mechanical rules in validators and tests. Put runtime values in `src/tokens.css`. Put portable visual guidance here.

Don't combine unrelated metrics in one generic movement chart. If measures use different units, denominators, directions, or materially different scales,
split them into typed KPI cards, separate trends, or a table with units.

Don't add visible source, reproducibility, or evidence chrome to the report body unless the artifact explicitly asks for it. Keep that in metadata and evidence affordances.

Don't replace tokenized surfaces with bespoke React unless the shared analytics primitives cannot express the artifact honestly.
