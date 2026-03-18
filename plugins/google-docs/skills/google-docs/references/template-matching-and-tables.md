# Template Matching And Tables

Read this file when the task involves template-fill work, document-native formatting, or table creation/editing.

## Template Matching

- Match the nearest true peer content, not a generic Docs default.
- Before inserting a new heading, body block, or table, inspect nearby peer content and capture the local baseline: heading level, font family, body sizing, emphasis pattern, spacing, and table treatment.
- If the template uses structured containers such as tables, cells, or form-like sections, preserve that structure unless the user explicitly asks for a reformatted rewrite.
- Do not flatten a template-driven control into plain text. Status chips, dropdowns, mentions, smart chips, and similar structured elements should stay structured.
- If the current write path cannot safely recreate a structured control, preserve the existing control and edit around it rather than silently replacing it with raw text.
- Treat visible mismatch in headings, tables, links, inline entities, or template container shape as a failed output that still needs repair.

## Tables

- Match the nearest comparable table in the document before inventing a new pattern.
- Prefer copying the nearest comparable section or table structure in the document as the style baseline. New text and tables should disappear into the template rather than looking newly generated.
- If the template already contains the target table or answer cell, fill that structure instead of appending a parallel draft somewhere else.
- Unless the user or template clearly wants something else, new tables must have a visibly colored header row, fully bold header text, and alternating white/light-gray body rows. The default header fill should be baby blue.
- Keep tables compact and readable. If a schema feels cramped, reduce column count instead of squeezing the page.
- Do not create a foreign-looking standalone table when a nearby peer table already establishes the right border treatment, fills, widths, or typography.
- If a table still looks plain, unstyled, or inconsistent with the rest of the document, keep fixing it before handoff.
