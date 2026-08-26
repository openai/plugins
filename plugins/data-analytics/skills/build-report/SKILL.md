---
name: build-report
description: "Build polished analytical reports for executive, product, business, or technical audiences. Use when the task needs a durable answer-first narrative with evidence-backed findings, visuals or tables, caveats, and source context."
---

## Related Skills

Use the focused analysis skill before building the report when the report depends on market sizing, metric diagnostics, KPI reporting, product/business analysis, data-quality checks, or validation.

# Report Building

Use this skill when the user needs a durable analytical report rather than a dashboard, notebook-only dump, or transient chat summary. The report owns the reader-facing narrative, audience shape, evidence placement, visual/table placement, caveats, source metadata, and handoff. The underlying analysis should still come from the appropriate analysis, notebook, data quality, diagnostics, KPI, or product-analysis workflow.

If this skill is selected directly or included by a report-mode workflow, the run is incomplete until the selected report surface exists or a concrete blocker is recorded. Do not finalize with chat-only prose, an inline widget, a local URL, or an ad hoc artifact that skips the report shape. Treat inline summaries and notebook outputs as progress evidence, not as substitutes for the report. Once this skill is selected, reserve charts, tables, and previews for the selected report surface. A user can explicitly waive report creation by requesting an inline, chat-only, brief/no-artifact answer, asking for no report/file/artifact, or selecting another primary artifact. Do not infer a waiver from the absence of the word "report" or from a direct diagnostic, recommendation, sizing, or readout question.

## Skill Configuration

Choose exactly one report delivery mode for each run:

- Work Mode on any surface: automatically use `sites-app` for durable reports when the full Sites create, checkpoint, and deployment lifecycle is callable. Do not ask for another delivery choice or publish confirmation. Build and validate the canonical MCP artifact payload without visibly rendering it, then export and deploy it through Sites. Automatically switch to `html` when Sites is unavailable, publishing fails, or the user explicitly declines Sites. MCP servers and other callable tools remain valid evidence sources.
- ChatGPT Desktop outside Work Mode: use `mcp-app` by default. After a successful final MCP report handoff, offer Sites as an optional coworker-sharing follow-up; do not publish unless the user explicitly requests or accepts it.
- ChatGPT web Chat mode after the user explicitly overrides the Work Mode recommendation: use `html`. Do not automatically publish to Sites or select `mcp-app` in this branch.
- Any other runtime where MCP app report rendering is unavailable: use `html`.
- Unknown or unclassified runtime: default to portable `html` rather than omitting the report.

On ChatGPT Desktop outside Work Mode, use `html` only when the user explicitly asks for HTML, offline portability, a file-based artifact, or no MCP rendering; a requested downstream conversion requires HTML; or an MCP app report was actually attempted and failed because the capability was unavailable or a documented renderer limit was exceeded.

If the selected MCP app report cannot be rendered after one targeted correction, fall back to `html` in the same run unless the user explicitly declined HTML. A renderer failure changes the delivery mode; it does not waive the report. If neither surface can be created, record the concrete blocker and the attempted surfaces before finalizing.

If an MCP app report was already rendered and the current context later positively identifies Work Mode, treat the MCP artifact as the wrong delivery mode regardless of surface. Rebuild through `sites-app` when the full Sites create, checkpoint, and deployment lifecycle is callable, and otherwise rebuild the report as self-contained HTML before final handoff.

Select exactly one delivery mode per run. `sites-app` is one delivery mode, not an MCP app plus an HTML report. Do not build an MCP app report and a static `report.html` as parallel outputs unless the user explicitly asks for a second delivery mode as a separate follow-up. Switch a Sites run to HTML only when the full Sites lifecycle is unavailable, publishing fails, or the user explicitly declines Sites. For every selected HTML report path, including ChatGPT Desktop explicit HTML, Work Mode fallback HTML, and HTML created for PDF, Google Docs, or Google Slides conversion, author the same canonical `artifact.json` shape accepted by `validate_artifact`, then package and verify it once with `npm run report:deliver -- --input artifact.json --output report.html` from the plugin root. Do not maintain a separate HTML-only chart or layout implementation.

## Workflow

1. Define the reporting job.

   State the user question, decision or action the report should support, primary audience, scope, time frame, comparison baseline, success criteria, and what would make the report decision-useful. Choose exactly one audience:

   - `product stakeholders`: default for product, business, leadership, strategy, diagnostics, KPI readouts, and general stakeholder reports.
   - `technical`: only when the user asks for a technical or methods-first report, or when the report's main value is methodology such as metric definitions, measurement design, statistics, modeling, experimentation, or validation.

   If the work is unusually methodology-heavy but the user did not ask for a technical audience, ask before switching.

2. Read the matching audience specification.

   Read exactly one matching audience specification before gathering evidence, shaping the report spine, or drafting the report surface:

   - [executive-report.md](specifications/executive-report.md) for `product stakeholders`
   - [technical-report.md](specifications/technical-report.md) for `technical`

   Treat the selected audience specification as a report-quality contract, not as a replacement for the workflow below. Capture its `Required Structure` entries in the report plan or supporting source notes, and stop with a blocker if the matching specification cannot be read.

3. Gather and bound the evidence.

   Inventory the source data, metric definitions, denominators, assumptions, requested cuts, caveats, notebooks, SQL, scripts, query permalinks, source documents, and reviewed datasets needed to support the report. Resolve ambiguities before drafting claims. If a requested metric or cut cannot be supported, record why and state what evidence would be needed to add it. Preserve process notes, source inventory, and reproducibility notes in source metadata, source notes, or supporting artifacts, not in the visible report body.

   When this skill is selected directly and the user explicitly asks to "use sample data" or create a report "using the sample data" without naming or attaching a different sample, treat that wording as selection of the bundled synthetic demo. Resolve [demo-product-growth.csv](../../assets/demo-product-growth.csv) relative to this skill, analyze those rows, label them synthetic, and do not search the workspace for a substitute or invent replacement data.

4. Distill the report spine.

   Before choosing a delivery surface, write or mentally verify a compact answer-first report spine with these entries:

   - question
   - decision-useful answer
   - metric, cohort, denominator, time window, and comparison basis
   - findings by requested segment or driver, with supporting evidence
   - sensitivity or validation checks when the answer is comparative, causal-adjacent, or surprising
   - caveats that could change interpretation
   - recommended next step, monitoring point, or open question

   Ensure report segments are clearly separated and duplicate feature/metric coverage is removed. Each major segment should have one clear job in the report and should pair a claim with evidence, interpretation, and a concrete implication.

   If the spine has only a title, an executive summary, and one chart or table, stop and expand the evidence path before rendering unless the user explicitly asked for a brief.

5. Plan the reader-facing structure.

   Draft the ordered major segments, visible segment titles, and intended evidence format for each segment before building the surface. Use visuals by default for quantitative findings when real data is available; use tables for exact lookup, audit detail, or cases where a chart would obscure the point. If a quantitative segment has no visual, record the omission reason in source notes or supporting artifacts.

   Every planned major segment must have a reader-facing title that will appear in the final report. Do not rely on chart headers, table titles, or non-rendered structure alone to carry the section title.

   Apply the report depth gate before building:

   - The executive summary does not count as the evidence section.
   - A report with quantitative findings must include visible metric/cohort definitions before those definitions are needed to interpret the evidence.
   - A comparative report must include segment-level interpretation, not only aggregate values.
   - A causal-adjacent or behavior-difference report must include at least one validation, sensitivity, or limitation note near the finding it qualifies.
   - A report with only one narrative block plus chart/table evidence is too thin unless the user explicitly requested a brief, an inline answer, or a single-chart readout.

6. Apply report standards and audience requirements.

   After the general structure exists, apply the relevant standards in this skill. Map each planned major segment to the selected audience specification's `Required Structure` entries, and record any merged, renamed, reordered, or omitted entry with a reason.

7. Design visuals and tables.

   Route every report visualization through `$visualize-data` for chart selection, chart contract, and final-context QA. Keep chart-selection rationale, validator notes, and QA details in working notes, source notes, or supporting artifacts unless the user asks for methodology or the detail changes the reader-facing takeaway. Make sure every visual or table supports a specific report claim rather than existing as decorative context. Plan an adjacent explanatory paragraph for every visualization before rendering. Reserve chart, table, and preview output for the selected report surface.

8. Choose and build one delivery surface.

   Use the single delivery mode selected after the report spine and evidence plan are clear. Do not add a second mode unless the user explicitly asks for it as a separate follow-up.

   Build the selected surface so it preserves the report reading path, visible titles, evidence order, caveats, and source metadata. Use the delivery-mode specifications in `Report Standards` as implementation guidance for the selected surface, not as a substitute for the report-building workflow. In HTML mode, follow `Portable HTML Packaging` in `../../src/analytics-app-core.md`: save the full validated report input as `artifact.json` and run the packaged delivery command to create and verify `report.html`.

   For `sites-app`, read the MCP app report specification and shared analytics app core, build the same complete manifest and bounded snapshot, and call `validate_artifact`. In Work Mode, do not call `render_artifact`; after validation succeeds, create or reopen a Sites worker-starter checkout and call `export_artifact_package` with that project id and checkout path as `output_dir`.

   Invoke `$publish-artifact-to-sites` for the Sites handoff. In ChatGPT Desktop outside Work Mode, do this only after an explicit request or acceptance of the post-handoff sharing offer; in Work Mode, the report request authorizes the automatic Sites handoff. Follow the current `sites-hosting` workflow for version saving, deployment, and polling; use one Site per logical report and deploy a new version when refreshing it. If the Sites exporter cannot hand its files to the hosting workflow or deployment fails in Work Mode, automatically switch this run to self-contained HTML, report the Sites blocker briefly, and do not claim that a Site was published.

   When revising an existing report, treat the current rendered report and source metadata as the starting artifact. Preserve every existing section, visual, table, source, dataset, title, and caveat exactly unless the user explicitly asks to change it or the requested edit makes a narrow dependent update unavoidable. A request to add a section, swap a chart, restyle a visual, or customize one part of the report is not a request to summarize, replace, reorder, or drop the rest of the report. Render the full revised report in the selected surface; do not hand off a section-only, slimmed, or partial replacement artifact when the prior report was complete.

   For correction passes after a validation or rendering issue, patch the previous full report artifact in place. Limit changes to the affected visual, table, section, dataset, or source plus any directly dependent references. Preserve unrelated ids, reading order, narrative text, caveats, recommendations, source metadata, package metadata, and datasets unchanged when the selected surface exposes those concepts. Before rendering, compare the old and new artifact structures and confirm that only the intended parts changed. If the previous full artifact is not available, stop and surface that blocker instead of rebuilding a shorter replacement from memory.

9. Validate the finished report.

   Review the rendered report itself, not just its source files. Confirm that:

   - the top of the report answers the user directly
   - every major segment has a visible title
   - claims, visuals, tables, caveats, and implications appear in the intended reading order
   - the selected delivery surface satisfies its mode-specific standards
   - the supporting evidence and source notes are sufficient for auditability

   Fix the report before handoff when any of these checks fail.

10. Hand off the selected report.

   Lead with the selected report artifact result or blocker. Then list only the relevant MCP app artifact, Sites URL, or HTML report path, plus supporting source, SQL, code, notebook, and chart artifacts. For `sites-app`, include the snapshot timestamp and say that the Site contains a published snapshot rather than a live connection. After a successful final MCP app handoff in ChatGPT Desktop outside Work Mode, offer to publish the report to Sites if the user wants to share it with coworkers; do not invoke the publishing workflow until they explicitly accept. In HTML mode, the actual interactive `report.html` file is the primary deliverable. A rendered PNG or screenshot may be included only as a labeled non-interactive QA preview; never use `image.png`, a screenshot, or another flattened image as the only report handoff. If the host cannot render HTML inline, attach or link the `.html` file instead of flattening it. Self-audit the report against the quality bar before handoff. If HTML sharing or conversion is needed and safe, resolve the presentation surface; otherwise record why sharing was unsafe, unavailable, or explicitly waived. Do not substitute a chat summary for the report.

## Report Standards

### PDF Export Specifications

When the user asks to export a Data Analytics report, dashboard, or inline chart surface to PDF, use `report-to-pdf`. That sub-skill owns PDF conversion mechanics so this root workflow stays delivery-mode neutral.

### MCP App And Sites Report Specifications

Read [mcp-app-report.md](specifications/mcp-app-report.md) when the selected report surface is `mcp-app` or `sites-app`. That file owns the shared manifest/snapshot mechanics plus the different visible-render and hosted-export handoffs so this root workflow stays delivery-mode neutral.

### HTML Report Specifications

- Use HTML mode only under the delivery rule in `Skill Configuration`; on ChatGPT Desktop outside Work Mode, do not choose it before an MCP attempt unless the user or downstream conversion explicitly requires HTML.
- Read `../../src/analytics-app-core.md`, including `Shared Contract` and `Portable HTML Packaging`. Author `artifact.json` as a complete `validate_artifact` input with `surface: "report"`, ordered native manifest blocks, bounded snapshot datasets, canonical sources, and any required access issues. Use the same report block, card, chart, table, and source contract as the MCP artifact reader.
- Run `npm run report:deliver -- --input artifact.json --output report.html` once from the plugin root. This one command revalidates the artifact, invokes the only HTML renderer for this workflow, and, when a compatible installed Chromium is available, extracts shared-renderer chart SVGs and runs the bounded browser verifier against the same artifact. The renderer always embeds the read-only artifact reader with the shared app tokens and layout and generates the semantic no-script/print/conversion representation from the same data.
- Preserve automatic system appearance support in the generated portable report: keep the packaged reader's `<meta name="color-scheme" content="light dark">` and `prefers-color-scheme`-driven tokens intact. Verify content, charts, semantic fallbacks, source affordances, and focus states in both light and dark system modes; do not replace this behavior with a manual-only theme toggle.
- Keep the HTML reading path report-like: answer first, visible segment titles, evidence and interpretation together, and caveats where they matter. Let the builder's source affordances and quiet semantic source inventory carry audit details; do not add a second narrative sources, notes, or reproducibility appendix unless the user explicitly asks for it.
- Give every source-backed card, chart, and table canonical inline `source` metadata or a `sourceId` that resolves to `manifest.sources[]`. Include exact source identity and, for structured data, the fully qualified table or view; list every material source for joined or multi-input evidence. Use precise dataset, file, or document names for non-tabular evidence. Never invent provenance; preserve unavailable-source gaps in access issues, source metadata, or report notes as appropriate.
- A markdown block may declare block-wide provenance with `sourceId` only when every quantitative claim in that block comes from the same canonical source. Split mixed-provenance claims into separate markdown blocks, omit `sourceId` on title-only or prose-only blocks, and never guess a source. The referenced source may be a structured query, file, or document and does not require SQL.
- Treat accessible source affordances, source tooltips/detail views, shared styling, and the semantic source inventory as builder outputs. The builder preserves safe canonical provenance exactly; it does not strip, normalize, or rewrite source fields. Credentials, credential-bearing URLs, and machine-local or parent-traversing paths fail packaging with an explicit error and must be corrected in `artifact.json`. The builder replaces `package_info` with the portable read-only delivery envelope; that envelope is runtime configuration, not provenance.
- Treat a compact success receipt with `stages.verification: "passed"` as sufficient per-report QA. It confirms that the HTML embeds the exact canonical artifact, then reuses an installed Chromium—never downloading a browser—to verify the enhanced reader at desktop and narrow widths, content counts and visibility, overflow, no network calls or browser errors, and a representative source menu/dialog flow. Do not write a bespoke Playwright script, take routine screenshots, or repeat browser inspection when it passes; screenshots are failure-only. A successful receipt with `stages.verification: "structural_only"` means no compatible browser was available: exact payload equality and the required runtime, reader, and semantic-fallback roots passed, but chart SVG extraction and per-artifact browser QA did not run. Keep the delivered semantic chart tables, report that QA limitation, and do not install a browser during report generation.
- The self-contained file uses responsive shared reader components on current browsers. Browsers that cannot start the enhanced reader retain the semantic fallback, so the report remains readable but may not be interactive. The per-report verifier's narrow viewport is a fast responsive smoke, not Safari, Firefox, touch-device, print, or conversion certification; those deeper compatibility checks belong to the shared reader's CI and should run only when its runtime or builder changes.
- Do not flatten the HTML into an image as the report deliverable. Use `report-to-pdf`, `report-to-google-doc`, or `report-to-google-slides` with the generated HTML, not a live MCP app report.

### Narrative

- Every report must have a short plain-English reader-facing title. For HTML reports, use the same title in the document title and visible page header. For MCP app reports, follow [mcp-app-report.md](specifications/mcp-app-report.md).
- Do not duplicate the title or executive summary in an unlabeled subtitle, lede, scope line, or second summary block.
- Treat the report title and executive summary as separate visible elements. The report title is the artifact-level name; it does not satisfy the executive-summary section role. For stakeholder reports, render a visible `Executive Summary` section heading immediately after the title before the summary content.
- Open stakeholder reports with an executive summary that answers the user's question directly. Default to 2-4 bullets or short mini-paragraphs with bold topic sentences.
- Open technical reports with a technical summary that states the main result, then provide definitions, methods, uncertainty, and limitations needed to trust it.
- Start major report segments with the takeaway, not setup prose. Use headings that carry the insight rather than copying generic labels.
- Include visible titles for every major report segment in every delivery mode. Titles are part of the reader-facing report contract, not just private metadata. In HTML reports, render titles as heading elements inside sections. For MCP app reports, follow [mcp-app-report.md](specifications/mcp-app-report.md). Use story-specific titles such as "API ARR is pulling ahead of plan" rather than generic labels when the evidence supports it.
- Keep an obvious top-to-bottom report reading path. Do not turn a report into a dashboard grid unless the user asked for a dashboard. Use a single-column document flow by default; half-width visual blocks are acceptable only when labels, series, and interpretation remain readable in the selected surface.
- Use report markdown blocks for narrative insights and interpretation. Give each independently laid out or editable major report segment its own markdown block; do not place multiple peer `##` section headings in one markdown body. Use `###` headings only for subordinate content that should remain in the same card. Keep chart/table headers neutral, and put takeaways in adjacent narrative blocks rather than hiding the argument inside visual metadata. Markdown blocks are the primary place for the story.
- When a narrative block contains sourced quantitative claims, apply its one block-wide `sourceId` only under the single-source rule above so generated readers can expose provenance on those values. Do not attach a source to unsourced prose merely to create a tooltip.
- Reports should be substantial enough to stand on their own. Do not deliver a report that is mostly a chart/table bundle with a short summary. The reader should be able to understand the answer, evidence, interpretation, caveats, and recommended next step from the narrative itself.
- Use flexible section names and story-specific ordering, but make sure the report still does the core jobs: answer the user's question directly; explain the metric, cohort, denominator, time window, and comparison basis when they affect interpretation; pair each important number or visual with plain-English interpretation; explain why the finding matters for the decision; state what remains uncertain or could change the conclusion; and include a practical next step when the evidence supports one.
- Use rich markdown beyond the executive summary when it improves scanning:
  bold topic sentences in important body paragraphs, keep recommendations as real markdown lists, and avoid collapsing list items into run-on paragraphs.
- When using ordered or unordered lists, put each item on its own Markdown line. Do not put `1.`, `2.`, and `3.` items in the same paragraph, and do not leave an intended list item as an unnumbered continuation line.
- For executive, strategic, and diagnostic reports, the first narrative content after the title should be the executive summary. Do not insert an unlabeled lede, duplicate summary, methodology block, caveat section, KPI strip, or metric card row before the summary.
- For diagnostic and strategy reports, do not insert a default KPI-card row before the executive summary. KPI, portfolio, MBR/QBR, and one-section-per area reports may use a compact KPI-card strip after the summary when headline actuals, deltas, and status signals are available.
- Do not use a broad comparison table directly beneath an executive summary as the primary summary artifact for KPI, portfolio, or multi-area reports. Use metric cards for skimmable top-line status when headline actuals, deltas, and status signals are available; use tables for supporting exact values or audit detail.
- Metric cards should contain one headline value, but one headline does not mean one `metrics[]` entry. Use labeled chips for short comparison context tied directly to that headline, such as its prior-period value, target, or delta. When a decision-relevant directional comparison is already used in the executive summary or findings, preserve it as a later comparison metric and set `signed: true`; move independent secondary measures to another card, chart, table, or narrative block.
- Let the report decision determine the number of headline metric cards. Do not pad or truncate the set to four—or any preferred count. Include only distinct, meaningful headline metrics, group coherent cards in the same strip, and split unrelated measures into another strip or supporting table; odd counts are valid because the artifact renderer balances rows responsively.
- Percent values must use a consistent numeric scale in the selected surface.
- Every major report segment should pair a claim with evidence and interpretation, then answer "so what" with an implication, risk, opportunity, recommendation, monitoring point, or next action.
- Include recommended next steps when the evidence supports action. If the evidence only supports monitoring, say what should be monitored and why.
- Include further questions when meaningful uncertainty, missing evidence, or follow-up analysis could change the decision. Omit the section only when there are no decision-relevant open questions, and record that choice in source notes.
- Caveats and uncertainty should be visible where they change interpretation, without crowding out the answer.

### Evidence And Sources

- Base every major claim on saved data, code, query results, notebook outputs, source documents, or rendered charts created or inspected during the task.
- Tie important numbers, charts, and recommendations to readable source metadata near the relevant paragraph or visual when the selected surface supports it.
- Keep raw paths, notebook locations, temp directories, request IDs, and implementation-facing audit details in source metadata, source notes, or supporting artifacts unless needed for trust. In HTML reports, preserve source-system and table names in canonical source metadata so the portable reader can expose them through its source affordances and detail views; keep them out of the primary narrative unless needed for trust.
- Keep source SQL in source metadata, source modals, linked query artifacts, or supporting notes. Do not paste source SQL into the visible report body or final chat handoff unless the user explicitly asks to see, write, review, debug, or receive SQL or query methodology.
- Do not add a visible bottom sources, notes, or reproducibility section unless the user explicitly asks for that methods layer.
- Preserve source datasets, query or transformation artifacts, rendering code, output folders, assumptions, omitted metrics, and chart QA notes in source metadata, source notes, or supporting artifacts even when they are not visible in the report body.
- Surface enough evidence affordance for audit without creating a heavy visible claim graph. Prefer block-level source references when the surface supports them.

### Visuals And Tables

- Report visual headers should be neutral: chart/table name plus a short description only when needed for metric, denominator, cohort, filter, or time window. Put narrative insights and caveats in adjacent markdown blocks.
- Every report visualization must have an adjacent explanatory paragraph immediately before or after it in the reading flow. The paragraph should state the takeaway, how to read the visual, and the implication or caveat needed to interpret it; chart titles, subtitles, captions, metric cards, or table headers do not satisfy this requirement by themselves.
- Chart and table subtitles should add a reader-facing insight or interpretive context that the title does not already cover. Prefer direction, magnitude, inflection, rank, comparison basis, scope, time period, unit of measurement, filters/exclusions, denominator, cohort, sample size, or basis of comparison, such as `Growth accelerated after mid-April and ended at a period high` or `FY2021-FY2024, values in millions of USD`. Keep descriptions and subtitles hidden by default unless `showDescription` or an equivalent flag is needed to clarify the reading path.
- Prefer human-readable dates in visible markdown, chart titles/subtitles, captions, table labels, and generated-date chrome. Keep ISO timestamps in query bindings, source metadata, and other machine-readable fields.
- Do not use source table names, raw query ids, dashboard slugs, notebook paths, SQL intent, metric definitions, or implementation labels as chart/table subtitles. Put those details in source metadata, source notes, or supporting artifacts unless the source identity is itself essential for reader trust. For HTML reports, keep exact source-system and table names on the related canonical card, chart, or table source so the generated source UI makes them available without cluttering the subtitle.
- Before rendering report tables, check every table subtitle against the table title and visible columns. If it does not clarify what rows are in scope, what period is covered, how values are measured, which filters apply, or what comparison is being made, rewrite it or omit it rather than falling back to the source name.
- Do not shrink visuals into unreadable sidecards. Use full-width blocks for dense charts, long labels, or chart-data summaries that need more room.
- Put report charts on their own readable row or block in the reading flow unless a half-width layout has been checked in final context and remains legible. Do not use narrow right-rail chart cards for report evidence.
- Report trend charts need enough observed data to make the shape worth reading. When a report chart would show only a few anchor periods, route back through `$visualize-data` to request a finer grain, longer lookback, or meaningful segment breakdown before rendering. If the source cannot support that without misleading the reader, replace the trend with a KPI strip, grouped period bars, table, or concise narrative comparison and record the omitted richer trend in source notes or supporting artifacts.
- Report tables default to spacious density for low-row, narrative, presentation-ready tables. Use dense tables only for audit/detail tables or compact lookup data.
- Reserve positive/negative table color for columns explicitly marked with `movement: true`, `semantic: "movement"`, or `role: "movement"`. Values in those columns should carry the intended sign or arrow, such as `+12%`, `-$4.2M`, `↑3 pp`, or `-18`. Keep composition, mix, share, percentile, and current-value columns neutral.
- For multi-chart reports, keep a compact chart map in source notes or supporting artifacts. Name each visual's report segment, analytical question, selected family/type, fields, and supported claim. Repeated chart types need a reason; do not default every visual to a trend chart when report segments ask different questions such as status, mix, variance, drivers, or distribution.
- When a report is exported or converted, every interactive or surface-native visual needs a readable static representation. Record a blocker if the static representation is missing or misleading.

### Metrics And Language

- Describe metrics in plain English before exposing implementation details.
- Clarify definitions, cohorts, denominators, filters, and comparison baselines before relying on a metric in the report.
- Choose the most interpretable audience-facing grain: user, account, workspace, task, turn, session, request, revenue, endpoint, customer, org, or another business-facing unit.
- Put raw numbers in context: percent of an active base, percent of the previous funnel step, percent of total change, comparison to baseline, target, peer segment, or historical range.
- Use shorthand large numbers in narrative text, chart labels, and summaries, such as `899k`, `10.9k`, or `1.2M`. Reserve exact comma-separated values for audit tables, SQL outputs, appendices, or cases where precision changes the interpretation.
- Keep implementation-facing event names, field names, table names, and exact predicates out of the main narrative unless they are essential for trust. Put them in caveats, source metadata, or short parentheticals.
- Polish the final language for the selected audience: concise, answer-first, free of process notes, and no deeper on methodology than the audience needs to trust the result.

## Quality Bar

Before final handoff, confirm:

- if any required item below fails, fix the report or record the blocking gap explicitly before finalizing
- exactly one delivery mode and exactly one audience specification were used, unless the user explicitly asked for a hybrid or second delivery mode
- the selected audience specification's `Required Structure` maps to visible report sections, with any merge, rename, reorder, or omission recorded in source notes or supporting artifacts
- the report spine, report depth gate, selected delivery-mode specification, and rendered report were all checked
- the rendered report answers the user directly, has visible reader-facing segment titles, and pairs each major claim with evidence, interpretation, caveats where needed, and a decision-useful implication
- definitions, denominators, baselines, requested metrics, and caveats are clarified before final claims are treated as decision-ready; omitted metrics have a reason and needed follow-up
- methodology depth fits the selected audience, and omitted requested metrics are explained with the reason and needed follow-up
- visuals and tables were routed through `$visualize-data`, inspected in the selected surface, and remain readable with useful subtitles, adjacent explanatory paragraphs for every visualization, source metadata, and supporting notes
- every source-backed card, chart, and table in an HTML report has canonical provenance, and the generated reader exposes working keyboard-accessible source affordances, tooltips, or detail views with exact source-system and table, view, dataset, file, or document identity
- sources and reproducibility notes, chart maps, and omission reasons are preserved in metadata, source notes, or supporting artifacts without cluttering the visible report
- the final handoff lists the selected report artifact plus relevant supporting evidence, not a chat-summary substitute or an unrequested parallel app plus HTML report
