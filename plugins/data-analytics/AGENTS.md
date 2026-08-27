# Data Analytics MCP Apps

## Purpose

This plugin contains a complex fullscreen analytics artifact workspace, a shared read-only portable artifact reader, and compact inline chart and table widgets. Preserve that architecture when iterating: MCP and portable artifacts consume the same validated manifest/snapshot contract and reader components, while chart and table widgets remain focused views of reviewed query results.

## Visual Style

Follow the local Codex style contract in `src/codex-style-contract.md`.
`src/styles/codex-theme.css` is the copied Codex fallback baseline and must load before `src/analytics-app/tokens.css`. Shared surfaces, controls, typography, spacing, borders, radii, shadows, focus, and motion should resolve through the Codex tokens. Analytics CSS may extend the baseline for charts, KPI states, tables, report widths, and dashboard layouts.

## Fullscreen Behavior

Inline surfaces that support fullscreen expose a compact top-right fullscreen control and hide it after fullscreen is active.

## Portable HTML

Standalone HTML reports and dashboards are generated from the canonical `validate_artifact` input with `skills/build-report/scripts/build_portable_artifact.mjs`. The packaged portable entry must stay self-contained and read-only, use the shared reader components and Codex fallback tokens, make no network or MCP-host calls, and retain its generated semantic fallback unless the reader signals a successful first render. Keep portable-only editor and host exclusions behind the Vite aliases rather than forking the reader UI.

## Workflow

Before future changes, start with the installed `codex-mcp-app-devkit` skill so it can route to the app-development workflow and the Codex visual references. Use `npm run preview:widgets` for local previews, `npm run build` for all widget and portable-reader bundles, `npm run typecheck` for TypeScript, and `npm test` for MCP server, reader, builder, and widget contract coverage. Reader changes must also pass `npm run test:portable-browser`, `npm run test:portable-parity`, `npm run test:portable-conversions`, and `npm run test:portable-release`; those browser, adapter-parity, semantic-fallback conversion, and release-package gates are intentionally separate from `npm test`.

The plugin package is materialized directly from this directory. After changing widget source, run `npm run build` so `assets/` and normalized bundle parts stay aligned, then reinstall the updated development plugin from the Plugin Development marketplace when testing inside ChatGPT Desktop.
