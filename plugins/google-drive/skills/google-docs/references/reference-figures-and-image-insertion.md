# Figures And Image Insertion

When to read: any task that carries figures, diagrams, screenshots, or slide visuals into a Google Doc.

## Critical Invariant

This blind environment cannot use Browser Use and cannot inspect rendered figure placement. Figures are only in scope when the available Google Docs connector supports the required insertion and readback path.

Do not claim that a figure looks clean, sits well on the page, is cropped correctly, or has native rendered spacing unless the connector exposes enough data to prove that property. If rendered placement cannot be verified, state that limitation plainly.

## Preferred Workflow

1. Use the Docs connector for text structure, headings, paragraph formatting, and any connector-supported image insertion.
2. Finish the document's title, heading hierarchy, and core text structure before any figure work.
3. Create a deliberate connector-visible figure block first: heading if needed, lead-in line if needed, then an insertion point or paragraph reserved for the figure.
4. Insert figures only through connector-supported mechanisms. Do not use browser UI, clipboard, cursor placement, upload dialogs, screenshots, or visible-tab workflows.
5. After insertion, verify through connector readback that the expected image/object exists at the intended structural location.
6. If the connector cannot insert or read back the figure reliably, do not treat a text placeholder as completion unless the user accepts that tradeoff.
7. Prefer fewer connector-verifiable figures over many unverifiable visual objects.

## Source Image Preparation

1. Prepare source visuals before editing the destination document.
2. Use durable local files or connector-acceptable image URLs only when the connector can consume them.
3. Prefer source-derived visuals or prepared composites over rough screenshots.
4. Do not emit large inline image payloads into the model conversation unless image inspection is needed for a hard decision.
5. If an authenticated source-media URL is likely session-scoped, prepare a durable asset first or skip figure insertion and report the limitation.

## Figure Block Placement

1. Insert figures only at deliberate block boundaries, never in the middle of a sentence or paragraph.
2. Surround the intended figure location with connector-written paragraph boundaries so body text resumes above and below it as separate blocks.
3. If a figure needs a lead-in line or caption, insert that text as its own paragraph.
4. If several related visuals are needed, prefer a compact grouped figure section over scattering unverifiable objects throughout the document.
5. Re-read the surrounding document structure after insertion to confirm the object is near the intended heading or paragraph.

## Verification

1. Verify connector readback shows the expected figure object or insertion marker in the intended document and tab.
2. Verify nearby headings, captions, and paragraphs are present in the intended order.
3. Verify no required figure is represented only by placeholder text unless that fallback was approved.
4. Record any unverified rendered properties, such as crop, page fit, visual spacing, or final on-page size.
5. If visuals are required for task success and connector insertion/readback is unavailable, stop and report the limitation rather than claiming the document is complete.
