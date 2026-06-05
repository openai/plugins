# FA Credit Limit Validation - Sub-flow Reference

**Tools used:** `fa_search_tool`, `query_portfolio`, `get_company_report`

This file defines the Credit Limit Validation workflow. It is loaded by the master
`SKILL.md` when user intent resolves to credit limit approval, increase, validation,
or a concise credit decision recommendation for a specific company.

**Core question answered by this workflow:**

> "Can I approve $X for [Company Y]?" or "Should I increase the credit limit for this customer?"

Use this workflow for concise, decision-focused credit limit assessments. Do not use it
for broad credit decisioning (use `fa-credit-decisioning.md`) or for creating new credit
applications (use the decisioning tools via `fa-onboarding-workflow.md`).

---

## Pipeline Overview

```
Stage 1:  Resolve Company
  -> Stage 2:  Retrieve Portfolio and Report Data
    -> Stage 3:  Produce Credit Validation Response
```

---

## Trigger Examples

- "Can I approve a 50,000 credit limit for Company X?"
- "I am owed 100,000 by Company Y. Can I increase the credit limit to 200,000?"
- "Validate this customer for a credit increase."
- "Give me a concise credit decision view for Company Z."
- "Can X's credit limit be raised to 50K?"
- "Should I extend more credit to this account?"

---

## Stage 1 - Resolve Company

**Purpose:** Identify the correct company and obtain its DUNS number.

**Tool call sequence:**

1. If the user provided a DUNS directly: use it. Skip `fa_search_tool`.
2. If the user provided only a company name: call `fa_search_tool` with name and country.
   - Identity resolution must use `fa_search_tool`, not `query_portfolio`.
   - If exactly one high-confidence match: proceed.
   - If multiple matches: show a short table (name, country, DUNS) and ask the user to
     confirm the correct company or provide the DUNS directly.
   - If no match: report that no record was found and ask the user to verify the name.

**Required outputs:** Confirmed company name, DUNS, country.

**Failure condition:** Do not proceed without a resolved DUNS.

---

## Stage 2 - Retrieve Portfolio and Report Data

**Purpose:** Gather the risk and financial data needed to perform the credit validation.
Portfolio data is the primary source; report data supplements missing fields only.

**Tool call sequence:**

1. Call `query_portfolio` with the resolved DUNS.
   - Restrict lookup to `credit_file_type` = `ACCOUNT` or `DUNSRIGHT` unless the user
     explicitly asks for another entity type.
   - A single DUNS may have **multiple accounts** in the portfolio. Retrieve ALL accounts
     associated with the DUNS. Never rely on a single account record for calculations.
   - Extract: `overall_business_risk`, `max_credit_recommendation`, `paydex_current`,
     `failure_score`, `delinquency_score`, `total_outstanding_dollars`,
     `total_past_due_dollars`, `credit_limit_utilization`, `db_bankruptcy_present`,
     trade payment indicators, legal event indicators, financial stress indicators.
   - Calculate the **Aggregated Existing Outstanding Amount** by summing
     `total_outstanding_dollars` across ALL accounts for the DUNS. Retain the
     account-level split for inclusion in Supporting Factors.
   - Calculate the **Aggregated Past Due Amount** by summing `total_past_due_dollars`
     across ALL accounts. Retain the account-level split.

2. Compare the returned fields against the required validation fields listed above.
   - If all required fields are present in the portfolio record: proceed to Stage 3
     without calling `get_company_report`.
   - If one or more required fields are missing from the portfolio record: call
     `get_company_report` with the resolved DUNS and extract only the missing fields.
   - **Portfolio values take precedence.** Never override a populated portfolio value
     with `get_company_report` data.

3. If the company is not in the portfolio at all: call `get_company_report` with the
   resolved DUNS for all validation data. Note in the output that the company is not
   in the portfolio.

**Required outputs:**

- Overall Business Risk (OBR) label
- Maximum Credit Recommendation (MCR) amount and currency
- PAYDEX / payment reliability score
- Failure Score and delinquency score
- Aggregated Existing Outstanding Amount (with account-level split if multiple accounts)
- Aggregated Past Due Amount
- Credit limit utilisation
- Bankruptcy and legal event flags
- Data source for each field (portfolio or report)

**Failure condition:** If neither portfolio nor report data is available, say that the
company could not be resolved or that validation data is unavailable. Do not invent values.

---

## Stage 3 - Produce Credit Validation Response

**Purpose:** Produce a concise, decision-supporting credit validation output. The response
must be 10-15 lines total and follow the output template exactly.

**Analysis rules:**

- Use `overall_business_risk` (OBR) and `max_credit_recommendation` (MCR) as the primary
  decision anchors.
- All validation calculations must be done at the DUNS level across ALL accounts.
- For credit extensions:
  - `Total Exposure = Aggregated Existing Outstanding Amount + Requested Credit Amount`
  - Validate Total Exposure against MCR, not only the requested credit amount.
- If Existing Outstanding Amount alone exceeds MCR: state this first before commenting
  on the requested credit amount.
- If Existing Outstanding Amount is not available and the DUNS is in the portfolio:
  compare only the requested credit amount and explicitly state that Total Exposure could not
  be calculated.
- If DUNS is not in the portfolio (using only `get_company_report`): compare only the
  requested credit amount against MCR. Do not mention Total Exposure.
- Never make a binding approval or decline. Frame the result as a suggested decision
  based on current data.
- Do not create, run, suggest, or check an application workflow or automated decisioning
  workflow unless the user explicitly asks for it.

**Response contract (strict):**

- Total length: 10-15 lines.
- Use exactly the sections in the Output Template below.
- Keep wording factual, short, and tool-grounded.
- Do not add background narrative, methodology sections, or full-report headings.
- All factual statements must be supported by explicit numbers (amounts, percentages,
  dates, classes, bands).
- Do not reference internal data labels such as `DUNSRIGHT record`, `ACCOUNT record`,
  `portfolio record`, or `report record` in user-facing output.

---

## Output Template

### Subject

#### `<Company Name> (DUNS: <#########>)`

### Executive Summary

Populate according to the applicable scenario below:

- **When credit limit available and Total Exposure can be calculated:**
  `<Company Name>` is assessed with an Overall Business Risk (OBR) of `<OBR Label - always
  append "risk" if not already present, e.g. Low risk, Low-Moderate risk, Moderate risk,
  Moderate-High risk, High risk>` and a Maximum Credit Recommendation (MCR) of
  `<MCR Amount Currency>`. Total Potential Exposure of `<Total Exposure Amount Currency>`
  (Existing Outstanding Amount `<Existing Outstanding Amount Currency>` + Requested Credit
  Amount `<Requested Amount Currency>`) is `<within/above>` the maximum recommended credit
  limit of `<MCR Amount Currency>` by `<Delta Amount Currency>`. `<Summarise significant
  legal events only if present - omit this sentence otherwise.>`

- **When Existing Outstanding Amount alone exceeds MCR:**
  `<Company Name>` is assessed with an OBR of `<OBR Label>` and an MCR of `<MCR Amount
  Currency>`. Existing Outstanding Amount of `<Amount Currency>` exceeds the MCR of
  `<MCR Amount Currency>` by `<Delta Amount Currency>`; an additional Requested Credit
  Amount of `<Requested Amount Currency>` is not recommended.

- **When Total Exposure cannot be calculated and DUNS is in portfolio:**
  `<Company Name>` is assessed with an OBR of `<OBR Label>` and an MCR of `<MCR Amount
  Currency>`. The requested credit limit `<Requested Amount Currency>` is `<within/above>`
  the MCR of `<MCR Amount Currency>` by `<Delta Amount Currency>`. Total Potential Exposure
  could not be calculated because Existing Outstanding Amount is not available.

- **When DUNS is not in portfolio (using only report data):**
  `<Company Name>` is assessed with an OBR of `<OBR Label>` and an MCR of `<MCR Amount
  Currency>`. The requested credit limit `<Requested Amount Currency>` is `<within/above>`
  the MCR of `<MCR Amount Currency>` by `<Delta Amount Currency>`.

- **When MCR is not available:**
  `<Company Name>` is assessed with an OBR of `<OBR Label>`. Maximum Credit Recommendation
  (MCR) is not available and hence a comparison cannot be made.

### Credit Assessment

- **Overall Business Risk (OBR):** `<Label>`
  - Overall assessment over the next 12 months: `<Label>`
  - Based on predicted risk of business discontinuation: `<Label>` (omit if not available)
  - Based on predicted risk of severely delinquent payments: `<Label>` (omit if not available)
- **Maximum Credit Recommendation (MCR):** `<Amount Currency>`
  - `<Tool-provided commentary, if available; omit when MCR is not available>`
- **Legal Events and News**
  - Legal Events: `<Detailed suits/liens/judgments if available>`
  - Latest News: `<Derogatory news specific to the company if available>`

### Response

Populate as per the Decision Logic below.

### Supporting Factors

3-5 short factual statements, directly supporting the decision. If multiple accounts were
retrieved for the DUNS, include the account-level split of outstanding and past due amounts
as a table. Example: "Delinquency Score risk class: 3 (Moderate) with 4.3% probability of
delinquency (effective YYYY-MM-DD)."

---

## Decision Logic

**If MCR is not numeric, is 0, or is not available:**
State exactly: `Maximum Credit Recommendation (MCR) is not available and hence a comparison
cannot be made.`

**If both `requested_limit` and MCR are numeric and greater than 0:**

| Condition | What to state |
|---|---|
| Existing Outstanding Amount available and exceeds MCR | "Existing Outstanding Amount `<amount>` exceeds MCR `<MCR>` by `<delta>`; an additional Requested Credit Amount `<requested>` is not recommended because Total Potential Exposure `<total>` would be above MCR." |
| Total Exposure available and within MCR | "Total Potential Exposure `<amount>` is within MCR `<MCR>` by `<delta>`." |
| Total Exposure available and above MCR | "Total Potential Exposure `<amount>` is above MCR `<MCR>` by `<delta>` and the request is not aligned with MCR." |
| Total Exposure not calculable, DUNS in portfolio, requested <= MCR | "Requested limit `<amount>` is within MCR `<MCR>` by `<delta>`. Total Potential Exposure could not be calculated because Existing Outstanding Amount is not available." |
| Total Exposure not calculable, DUNS in portfolio, requested > MCR | "Requested limit `<amount>` is above MCR `<MCR>` by `<delta>`. Total Potential Exposure could not be calculated because Existing Outstanding Amount is not available." |
| Total Exposure not calculable, DUNS not in portfolio, requested <= MCR | "Requested limit `<amount>` is within MCR `<MCR>` by `<delta>`." |
| Total Exposure not calculable, DUNS not in portfolio, requested > MCR | "Requested limit `<amount>` is above MCR `<MCR>` by `<delta>`." |

Do not use the words "approve" or "decline" in the Response section.

**Always include:**

- OBR label exactly as returned by tool output
- MCR amount and currency
- Total Exposure vs MCR numeric comparison when Existing Outstanding Amount is available
- Requested amount vs MCR comparison only when Total Exposure cannot be calculated

---

## Missing Data Rules

- If OBR is available and MCR is missing: state MCR as `Not available`.
- If both OBR and MCR are missing: state `Not available via tools`.
- Do not infer missing values.
- If a required field is missing from portfolio data: try `get_company_report` before
  marking it unavailable.
- Continue with a constrained answer using only available data.

---

## Handoff Contracts

| Handoff | Payload |
|---|---|
| Stage 1 -> Stage 2 | Confirmed company name, DUNS, country |
| Stage 2 -> Stage 3 | OBR, MCR, PAYDEX, failure score, delinquency score, aggregated outstanding amounts (with account-level split), legal flags, data source for each field |
| Stage 3 -> Output | Completed credit validation response (10-15 lines), audit trail |

---

## Known Tool Integration Notes

| Tool | Issue | Handling |
|---|---|---|
| `query_portfolio` | A single DUNS may have multiple accounts | Always retrieve all accounts. Aggregate outstanding and past due at DUNS level. Retain account-level split for output. |
| `query_portfolio` | Use for portfolio lookup only - not for name-based company search | Always resolve company name via `fa_search_tool` first, then look up by DUNS in portfolio |
| `get_company_report` | Use only to fill gaps missing from portfolio - never override portfolio values | Call only when `query_portfolio` does not return all required fields |
| `get_company_report` | `continue_report_pull` must be `false` unless user has explicitly approved | Never carry `continue_report_pull=true` from a prior conversation turn |

---

## Behavioural Requirements (Credit Validation - specific)

- Never make a binding approval or decline. The output is a suggested decision for the
  credit manager's consideration - they retain final authority.
- The response must be 10-15 lines. Do not expand into a full credit decisioning report.
- Do not trigger an application or account decisioning workflow from this sub-flow unless
  the user explicitly requests it. If they do, route to `fa-onboarding-workflow.md` Stage 3.
- Portfolio values always take precedence over report values for the same field.
- Always include the complete audit trail at the bottom of the output.


