# Source and Data Protocol

## Source hierarchy
Use the highest-quality available source for each event. Prefer in this order:
1. User-provided materials, callable connected routes, and exports: portfolio exports, watchlists, models, research notes, internal calendars, CRM/IR notes, Slack/email summaries, Drive files, and approved market-data connectors.
2. Primary company sources: IR calendars, press releases, SEC/SEDAR/market filings, earnings releases, shareholder materials, prospectuses, registration statements, merger documents, event pages, and company presentation decks.
3. Regulator, court, exchange, and official calendars: SEC, FDA, EMA, CMS, FTC/DOJ, EU regulators, court dockets, exchange notices, index providers, central banks, treasury, BLS/BEA/Census/FRED, and other official agencies.
4. Trusted market-data and research routes or exports: FactSet, Bloomberg, LSEG, S&P Capital IQ, Visible Alpha, AlphaSense, Daloopa, Quartr, broker research, exchange calendars, and industry databases, subject to runtime availability and entitlement.
5. Reputable press and web sources, used as fallback or corroboration. Do not treat press speculation as a confirmed date.
6. User-provided assumptions, explicitly labeled as assumptions.

## Required source metadata
For each material event, capture:
- Source name and link or connector reference when available.
- Source date or retrieval date.
- Event date publication date if different from retrieval date.
- Confidence label: confirmed, guided, expected, inferred, rumored, or unknown.
- Date type: hard date, soft date, date window, quarter window, half-year window, seasonal window, or unknown.
- Last checked timestamp.

## Freshness rules
- Earnings dates, conference schedules, merger dates, regulatory dates, trial readouts, lockup expirations, and macro calendars can change. Treat them as time-sensitive.
- If the user asks for current or upcoming events, refresh using connected live sources or web where permitted.
- For recurring events, do not carry forward prior-year dates without labeling them inferred.
- When an aggregator and primary source conflict, prefer the primary source and show the conflict.
- If a date is stale, keep it in the tracker with status `Needs Refresh` rather than silently deleting it.

## Evidence labels
Use these labels in outputs:
- **Fact:** Source-backed event/date.
- **Company-guided:** Management has indicated timing but not exact confirmed details.
- **Consensus/Street:** Based on consensus or sell-side/buy-side expectation.
- **Inferred:** Derived from historical cadence, statutory timeline, or management commentary.
- **Assumption:** User or model assumption.
- **Judgment:** PM interpretation or prioritization.

## Non-destructive update protocol
When editing an existing file:
1. Create a backup/copy or new dated version.
2. Preserve raw source tabs, hidden tabs, formulas, comments, and prior evidence logs.
3. Append new rows rather than overwriting unless matching on a stable event ID.
4. If updating matched events, keep old date/status/source in change log.
5. Do not delete rows. Mark as archived, superseded, canceled, or stale.
6. Include a clear refresh log: date/time, sources checked, rows added, rows changed, rows requiring review.

## Confidentiality and compliance
- Treat internal research notes, portfolio holdings, meeting notes, and position-sizing context as confidential unless the user asks for an external-clean version.
- Do not blend confidential notes into an output intended for external distribution.
- Flag potential MNPI indicators, including non-public company guidance, non-public process details, private trial or regulatory communications, or private order/customer information.
- For external-clean materials, use only public or clearly authorized sources and omit internal view, position, cost basis, target prices, and trade intent unless explicitly approved.

## Index And Passive Flow Sources

Use index-provider, exchange, issuer, regulator, and primary company sources before aggregators. Index/ETF events require methodology, official announcement, holdings/rebalance file where available, issuer float/share-count disclosure, price, ADV, liquidity, and as-of times. Separate confirmed dates from inferred windows.
