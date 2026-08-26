# Reference Router

Load only what the request requires.

| Need | Load |
|---|---|
| Chat-native report contract and source pack | `CHAT_REPORT_CONTRACT.md` |
| Output shape/template | `OUTPUT_MODES.md` |
| Full operating mechanics | `PLAYBOOK.md` |
| Scripted plan/CSV/model contracts | `SCHEMAS.md`, `SCRIPT_QUICKSTART.md` |
| Source tags and absence labels | `SOURCE_TAGGING.md`, `QUALITY_CHECKS.md` |
| Metrics and sector KPIs | `METRIC_CATALOG.md` |
| EPS quality / ex-gain bridge | `PLAYBOOK.md`, `METRIC_CATALOG.md`, `QUALITY_CHECKS.md` |
| Model diff/update detail | `MODEL_DIFF_GUIDE.md` |
| Examples | `EXAMPLES.md` |
| Polished HTML full deep dive | `../../../shared/html-artifact-standard.md`, `CHAT_REPORT_CONTRACT.md`, `OUTPUT_MODES.md`, then `QUALITY_CHECKS.md` |
| Explicit standardized dashboard | `DASHBOARD_PACK.md`, then `QUALITY_CHECKS.md` |

Fast route:

- Default post-print requests route to full deep dive and usually need `CHAT_REPORT_CONTRACT.md`, `PLAYBOOK.md`, `OUTPUT_MODES.md`, and `METRIC_CATALOG.md`.
- One-page tear sheet is only for explicit summary/one-pager/quick/brief/TL;DR requests and usually needs `CHAT_REPORT_CONTRACT.md`, `OUTPUT_MODES.md`, and `QUALITY_CHECKS.md`.
- Audit-ready model update is only for user-supplied or referenced model/model-update inputs and usually needs `MODEL_DIFF_GUIDE.md`, `SCHEMAS.md`, and `SCRIPT_QUICKSTART.md`.
- Deterministic mode always needs `SCHEMAS.md`, `SCRIPT_QUICKSTART.md`, and QA checks.
- An explicit deep dive, full report, or reusable/source-heavy package defaults to polished standalone HTML.
- Standardized dashboard output keeps `earnings-deep-dive` as the analysis owner and uses `dashboard-builder` only when explicitly selected.
