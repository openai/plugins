# FA Credit Decisioning - Sub-flow Reference

**Tools used:** `fa_search_tool`, `query_portfolio`, `get_company_report`

This file defines the Credit Decisioning workflow. It is loaded by the master
`SKILL.md` when user intent resolves to a credit decisioning request or a
company overview to support a credit decision.

**Core question answered by this workflow:**

> "Give me a full picture of [Company X] so I can make an informed credit decision."

Use this workflow for broad, report-driven credit decisioning. Do not use it for
focused point questions (those call only the relevant tool directly) or for credit limit
validation requests (use `fa-credit-validation.md` instead).

---

## Pipeline Overview

```
Stage 1:  Resolve Company
  -> Stage 2:  Retrieve Report Data
    -> Stage 3:  Produce Credit Decisioning Report
```

---

## Trigger Examples

- "Provide an overview of Company Z to help me make a credit decision."
- "Provide an overview of Company Z, focusing on recent financials, negative legal events,
  and credit profile."
- "Run a credit decisioning for Company Z."
- "Generate the credit decisioning report for company X."
- Any question asking for a general company assessment that is NOT a portfolio question,
  NOT a focused credit limit validation, and NOT a narrow single-metric query.

---

## Stage 1 - Resolve Company

**Purpose:** Identify the correct company and obtain its DUNS number.

**Tool call sequence:**

1. If the user provided a DUNS directly: use it. Skip `fa_search_tool`.
2. If the user provided only a company name: call `fa_search_tool` with name and country.
   - If exactly one high-confidence match: proceed with that DUNS.
   - If multiple matches: show a short table (name, country, DUNS) and ask the user to
     select the correct company or provide the DUNS directly.
   - If no match: report that no record was found and ask the user to verify the name.

**Required outputs:** Confirmed company name, DUNS, country.

**Failure condition:** Do not proceed without a resolved DUNS.

---

## Stage 2 - Retrieve Report Data

**Purpose:** Pull the full D&B company report to populate the Credit Decisioning Report
template. Use portfolio data to supplement where available.

**Tool call sequence:**

1. Call `get_company_report` with the resolved DUNS.
   - Set `continue_report_pull` to `false` unless the user explicitly answered "yes" to
     a previous prompt about report retrieval. Do NOT carry this parameter over from
     earlier tool calls - each request requires a fresh evaluation.
   - Extract all fields listed in the Data Extraction Guide below.
2. Call `query_portfolio` with the resolved DUNS to retrieve any current portfolio
   account data (outstanding, past due, credit limit utilisation, account type).
   - Portfolio data supplements the report but does not override it for risk scores.
   - If the company is not in the portfolio, note this in the report.

**Data Extraction Guide - fields to extract from `get_company_report`:**

| Section | Field path |
|---|---|
| Company Name | `header.companyName` |
| DUNS | `header.duns` |
| Tradestyles | `header.tradestyles` |
| Business Status | `header.businessStatus` |
| Address | `header.address` (address1, city, stateCode, postalCode, country) |
| Phone | `header.phone` |
| Report Date | `header.reportDate` |
| PAYDEX Score | `scoring.paydex.score`, `.paymentBehavior`, `.days` |
| PAYDEX History | `scoring.paydex.history` |
| Delinquency Score | `scoring.delinquencyScore.score`, `.probability`, `.scoreCommentaryText` |
| Failure Score | `scoring.failureScore.score`, `.probability`, `.scoreCommentaryText` |
| D&B Rating | `scoring.currentDnbRating.score`, `.assignedRiskIndicatorMessageKey` |
| Viability Score | `scoring.viabilityScore.score`, `.viabRiskLevel`, `.portfolioRiskLevel` |
| Max Credit Recommendation | `scoring.maxCredit.amount`, `.currency`, `.riskLevel` |
| Overall Business Risk | `scoring.riskAssessment.overallAssessmentTextKey`, `.summaryRiskLevel` |
| Active/Bankruptcy Status | `scoring.activeStatus` |
| Annual Sales | `financialSummary.profitLoss.data.sales.current.value` |
| Net Worth | `financialSummary.balanceSheet.data.netWorth.current.value` |
| Total Assets | `financialSummary.balanceSheet.data.totalAsset.current.value` |
| Total Liabilities | `financialSummary.balanceSheet.data.totalLiabilities.current.value` |
| Current Assets | `financialSummary.balanceSheet.data.currentAsset.current.value` |
| Current Liabilities | `financialSummary.balanceSheet.data.currentLiabilities.current.value` |
| Pre-Tax Profit | `financialSummary.profitLoss.data.ebit.current.value` |
| Net Income | `financialSummary.profitLoss.data.netIncome.current.value` |
| Financial Source/Date | `financialSummary.source`, `.dateMonthYear` |
| Suits | `legalEvents.suitCount`, `.suitDate` |
| UCC Filings | `legalEvents.financingStatementFilingCount`, `.financingStatementFilingDate` |
| Judgments | `legalEvents.judgementCount`, `.judgementDate` |
| Liens | `legalEvents.lienCount`, `.lienDate` |
| Trade Payments | `tradePayments` object - avg high credit, now owing, past due, total experiences, trade within terms |
| Location Type | `ownership.locationType` |
| Member/Sub/Branch Count | `ownership.memberCount`, `.subsidiaryCount`, `.branchCount` |
| Named Principal | `companyProfile.namedPrincipal` |
| Control Ownership Date | `companyProfile.controlOwnershipDate` |
| Domestic/Global Ultimate | `ownership.ancestorInfos` |
| Employee Count | `keyDataElements.employees.minimumQuantity` |
| Business Start Year | `keyDataElements.businessStartYear`, `.ageofBusiness` |
| SIC/NAICS | `companyProfile.sicCode`, `.naicsCode` |
| Industry Description | `companyProfile.primaryIndustryCodeDescription` |

For any field not available in the tool output: use `Not available via tools`.
For news and funding events: `get_company_report` does not provide these natively - mark as
`Not available via tools` unless a separate tool call is made.

**Failure condition:** If `get_company_report` fails after one retry, document the gap and
produce a constrained report using any portfolio data available from `query_portfolio`.
Clearly label the report as constrained due to data unavailability.

---

## Stage 3 - Produce Credit Decisioning Report

**Purpose:** Populate and output the Credit Decisioning Report template using all data
retrieved in Stage 2. The template structure must be respected exactly.

**Formatting rules:**

- Use ATX headings only (`#`, `##`, `###`). No bolded pseudo-headings.
- Put a blank line after each heading and before/after every list or table.
- Do not start a list on the same line as a colon; move lists to the next line.
- Keep lists single level unless hierarchy requires nesting.
- Output `$` as `\$` to avoid encoding issues.

---

## Credit Decisioning Report Template

### Subject

`<Company Name> (DUNS: <#########>)`

### Executive Summary

Directly provide conclusions and answer to the initial question. State the overall risk
level, maximum credit recommendation, and any significant flags in 2-3 sentences.

### Risk Snapshot

- Overall Business Risk: `<overall_risk_level from scoring.riskAssessment>`
- Probability of Severe Delinquency (12 months): `<probability from scoring.delinquencyScore>`%
- Industry Comparison: `<Not available via tools or use relevant benchmark if available>`

**Source:** `get_company_report`

### Key Drivers of Credit Assessment

- Risk Drivers: `<items from risk model, if available>`
- Payment Drivers: `<items from payment behavior, if available>`

**Sources:** `get_company_report`

### Company Profile

- In Business Since: `<YYYY or duration>`
- Foreign Exposure: `<Yes/No/Unknown or Not available via tools>`
- Financials (Latest Summary):
  - Tangible Net Worth
  - Current Assets
  - Total Fixed Assets
  - Total Current Liabilities
  - Long Term Liabilities
  - Net Current Assets (Liabilities)
  - Sales/Revenue
  - Pre-Tax Profit
  - Net Profit

**Source:** `get_company_report`

### Corporate Structure

- Domestic Ultimate: `<Name - Country - DUNS or Not available via tools>`
- Global Ultimate: `<Name - Country - DUNS from ownership.ancestorInfos if available, else Not available>`
- Notes on Structure: `<concise summary or Not available via tools>`

**Source:** `get_company_report` (limited information may be available)

### Funding and Material Events

- Funding Events: `<Not available via tools unless fetched separately>`
- Derogatory Legal Events: `<Summary of suits, liens, judgments from legalEvents>`
- Ownership or Other Material Changes (Last Month): `<items or Not available via tools>`
- Significant Events: `<items indicating negative developments; otherwise Not available via tools>`

**Source:** `get_company_report`

### News with Potentially Negative Impact

From collected articles, identify only those that may indicate a negative credit impact.
Relevant signals include:

- Weak financial results, margin deterioration, or negative guidance
- Rising leverage, liquidity constraints, refinancing pressure, or debt-related issues
- Governance concerns (leadership exits, investigations, accounting issues)
- Regulatory, legal, or credit decisioning risks
- Operational disruptions (supply chain issues, cyber incidents, accidents)
- Sector or macro headwinds that materially affect the company

Exclude all articles that are neutral, irrelevant, or positive unless they contain embedded
credit-negative implications.

**Output format - Summary:**

Output the label `Summary:` exactly.

- If one or more negatively relevant items are found: provide exactly one concise sentence
  summarising key credit-negative themes. Group related topics into meaningful categories
  (e.g., liquidity pressure, governance instability, regulatory risk). Do not include article
  numbers or references in the summary.
- If no negatively relevant items are found: output exactly `Summary: No negatively impacting
  news found.` Do not generate the article list in this case.

**Output format - Relevant Articles** (only if negatively relevant items exist):

Output the label `Relevant Articles:` exactly. Number items sequentially starting from 1
(restart numbering in this section). For each article: provide a short title or one-sentence
overview, one sentence on the credit-relevant negative implication, and the article link.

**Source:** `get_company_report`

### Payment Behavior

- Average Days Beyond Terms (DBT): `<value from scoring.paydex.days>`
- Trend: `<Derived from scoring.paydex.history>`
- Comparison to Industry: `<Not available via tools or use relevant benchmark>`

**Source:** `get_company_report` (using `paydex`, `trade_payment_indicators`)

### Detailed Risk Metrics

For Failure Score, Delinquency Score, and PAYDEX:

- State the score as a percentile without `%` and without the word `percentile`
- Always include the probability value
- Always include the risk class and risk band

**Sources:** `get_company_report`

### Detailed Financials

Present the same financial fields as in Company Profile. By default, present the latest
available financial snapshot. If historical data is available from `get_company_report`,
present it as a table with one metric per row and each available year as a column. Note
that more historical data may be available on explicit request.

**Source:** `get_company_report`

### Notes and Exceptions

`<Data caveats, entitlement limits, missing fields, calculation notes>`

---

## Handoff Contracts

| Handoff | Payload |
|---|---|
| Stage 1 -> Stage 2 | Confirmed company name, DUNS, country |
| Stage 2 -> Stage 3 | Full `get_company_report` output, supplementary `query_portfolio` data, identified data gaps |
| Stage 3 -> Output | Completed Credit Decisioning Report, audit trail |

---

## Known Tool Integration Notes

| Tool | Issue | Handling |
|---|---|---|
| `get_company_report` | `continue_report_pull` must be `false` unless user has explicitly approved the report pull for this request | Never carry `continue_report_pull=true` over from prior conversation turns |
| `get_company_report` | Does not natively provide news or funding events | Mark as `Not available via tools`; do not fabricate |
| `query_portfolio` | A company may have multiple accounts per DUNS | Retrieve all accounts; summarise outstanding and past due at DUNS level |
| `fa_search_tool` | May return multiple candidates | Present a selection table; do not auto-select when ambiguous |

---

## Behavioural Requirements (Credit Decisioning - specific)

- Never make a binding credit approval or decline. The report is an informational credit
  assessment - final credit decisions must go through `fa-credit-validation.md` or the
  decisioning tools.
- Do not skip any template section. Use `Not available via tools` or `Not applicable` for
  missing data - never leave a section empty.
- Prefer `get_company_report` data over `query_portfolio` data for risk scores and financial
  data. Portfolio data supplements the report; it does not replace it.
- Always include the complete audit trail at the bottom of the output.


