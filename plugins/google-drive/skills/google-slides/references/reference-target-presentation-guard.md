# Target Presentation Guard

When to read: before every connector write batch to Google Slides, and again before ending the task.

## Rule

The exact working presentation and target slides must be identified by connector-visible deck and slide identity at write time and handoff time.

## Hard Precondition

It is not enough that:

1. a URL was mentioned earlier
2. a title looks similar
3. a previous connector read returned some deck
4. the intended slide title exists in multiple decks

Before writing, confirm the target presentation id or URL, title when available, slide count, and target slide object IDs.

## Required Check Before Every Write Batch

1. Confirm the intended working deck URL or presentation id.
2. Re-read enough connector metadata to verify the target deck identity.
3. Re-read the target slide to capture current object IDs and geometry.
4. Only then issue the connector write.

## Required Check Before Final Handoff

1. Run connector readback on the edited deck.
2. Confirm the target presentation id, title, and edited slide object IDs.
3. Confirm the inserted or edited content is present on the intended slides.
4. For visible changes, confirm a fresh post-write thumbnail was checked.
5. Report any visual property that could not be verified through connector data or thumbnails as unverified.

## Stale Identity Triggers

Treat target identity as stale after reading source decks, copying/importing a deck, connector errors, runtime reset, or any long source-gathering step.
