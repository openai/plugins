# Visual QA

Read this file when formatting quality matters, especially for templates, briefs, handoff docs, or docs with tables, images, appendix content, or structured controls.

## Verification Loop

- After creation or major edits, inspect the rendered document rather than trusting the write requests alone.
- Prefer connector-native reads for structure and content verification, but also visually render the document when formatting quality matters.
- If connector reads are not enough to judge visual quality, Atlas, if available, may be used only to open the finished doc and capture screenshots for visual inspection. Do not use Atlas to do the document authoring.
- If the rendered document shows ugly tables, missing link styling, broken spacing, flattened structured controls, or other visual drift, iterate and fix those issues before handoff.

## Failure Conditions

- Treat visible formatting drift as a real failure. If headings, labels, tables, links, or body text do not look native to the document, keep fixing them before handoff.
- Treat missing hyperlink styling as a real failure when the document is supposed to contain links.
- Treat a plain, unfilled, or unbolded table header as a real failure unless the surrounding document clearly uses that style intentionally.
- If a source document already contains mentions, chips, status controls, or other structured inline entities, verify they are still present and semantically intact before handoff.
