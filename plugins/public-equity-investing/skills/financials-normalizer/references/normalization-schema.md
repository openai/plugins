# Normalization schema

Use this schema for model-ready financial outputs. Prefer long-form staging first; pivot to wide statements only after QA.

## Source_Index

Required columns:
- `source_id`: stable identifier such as `SRC-001`.
- `source_name`: file, system, report, filing, provider, or source title.
- `source_type`: `uploaded_file`, `callable_connected_system`, `user_provided_export`, `filing`, `earnings_release`, `transcript`, `investor_deck`, `provider_export`, `web`, `user_prompt`, `assumption`. Use `uploaded_file` for a supplied provenance note or source-support file; use `user_prompt` only for facts or instructions contained directly in the user's message.
- `owner_or_provider`: source owner, provider, or uploader when known.
- `period_covered`: period(s) covered by source.
- `as_of_date`: report date, filing date, close date, data snapshot date, or version date.
- `retrieved_at`: date/time the assistant accessed or used the source.
- `file_tab_page_url_or_location`: page, tab, cell, row, URL, connected table, or object reference.
- `source_rank`: rank from source protocol.
- `freshness_status`: `current`, `acceptable_for_period`, `preliminary`, `stale`, `unknown`.
- `notes`: caveats, version notes, limitations.

`source_id` cannot be blank for decision-grade outputs. If deterministic helpers emit `SRC-UNSPECIFIED`, treat it as a blocking provenance error until a real `SRC-###` ID from `Source_Index` is assigned.

## Normalized_Financials_Long

Required columns:
- `entity`
- `source_id`
- `statement`: `income_statement`, `balance_sheet`, `cash_flow`, `kpi_schedule`, `segment`, `equity_risk_debt_liquidity_context`, `share_count`, `working_capital`, `capital_allocation`, `consensus_estimate`, `etf_index_context`, `adjustment`
- `line_item_original`
- `line_item_standard`
- `line_item_id`
- `period_end`: `YYYY-MM-DD` when known.
- `period_label`: source period label such as FY2025, Q1-2026, LTM Sep-2025, Apr-2026.
- `period_type`: `annual`, `quarterly`, `monthly`, `ytd`, `ltm`, `forecast`, `budget`, `pro_forma`, `scenario`.
- `currency`
- `units`: source or normalized unit such as ones, $000, $mm, %, bps.
- `source_value`: exact extracted value where possible.
- `normalized_value`: numeric value in normalized unit/sign convention.
- `normalization_method`: e.g. `as_reported`, `scaled_or_sign_normalized`, `calculated`, `mapped`, `currency_converted`.
- `source_location`: page, table, tab, cell, row, URL, or system object.
- `evidence_label`: one of the required canonical labels in SKILL.md.
- `confidence`: `high`, `medium`, or `low`.
- `normalization_note`

Use `kpi_schedule` with `issuer_management_claim` for issuer outlook or guidance. Use `consensus_estimate` only for an external consensus estimate or provider forecast, with `estimate_consensus`; do not classify company guidance as consensus.

## Wide outputs

Pivot long-form values into these sheets only after staging:
- `Normalized_IS`
- `Normalized_BS`
- `Normalized_CF`
- `KPI_Schedule`
- `Equity_Risk_Debt_Liquidity_Context`
- `Share_Count`
- `Segment_Financials`
- `Working_Capital`

Each wide output should retain source/citation columns or companion note columns if cell-level comments are not supported.

## Standalone model-ready package

When the user explicitly requests model-ready normalized financials, the staged long-form file is the audit foundation, not the complete human deliverable. Create:

- complete wide load schedules for the sourced scope, such as income statement, balance sheet, cash flow, segment/KPI, guidance, adjustments, and share-count schedules where supplied;
- `Disclosure_Comparability_Bridge` when segment, KPI, non-GAAP, or presentation definitions changed;
- `QA_Flags` containing every material open readiness exception;
- `Validation_Checks` recording each performed tie-out/control and its result; and
- `Source_Index` and `Normalized_Financials_Long` as traceable supporting data.

A compact headline-metric schedule may be included for review, but it must not be labeled a complete model-input package when material statement or driver lines were sourced and omitted.

For any loadable wide schedule, retain or accompany each affected series with `comparison_status` (`comparable`, `comparable_rounded`, `recast_comparable`, `legacy_only`, `directional_only`, `missing_required_source`, or `not_comparable`) and `model_treatment`. Apply the status line by line: a presentation change should affect only the lines actually re-presented or redefined.

## Sign conventions

Default institutional modeling convention:
- Revenue, gross profit, EBITDA, operating income, pretax income, net income: positive when income/profit.
- Expenses: positive as line-item values unless a downstream model explicitly requires negative expenses.
- Assets, liabilities, equity, cash, debt: positive balances.
- Cash-flow inflows: positive. Cash-flow outflows: negative.
- Capex: negative in cash-flow outputs; positive as a separate operating driver if requested by downstream model.
- Changes in working capital: preserve source cash-flow sign; do not convert to balance-sheet delta without documenting method.
- Share count and per-share data: preserve units separately from currency.

## Scaling and currency

- Preserve source scale in `source_value` and normalized scale/sign in `normalized_value` / `units`.
- Default to `$mm` for institutional finance work unless user/source/downstream model specifies another unit. The shipped helper can infer common USD/GBP/EUR markers, common quarter/year period labels, `$000` / `$mm` / `$bn` scale, and cash-flow capex sign convention.
- Do not perform full currency conversion unless requested or needed for comparability. When converting, include FX rate, date, and source in `normalization_note` and `Source_Index`.

## Deterministic helper output contract

The shipped `scripts/normalize_extracted_financials.py` helper emits:
- `Source_Index.csv`
- `Normalized_Financials_Long.csv`
- `Normalization_Issues.csv`

It does not automatically create wide statements, KPI schedules, adjustment logs, conflict logs, assumption registers, workbook tabs, or full FX conversions. Those are instruction-led artifacts that should be built only when the agent has enough source context and explicitly creates them.

If an instruction-led XLSX workbook is created from normalized outputs, make `Cover` the first visible tab and summarize source posture, normalized period/entity scope, key metrics, conflict count, adjustment count, unresolved assumptions, and the workbook map before statement/detail tabs.

## Required companion logs

### Adjustments_Log
Use for all normalized, pro forma, issuer/management-defined, provider-standardized, or analyst adjustments. Include: `adjustment_id`, `entity`, `period`, `metric`, `amount`, `direction`, `reason`, `source_id`, `evidence_label`, `confidence`, `included_in_output`.

### Conflict_Log
Use for material conflicting values. Include: `conflict_id`, `entity`, `metric`, `period`, `source_a`, `value_a`, `source_b`, `value_b`, `conflict_type`, `working_value`, `resolution_basis`, `open_question`.

### Assumptions_Register
Use for user or inferred assumptions. Include: `assumption_id`, `assumption`, `source_or_owner`, `rationale`, `affected_outputs`, `evidence_label`, `confidence`, `replacement_source_needed`.

### QA_Flags
Use for exceptions. Include: `flag_id`, `severity`, `entity`, `period`, `area`, `issue`, `impact`, `recommended_fix`, `source_id`, `status`.

### Disclosure_Comparability_Bridge
Use whenever disclosures are renamed, regrouped, newly introduced, discontinued, recast, or definition-changed. Include: `area`, `metric_or_framework`, `current_period`, `prior_period`, `current_basis`, `prior_basis`, `comparison_status`, `current_value`, `prior_value`, `model_treatment`, `required_source`, `source_id`.

Preserve legacy components and current-framework lines even when no exact bridge is possible. Do not create loadable historical values by deriving undisclosed amounts from rounded disclosures or narrative growth rates.

Use `comparable_rounded` rather than `directional_only` when the issuer reports the same retained metric across both periods and only rounding prevents an exact total tie-out. For example, a retained top-level platform series may be comparable for trend analysis even while new sub-platform history remains unavailable.

### Validation_Checks
Use for controls actually performed. Include: `check_id`, `area`, `period`, `test`, `expected_value`, `observed_value`, `variance`, `result`, `source_id`, `notes`.

Distinguish helper processing issues from analytical readiness exceptions: `Normalization_Issues` records extraction/schema/provenance processing problems, while `QA_Flags` records substantive downstream-readiness issues. An empty `Normalization_Issues` output never overrides open `QA_Flags`.


Credit-security schedules such as covenant packages, recovery waterfalls, bond/loan/CDS pricing, spread/yield relative value, and debt-security selection belong in Credit Markets. This schema may hold net debt, maturities, liquidity, ratings, or CDS/spread signals only as common-equity risk context.
