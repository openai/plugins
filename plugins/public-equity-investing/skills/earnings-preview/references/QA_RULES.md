# QA Rules

Use before returning a human-readable report or packaging deterministic outputs.

## Hard Fails

- Fabricated number/date/source, unlabeled web fallback, or unlabeled analyst assumption.
- Missing freeze time for time-sensitive market, consensus, whisper, option, or price data.
- Mixed GAAP/non-GAAP, period, unit, scale, or KPI definition without labeling.
- A chart axis or displayed scale that conflicts with the stated unit in adjacent tables, headings, or narrative.
- An options-derived metric labeled as an earnings implied move when the cited expiry includes substantial pre-event trading time or another material catalyst window without a prominent `expiry-tenor volatility context` qualification.
- Whisper presented as consensus or implied MNPI/confidential information.
- Generated user-facing report/dashboard text, or any generated support note, contains unresolved `[TOKEN]`, `{PLACEHOLDER}`, `TODO`, or unfinished authoring text.
- Scripted pack writes outputs into the packaged skill tree instead of the requested/temp output directory.

## Human-Readable Report QA

Confirm:

- Preview quarter and `t/t-1/t-4/t-8` mapping are explicit.
- Every bar number has source/as-of, unit, scale, and definition.
- Guidance is separated from consensus/whisper and labeled by period/scope/basis.
- EPS-quality watch is included when EPS matters: consensus basis, tax/share-count, below-the-line, mark-to-market, or one-time item risk.
- Peer, macro, reaction, and options sections appear only when sourced or are marked missing.
- Options-derived volatility is labeled as an earnings implied move only when the tenor reasonably isolates the event; broader expiries are labeled `expiry-tenor volatility context` and are not treated as a clean earnings hurdle.
- Bull/base/bear cases state drivers, assumptions, and falsifiers.
- Call questions include why they matter and listen-fors.
- Missing evidence is visible rather than hidden.
- HTML hierarchy makes the expectation bar and stock-reaction debate immediately visible for a full preview report.
- Citations are traceable without fragmenting readable dates, times, ticker symbols, product names, or product specifications.

## Deterministic QA

Run plan validation before `run_plan.py`. Check required files, required columns, output manifest, workbook tabs listed in `OUTPUT_SPEC.md`, `qa_report.*`, and generated report/support-note placeholder scans.

Accept `PASS_WITH_WARNINGS` only when warnings are limitations, not broken calculations or unresolved placeholders.

## PM Judgment QA

Fail the output if it lacks freeze time, expectation bar, stock-moving debate, source labels for consensus/options/positioning, or falsifier/listen-for questions. Penalize generic earnings summaries that do not say what would change sizing or watchlist status.
