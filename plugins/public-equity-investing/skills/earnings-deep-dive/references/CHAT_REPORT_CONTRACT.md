# Chat Report Contract

Use this reference after `earnings-deep-dive` is selected for the analysis and evidence contract of a chat-native response or polished standalone HTML report. For explicit standardized dashboards, additionally use `DASHBOARD_PACK.md` and `dashboard-builder`; do not make Markdown the final deliverable for substantive reusable artifacts.

## Non-Negotiables

- Never invent numbers, quotes, guidance, definitions, accounting facts, or estimate timestamps.
- Every reported number and every quote must carry a source tag. Analyst-derived numbers must show formula or assumption.
- Source precedence: `10-Q/10-K` -> `8-K / Exhibit 99.1` -> `Earnings PR` -> `Deck / Prepared Remarks` -> `Transcript`.
- Treat transcripts as narrative support, not the primary numeric source; cross-check transcript numbers against authoritative tables when possible.
- For non-GAAP metrics, show the closest GAAP comparable and reconciliation source.
- Keep GAAP/non-GAAP, reported/constant-currency, basic/diluted, percent/bps, and company-guided/analyst-derived distinctions explicit.
- Run an EPS quality screen before interpreting EPS surprise. Show a full ex-gain / recurring EPS bridge when GAAP EPS is distorted by below-the-line, tax, mark-to-market, equity-investment, FX, restructuring, litigation, asset-sale, impairment, share-count, or other non-recurring items.
- Use precise absence labels: `not guided`, `not disclosed`, `not provided`, `source not provided`, or `MISSING: <dependency>`.
- Anchor falsifiers to the next real catalyst window. Do not invent arbitrary dates.
- Do not edit workbooks, send messages, publish, or take external actions unless the user explicitly asks and approves.

## Inputs

Minimum:

- company or ticker;
- fiscal quarter, period, or enough context to identify the latest reported quarter.

Helpful:

- earnings PR, SEC filing, deck/prepared remarks, transcript;
- consensus or internal estimates with `AsOf`;
- prior-quarter tear sheet, prior guide, or prior model;
- driver registry, output registry, or model-update plan.

If critical information is missing, ask up to 5 targeted questions only when the missing data blocks the core task. Otherwise proceed with available connected/public sources and label source limitations.

## Source Pack

Use the evidence pack that supports the selected artifact without shrinking the user-facing analysis.

- Full deep dive: release or filing, deck/prepared remarks, transcript, estimates, prior-quarter or prior-guide source where available.
- Explicit summary or one-page tear sheet: release or 8-K, deck if available, estimate source, transcript only for 2-4 high-signal quotes.
- Audit-ready model update: release or 8-K, deck, prior guidance, estimate set, and user-supplied or referenced model inputs.
- Standalone quote/debate map: transcript plus release/deck for numeric cross-checks.

If user artifacts are absent, prefer official IR and SEC materials, then reputable transcript/consensus providers, then clearly labeled web fallback. Freeze and disclose the estimate set `AsOf`; if unavailable, say `estimate timestamp not provided`.

## Default Output Contract

Unless the user explicitly asks for a summary/one-pager/brief/quick read or a narrower artifact, default to a full deep dive in the selected presentation surface. Explicit full or reusable/source-heavy post-earnings reports default to polished standalone HTML under the skill's intake rule. Every full deep dive should include:

- setup: ticker, quarter, event timing if known, artifacts used, estimate set as-of or limitation;
- bottom line on whether the quarter changes the investment case;
- beat/miss or guide-versus-bar analysis when estimates are available;
- EPS quality screen, expanded into an ex-gain / recurring EPS bridge when headline EPS is materially distorted or the estimate basis is mismatched;
- prior-versus-new guidance or narrative change when relevant;
- 2 to 3 load-bearing drivers;
- transcript quote/Q&A map, when transcript evidence is available, with questioner name, firm if available, answering executive, topic, source tag, why it matters, bull/bear implication, and next-check/falsifier;
- debate map that separates bull case, bear case, what changed, and what would falsify each side;
- model or thesis impact, including stock-reaction or valuation relevance when decision-useful;
- watch list or falsifiers with measurable items where possible;
- source limitations, open questions, and confidence notes.

If the transcript is unavailable, include a concise visible evidence limitation labelled `transcript not provided` or `transcript source not found` and name the missing artifact. Do not create an empty Q&A table or shorten the rest of the report solely because the transcript is missing.

Use a one-page tear sheet only when the user explicitly asks for a summary, one-pager, quick read, brief, or TL;DR.

Use audit-ready model update mode only when the user supplies or references a model/workbook, driver registry, output registry, normalized CSVs, model-update inputs, or explicit data to update the model. A normal full deep dive may include model/thesis impact, but should not imply a deterministic model update happened without model inputs.

For investor-facing prompts, include a compact decision box:

- `Thesis change`: strengthened, weakened, unchanged, or mixed;
- `Likely estimate revision`: revenue, EPS/margin, FCF, and timing;
- `Stock / valuation skew`: upside/downside, multiple support, or risk premium;
- `Next catalyst`: next earnings, guidance update, investor day, KPI event, or not found.

## Final QA

Before finishing, verify:

- every number and quote has a source tag;
- estimate set `AsOf` is shown or explicitly unavailable;
- EPS surprise has been screened for non-recurring, below-the-line, tax, mark-to-market, share-count, or estimate-basis distortion;
- guidance period, midpoint, and GAAP/non-GAAP basis are clear;
- unavailable values use precise labels, not avoidable `MISSING`;
- company guidance is separate from analyst-derived assumptions;
- surprise percentages are not computed against zero or near-zero estimates;
- transcript points, when available, identify questioner name, firm if available, answering executive, speaker, and section;
- a full deep dive includes substantiated transcript/Q&A evidence or a precise transcript-absence callout, plus a debate-map treatment;
- falsifiers/watch-list items are tied to a real catalyst or reporting cadence;
- output length matches the requested mode.

## PM Bottom Line Contract

Every substantial post-print report should say whether the quarter changed the business thesis, stock thesis, estimate path, valuation support, or sizing. Include quality-of-beat/miss, revision bridge, next catalyst, source caveats, and action discipline.
