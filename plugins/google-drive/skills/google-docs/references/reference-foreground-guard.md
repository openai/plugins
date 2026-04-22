# Target Document Guard

When to read: before every connector write batch to a Google Doc, and again before ending the task.

## Rule

The exact working Google Doc must be identified by connector-visible document identity at write time and handoff time.

This environment has no Browser Use and no rendered visual inspection. Do not require a visible browser tab, foregrounding, screenshots, cursor placement, or rendered-page scans.

## Hard Precondition

It is not enough that:

1. a URL was mentioned earlier
2. a document title looks similar
3. a previous connector read returned some Google Doc
4. the intended section name exists in multiple documents or tabs

Before writing, confirm the target document URL or id, document title when available, and resolved `tabId` when the document has tabs.

## Required Check Before Every Write Batch

1. Confirm the intended working doc URL or document id.
2. Re-read enough connector metadata to verify the target document identity.
3. If the document has tabs, confirm the target `tabId`.
4. Resolve the target section, paragraph, range, table, or cell from fresh connector data.
5. Only then issue the connector write.

## Required Check Before Final Handoff

1. Run connector readback on the edited document.
2. Confirm the target document id, title, and `tabId` where applicable.
3. Confirm the inserted or edited content is present in the intended section, range, table, or cell.
4. Report any rendering or visual-layout property that could not be verified through connector data as an unverified limitation, not as a completed visual check.

## Stale Identity Triggers

Treat target identity as stale after any of the following:

1. opening, reading, or copying content from another Google Doc
2. switching between document tabs
3. using a source document as input for a destination document
4. connector errors or runtime reset
5. any ambiguity about document id, title, or `tabId`
6. performing a write after a long source-gathering step

## Failure Rule

If the working doc identity was not freshly confirmed before the current write batch, or final readback does not prove the edits landed in the intended document and location, the target-document precondition failed.
