# New Deck And Final Pass

When to read: any presentation creation workflow and final handoff after a write.

## Referenced Materials

Use every available relevant source before creating or finalizing the deck: web, MCP/connectors, local files, metadata, thumbnails, previews, and the referenced materials themselves. There is no time constraint; be thorough.

## New Deck Defaults

1. Do not ask for styling unless the request depends on a brand, template, or aesthetic.
2. Create the content structure first, then do a polish pass.
3. Use lightweight visible design: clear hierarchy, comfortable spacing, restrained color, and simple visual accents.
4. Avoid raw black text on white slides when creating a new deck.
5. Keep titles short enough to avoid wrapping.
6. Use real bullet lists for natural lists.
7. Split dense content across slides instead of shrinking everything until it fits.
8. Preserve user control over substantive design choices; do not invent a heavy brand system.

## Final Readback

1. Re-read the full presentation from the connector, then re-read high-risk edited slides individually when the presentation response is abbreviated.
2. Confirm deck id, title, slide count, and edited slide object IDs.
3. Confirm requested text, charts, images, tables, links, media, and speaker notes are present.
4. Confirm editable Google Slides components exist with `mcp__codex_apps__google_drive_get_presentation` or `mcp__codex_apps__google_drive_get_slide`.
5. Do not accept a deck made of slide-sized PNG screenshots unless the user explicitly requested image-only slides.
6. Confirm no placeholder text, empty placeholder objects, generic editor prompts, sample copy, duplicate scaffolding, skipped slides, or mixed old/new state remains.
7. For visible changes, verify fresh thumbnails after the final write.
8. Distinguish connector-verified facts from visual properties that could not be verified.
9. For any slide created from a layout during the task, inspect connector JSON and confirm inherited placeholders are populated, replaced, or intentionally deleted. Do not rely on thumbnails alone; empty placeholders can be invisible in rendered previews.
10. For copied template/reference decks, confirm the final deck still uses the template structure: existing placeholders and reusable content objects are populated or intentionally removed, primary content is not carried by unjustified new freeform boxes, and any newly created object IDs are accounted for by the slide plan.
11. When adapting or migrating provided source material, reconcile a source-to-destination fidelity ledger covering text, images, charts, tables, links, media type/source, and speaker notes. Do not silently shorten required source content.
12. When source slides contain speaker notes that should carry forward, compare source and destination note counts and spot-check exact note text on representative and high-risk slides.
13. Confirm mixed text-style runs, links, list structure, and semantic emphasis were not flattened or copied into the wrong meaning.
14. Confirm there are no whitespace-only bullets, bracketed instructions, lorem ipsum, stale source/reference content, or other inherited scaffolding.
15. Inspect at least one high-risk visual slide at large size for crop, orientation, label/footnote legibility, and evidence preservation. A contact sheet alone is insufficient.
16. When adapting source media, confirm type and source-identifier parity for active accessible media. For inaccessible, trashed, or deprecated media, verify any fallback is source-faithful and record the exception.

## Output

Reference slide numbers and titles. Say which presentation and slides were read or changed, and call out any remaining issue that needs a narrower workflow or human design judgment.

When source media was adapted, a brief confirmation is enough if everything migrated successfully. Describe slide-specific media fallbacks only when they occurred. If chart or evidence content was preserved as a raster because native reconstruction was impractical, disclose that those elements are not natively editable.
