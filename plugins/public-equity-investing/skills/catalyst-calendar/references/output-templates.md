# Output Templates

## No-context kickoff
Use when the user asks for a catalyst calendar but provides no universe.

```markdown
## Catalyst Calendar Setup
I can build this, but I need the universe first. Please provide one of:
- Ticker list / portfolio export
- Sector/theme and geography
- Existing watchlist or model workbook
- Timeframe and output format

Default output once provided: full next 30/60/90 day catalyst package, full register or scoped subset, top catalyst table, PM prep plan, source map, and optional Excel/ICS export.
```

## PM summary
```markdown
## Catalyst Calendar - PM Summary
**Scope:** [universe], [timeframe], last refreshed [date/time]
**Highest-priority catalysts:**
1. [Ticker] - [date/window] - [event]: [why it matters] | prep: [action]
2. ...

**Calendar risk:** [same-day clusters, binary events, low-confidence dates, macro overlap]
**Immediate work:** [this week actions]
**Source gaps:** [missing/stale/conflicting sources]
```

## Top catalysts table
| Date / Window | Ticker | Event | Type | Confidence | Importance | What Could Change | Thesis Link | Prep Action |
|---|---:|---|---|---|---:|---|---|---|
| [date/window] | [ticker] | [event] | [type] | [confirmed/guided/inferred] | [1-5] | [estimates/multiple/narrative/risk] | [thesis element] | [owner/action] |

## Single-event brief
Use only when the user explicitly asks for one event, a brief, or a compressed output.

```markdown
## [Ticker] [Event] Brief
**Timing:** [date/window] ([confidence], source: [source/date])
**Setup:** [investor debate and why event matters]
**Market expectation:** [guidance/consensus/buy-side bogey/implied move if available]
**Variant-view relevance:** [what could surprise]
**Confirming evidence:** [thresholds/signals]
**Disconfirming evidence:** [thresholds/signals]
**Prep before event:** [model, questions, checks, calls]
**Post-event action:** [model update, thesis tracker, risk review, note]
**Source caveats:** [conflicts/stale/missing]
```

## Existing calendar refresh log
```markdown
## Refresh Log
**Refreshed:** [date/time]
**Sources checked:** [list]
**Rows added:** [count]
**Rows changed:** [count]
**Rows marked stale/needs refresh:** [count]
**Material changes:**
- [Ticker/Event]: [old date/status/source] -> [new date/status/source], reason [source]
**Do not rely on:** [unconfirmed/stale items]
```

The deterministic workbook helper supports refresh mode with `--prior prior_events.csv --input refreshed_events.csv`. It preserves prior events, updates matched `event_id` rows from refreshed evidence, marks prior rows missing from the refreshed file as `needs refresh`, and writes an append-only `Change Log` tab.

ICS exports are exact-date only. Windowed, guided, street-estimated, or speculative catalysts remain in workbook tables and should not be converted into one-day calendar events.

## Weekly PM prep plan
| Priority | Due | Ticker/Event | Work Product | Owner | Decision It Supports |
|---:|---|---|---|---|---|
| 1 | [date] | [event] | [earnings preview/model sensitivity/question list] | [owner] | [add/trim/hold/hedge/update thesis] |

## Source map
| Event ID | Source | Source Date | Retrieval Date | Confidence | Notes |
|---|---|---|---|---|---|

## Final response when returning a file
```markdown
Built the catalyst calendar and included:
- [workbook/export details]
- [top PM findings]
- [source/freshness caveats]
- [change log / missing data]
Download: [file]
```
