# QA and Pressure Testing Rubric

Use this reference for MD/PM-grade review of a comps model or analysis.

## Overall standard

A strong comps model must be accurate, transparent, dynamic, and defensible. It should let a senior decision-maker understand:

- What peer evidence matters.
- Which data is trusted and why.
- How the model handles exceptions.
- Why the selected valuation range is appropriate.
- What would change the conclusion.

## Red-team questions

### Investment logic

- What is the actual decision this model supports?
- Does the selected peer set answer that decision, or just fill a template?
- What are the top three drivers of the target's multiple?
- Does the target deserve a premium, discount, or in-line valuation?
- Is the selected range driven by Core peers or diluted by weak comparables?

### Peer universe

- Are Core peers similar in business model, not just industry classification?
- Are obvious peers missing?
- Are any included peers too large, too small, too geographically different, or too diversified?
- Are excluded peers documented with rationale?
- Are private or acquired companies being mixed with trading comps without context?

### Data and sources

- Are market prices current as of the valuation date?
- Are source dates documented?
- Are reported, adjusted, consensus, and internally estimated figures separated?
- Are data definitions consistent across companies?
- Are units, currencies, and fiscal periods consistent?
- Are key figures triangulated against primary sources or trusted vendor systems?

### Normalization

- Are LTM and forward periods correctly defined?
- Is calendarization needed and documented?
- Are non-recurring items treated consistently?
- Are lease accounting, SBC, M&A, discontinued operations, and FX considered where material?
- Are negative or immaterial denominators handled as not meaningful rather than forced into ratios?

### Formula integrity

- Are formulas consistent across peer rows?
- Are calculated outputs formula-driven rather than hardcoded?
- Are there broken links, external references, or circular formulas?
- Are signs correct for cash, debt, minority interest, preferred stock, and other claims?
- Are formulas using the intended period and metric?
- Are hidden rows/columns, filters, or grouped sections concealing issues?

### Valuation conclusion

- Is the selected multiple range supported by Core peer statistics and qualitative judgment?
- Does the range reflect growth, margin, quality, leverage, and risk differences?
- Are sensitivities robust enough for senior review?
- Does the written conclusion include confidence level and open diligence items?
- Could a skeptical PM or board member understand and challenge the reasoning?

## Quality gates

Use these gates before final delivery:

1. **Structure gate**: Workbook includes clear tabs for inputs, data, normalization, multiples, valuation, sources, and QA.
2. **Source gate**: Every key metric has a source, retrieval date, and confidence label.
3. **Formula gate**: No unexplained broken formulas, hardcoded outputs, or inconsistent peer-row formulas.
4. **Comparability gate**: Peer tiers and inclusion/exclusion rationale are documented.
5. **Normalization gate**: LTM/NTM, currency, fiscal-year, and adjustment logic are explicit.
6. **Statistics gate**: Median, percentile, and peer-tier views are shown; outliers are explained.
7. **Judgment gate**: Selected valuation range is not a blind mean; it reflects business quality and risk.
8. **Communication gate**: Executive summary is decision-oriented and highlights uncertainty.

## Red flags requiring escalation

- User asks for a fairness, tax, legal, solvency, or formal valuation opinion without appropriate caveats.
- Public-company data conflicts materially across sources and cannot be reconciled.
- Target has no meaningful public comps and the conclusion relies on weak analogies.
- A model has formula errors in final output cells.
- Stale market data is used for a current valuation.
- A selected valuation range is materially inconsistent with Core peer evidence and no rationale is provided.
- The target has negative or volatile financials and the model still uses simple EV/EBITDA or P/E without adjustment.

## Review memo template

Use this structure for a pressure-test memo:

### Bottom line

State whether the model is ready for senior review, needs targeted fixes, or requires a rebuild.

### Highest-priority issues

List the 3-7 issues that most affect valuation conclusion or credibility.

### Peer universe judgment

Assess Core peer quality, missing peers, and exclusions.

### Data and formula integrity

Summarize source freshness, data confidence, formula issues, hardcodes, and link risks.

### Valuation judgment

Assess selected range, premium/discount logic, outlier treatment, and sensitivity quality.

### Recommended fixes

Give specific actions in priority order.

### Residual risk

State what uncertainty remains after fixes.
