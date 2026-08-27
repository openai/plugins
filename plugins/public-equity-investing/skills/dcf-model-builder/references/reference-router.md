# DCF Reference Router

Load the narrowest reference needed for the current task. Keep the invoke path in `SKILL.md` compact; use these deferred docs for model nuance, implementation details, and senior review standards.

## Default Formula Workbook Contract

- `plan-schema.md`: input schema, required fields, source-basis expectations, and decision-grade requirements.
- `output-spec.md`: generated artifacts, workbook sheets, `run_log.json`, `manifest.json`, report template, and P0 handoff shape.
- `qa-checks.md`: hard failures, warnings, senior-review red flags, and status downgrade logic.
- `banker-formula-workbook-contract.md`: default formula workbook mode, required sheets, inspection gate, truthfulness rules, and `model_citations.json` source-to-cell handoff.

## Valuation Mechanics

- `model-math.md`: DCF formulas, valuation bridge mechanics, and economic coherence checks.
- `cash-flow-methods.md`: FCFF, FCFE, DDM, financial-institution, and special-situation method selection.
- `wacc-terminal-value.md`: cost of capital, terminal growth, exit multiple, and terminal-value reasonableness.
- `sensitivity-and-scenarios.md`: base/downside/upside design, reverse DCF, and pressure-test grids.

## Senior Judgment And Architecture

- `dcf-architecture.md`: preserved workbook architecture, tabs, formulas, and formatting conventions.
- `valuation-judgment.md`: forecast challenge, valuation reasonableness, ROIC/reinvestment tests, and senior review prompts.
- `integrity-controls.md`: workbook QA, formula controls, checks, sign-off standards, and artifact integrity.
- `industry-playbooks.md`: sector-specific DCF adaptations and model-driver choices.
- `output-and-review.md`: final review, communication standards, caveats, and decision-readiness narrative.

## Integrations

- `p0-integrations.md`: coordination with launch-priority Public Equity Investing and shared-core skills.

## Loading Rule

Do not load all references by default. Start with the formula workbook contract docs for user-facing model builds, deterministic support docs for implementation or QA issues, valuation mechanics docs for assumption/math issues, and senior judgment docs only when the user needs full diligence-quality reasoning.
