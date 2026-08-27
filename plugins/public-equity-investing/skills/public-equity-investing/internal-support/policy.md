# Internal Support Policy

## Purpose

This file is the Public Equity Investing adapter layer for bundled support capabilities. Visible skills own listed-equity decisions and user-facing workflows. Internal playbooks provide evidence control, data preparation,
rendering, style application, and sector context without expanding the selectable skill catalogue. Model QA remains a visible workflow.

## Internal Capability Registry

These capabilities are packaged with this plugin but are not registered `SKILL.md` entrypoints:

| Capability label | Internal playbook | Plugin-specific obligation |
| --- | --- | --- |
| `dashboard-builder` | `internal-support/dashboard-builder/INTERNAL.md` | Render optional standardized dashboards with citation visibility and readiness posture. |
| `financial-source-of-truth` | `internal-support/financial-source-of-truth/INTERNAL.md` | Apply public-company source hierarchy, market-data freshness, and evidence labels. |
| `excel-data-cleaner` | `internal-support/excel-data-cleaner/INTERNAL.md` | Preserve ticker, period, unit, timestamp, and equity-workflow identifiers. |
| `style-guide-adapter` | `internal-support/style-guide-adapter/INTERNAL.md` | Restyle without changing facts, formulas, citations, or investment conclusions. |
| `sector-context-overlay` | `internal-support/sector-context-overlay/INTERNAL.md` | Supply sector lens only under an owning listed-equity workflow. |
| `daloopa-provider-guide` | `internal-support/daloopa-provider-guide/INTERNAL.md` | Shape bounded, explicit-period Daloopa calls and preserve provider citations. |
| `quartr-provider-guide` | `internal-support/quartr-provider-guide/INTERNAL.md` | Shape bounded Quartr filing, document, event, and standardized-financial calls with provenance. |

`financials-normalizer`, `model-audit-tieout`, `deck-report-qc`, and `scenario-sensitivity-generator` remain visible in this release because normalization, model review, circulation review, and scenario interpretation can each be explicit user-facing public-equity jobs.

## Routing Rule

After the plugin invocation gate passes, a visible owning workflow may load an internal playbook whenever its support lane is needed. Existing documents may continue to use the capability labels above; resolve each label to its `INTERNAL.md` file rather than asking the user to select a separate skill.

For an explicit support-only request within Public Equity Investing, such as cleaning an equity workbook, applying a style guide, checking sources, or rendering an already-defined dashboard, the root router coordinates the request and loads the matching internal playbook.
Use `standalone_support_request` as the owning workflow where the playbook requires one, and preserve its support-artifact/readiness rules.

Provider guides are narrower: load one only after an ordinary workflow attempts a semantic source category, selects Quartr or Daloopa as the concrete route, and confirms that route is callable in the current runtime. Do not load provider guides during preflight, onboarding, broad setup, or merely because `.app.json` declares a dependency.

## Customization Boundary

This policy and the referenced internal playbooks are plugin-owned adapters:
customized plugin distributions may change them to reflect team evidence,
style, readiness, workbook, or dashboard requirements. Reusable support engines must consume these Public Equity-specific obligations rather than silently replacing them with generic behavior.
