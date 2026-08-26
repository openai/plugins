# Source Hierarchy and Evidence Discipline

Use this reference whenever source quality, citations, or missing data affect the analysis.

## Core principle

Event-driven investing is document driven. Press is useful for context, but primary documents define terms, rights, deadlines, remedies, and process. Treat market prices as evidence of market belief, not as truth.

## Global source hierarchy

1. User-provided materials: uploaded filings, models, memos, trackers, notes, call transcripts, and pasted text.
2. Callable connected routes or user-provided exports: Google Drive, Slack, Gmail, Notion, internal research stores, broker data, or market-data connectors.
3. Primary public records: filings, court dockets, regulator pages, company releases, exchange notices, and official calendars.
4. Market data: prices, spreads, borrow, options, bonds, loans, CDS, rates, consensus, peer multiples, and factor data.
5. Company materials: investor decks, transcripts, annual reports, proxy materials, activist decks, spin information statements, lender presentations.
6. Third-party commentary: sell-side, legal alerts, press, specialist newsletters, expert call notes, and web search.

## Evidence weighting rules

- Signed transaction documents beat press releases.
- Definitive proxy/S-4/offer documents beat announcement decks.
- Court orders beat legal commentary.
- Regulator calendars and official decisions beat management timing optimism.
- Ordinary-course company documents can be more probative than advocacy materials.
- Market price reflects consensus and constraints; it does not answer the underwriting question.
- User assumptions may be used, but must be labeled as user assumptions.

## Source map by event type

### Merger arbitrage
Primary sources:
- Merger agreement exhibit to 8-K or equivalent.
- S-4/F-4 for stock deals.
- Preliminary and definitive proxy.
- Schedule TO and 14D-9 for tender offers.
- Press release and investor presentation.
- Antitrust/regulatory filings and agency updates.
- Shareholder meeting materials and vote results.

Must extract:
- Consideration, exchange ratio, collar, election mechanics.
- Conditions, outside date, termination rights, break fee, reverse termination fee.
- Financing commitments, debt marketing, buyer funding obligations.
- Required approvals and vote thresholds.
- Background/process details that indicate buyer commitment or renegotiation risk.

### Spin-offs and split-offs
Primary sources:
- Form 10, information statement, proxy/prospectus, 8-Ks, parent filings.
- Separation agreement, tax matters agreement, employee matters agreement, transition services agreement.
- Capitalization table and pro forma financials.
- When-issued trading notices and exchange/index announcements.

Must extract:
- Distribution ratio, record date, distribution date, tax treatment, retained stake.
- Debt allocation, cash transfer, stranded costs, dis-synergies, transition costs.
- Management incentives, board composition, segment financials.
- Index eligibility and expected holder base.

### Activism
Primary sources:
- 13D/G and amendments.
- Activist letters, presentations, proxy materials, definitive proxy cards.
- Company response letters and governance documents.
- Bylaws, advance notice deadlines, rights plans, director nomination requirements.
- Annual meeting notice, record date, ISS/Glass Lewis if available.

Must extract:
- Ownership, derivatives, campaign demands, board seats sought.
- Nomination deadlines, annual meeting date, settlement terms.
- Shareholder base and vote math.
- Activist track record and credibility.

### Litigation
Primary sources:
- Complaint, answer, motions, orders, trial calendar, docket entries.
- Settlement agreements, judgments, appellate briefs, damages reports where public.
- Company disclosures on contingencies and risk factors.

Must extract:
- Venue, judge, procedural posture, key motions, trial/appeal dates.
- Damages/remedy theory, injunction risk, settlement path.
- Balance-sheet impact and insurance/indemnity if disclosed.

### Regulatory
Primary sources:
- Agency pages and official calendars.
- Company disclosures, transaction documents, remedy proposals.
- Consent orders, complaints, statements of objections, phase decisions, press releases.

Must extract:
- Which regulator controls the path.
- Filing status, review stage, statutory timeline, likely remedy, political sensitivity.
- Interaction with outside date, financing commitments, and transaction conditions.

### Restructuring and distressed special situations
Primary sources:
- 10-K/Q, debt agreements, indentures, credit agreements, exchange-offer memoranda, RSA, bankruptcy petitions, first-day motions, disclosure statement, plan, court docket.
- Bond/loan prices, CDS, maturity schedules, covenant tests, collateral docs.

Must extract:
- Dated catalyst, court/process status, exchange or RSA terms, next hearing/vote/deadline, security price, payoff assumptions, and source date.
- If claims stack, maturity wall, liquidity, covenant headroom, collateral, guarantees, priority, creditor groups, class votes, DIP, rights offering, backstop, or recovery waterfall are central and not already supplied, route that capital-structure/recovery work to Credit Markets.

## Timestamping rules

Always timestamp:
- Equity price, deal value, spread, annualized return.
- Bond/loan/CDS levels.
- Borrow cost and locate status.
- Options prices and implied volatility.
- Regulatory status and court status.
- Consensus, peer multiples, and market data.

Use wording such as: `Market data timestamp: [date/time/source]. If unavailable, current market math could not be verified.`

## Missing data language

Use direct language:
- `Unverified: merger agreement not reviewed, so termination rights and reverse termination fee are not confirmed.`
- `Assumption: current price supplied by user; no live quote available in this environment.`
- `Judgment: downside uses peer-adjusted unaffected price because the unaffected price appears leak-influenced.`

## Citations and auditability

When the runtime supports citations, cite the source for:
- Deal terms.
- Filing dates and deadlines.
- Regulatory process status.
- Court rulings or docket events.
- Financial metrics, consensus, prices, and valuation data.
- Ownership and vote thresholds.

Do not over-cite generic judgment, but make the factual substrate auditable.

## Index / ETF / Passive Flow Event Sources

Use index methodology docs, official constituent announcements, exchange notices, ETF holdings/rebalance files where available, issuer float/share-count disclosures, short interest/borrow, ADV/liquidity, and timestamped price/volume data. Flow math requires market data timestamps for price, ADV, float, market cap, borrow, options, and ETF/index AUM assumptions.
