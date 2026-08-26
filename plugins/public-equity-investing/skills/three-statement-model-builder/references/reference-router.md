# Three Statement Reference Router

Load the narrowest reference needed for the current task. Keep the invoke path in `SKILL.md` compact; use these deferred docs for model nuance, implementation details, and senior review standards.

## Default Formula Workbook Contract

- `plan-schema.md`: input schema, source-basis requirements, examples, and decision-grade requirements.
- `output-spec.md`: required artifacts, workbook sheets, `run_log.json`, `manifest.json`, report template, and P0 handoff shape.
- `qa-checks.md`: hard failures, warnings, tie-out rules, status logic, and senior-review red flags.
- `banker-formula-workbook-contract.md`: default formula workbook mode, required sheets, inspection gate, truthfulness rules, and `model_citations.json` source-to-cell handoff.

## Operating Model Mechanics

- `model-math.md`: IS/BS/CF formulas, line-item logic, cash sweep, working capital, PP&E, debt, and retained earnings mechanics.
- `model-architecture.md`: preserved workbook architecture, tab structure, formula conventions, scenario layout, and formatting standards.
- `forecast-judgment-guide.md`: CFO/PM-grade assumption logic, scenario design, unit economics, margin, capex, cash conversion, and pressure tests.

## Controls And Review

- `integrity-controls.md`: formula controls, sign conventions, model checks, stress tests, and sign-off procedures.
- `output-and-review.md`: executive summary, circulation standard, caveats, diligence asks, and model-readiness communication.

## Industry Adaptation

- `industry-playbooks.md`: company-type and revenue-model adaptations for SaaS, consumer, industrial, energy, banks, insurers, REITs, biotech, and other public-company contexts.

## Integrations

- `p0-integrations.md`: coordination with Public Equity Investing and shared-core skills, including model update, DCF, comps, scenario, memo, and audit handoffs.

## Loading Rule

Do not load all references by default. Start with formula workbook contract docs for user-facing model builds, deterministic support docs for implementation or QA issues, operating mechanics for model construction questions, and judgment/review docs only when the user needs full diligence-quality reasoning.
