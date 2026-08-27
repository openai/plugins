# Credit Markets Handoff

Public Equity Investing owns common-stock, ADR, listed-equity, equity-short, pair-trade, event-driven equity, earnings, valuation, thesis-tracking, and equity portfolio workflows.

Use Credit Markets for credit instruments, creditworthiness, restructuring, distressed, recovery, spreads, yields, covenants, and debt security analysis.

Keep leverage, maturities, liquidity, ratings, spreads, covenants, debt terms, and recovery considerations in this plugin only when they support a listed-equity decision. If the user's primary decision is a bond, loan, CDS, private-credit / public-credit instruments, distressed exchange, restructuring, bankruptcy, covenant package, recovery waterfall, or debt-security relative-value question, route out to Credit Markets.

## PM/Risk Handoff Boundary

For `portfolio-risk-management`, Public Equity Investing owns sizing and hedge judgment for listed-equity longs, listed-equity shorts, pairs, ETF/index constituents, listed options, equity factor hedges, and macro proxies when the purpose is a public-equity decision.

Use Credit Markets for CDS hedges, bond hedges, loan hedges, high-yield or investment-grade bond selection, leveraged loans, bank loans, spread DV01 / CS01 sizing, credit spread hedges, capital-structure hedges, distressed hedges, recovery waterfalls, covenant hedging, covenant analysis, debt-security valuation, and any credit instrument where the security being sized or hedged is debt or CDS.

Public Equity Investing exception: CDS, credit spreads, ratings, maturity walls, refinancing pressure, covenant headlines, and liquidity stress may appear only as equity-risk context, warning signals, or inputs to common-equity downside. If the next action is to buy, sell, size, hedge, or value a credit security, route to Credit Markets.

Risk-workflow reminder: credit hedge construction belongs in Credit Markets; use here only as public-equity risk context. Route CDS, bonds, loans, spread DV01/CS01, capital-structure, distressed, recovery, and covenant implementation to Credit Markets.
