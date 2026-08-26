# QA rules

Use these checks before any normalized financials are handed to modeling, memo, deck/report, equity-model-update, scenario, risk, ETF/index, or earnings skills.

## Required QA outputs

Create `QA_Flags` with: `flag_id`, `severity`, `entity`, `period`, `area`, `issue`, `impact`, `recommended_fix`, `source_id`, and `status`.

Create `Validation_Checks` for checks actually performed, with: `check_id`, `area`, `period`, `test`, `expected_value`, `observed_value`, `variance`, `result`, `source_id`, and `notes`. Do not report a number of passed checks unless those checks are preserved here or in an equivalent audit output.

When disclosure definitions or presentation bases changed, create `Disclosure_Comparability_Bridge` before downstream handoff. Preserve the legacy and current bases, identify any recast comparable series, and state which lines are loadable, historical/audit-only, directional-only, or missing required source.

Severity:
- `blocker`: cannot use downstream until resolved.
- `high`: materially affects valuation, rating/target support, investment memo, earnings interpretation, equity risk, or public-equity reporting.
- `medium`: should be reviewed before senior/client/committee use.
- `low`: documentation, labeling, or immaterial cleanup.

## Source checks

- Every material value has a source ID and source location.
- Every source ID exists in `Source_Index`.
- Every source has source date, period coverage, and source type.
- User, management, provider, calculated, adjusted, estimated, and inferred values are separately labeled.
- Issuer guidance is labeled `issuer_management_claim` in `kpi_schedule`; `consensus_estimate` is reserved for externally sourced estimates labeled `estimate_consensus`.
- A user-supplied provenance note or source-support file is classified as `uploaded_file`, not `user_prompt`.
- Conflicting source values are retained in `Conflict_Log`.
- Stale or preliminary values are flagged but not automatically discarded.

## Period checks

- Fiscal year-end is identified or marked unknown.
- Annual, quarter, month, YTD, LTM/TTM, budget, forecast, estimate, and pro forma periods are labeled distinctly.
- Period end dates align with fiscal labels.
- Fiscal period-end dates are sourced explicitly; do not assume calendar quarter ends from labels such as `Q1 FY2027`.
- Stub periods are not mixed with full periods without disclosure.
- Restated values supersede prior values when restatement status is clear.

## Scale, unit, and currency checks

- Currency and units are identified for every value.
- Source units and normalized units are preserved.
- Factor-of-1,000 / 1,000,000 differences are flagged.
- Per-share, percentage, bps, count, and dollar values are not mixed.
- FX conversions include rate, date, and source.

## Income statement checks

- Revenue - COGS ties to gross profit when all values are available.
- Gross profit - operating expenses ties to operating income when all values are available.
- Pretax income - tax expense ties to net income when all values are available.
- EPS directionally ties to net income and share counts when available.
- Non-GAAP values are not treated as GAAP facts.
- Discontinued operations, minority interest, preferred dividends, and non-operating items are isolated when material.

## Balance sheet checks

- Total assets tie to total liabilities plus equity when available.
- Current assets and current liabilities tie to component sums when available.
- Ending cash ties to cash-flow statement ending cash when available.
- Debt, leases, preferred stock, and noncontrolling interest are not hidden inside generic liabilities/equity without notes.

## Cash flow checks

- CFO + CFI + CFF + FX effect ties to net change in cash when available.
- Beginning cash + net change ties to ending cash when available.
- Capex sign is explicit.
- FCF formula is explicit and not assumed to match company definition.
- Working-capital cash-flow signs preserve source convention unless clearly converted and documented.

## KPI and segment checks

- KPI definitions are captured or marked missing.
- Segment totals tie to consolidated totals when source provides reconciliations.
- Company-defined metrics are labeled company-defined.
- Sector metrics include units and definition: ARR, NRR, RPO, GMV, AUM, NIM, loss ratio, NOI, production, reserves, bookings, backlog, cohort data, and similar.
- New, renamed, regrouped, discontinued, or recast KPIs/segments appear in `Disclosure_Comparability_Bridge` with both available disclosure bases and a model treatment.
- Use `comparable_rounded` for a retained same-definition series available across periods in rounded narrative units; reserve `directional_only` for data that cannot support a comparable series.
- Narrative growth rates or rounded current-period disclosures do not silently become exact historical model inputs.

## Presentation-change checks

- Apply `recast_comparable` only to rows changed or re-presented on a comparable basis; do not apply a changed cash-and-securities presentation to unrelated balance-sheet lines.

## Downstream readiness

Mark readiness as `ready`, `partial`, or `not_ready` for relevant downstream skills.

For standalone model-ready requests, state readiness by schedule or series as well as overall. A consolidated actuals schedule may be `ready` while a recast segment driver schedule is `partial`; do not label the full package model-ready without this distinction.

- Valuation/DCF: revenue, margins/EBIT/EBITDA, tax, D&A, capex, working capital, cash, debt, shares, and forecast basis.
- Public valuation/modeling: historicals, revenue, EBITDA/EBIT, EPS, FCF, capex, working capital, cash/debt, tax, share count, and forecast drivers.
- Normalization adjustments: financials, trial balance/detail where available, management adjustments, add-back support, customer/vendor concentration, and NWC support.
- Earnings: reported financials, guidance/KPIs, transcript/source commentary if requested, and consensus if available.
- Credit Markets handoff / equity-risk context: net debt, cash, liquidity runway, maturity wall summary, rating or CDS/spread signal, refinancing pressure, and common-equity downside drivers. Route covenant disclosures, collateral coverage, recovery, bond/loan/CDS pricing, and debt-security analysis to Credit Markets.
- Internal/source exports: actuals, forecast/estimate, account/cost center mappings, department or segment owners, and refresh timestamp.
