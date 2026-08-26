# Technical Report Specification

Use this specification when the user explicitly wants a technical audience or when the report is primarily about data methodology, measurement design,
statistical analysis, experimentation, modeling, or other audit-heavy work.

Shared artifact, visualization, layout, citation, and sharing rules live in
$build-report. This file only captures what is different for the technical shape.

## What This Shape Optimizes For

- Lead with the main result, then show the definitions, evidence, methods, and limitations needed to trust it.
- Preserve technical precision. Simplify wording only when meaning is unchanged.
- Define metrics, cohorts, filters, baselines, and units before leaning on them in argument.
- Keep assumptions, uncertainty, and failure modes close to the findings they affect.
- Distinguish descriptive, diagnostic, inferential, predictive, and causal claims.
- Integrate implications into the technical summary, section-level interpretation, and next-step framing rather than isolating them in a standalone section.

## Required Structure

Default to this order:

1. Title
2. Technical summary
3. Key findings with visual evidence
4. Scope, data, and metric definitions
5. Methodology
6. Limitations, uncertainty, and robustness checks
7. Recommended next steps
8. Further questions

These entries define section roles, not literal heading text. Use headings that fit the actual result and method story instead of copying the template labels verbatim.

If the work is model-heavy, experimental, or inferential, add a dedicated section for model specification, experimental design, or validation details instead of hiding them inside footnotes.

## Drafting Rules

- The technical summary should stand on its own and state the main result directly.
- Start sections with the result, not with methodology setup.
- Use section headings that reflect the actual result or method question rather than copying the template labels verbatim when a more specific heading would improve readability.
- For major findings, make the heading the substantive result or driver, not a generic topic label. Prefer headings like `Digital Natives and Startups drove most of the segment expansion` over labels like `Customer and segment drivers`.
- Define uncommon or overloaded terms on first use.
- Make definitions, cohorts, denominators, and comparison baselines explicit before the reader needs them.
- If a claim depends on modeling choices, thresholds, priors, sampling rules,
  or feature engineering, say so explicitly.
- Include negative results, counterexamples, sensitivity, or failure modes when they change interpretation.
- Use top-line metrics only when each one adds analytical value.
- If the work builds a model, keep fitting, diagnostics, and interpretation in the companion notebook unless a reusable support module is clearly necessary.
- Recommendations or next steps should follow from the evidence, not from generic best practice.

## Section Pattern

For each major section:

1. Result headline
2. Precise interpretation
3. Visual evidence
4. Evidence note with definition or sample context
5. Method or assumption note when needed
6. Limitation, implication, or open question

Use the heading to state the result the section proves. Avoid generic topic headers such as `Segment drivers`, `Customer analysis`, or `Performance trends`.

Do not separate results from the definitions or assumptions needed to trust them. Do not open with methods text that delays the result.

## Technical QA Addendum

- A first-time technical reader can audit the logic without guessing what was measured or how.
- The technical summary and body tell the same story at different depth.
- Definitions, cohorts, denominators, and baselines are explicit.
- Each major section clearly distinguishes result, evidence, and limitation.
- Implications appear in the summary, relevant sections, or next steps rather than as a standalone block.
- Uncertainty is quantified when possible and described precisely when not.
- If the work includes forecasting, experiments, causal claims, or modeling,
  the report states what the result does and does not establish.
- Recommendations and implications remain clearly signposted and evidence-backed.
