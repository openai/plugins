# Earnings Preview Execution Playbook

Use this reference for detailed mechanics after `SKILL.md` has routed the request.

## Quarter Anchoring

- Identify latest reported quarter and upcoming preview quarter.
- Map `t`, `t-1`, `t-4`, and `t-8` to exact fiscal periods.
- Use the same `t` across consensus, guidance, KPI history, options, reaction analysis, and scenarios.
- If the preview quarter is ambiguous, ask for the period before presenting precise tables.

## Core Formulas

- Level metric QoQ: `(x_t / x_t-1) - 1`.
- Level metric YoY: `(x_t / x_t-4) - 1`.
- Level metric two-year stack: `(x_t / x_t-8) - 1`.
- Rate metric changes: use percentage-point or bps deltas, not percent growth.
- Surprise: `reported - consensus`; for level metrics, `(reported / consensus) - 1`.
- Guidance midpoint: `(low + high) / 2`.
- Options implied move from straddle: `straddle price / spot`.
- Options implied move from IV: `iv * sqrt(dte / 365)`.

Suppress percentage changes when the denominator is zero, negative, structurally unstable, or definitionally mismatched.

## Whisper Framing

- External whisper: show value/range, provenance, timestamp, and confidence.
- No external whisper but guidance history exists: infer only a labeled analyst-derived implied whisper from guide midpoint, historical beat pattern, and conservatism trend.
- Weak support: use soft setup language, not a hard estimate.
- Never blend whisper and consensus without explaining the bridge.

## Memo Modules

Use the full module set by default. If an input is unavailable, keep the section and state the missing evidence rather than silently shrinking the report. Only compress the module set when the user explicitly asks for a summary, short version, one-pager, quick read, or top-things-to-watch note.

- Executive summary: stance into the print, bar location, key cruxes, and conviction-changing evidence.
- Last quarter recap: beat/miss, narrative, stock reaction, debated KPI, still-relevant issue.
- Outstanding guidance: metric, value/wording, source quarter, type, note.
- Guidance credibility: beat rate, beat size, conservatism trend, and data limits.
- Expectation bar: Street, whisper, prior guide, base framing, and bar location.
- KPI dashboard: 3 to 6 KPIs that actually set the quarter.
- Peer read-throughs: competitor, supplier, customer, and bellwether signals.
- Bull/base/bear: explicit drivers, expected print, reaction, and falsifiers.
- Call questions: why it matters, validate, break, and listen-fors.
- Historical reaction: next-day move, driver, and continued/reversed.
- Macro/sector backdrop: short positive/negative/uncertain bullets only.
- Final checklist: top bar numbers, top 3 metrics, bull catalyst, bear risk, read-through, move comparison, and single call watch.

## Deterministic Script Mode

The shipped scripts are local materializers. They read CSV inputs, validate schema, render a markdown preview note, export CSV/XLSX support tables, and write a run manifest. They do not fetch data, infer current earnings dates, or replace analyst judgment.

Canonical event file name: `event_calendar.csv`.

Required scripted inputs:
- `company_master.csv`
- `fiscal_period_index.csv`
- `reported_financials.csv`
- `kpi_timeseries.csv`
- `consensus_estimates.csv`

Optional scripted inputs:
- `guidance_history.csv`
- `event_calendar.csv`
- `whisper_estimates.csv`
- `price_returns.csv`
- `options_snapshot.csv`
- `qual_notes.csv`
- `scenario_assumptions.csv`

If deterministic outputs contain unresolved bracket tokens, `TODO`, or unfinished placeholders, treat the run as failed.

## PM Setup Rubric

Answer whether the bar is beatable, whether it matters, and what would change sizing into or after the print. Cover expectation bar, consensus dispersion, guidance bridge, implied move, buyside whisper if sourced, positioning, estimate-revision risk, catalyst asymmetry, and call-question falsifiers.

Consensus, options, ownership, short interest, and positioning require as-of dates and source labels. If unavailable, mark them as missing evidence rather than inferring.
