# Model Audit Playbook

## Audit modes

### Rapid screen
Use when the user wants a quick view of model health, likely issues, or readiness for a meeting.

Deliver:
- model purpose and inferred decision context
- health score: green, yellow, red, or not assessable
- top 5 issues by decision impact
- must-fix items before use
- open questions and missing files

### Formula integrity audit
Use when the user asks whether formulas are right, whether a workbook is broken, or whether formulas tie across tabs.

Check:
- formulas copied consistently across rows and periods
- formulas using source/assumption cells rather than embedded constants
- external workbook links and stale links
- hidden or very hidden tabs
- volatile formulas: today, now, rand, offset, indirect, info, cell
- circular references or iterative-calculation dependencies
- balance sheet, cash flow, debt schedule, and covenant checks
- formulas that point to blank cells or unused ranges
- formulas overwritten by hardcoded values inside expected formula regions

### Source tie-out audit
Use when the user asks whether model values tie to filings, earnings documents, company supplements, market data, Credit Markets documents, provider exports, third-party data, or internal assumptions.

Check:
- each material historical number ties to a named source
- each forecast driver has a source, bridge, or explicit assumption
- stale market data and stale consensus are identified with as-of dates
- issuer/management/provider claims are not treated as verified facts
- conflicting sources are escalated rather than silently averaged
- each final output has a source path from source document to model cell to final output

### Scenario and sensitivity review
Use when the user asks whether a model is appropriately stress-tested.

Check:
- base, downside, and upside are coherent cases, not isolated arbitrary toggles
- sensitivity variables reflect the real value/risk drivers
- downside includes plausible negative outcomes for the asset class
- extreme cases do not break formulas or produce impossible outputs
- output ranges are not presented with false precision
- auditor-created replacement assumptions or stresses are labeled `Illustrative audit sensitivity` and are not represented as corrected forecasts or a revised base case

### IC-ready QA
Use when the model will support an investment memo, credit committee, client deck, board pack, or transaction decision.

Combine:
- workbook/formula audit
- source tie-out and evidence labels
- assumption critique
- scenario and downside review
- output traceability
- issue log with severity and owners
- decision-readiness posture

## Model-specific audit focus

### DCF / intrinsic value
- historical actuals tie to filings or source documents
- revenue, margin, capex, tax, working capital, and fcf assumptions are explicit
- terminal growth and exit multiple assumptions are defensible and not duplicative
- wacc, cost of equity, beta, risk-free rate, credit spread, and tax assumptions are sourced or clearly assumed
- enterprise-to-equity bridge includes debt, cash, minority interest, preferred, pensions, leases, and other claims where material
- sensitivity tables show the true drivers and do not overstate precision

### Three-statement operating model
- income statement, balance sheet, and cash flow statement link correctly
- working capital, depreciation, capex, debt, taxes, and equity schedules are internally consistent
- balance sheet balances in every period and checks are meaningful
- cash flow statement ties to cash on the balance sheet
- assumptions flow through all statements and do not create hidden plugs
- determine whether valuation or scenario outputs are intended to be embedded or provided by a linked companion layer; do not classify missing target price inside an operating model as a mechanical defect without confirming package scope
- when the stated use is an investment or portfolio decision, block decision readiness until a supportable linked decision layer exists

### Event-driven / transaction model
- transaction terms, consideration, dates, closing conditions, break fees, and spreads tie to primary documents or company releases
- probability-weighted outcomes reconcile to deal terms, downside price, timing, borrow/carry, and expected return
- regulatory, court, shareholder, financing, or other milestone assumptions are explicit and source-labeled
- downside and break-price cases do not rely on stale unaffected prices or unsupported valuation assumptions
- output return metrics tie to share price, consideration, timing, and probability assumptions
- catalyst bridge separates definitive terms, market spread, timing, probability, downside, and risk controls

### Comps / valuation range
- peer universe is justified and not cherry-picked
- market values, net debt, minority interest, preferred, leases, and other adjustments are current and sourced
- ltm/ntm metrics are calendarized and normalized consistently
- outliers are treated explicitly
- implied valuation range is not presented as more precise than the peer set supports

### Adjusted metrics / non-GAAP bridge
- non-GAAP adjustments are source-supported and reconciled to reported metrics where possible
- one-time, recurring, stock-based comp, restructuring, acquisition, FX, and pro forma adjustments are separated
- company-defined metrics are not treated as verified economics without support
- provider-standardized and analyst-adjusted views are not conflated
- adjustments that materially change valuation, leverage, coverage, or thesis support are escalated

### Credit Markets handoff / equity-risk debt context
- debt capacity, leverage, interest coverage, fixed charge coverage, and liquidity are calculated consistently when they affect common-equity downside
- covenant-pressure references cite the actual source definition, but covenant-package interpretation routes to Credit Markets
- EBITDA add-backs and baskets are source-supported before they influence equity value, sizing, or risk
- downside case tests debt service, liquidity, revolver usage, refinancing, and covenant-pressure risk as equity impairment inputs
- collateral, guarantees, priority, and recovery assumptions are visible only as handoff inputs unless Credit Markets supplies the analysis

### Restructuring / distressed-equity event context
- debt stack, collateral, guarantees, maturity, priority, liens, and intercreditor mechanics are identified as Credit Markets handoff inputs
- recovery waterfall, plan value, liquidation value, DIP, exit financing, fulcrum-security, and impaired-class analysis routes to Credit Markets
- Public Equity may use supplied restructuring outputs only as dated-event payoff inputs, common-equity option value, or downside impairment context

### Real estate / infrastructure / real assets
- NOI, occupancy, rents, rent roll, capex, reserves, taxes, insurance, and leasing costs are sourced
- DSCR, debt yield, LTV/LTC, and cap rate assumptions are current and supportable
- tenant rollover, lease expirations, market rent, and occupancy risk are stress-tested
- construction/project finance models include draw schedule, contingency, completion, and interest reserve logic

### Macro, rates, fixed income, FX, commodities
- prices, yields, curves, spreads, indices, and macro releases have as-of dates
- duration, convexity, carry, roll-down, and spread assumptions are clear
- base/downside/upside cases reflect coherent macro regimes
- stale market data is not mixed with current market commentary
- source conflicts across vendors, central bank data, and market feeds are flagged

## Decision-readiness posture

Use one of these labels:

- **ready for decision:** no unresolved critical/high issues, material outputs have source support, assumptions and downside are clearly disclosed.
- **ready with caveats:** usable if caveats are explicitly included in the memo/deck and listed fixes are not decision-changing.
- **not ready:** critical or high issues block use for an ic, lender, client, or trading decision.
- **not assessable:** missing workbook, key tabs, source documents, or outputs prevent reliable review.

For an audit-only mandate, use readiness and permitted-use language. If decision outputs are missing or unreliable, state `Do not use for portfolio action until remediated and re-audited` rather than expressing an add, trim, exit, hedge, or wait-for-proof investment stance.

## Public Equity Model Scope

This skill audits equity models, public-company valuation files, estimate update files, comps workbooks, DCFs, three-statement models, and public-equity sensitivity decks. Credit, macro, and real-asset model sections are reviewed only when they feed a common-equity decision. Route primary credit-security valuation, covenant-package work, spread/yield analysis, recovery waterfall, distressed claim valuation, or debt comps to Credit Markets.
