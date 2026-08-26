# Output Modes

## Deterministic File Mode

Use when the user supplies local `plan.json`, normalized CSVs, or asks to run scripts.

- Run `validate_plan.py` and `validate_normalized_inputs.py` before `run_plan.py`.
- Treat generated Markdown as a support note or renderer input unless the user explicitly requests Markdown. Unresolved bracket tokens, `TODO`, or authoring placeholders are hard failures.
- `MISSING` is allowed in input templates/staging files; generated reports should prefer `not guided`, `not disclosed`, `not provided`, or `source not provided`.
- Disclose whether model update ran as `packet` or workbook `apply`. Fall back to packet if apply is unsafe.

## One-Page Tear Sheet

Use only when the user explicitly asks for a summary, one-pager, quick read, brief, or TL;DR. Target 700-1,100 words unless asked otherwise. Order: setup, PM bottom line, beat/miss, guidance delta, 2-3 drivers, high-signal quotes, model/thesis impact, watch list/source limits. Include revision/stock skew for investment-decision prompts.

## Full Deep Dive

This is the default analytical post-print deliverable. Include setup/source posture, executive summary, what changed, revision/stock setup, beat/miss, EPS quality screen, guidance delta, drivers, transcript evidence and debate map when available, model impact, watch list, falsifiers/next checks, and missing data/open questions. Move raw source detail to a compact appendix. For an explicit deep dive, full report, or reusable/source-heavy artifact, render a polished standalone HTML report following `../../../shared/html-artifact-standard.md` rather than treating Markdown as the final file.

```markdown
## Setup
Ticker/quarter/event; sources used; estimate set as-of; next catalyst.

## Executive summary
- ...

## What changed / PM bottom line
| Item | Prior/bar | New | Implication |
|---|---|---|---|

## Revision / stock setup
| Lens | Read-through |
|---|---|
| Thesis change | |
| Likely estimate revision | |
| Stock / valuation skew | |

## Beat / miss vs expectations
| Metric | Reported | Consensus | Delta | Surprise % | Internal | Delta | Source |
|---|---:|---:|---:|---:|---:|---:|---|

## EPS quality screen
| Check | Status | Read-through | Source |
|---|---|---|---|
| GAAP EPS vs operating / adjusted EPS | expanded bridge required / no material trigger / source not provided | | |
| Below-the-line, tax, mark-to-market, share-count, or non-recurring items | | | |

Expand this into a full ex-gain / recurring EPS bridge when triggered. If no trigger is identified, state the conclusion and keep moving.

## Guidance delta
| Metric | Period | Low | High | Mid | Consensus | Delta(mid) | Internal | Delta(mid) | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|

## Transcript quote / Q&A map
| Topic | Questioner | Firm | Answering executive | Section | Quote / paraphrase | Why it matters | Bull / bear implication | Falsifier / next check | Source |
|---|---|---|---|---|---|---|---|---|---|

If no transcript is available, replace this table with a concise evidence-gap callout labelled `transcript not provided` or `transcript source not found`; do not invent questions, speakers, firms, or quotes.

## Debate map
Bull case, bear case, what changed this quarter, and falsifiers tied to the next catalyst.

## Drivers, model impact, watch list, falsifiers, missing data
```

## Audit-Ready Model Update

Use only when the user supplies or references a model/workbook, driver registry, output registry, normalized CSVs, model-update inputs, or explicit data to update a model. Separate reported actual, company-guided, analyst-derived, and not-provided lines. Show formula/assumption and confidence for analyst-derived proxies. Prioritize next-quarter/full-year revenue, margin/profit, EPS, and FCF. Separate GAAP EPS, adjusted/operating EPS, and recurring EPS drivers before updating forward EPS estimates. If EBITDA is derived from operating-profit guidance, show the operating-profit anchor first.

## HTML Full Deep Dive

Use flexible standalone HTML for explicit full post-earnings deep dives and reusable/source-heavy post-print reports. The opening view should contain the verdict, 4-6 decision-relevant metrics, one decision box, and the bridge from reported print to recurring investment evidence. Add transcript, scenario, read-through, market-event, or chart sections only when their contents are substantive and source-supported; omit empty modules.

## Standardized Dashboard

Use `DASHBOARD_PACK.md` and `dashboard-builder` only when the user explicitly requests the standardized dashboard, a reusable dashboard template, or a structured payload-driven render.

## Quote and Debate Map

Standalone mode is only for quote/debate-only requests. In a full deep dive, include this as a required section. Use 6-8 complete, non-fragmentary quotes or concise compliant excerpts when transcript access allows. For each: topic, questioner name, firm if available, answering executive, section, quote or paraphrase, source tag, why it matters, bull/bear implication, and falsifier/next check. Tie falsifiers to the next real catalyst or reporting cadence.

## Common Failure Modes

- Mixed GAAP/non-GAAP, reported/CC, units, periods, or estimate definitions.
- Treating a one-time or below-the-line EPS beat as recurring operating earnings.
- Transcript cited for a filed GAAP number.
- Surprise percent against near-zero expectations.
- Numeric range invented from qualitative guidance.
- `MISSING` used in final copy where a precise absence label is better.
- No source tag on a number or quote.
- Investment prompt missing thesis/revision/stock skew.
- Quotes clipped so tightly they lose meaning.
