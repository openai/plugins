# Hyperlinks And Entities

Read this file when the document includes source links, appendix/reference sections, mentions, chips, dropdowns, or other semantic inline entities.

- Use readable linked labels instead of raw pasted URLs unless the template explicitly requires visible raw URLs.
- If content includes a URL that is meant to be a source or reference, convert it into an actual hyperlink instead of leaving it as plain text.
- Apply links after the final text is in place. Re-read the document and resolve the exact visible label range before styling it as a hyperlink.
- Link the full intended phrase, especially inside tables. Partial-link formatting is a failure.
- In appendix or reference sections, do not leave naked URLs when a readable source label would work. The visible text should be human-readable and clickable.
- Preserve existing `@` mentions, smart chips, dropdowns, and similar semantic inline entities when editing nearby text.
- Do not silently downgrade a mention, chip, or dropdown into an ordinary hyperlink or plain text label.
