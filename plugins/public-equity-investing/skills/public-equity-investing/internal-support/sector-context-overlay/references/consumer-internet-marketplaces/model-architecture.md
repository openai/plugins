# Model Architecture

Deferred reference for `sector-context-overlay` consumer-internet-marketplaces sector lens. Load only when the task needs a model build, model update, driver decomposition, or sensitivity design.

## Modeling rules for consumer internet and marketplaces

## Required model structure
- GMV or gross-bookings bridge built from active demand, frequency, ticket size, and mix.
- Revenue split into core transaction revenue, ads, subscriptions or memberships, payments or fintech, shipping or fulfillment, first-party or other, where relevant.
- Take-rate schedule by revenue component.
- Cohort-informed demand build where data allows.
- Supply-side schedule including active sellers, merchants, hosts, or providers and liquidity assumptions where relevant.
- Contribution-margin schedule capturing incentives, payment costs, support, trust and safety, insurance, logistics, and fulfillment costs.
- Opex schedule by sales and marketing, product or engineering, G and A, and regional investments.
- SBC and diluted-share-count schedule.
- Cash-flow schedule that explicitly captures working-capital balances, restricted cash, customer funds, and capex.

## Mandatory decomposition
- Separate growth from active-demand growth, frequency growth, and ticket-size growth.
- Separate take-rate changes from core-transaction growth.
- Separate ads, subscriptions, and fintech from the core marketplace.
- Separate direct-margin improvement from promotional cuts or timing benefits.
- Separate organic growth from M and A, divestitures, and FX.
- Separate gross and net recognition effects when mix can distort reported revenue.

## Archetype-specific driver trees

### Ecommerce marketplace
- active buyers x orders per buyer x AOV = GMS or GMV
- GMS x transaction take rate plus ads plus payments or services = revenue

### Travel marketplace
- room nights or nights booked x ADR = gross bookings or GBV
- gross bookings x effective take rate, adjusted for merchant or agency mix and timing = revenue

### Delivery or mobility marketplace
- monthly active consumers x orders or trips per consumer x average basket or gross booking per trip = GOV or gross bookings
- GOV x net revenue margin plus ads and memberships = revenue
- revenue less variable fulfillment and incentives = contribution profit

### Classifieds or listings marketplace
- paying listers or dealers x ARPA plus lead or media products = revenue
- do not force a GMV framework onto a listings model unless transactions are truly monetized

## Mandatory sensitivities
- active-buyer or active-consumer growth
- order, trip, or booking frequency
- AOV or ADR
- supply density or seller growth
- core transaction take rate
- ads or ancillary-service attach
- promotions and incentive intensity
- contribution margin and logistics cost
- working-capital support and restricted-cash assumptions
- valuation multiple on revenue, gross profit, contribution profit, EBITDA, or FCF as appropriate
