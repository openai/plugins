---
name: google-slides
description: Google Slides work for finding, reading, summarizing, creating, importing, template following, visual cleanup, source-deck adaptation, structural repair, and content edits in native Slides decks.
---

# Google Slides

Use this skill for Google Slides work in Codex local-plugin sessions.

## Purpose Of This File

This file is intentionally minimal and only covers:

1. connector loading and runtime boundaries in the Codex `node_repl` world
2. mandatory routing to reference files
3. routing to workflow references

Detailed write, chart, thumbnail, creation, and final-pass rules live in `references/`.
Latency is not a constraint for this skill, so always read the relevant reference files before performing the task.

The active/main agent must personally read this file and every relevant reference file in the current turn. Do not delegate reference-file reading or summarization to a subagent and then rely on that summary for the workflow. This is not a general prohibition on subagents: they may still be used for other well-scoped execution, extraction, or QA work after the main agent has loaded the applicable skill guidance itself.

## Runtime Model

1. Use Google Slides connector or app tools directly from Codex when they are available.
2. Use `node_repl` only for source processing or small JavaScript utilities that are not connector calls.
3. Do not use embedded-runtime helper snippets or assumed global connector bindings.
4. Connector tools are not called from inside `node_repl`. Treat connector calls and `node_repl` helper work as separate execution surfaces.
5. Browser Use is not the Slides editing path. Use connector reads, slide structure, and thumbnails.

## Default Routing

Unless the user asks otherwise:

1. New deck from a provided native Google Slides template or reference deck: copy the provided deck directly in Google Drive, then use Slides `batchUpdate` on the copy. Read `references/reference-template-reference-deck-copy-workflow.md`.
2. Net-new Google Slides deck without a provided native Slides template or reference deck: use `[@presentations](plugin://presentations@openai-primary-runtime)` to create a local `.pptx` first. Then read `references/reference-import-presentation.md` and import with `mcp__codex_apps__google_drive_import_presentation` using `upload_mode: "native_google_slides"`.
3. If the Presentations plugin is unavailable for a net-new deck that does not use the native Slides copy workflow, do not create the deck directly. Report that the required local Presentations authoring path is unavailable.
4. Existing Google Slides reads, summaries, edits, comments, and template-preserving modifications: use Google Slides connector or app tools directly.

For net-new Google Slides without a provided native Slides template or reference deck, the PPTX-import path is the only currently supported high-quality workflow. Do not create a blank Google Slides deck and fill it with Google Slides write APIs, use Computer Use, use Browser Use, or build the deck directly in Google Drive unless the user explicitly asks for that alternate workflow. If they do, mention first that output quality is expected to be best when a local `.pptx` is imported through the Google Drive plugin.

For new decks from a provided native Google Slides template or reference deck, do not create a local `.pptx` first. Copy the provided deck directly, treat the copy as the destination deck, and create/edit slides there with `batchUpdate` using duplicated exemplar slides or layouts from the copied deck. Populate existing template objects first: replace text, images, charts, tables, and placeholder content in the copied slide's existing slots instead of adding new primary content boxes.

The slide-planning, archetype-selection, hierarchy, semantic-emphasis, evidence-legibility, and deck-consistency rules apply across both creation paths and to slides added to existing decks. Only source-parity requirements such as exact text preservation, speaker-note parity, and media-ID parity depend on a source-based adaptation or migration request.

The import reference owns the exact connector action, plugin install/reinstall handling, native-conversion verification, post-import verification, and cleanup expectations. Read it before any net-new Google Slides import attempt.

For imports and any explicit direct-create override, wait for the write action to complete, then perform connector readback or Drive metadata readback before returning a Google Slides URL or presentation id. Use only a URL or id observed from the completed connector result or readback. Do not synthesize or predict Google Slides URLs, and do not present a URL as ready if readback fails.

## Non-Negotiable Output Invariant

Inserted or edited content must match the target deck's existing structure and connector-observable presentation closely enough that it reads as native deck content. Net-new slides must use a coherent archetype, hierarchy, and visual system rather than an arbitrary collection of objects.
Treat wrong target deck, wrong slide, stale object IDs, missing chart updates, leftover placeholder or template sample text, empty or unresolved placeholder objects, primary content placed in newly created freeform boxes while an inherited or template slot remains unused, clipped text, broken slide order, or unverified visible layout changes as failed output that must be corrected before handoff.

For Slides batch updates, API success is not completion. A fresh post-write LARGE thumbnail and examining the image by curling it is required for every touched slide. You MUST curl the image after requesting thumbnail. No skip.
For net-new Google Slides without a provided native Slides template or reference deck, create a local `.pptx` with `[@presentations](plugin://presentations@openai-primary-runtime)` and import it to Google Drive with `upload_mode: "native_google_slides"`.

## Canonical Workflow Bias

Prefer one simple proven workflow over a large tree of recovery branches.
When a task matches a known successful pattern, follow that pattern directly instead of re-evaluating every possible insertion or fallback path.
Do not let accumulated edge-case guardrails turn a straightforward Slides task into a long blocker-analysis exercise.

For deck creation and editing tasks, prefer this general sequence when viable:

1. gather the required source material
2. attach to or create the destination presentation
3. read the deck structure and target slides
4. establish the slide checklist or slide plan
5. write small, grounded batches with live object IDs
6. verify through connector readback and post-batch thumbnails
7. stop once the deck is clean, complete, and scannable

If a simple verified workflow is viable, use it. Do not drift into speculative alternate paths.

## Release-Blocker Checklist

Before final handoff, explicitly verify these with connector readback and thumbnails where relevant:

1. the target presentation id, title, and URL are the intended deck
2. every edited slide in scope was read after the write
3. every slide touched by a batch update has a fresh post-write thumbnail check
4. every changed chart is refreshed or replaced in the intended footprint, with obsolete placeholder text removed unless the user asked to keep it
5. every new or edited shape, image, table, and text box stays inside the slide bounds unless intentionally full-bleed
6. no slide in a multi-slide task was skipped, duplicated, or left in a mixed old/new state
7. duplicated slides that needed reordering were moved only after a post-duplicate readback, with `slideObjectIds` listed in current presentation order
8. no visual property is claimed as verified unless connector data or a fresh thumbnail supports it
9. final presentation output is an editable Google Slides deck, not one PNG per slide; verify editable components with `mcp__codex_apps__google_drive_get_presentation` or `mcp__codex_apps__google_drive_get_slide`
10. for imports and direct creates, the final returned URL or presentation id came from a completed connector result or readback, not a predicted Google Slides URL
11. for template/reference-deck copies, the final returned URL or presentation id came from the completed copy result or readback, not from the source deck or a predicted URL
12. Even when a local pptx was created for an import workflow, do not cite the local pptx path as a deliverable in your final answer. Your final answer must only reference the verified gsuite link.
13. for any slide inserted from a layout (`slideLayoutReference`, `predefinedLayout`, or inherited master/layout placeholders), every inherited placeholder object was populated, replaced, or intentionally deleted; do not rely on thumbnails alone because empty placeholders can be invisible
14. for template/reference-deck copies, full `get_presentation` or per-slide `get_slide` readback was used for final structural validation; `get_presentation_outline` alone is insufficient
15. for template/reference-deck copies, content-bearing placeholders and reusable template objects were used where they exist; newly created primary text/image boxes are justified by the chosen slide plan, not a shortcut around the template
16. when adapting or migrating provided source material, source-to-destination fidelity was checked for substantive text, visuals, charts, tables, links, media type and source identifier when active/accessible, and non-empty speaker notes; no required source content disappeared or was silently summarized
17. text hierarchy and layout semantics remain meaningful: mixed heading/body style runs were not flattened, blank bulleted paragraphs do not render stray bullets, and inherited emphasis does not imply unsupported totals, rankings, categories, status, or importance
18. visual evidence is presentation-readable, not merely unclipped: crops preserve essential regions, important labels and footnotes remain legible, and landscape evidence was not forced into an unsuitable portrait frame
19. no generic editor prompts, bracketed instructions, sample copy, lorem ipsum, old-event content, or other template scaffolding remains unless explicitly requested by the user

**Slides**

* Content: ensure the content covers everything requested by the user and ensure the storytelling of the overall deck is coherent.
* Search: use `web.run`'s `image_query` for efficient image search instead of `search_query`.
* Visual assets: DO NOT use Python to draw any images; DO NOT use programmatic vector shapes for visuals; DO NOT use programmatic drawings of any sort. Use image search or imagegen instead! By default, DO NOT reuse the same image more than once (unless it's a background). Not only do you need to prepare visuals for the main concept, you also need to get decorative visuals. Before sourcing or generating visuals, be mindful of the desired aspect ratio, placement, and cropping options on the slide. For example, if you intend to place text to the left of the image containing a person, you should ask imagegen to put the person on the right side of the image.
* Default styling: use one composition instead of a collection of UI panels. UI-like styling typically includes card grids, pills, badges, button-like text boxes, tab or navigation patterns, repeated modular panels, dense dashboard-style layouts, and other component-library aesthetics that imply interactivity. Use stylized text boxes less, favoring a flat structure on the canvas.
* Visual storytelling: Prioritize visual storytelling by default, favoring real images, generated visuals, diagrams, plots, and charts to convey concepts whenever appropriate rather than relying solely on plain text, especially when the user does not provide assets. As a general rule of thumb, aim for approximately 2-4 visual assets per slide, including meaningful styling elements, adjusting as needed based on the topic, complexity, and overall theme of the task.
* Connectors in diagrams: In the final implementation, create connectors (arrows/edges) before creating entity nodes, so edges appear behind nodes and never cross through node shapes or labels. If this ordering is awkward during early iteration, you may create nodes first in the initial draft, then switch to connectors-first in the revised code.
* Overlap: You MUST fix ALL unintended overlap errors before you deliver the slides! It's of paramount importance!
* Font size: When a template is provided, match its font sizes. Avoid overly small text. When no template or style guidance is given, a good rule of thumb is at least 42pt for deck titles, 32pt for slide titles, and 17pt for body text. If you see overflow/overlap, try cutting content before shrinking text further to improve text layout.
* Text layout: for net-new authoring where wording is flexible, shorten copy when needed. When the user supplied required wording or source material whose fidelity matters, do not silently shorten or summarize it; choose a denser archetype, restructure within the slide, split only when the request permits it, or flag the tradeoff. Inspect visually for unexpected text wrapping. NEVER put 2 lines of text into a title/banner text box meant for a single line of text.
* Diagrams implementation: use native PowerPoint shapes for simple diagrams; use Graphviz for complex relational/topological/network-like diagrams; use imagegen for highly aesthetic, illustrative, or scientific infographic diagrams (e.g. chemical structures, circuit diagrams, etc.).
* Title slide: Keep the title slide minimal and simple. Avoid cramming in too much information.
* When to use diagrams: Prefer data-driven charts or plots when applicable; use diagrams only when they improve the storytelling (not to fill empty space).

If any check fails, the task is not complete.

## Required Read Order (No Skips)

Before any content write or edit operation:

The active/main agent must perform this reading itself. Do not assign these files to subagents for summarization. Subagents remain available for other independent tasks after the main agent has read the applicable guidance.

"Relevant" means the baseline safety references below plus every matching task-specific row in the task map. It does not require unrelated reference files unless the task is ambiguous.

1. Read `references/reference-connector-runtime-and-safety.md`.
2. Read `references/reference-target-presentation-guard.md`.
3. Read `references/reference-google-slides-mcp-discovery.md`.
4. Read `references/reference-request-shapes-and-write-safety.md`.
5. Read `references/reference-thumbnail-visual-verification.md`.
6. Read every task-specific file from the matrix below.
7. If the task spans multiple categories, read all matching files.
8. If uncertain, read every file in `references/`.

For net-new local `.pptx` creation, read the `[@presentations](plugin://presentations@openai-primary-runtime)` authoring skill before creating the deck.

Do not execute content edits until the required references are read in the current turn.

## Connector Load Checklist

1. Confirm the exact target Google Slides URL or presentation id.
2. Resolve and record the presentation id, title, slide count, and target slide object IDs.
3. Treat target-presentation identity as a hard precondition for connector writes.
4. Before each edit pass, identify the slide, object IDs, and current geometry through connector reads.
5. Before every connector write batch, re-read `references/reference-target-presentation-guard.md` and re-confirm the target presentation and slide object IDs.
6. Read via connector first, using the current Google Slides actions:
   - get presentation, text, or outline
   - get slide
   - get slide thumbnail before and after batch updates, and when visual evidence matters
7. If the source is a template or existing deck that should be preserved, create a copy before editing.
8. Do not claim the connector is unavailable, read-only, or blocked unless the current session has established that through capability evidence.

## Task To Reference Map

| Task area | Required reference file |
| --- | --- |
| Runtime attachment, target identity, safety, and recovery | `references/reference-connector-runtime-and-safety.md` |
| Confirming the target presentation before every write batch | `references/reference-target-presentation-guard.md` |
| Google Slides MCP discovery, connector wrapper vs official Slides API mapping, method catalog, and batchUpdate request catalog | `references/reference-google-slides-mcp-discovery.md` |
| Batch update request shape, live object IDs, geometry, and write safety | `references/reference-request-shapes-and-write-safety.md` |
| Deck summaries, candidate slides, multi-slide edits, translation, or deck-wide changes | `references/reference-read-before-write-and-deck-scope.md` |
| Any layout, styling, image, chart, or placement change | `references/reference-thumbnail-visual-verification.md` |
| New deck from a provided native Google Slides template or reference deck | `references/reference-template-reference-deck-copy-workflow.md` |
| New deck creation, copy-from-template workflows, or final handoff after any write | `references/reference-new-deck-and-final-pass.md` |
| Local `.ppt`, `.pptx`, or `.odp` import | `references/reference-import-presentation.md` |
| Visual cleanup, overflow, spacing, alignment, or deck polish | `references/reference-visual-iteration.md` |
| Migrating source content onto a template deck with fidelity requirements | `references/reference-template-migration.md` |
| Any multi-slide creation, source adaptation, template following, or layout-selection workflow | `references/reference-slide-planning-and-layout-selection.md` |
| Choosing slide archetypes, compositions, or repeated layout families for any created or adapted slide | `references/reference-slide-archetype-mapping.md` |
| Chart refresh, chart replacement, or Sheets-sourced chart work | `references/reference-chart-workflows.md` |
| Copy-and-fill raw batch update examples | `references/reference-batch-update-recipes.md` |
