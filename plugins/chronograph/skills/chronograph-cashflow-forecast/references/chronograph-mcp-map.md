# Chronograph MCP Data Map

Use this map to translate cashflow forecast data needs into Chronograph MCP tool selection. Do not hard-code tool names — read the Chronograph MCP server's live tool descriptions to stay current.

## Primary data needs

The skill needs four categories of data from the Chronograph MCP server:

- **Entity identifiers.** Fund IDs, group IDs, GP IDs, commitment IDs. Chronograph exposes a dedicated tool for resolving names to IDs. Use it before pulling any metric data.
- **Fund metadata.** Fund name, fund type, vintage year, reporting currency, geographic focus, final reporting date, general partner. Chronograph exposes a generic query tool covering core entity attributes — use it for all metadata reads.
- **Net LP commitment values.** NAV, called, distributed, unfunded, commitment amount, net IRR, net MOIC, DPI, RVPI. Chronograph exposes a dedicated tool for net LP-level performance that covers all of these in a single call.
- **Custom investment-level metrics (rare for cashflow forecasting).** Only needed if the user asks for non-standard metrics like Revenue or EBITDA. Chronograph exposes a metrics tool for these; it requires a discovery call first to enumerate available metric types.

## Net vs gross

This skill uses *net* LP cashflow values, not gross fund returns. If the user request is ambiguous ("show me MOIC for these funds"), confirm net or gross before pulling data. Gross returns (gross IRR, gross MOIC, cost, realized, unrealized) live in a separate Chronograph tool and are not used in this forecast.

## Currency

Do not default to USD. Resolve reporting currency from fund metadata before pulling cashflow values. If reporting currencies conflict across a multi-fund portfolio, ask the user.

## Fund type mapping

Map Chronograph fund-type values to general forecast buckets per the table in `model-methodology.md`. Do not duplicate that table here.

## Presentation requirements

Always surface in user-facing output:

- as-of date
- currency
- that the values are net (not gross)
- number of funds or commitments included
- any funds excluded because data was missing

When forecast assumptions are applied, separate Chronograph-reported actuals from model-generated forecasts.
