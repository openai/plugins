---
name: build-business-case
description: Own customer-led business cases, ROI or value analyses and models, pricing or investment rationales, customer-ready value stories, and buyer-ready commercial decision decks, including requests to turn customer ROI analysis into a decision deck. Review commercial proposals and build 8-12 slide proposal or value-case decks tied to a customer, workflow, initiative, or buying decision before handing visual authoring to the presentation partner.
---

# Build Business Case

Turn uneven account evidence into a customer-led, decision-useful value case. This skill owns the business-case logic and drafts, including the content of requested value-case presentations; delegate visual design and artifact creation to the appropriate authoring skill.

Start with the customer, not the product. Follow this chain on every run:

`customer context -> account-native anchor -> workflow -> use case -> value drivers -> metrics -> quantified impact -> narrative -> public research when useful`

If the evidence cannot support credible math, produce a clearly labeled structural case and the smallest validation plan needed to make it finance-ready.

## Common Skill Instructions

MANDATORY: If they are not already in context, read and follow [the shared Sales skill instructions](../../shared_skill_instructions.md).

## Key Dependency Categories

Use only lanes that materially improve the case.

- [Blocking] ~~CRM for authoritative account, opportunity, owner, stage, amount, close timing, contacts, and commercial context. It blocks customer/account-specific cases unless authoritative account and commercial context is already grounded; generic scenario cases can proceed without it.
- ~~Meeting Transcripts for discovery evidence, stakeholder language, workflow pain, objections, quantified claims, decisions, and validation gaps
- ~~Knowledge & Files for account plans, source packs, discovery notes, prior value cases, proof points, and account-native metrics
- ~~Sales Intelligence only when company, fit, stakeholder, or market context closes a specific evidence gap

Use public research only when it sharpens strategic priorities, executive wording, operating pressure, or “why now.” Prefer company-controlled, investor, regulatory, and other primary sources. Never let public or enrichment context substitute for customer-confirmed pain, workflow metrics, decision process, or CRM-owned truth.

## Reference Loading

`SKILL.md` owns the normal customer-led flow, evidence order, guardrails, and default package. Load references only when their extra detail matters:

- Use [references/input-and-output.md](references/input-and-output.md) when inputs are uneven, the user names an output mode, or the full required-content contract matters.
- Use [references/workflow.md](references/workflow.md) when a complex case needs the expanded customer-to-value sequence and examples.
- Use [references/value-model-and-evidence.md](references/value-model-and-evidence.md) when quantification, confidence labeling, evidence conflict, or value-bucket logic needs more detail.
- Use [references/output-and-presentation.md](references/output-and-presentation.md) only for a formatted artifact, exact presentation/output requirements, or behavior tests.

## Workflow Guidance

### 1. Resolve the customer and decision anchor

- Require a customer/account/scenario and a workflow, initiative, pain, metric goal, or decision context. Proceed from pasted notes, links, exports, or a clearly anchored thread when sufficient.
- A clearly identified team and workflow are sufficient for a generic scenario: deliver a structural case with value hypotheses, symbolic formulas, missing inputs, and a short measurement plan before asking for baselines or buyer details.
- If an inferred required anchor is ambiguous, make a bounded pass using at most three source reads, offer up to three concrete candidates, and ask the user to choose before broad enrichment.
- Treat company-like names as possible account anchors. When ~~CRM is available, resolve the account and matching opportunity before relying on indirect context.
- If the customer and workflow are both too weak for a stable hypothesis, ask only the smallest clarifying question.

### 2. Find the account-native anchor first

- Start with user-provided metrics, notes, links, or exports. Otherwise look for the highest-signal account-native artifact before broad search: exact-match ~~Knowledge & Files queries such as `[customer] business case`, `value case`, `ROI`, `pilot target`, or `expansion path`; then the matching ~~CRM opportunity; then relevant ~~Meeting Transcripts.
- Fetch the strongest anchor first. High-signal anchors contain the named customer, workflow, decision audience, commercial stakes, metrics, urgency, or caveats.
- Use adjacent sources only to validate material gaps such as workflow pain, approval path, budget ownership, timing, risks, or customer-facing follow-up.
- Preserve commercial anchors from account-native evidence, including pilot amount, expansion path, target value, budget range, close timing, and paid-pilot terms. If CRM is thin, keep the sourced fact and separately name the CRM gap.
  - Example: `Known from ~~Knowledge & Files source pack: SGD 420K pilot target and SGD 1.8M expansion path. Missing from ~~CRM: opportunity stage, owner, and close date.`
- Stop the first pass once the core case is supported; do not continue low-yield searches merely because more sources exist.
- For a named public company, run a focused public-primary pass unless the user disables it or the account-native anchor already answers the material why-now question. Use it to sharpen strategic priorities and executive wording, never to delay the first useful case or replace account-native proof.

### 3. Build the customer value logic

- Name the customer objective, business pressure, relevant buyer or team, constraints, and actual workflow before naming seller capabilities.
- Describe the workflow in business language: actors, steps, handoffs, bottlenecks, tools, KPIs, and what good looks like.
- Prioritize one to three use cases. For each, explain the workflow problem, why it matters now, who cares, supporting evidence, and remaining validation.
- Map each use case to the fewest applicable value buckets: `Enhanced Productivity`, `Cost Reduction`, `Risk Reduction`, `Revenue Acceleration`, and `Time to Market`.
- Make the causal chain explicit: workflow change -> operational effect -> business outcome -> metric.

### 4. Quantify only what the evidence supports

- Label material claims and inputs as `Known`, `Inferred`, `Assumed`, or `Missing`.
- Use this evidence order when sources conflict: customer-provided metrics; product telemetry or usage data; discovery or transcript evidence; ~~CRM, ~~Knowledge & Files, or internal account notes; public primary materials; analogous wins or directional benchmarks.
- For a finance-ready case, show formula, inputs, source/label, low/base/high scenarios, caveats, and confidence. Useful formula patterns include:
  - Productivity: `users x tasks per period x time saved per task x labor cost x adoption rate`
  - Cost: `current cost baseline - future cost baseline`
  - Risk: `incidents avoided x average cost per incident x confidence factor`
  - Revenue: `impacted revenue pool x improvement rate x confidence factor`
  - Time to Market: `cycle-time reduction x value of earlier release or deployment`
- If required inputs are missing, keep the math structural: show the formula, mark missing inputs, state what can be said directionally, and list the smallest questions that would make it finance-ready.

### 5. Draft the decision-useful package

- Translate operational impact into the customer’s business outcomes, then explain why the seller solution fits this workflow and buyer need.
- Keep public strategic context separate from account-native proof. Use analogous wins as support for a hypothesis, never as proof for this customer.
- Cite material claims with useful clickable links when available; use a plain source label only when no stable link exists.
- When the user requests a value-case document or deck, finish this business-case workflow before loading the matching authoring skill: use Google Slides for a native Slides deck, Presentations for PowerPoint, Google Docs for a native document, or Documents for Word. The explicitly requested artifact is the first deliverable, not an optional follow-up.
- Directly read the exact supplied template, existing file, workbook, and other named sources before composition. Preserve the template's actual masters, layouts, typography, branding, and placeholders; reuse or copy the specified template without modifying its original unless the user explicitly requests an in-place update.
- Carry grounded decision logic, customer evidence, formulas, missing inputs, caveats, and source links into the artifact. Create only the requested unshared output, verify its substantive finished content by readback, and return its real link; do not invent a template, file, source, ROI, or completed deliverable.

### 6. Build the Decision Deck

- For an explicitly requested customer ROI, commercial proposal, business-case, or decision deck, this selected business-case skill remains the seller-workflow owner. Read and follow [Sales Presentations](../sales-presentations/SKILL.md) as the downstream presentation partner before a substantive final response, gathering evidence, or invoking an artifact-authoring skill.
- If the user accepts a deck offer after the case is complete, read and follow [Sales Presentations](../sales-presentations/SKILL.md) at that point. Turn this exact case into the deck; do not restart as a generic product overview.
- After a substantive default or finance-ready case, prefer this as the single next-step offer unless the user has already requested another follow-up.
- Build an 8-12 slide decision deck: executive summary; what we heard; prioritized workflows/use cases; proposed solution; value model and assumptions; commercial structure; deployment, security, and governance; proof; recommended proposal structure; sources/open questions; and the decision requested. Combine or move sections to an appendix when evidence or audience warrants.
- Make the commercial choice legible: connect persona and workload to product surface, capacity or cost model, governance, and expected value. Keep unconfirmed pricing, ROI, eligibility, and terms visibly labeled.

### Next Step Options

After the first output, offer the most relevant follow-up from the options below. Offer one clear transition, not a menu. Suggest ONLY these unless you are very confident another option is more useful:
- Improve the case using the user's guidance or close the smallest material validation gap.
- Produce a customer-ready executive summary or value narrative for review.
- Produce a champion talk track or internal account-team note for review.
- Build a value-model table or spreadsheet-ready model structure.
- Turn the reviewed case into an 8-12 slide customer decision deck using `@presentations`.
- Turn the case into a concise meeting pre-read or decision document after the content is reviewed.

Next steps to avoid:
- Saving, sharing, posting, creating a document, or updating a system before the user reviews the content and explicitly requests that action.

### Mandatory Deck Offer

- End every successful non-deck output with this exact final line: `Would you like me to turn this into an 8–12 slide customer decision deck using @presentations?`
- Treat this as the one required next-step transition; do not append a competing menu or another offer after it.
- Skip it only when the user already requested or received the deck, explicitly declined slides, or the workflow is blocked before producing a usable case.

## Modes

- `Default Package` — the full business case below.
- `Structural Case` — use when the customer and workflow are clear but credible quantified inputs are missing.
- `Finance-Ready Case` — use when sourced inputs support formulas and low/base/high scenarios.
- `Focused Output` — use when the user asks only for an executive summary, ROI table, customer-ready narrative, differentiators, or validation questions; include a compact evidence posture and gaps.
- `Decision Deck` — use when the user explicitly requests or accepts a customer-facing commercial proposal or executive decision presentation.

## Output Format

Use this structure for the default package.

```md
# Business Case: [Customer / Initiative]

## Executive Summary
[Customer objective, why now, priority workflow/use cases, likely value story, seller fit, and confidence.]

## Strategic Initiatives
- [Known/Inferred/Assumed/Missing: initiative + source]

## Key Challenges
- [Customer or workflow challenge + evidence label/source]

## Priority Workflows
- **[Workflow]:** [Actors, bottleneck, KPI, and why it matters]

## Priority Use Cases
1. **[Use case]** — [Problem, buyer/team, why now, evidence, validation gap]

## Value Hypothesis by Use Case
| Use Case | Value Bucket | Causal Chain | Evidence Posture | Confidence |
| --- | --- | --- | --- | --- |
| [Use case] | [Exact bucket] | [Change -> effect -> outcome -> metric] | [Known/Inferred/Assumed/Missing] | [High/Medium/Low] |

## Metrics and Assumptions
| Metric / Input | Value | Label | Source | Why It Matters |
| --- | --- | --- | --- | --- |
| [Input] | [Value or Missing] | [Known/Inferred/Assumed/Missing] | [Link/label] | [Formula role] |

## ROI or Value View
| Use Case | Formula | Low | Base | High | Caveats |
| --- | --- | --- | --- | --- | --- |
| [Use case] | [Formula] | [Value/Structural] | [Value/Structural] | [Value/Structural] | [Gap/confidence] |

## Solution Differentiators
- [Differentiator tied to workflow, buyer need, and expected business effect]

## Proof Points or Analogous Wins
- **Account-native proof:** [Evidence or Missing]
- **Analogous / public support:** [Evidence, clearly not customer proof]

## Caveats and Open Questions
- [Most important validation gap and smallest next collection step]

---

{Follow the instructions and output format/conditions in [Limitations and Improvements](../../shared_skill_instructions.md#limitations-and-improvements)}

{Follow the instructions and output format/conditions in [Next Steps](../../shared_skill_instructions.md#4-offer-one-next-step)}
```

## Rules

- Do not invent customer numbers, buyers, workflow owners, tools, approvals, commercial terms, ROI, or source links.
- Do not turn public strategic language, benchmarks, or analogous wins into customer-confirmed impact.
- Do not hide missing data behind polished prose; say whether the case is structural or finance-ready and why.
- Prioritize one to three use cases and the fewest value buckets that explain the decision.
- Keep this workflow read-only unless the user explicitly requests a specific document or presentation; that request authorizes creating or updating only the requested artifact. Do not post, send, share, update CRM, modify the original template, or create unrelated files.

## Failure Handling

If no credible customer/workflow anchor exists, state the blocker and ask for the smallest missing input. If optional lanes are unavailable, continue with the strongest grounded evidence and make the resulting confidence limits visible.
