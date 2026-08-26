# Citations And Hyperlinks

When to read: any task that includes sources, links, evidence, or source lists.

## Requested Evidence Gate

Use this gate only when the prompt requests research, current facts, named metrics, benchmarks, citations, or source links:

1. Extract the requested evidence targets before drafting.
2. Resolve each target from supplied sources or current authoritative sources and note whether it is available.
3. Do not replace a requested current fact with an invented range, generic claim, or instruction to refresh it later.
4. If a target is unavailable, disclose the gap in the document; stop when the evidence is essential to the deliverable.
5. Distinguish supplied/reported facts from assumptions, interpretations, and recommendations.

Before handoff, confirm every available target appears, source labels are native hyperlinks, and decision-relevant dates or regulatory changes include the material details. Do not introduce evidence levels, an evidence ledger, or research work for prompts that do not request or materially require it.

## Hyperlink Requirement

Before applying ordinary text hyperlinks, classify the destination. A Google Docs, Google Sheets, Google Slides, or Google Calendar event URL must be inserted as a native `richLink` chip under `reference-smart-chips-and-building-blocks.md`; canonicalize Docs/Sheets/Slides URLs with `scripts/canonicalize_google_workspace_url.mjs` first. The ordinary hyperlink rules below apply to other destinations and to an optional location-specific deep link placed next to the required canonical file chip.

1. Use readable linked labels instead of naked URLs in narrative sections.
2. Citations must be hyperlinks instead of raw URL text unless the template explicitly requires raw links.
3. Keep citation labels short and descriptive.
4. Resolve hyperlink ranges from exact document text when possible. Prefer `find_text_range` or another text-exact lookup over hand-counted start and end indexes.
5. Link the full visible label, including plural endings or trailing words that are part of the intended citation text. Do not stop the link one character early.
6. If a URL must appear in the document, apply it as a hyperlink to readable label text unless the template explicitly requires the raw URL string to stay visible.
7. This rule still applies inside tables, supporting sections, and structured response areas. Raw pasted URLs are not an acceptable default just because the content lives in a grid or structured block.
8. Never apply hyperlinks to guessed or pre-insertion ranges. Insert the final text first, re-read the live document, then resolve the exact visible label range before applying the link.
9. If a link is meant for a table label or other short visible phrase, target that exact text only. Do not rely on broad row ranges or offsets that can drift after content insertion.
10. In a copied template/reference, adding or updating an ordinary hyperlink must not change the surrounding font family, size, weight, bold, italic, color, underline state, baseline offset, or paragraph role. Sample the exact linked span before linking and retain its paragraph style.
11. Do not rely on a link-only `updateTextStyle` request in styled template text. Google Docs may introduce default blue or underlined link presentation. In the same request batch, or immediately after resolving the live range, set `link` and explicitly reapply the sampled `weightedFontFamily`, `fontSize`, `bold`, `italic`, `foregroundColor`, `underline`, and `baselineOffset` fields that were present or materially inherited. Preserve an original `underline: false` and non-link color explicitly.
12. Re-read the linked elements and compare the final style field by field with the pre-link sample. A correct URL with changed color, underline, size, weight, or paragraph role is a failed hyperlink write and must be repaired before handoff.

## Citation Behavior

1. Add short source callouts where trust and traceability matter.
2. Keep citations concise and unobtrusive.
3. Prefer linked labels over raw URL dumps in source lists, evidence sections, and supporting notes; use native rich-link chips for Google Docs, Sheets, Slides, and Calendar events.
4. After applying a link, verify through connector readback that the label text still matches the intended phrase exactly.
5. If the source block already contains raw URLs from an earlier write, clean them up into linked labels during the final pass instead of leaving them behind.
6. If connector readback shows a partial hyperlink on only part of a word or phrase, treat that as a failed write and repair it before handoff.
7. If a heading is the hyperlink label, keep its original heading style and full visible typography. Do not accept a blue or newly underlined title merely because the link target is correct.
