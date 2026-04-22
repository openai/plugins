# Citations And Hyperlinks

When to read: any task that includes sources, links, evidence, or source lists.

## Hyperlink Requirement

1. Use readable linked labels instead of naked URLs in narrative sections.
2. Citations must be hyperlinks instead of raw URL text unless the template explicitly requires raw links.
3. Keep citation labels short and descriptive.
4. Resolve hyperlink ranges from exact document text when possible. Prefer `find_text_range` or another text-exact lookup over hand-counted start and end indexes.
5. Link the full visible label, including plural endings or trailing words that are part of the intended citation text. Do not stop the link one character early.
6. If a URL must appear in the document, apply it as a hyperlink to readable label text unless the template explicitly requires the raw URL string to stay visible.
7. This rule still applies inside tables, supporting sections, and structured response areas. Raw pasted URLs are not an acceptable default just because the content lives in a grid or structured block.
8. Never apply hyperlinks to guessed or pre-insertion ranges. Insert the final text first, re-read the live document, then resolve the exact visible label range before applying the link.
9. If a link is meant for a table label or other short visible phrase, target that exact text only. Do not rely on broad row ranges or offsets that can drift after content insertion.

## Citation Behavior

1. Add short source callouts where trust and traceability matter.
2. Keep citations concise and unobtrusive.
3. Prefer linked labels over raw URL dumps in source lists, evidence sections, and supporting notes.
4. After applying a link, verify through connector readback that the label text still matches the intended phrase exactly.
5. If the source block already contains raw URLs from an earlier write, clean them up into linked labels during the final pass instead of leaving them behind.
6. If connector readback shows a partial hyperlink on only part of a word or phrase, treat that as a failed write and repair it before handoff.
