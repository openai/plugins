# Rendering — legal_docx.js (Word)

Every Word document in this suite is rendered through `scripts/legal_docx.js`, so two outputs
from two skills look like siblings. Never hand-roll docx styling; if something is missing,
extend the script.

**The look it enforces: court-document style, restrained.** Times New Roman throughout (never
a sans-serif unless a court rule requires it), black on white, hierarchy from case, weight,
italics, and indent — never from typeface or size changes. The only color is links (blue
`#0563C1`, underlined) and status words. Tables are real aligned tables with a gray header
row, never stacked cards. Page: US Letter, 1″ margins, footer is nothing but a centered page
number.

## Setup

```bash
npm install docx   # in the working directory (Node 18+; works in Claude's and OpenAI's code environments)
```

```js
const D = require("./scripts/legal_docx.js");
const { Paragraph, AlignmentType } = D.docx;   // docx classes re-exported for advanced use
```

## Profiles — pick a register, don't hand-set typography

Bind the builders to a profile so a document can't drift: `const B = D.builders(profile,
overrides?)`. Overrides are the court-rules-deference hook — when a rule fixes spacing, pass
it; when rules are silent, the default stands. Units: sizes in half-points (24 = 12 pt),
spacing/indent in twips (240 single, 360 = 1.5, 480 double, 720 = 0.5″).

| Profile | Body spacing | Use |
|---|---|---|
| `brief` | double (rule-overridable) | Court-filed brief/motion |
| `memo` | single (double-space long-form: `{ lineSpacing: 480 }`) | Internal memo / work product |
| `letter` | single, airier | Client or counsel letter |
| `table` | single; bolds attention statuses | Spec-driven checklist / punch list |

All profiles: 0.5″ first-line indent (legal documents indent), title and all headings 12 pt,
no heading rules or shading, US Letter, 1″ margins, footer is nothing but a centered page
number.

```js
const B = D.builders("brief", { lineSpacing: 360 });  // judge's order requires 1.5
const B = D.builders("memo",  { lineSpacing: 480 });  // long-form memo, double-spaced
```

## Builder API

`D.builders()` returns `{ section, title, caption, sub, p, bullet, numbered, heading, h1–h4,
t, link, status, table, box, cell, write, profile }`.

- `B.title(text, opts)` — bold 12 pt title; center with `{ alignment: AlignmentType.CENTER }`.
- `B.caption(text)` / `B.sub(text)` — bold case caption; gray sub-line.
- `B.p(content, opts)` — body paragraph (spacing/indent from the profile). `content` is a
  string, a run, or an array of runs. Inline `opts` override per-paragraph — e.g. a centered
  caption line: `B.p(text, { alignment: AlignmentType.CENTER, firstLineIndent: 0, lineSpacing: 240 })`.
- `B.h1`–`B.h4` — the four nested court point headings, auto-numbered `I. / A. / i. / a.` on
  hanging indents (0.5″ hang, +0.5″ left per level). Level 1 ALL CAPS bold, 2 bold, 3 italic,
  4 regular. Keep-with-next and space-after are built in. Type plain heading text; the style
  capitalizes Level 1. Custom enumerator: `{ label: "I", numbering: false }`.
- `B.t(text, opts)` / `B.link(text, url)` / `B.status(text, "green"|"orange"|"blue"|"black", opts)`
  — a Times run, a blue underlined hyperlink, a colored status run (`{ bold: true }` to bold).
- `B.bullet(content)` / `B.numbered(content, { instance })` — real Word lists on hanging
  indents so wrapped lines align under the text. Each distinct numbered list needs its own
  `instance` so it restarts at 1. Never fake a list with a literal "1." + tab.
- `B.table({ headers, widths, rows, size })` — gray-header table (`#D9D9D9` header, thin
  `#BFBFBF` borders). `widths` in DXA summing ≤ 9360. Cells take strings, runs, arrays, or
  Paragraphs. **`size: 24` for full 12 pt legal-document tables** (default 18 is compact).
- `B.box(runs)` — light-gray callout box.
- `B.section({ header, children })` — page setup; optional `header` renders a one-line gray
  notice on every page (e.g. a required disclaimer). No footer options — always just the page
  number.
- `B.write(filename, [section], outDir, opts?)` — packs and writes; returns a Promise of the
  path. Pass `{ comments: R.comments() }` when review comments were used (below).

Status color vocabulary: Compliant/Done/Favorable → green `#2E7D32`;
Fix/Pending/Caution/Review → orange `#B26A00`; Informational → blue `#0563C1`; N/A → black.
Never a bare green/red pair.

## Comments and tracked changes (review markup)

For marking up a document — cite-check's whole deliverable — use `D.review()`. It returns
helpers whose output renders as real Word comments and redline suggestions, all attributed to
one reviewer (default author: "Midpage Cite Check"):

```js
const R = D.review();   // or D.review("Custom Author")

// Comment anchored to specific run(s) — returns runs to splice into a paragraph:
B.p([ ...R.comment([B.t("Smith v. Jones, 999 F.3d 100 (9th Cir. 2021)")],
      "OK — resolves on Midpage; proposition supported. https://app.midpage.ai/…") ])

// Tracked changes — visible redline the reader can accept/reject:
B.p([ B.t("harm must be "), R.del("possible"), R.ins("likely"), B.t(".") ])

// Writing REQUIRES passing the comments:
B.write("out.docx", [sec], outDir, { comments: R.comments() });
```

`R.comment(anchorRuns, text)` wraps the anchors in a comment range; `R.ins(text)` /
`R.del(text)` are tracked insertions/deletions (Times New Roman 12 pt by default; pass run
opts to match other styling). Never alter body text directly — every suggested change is an
`ins`/`del` pair so it's visibly a suggestion.

## Spec-driven tables (checklists, reports)

For source-linked table documents, build one JSON `spec` and render it with
`D.writeSpec(filename, spec, outDir, "table")`: `title`, `subtitle`, `footer`, optional
`header` (page-header notice), `columns` (any of `requirement`, `source`, `status`,
`action`), and `groups[]` (each `{ heading, headingUrl?, rows[] }`) or flat `rows[]`. Each
row: `requirement`, `sourceText`, `sourceUrl`, `status`, `action`. The `source` column
renders as a blue link; `status` is colored by the shared vocabulary, with orange (attention)
statuses bolded under the `table` profile.

## Two rules that bite

- **Real Unicode punctuation everywhere** (' " " — § ¶), never HTML entities. (A defensive
  decoder catches strays; do not rely on it.)
- **Validate after rendering** when a court rule drove a setting: line spacing matches the
  rule, first-line indents present, no `<w:pBdr>` on headings (grep the unzipped
  `document.xml`), length within the limit.
