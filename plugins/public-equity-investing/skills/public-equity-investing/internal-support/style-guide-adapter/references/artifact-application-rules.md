# Artifact Application Rules

Use this guide when applying a style profile to a real artifact through an artifact-specific editing surface. The bundled `extract_office_style.py` script is metadata-only and does not apply edits. Preserve the artifact's substance unless the user explicitly requests rewriting, restructuring, or content deletion.

## PowerPoint and slide decks

### Preserve by default

- master slides, layouts, placeholders, slide size, and theme unless changing them is the requested style action
- speaker notes, comments, hidden slides, section structure, slide IDs, page numbers, confidentiality markers, logos, source lines
- embedded Excel objects, chart data, links, alt text, images, icons, and crop settings
- all factual claims, numbers, signs, units, dates, citations, and footnotes

### Prefer these style-safe edits

- apply theme colors and fonts where compatible with the master
- align titles, subtitles, page numbers, source lines, and footers to the profile
- normalize chart/table formatting without changing chart data
- improve spacing, alignment, object size consistency, and typography hierarchy
- standardize section dividers, appendix labels, page titles, and callouts
- replace manual formatting with master/layout styles when doing so preserves content

### Avoid unless requested

- deleting slides, notes, appendices, footnotes, or exhibits
- changing chart data, categories, series order, or formulas
- flattening editable charts into images
- breaking embedded links or template placeholders
- overfitting to one precedent slide that conflicts with the current master

## Word documents, memos, and reports

### Preserve by default

- headings, bookmarks, cross-references, table of contents, comments, tracked changes, footnotes/endnotes, citations, links, and document properties
- defined styles and numbering schemes unless replacing them is the explicit task
- substantive legal, compliance, disclosure, or risk language

### Prefer these style-safe edits

- map paragraphs to the nearest target named style
- standardize heading hierarchy, table styling, caption/source formatting, footnote style, and appendix treatment
- tighten prose for voice and consistency while preserving meaning
- add a style profile or style notes if the user wants reusable guidance

### Avoid unless requested

- accepting/rejecting tracked changes
- deleting comments, footnotes, appendix sections, tables, or cited material
- changing definitions, legal terms, financial claims, or recommendations under the guise of tone

## Excel, Google Sheets, and financial models

### Preserve by default

- formulas, named ranges, source links, data validations, conditional formatting logic, comments/notes, hidden rows/columns/sheets, grouping, macros/VBA, protected ranges, pivots, charts, and external data connections
- color semantics that indicate inputs, formulas, linked cells, outputs, checks, historicals, forecasts, and errors

### Prefer these style-safe edits

- apply tab colors, headers, number formats, borders, freeze panes, print settings, and navigation rows consistent with the style profile
- normalize input/output/check formatting while preserving model semantics
- improve readability of summaries, dashboards, bridges, and charts
- add style flags or a change log rather than silently changing sensitive workbook structure

### Avoid unless requested

- hardcoding formulas, pasting values over formulas, deleting hidden tabs, renaming named ranges, changing signs, moving source tabs, modifying macro logic, or overwriting linked data
- changing financial-model color conventions if the workbook already uses a clear institutional standard

## Text-only / chat / email outputs

When no editable file is being produced, adapt:

- subject/title format
- opening structure and level of directness
- bullet style, punctuation, and bold lead-ins
- recommendation, caveat, and ask language
- source/citation presentation

Do not invent logos, exact colors, fonts, or proprietary style rules without evidence. Provide a concise style assumption note when using defaults.


For Public Equity Investing, preserve rating/stance language, price targets, estimates, citations, caveats, source posture, and confidence labels. Style edits must not make an assumption look sourced or an issuer claim look verified.
