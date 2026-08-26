# Source, Evidence, and Data-Handling Standards

Use this reference when the request depends on user files, connected apps, current market data, filings, models, portfolios, watchlists, or any factual data that could be stale.

## Source hierarchy

Prefer sources in this order:

1. Prompt-provided context: tickers, constraints, portfolio holdings, watchlists, uploaded tables, models, notes, and user instructions.
2. Callable apps/connectors and internal context the user has authorized: drive/docs, sheets, slides, email, chat, calendar, notebooks, research repositories, callable financial data connectors, or other linked systems.
3. User-uploaded files: spreadsheets, PDFs, models, filings, decks, tearsheets, research notes, and CSV exports.
4. Primary company sources: 10-k, 10-q, 20-f, 6-k, 8-k, earnings releases, transcripts, investor presentations, proxy statements, guidance, and capital allocation announcements.
5. Market and consensus data: prices, volume, market cap, enterprise value, valuation multiples, analyst estimates, revisions, short interest, borrow, ownership, options, equity-risk credit signals such as CDS/spread context, peer data, and benchmark membership.
6. News and external context: regulatory updates, litigation, macro releases, industry reports, supply-chain data, pricing data, web/app data, and other alternative data.
7. User clarification: ask only if the missing context would materially change the answer and cannot be reasonably inferred.

Always label which level of the hierarchy was used. If relying on fallback sources or assumptions, say so.

## Connected-app behavior

When connected apps are available, use them before public web search if the user's request implies private or firm-specific context. Examples:

- Existing portfolio, watchlist, restrictions, or benchmark exposures.
- Internal research notes, prior thesis trackers, PM comments, model outputs, or idea logs.
- Firm style, templates, prior memos, and sector coverage conventions.
- Meeting notes, earnings call notes, diligence questions, or analyst feedback.

Do not assume connected-app context is complete. If an app search returns nothing, state the gap and continue with available public/user-provided data.

## Current data and web fallback

Use current web or market-data tools whenever facts may have changed, including:

- Prices, market caps, volume, valuation multiples, estimates, and revisions.
- Earnings dates, conference appearances, regulatory decisions, litigation milestones, index changes, and corporate actions.
- Management changes, guidance updates, filings, financing events, debt maturities, buybacks, dividends, M&A, and activism.
- Laws, regulations, sanctions, tariffs, central bank decisions, macro data, commodity prices, rates, FX, and sector news.

If current market data is not available, provide a methodological output with placeholders and clearly say which metrics must be populated before ranking can be relied upon.

## Non-destructive handling

Never delete, overwrite, or destructively edit user data unless the user explicitly requests it. For files and spreadsheets:

- Preserve the original file.
- Create a copy, new tab, new output file, or appended section for generated screens.
- Keep raw source data separate from cleaned, normalized, and output tabs.
- Add data-quality flags rather than silently fixing source issues.
- Do not remove rows, names, formulas, tabs, comments, or prior workpapers unless specifically instructed.
- If cleaning is required, route to or follow `excel-data-cleaner` / `financials-normalizer` style handling before analysis.

## Evidence labels

Use these labels or equivalents:

- Fact: directly sourced or provided.
- Assumption: inferred because the user did not specify.
- Estimate: derived from a model, consensus, or calculation.
- Inference: analytical conclusion based on facts and assumptions.
- Data gap: unavailable, stale, inconsistent, or incomplete.
- PM judgment: qualitative conclusion that reflects professional interpretation.

## Stale-data checks

Before relying on a metric, check:

- Date of source.
- Reporting period and fiscal year.
- Whether consensus is before or after the latest print.
- Whether company guidance has changed.
- Whether capital structure changed through debt issuance, buyback, equity issuance, M&A, spin, or divestiture.
- Whether prices and market caps are current.
- Whether estimates are calendarized or fiscal-year based.
- Whether the metric uses adjusted or GAAP/IFRS definitions.
- Whether reported financials are pro forma for recent acquisitions or divestitures.

Flag stale data in the output rather than smoothing it over.

## Public-equity data normalization checks

Normalize or flag:

- Ticker changes, share classes, dual listings, ADR ratios, depositary receipts, and local vs U.S. lines.
- Currency and reporting currency.
- Fiscal year ends and calendar-year mismatches.
- Enterprise value components, including cash, debt, leases, pensions, minority interests, preferred stock, and unconsolidated investments.
- Sector-specific metric definitions: e.g. ebitda is not meaningful for banks; affo matters for reits; fcf at strip matters for energy.
- One-time items, adjusted ebitda add-backs, stock-based compensation, restructuring charges, working capital swings, tax rates, and non-cash gains/losses.
- Recently IPO'd companies, spin-offs, restatements, discontinued operations, and post-merger financials.

## Citation discipline

Cite retrieved facts and current market data. Do not cite unsupported calculations as if sourced; cite the inputs and explain the calculation. If source confidence is low, explicitly say so.

## Investment framing

Use research language rather than trade instructions:

- Good: "candidate for further work," "possible revision-inflection long," "watchlist pending catalyst," "short-screen flag requiring borrow check."
- Avoid: "buy this," "sell this," "guaranteed upside," or personalized portfolio instruction without appropriate context.

## Public Equity Source QC

Label facts, management claims, consensus, market data, assumptions, and PM judgment. Price, consensus, short interest, borrow, options, ETF holdings, index rules, liquidity, and ownership require as-of dates.
