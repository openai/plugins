# Template Preservation And Edit Scope

When to read: before editing an existing structured document, filling or adapting a template, following a reference document, duplicating a document or tab, changing branded furniture, or writing near tables, lists, chips, dropdowns, images, headers, footers, or other native controls.

Do not use this reference for ordinary net-new documents without a supplied template/reference.

## Choose The Mode

- Use `in-place` only when the user explicitly targets an existing working document.
- Use `copied-document` for a reusable template that must remain pristine.
- Use `duplicated-tab` when the user asks for a new tab based on an existing tab.
- Use `broad-reformat` only for an explicit document-wide redesign or normalization request.
- Use `exact-template` when the supplied Google Doc should keep its structure while content is replaced. Copy the native document and fill its real containers.
- Use `template-adaptation` when the supplied Google Doc should remain the base but the request requires targeted additions, removals, new columns, new sections, or other extensions. Copy the native document and change only the required structures.
- Use `selective-reference` only when the user explicitly identifies which parts to borrow or asks for inspiration rather than fidelity. Keep the work native; copy and prune the reference, or create a native Google Doc directly when no selected native structure must carry forward.
- Use `content-source` when a supplied document contributes facts only and the prompt does not ask the output to follow its structure, styling, or native organization.

When the user says to use a Google Doc as a template, reference, example, model, or basis for the same kind of deliverable, default to `exact-template` or `template-adaptation`. Do not infer `selective-reference` merely because the prompt uses the word “reference.” Do not route `exact-template`, `template-adaptation`, or `selective-reference` work through DOCX.

### Multi-Tab Preservation Invariant

When an `exact-template` or `template-adaptation` source has multiple tabs, the destination starts as a full native copy and retains the complete tab tree. “Use this as a reference,” a URL scoped to one tab, or a request for the same document type does not authorize a one-tab reconstruction.

- Record every source tab's title, id, order, parent, and nesting before reading one tab deeply.
- Give every tab separate structural and content treatments. Unmentioned tabs retain their structure; their content is not automatically carried forward.
- Remove, merge, flatten, or consolidate tabs only when the user explicitly asks for selected parts, a single-tab deliverable, or named tab removal.
- Adapt content inside every copied tab. For a past/example reference used to create a new deliverable, every retained tab defaults to `adapt content`; do not satisfy the task by recreating only the initially visible tab or by labeling untouched tabs as legacy/reference material.
- Before handoff, compare source and destination topology and reject an unauthorized count, order, nesting, or title mismatch.

### Structure And Content Are Separate Axes

For each tab, section, table, list, image, link, chip, and control, make two independent decisions:

1. **Structural treatment:** retain, extend, reorder by user direction, or remove by user direction.
2. **Content treatment:** carry current content, adapt to the new subject, replace from an authoritative source, or clear when the field is inapplicable.

`Retain structure` includes both native form and semantic organization: topology, section order, container identity and position, field roles, table row and column roles, comparison dimensions, ordering, dependencies, and operative instructions embedded in or adjacent to retained structures. It does not mean freezing the initial dimensions; an applicable instruction to extend, delete, substitute, or reorder a structure is itself part of the structure to preserve. `Retain structure` never implies `carry content`. When a reference represents another project, event, product, experiment, incident, customer, organization, or time period, its structure and native styling may be reusable while its facts are not. Unless the user explicitly requests a historical appendix or side-by-side comparison:

- adapt or replace content in every retained functional section
- remove prior-project people, dates, venues, organizations, links, approvals, metrics, statuses, and distinctive copy
- do not retain old material under labels such as `legacy`, `reference`, `do not send`, `do not use`, or `historical`
- do not preserve old people/date/link chips merely because native elements are fragile

The user prompt governs the requested outcome. Applicable instructions in the selected template/reference govern how retained structures must be used or adapted. Designated content sources govern facts. Skill guidance supplies defaults and implementation methods only where those authorities are silent; it must not weaken, reinterpret, or override an explicit instruction. The template/reference governs facts only when the user explicitly says its content remains authoritative. If a required value is absent from the factual sources, disclose it as unavailable/TBD or frame a clearly labeled recommendation; never fill it from the past/example reference.

## Native Copy Route

Before creating a destination:

1. Read the native reference signature required by `SKILL.md`, beginning with the complete tab tree. Never treat the tab in the URL as the whole document.
2. Classify the mode from the prompt and record both the structural and content treatment of every tab, then each relevant component. For past/example references, identify a compact set of reference-only factual signatures that must disappear from the finished artifact.
3. For `exact-template` and `template-adaptation`, copy the Google Doc with the Drive copy action exposed by the current runtime. Do not create a blank document and rebuild it.
4. Run the file-backed trusted read on the copied destination before its first write. Omit `tabId` for the initial read when the task spans multiple tabs; use targeted per-tab reads afterward.
5. Preserve source tab order, nesting, named styles, local text styling, tables, lists, images, headers, footers, controls, semantic roles and relationships, and applicable instructions unless the treatment map or user direction changes them. Preserve links, people, dates, and other semantic elements only when they remain relevant and authoritative; otherwise replace or remove them without flattening the surrounding native structure.
6. Follow applicable user and template instructions while replacing or extending content inside preserved containers. Append after a stable prompt/label, replace only an explicit placeholder span, or insert a sibling paragraph. Avoid deleting and recreating a whole paragraph, list item, table cell, or section when it contains or may contain native elements.
7. Reconcile the destination against the reference signature and the treatment map before handoff.

If native copy is unavailable and the requested fidelity depends on tabs, custom styles, table formatting, chips, controls, or other native semantics, stop and report the limitation. Do not silently downgrade to DOCX or plain text.

## One-Pass Semantic Inventory

For every template fill, template adaptation, or selective-reference task, classify only source components relevant to the requested output:

| Component | Allowed treatment |
| --- | --- |
| Tab tree: count, titles, order, parent/nesting | Retain completely by default; remove, merge, or consolidate only through explicit user direction. Decide content separately |
| Ordered section or functional category | Preserve, fill, or adapt |
| Template answer container | Fill in place |
| Guidance or instruction text | Follow as an operative requirement; remove only after it has been satisfied and only when it is clearly scaffolding rather than intended output content |
| Heading or typography role | Preserve the relevant named style and representative font/size/weight/color/spacing signature |
| Native table, matrix, checklist, timeline, or scorecard | Preserve its native container, semantic schema, roles, relationships, and relevant style and geometry; extend as required by the user or applicable template instructions, using local peers for new structure |
| Figure, chart, image, or diagram | Preserve, recreate, or report unsupported |
| Source citation or hyperlink | Preserve when its associated content remains; canonicalize retained Workspace rich links and remove irrelevant prior-project links |
| Decision gate, condition, threshold, permission, or prohibition | Preserve its operative force; adapt only from supplied authority |
| Person chip | Classify its role as carry-forward, source replacement, or example/project-specific removal; if the relevant person remains and email is known, preserve/write it as a chip |
| Date/rich-link chip, dropdown, or opaque control | Preserve/copy unless an exact mutation route exists; never silently convert it to visible text |
| User-requested removal | Remove and verify |
| Unsupported element | Leave copy-preserved or report before writing |

Keep this inventory in working notes only. Do not persist, serialize, count, or script-validate semantic coverage. Perform it once before drafting and compare it once before handoff. Record the compact mechanical reference signature separately; sample representative styles rather than inventorying every paragraph or spacing boundary.

For exact-template, template-adaptation, and selective-reference work, treat prompt-, applicable template-, and authoritative source-defined instructions and decision constraints as authoritative semantics. Preserve distinctions such as `only after`, `before`, `unless`, `must`, `may`, numeric thresholds, approval gates, ordered dependencies, field roles, and comparison dimensions. Do not weaken a gate, broaden permission, merge a required distinction, or invent an exception, parallel path, waiver, or interim action unless the prompt, selected template, or an accepted source explicitly authorizes it. Concision may shorten the wording, but not change who may act, under what conditions, in what sequence, or through which structural relationship.

Treat facts found only in a past/example reference as non-authoritative. Do not carry a reference-only date, time, owner, organization, venue, URL, metric, claim, or status into the new deliverable, even when it appears to fill a matching field plausibly. Reusing a reference's unsupported schedule endpoint or other operational detail is an invented fact.

## Targeted Snapshot

For an ordinary edit with clear boundaries, record compact working notes for:

1. target document id, URL, `tabId`, and revision
2. exact editable range or structural container
3. unique anchors immediately before and after the edit
4. native structures intersecting or immediately adjacent to the edit
5. one comparable local style peer
6. one sampled out-of-scope anchor

Use the initial file-backed trusted read from `reference-trusted-read-wrapper.md` to populate native and opaque controls in this snapshot. Its control awareness is advisory; this semantic inventory and the selected edit scope remain model-owned.

Treat sampled out-of-scope structure as immutable. Refresh the snapshot only after a write shifts indexes or changes the containing structure.

## Conditional Full Preservation Manifest

Use a full manifest only when copying a reusable native template, changing branded furniture, duplicating a document/tab containing native controls, performing an explicit broad reformat, or editing a region whose safe boundaries cannot be isolated.

Inventory only the affected template/request scope: source and destination identity, permitted mutation surface, relevant headers/footers/objects/section properties, affected tables/lists/images/native controls, nearby style anchors, and unique anchors around fragile components. Do not inventory unrelated regions merely because they exist.

## Pristine Source Recovery

If a supplied folder is empty:

1. resolve folder metadata and list direct children
2. search by the exact prompt or source-package title
3. accept a recovered source only when its MIME type and source-package name match, its metadata is consistent with a pristine input, and its content has no skill labels, QA notes, or generated-output markers
4. record the recovered source id
5. if no pristine source is found, stop rather than reuse a prior evaluated output

## Native-Control Rules

1. Preserve every existing dropdown by default.
2. Treat provider metadata—not visible text or a placeholder glyph—as authority for options and selected value.
3. Mutate a dropdown only through the checked-in Google Docs route selected before the first write.
4. Treat unmatched private-use glyphs and unclassified controls as copy-only.
5. Never replace a native control with its visible label or placeholder character.
6. If the active path cannot preserve a required native component, stop before destructive work.

## Apply And Verify

1. Confirm the target and edit surface from fresh connector readback.
2. For fragile repeated work, verify one representative write before continuing.
3. Use the smallest section- or container-sized writes that preserve target identity.
4. Re-read after index shifts, table/object/tab changes, or native-control changes.
5. Repair local drift locally; never restart by rebuilding the whole document.
6. Confirm the complete destination tab tree matches the planned structural treatment. For a multi-tab source, compare tab count, titles, order, and parent/nesting; one matching visible tab is insufficient.
7. Confirm the content treatment completed on every retained tab. For a past/example reference, inspect every tab for reference-only identifiers, people, dates and times, venues, links and chips, claims, metrics, statuses, and distinctive copy. An untouched or substantially historical tab is a failed adaptation unless the user explicitly requested it.
8. Confirm relevant heading styles, table styling/geometry, chips, links, lists, images, headers, footers, and controls match the reference except for intentional changes.
9. Confirm the source remains unchanged and every semantic-inventory component has its planned treatment, including the exact force of decision gates and conditions.
10. Compare before/after anchors and sampled out-of-scope structure.
11. Report any native or rendered property that cannot be verified.

Reject a result that changed the source, collapsed or reordered tabs without authorization, left a retained tab as unrequested historical/reference content, carried reference-only facts into a new deliverable, rebuilt a supplied template/reference through DOCX, modified undeclared structure, bypassed actual answer containers, lost a semantic-inventory component, weakened or broadened an authoritative decision constraint, replaced chips with visible text, or returned matching visible text after losing required native styling or structure.
