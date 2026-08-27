# HTML Artifact Standard

Use this standard whenever a Public Equity Investing workflow creates a user-facing HTML artifact. HTML should improve the reader's ability to understand and act on the analysis, not force every workflow into the same dashboard shape.

## Design Principles

- Produce a polished, investment-professional artifact appropriate for an institutional investor, research analyst, or portfolio manager.
- Let the requested job determine the hierarchy and layout. A catalyst calendar should feel like a calendar; an earnings preview should lead with the expectation bar; a thesis tracker should lead with what changed.
- Prefer legibility, restrained color, readable typography, clear visual hierarchy, and scan-friendly sections over bright palettes, decorative complexity, or crowded dashboard panels.
- Put the most decision-relevant information near the top and make the workflow's primary object easy to find without extensive scrolling.
- Create a strong first-read layer with the concise investor readout, key decision triggers, and the workflow's primary analytical object. Put detailed registers, monitoring queues, and source ledgers below that scan layer.
- Use tables, timelines, cards, charts, and callouts only when they reduce interpretation time or improve comparison.
- Avoid repetitive sections, redundant decision framing, and citation presentation that competes with the analysis.

## Evidence And Integrity

- Cite material figures, confirmed dates, time-sensitive facts, and consequential factual claims near where the reader uses them.
- Before displaying a market price, return, multiple, or market-derived value in a hero card, headline KPI, or decision conclusion, verify that the cited source identifies the correct issuer, security, or ticker and the applicable as-of date. If that verification fails, omit the figure from the headline view or label it unavailable rather than carry an unverified anchor into the artifact.
- Keep citations traceable without making the page read like a control log. Cite material figures, derived calculations, dated events, quotes, and consequential disputed claims inline; when adjacent narrative sentences rely on the same source, use a single nearby citation or short section-level source note instead of repeating identical source chips after each clause.
- Distinguish confirmed facts from inferred windows, monitoring items, assumptions, and PM judgment.
- Keep important missing evidence and limitations visible, but integrate them proportionately rather than overwhelming the artifact.
- Express evidence limitations in plain investment-professional language. Do not expose internal workflow, validation, schema, or artifact-tracking fields such as `owning_workflow`, `decision_impact`, `readiness_effect`, `artifact_role`, or `hidden_unless_requested` in a user-facing artifact.
- A visible source ledger is appropriate when provenance matters to the investment decision, but it should read as research documentation rather than an internal control record.
- Do not claim decision readiness or precision unsupported by the available sources.

## Output And QA

- Deliver one polished standalone HTML file unless the user asks for another format or the workflow's primary deliverable is a workbook.
- Keep JSON, Markdown, CSV, manifests, logs, payloads, and intermediate notes as secondary support artifacts unless explicitly requested.
- Keep generation mechanics and intake/default disclosures out of the visible artifact, including badges such as `Format assumption`; when the workflow must disclose an assumed format or depth, do so in the delivery message or accompanying summary.
- Before delivering a substantive HTML artifact, render and visually inspect screenshots of the opening viewport and important downstream sections, then iterate on hierarchy, legibility, clipping, crowding, citation noise, and whether the requested job is immediately visible.
- For standalone local `.html` artifacts opened from a filesystem path or `file://` URL, do not use the in-app Browser plugin for visual inspection because it cannot open local HTML files reliably. Use local headless-browser screenshots instead.
- For HTML served through an allowed local or hosted URL, the normal browser inspection workflow may be used.

## Standardized Dashboard Option

Use the internal `dashboard-builder` capability when the user asks for a standardized dashboard, a reusable validated template, a structured payload-driven render, or another workflow explicitly selects that rendering path. Its payload schema and validation rules apply only on that standardized dashboard path; bespoke HTML artifacts should follow this standard without being forced through a fixed module inventory.
