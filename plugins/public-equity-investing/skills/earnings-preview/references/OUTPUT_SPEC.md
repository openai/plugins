# Output Spec

Use this only after `SKILL.md` routes the request.

## Human-Readable Outputs

### Full preview report

Target: default full deliverable for pre-earnings preview requests. For an explicit pre-earnings preview, full preview report, or reusable/source-heavy pre-print package, render a polished standalone HTML report following `../../../shared/html-artifact-standard.md` and the owning skill's HTML guidance. Use `dashboard-builder` only when the standardized dashboard path is explicitly selected. Chat can remain the surface for narrow or explicitly no-file asks. Missing data should create labeled gaps and data requests rather than unsupported conclusions or decorative empty modules.

Required analytical objects:

1. Executive summary: stance into the print, expectation-bar location, stock-reaction debate, and the one thing that would change conviction.
2. Setup/source freeze: ticker/company, quarter, event timing, freeze time, source timestamps, and relevant source gaps.
3. Expectation bar: guide, consensus/whisper where sourced, key operating proof points, what the stock likely requires, and why.
4. Reaction framework: what is already priced in, what could drive an upside or downside reaction, and what evidence is needed before taking incremental event risk.
5. Call watch items and missing evidence: focused questions/listen-fors/falsifiers plus the data refresh required before the print.

Conditional analytical objects: last-quarter recap, guidance-credibility bridge, EPS-quality watch, KPI dashboard, peer/sector or macro read-throughs, market events, reaction/options context, historical move analysis, bull/base/bear scenarios, and expanded call preparation. Include them only where they answer the question or provide source-backed decision support. Present an options-derived metric as an earnings implied move only when its tenor reasonably isolates the event; otherwise label it `expiry-tenor volatility context` and disclose the extra time or catalysts included.

Final checklist: top bar numbers, most decision-relevant operating proofs, upside and downside reaction drivers, key read-through where sourced, historical average move versus an event-isolating implied move only when both are sourced, and the single most important call watch.

### Explicit short summary

Use only when the user explicitly asks for a shorter output such as `summary`, `short`, `quick read`, `one-pager`, or `top things to watch`.

This is a compression of the full preview report, not a separately maintained tear sheet. Preserve:

- Freeze time, source posture, and missing-data caveats.
- 3-5 key bar numbers/KPIs, if sourced.
- 2-3 stock-moving debates.
- 5-8 must-answer call questions with listen-fors.
- Explicit data requests or source limits.

## Table Specs

KPI dashboard columns: `metric`, `t_consensus`, `t_whisper`, `t-1_actual`, `t-4_actual`, `qoq`, `yoy`, `2yr_stack`, `guide_mid`, `vs_guide`, `flag`, `commentary`.

Consensus/whisper columns: `metric`, `period`, `consensus_value`, `whisper_value_or_range`, `delta_abs`, `delta_pct`, `confidence`, `source_timestamp`, `provenance/notes`.

EPS-quality watch columns: `item`, `why_it_could_distort_eps`, `pre_print_risk`, `post_print_evidence_needed`, `model_line_affected`.

Peer read-through columns: `category`, `name`, `signal`, `why_it_matters`, `read_through`, `confidence`.

Historical reaction columns: `quarter`, `beat_miss_context`, `next_day_move`, `driver`, `continued_or_reversed`.

Call-question fields: `question`, `why_it_matters`, `validates_thesis`, `breaks_thesis`, `listen_fors`.

## Deterministic Workbook

Current `scripts/run_plan.py` tabs when inputs exist:

- `Cover`
- `01_PeriodIndex`
- `02_Financials_Q`
- `03_KPIs_Q`
- `04_Guidance_History`
- `05_Consensus_Snapshot`
- `06_Whisper`
- `07_KPI_Dashboard`
- `08_Cons_vs_Whisper`

`Cover` is the first visible dashboard tab. It summarizes company/ticker, preview period, freeze time, workbook mode, warnings, consensus bar, scenario framing, KPI dashboard counts, source/input posture, and workbook map.

Sidecars: `qa_report.json`, `qa_report.md`, `run_manifest.json`. These are support/audit artifacts unless explicitly requested. Do not advertise future tabs until the exporter writes them. Workbook conventions: stable column order, no merged cells, explicit `unit` and `scale`.

## Public Equity PM Output Additions

Include audience mode, expectation bar, what is priced in, estimate-revision risk, positioning/reaction setup, call-question falsifiers, and position action triggers. ETF/index diligence should add constituent weight, passive-flow relevance, liquidity, benchmark exposure, and rebalance/event risk when relevant.
