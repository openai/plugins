# Citations — every assertion links to ground truth

The single most valuable property of the work product: a reader can click and verify in
seconds. Formats are **defined by the Midpage MCP tools** — use the tool output verbatim,
never construct citations from memory.

**The non-negotiable:** never assert a rule, holding, quote, or record fact without a link to
its source, and never recall a citation from memory. Citations come from a tool call *this
session* (`analyzeOpinion`, `analyzeDocketFiling`) or, for court rules, from the page actually
retrieved. No fabricated case, quote, pin cite, statute, or rule, ever — if a tool can't
verify it, say so rather than filling the gap. An unsourced citation is worse than none — it
invites misplaced reliance.

## Case law (from `analyzeOpinion`)

- A specific proposition or quote → `[{citation}]({deeplinkURL})`; the case generally →
  `[{citation}]({url})`.
- Use the **exact** Bluebook string the tool returns — never abbreviate or modify it.
- No short cites (`id.`, `supra`) — always the full linked citation. Never WL or LEXIS (use
  the reporter citation or the docket-number citation the tool returns for unpublished cases).
- Never invent a pin cite; the `deeplinkURL` is the line-specific link.
- Add a parenthetical (often an `-ing` phrase or short quote) where it helps.

## Docket filings (from `analyzeDocketFiling`)

- Hyperlink to `filing.url`. Format: descriptive name, any real page/paragraph pin, then
  `ECF No. {entryNumber} ({dateFiled} as "Mar. 3, 2020")` — e.g.
  `[Pl.'s Mot. for Summ. J. 5, ECF No. 30 (Mar. 3, 2020)](https://app.midpage.ai/…)`.
- The ECF No. suffix is required. If `dateFiled` is unavailable, omit the date — don't invent
  one. No short cites; repeat the full linked citation.

## Court rules and web sources

- Hyperlink the exact official page or PDF you retrieved (court `.uscourts.gov` site,
  judiciary portal, Cornell LII for federal rules when no official link exists). Name the rule
  precisely ("Local Civil Rule 7.1(c)"), state the requirement in one sentence, link it.
- If a source genuinely cannot be linked, show a screenshot of the governing language rather
  than asserting the rule unsupported.

## In every medium

Word links render blue and underlined (the renderer handles it); on the web (e.g. a blog
post), links are real hyperlinks. Write real Unicode punctuation in all strings (' " " — § ¶),
never HTML entities.
