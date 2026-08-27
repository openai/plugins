# HTML Dashboard Specification

Use this when the dashboard should be delivered as a portable, self-contained HTML file rather than a connected BI dashboard, MCP artifact dashboard, or Streamlit app. The generated reader may keep supported exploration interactions while remaining read-only and offline.

## When To Use

- Use HTML when the user requests a static file or when BI and MCP surfaces are not suitable for the requested handoff.
- Do not use HTML to bypass missing source access. HTML dashboards must still be source-backed, validated, and reproducible from reviewed data.
- Prefer MCP artifacts for ChatGPT Desktop handoff and BI tools for shared operating dashboards with managed refresh.

## Build Shape

- Read `../../../src/analytics-app-core.md`, including `Shared Contract` and `Portable HTML Packaging`.
- Author a complete `artifact.json` in the exact shape accepted by `validate_artifact`, with `surface: "dashboard"`, ordered native manifest blocks, compact bounded snapshot datasets, canonical sources, and required access issues. Prefer native metric-strip, chart, table, markdown, and filter definitions so the portable file stays aligned with the MCP artifact experience.
- Build and verify the dashboard once with `npm run report:deliver -- --input artifact.json --output report.html` from the plugin root. Treat the generated file as the only HTML implementation. The delivery command validates, embeds the read-only artifact reader, shared styling/tokens, layout, charts, tables, and supported exploration interactions, generates the semantic no-script/print/conversion representation, then runs the bounded verifier against the same artifact.
- Keep portable HTML exports content-only: include the dashboard title, narrative, charts, tables, filters, and source details, but omit the MCP app top bar and app-only controls.
- Lead with the dashboard's primary metric context, then trends, diagnostic breakdowns, and detail tables.
- Keep filters and interactions limited to canonical artifact controls that materially help the reader explore the dashboard. The portable reader is read-only and must not expose edit, persistence, refresh, export, share, or MCP-host-only controls.
- Give every source-backed card, chart, and table an inline `source` or a `sourceId` that resolves to `manifest.sources[]`. Preserve query links, exact source tables or datasets, freshness, definitions, and important predicates in the canonical source object. Treat accessible source affordances, tooltips/detail views, and the semantic source inventory as builder outputs.
- Use a markdown block's `sourceId` as block-wide provenance only when all quantitative claims in that block come from the same canonical source. Split mixed-provenance claims into separate blocks, omit `sourceId` on title-only or prose-only blocks, and never guess. File and document sources are valid and do not require SQL.
- Use compact reader-facing number formats in cards, chart labels, axes, tooltips, headings, and narrative text unless exact values are the point.
- Define business-specific KPI labels in nearby text or a source/methodology section so the dashboard can be understood without reading SQL.

## Validation

- Fix only validation, safety, source, payload-size, or browser failures reported by `report:deliver`, then rerun the same command. A compact success receipt with `stages.verification: "passed"` is sufficient per-dashboard QA; do not add routine screenshots, bespoke browser automation, or repeated visual inspection. If it reports `stages.verification: "structural_only"`, keep the delivered semantic chart tables and disclose that chart SVG extraction and per-artifact browser QA could not run because no compatible browser was available.
- The bounded browser verifier covers exact artifact embedding, enhanced-reader startup at desktop and narrow widths, rendered content counts and geometry, overflow, external requests, browser errors, and a representative source menu/dialog flow. Structural-only verification covers exact payload equality plus the required runtime, reader, and semantic-fallback roots. Shared reader CI—not per-dashboard work—owns deeper no-script, unsupported-browser, keyboard, print, conversion, touch, and multi-engine certification.
- Before handoff, reconcile cards, charts, and tables against the reviewed source extracts and ensure canonical provenance is non-placeholder. The shared reader and verifier own their rendering and source affordances.
