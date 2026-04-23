# Headings And Question Format

When to read: any task that formats prompts, questions, or answer sections.

## Critical Invariant

New section labels, headings, and body text must match the adjacent document pattern using connector-visible style data. If a new heading, label, font, size, or bolding treatment differs from peer content in connector metadata, treat that as a failure and fix it before handoff.
Missing or weak section hierarchy is launch-blocking. A document that has the right facts but does not clearly read as structured sections with matched headings is not done.
For template-fill tasks, matching the section hierarchy is not enough by itself. If the template uses tables or other structured containers for answers, preserve that structure unless the user explicitly asks for a reformatted rewrite.

## Prompt And Answer Layout

1. Keep each prompt or question on its own paragraph.
2. Format the question being answered as bold body text, not plain text.
3. Put answers below the prompt, never on the same line.
4. Do not promote prompt lines to headings unless the template explicitly defines them as headings.
5. Do not turn prompt-and-answer pairs into bullets unless the template explicitly shows list formatting for that section.
6. Do not type literal bullet characters such as `•` to mimic question styling.
7. If a standalone line introduces a structured content block and reads like a subsection title, promote it to the appropriate heading level or bold label style instead of leaving it as plain body text.
8. Match the local template hierarchy when promoting new section titles. If nearby peer sections use `HEADING_1`, use that style for the new peer section instead of improvising with plain bold body text.
9. Do not hard-code a generic heading level such as `HEADING_2` just because the inserted content feels subordinate. Anchor the choice to the nearest existing section at the same structural level in the live document.
10. If a line is acting as a real section header, do not simulate that with `bold: true` on `NORMAL_TEXT`. Apply the actual matched heading shape or matched local label treatment.

## Heading And Paragraph Discipline

1. Preserve the template heading skeleton.
2. Keep answer and body lines in normal body style unless surrounding context requires otherwise.
3. Treat accidental heading inheritance as a bug and fix it immediately.
4. When replacing or inserting a multi-paragraph section, first normalize the full inserted range to `NORMAL_TEXT`, then clear inherited character styling across that range with an `updateTextStyle` reset such as `bold: false` before reapplying intentional emphasis.
5. Paragraph style updates do not reliably clear inherited text styling. If a question should be bold and its answer should not, explicitly reset the answer/body range instead of assuming the surrounding template will do it for you.
6. Intro labels immediately above standalone tables should follow the surrounding hierarchy: real heading when they divide content into a new subsection, bold label only when they are short inline lead-ins.
7. Preserve the document's local typography for new insertions. Match the surrounding font family and normal body size instead of leaving connector defaults such as Helvetica in a document that is otherwise Arial.
8. Do not assume named paragraph style alone will restore typography. If the template body uses a specific font family, explicitly reset inserted body ranges to that local baseline before applying selective emphasis.
9. If connector reads do not expose enough style detail to confidently match a heading or label, sample the nearest connector-visible peer heading and copy the exposed style fields rather than guessing.
10. For a new section heading, copy the nearest true peer heading's actual presentation, not just its semantic role. Match bolding, font size, and font family along with heading level or local label treatment.
11. If the live peer heading and the inserted heading differ materially in weight, size, or font family, that is a failed match even if both read like headings. Match the peer heading exactly enough that the new line disappears into the template.
12. Prefer promoting a new section heading with the matched paragraph style first, then verify connector-visible style fields before adding any heading-specific text-style override.
13. Do not force heading font family, size, or weight from generic assumptions or connector defaults. If a paragraph-style promotion already matches the peer heading in connector-visible style data, leave the heading text style alone.
14. Only add explicit heading text-style overrides when the peer heading uses a custom local treatment that you have directly sampled and need to reproduce.
15. Treat a heading as unmatched if it shares the peer heading's semantic style but not its concrete connector-visible text style fields.
16. When comparing against peer headings, use the nearest headings on both sides of the insertion point if available. A single semantic match is not enough if the inserted heading still reads heavier, lighter, larger, smaller, or otherwise different on the page.
17. After any bulk insertion, establish the heading skeleton immediately before moving on to figures, tables, or fine-grained styling.
18. A document that contains the right text but lacks clear section headings is not an acceptable fallback. Missing or weak section hierarchy is a formatting failure, not a cosmetic nit.
