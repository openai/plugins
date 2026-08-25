# Smart Chips And Building Blocks

When to read: any task that needs smart chip, dropdown, or building-block parity beyond simple supported chip insertion, or needs to inspect or edit content near native controls.

## Dropdown Terminology

Treat `dropdown`, `drop-down`, `status button`, `smart button`, `choice chip`, `button with options`, and similar selectable pills as dropdown intent unless the context clearly identifies a date, person, or Google resource chip.

Preserving or copying a dropdown is not permission to replace it with its visible label. Exact dropdown creation, option replacement, or selected-value mutation uses only `reference-dropdown-code-mode.md` and the checked-in Google Docs executor after capability discovery.

## Current Support Level

Support these smart chip element types through connector readback and `batchUpdate` writes:

- Date chips: read as `dateElement`, write with `insertDate`
- People chips: read as `person`, write with `insertPerson`
- Google resource chips: read as `richLink`, write with `insertRichLink`

Treat Google Docs building blocks as recognizable document structure, not as single API objects. There is no documented `batchUpdate` request that inserts arbitrary UI building blocks as native building-block objects.

## Smart-Chip-First Authoring Policy

Audit the content plan before writing and use the following representations wherever those values occur:

| Content being added | Required representation | Required source value |
| --- | --- | --- |
| Concrete semantic date | `insertDate` | Faithful timestamp plus appropriate locale/display format |
| Person name | `insertPerson` | Verified email address |
| Google Calendar event | `insertRichLink` | Google Calendar event URL |
| Google Doc, Sheet, or Slides presentation | `insertRichLink` | Resource URL |

The date and Google Workspace file rules are unconditional whenever the value is added. The people and Calendar rules are mandatory when their required source values are available. Never invent a timestamp, email, or URL to satisfy the policy. When only a person's name is known, plain text is allowed. When a supplied date is too ambiguous to encode faithfully, preserve an existing ambiguous value or disclose the ambiguity rather than fabricating precision.

These rules apply in prose, metadata, tables, lists, citations, source lists, appendices, copied templates, and native post-import repair. Ordinary text hyperlinks remain appropriate for non-Google web citations, but are not a substitute for rich-link chips on Google Docs, Sheets, Slides, or Calendar event URLs. For other Google resources supported by `insertRichLink`, prefer a rich-link chip when convenient.

### Person Relevance Before Representation

A person chip is semantic content, not decorative template furniture. Before preserving, deleting, or replacing one:

1. Read its surrounding role label and the prompt/source authority for that role.
2. Choose `carry-forward` when the template defines a reusable/current contact or approver and nothing supersedes it.
3. Choose `replace` when the source names a different person for the same role.
4. Choose `remove` or visibly mark the role unassigned when the person belongs only to an example, prior project, or instructional sample.
5. If the relevant person remains and a verified email is known, preserve or insert the native `person` element. Never keep an irrelevant person merely to preserve a chip count.

### Canonical Workspace Rich Links

Run `node scripts/canonicalize_google_workspace_url.mjs '<url>'` before inserting a Google Docs, Sheets, or Slides rich link. The helper unwraps Google redirect URLs and returns a canonical file-level URI suitable for `insertRichLink`.

- Use `canonicalUri` for the rich-link chip.
- Account selectors such as `/u/0/`, sharing parameters, and tab/range/heading/bookmark/slide fragments do not belong in the chip URI.
- If `deepLinkUri` is returned and the location matters, add a separate readable ordinary hyperlink such as “open the referenced slide.” The file chip remains mandatory.
- Do not treat an insertion failure on the original deep URL as evidence that rich links are unavailable; retry once with the helper's canonical URI.
- Verification fails when a Docs/Sheets/Slides destination exists only as an ordinary hyperlink.
- Apply this normalization to existing copied `richLink` elements too. Inventory their connector-visible `uri` values after native copy. For each retained relevant link, replace account-routed, redirected, sharing, tab, range, heading, bookmark, slide, or fragment-bearing chip URIs with the helper's `canonicalUri`; remove irrelevant prior-project chips. Existing chips are not grandfathered into a noncanonical state.

Use these support tiers:

- Exact through `batchUpdate`: date chips, people chips, rich links, and meeting-notes-like regions composed from supported chips, text, paragraph style, and bullets after sampling a matching exemplar.
- Exact existing-dropdown preservation: keep the control and its containing native structure intact, using `reference-template-preservation-and-edit-scope.md`.
- Exact dropdown create/options/selection: use the checked-in Google Docs dropdown path only when provider metadata and post-write readback prove ordered options and selected value.
- Exact by template copy only: UI-inserted Email draft, Task tracker, Simple decision log, Calendar event draft, Code block, custom building blocks, and other native controls without a verified mutation path.
- Approximation only with explicit user acceptance: recreate visible tables, labels, and text while stating that dropdowns, placeholder chips, code-block containers, draft metadata, and other UI-only affordances are not native.
- Copy-only opaque controls: unmatched private-use glyphs and unclassified controls. Never infer dropdown semantics from the glyph alone.
- Unsupported dynamic or account-dependent UI: AI summary, View more catalog entries, and user/workspace-defined custom building blocks unless an existing exemplar is copied.

Do not claim exact Google Docs UI parity for a block unless connector readback proves the same observable structure and every unsupported native UI component came from an existing copied exemplar.

## Template Shape Sampling

Before writing into an existing template or building-block-like region:

1. Resolve the target `documentId` and `tabId`.
2. Use the file-backed trusted read from `reference-trusted-read-wrapper.md` for the initial full read. Inspect its control awareness and normalized artifacts, then read the nearest comparable section with `get_document` when a narrower follow-up is useful.
3. Capture paragraph-level metadata: `namedStyleType`, paragraph style fields, bullet/list state, and start/end indexes.
4. Capture table-level metadata when present: row/column count, table ranges, cell ranges, cell text, private-use placeholder glyph counts, inline object elements, and cell styles exposed by the connector.
5. Capture element-level metadata: `textRun`, `dateElement`, `person`, `richLink`, inline object, text style, and element ranges.
6. Capture provider dropdown metadata, containing structure, visible label when exposed, and surrounding anchors for every dropdown in scope.
7. Reconstruct only portions with a verified write path. Preserve or copy other native controls and edit around them.
8. Re-read the inserted or edited region and compare element types and native metadata, not just visible text.

## Critical Readback Rule

Do not use exact text range search as the primary way to find smart chips.
Chip display text appears in full `get_document` structure, but exact text match helpers may return `null` for that same visible display text.

For chip-aware work:

1. Use `get_document`.
2. Inspect paragraph `elements`.
3. Detect `dateElement`, `person`, and `richLink` directly.
4. Use each element's `startIndex` and `endIndex` for styling, deletion, or replacement.
5. Use element properties for semantic comparison:
   - `dateElement.dateElementProperties.displayText`, `timestamp`, `locale`, `dateFormat`, `timeFormat`
   - `person.personProperties.name`, `email`
   - `richLink.richLinkProperties.title`, `uri`, `mimeType`

Smart chips usually occupy a one-code-unit range. To change the chip payload itself, delete the element range and reinsert the chip. Use `updateTextStyle` only for style changes.

Do not apply that delete-and-reinsert rule to dropdowns. Use the Google Docs dropdown executor for a positively identified exact mutation; otherwise preserve the control.

## Dropdown Preservation

1. Include every existing dropdown intersecting or adjacent to the edit in the targeted snapshot.
2. Treat the control and its containing native structure as immutable unless the Google Docs dropdown route positively identifies it as exact-writable.
3. Edit supported text before or after the control rather than rewriting its range.
4. Use only a copy path proven to retain native controls when duplicating a document or tab.
5. If no available route can preserve a required dropdown, stop before writing.

## Building Block Recognition

For calendar-backed Meeting notes insertion, use `reference-meeting-notes-direct.md` as the operational guide. This reference only records the broader capability boundary: the API may not prove that the user inserted the region through Insert > Building blocks > Meeting notes, but it can prove the same observable constituent structure.

For Email draft, Task tracker, Simple decision log, Calendar event draft, and Code block, exact output means starting from a UI-inserted exemplar or template copy. Writing out only the visible labels and table cells is an approximation unless the unsupported UI-only child components came from the copied exemplar.

## Verification

After writing chips or a building-block-like region:

1. Re-read with `get_document`.
2. Confirm the expected element types are present where supported: `dateElement`, `person`, `richLink`.
3. Confirm chip properties match the intended date, attendee emails, and resource URI.
4. For connector-identified dropdowns, confirm provider identity, range, ordered options, selected value, containing structure, and surrounding anchors.
5. For opaque controls, confirm the containing structure, location, anchors, and signature without claiming semantic verification.
6. Confirm paragraph styles, list state, table shapes, inline objects, and other sampled peer structure remain intact.
7. Confirm there are no unintended extra empty bullets, duplicate sections, or leftover scaffolding.
8. Do not treat HTML export as proof that a chip or dropdown survived natively; HTML export flattens native controls.
9. Do not use Drive thumbnails as proof of final visual layout. Use PDF export plus page raster inspection when rendered page quality matters.
