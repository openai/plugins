# Issue Taxonomy

## Severity levels

### Critical
Use when the issue likely changes the public-equity investment decision, valuation range, liquidity conclusion, common-equity recovery read-through, or client recommendation; route credit-approval, covenant-package, and recovery-workflow issues to Credit Markets.

Examples:
- broken formula in final valuation or return output
- debt schedule, covenant-pressure, or liquidity calculation materially wrong for common-equity downside; route covenant-package analysis to Credit Markets
- key source value does not tie and changes the recommendation
- issuer/management/provider claim treated as verified fact for a material driver
- model omits a material claim in enterprise-to-equity bridge or common-equity recovery read-through; route recovery waterfalls to Credit Markets
- final output uses stale market data that would materially change the answer

### High
Use when the issue may materially change the result or undermine confidence and should be fixed before ic, client, credit committee, or trading use.

Examples:
- formula inconsistency in a key forecast row
- external links feed key outputs and source files are missing
- material assumption lacks source support or sensitivity
- downside case does not test relevant liquidity, covenant-pressure, margin, or exit risk
- control checks are missing or inadequate for a key schedule

### Medium
Use when the issue matters for quality, traceability, or explanation but is unlikely to change the decision alone.

Examples:
- hardcoded constant inside a non-core formula
- model lacks clear source labels for some historical inputs
- sensitivity range is narrow but not central to the decision
- output labels or units are ambiguous
- hidden tabs exist but appear non-material

### Low
Use for minor cleanups that improve readability or handoff quality.

Examples:
- inconsistent formatting
- unclear tab names
- duplicated labels
- minor rounding differences
- incomplete but non-critical footnotes

### Info
Use for observations, optional improvements, or context.

Examples:
- model could benefit from a dashboard
- add version-control notes
- add optional sensitivities for presentation quality

## Issue categories

- **formula_integrity:** formula errors, overwritten formulas, inconsistent formulas, hardcodes, broken links, volatile formulas, circularity.
- **source_tieout:** value does not tie to source, no source, stale source, conflicting sources, unclear source hierarchy.
- **assumption_support:** key forecast or valuation driver lacks evidence, bridge, benchmark, or sensitivity.
- **scenario_design:** base/downside/upside cases are incoherent, missing, too narrow, or not relevant to the decision.
- **model_architecture:** workbook structure, tab flow, input/calculation/output separation, hidden sheets, macros, checks.
- **output_presentation:** final outputs, dashboards, memo/deck values, units, labels, precision, footnotes.
- **governance:** version control, review trail, source dates, signoffs, protected formulas, change log.
- **formatting:** cosmetic or readability items.

## Reader-Facing Finding Types

Use one of these finding types for each decision-relevant issue so the report does not conflate mechanical errors, underwriting gaps, and package-scope omissions:

- **Formula/control defect:** broken or misleading workbook mechanics, checks, links, formulas, or controls.
- **Source contradiction:** a modeled value conflicts with a controlling source without a supported explanation.
- **Unsupported assumption:** a forecast or valuation driver may be intentional but lacks evidence, approval, or sensitivity support.
- **Missing forecast refresh:** new actuals, guidance, market data, or source developments have not been bridged into the forecast.
- **Missing decision output:** the requested decision requires a linked valuation, scenario, price implication, or risk output not present in the reviewed package.
- **Not comparable without bridge:** a model metric and disclosed metric use different definitions, periods, currencies, or adjustment bases.

Label auditor-created replacement assumptions or stress calculations `Illustrative audit sensitivity`; they diagnose decision impact but do not constitute corrected model forecasts or a revised base case.

## Owner defaults

Assign likely owner when possible:
- analyst: formula corrections, tie-outs, formatting, source labels
- associate/vp: assumption logic, model architecture, scenario design, output framing
- md/pm/ic member: decision posture, risk tolerance, recommendation, valuation/range choice
- Credit Markets reviewer: covenant definitions, credit-approval standards, risk appetite, debt-security analysis
- accounting/research lead: adjusted metrics, accounting treatment, restatement issues, reporting quality
- issuer/management/provider: issuer claims, source support, provider extracts, missing evidence
- legal/restructuring counsel: credit agreement, indenture, priority, intercreditor, bankruptcy plan issues
- unknown: use only when owner is unclear

## Escalation rules

Escalate immediately when:
- a critical issue affects a final model output
- source documents are missing for a material claim
- the model appears to use stale market data for a live decision
- covenant-pressure, liquidity, debt capacity, or common-equity recovery read-through outputs are unsupported; route credit-security outputs to Credit Markets
- the workbook contains hidden or external-linked data that drives outputs
- formulas cannot be recalculated or reviewed
- the user asks for a recommendation but the model is not decision-ready

## Model health score

Use this simple score for rapid screens:

- **green:** no unresolved high/critical issues; model is reviewable and source-supported for the requested use.
- **yellow:** some medium/high caveats; model can be used only with explicit caveats and targeted fixes.
- **red:** high/critical issues block decision use.
- **gray:** insufficient information to assess.

## Equity Decision Severity Overlay

Severity is driven by public-equity decision impact: wrong value/share, wrong EPS or FCF path, unsupported selected multiple, stale market data, broken source tie-out, false downside protection, or hidden model mechanics that would change target, rating, sizing, hedge, trim, exit, or watchlist status. Credit-specific issues route to Credit Markets unless they directly impair common-equity value.
