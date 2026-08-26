---
name: sales-presentations
description: Use for explicitly requested customer-facing PowerPoint or Google Slides creation from an already completed meeting brief or approved customer proposal, or a complete user-supplied customer fact packet needing a standalone buyer-ready decision deck without new seller analysis. Use as the presentation partner for finished seller-workflow outputs; ongoing meeting preparation, customer ROI or business-case analysis, buyer-ready decision-deck development requiring new seller analysis, and completed-call evaluation belong to their respective seller workflows.
---

# Sales Presentations

## Common Skill Instructions

MANDATORY: If the Sales index has not genuinely been read in this conversation, read [the Sales index](../index/SKILL.md), then reread this focused skill in full before continuing.

MANDATORY: If they are not already in context, read and follow [the shared Sales skill instructions](../../shared_skill_instructions.md).

## Key Dependency Categories

- [Blocking] ~~Presentation Authoring for creating the requested editable PowerPoint or Google Slides deck through the available [@Presentations](plugin://presentations@openai-primary-runtime) capability.
- ~~Knowledge & Files for the supplied template, source deck, customer materials, and reviewed account evidence.

Turn the current Sales workflow output and its evidence into a customer-facing decision narrative. This skill owns sales-specific narrative, audience, and safety guidance; the latest [@presentations](plugin://presentations@openai-primary-runtime) plugin owns slide authoring, template handling, rendering, and visual QA.

## Invocation

- Use this skill only when the user explicitly requests a deck or accepts a deck offer. If the initial request already asks for slides, complete the triggering Sales workflow and build the deck in the same run.
- Treat the triggering question and the immediately preceding or current Sales output as the content brief. Build the deck directly from that material; do not replace it with a generic company or product pitch.
- After completing the focused and shared Sales instruction chain, resolve the blocking `@presentations` capability before inspecting templates, loading artifact helpers, or drafting. Read and follow its installed skill immediately before authoring. If it is unavailable, use the native plugin-install surface when available; if installation is unavailable or declined, explain that an editable deck cannot be created without that capability. Never recover an excluded plugin from a global cache, substitute another slide implementation, or repeat a declined offer.
- Produce the requested editable deck, not only an outline. Preserve the source package and cited evidence so later edits remain grounded.

## Customer-Facing Standard

- Write for the named customer and meeting audience. Start with their priorities, workflows, requirements, and decision; introduce the seller solution only as the response.
- Build a clear arc: customer context -> what matters -> recommended approach -> value or proof -> risks and plan -> decision or next step.
- Give each slide one decision-useful takeaway and use a conclusion-style headline. Prefer customer language and direct answers over product taxonomy or feature inventories.
- Keep the deck customer-safe. Exclude internal strategy, opportunity probability, negotiation posture, margins, unverified competitive claims, private CRM notes, and seller-only coaching.
- Preserve evidence posture. Label assumptions, ranges, open questions, and dependencies; never convert an inference or benchmark into a customer-confirmed fact. Put useful citations near material claims and include a compact sources/assumptions appendix when needed.
- For enterprise evaluation decks, emulate the strongest CompuCom pattern: organize around the buyer's questions, lead each section with a direct answer, separate confirmed capability from caveat or availability, map personas/workloads to solution and cost, and close with a recommendation, sources, assumptions, owners, and next decision.

## Template Choice

- Follow the latest `@presentations` template precedence: use a supplied customer or company deck as the visual source; otherwise honor explicit style direction; otherwise use a current built-in template.
- When visual choice would materially help, offer up to three concise options before authoring: exact named templates currently exposed by `@presentations`, a customer-supplied brand/template deck, or a clearly labeled custom treatment. Never invent a built-in template name.
- Recommend **Codex Grid Layout Library** when it is available and the deck needs a restrained, evidence-led executive style. A CompuCom-inspired clean customer briefing is a custom treatment, not a built-in template.
- Do not block on template choice when the user has no preference; use the current `@presentations` default.

## Deck Rules

- Use 16:9 unless the user or source template requires another format.
- Use the slide count and narrative pattern defined by the triggering Sales skill. Add an appendix for detailed assumptions, Q&A, or sources rather than crowding the core story.
- Prefer simple native diagrams only when they clarify architecture, workflow, operating model, or rollout. Use charts and tables as evidence, not decoration.
- Keep commercial, security, integration, and deployment claims time-bounded and source-backed. Treat the final proposal, order form, security documentation, or other contract-specific source as authoritative where applicable.
- End with a concrete customer decision, discussion, or next step. Do not end on a generic product summary.
