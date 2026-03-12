# Template Surgery Playbook

Use this file when the main skill has already triggered and you need the operational details.

## When To Escalate

Escalate from normal visual iteration to template surgery when:
- a slide needs more than 2-4 visual passes and still looks structurally wrong
- the same layout defect appears across a family of slides
- the problem is caused by placeholder design, not local position drift
- fixing one element keeps creating new collisions elsewhere

## Safe Operating Order

1. Choose one representative slide.
2. Fetch the live slide structure.
3. Choose a narrow structural move:
- duplicate the clean slide
- delete stale elements
- replace one placeholder pattern
- rework one title/body/image arrangement
4. Apply a small batch.
5. Re-fetch the thumbnail.
6. Check one sibling slide with the same pattern.
7. Only then continue to the rest of the section.

## Preferred Structural Strategies

### Strategy 1: Duplicate the cleanest sibling

Use when one slide in the section already has the right composition.

Why:
- lower risk than creating a new layout from scratch
- easier to preserve consistency across a section

Then:
- duplicate the clean slide
- replace or reset only the objects that should differ
- verify the duplicated slide thumbnail immediately

### Strategy 2: Remove stale structure first

Use when the slide has multiple overlapping legacy shapes, text boxes, or images.

Why:
- many bad iterations happen because the model keeps adding instead of clearing

Then:
- identify redundant objects from `get_slide`
- delete only clearly stale or duplicate elements
- verify the slide before adding new structure

### Strategy 3: Rebuild one content zone

Use when only one region is broken, such as title band, body column, or image area.

Why:
- safer than rebuilding the whole slide

Then:
- keep untouched regions intact
- rebuild only the broken zone
- verify that the rebuilt zone does not collide with preserved content

## Deck-Wide Rollout

After a representative slide works:
- apply the same structure to 2-3 more slides in the same family
- verify each one with thumbnails
- stop if content density makes the pattern stop fitting

Do not force one template across slides that clearly need different density or visual hierarchy.

## Stop Conditions

Stop and report instead of continuing when:
- you cannot identify stable object IDs for the target elements
- every pass makes the slide less legible
- the remaining choices are aesthetic and subjective rather than structural
- the requested change would require a broad redesign rather than safe cleanup
