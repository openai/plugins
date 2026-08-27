# Adaptive Deliverable Intake Policy

Use this policy before a Public Equity Investing skill acting as the lead owner creates a new substantive human-facing artifact. It applies to research reports, memos, models, valuation packages, event and catalyst artifacts,
risk/monitoring views, and dashboards. Presentation and support skills consume resolved choices from an owning workflow; they ask only when independently invoked to create a new standalone hero deliverable.

## When To Ask

Before source gathering, substantive analysis, building, or rendering,
determine whether the user's current prompt and conversation context give high-confidence direction on deliverable package or output format, analysis depth, audience/use, and material analytical focus.

- Ask only for materially unresolved choices.
- Do not ask the deliverable-package question when the requested surface or package is high-confidence from explicit wording or strong contextual cues, such as a Word memo, HTML report, PowerPoint deck, Excel workbook, dashboard, inline answer, update to an existing artifact, model build, tracker, or combined dashboard-plus-workbook package. The user does not need to name a file extension; infer the surface or package when the prompt and conversation make it clear.
- Treat the deliverable package as materially unresolved for any new memo, report, note, briefing, model, valuation package, dashboard, tracker, or similar substantive deliverable when two or more surfaces or artifact bundles would be plausible from the prompt. In those semi-ambiguous cases, ask with `request_user_input` before building.
- For a substantive single-company 60/90-day `catalyst-calendar` request,
  treat a polished HTML catalyst calendar as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a workbook/tracker. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus; present another format as an opt-out rather than a blocking intake decision.
- For high-confidence source-heavy post-earnings `deep dive`, `full report`, or reusable post-print packages, a polished standalone HTML post-earnings report may be the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or workbook/model-update output. If the prompt could reasonably mean a Word memo, inline note, model update, or combined report-plus-XLSX package, ask the deliverable-package question first. A narrower post-result question does not trigger this format default.
- For high-confidence source-heavy `pre-earnings preview`, `full preview report`, or reusable pre-print packages, a polished standalone HTML pre-earnings report may be the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or workbook/model output. If the prompt could reasonably mean a Word memo, inline note, model output, or combined report-plus-XLSX package, ask the deliverable-package question first. A narrow question about one earnings metric does not trigger this format default.
- For high-confidence source-heavy `full event analysis`, `full event report`, or reusable special-situations packages, a polished standalone HTML event report may be the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or model/math output. If the prompt could reasonably mean a Word memo, inline note, model output, or combined report-plus-XLSX package, ask the deliverable-package question first. A narrow question about one event term does not trigger this format default.
- For high-confidence reusable `idea-generation` screens, market maps, watchlist reviews, or source-heavy candidate sets, a polished standalone HTML idea-triage report may be the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or workbook/tracker output. If the prompt could reasonably mean an inline idea list, Word memo, workbook/tracker, or combined report-plus-XLSX package, ask the deliverable-package question first. A narrow question about one candidate does not trigger this format default.
- For an investment committee memo, substantive buy-side investment memo, or reusable/source-heavy public-equity memo, ask the deliverable-package question unless the prompt and conversation make the surface or package high-confidence. Formal IC, PM, or client memos normally recommend `Word document (.docx)`; source-heavy web-style investment reports normally recommend HTML; quick memo updates normally recommend inline.
- For a substantive reusable `meeting-prep` packet or explicit HTML meeting brief, treat a polished standalone HTML live-meeting brief as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, meeting type, or focus. A short question-list request does not trigger this format default.
- For a substantive reusable `long-short-pitch` package or explicit HTML trade pitch, treat a polished standalone HTML trade-pitch report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, trade direction, or focus. A narrow variant-wedge, expression, or cover-rule request does not trigger this format default.
- For a substantive reusable `economic-impact-report` package or explicit HTML public-equity shock analysis, treat a polished standalone HTML economic-impact report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus. A narrow question about one macro datapoint or named exposure does not trigger this format default.
- For a substantive reusable `scenario-sensitivity-generator` package, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, treat a polished standalone HTML scenario report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, workbook/model output, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus. A narrow request for one sensitivity calculation does not trigger this format default.
- For a substantive standalone `model-audit-tieout` review of an existing model or explicit HTML model-audit request, treat a polished standalone HTML model-audit report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, remediation output, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, materiality, or focus. A narrow formula check does not trigger this format default.
- For a substantive standalone `deck-report-qc` review of an existing deck or report with supporting materials, treat a polished standalone HTML senior-review QC report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, circulation stage, audience/use, or review focus. An embedded QC check inherits the owning workflow's resolved surface and does not create a new HTML report by default.
- For an explicit `initiating coverage` report, substantive `long_only_initiation`, or reusable/source-heavy coverage launch, treat a polished standalone HTML initiation report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, a model/workbook-first deliverable, or a standardized dashboard. In an interactive run, ask only remaining material choices such as depth, audience/use, or focus. A narrow coverage question does not trigger this format default.
- For a substantive `integrated_risk_plan`, reusable position-and-hedge package, or explicit HTML risk-plan request, treat a polished standalone HTML risk decision report as the workflow-resolved format unless the user requests another surface, a quick/no-file answer, workbook output, or a standardized dashboard. In an interactive run, ask only remaining material choices such as loss-budget interpretation, depth, audience/use, or focus. A narrow request for one risk calculation does not trigger this format default.
- A format-only request resolves only the delivery surface. For example,
  "make a doc" can select a Word document, but does not resolve depth,
  audience/use, or analytical focus. Do not silently infer those choices.
- When editing or reviewing an existing deck, workbook, or document, preserve the existing format unless the user asks for conversion. Ask only missing depth, audience/use, or focus questions that change the work.
- Apply a saved reader-facing output preference as a bias only when multiple reader-facing formats are reasonable. Do not let a saved HTML preference override an obvious workbook, deck, document, or existing-artifact workflow. Models, model updates, trackers, workbook audits, workbook-first calculations, deck requests, document requests, and edits to an existing artifact keep their natural format unless the user explicitly asks for conversion.
- Reuse choices already confirmed in the current conversation or workflow.
  Downstream modeling, QC, and dashboard rendering do not ask again unless a new hero artifact creates a consequential unresolved choice.
- Keep preferences in conversational context only; do not add fields to dashboard payloads, workbooks, manifests, run logs, or schemas.

## Native Prompt Contract

If a material choice remains unresolved and `request_user_input` is callable in an interactive runtime, call `request_user_input` before creating the hero artifact:

- Include only unresolved decisions and no more than three questions.
- Supply two or three meaningful options for each question.
- The UI provides a free-form `Other` response automatically; never include an `Other` option in the options list.
- Batch all known material questions into the same `request_user_input` call whenever possible. If deliverable package and analysis assumptions are both unresolved, ask them together up front rather than asking a package question first and a horizon, model-update, scenario, depth, or audience question later.
- Filter deliverable-package choices to surfaces and artifact bundles that are available in the active runtime.
  If a requested format is infeasible, ask for a feasible alternative.
- Put the recommended option first and suffix its label with `(Recommended)`.
- Set `autoResolutionMs` so the picker times out to the recommended option when the user does not answer. Use `120000` milliseconds as the normal timeout, `60000` for lightweight preference checks, and up to `240000` only when the choice materially changes the workflow or artifact. If the timeout resolves automatically, continue with the recommended option and disclose that assumption outside the investor-facing artifact.

If `request_user_input` is unavailable or errors in an interactive run, the missing material choices still require intake: ask all known unresolved material questions together in the next normal chat response and wait for the answer. Use a concise numbered list, front-load the questions before any analysis, and keep the same question set you would have sent to `request_user_input`. For bounded choices, show two or three plain-text options with the recommended/default option first and marked `(Recommended)`; if the tool picker would have relied on its automatic free-form option, include `Other/free-form` as the final plain-chat fallback option. For open-ended issuer, security, portfolio, or source facts, ask a short free-form question. Do not ask the questions one by one unless the user's answer creates a new material ambiguity, and do not silently select deliverable package, depth, horizon, scenario framing, model-update scope, or audience. In a non-interactive run, do not attempt an intake exchange: apply the owning workflow's documented recommended defaults and disclose the assumed deliverable package, format, and depth in the delivery message or accompanying chat summary, not as visible artifact metadata.
For a substantive 60/90-day catalyst calendar, those recommended defaults are a polished standalone HTML artifact and `Full working analysis`.
For an explicit full or reusable/source-heavy post-earnings deep dive, those recommended defaults are a polished standalone HTML post-earnings report and `Full working analysis`.
For an explicit full or reusable/source-heavy pre-earnings preview, those recommended defaults are a polished standalone HTML pre-earnings report and `Full working analysis`.
For an explicit full or reusable/source-heavy event-driven analysis, those recommended defaults are a polished standalone HTML event report and `Full working analysis`.
For a substantive idea-generation screen, market map, watchlist review, or reusable/source-heavy candidate set, those recommended defaults are a polished standalone HTML idea-triage report and `Full working analysis`.
For an investment committee memo, substantive buy-side investment memo, or reusable/source-heavy public-equity memo with unresolved format, those recommended defaults are context-sensitive: `Word document (.docx)` for formal IC, PM, committee, or client memo circulation, `HTML report` for high-confidence source-heavy web-style reports, and `Inline response` for quick or conversational memo updates, with `Full working analysis` unless depth is otherwise clear.
For a substantive reusable meeting-prep packet or explicit HTML meeting brief, those recommended defaults are a polished standalone HTML live-meeting brief and `Full working analysis`.
For a substantive reusable long/short pitch package or explicit HTML trade pitch, those recommended defaults are a polished standalone HTML trade-pitch report and `Full working analysis`.
For a substantive reusable economic-impact-report package or explicit HTML public-equity shock analysis, those recommended defaults are a polished standalone HTML economic-impact report and `Full working analysis`.
For a substantive reusable scenario-sensitivity-generator package, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, those recommended defaults are a polished standalone HTML scenario report and `Full working analysis`.
For a substantive standalone model-audit-tieout review of an existing model or explicit HTML model-audit request, those recommended defaults are a polished standalone HTML model-audit report and `Full working analysis`.
For a substantive standalone deck/report QC review with supporting materials, those recommended defaults are a polished standalone HTML senior-review QC report and `Full working analysis`.
For an explicit initiating coverage report, substantive long-only initiation, or reusable/source-heavy coverage launch, those recommended defaults are a polished standalone HTML initiation report and `Full working analysis`.
For a substantive integrated risk plan, reusable position-and-hedge package, or explicit HTML risk-plan request, those recommended defaults are a polished standalone HTML risk decision report and `Full working analysis`.

When using the interactive chat fallback, ask the grouped questions directly and wait for the answer. Do not suggest switching products or modes instead of asking the unresolved scoping questions.

## Deliverable Package Choices

Use the deliverable-package options for the routed artifact lane. A package option can include more than one artifact when that is likely to match the user's job, such as an HTML dashboard plus an XLSX model update, or a Word memo plus supporting valuation workbook. The recommended option should be context-sensitive: pick the most useful first-read artifact and companion set implied by the prompt, not a fixed favorite format.

| Artifact lane | Options |
| --- | --- |
| Formal IC, PM, committee, client, or research memo | `Word document (.docx) (Recommended)`, `Word document (.docx) + XLSX valuation support`, `HTML report + XLSX valuation support` |
| Source-heavy narrative report, diligence packet, or web-style readout | `HTML report + XLSX model/update support (Recommended)`, `HTML report only`, `Word document (.docx)` |
| Quick memo answer, narrow update, or conversational note | `Inline response (Recommended)`, `Word document (.docx)`, `HTML report` |
| Deck or presentation | `PowerPoint deck (.pptx) (Recommended)`, `PowerPoint deck + XLSX appendix`, `HTML storyboard` |
| Model, schedule, tracker, or tabular package | `XLSX workbook + HTML summary/report (Recommended)`, `XLSX workbook only`, `HTML summary/report only` |
| Dashboard or monitoring view | `HTML dashboard + XLSX tracker/workbook (Recommended)`, `HTML dashboard only`, `XLSX tracker/workbook only` |

For single-artifact prompts, labels such as `HTML report (Recommended)` or `Excel workbook (.xlsx) (Recommended)` remain valid when the user's wording makes the companion unnecessary. A selected presentation package does not eliminate required model, evidence, or QA companions. For example, a valuation model may retain an XLSX workbook even if the requested first-read presentation is HTML. Conversely, if DOCX is offered and selected for a memo, create a real full DOCX rather than a thin companion to HTML.

## Material Ambiguity Choice Sets

Use `request_user_input` for consequential ambiguity. A choice is consequential when it would materially change the lead workflow, deliverable package, first-read artifact, source strategy, reliance standard, analysis horizon, scenario architecture, model-update scope, or the user's next action. Format ambiguity for a new memo, report, note, or briefing is consequential unless the prompt and conversation already make one surface high-confidence. If the prompt gives a strong answer, proceed with that surface and state any assumptions outside the investor-facing artifact.

Do not use the picker merely because several skills could contribute. The router and lead owner should infer the natural path from the prompt whenever possible. Do not ask when the user has already named a format, named a specialist workflow, supplied an existing artifact whose format should be preserved, or asked for a narrow calculation or fact check. Support skills inherit the owning workflow's resolved choices and do not re-prompt.

When the picker is appropriate, keep it tight:

- Ask one question when one fork controls the work.
- Ask up to three questions only when each answer changes the artifact or analysis path.
- If more than three choices are material, prioritize: deliverable package first, then analysis horizon/scope, then audience/use, source posture, or focus depending on what most changes the work. State any remaining assumptions outside the investor-facing artifact.
- Put the context-specific best option first and suffix its label with `(Recommended)`.
- Do not include an `Other` option; the UI supplies it.
- Filter options to choices the active runtime can execute.
- If the picker is unavailable, ask the same unresolved questions together in plain chat with the recommended choices first and include `Other/free-form` where the picker would have supplied an automatic free-form response.

Use these choice sets as reusable patterns, adapting labels to the issuer, event, or artifact named in the prompt:

| Ambiguity | Use when | Options |
| --- | --- | --- |
| Lead workflow direction | A broad public-equity request could reasonably become a research memo, valuation/modeling package, or event/risk workflow. | `Research / memo (Recommended)`, `Model / valuation`, `Event / risk` |
| Source posture | The user asks for source-backed work but does not make clear whether to rely on supplied files, callable/public sources, or a screen-grade answer with gaps. | `Use provided materials (Recommended)`, `Use callable/public sources`, `Proceed screen-grade with gaps` |
| Existing artifact handling | The user provides or references a workbook, tracker, deck, report, or dashboard and wants "update", "review", "fix", or "use this" without stating whether to modify or only assess it. | `Review only (Recommended)`, `Additive copy/update`, `Remediate source artifact` |
| Earnings workflow mode | The request mentions earnings but the timing and expected deliverable are unclear. | `Pre-print preview (Recommended)`, `Post-print deep dive`, `Model/update impact` |
| Portfolio risk mode | A risk prompt could mean position sizing, hedging, or an integrated position-and-hedge plan. | `Position sizing (Recommended)`, `Hedge design`, `Integrated risk plan` |
| Catalyst or tracker scope | The request asks for catalysts, monitoring, or a tracker without specifying issuer breadth or whether to refresh an existing tracker. | `Single-name 60/90-day (Recommended)`, `Portfolio/sector sweep`, `Refresh existing tracker` |
| Scenario package role | A scenario or sensitivity request could be a standalone narrative artifact, a workbook/model overlay, or support for another owner such as event analysis or valuation. | `Standalone scenario report (Recommended)`, `Workbook/model overlay`, `Support for another workflow` |
| Valuation horizon | A DCF, comps valuation, model update, initiation, long/short pitch, thesis tracker, or scenario package needs forecast period or target horizon and the prompt does not make it clear. | `5-year forecast / DCF base (Recommended)`, `3-year estimate bridge`, `10-year long-range case` |
| Model-update scope | A model update request leaves whether the user needs a quick estimate bridge, key-driver refresh, or full model rebuild unresolved. | `Update key drivers and valuation (Recommended)`, `Full three-statement refresh`, `Quick estimate bridge` |
| Investment scenario framing | A thesis, valuation, event, or risk request could use materially different case architecture. | `Base / bull / bear with thesis disconfirmers (Recommended)`, `Downside-first risk case`, `Upside / variant case` |

For a substantive single-company 60/90-day `catalyst-calendar`, the default presentation surface is a polished HTML catalyst calendar rather than an `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that calendar default.

For an explicit post-earnings `deep dive`, `full report`, or reusable/source-heavy post-print package, the default presentation surface is a polished standalone HTML post-earnings report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that deep-dive default.

For an explicit `pre-earnings preview`, `full preview report`, or reusable/source-heavy pre-print package, the default presentation surface is a polished standalone HTML pre-earnings report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that preview-report default.

For an explicit `full event analysis`, `full event report`, or reusable/source-heavy special-situations package, the default presentation surface is a polished standalone HTML event report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that event-report default.

For a substantive `idea-generation` screen, market map, watchlist review, or reusable/source-heavy candidate set, the default presentation surface is a polished standalone HTML idea-triage report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or the requested job no longer fits that idea-triage default.

For an investment committee memo, substantive buy-side investment memo, or reusable/source-heavy public-equity memo, do not default to HTML merely because the request says "memo." Ask the deliverable-package question when the surface or companion package is semi-ambiguous. Recommend `Word document (.docx)` for formal IC, PM, committee, or client memo circulation; recommend HTML only when the prompt clearly calls for a source-heavy web-style report; recommend inline for quick or conversational memo updates. Do not route ordinary memo work to a standardized dashboard unless explicitly requested.

For a substantive reusable `meeting-prep` packet or explicit HTML meeting brief, the default presentation surface is a polished standalone HTML live-meeting brief rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `long-short-pitch` package or explicit HTML trade pitch, the default presentation surface is a polished standalone HTML trade-pitch report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `economic-impact-report` package or explicit HTML public-equity shock analysis, the default presentation surface is a polished standalone HTML economic-impact report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For a substantive reusable `scenario-sensitivity-generator` package, explicit HTML scenario report, or sourced discrete-event success/delay/break overlay, the default presentation surface is a polished standalone HTML scenario report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, workbook/model output, or explicitly request a standardized dashboard.

For a substantive standalone `model-audit-tieout` review of an existing model or explicit HTML model-audit request, the default presentation surface is a polished standalone HTML model-audit report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, remediation output, or explicitly request a standardized dashboard.

For a substantive standalone `deck-report-qc` review of an existing deck or report with supporting materials, the default presentation surface is a polished standalone HTML senior-review QC report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output or explicitly request a standardized dashboard.

For an explicit `initiating coverage` report, substantive `long_only_initiation`, or reusable/source-heavy coverage launch, the default presentation surface is a polished standalone HTML initiation report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, a model/workbook-first deliverable, or explicitly request a standardized dashboard.

For a substantive `integrated_risk_plan`, reusable position-and-hedge package, or explicit HTML risk-plan request, the default presentation surface is a polished standalone HTML risk decision report rather than a standardized `HTML dashboard`. Do not ask the user to select a format unless they request an alternate output, workbook output, or explicitly request a standardized dashboard.

## Depth And Framing

If depth is unresolved, offer:

- `Focused first pass`: top drivers, risks, targeted analysis, and next questions.
- `Full working analysis (Recommended)`: the normal complete working artifact.
- `Deep diligence package`: expanded scenarios, supporting tables, evidence requests, and appendices.

Depth is not readiness. Deep analysis does not permit PM-ready, client-ready,
committee-ready, publication-ready, or decision-grade language without the source and review gates required by the owning skill.

Use the third question slot for audience/use when it could change tone,
decision framing, disclosure, or delivery:

- `PM or investment team`
- `Client or research audience`
- `Internal committee`

If audience is known or immaterial and the requested work remains broad, ask for focus instead:

- `Thesis / catalysts`
- `Valuation / estimates`
- `Risk / monitoring`

## Expected Behavior

- A new model or valuation-package request with no stated package asks for deliverable package, depth, and any consequential audience/use preference before building, recommending `XLSX workbook + HTML summary/report (Recommended)` when both an editable model and first-read summary would help.
- A broad valuation or model-update request with no high-confidence package or horizon should ask deliverable package and valuation horizon/model-update scope in the same `request_user_input` call, recommending `XLSX workbook + HTML summary/report (Recommended)` and `5-year forecast / DCF base (Recommended)` unless the prompt points elsewhere.
- A dashboard/report/model request that could plausibly require both a reader-facing view and editable analysis may recommend a combined package such as `HTML dashboard + XLSX tracker/workbook (Recommended)`, with single-artifact alternatives like `HTML dashboard only` or `XLSX tracker/workbook only`.
- An explicit HTML research report request skips the deliverable-package question unless the prompt also leaves a material XLSX/model companion unresolved.
- "Make a doc about why Duolingo's stock has plummeted since last May"
  resolves Word format only and still asks for unresolved depth and audience before research begins.
- A review of an existing workbook preserves `.xlsx` as its selected surface.
- An analysis owner that has already collected preferences passes them through to model, QC, and `dashboard-builder` steps without repeated prompts.
- A substantive single-company 60/90-day catalyst-calendar request with no selected format or depth defaults to a polished HTML catalyst calendar; in an interactive run it asks for unresolved depth without blocking on format,
  and in a non-interactive run it proceeds with full working analysis and states those assumptions in the delivery message rather than in the investor-facing artifact.
- An explicit post-earnings deep dive or reusable/source-heavy post-print package with no selected format defaults to a polished standalone HTML post-earnings report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit pre-earnings preview or reusable/source-heavy pre-print package with no selected format defaults to a polished standalone HTML pre-earnings report; in an interactive run it asks only for unresolved depth,
  audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit full event analysis or reusable/source-heavy special-situations package with no selected format defaults to a polished standalone HTML event report; in an interactive run it asks only for unresolved depth,
  audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive idea-generation screen, market map, watchlist review, or reusable/source-heavy candidate set with no selected format defaults to a polished standalone HTML idea-triage report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An investment committee memo, substantive buy-side investment memo, or reusable/source-heavy public-equity memo with no high-confidence surface asks for deliverable package before drafting; it normally recommends `Word document (.docx)` for formal memo circulation, HTML for source-heavy web-style reports, and inline for quick memo updates. When valuation, estimate bridge, catalyst, or scenario support would plausibly matter, one option should offer a Word memo plus XLSX valuation support.
- Regression prompt: `Prepare an investment committee memo on this company` with no selected or high-confidence surface should make the first action `request_user_input` with `Word document (.docx) (Recommended)`, `Word document (.docx) + XLSX valuation support`, and `HTML report + XLSX valuation support`.
- A substantive reusable meeting-prep packet or explicit HTML meeting brief defaults to a polished standalone HTML live-meeting brief; in an interactive run it asks only for unresolved depth, audience/use, meeting type, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive reusable long/short pitch package or explicit HTML trade pitch defaults to a polished standalone HTML trade-pitch report; in an interactive run it asks only for unresolved depth, audience/use, trade direction, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive reusable economic-impact-report package or explicit HTML public-equity shock analysis defaults to a polished standalone HTML economic-impact report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive standalone model-audit-tieout review of an existing model or explicit HTML model-audit request defaults to a polished standalone HTML model-audit report; in an interactive run it asks only for unresolved depth, audience/use, materiality, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive standalone deck/report QC review with supporting materials and no selected format defaults to a polished standalone HTML senior-review QC report; in an interactive run it asks only for unresolved depth, circulation stage, audience/use, or review focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- An explicit initiating coverage report, substantive long-only initiation, or reusable/source-heavy coverage launch with no selected format defaults to a polished standalone HTML initiation report; in an interactive run it asks only for unresolved depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing those assumptions outside the artifact.
- A substantive integrated risk plan, reusable position-and-hedge package, or explicit HTML risk-plan request with no selected format defaults to a polished standalone HTML risk decision report; in an interactive run it asks only for unresolved loss-budget interpretation, depth, audience/use, or focus, and in a non-interactive run it proceeds with full working analysis while disclosing assumptions outside the artifact.
