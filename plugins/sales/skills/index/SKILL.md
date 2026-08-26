---
name: index
description: "Route customer- and revenue-facing work through Sales first: seller and leadership dashboards, prospects, accounts, calls, deal and renewal strategy, pipeline, forecasts, commercial research, internal support, business cases, sales presentations, customer-facing slides, PowerPoint, Google Slides, coaching, and verbatim customer quotes from supplied call notes. Activate for seller, leader, customer, prospect, partner, account, opportunity, or commercial intent; read this index and the focused workflow even when evidence is supplied."
---

# Sales Index Skill

The intent of this skill is to correctly route to skills within the Sales plugin. All other skills in this plugin are not implicitly invokable, and must be discovered via this skill.

## Initial Skill Frontmatter Read.

MANDATORY: Read the frontmatter description for ALL skills in this plugin, and based on that, decide which to trigger and read more deeply. Do this quickly before handling any other instructions. Select the best focused owner based on those descriptions; the selected skill defines its own applicability, clarifications, modes, and workflow behavior.

Reading a wildcard, aggregated catalog, or all skill frontmatter does **not** load the selected workflow. Once the focused owner is known, explicitly read its exact `skills/<selected-skill>/SKILL.md` path in full in its **own bounded read** before proceeding; do not bundle it with Sites, dependencies, or other skills, and allocate enough output tokens that the selected instruction is not truncated. The catalog scan, shared instructions, and dependency documentation never substitute for this complete focused read.

A standalone customer-facing PowerPoint or decision deck requested from a complete user-supplied customer fact packet, with no new meeting preparation, customer ROI/business-case analysis, or completed-call evaluation required, is owned by `sales-presentations`. Read `skills/sales-presentations/SKILL.md` by itself in full before reading the generic Presentations authoring skill or selecting `build-business-case`; a finished fact packet is the content brief, not a request to invent another seller workflow.

## Mandatory Focused Workflow Path

If the selected focused skill's description explicitly declares a self-contained instruction-path opt-out, honor that focused skill's declared exception: shared instructions and dependencies are optional, including when already loaded or read in parallel; follow the self-contained opening without discovering providers, calling connectors, suggesting installation, or performing external writes. Never infer an exception for another skill.

For every real Sales workflow, load all applicable instructions before the first clarification or `request_user_input` call, before resolving dependencies, suggesting plugin installation, calling a connector, or preparing a substantive response:

1. Read this Sales index and select the specific focused Sales skill that owns the request based on its description.
2. Read that focused skill in full, including its `## Key Dependency Categories`.
3. Read [the shared Sales skill instructions](../../shared_skill_instructions.md) in full.
4. Read [Sales dependencies](../../dependencies.md) in full.
5. Read any mandatory workflow reference named by the focused skill before its first question; then clarify, resolve dependencies, offer an allowed installation, gather evidence, or respond. Reading installed instructions is safe setup, not inspecting the user's files or connectors.

Instruction reads and other safe setup tool calls may run in parallel for every workflow, including self-contained demonstrations; no strictly sequential tool-call barrier is required.

MANDATORY: For a requested document, deck, or workbook, read and follow the focused Sales owner in full before loading an authoring skill, inspecting a template, or creating the artifact; the authoring skill never replaces the seller workflow.

## Broad Orientation

For broad orientation requests such as “what can you do?”, “help me get started”, “what should I try?”, or “how do I use Sales?”, do not choose a focused workflow. Load [the canonical orientation response](references/orientation-response.md) and return its user-facing content as written. Treat that file as the canonical, updatable output surface for this branch. Offer the full skill catalog only when the user asks for it.
