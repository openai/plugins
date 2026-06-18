---
name: chronograph-cashflow-forecast
description: Forecast private capital cashflows for existing portfolios using Chronograph MCP data and a Takahashi-Alexander style model. Use when Codex needs to analyze or forecast LP-level contributions, distributions, NAV, unfunded exposure, net cashflows, or Excel-style cashflow forecast outputs from existing Chronograph funds, commitments, groups, or portfolios.
---

# Chronograph Cashflow Forecast

**Requirements:** The Existing Portfolio Forecast mode requires a connected Chronograph MCP server — these workflows are designed for permissioned Chronograph users to connect to their private investment data. The Future Commitment Pacing Overlay mode runs from user-provided assumptions and works without a connection.

## Overview

Use the Chronograph MCP server as the source of truth for private capital commitment data, then forecast fund and portfolio cashflows with a Takahashi-Alexander style model. Prefer concise analysis in chat unless the user asks for a workbook, export, or model artifact.

Do not hard-code tool names — read the Chronograph MCP server's live tool descriptions to pick the appropriate tool for each data need.

## Workflow

1. Clarify scope only when needed: portfolio, group, fund IDs, commitment IDs, currency, as-of date, forecast horizon, and units. V1 is existing-portfolio-only; do not model future commitments or pacing schedules.
2. Resolve entities. The Chronograph MCP server exposes a tool for resolving fund, group, GP, or company names to IDs. Use it to turn user-provided names into IDs before pulling any metrics.
3. Pull fund metadata. The Chronograph MCP server exposes a generic query tool for retrieving core entity attributes — use it to get fund name, fund type, vintage year, reporting currency, geographic focus, general partner, and final reporting date where useful.
4. Pull net LP commitment values: NAV, called, distributed, unfunded, commitment amount, net IRR, net MOIC, DPI, and RVPI. The Chronograph MCP server exposes a dedicated tool for net LP-level performance that covers all of these. Treat the values as net and surface the as-of date, currency, and that the values are net (not gross) in user-facing results.
5. Map fund types to forecast assumptions. Use the default assumptions in `references/model-methodology.md` unless the user provides custom assumptions.
6. Build yearly or quarterly forecast periods from the as-of date through the requested horizon. Default to annual periods for executive analysis and quarterly periods for Excel-style output.
7. Forecast contributions, distributions, NAV, unfunded, and net cashflow by fund, then aggregate to portfolio, group, vintage, fund type, or GP as requested.
8. Present assumptions, source context, and checks. Always state currency, units, as-of date, forecast horizon, and that future commitments are excluded in V1.
9. If the user requests Excel, create a workbook with Inputs, Fund Forecast, Portfolio Summary, and Checks.

## Planning Mode

Use one of these modes, or combine them when the user asks for a liquidity plan:

- **Existing Portfolio Forecast.** Use Chronograph actuals for current commitments, NAV, unfunded, called, distributed, and net performance, then forecast runoff for existing commitments only.
- **Future Commitment Pacing Overlay.** Use user-provided planned commitments and strategy assumptions to estimate future calls, distributions, NAV, unfunded, exposure, and net cashflow. These values are planning assumptions, not Chronograph actuals.
- **Combined Liquidity Plan.** Add the existing portfolio forecast and pacing overlay to show total expected calls, distributions, net cashflow, NAV, unfunded, and exposure.

## Chronograph MCP Usage

The skill needs three categories of data from the Chronograph MCP server: entity identifiers (fund and group IDs), fund metadata (name, type, vintage, reporting currency, geographic focus, GP, final reporting date), and net LP-level cashflow values (NAV, called, distributed, unfunded, commitment amount, net IRR, net MOIC, DPI, RVPI). Inspect the server's live tool descriptions and pick the appropriate tool for each category. Do not hard-code tool names.

**Net vs gross — confirm with the user when ambiguous.** This skill forecasts *net* LP cashflows. The Chronograph MCP server exposes separate tools for net LP-level performance and gross fund-level returns. User requests like "show me MOIC for these funds" are ambiguous — confirm net or gross before picking a tool. Gross returns (gross IRR, gross MOIC, cost, realized, unrealized) are not used in this forecast and live in a different tool.

**Currency.** Do not default currency to USD. For specific funds, resolve reporting currency from fund metadata before pulling cashflow values. If reporting currencies conflict across a multi-fund portfolio, ask the user.

**Custom investment-level metrics.** If a tool requires a discovery / help / schema-introspection call first (common pattern on the Chronograph MCP server), make that call to see which metric types are available, then query each line item.

See `references/chronograph-mcp-map.md` for data-need to tool mapping guidance.

## Error Handling

- **MCP not connected.** Depends on mode. For an Existing Portfolio Forecast, stop — the connection is required, because forecasting runoff of a real portfolio needs its actual NAV, unfunded, called, and distributed baseline; do not invent those values or forecast a real portfolio from assumptions alone. For a Future Commitment Pacing Overlay (or a from-scratch pacing request with no existing portfolio), proceed from user-provided commitment amounts, vintages, and strategy assumptions, and label every value as a planning assumption rather than a Chronograph actual. If the user wants a Combined Liquidity Plan but Chronograph is unavailable, produce the pacing overlay only and list the existing-portfolio baseline as a missing input.
- **Entity not found.** Ask the user to confirm the fund / group / GP name. Do not silently substitute a near-match.
- **Currency cannot be resolved.** Ask the user which currency to use rather than defaulting to USD.
- **Future commitments / pacing overlay.** Chronograph is still the source of truth for the existing portfolio baseline. Future commitments are user-provided planning assumptions. Do not imply that planned commitments, future calls, future distributions, future NAV, or wind-down schedules are sourced from Chronograph if they are guided by the user in conversation.
- **Net-vs-gross ambiguity.** Confirm with the user before proceeding.
- **Pacing details incomplete.** If the user gives a high-level plan such as "deploy $500mm for a couple years, then wind down," make a conservative explicit schedule and label it as an assumption. Ask when the missing detail materially changes the decision, such as currency, annual versus total commitment budget, or strategy mix.

## Forecast Method

Use `references/model-methodology.md` for the distilled forecast methodology. Load it when doing actual forecast math, explaining assumptions, building an Excel output, or debugging differences versus a reference workbook.

Core outputs:

- Contributions: forecast capital calls.
- Distributions: forecast realizations/income.
- NAV: forecast residual value.
- Unfunded: forecast remaining callable commitment.
- Net cashflow: distributions minus contributions.
- Total exposure: NAV plus unfunded.

## Output Standards

- Include a compact assumption table whenever forecast values are shown.
- For planning-mode outputs, include a baseline section, an assumed commitment schedule, an overlay cashflow table, a combined liquidity view when available, and caveats / missing inputs.
- Separate actuals from forecasts. Label actual periods with `A` and forecast periods with `E` when producing Excel-style tables.
- Show totals and key years first, then detail by fund or fund type.
- Include basic checks: beginning NAV plus contributions less distributions plus growth should reconcile to ending NAV; prior unfunded less contributions should reconcile to ending unfunded; net cashflow should equal distributions less contributions.
- Avoid overstating precision. Forecasts are model estimates driven by assumptions, not Chronograph-reported future values.

## Guardrails

- Treat the output as draft analyst work product for liquidity and pacing planning.
- Do not provide investment, legal, tax, audit, or valuation advice. A forecast or liquidity plan is a scenario estimate, not a recommendation to commit, call, distribute, or sell.
- Do not present a pacing figure or commitment range as advice to act. Frame it as what the model implies under the stated assumptions, and surface the assumptions that drive it.
- Forecasts are scenario estimates under explicit assumptions, not predictions. Disclose the assumption set and that actual outcomes will differ.
- Do not imply that planned commitments, future calls, future distributions, or future NAV are sourced from Chronograph when they are user-provided planning inputs.

## Excel Outputs

When asked for Excel, use the spreadsheet skill and build a clean workbook rather than recreating the original workbook cell-by-cell. A good workbook shape is:

- `Inputs`: scope, as-of date, currency, units, horizon, assumptions by fund type.
- `Fund Forecast`: one row per fund/period with actuals and forecast values.
- `Portfolio Summary`: annual totals, net cashflow, NAV, unfunded, exposure, charts when useful.
- `Checks`: reconciliation checks and source context.

## Reference Files

- `references/model-methodology.md`: forecast formulas and default assumptions based on the Excel model.
- `references/chronograph-mcp-map.md`: Chronograph MCP data-need to tool mapping guidance for this workflow.
