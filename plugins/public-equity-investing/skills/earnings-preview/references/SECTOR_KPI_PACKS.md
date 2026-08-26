# Sector KPI Packs

`sector_pack` selects default KPIs from `assets/sector_kpi_packs.yaml`; scripts also load driver templates from `assets/templates/driver_model_templates.yaml`.

## Selection Rules

- Prefer the company's actual disclosure model over a generic sector label.
- Use the pack as a default, then add/remove KPIs based on what can move the stock this quarter.
- Preserve company-specific metric definitions and mark definition changes or restatements.
- Do not force unsupported KPIs into a preview; label missing but important KPIs as data requests.

## Default Pack Families

- `saas`: revenue, ARR/RPO/billings, NRR/GRR/churn, customers/seats, ARPU/ARPA, gross/operating/FCF margin.
- `internet_marketplace`: GMV/GOV/GPV, active users/merchants, take rate, transactions, engagement, ad pricing/load, contribution margin.
- `consumer_retail`: revenue, comps, traffic, ticket, units, gross margin, inventory, markdowns, shrink, store/channel mix.
- `semis_hardware`: revenue, units, ASP, backlog, book-to-bill, utilization, inventory/channel inventory, gross margin, capex.
- `banks_financials`: NII, NIM, loan/deposit growth, deposit beta, PCL, charge-offs, delinquencies, CET1, efficiency ratio.
- `industrials_services`: orders, backlog, book-to-bill, utilization, pricing, mix, labor, operating margin, FCF.
- `energy`: production, realized prices, hedges, LOE/unit, capex, FCF, leverage, return of capital.

## Safe Edits

When editing YAML packs, keep metric IDs aligned with input files, add source/definition notes in the analysis, and update tests or sample inputs if a scripted output depends on the new metric.
