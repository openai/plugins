# SaaS Modeling Guardrails

Deferred reference for `SaaS Subscription Software Sector Analysis`. Load this when the task needs forecast, valuation, downside, credit, or security-specific modeling detail.

## Recurring-Revenue Posture

Treat a SaaS issuer as a recurring gross-profit stream whose value depends on retention, expansion, monetization architecture, product durability, and cash efficiency. Do not lead with generic technology shortcuts or headline revenue growth alone.

Start with what the customer buys, how seats/usage/transactions/data volumes convert into ARR, ACV, billings, RPO, revenue, and gross profit, how much growth comes from existing customers versus new logos, whether AI increases wallet share or cost to serve, and where the security sits in the capital structure. Treat beats as lower quality when they come from duration pull-forward, invoice timing, one-time mega-deals, services mix, reseller pass-through, acquisition noise, non-durable usage spikes, or aggressive FCF add-backs.

## Analysis Path

1. Monetization architecture: classify seat, usage, transaction, asset, API, bundled, or hybrid pricing; separate commitments from overages, prepaid credits, true-ups, onboarding, services, and channel pass-through.
2. Installed-base quality: verify ARR definition and measurement timing; split customer size, geography, product, channel, and end market; compare ARR growth, large-customer growth, gross retention, logo retention, NRR/DBNRR, and concentration.
3. Expansion behavior: decompose expansion into seat growth, usage, price, edition upgrades, module attach, cross-sell, and AI add-ons; test whether mature cohorts keep compounding or flatten after onboarding.
4. Billings, RPO, and revenue recognition: reconcile revenue, calculated billings, deferred revenue, RPO/cRPO, contract duration, billing cadence, renewal seasonality, cancellation terms, services deferrals, acquisitions, and FX.
5. Go-to-market quality: separate new-logo and expansion selling; review sales capacity, quota attainment, ramp time, pipeline coverage, win rates, partner productivity, Magic Number, CAC payback, and whether leverage is real or underinvestment.
6. Gross-margin architecture: isolate subscription, services, support, cloud, data-transfer, storage, partner revenue share, payment processing, data/content licensing, and AI inference costs; test whether AI is margin accretive, neutral, or dilutive at current pricing.
7. Cash conversion and dilution: reconcile GAAP margin, non-GAAP margin, operating cash flow, FCF, annual prepay, deferred revenue, restructuring, tax timing, SBC, share count, buybacks, capitalized commissions, internal-use software, and lease commitments.
8. Moat and AI risk: decide whether the product is system of record, system of action, point tool, infrastructure layer, or bundled feature; test workflow embedment, data lock-in, compliance burden, ecosystem, open-source risk, suite bundling, hyperscaler pressure, and AI commoditization.
9. Guidance and revision risk: compare revenue, margin, ARR, cRPO, billings, retention, and FCF guide to seasonality, backlog conversion, renewal calendar, large-deal timing, quarter-end linearity, FX, and management conservatism.
10. Public-equity security context and Credit Markets handoff: for equity, define rerating drivers, multiple support, dilution, and refinancing read-through. Route debt/convert instrument underwriting, covenant definitions, capped-call mechanics, and debt-security refinancing analysis to Credit Markets.

## Model Must Show

- Revenue driver tree by seat, usage, transaction, module, edition, price, AI attach, services, and channel economics.
- ARR, customer thresholds, gross retention, NRR/DBNRR, churn, expansion, cohort behavior, and customer concentration.
- Billings, deferred revenue, RPO/cRPO, contract duration, revenue recognition, and backlog conversion.
- Subscription gross margin, services gross margin, cloud/AI cost, S&M efficiency, CAC payback, operating leverage, SBC, dilution, OCF, and FCF.
- Sensitivities for retention, usage optimization, large-deal timing, AI cost, gross margin, sales productivity, cRPO conversion, multiple compression, and convert refinancing.

## Do Not

- Treat ARR, billings, cRPO, or Rule of 40 as clean without definitions, duration, usage, acquisitions, FX, and cash-quality checks.
- Read NRR without gross retention and logo retention.
- Value all recurring software on one multiple when seat-based, consumption, PLG, vertical SaaS, and transition stories have different durability.
- Treat FCF as high quality when it is mainly annual prepay, deferred-revenue growth, restructuring, SBC, or underinvestment.

## Deferred Modeling Layers

Load deeper files only when the task needs that layer:

- `valuation-rules.md`: valuation hierarchy and public-equity security context; route Credit Markets handoff rules to Credit Markets.
- `model-architecture.md`: required model structure, driver decomposition, and sensitivities.
