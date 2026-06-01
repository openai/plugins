---
name: reference-pdf-export-visual-qa
description: Verify native Google Docs layout by exporting to PDF, rasterizing every page, and inspecting rendered page images.
---

# PDF Export Visual QA

When to read: before final handoff for layout-sensitive, table-heavy, figure-heavy, polished, or final-deliverable Google Docs work.

## Critical Invariant

Connector readback proves structure and metadata. HTML export proves generated markup and CSS. Neither proves final rendered pages.

When Google Drive PDF export and local PDF page rasterization are available, use exported PDF pages as the visual QA gate for native Google Docs work. Inspect every rendered page image before claiming rendered visual verification.

## When This Is Required

Run this workflow when any of these apply:

1. the user asked for a final Google Docs deliverable rather than a rough draft
2. the work changed tables, figures, images, headers, footers, section breaks, page setup, or dense multi-section content
3. the document is presentation-oriented, polished, executive-facing, or design-sensitive
4. HTML export or connector metadata suggests possible density, width, clipping, overlap, or page-break risk

For narrow text-only edits or basic connector-native docs, connector readback plus targeted range verification can be enough. Do not overstate that as visual QA.

## Workflow

1. Finish all connector writes first.
2. Re-read the target document with the connector and confirm document id, title, `tabId` when applicable, edited ranges, links, lists, tables, and figures.
3. Export `text/html` when available and check generated structure and CSS.
4. Export the native Google Doc through Google Drive as `application/pdf`.
5. Save or resolve the exported PDF as a local file reference.
6. Rasterize every PDF page to page images using the available local PDF rendering toolchain.
7. Inspect every rendered page image at full size.
8. If any page has a defect, return to connector writes, repair the document, re-read connector state, re-export PDF, and re-inspect all affected pages.
9. After a passing PDF visual review, final handoff may say the exported PDF pages were visually inspected. Do not claim live browser-canvas inspection.

## What To Check

Inspect every rendered page for:

1. clipped, overlapping, or missing text
2. broken tables, over-wide tables, cramped cells, or clipped cell content
3. awkward page breaks, stranded headings, orphaned captions, or large blank gaps
4. figures or images with bad crop, bad scale, missing content, or poor placement
5. headers, footers, page numbers, footnotes, and section breaks rendering in the intended locations
6. font, size, bolding, heading hierarchy, links, and list formatting that visibly drift from the surrounding document
7. duplicate content, placeholder text, unintended empty bullets, or leftover scaffolding

## Thumbnail Limitation

Do not use Drive `thumbnailLink` or other file thumbnails as final visual QA. Thumbnails are acceptable only as a quick first-page smoke signal because they are low-resolution, can be stale, and do not provide every page. They cannot prove table fit, page breaks, crop quality, or small-text readability.

## Export And Rendering Limits

If PDF export is unavailable, too large, blocked by connector permissions, or cannot be rasterized locally, fall back to connector readback plus HTML export when possible. In that case, say plainly that rendered PDF visual QA could not be completed.

If the exported PDF exists but page images cannot be inspected, do not claim a visual pass. A successful export is not the same thing as rendered-page review.

## Final Response Language

Use precise language:

- Good: "Connector readback and HTML export passed; exported PDF pages were rasterized and visually inspected."
- Good: "Connector readback passed, but PDF-export visual QA was unavailable, so rendered page fit was not verified."
- Bad: "The Google Doc looks good" when only connector metadata was checked.
- Bad: "The document was visually verified" when only a thumbnail or HTML export was checked.
