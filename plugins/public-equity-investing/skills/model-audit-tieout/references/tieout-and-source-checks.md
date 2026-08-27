# Tie-out and Source Checks

## Purpose

A model audit is incomplete unless material outputs and assumptions can be traced to reliable evidence. Use this reference to build a source tie-out ledger and identify whether the model is fact-supported, assumption-led, or unsupported.

When available, use financial-source-of-truth for the source hierarchy, stale-data rules, source conflict handling, and fact/assumption labels.

## Tie-out workflow

1. Identify key outputs.
2. Trace each output to the model tab, cell, and formula path.
3. Identify the assumptions, source rows, and source documents that feed the output.
4. Label each driver by evidence type.
5. Flag missing, stale, conflicting, or unsupported evidence.
6. State whether the output is decision-grade, research-grade, preliminary, assumption-led, or not supportable.

## Evidence labels

Use canonical labels consistently:

- **fact_source_reported:** directly supported by a source document or connected system.
- **fact_provider_standardized:** provider-standardized data from trusted market/financial data vendors.
- **derived_calculation:** calculated from cited inputs with visible formula or bridge.
- **issuer_management_claim:** statement from issuer management, earnings call, investor presentation, conference deck, or management interview.
- **management_adjusted:** management-defined adjusted metric or add-back.
- **analyst_adjusted:** analyst normalization, add-back, reclass, or pro forma change.
- **analyst_interpretation:** reasoned conclusion based on facts but not directly stated by a source.
- **assumption_user_provided:** assumption explicitly supplied by the user.
- **assumption_inferred:** assumption inferred from incomplete context.
- **estimate_consensus:** consensus/provider forecast or estimate.
- **stale_source:** source may be superseded for the current decision.
- **contradicted_source:** source conflicts with another material source.
- **missing_required_source:** no reliable support found or provided for a required item.
- **unknown:** evidence type cannot be determined.

## Source tie-out ledger fields

Use these fields for full audits:

| field | purpose |
|---|---|
| output_or_driver | material output, assumption, or line item being tested |
| model_location | workbook, tab, cell/range, formula, or memo/deck location |
| model_value | value shown in the model |
| source_name | filing, company supplement, transcript, Credit Markets document, market data source, model tab, or document |
| source_location | page, section, table, note, exhibit, or citation |
| source_value | value from the source |
| tie_status | ties, ties_with_rounding, does_not_tie, unsupported, stale, conflicting, not_tested |
| variance | difference between source and model value |
| evidence_label | evidence type label |
| as_of_date | date the source value was current |
| decision_impact | low, medium, high, or critical |
| recommended_action | fix, explain, sensitivity-test, source request, or escalate |

## Tie status definitions

- **ties:** model value matches source exactly or within immaterial rounding.
- **ties_with_rounding:** variance explained by rounding, scaling, currency conversion, or period convention.
- **does_not_tie:** variance is unexplained or material.
- **unsupported:** no source has been provided or identified.
- **stale:** source may have been valid historically but is not current for the decision.
- **conflicting:** two or more sources disagree and the model does not explain the chosen source.
- **not_tested:** outside current scope or source unavailable.

## Staleness rules by source type

Treat stale data as a model issue when it feeds a material decision driver.

Examples:
- market price, fx rate, yield, spread, index level, commodity price, public-equity multiple: must have a current as-of date.
- consensus estimates and broker data: must identify estimate date and data provider/source.
- financial statements: must identify fiscal period and whether annual data is audited or quarterly/interim.
- company presentations, conference decks, Credit Markets materials, rating reports, and provider exports: must identify document date, provider/as-of date, and whether a newer version exists.
- credit agreement, indenture, lease, purchase agreement, or court filing: must identify execution or filing date and whether amendments exist.

## Source conflict handling

When sources conflict:
1. Do not silently average or choose the source that supports the thesis.
2. Rank sources using financial-source-of-truth or the best available hierarchy.
3. Show the competing values and source dates.
4. Explain likely reasons for the variance: period, currency, scope, accounting treatment, pro forma adjustment, share count, denominator definition, or stale data.
5. Mark decision impact.
6. Recommend a tie-out fix or evidence request.

## Common tie-out failure patterns

- LTM metrics do not match the period used in comps or leverage calculations.
- EBITDA or adjusted metric definition differs across valuation, credit, covenant, and source tabs.
- Net debt excludes leases, preferred, minority interest, pensions, or earnouts inconsistently.
- Shares outstanding use basic share count in one tab and diluted share count in another.
- Market data is current in one tab but stale in another.
- Issuer add-backs or adjusted metrics are treated as verified economics without support.
- Model output ties to deck but neither ties to source documents.
- Forecast assumptions are presented as sourced facts.
