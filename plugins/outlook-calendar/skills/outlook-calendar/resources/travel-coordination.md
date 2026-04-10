# Travel Coordination

Use this resource when Outlook Calendar work depends on physical movement, airport timing, or in-person logistics rather than only meeting duration.

## Travel Read Path

- Resolve the travel context first: meeting locations, departure and arrival times, cities, timezone boundaries, and whether the travel block should be public or private.
- Interpret each stated travel time in the local timezone where that timestamp occurs before comparing it to calendar events.
- Read the affected calendar window before proposing any travel buffer or reschedule.
- If the travel request spans multiple cities or airports, keep each local timestamp anchored to the city where it occurs until after interpretation.

## Outlook-Specific Focus

- Work location and in-person versus online context matter more here than raw availability.
- Travel buffers should usually protect the user's real day rather than appear as optional notes buried inside another event.
- Hybrid-office days often need explicit before and after commute blocks to keep Outlook availability realistic.
- If the user asks to shift meetings because of travel, restate the travel anchor and the affected meetings before writing.

## Coordination Rules

- Add buffer time around in-person meetings, office commutes, and airport travel in a way that reflects how the day is actually used.
- When travel overlaps existing meetings, identify which meetings are fixed versus movable before suggesting changes.
- Preserve privacy expectations for travel events such as flights when the user asks for them to be private.
- If a commute or travel block would create obvious overlap, prefer the minimum set of meeting changes needed rather than broadly reworking the day.

## Output Conventions

- Label every travel-related timestamp with its local timezone.
- Show which meetings are affected by the travel constraint.
- If proposing reschedules, explain the minimum set of moves needed.
- If creating new travel events, specify whether they should be private, public, or tentative.
