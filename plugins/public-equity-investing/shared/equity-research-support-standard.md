# Equity Research Support Standard

Use this shared standard for `financial-source-of-truth`, `financials-normalizer`, `excel-data-cleaner`, `deck-report-qc`, and `style-guide-adapter` inside Public Equity Investing.

Also load `shared/support-layer-routing-contract.md` whenever these skills are invoked as embedded support services under an owning Public Equity Investing workflow.

## Support-Layer Role

These skills are the research operating layer underneath public-equity work. They own evidence control, source hierarchy, data hygiene, financial normalization, table cleaning, artifact QC, and style preservation for long-only PMs, long/short hedge funds, sell-side equity research, event-driven equity investors, ETF/index diligence, and public-company diligence.

They do not own the investment conclusion. They should feed `earnings-preview`, `earnings-deep-dive`, `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `long-short-pitch`, `memo-builder`, `portfolio-risk-management`, `event-driven-analyzer`, `thesis-tracker`, and `dashboard-builder`.

## Embedded Services Contract

Support skills are usually embedded under the owning workflow, not peer investment owners. When embedded, preserve `owning_workflow`, `decision_impact`, `readiness_effect`, `artifact_role`, and whether support files are `hidden_unless_requested` in internal working context or support/audit artifacts. Do not print these field names in the user-facing hero artifact; surface material implications in plain reader-facing language. Standalone support use is allowed only when the user explicitly asks for source review, normalization, table cleaning, QC, or style adaptation as the task itself.

## Not-Owner Rule

They do not own memos, pitches, valuation, earnings calls, trade construction, credit research, or investment recommendations. If the user asks for the substantive view, route to the owning Public Equity skill after making the source/data/QC posture visible.

## PM Judgment Layer

Evidence quality is an investment input, not a footnote. Stale consensus, unsupported market data, conflicted EPS, missing source IDs, broken fiscal periods, bad units, unsupported chart claims, or style edits that alter caveats should change confidence, readiness, actionability, rating/target support, sizing, hedge posture, or watchlist status.

Every substantial support output should surface:

- evidence posture and source hierarchy;
- source/as-of dates for market-sensitive data;
- facts versus issuer claims versus consensus versus analyst assumptions;
- missing evidence that would change the public-equity decision;
- data QA issues that affect valuation, EPS, target price, rating, catalyst, benchmark/ETF/index exposure, sizing, or risk;
- the downstream owning skill and handoff readiness.

## Connector Honesty Rule

Never imply live Bloomberg, FactSet, S&P Capital IQ, CapIQ, LSEG, Refinitiv, Daloopa, PitchBook, Morningstar, broker, email, collaboration-app, or internal data-system access unless that connector/app/tool is actually callable in the current runtime. If unavailable, use user-provided exports, request the export, label the gap as `missing_required_source`, and keep the output `preliminary`, `screen-grade`, or `not supportable` as appropriate.

## Credit Markets Boundary

Credit data may support common-equity risk judgment when it explains refinancing stress, solvency pressure, maturity walls, liquidity risk, ratings pressure, CDS/spread warning signals, or downside equity impairment.

Credit Markets owns CDS, bonds, loans, investment-grade credit, high yield, leveraged loans, bank loans, private-credit / public-credit instruments, creditworthiness, covenant analysis, distressed, restructuring, recovery waterfalls, spread/yield relative value, and debt-security selection. In this plugin, credit terms may appear only as public-equity evidence or a Credit Markets handoff.

## Output Discipline

Support artifacts such as CSV, JSON, run logs, evidence ledgers, profiles, and style profiles are audit layers. For substantial user-facing work, lead with a concise source/data/QC verdict or an HTML/dashboard/workbook/report handoff when the owning skill calls for it. Never hide missing source evidence in sidecars.

When embedded, support artifacts should remain secondary to the owning workflow's HTML dashboard/report, XLSX workbook, memo/report, meeting brief, thesis tracker, or QC report. CSV, JSON, Markdown, logs, manifests, profiles, and ledgers stay behind the curtain unless requested.
