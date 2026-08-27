# Public Equity Investing Invocation Policy

## Entry Gate

Activate this plugin only when at least one of these conditions is satisfied:

1. **Explicit invocation.** The user tags or names Public Equity Investing,
   uses `@public-equity-investing`, supplies its plugin link, or explicitly invokes one of its skills.
2. **Public-equity investor context.** The prompt asks for listed-company or public-security research, earnings analysis, valuation, model updates, long/short pitches, catalysts, thesis tracking, ETF/index or constituent diligence, position sizing, hedging, dashboards, investment memos, or portfolio work through an investor lens.

When a prompt lacks public-equity investment context, do not activate this plugin. A public company name, share-price reference, model, deck, report, or document request does not on its own pass the gate.

## High-Intent Signals

The untagged prompt should tie a listed issuer, ticker, equity position, sector, portfolio position, event, earnings setup, investment thesis, or public security to a public-equity workflow, such as:

- an earnings preview/deep dive, public-equity investment thesis, initiation,
  long/short pitch, catalyst calendar, or thesis tracker;
- a common-equity DCF/comps/model update, price-target debate, risk sizing,
  hedge view, or add/trim/exit decision;
- listed-equity event, ETF/index constituent, or benchmark-relative equity diligence for an investment team.

## Non-Triggers

Do not invoke Public Equity Investing automatically for private-company diligence, credit-first analysis, personal financial advice, generic company summaries, or generic document drafting with no public-equity investment context. Generic requests to research a company, explain a share-price move, create a report or document, build a model, value a business, summarize earnings, clean a workbook, or prepare a meeting brief need an investor lens such as what is priced in, what is mispriced, what proves or kills the thesis, what to watch next, or how it affects a position.

## After Activation

Once this gate is met, use `final-deliverable-framework.md` to select the owning workflow and `deliverable-intake-policy.md` before a new substantive human-facing artifact begins. Support and presentation skills inherit this activation decision rather than extending the implicit scope.
