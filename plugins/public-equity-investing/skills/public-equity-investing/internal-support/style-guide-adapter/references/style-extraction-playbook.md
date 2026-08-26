# Style Extraction Playbook

Use this guide when turning a style guide, precedent, template, or current artifact into a reusable style profile.

## 1. Classify each source

Record each source as one of:

- **official guide**: brand book, style guide, compliance-approved writing guide, legal/disclosure guide.
- **template/master**: PowerPoint template, Word template, spreadsheet/model shell, memo shell, research report shell.
- **final precedent**: sent, board-ready, client-ready, committee-approved, published, or final artifact.
- **draft precedent**: working version or partially styled sample.
- **current artifact**: the deck/doc/model being edited.
- **verbal instruction**: user-provided preference or target style description.
- **public brand source**: website, annual report, investor presentation, or public style reference.
- **industry default**: generic finance style used only when no better source exists.

For each source, capture: artifact type, audience, date/period, author/team/client, final-vs-draft status, source confidence, and any obvious limitations.

## 2. Extract visual system

Look for rules that appear in official guides, masters, templates, or repeated precedent patterns.

### Colors

Capture:

- primary brand colors and secondary/accent colors
- neutral palette, background colors, divider colors, table fills, and gridlines
- semantic colors for positive/negative/neutral, actual/forecast, downside/base/upside, primary/secondary series
- colors to avoid or use sparingly
- accessibility concerns, especially low contrast or red/green-only encoding

Prefer exact RGB/hex values from theme XML, style guides, or templates. If colors are inferred from screenshots or images, label them as approximate.

### Typography

Capture:

- font family for title, subtitle, body, labels, footnotes, tables, chart labels, callouts, and appendix text
- relative size hierarchy and weight, not just exact point sizes
- capitalization rules: title case, sentence case, all caps, small caps
- line spacing, bullet indentation, paragraph spacing, and dense-vs-airy layout preference
- treatment of numbers, tickers, company names, and acronyms

Do not embed or share font files. If the font is unavailable, select a reasonable fallback and label it.

### Layout grammar

Capture:

- page/slide size and orientation
- margin grid, column structure, title block, and content zones
- footer structure: source line, page number, confidential label, logo, date, author, client name
- section divider style and appendix style
- title/subtitle/callout placement
- exhibit density: number of charts/tables per page, white space norms, and annotation style
- use of icons, logos, imagery, and watermarks

### Chart and table style

Capture:

- preferred chart types and when they are used
- axis, label, legend, gridline, and data-label conventions
- number formatting: decimals, percentages, basis points, multiples, currency, K/M/B notation
- table header style, subtotal/total rows, zebra striping, border weight, and variance columns
- footnote markers, source placement, and chart annotations
- color mapping for scenarios, time periods, benchmarks, and comparables

## 3. Extract writing style

Capture:

- headline style: descriptive label vs full so-what sentence
- tone: neutral, assertive, analytical, promotional, skeptical, legalistic, investor-oriented, executive-facing
- default structure: recommendation-first, issue-analysis-recommendation, thesis-evidence-risk, or summary-details-appendix
- bullet style: fragments vs complete sentences, punctuation, parallelism, indentation, and bold lead-ins
- treatment of caveats, risk language, assumptions, and management claims
- citation style: inline links, footnotes, endnotes, source lines, appendix source tables, or cell comments
- audience-specific language: banker, investor, CFO, board, lender, committee, public research, client pitch

## 4. Identify rules versus quirks

Classify each finding:

- **rule**: explicitly stated or repeated consistently across high-priority sources.
- **pattern**: repeated in precedents but not written down.
- **quirk**: appears once or conflicts with higher-priority style.
- **artifact constraint**: caused by the current file, tool, template, or source data rather than a style preference.

Apply rules and patterns. Avoid copying quirks unless the user specifically wants to match that exact artifact.

## 5. Build a style profile

Use this compact structure:

```markdown
# Style profile: [institution/client/artifact]

## Source basis
| Source | Type | Priority | Freshness | Relevance | Notes |
|---|---:|---:|---:|---:|---|

## Core style rules
- Visual identity:
- Layout grammar:
- Chart/table conventions:
- Writing voice:
- Citation/source style:
- Do-not-change rules:

## Artifact-specific application
- Deck:
- Memo/report:
- Spreadsheet/model:

## Inferred assumptions
- [Assumption] [why chosen] [confidence]

## Conflicts/open questions
- [Conflict or missing input] [recommended resolution]
```

## 6. Office metadata extraction

For Office files, use `scripts/extract_office_style.py` when available to extract theme fonts, theme colors, named styles, slide layout names, workbook sheet names, and style metadata. Treat this as a supplement, not a substitute for visual review.

- Theme XML is reliable for available palette and fonts, but it may not reflect manual overrides.
- Named styles can show intent, but not all content uses them consistently.
- Rendered review is still required for final visual fidelity, especially for charts, images, complex tables, and manually positioned objects.
