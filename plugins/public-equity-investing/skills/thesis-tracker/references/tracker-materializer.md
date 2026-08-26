# Tracker Materializer

Run `scripts/materialize_thesis_tracker.py` to create a new local CSV bundle, with optional XLSX packaging when `openpyxl` is installed. The helper scaffolds artifacts; it does not decide thesis status, provide final presentation formatting, or edit existing trackers in place.

```bash
python scripts/materialize_thesis_tracker.py [tracker_input.json] --output-dir output
```

Input JSON top-level keys are optional: `dashboard`, `thesis_pillars`, `evidence_ledger`, `kpi_tracker`, `catalyst_calendar`, `estimate_revisions`, `model_changelog`, `decision_log`, `sources`, `open_questions`.

Outputs: one CSV per table, `run_log.json`, and `manifest.json`; XLSX is best-effort if dependencies exist. Optional XLSX packages start with `Cover`, a senior-review dashboard summarizing thesis status, conviction/rating, valuation frame, next catalyst, action recommendation, evidence density, source/open-question counts, and workbook map. Use a new output directory/file for updates unless the user explicitly authorizes overwriting a workbook.

For a final tracker-update deliverable, use the XLSX workbook as the hero artifact when available and ensure its `Cover` distinguishes company-thesis status from security-thesis readiness and position action. Refine generated workbook layouts as needed so first-read tabs are compact and decision-facing; move detailed evidence into audit tabs. Summarize action-rule posture and top decision blockers on `Cover`, while keeping full action-rule and diligence/gap registers on dedicated tabs. Render and inspect every final workbook tab before delivery, and do not add numeric score charts unless a scoring method is inherited or explicitly requested.
