# Executive Report Specification

Use this specification for `product stakeholders`: product, business,
leadership, and general stakeholder readers who need a decision-ready narrative rather than a methods memo.

Shared artifact, visualization, layout, citation, and sharing rules live in
$build-report. This file only captures what is different for the executive shape.

## What This Shape Optimizes For

- Lead with the answer and why it matters.
- Use plain language and translate jargon before using it.
- Optimize for decision usefulness over methodological completeness.
- Show enough evidence to trust the point, but keep supporting mechanics out of the main reading path unless they materially change the takeaway.
- Integrate implications into the summary, section-level interpretation, and next-step framing rather than isolating them in a standalone section.

## Required Structure

Default to this order:

1. Title
2. Executive summary
3. Key findings with visual evidence
4. Recommended next steps
5. Further questions
6. Caveats and assumptions

These entries define section roles, not literal heading text, except that the executive summary must remain a visible section labeled `Executive Summary`. Use story-specific headings for later sections when that reads better. For example, a findings section can be titled `Why concentration increased` instead of the generic `Key findings with visual evidence`.

For most reports, a busy reader should be able to skim the title, executive summary, and first one or two body sections and understand the answer.

## Drafting Rules

- Use a short plain-English title.
- The executive summary should stand on its own and answer the user's question directly.
- Render the executive summary as its own visible section immediately after the report title. Do not collapse it into the title block, an unlabeled lede, a subtitle, KPI cards, or bold opening paragraphs.
- Default to 2-4 executive-summary bullets or short mini-paragraphs. Start each item with a bold topic sentence.
- The required structure is role-based, not a rigid outline. Headings may be renamed, sections may be combined, and the order may adapt to the story. However, the report should still visibly perform the needed roles: summary, findings, evidence, interpretation, implications or next steps, open questions when useful, and caveats or assumptions.
- Avoid thin executive reports. A concise report is fine, but it should not leave the reader to infer the meaning of tables or charts. Each major finding should include enough explanation to understand the comparison, magnitude, interpretation, and so-what.
- Executive reports should be concise in the summary, not compressed in the evidence path. The body must be substantial enough that a reader can audit the conclusion without relying on hidden process notes.
- Do not open the report with methodology, definitions, or caveat-setting before the answer unless that context materially changes interpretation.
- Start each major section with the takeaway, not scene-setting.
- Use rich markdown in the body as well as the executive summary when it helps scanning: bold topic sentences for important paragraphs, render numbered or bulleted recommendations as real lists, and avoid run-on list text in a single paragraph.
- Use section headings that advance the story rather than copying the template labels verbatim when a more specific heading would read better.
- For major findings, make the heading the insight, tension, or driver, not a generic topic label. Prefer headings like `Multimodal ARR expanded sharply,
  but the current run-rate is below the peak` over labels like `Customer and segment drivers`.
- Keep each section's `so what` explicit. Put it immediately after the evidence when possible.
- Keep methods brief in the body unless a methodological caveat materially changes the takeaway.
- Do not include process notes, validator notes, chart-selection rationale, or
  "why this chart is absent" explanations in the visible report body unless the user explicitly asks for methodology or the detail changes the decision.
- For diagnostic and strategy reports, do not insert a default KPI-card row or scorecard strip between the title and executive summary.
- For executive KPI readouts, portfolio scorecards, MBR/QBR-style reports, or one-section-per-business-area reports, include a compact KPI-card strip after the executive summary when headline actuals, deltas, and plan/status signals are available. Do not use a broad summary table as the default substitute for those cards.
- Use neutral, descriptive visual headers for charts and tables. Keep the narrative claim in the surrounding markdown, not duplicated as the visual title. Prefer visible dates like `May 12, 2026` or `Q2 FY26 to date` over ISO-formatted dates in reader-facing copy.
- Include next steps and further questions when they help the user act.

If the report is one of these common forms, bias the section framing accordingly:

- KPI readout: bottom line, current state, comparison, status, drivers, risk,
  next action.
- Diagnostic memo: what changed, verified drivers, rejected explanations,
  residual uncertainty, and implications integrated into the summary and major sections.
- Strategy memo: answer or recommendation, strongest evidence, tradeoffs,
  caveats, next decision.

## Section Pattern

For each major section:

1. Takeaway headline
2. More detailed evidence
3. Visual evidence
4. Short evidence note or caption
5. Short implication, next step, or open question when useful

Use the heading to carry the narrative insight. Avoid generic topic headers such as `Segment drivers`, `Customer analysis`, or `Performance trends`.

Do not dump visuals without interpretation. Do not delay the main point behind setup prose.

## Executive QA Addendum

- A first-time reader can skim the title, executive summary, and section headers and understand the answer.
- The title is short and plain-English.
- The executive summary uses 2-4 bullets or short mini-paragraphs with bold topic sentences by default.
- The executive summary does not duplicate itself elsewhere near the title.
- The body expands the same takeaways from the summary rather than introducing a disconnected second story.
- The report does not open with methodology, definitions, or caveats before the answer unless that context materially changes interpretation.
- Implications appear in the summary, relevant sections, or next steps rather than as a standalone block.
- Citations support trust without interrupting reading flow. If numeric markers like `[1]` or `[2]` are used, they should resolve to linked,
  human-readable citation metadata and report evidence affordances rather than opaque labels.
- Every major section answers `so what`.
- Plain language wins unless a technical term is actually necessary.
- Diagnostic and strategy reports do not insert a default KPI-card row between the title and executive summary.
- Executive KPI and portfolio reports use KPI cards for the skimmable top-line status and reserve tables for supporting exact values or audit detail unless the user asked for a table.
- Visual titles are neutral labels, not insight sentences, and charts use differentiated categorical colors for unrelated entities plus neutral dashed styling for plan, target, forecast, budget, quota, or baseline comparisons.
- Methods, caveats, and uncertainty are present where needed but do not crowd out the decision story.
- Report-building decisions and visualization QA details are preserved in source notes or handoff artifacts, not narrated as executive content.
- Recommendations and implications are clearly signposted and evidence-backed.
