# Hedge Instrument Playbooks

Use to select and critique instruments. The aim is not exhaustive coverage; it is PM judgment on fit, cost, and basis risk.

## Instrument Map

| Instrument | Best use | Key checks | Failure modes |
|---|---|---|---|
| Factor hedge | Reduce beta, growth/value, momentum, quality, size, leverage, duration, liquidity, or crowding while retaining idiosyncratic alpha | factor definition/source, stability across regimes, liquidity, crowding, whether factor is part of alpha | stale/unstable exposure, over-hedging alpha, crowded basket, correlation breaks, hedge becomes main P&L |
| Proxy hedge | Direct hedge unavailable, illiquid, too expensive, or too narrow | same driver, geography, currency, cycle, market cap, leverage, factor profile, liquidity, stress behavior | unrelated exposures dominate, fails in feared scenario, poor stress liquidity |
| Pair/peer hedge | Express relative value while reducing market/sector/factor risk | similar end-market, clear relative thesis, catalyst, borrow, dividends, corporate actions, sizing basis | short leg M&A/squeeze, borrow spike, spread not mean-reverting, hidden factor bet, both legs fall |
| Options | Nonlinear/event protection, defined downside, squeeze cap, upside preservation | expiry vs catalyst, strike vs downside, premium vs alpha, IV/skew/term, delta/gamma/vega/theta, liquidity, monetization | rich IV decay, wrong tenor, capped protection too soon, collar caps thesis upside, poor liquidity |
| Macro/cross-asset | Rates, curve, inflation, FX, commodity, country, vol, or CDS/credit-spread signal risk is causal to the equity thesis | economic link, tenor/roll, natural hedges, portfolio-level overlap, whether the proxy preserves alpha | loose macro proxy, relationship regime shift, roll dominates, headline exposure offset elsewhere |
| Credit Markets handoff / equity-risk signal | Use CDS levels, spreads, ratings, refinancing pressure, maturity walls, or covenant headlines only to judge common-equity downside; route implementation to Credit Markets | confirm the signal is causal to equity downside, dated, sourced, and not a substitute for credit-security analysis | treating a credit signal as an equity hedge, basis widens, capital-structure trade requires CDS/bond/loan expertise |
| Portfolio overlay | Common unwanted risk across book or single-name hedges are too costly | book exposure, benchmark risk, liquidity, rebalancing rules | over-hedges existing offsets, less precise, changes active risk |
| No hedge / size down | Hedge cost or basis risk is worse than exposure | opportunity cost, liquidity, tax/mandate, catalyst timing | missed protection if risk is hedgeable and material |

## Options Structures

| Structure | Best for | Tradeoff |
|---|---|---|
| Long put | Clean disaster/idiosyncratic downside | highest premium/theta |
| Put spread | Normal adverse move or event gap range | capped protection |
| Collar / put-spread collar | Lower net cost when upside can be sold | caps upside and/or disaster protection |
| Index/sector put | Broad beta/sector selloff | basis to single name |
| Long call on short | Cap squeeze risk when sized share-for-share and priced through maximum loss | premium drag and theta |
| Call spread on short | Offset a defined squeeze range | loss reopens above written call strike; not an absolute cap |
| Calendar / risk reversal | timing/vol or premium efficiency | more complex Greeks and obligations |

## Pair Sizing Choices

Dollar-neutral for similar risks; beta-neutral for market/sector beta; volatility-neutral for risk contribution; factor-neutral for style exposures; driver-neutral for units, revenue, commodity sensitivity, deposits/assets, or other economic drivers.

Treat every pair as a second thesis, not just a hedge.

For a short subject to an absolute loss cap, require one listed long-call contract per 100 shares short, adjusted for the contract multiplier and any corporate action. Maximum loss must include strike minus short sale entry, call premium, borrow/dividend cost, bid/ask and execution reserve, and applicable carry. If that package cannot be priced and shown within the cap, recommend no position rather than an unhedged or call-spread substitute.

## Sector Hedge Cues

| Sector | Likely exposures | Candidate hedges | Watch basis |
|---|---|---|---|
| SaaS/software | growth factor, rates/duration, NRR/bookings, IT spend, margins, AI disruption | software ETF, Nasdaq/growth basket, peer basket, earnings put spreads, rates proxy if duration matters | vertical vs horizontal, SMB vs enterprise, profitable vs unprofitable, seat vs usage, AI beneficiary vs disrupted |
| Semis | AI capex, memory/equipment cycle, China/export controls, inventory, margins | semi ETF, equipment/memory/analog peers, customer/supplier proxies, Nasdaq, options, China/Asia proxy | fabless/foundry/equipment, AI leader vs cyclical analog, China exposure, cycle timing |
| Banks | rates/curve, deposits, credit cycle, CRE, capital, regulation | bank ETF, regional/peer banks, curve hedge, event options; CDS/spreads as equity-downside signal only | asset sensitivity, deposit mix, CRE, capital ratios, HTM marks, regulatory category |
| Biotech/pharma | clinical/regulatory binary events, patent cliff, M&A, rates, reimbursement | biotech/pharma ETF, event options, modality/TA basket, index puts for funding risk | binary idiosyncratic risk often not hedgeable by ETF; tenor must match event |
| REITs | rates/cap rates, leverage/refi, property type, occupancy/rent growth | REIT ETF, property-type peers, rates futures, housing proxy; credit spreads as equity-risk signal only | property type and maturity structure dominate |
| Energy/E&P | oil/gas, basis differentials, service costs, production mix, balance sheet | commodity futures, energy/E&P ETF, service proxy; credit spreads as equity-downside signal only | company hedge book, basin, transport, production mix |
| Consumer/retail | consumer spend, wages/freight, inventory, promotions, rates/housing, FX | sector ETF, cohort/channel peers, rates/housing proxy, FX, earnings put spreads | luxury vs mass, online vs store, discretionary vs staple-like |
| Industrials/transports | PMI/capex cycle, backlog, labor/fuel, supply chain | industrial ETF, subsector peers, oil/fuel, cyclical basket, rates proxy; credit spreads as signal only | diversified ETF may not match subsector |
| Insurance | rates, investment income, catastrophe, reserves, pricing cycle | insurance ETF, line-specific peers, rates, cat-risk proxies | P&C/life/brokers/reinsurers differ |
| Exchanges/brokers | volumes, volatility, rates, cash balances, crypto, listings, regulation | peer basket, vol proxy, rates, financials ETF | vol can help exchanges but hurt brokers depending mix |
| Payments/fintech | consumer spend, cross-border, rates, credit losses, regulation, SMB, crypto | peer basket, financials/tech blend, consumer proxy, rates; credit-loss and spread signals as equity context only | networks/processors/lenders/wallets have different drivers |

## Recommendation-Changing Red Flags

Hedge cost exceeds expected alpha/protection value, hedge caps needed upside, hedge has more idiosyncratic risk than target, borrow is unavailable/unstable, option liquidity is poor, ETF overlap is weak, tenor misses catalyst, portfolio already offsets the risk, basis risk is highest in the adverse scenario, or size reduction is cleaner.
