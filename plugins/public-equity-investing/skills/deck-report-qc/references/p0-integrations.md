# P0 Integrations

Use this map to fit `deck-report-qc` into the Public Equity Investing P0 stack.

## financial-source-of-truth

Use for:
- source hierarchy and controlling-source decisions
- stale-data checks and as-of-date standards
- citation format
- source conflict handling
- fact / assumption / issuer claim / management claim / third-party estimate labeling

Deck/report QC should identify source issues, then apply the source-of-truth standard to resolve them.

## model-audit-tieout

Use for:
- model formula errors
- workbook structure problems
- hardcodes, broken links, inconsistent formula families
- sensitivity/scenario logic
- source-to-model tie-outs
- formula-driven numbers that differ from deck/report outputs

Deck/report QC should not rebuild models. It should route model problems to model audit.

## excel-data-cleaner

Use for:
- badly formatted source tables
- inconsistent date/number formats
- duplicate records
- merged-cell tabular data
- CSV/XLSX cleanup before tie-out

## three-statement-model-builder

Use when a deck/report issue reveals missing or broken operating model logic, including financial-statement linkage, working capital, debt, capex, taxes, or cash flow.

## dcf-model-builder

Use when valuation deck/report issues involve DCF forecast drivers, WACC, terminal value, EV-to-equity bridge, sensitivity tables, or intrinsic value range.

## comps-valuation

Use when issues involve peer selection, calendarization, metric normalization, EV/equity bridge, multiple calculation, outlier treatment, or implied valuation range.

## equity-model-update

Use when issues involve model changes from filings, earnings releases, transcripts, guidance, consensus, KPI disclosures, share count, net debt, or market-data updates.

## Credit Markets

Use when issues involve a public-credit memo, bond/loan/CDS analysis, covenant disclosure, spread/yield relative value, recovery, restructuring, or distressed-security value. In this plugin, retain only common-equity read-through such as maturity wall, liquidity, refinancing risk, or CDS/spread signal.

## event-driven-analyzer

Use when issues involve M&A, spin-offs, activism, litigation, regulatory approvals, tenders, CVRs, strategic reviews, restructurings, index events, or other special situations.

## earnings-preview and earnings-deep-dive

Use when issues involve reported vs expected results, consensus, guidance deltas, transcript quotes, KPI tables, peer read-throughs, or earnings reaction history.

## economic-impact-report

Use when issues involve catalyst implications, macro shock pathways, cross-asset spillovers, winners/losers, or monitoring signals.

## memo-builder

Use after QC fixes when the user wants final IC/committee synthesis, decision framing, open questions, risks, and recommendation language.

## long-short-pitch and thesis-tracker

Use when issues involve investment thesis support, variant perception, catalyst path, risk/reward, thesis drift, invalidation tests, or ongoing monitoring signals.
