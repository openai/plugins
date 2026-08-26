# Fact, Assumption, Claim, and Inference Labeling

Use this guide to keep public-equity-investing analysis honest about what is known, what is asserted, what is assumed, and what is inferred.

## Canonical label definitions

Use these machine-readable labels across source, normalization, audit, model update, and tearsheet outputs.

| Label | Definition | Example | Required treatment |
|---|---|---|---|
| `fact_source_reported` | Directly supported by a source document or connected system | FY2025 revenue from audited filing | Cite source and use normally |
| `fact_provider_standardized` | Provider-standardized data sourced from a trusted market/financial data vendor | Consensus EPS from provider export | Cite provider, timestamp, and limits |
| `derived_calculation` | Calculated from cited inputs | LTM revenue from four quarters | Show formula and cite inputs |
| `issuer_management_claim` | Asserted by issuer, company, or management | Investor presentation says AI attach rates improved retention | Attribute, caveat, and test |
| `management_adjusted` | Management-defined adjusted metric or add-back | Adjusted EBITDA per release | Cite definition and avoid treating as verified economics |
| `analyst_adjusted` | Analyst normalization or pro forma adjustment | Excluding one-time restructuring cost | State method, support, and inclusion decision |
| `analyst_interpretation` | Analyst conclusion drawn from evidence | Margin decline likely reflects mix pressure | Cite underlying facts and state confidence |
| `assumption_user_provided` | Explicit user assumption | User-provided terminal growth rate | Preserve and label |
| `assumption_inferred` | Agent/analyst assumption inferred from incomplete evidence | Estimated KPI split | Keep low confidence and request evidence |
| `estimate_consensus` | Consensus/provider forecast or estimate | Street FY2026 EPS | Cite provider/as-of date |
| `stale_source` | Source may be superseded for current decision | Old consensus pull | Flag freshness and replace if material |
| `contradicted_source` | Source conflicts with another material source | Filing and deck disagree | Preserve conflict and escalate |
| `missing_required_source` | Required fact or metric not available | Segment KPI not disclosed | Convert to evidence request |
| `unknown` | Evidence type cannot be determined | Unlabeled copied table | Do not use for decision-grade work |

Legacy prose labels such as "verified fact", "issuer/management claim", "assumption", and "estimate" are accepted by the validator as aliases, but new outputs should use the canonical labels above.

## Labeling standard by work product

### DCF and three-statement model

- Label historical values as sourced facts when tied to filings, releases, or audited statements.
- Label forecast drivers as assumptions unless explicitly supported by company guidance, disclosed backlog, or a cited operating driver.
- Label WACC, terminal growth, exit multiple, discount rate, and scenario cases as assumptions or estimates.

### Comps and valuation

- Label market prices, share counts, net debt, estimates, and multiples with timestamp/date and source.
- Label peer selection rationale separately from objective facts.
- Label adjusted EBITDA, non-GAAP, or calendarization comparability issues as estimates if definitions differ.

### Earnings and equity model update

- Label reported results, consensus, guidance, transcript statements, and analyst interpretation separately.
- Do not treat a management explanation as verified causality without supporting data.
- Separate company guidance from Street estimates and internal forecast assumptions.
- For EPS, separate reported GAAP EPS, management-adjusted EPS, analyst-adjusted recurring EPS, below-the-line items, tax/share-count effects, and consensus basis. A headline GAAP EPS beat is not a recurring earnings fact unless the bridge supports it.

### Credit Markets handoff / equity-risk signals

- Route covenant definitions, debt terms, trading levels, spreads, prices, yields, recovery values, and distressed-security conclusions to Credit Markets when the output is credit analysis.
- In Public Equity Investing, label CDS/spreads, ratings, maturity walls, refinancing pressure, liquidity runway, and covenant headlines only as equity-risk context.
- Label equity downside cases built from credit signals as analyst interpretation, estimate, or assumption unless directly supported by source documents.

### Event-driven and special situations

- Label definitive transaction terms only when tied to agreements, proxies, tender documents, or regulatory/court filings.
- Label probability, timing, remedy, and spread assumptions as assumptions unless explicitly source-backed.
- Separate company statements, press reports, and market-implied conclusions.

### Investment memo and long/short pitch

- Use labels to separate what supports the recommendation from what still needs evidence.
- In the executive summary, avoid conclusions that require unsourced assumptions unless clearly framed as conditional.
- Label variant perception and disconfirming evidence explicitly.

## Language standards

Use stronger language only when evidence supports it.

| Evidence strength | Suitable language | Avoid |
|---|---|---|
| Source fact | "reported", "filed", "contracted", "audited", "per source" | "appears" if no uncertainty exists |
| Provider fact | "according to", "reported by", "as stated in" | "verified" without primary support |
| Issuer / management claim | "company states", "management says", "issuer presentation claims" | "the company has" unless supported |
| Assumption | "we assume", "case assumes", "if" | "will", "should", "is expected" without source |
| Analyst interpretation | "suggests", "indicates", "is consistent with" | "proves", "confirms" |
| Missing / unknown | "not yet supported", "requires evidence" | filler or false precision |

## Assumption escalation rule

Escalate an assumption into a visible caveat when any of these are true:

- It changes valuation by more than a modest amount.
- It changes buy/sell/hold/pass, rating/target support, sizing, or common-equity risk view.
- It changes liquidity runway, solvency risk, refinancing pressure, or equity impairment risk.
- It is unsupported by current evidence.
- It contradicts management, market, historical, or peer evidence.
- It is a heroic assumption relative to peer or historical benchmarks.

## Claims ledger template

```markdown
| Issuer / management claim | Label | Evidence support | Test | Evidence request | Risk if false |
|---|---|---|---|---|---|
| [claim] | [`issuer_management_claim` / `analyst_interpretation`] | [source ID or none] | [how to test] | [request] | [impact] |
```
