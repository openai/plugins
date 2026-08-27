---
name: excel-data-cleaner
description: Use when cleaning messy public-equity-investing tables for CSV/XLSX/model inputs. Do not use for unrelated corporate cleanup.
---

# Excel Data Cleaner

> Internal support playbook. Load through `internal-support/policy.md`; this data-cleaning capability is bundled with the visible router rather than exposed as a skill entrypoint.

## Deliverable Intake

When invoked as support for an owning workflow, inherit its resolved deliverable preferences and do not re-prompt. Only when this skill independently owns a new substantive standalone cleanup deliverable should it, before source gathering, analysis, or rendering, load `../../../../shared/deliverable-intake-policy.md` and perform its adaptive `request_user_input` preflight for materially unresolved preferences.

## Purpose

Load `shared/equity-research-support-standard.md` and `shared/support-layer-routing-contract.md` before substantial source, data, QA, or style work.

Clean messy Public Equity Investing tables into analyst-grade CSV/XLSX/model inputs. Preserve decision-critical detail, trace transformations, and produce outputs an equity research, event-driven, ETF/index, portfolio/risk, or PM analyst can inspect.

Use for public-company financials, earnings tables, market/security data, portfolio/risk, ETF/index, security master, consensus/provider exports, and event-driven datasets. Do not use for corporate FP&A cleanup, GL reconciliation, private-company QoE, formula audit, or Credit Markets instrument analysis. If the table is clearly bonds, loans, CDS, covenants, recovery, restructuring, or debt-security selection, route to Credit Markets after preserving the source posture.

## Embedded Support Routing

This is an embedded service under an owning workflow unless the user explicitly asks for standalone table/workbook cleanup. Preserve the `owning_workflow` internally, such as `financials-normalizer`, `equity-model-update`, `dcf-model-builder`, `three-statement-model-builder`, `comps-valuation`, `portfolio-risk-management`, `event-driven-analyzer`, `thesis-tracker`, `meeting-prep`, or `dashboard-builder`.

For substantial embedded work, preserve `decision_impact`, `readiness_effect`, `artifact_role`, and `hidden_unless_requested` in internal context or support artifacts. Do not print those internal field names in the owning workflow's user-facing artifact. Do not own the investment conclusion; state in natural language how duplicate rows, malformed fiscal periods, stale timestamps, broken identifiers, missing units, or ambiguous table grain changes model readiness, dashboard reliability, valuation support, sizing confidence, or circulation readiness. Cleaned workbooks, CSV, JSON, profiles, logs, and manifests are secondary/support artifacts when invoked by an owning workflow.

## Reference Router
- `cleaning-standards.md`: transformation policy and destructive-decision guardrails.
- `domain-playbook.md`: domain keys, validations, units, and formatting.
- `workbook-output-spec.md`: workbook tabs, formatting, and QA.
- `examples.md`: common messy-data patterns.
- `profile_tabular_data.py`: profile CSV/XLSX/XLS before editing.
- `clean_tabular_data.py`: deterministic first-pass cleaner/workbook materializer.

## Rules
- User instructions win unless they would destroy integrity.
- Preserve raw data, IDs, timestamps, units, currencies, fiscal labels, notes, sources, and exceptions.
- Infer row grain before cleaning: issuer metric, security, instrument, position, estimate, event, period, line item, or source record.
- Do not invent values, mappings, categories, signs, currencies, or formulas.
- Log assumptions, transformations, dropped rows/columns, duplicate decisions, and parsing uncertainty.
- Ask before fuzzy merges, conflicting duplicate merges, source overwrites, or business-critical imputations.

## Workflow
1. Classify objective, domain, grain, must-preserve fields, output type, and destructive choices.
2. For non-trivial files, profile first:

```bash
python scripts/profile_tabular_data.py input.xlsx --output profile.json
```

3. Define a cleaning spec: headers, type conversions, duplicate policy, missing-value policy, category mapping, validations, assumptions.
4. Clean conservatively: remove only clear structural noise, standardize headers, parse obvious types, preserve IDs as text, and flag uncertain duplicates/outliers.
5. For deterministic first pass:

```bash
python scripts/clean_tabular_data.py input.xlsx --output cleaned.xlsx --domain auto --dedupe exact
```

6. Review and refine with analyst judgment; the script is a helper, not a substitute for review.

## Dependencies
Scripts require `pandas`, `openpyxl`, and `xlrd` from `scripts/requirements.txt`. They lazy-load after argparse, so `--help` works without installs. If packages are missing, install requirements or disclose that deterministic cleaning could not run.

## Output Contract
Default workbook tabs: `Cover`, `clean_data`, `raw_source`, `summary`, `data_dictionary`, `quality_checks`, `assumptions_audit`.

The `Cover` tab is the first-tab dashboard: input file, workbook mode, sheet/row/column counts, inferred domain/grain where available, quality issue counts, fatal/warning count, cleaning policies, raw-source preservation, workbook map, and downstream-use limitations.

Domain lenses: issuer financials, markets/security data, portfolio/risk, ETF/index data, consensus/provider exports, and event-driven data. Preserve the identifiers, periods, units, source timestamps, and metric definitions that make each domain auditable. Credit tables may be profiled only as `credit_markets_handoff` / equity-risk signal support.

Final response: what changed, what was preserved, high/medium/low issues, user-directed vs inferred assumptions, and deliverable path or cleaned table.
