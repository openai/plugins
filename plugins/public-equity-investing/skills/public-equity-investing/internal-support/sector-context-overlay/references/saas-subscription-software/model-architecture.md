# Model Architecture

Deferred reference for `sector-context-overlay` saas-subscription-software sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for SaaS and subscription software

## Required model structure
- Revenue split into subscription or SaaS, usage-based product revenue where applicable, professional services, and other.
- Customer or ARR bridge showing beginning ARR, new-logo ARR, expansion, price, contraction, churn, acquisition, FX, and ending ARR when possible.
- Separate drivers for seats, ARPU or price, usage or workload growth, and product attach.
- Backlog schedule linking deferred revenue, RPO or cRPO, billings, and revenue recognition.
- Gross-margin build by subscription, services, and major infrastructure or AI-cost drivers.
- Opex schedule by S&M, R&D, and G&A with explicit headcount or productivity assumptions when available.
- SBC and diluted-share-count schedule.
- Cash-flow schedule that captures deferred-revenue dynamics, capitalized commissions, capex, leases, and taxes.

## Mandatory decomposition
- Separate growth from new logos, expansion, price, and M&A.
- Separate seat-based growth from usage-based growth.
- Separate retention quality from expansion quality.
- Separate AI monetization from core product growth.
- Separate reported free cash flow from normalized free cash flow.

## Mandatory sensitivities
- gross retention
- NRR / DBNRR
- new-logo adds or new ARR
- contract-duration / billing-cadence assumptions
- subscription gross margin and AI/infrastructure cost
- sales-efficiency / Magic Number or payback assumptions
- SBC and diluted-share-count growth
- valuation multiple on revenue, gross profit, or FCF as appropriate
