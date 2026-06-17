/*
 * legal_docx.js — the single Word-rendering engine for the litigation skills suite.
 *
 * Owns the docx implementation of the suite's court-document look (see references/legal-docx.md
 * for the full API). Every skill that emits Word calls this module; none hand-roll docx
 * styling. Three surfaces:
 *
 *   1. A helper API for prose documents: section(), title/caption/sub/h1–h4, p/bullet/numbered/t/
 *      link/status, table(), box(), write().
 *   2. A data-driven builder: buildSpec()/writeSpec() turn a JSON `spec` (title, subtitle,
 *      footer, columns, groups[]/rows[]) into a checklist / punch-list / table document.
 *   3. Format profiles (brief, memo, letter, table) so callers pick a look without re-specifying
 *      spacing/indent/status defaults each time.
 *
 * The look: Times New Roman, black on white, blue underlined links (#0563C1), gray (#D9D9D9)
 * bold-black table headers, thin gray (#BFBFBF) cell borders, US Letter with 1" margins,
 * centered page-number-only footer.
 *
 * Requires the `docx` package: run `npm install docx` in the working dir, then
 *   const D = require("./scripts/legal_docx.js");
 */
const fs = require("fs");
const path = require("path");
const docx = require("docx");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, LineRuleType, ExternalHyperlink,
  BorderStyle, WidthType, ShadingType, PageNumber, VerticalAlign,
} = docx;

// ---- design-system constants (the one source of truth for the Word look) ----
const FONT = "Times New Roman";
const BLACK = "000000";
const GREY_TEXT = "595959";   // footer + sub-caption gray
const HEADER_FILL = "D9D9D9"; // table header row fill
const BOX_FILL = "F2F2F2";    // light callout/code box fill
const BORDER = "BFBFBF";      // thin gray cell border
const LINK = "0563C1";        // hyperlink blue, underlined
const STATUS = { green: "2E7D32", orange: "B26A00", blue: "0563C1", black: BLACK };

// Reconciled divergence — border weight. docx_style.js used size 1 (a 0.125pt hairline that
// renders inconsistently / can vanish across Word versions); build_punchlist_docx.js used
// size 4 (0.5pt). The design system asks for a *thin* gray rule, so we standardize on size 4:
// reliably visible, still thin. This is the one value used for every table border in the suite.
const BORDER_SIZE = 4;
const cellBorder = { style: BorderStyle.SINGLE, size: BORDER_SIZE, color: BORDER };
const cellBorders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };

const CONTENT_WIDTH = 9360; // US Letter content width at 1" margins (DXA)
const CELL_MARGINS = { top: 60, bottom: 60, left: 100, right: 100 };

// Heading geometry — shared by every profile. Four nested point-heading levels, each on a
// hanging indent: the hanging distance is constant (HEADING_STEP) while the left indent grows
// by one step per level (left = level × HEADING_STEP). That keeps each level's wrapped lines
// aligned under the title text (never under the enumerator) and steps each level 0.5" further
// right than the one above. 12 pt across all levels — hierarchy is carried by case/weight/
// italic/indent, not by size (see the heading() builder for per-level run styling).
const HEADING_STEP = 720; // 0.5" in twips
const HEADING_SIZE = 24;  // 12 pt, all four levels

// ---- format profiles ----
// A profile is the single place per-profile *typography* lives, so a caller picks a complete
// look by name instead of hand-setting spacing/indent/sizes. Explicit options always override.
// This split is the suite's two registers (see references/legal-docx.md):
//   • a court-filing register (brief) — double-spaced (or rules-driven); and
//   • a work-product register (memo/letter/table) — single-spaced.
// Every profile indents paragraphs 0.5" on the first line — legal documents indent.
// Units: half-points for sizes (24 = 12 pt); twips for spacing/indent (240 = single line,
// 480 = double, 720 = 0.5").
//   boldStatus      — also bold attention statuses (orange) in spec tables so they draw the eye?
//   lineSpacing     — body line spacing (twips); brief default is double, overridable by court rule
//   firstLineIndent — body first-line indent (twips); all profiles indent 0.5"
//   bodyAfter       — body paragraph spacing-after (twips); for briefs the line spacing carries it
//   titleSize       — document title font (half-points)
//   headingSize     — point-heading font, all levels (half-points)
const PROFILES = {
  // Court-filed brief: double-spaced, first-line-indented body; hanging point headings. lineSpacing
  // defaults to double but defers to a governing court rule when the caller passes one (see
  // Court-rules deference / the builders() factory).
  brief:  { boldStatus: false, lineSpacing: 480, firstLineIndent: 720, bodyAfter: 0,   titleSize: 24, headingSize: HEADING_SIZE },
  // Internal legal memo: single-spaced by default (callers double-space when they want it, e.g. a
  // long-form memo via builders("memo", { lineSpacing: 480 })).
  memo:   { boldStatus: false, lineSpacing: 240, firstLineIndent: 720, bodyAfter: 120, titleSize: 24, headingSize: HEADING_SIZE },
  // Client/opposing-counsel letter: single-spaced, airier body.
  letter: { boldStatus: false, lineSpacing: 240, firstLineIndent: 720, bodyAfter: 160, titleSize: 24, headingSize: HEADING_SIZE },
  // Spec-driven checklist / punch list / compliance table: single-spaced; bold the attention
  // (orange) statuses so non-compliant items draw the eye, per the punch list.
  table:  { boldStatus: true,  lineSpacing: 240, firstLineIndent: 720, bodyAfter: 120, titleSize: 24, headingSize: HEADING_SIZE },
};
function profile(name) {
  return PROFILES[name] || PROFILES.brief;
}
// Resolve a profile argument to a concrete typography object. Accepts a profile name
// ("brief"), an already-resolved profile/options object (returned as-is so caller overrides
// like a court-ordered lineSpacing survive), or undefined (→ the brief default).
function resolveProfile(p) {
  if (!p) return PROFILES.brief;
  if (typeof p === "string") return PROFILES[p] || PROFILES.brief;
  return p;
}

// ---- HTML-entity decoder (defensive backstop) ----
// Strings in this suite are meant to carry real Unicode punctuation ( ' " " — § ¶ ).
// If a stray &rsquo;/&mdash; slips in, it would otherwise print literally in Word — so we
// decode named + numeric entities here.
const NAMED = {
  amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: "\u00A0",
  rsquo: "\u2019", lsquo: "\u2018", rdquo: "\u201D", ldquo: "\u201C",
  mdash: "\u2014", ndash: "\u2013", hellip: "\u2026", sect: "\u00A7",
  para: "\u00B6", deg: "\u00B0", times: "\u00D7", middot: "\u00B7", trade: "\u2122",
};
function decode(s) {
  if (s == null) return "";
  return String(s)
    .replace(/&#x([0-9a-fA-F]+);/g, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(parseInt(d, 10)))
    .replace(/&([a-zA-Z]+);/g, (m, n) => (n in NAMED ? NAMED[n] : m));
}

// ---- document styles ----
// Heading hierarchy is shown by case / weight / italic / indent — never by size (all 12 pt) and
// never by a paragraph border (point headings carry no rule; see Change 1). Level 1 is rendered
// ALL CAPS via the run property so a drafter types normal text and the style capitalizes it.
function styles() {
  return {
    default: { document: { run: { font: FONT, size: 24, color: BLACK } } }, // 12 pt body
    paragraphStyles: [
      {
        id: "TitleX", name: "TitleX", basedOn: "Normal", next: "Normal",
        run: { size: HEADING_SIZE, bold: true, font: FONT, color: BLACK },
        paragraph: { spacing: { after: 120 }, keepNext: true },
      },
      // All headings carry keepNext so a heading never strands alone at the bottom of a page —
      // it stays with the paragraph that follows it. spacing.after is a full line (240 twips =
      // 12 pt) so there is real air between a heading and the paragraph that follows.
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: HEADING_SIZE, bold: true, allCaps: true, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 280, after: 240 }, outlineLevel: 0, keepNext: true },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: HEADING_SIZE, bold: true, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 1, keepNext: true },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: HEADING_SIZE, italics: true, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 200, after: 240 }, outlineLevel: 2, keepNext: true },
      },
      {
        id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: HEADING_SIZE, font: FONT, color: BLACK },
        paragraph: { spacing: { before: 200, after: 240 }, outlineLevel: 3, keepNext: true },
      },
    ],
  };
}

// One multilevel numbering definition for the four point-heading levels, so I / A / i / a
// auto-increment and reset correctly per nesting and drafters never hand-maintain enumerators.
// The per-level indent (constant 0.5" hang, +0.5" left per level) lives here in one place; a
// "tab" suffix lands the title at the body indent so wrapped lines align under the title text.
const headingLevels = [
  { level: 0, format: LevelFormat.UPPER_ROMAN,  text: "%1.", left: HEADING_STEP * 1 },
  { level: 1, format: LevelFormat.UPPER_LETTER, text: "%2.", left: HEADING_STEP * 2 },
  { level: 2, format: LevelFormat.LOWER_ROMAN,  text: "%3.", left: HEADING_STEP * 3 },
  { level: 3, format: LevelFormat.LOWER_LETTER, text: "%4.", left: HEADING_STEP * 4 },
].map((l) => ({
  level: l.level, format: l.format, text: l.text, alignment: AlignmentType.LEFT, suffix: "tab",
  style: { paragraph: { indent: { left: l.left, hanging: HEADING_STEP } } },
}));

const numbering = {
  config: [
    {
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 480, hanging: 240 } } },
      }],
    },
    // Decimal ordered list (1. 2. 3. …) on a hanging indent, so wrapped lines align under the item
    // text, not under the number. Geometry: the number sits at a full 0.5" indent (like a paragraph
    // first line) and the text hangs 0.25" after it — left 1080 (0.75") with a 360 (0.25") hang puts
    // the number at 0.5" and the text (and its wrapped lines) at 0.75". Used by numbered() for
    // enumerated issues (Questions Presented, Brief Answers, numbered allegations). Each separate
    // list restarts via numbered()'s `instance`.
    {
      reference: "numbers",
      levels: [{
        level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
      }],
    },
    { reference: "headings", levels: headingLevels },
  ],
};

// ---- runs & paragraphs ----
const t = (text, o = {}) => new TextRun({ text: decode(text), font: FONT, ...o });
function link(text, url, o = {}) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text: decode(text), style: "Hyperlink", font: FONT, color: LINK, underline: {}, ...o })],
  });
}
// A colored status run per the shared status vocabulary (green/orange/blue/black). Pass
// { bold: true } to also bold it. Both forms are supported so callers can use color, bold, or
// both — reconciling docx_style's color-only status with the punch list's bold-only status.
const status = (text, color = "black", o = {}) => new TextRun({ text: decode(text), font: FONT, color: STATUS[color] || BLACK, ...o });

// Map a status word to its design-system color. Drives the spec builder's status column.
const STATUS_WORDS = {
  compliant: "green", done: "green", favorable: "green", complete: "green", filed: "green", granted: "green",
  fix: "orange", pending: "orange", caution: "orange", review: "orange", "needs review": "orange", overdue: "orange",
  informational: "blue", info: "blue", neutral: "blue", "n/a": "black", na: "black", "": "black",
};
function statusColorFor(text) {
  return STATUS_WORDS[String(text || "").trim().toLowerCase()] || "black";
}

const asRuns = (c) => (Array.isArray(c) ? c : [typeof c === "string" ? t(c) : c]);

// Body paragraph — profile-aware. Reads line spacing, first-line indent, and spacing-after from
// the active profile: a brief renders double-spaced, a memo single-spaced, and every profile
// indents the first line 0.5". Any of those can be overridden inline (e.g. a court-ordered spacing
// via `lineSpacing`, or `firstLineIndent: 0` for a centered caption line); inline wins over the
// profile, which wins over the brief default.
//   p(content, { profile, lineSpacing, firstLineIndent, after, ...paragraphOpts })
const p = (c, o = {}) => {
  const { profile: prof, lineSpacing, firstLineIndent, after, ...rest } = o;
  const P = resolveProfile(prof);
  const line = lineSpacing != null ? lineSpacing : P.lineSpacing;
  const fli = firstLineIndent != null ? firstLineIndent : P.firstLineIndent;
  const aft = after != null ? after : P.bodyAfter;
  const para = { children: asRuns(c), spacing: { line, lineRule: LineRuleType.AUTO, after: aft }, ...rest };
  if (fli) para.indent = { firstLine: fli, ...(rest.indent || {}) };
  return new Paragraph(para);
};
const bullet = (c) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: asRuns(c) });

// Numbered (ordered) list item — "1. 2. 3." on a hanging indent, so wrapped lines align under the
// item text rather than under the number (the fix for enumerated Questions Presented / Brief
// Answers / numbered allegations that otherwise wrap flush-left and read ragged). Profile-aware for
// spacing like p(). Pass a distinct `instance` per list so each list restarts at 1 instead of
// continuing the previous one's count.
//   numbered(content, { instance, profile, lineSpacing, after, ...paragraphOpts })
const numbered = (c, o = {}) => {
  const { profile: prof, instance, lineSpacing, after, ...rest } = o;
  const P = resolveProfile(prof);
  const line = lineSpacing != null ? lineSpacing : P.lineSpacing;
  const aft = after != null ? after : P.bodyAfter;
  const num = { reference: "numbers", level: 0 };
  if (instance != null) num.instance = instance;
  return new Paragraph({ numbering: num, spacing: { line, lineRule: LineRuleType.AUTO, after: aft }, children: asRuns(c), ...rest });
};
const title = (text, o = {}) => {
  const P = resolveProfile(o.profile);
  const size = o.size != null ? o.size : P.titleSize;
  return new Paragraph({ style: "TitleX", ...(o.alignment ? { alignment: o.alignment } : {}), children: [t(text, { size, bold: true, ...(o.run || {}) })] });
};
const caption = (text) => new Paragraph({ spacing: { after: 20 }, children: [t(text, { bold: true, size: 24 })] });
const sub = (text) => new Paragraph({ spacing: { after: 200 }, children: [t(text, { size: 20, color: GREY_TEXT })] });

// Four-level nested point headings. Each level is a hanging-indent paragraph bound to the shared
// "headings" multilevel numbering (I / A / i / a auto-increment, geometry from headingLevels):
//   Level 1 — UPPER ROMAN, ALL CAPS, bold
//   Level 2 — UPPER ALPHA, mixed case, bold
//   Level 3 — lower roman, mixed case, italic (not bold)
//   Level 4 — lower alpha, mixed case, regular
// All four are 12 pt; the per-level run styling is applied to the whole run (enumerator included
// via the matching paragraph style). Hierarchy is case/weight/italic/indent — never size, never a
// border. If the caller passes `label` (and `numbering: false`), the same indent/tab geometry and
// run styling apply but the enumerator is taken verbatim instead of auto-numbered.
const HEADING_STYLE = { 1: "Heading1", 2: "Heading2", 3: "Heading3", 4: "Heading4" };
const HEADING_RUN = {
  1: { bold: true, allCaps: true },
  2: { bold: true },
  3: { italics: true },
  4: {},
};
function heading(level, text, o = {}) {
  const lvl = Math.min(4, Math.max(1, level | 0));
  const P = resolveProfile(o.profile);
  const size = o.size != null ? o.size : P.headingSize;
  const runOpts = { size, ...HEADING_RUN[lvl], ...(o.run || {}) };
  const autoNumber = o.numbering !== false && o.label == null;
  const para = { style: HEADING_STYLE[lvl] };
  if (autoNumber) {
    para.numbering = { reference: "headings", level: lvl - 1 };
  } else {
    // Caller-supplied label: reproduce the level's hanging geometry by hand and prefix the
    // enumerator + a real tab so the title lands at the body indent.
    para.indent = { left: HEADING_STEP * lvl, hanging: HEADING_STEP };
  }
  const titleRuns = typeof text === "string" ? [t(text, runOpts)] : asRuns(text);
  const label = o.label != null ? [t(String(o.label) + "\t", runOpts)] : [];
  para.children = [...label, ...titleRuns];
  return new Paragraph(para);
}
const h1 = (text, o = {}) => heading(1, text, o);
const h2 = (text, o = {}) => heading(2, text, o);
const h3 = (text, o = {}) => heading(3, text, o);
const h4 = (text, o = {}) => heading(4, text, o);

// ---- tables ----
function cell(content, { w, fill, margins } = {}) {
  const paras = asRuns(content).map((c) => (c instanceof Paragraph ? c : new Paragraph({ children: [c] })));
  return new TableCell({
    borders: cellBorders,
    width: { size: w, type: WidthType.DXA },
    shading: fill ? { fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: margins || CELL_MARGINS,
    verticalAlign: VerticalAlign.CENTER,
    children: paras.length ? paras : [new Paragraph({})],
  });
}

// Generic gray-header table. Cells accept strings, runs, or Paragraphs. `size` (half-points)
// sets the default text size for header + string cells — pass 24 for full 12 pt legal-document
// tables (e.g. the case-manager deliverables); defaults to 18 (9 pt) for compact reference tables.
function table({ headers, widths, rows, size = 18 }) {
  const total = widths.reduce((a, b) => a + b, 0);
  const head = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) =>
      cell(new Paragraph({ children: [t(h, { bold: true, size, color: BLACK })] }), { w: widths[i], fill: HEADER_FILL })),
  });
  const body = rows.map((r) => new TableRow({
    children: r.map((c, i) => {
      const content = typeof c === "string" ? new Paragraph({ children: [t(c, { size })] })
        : c instanceof Paragraph ? c
        : new Paragraph({ children: asRuns(c) });
      return cell(content, { w: widths[i] });
    }),
  }));
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [head, ...body] });
}

// Light-gray callout box (e.g., a copy-paste email block).
function box(runs) {
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: [CONTENT_WIDTH],
    rows: [new TableRow({ children: [cell(new Paragraph({ children: asRuns(runs) }), { w: CONTENT_WIDTH, fill: BOX_FILL })] })],
  });
}

// ---- section (page setup, footer) ----
// The footer is nothing but a centered Times New Roman page number — no labels, no "Page",
// no color. This is the one footer for every document in the suite.
function footer() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 24, font: FONT, color: BLACK })],
    })],
  });
}
// Optional one-line page header (small gray italic, right-aligned) — used for required notices
// like the cite-check disclaimer. Not a privilege stamp; the suite does not stamp documents.
function headerLine(text) {
  return new Header({
    children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      spacing: { after: 0 },
      children: [t(text, { size: 16, italics: true, color: GREY_TEXT })],
    })],
  });
}
// section({ profile, lineSpacing, header, children }) — page setup + footer. `lineSpacing` is
// accepted as a court-rules-deference override: pass it the spacing a governing rule requires and
// it wins over the profile default for body paragraphs built with the matching builders() (see
// Court-rules deference); when omitted the profile default stands. `header` (optional) renders a
// one-line notice in the page header on every page (e.g. the cite-check disclaimer). The footer is
// always just the centered page number — there is no footer-label option.
function section({ profile: profileName, lineSpacing, header, children = [] }) {
  return {
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: header ? { default: headerLine(header) } : undefined,
    footers: { default: footer() },
    children,
  };
}

// builders(profile, overrides) — the recommended call site. Returns the prose builders bound to a
// resolved profile so every p()/title()/heading() reads the right typography without restating it,
// and threads any overrides (e.g. a court-ordered { lineSpacing }) through all of them. This is how
// Court-rules deference is plumbed: builders("brief", { lineSpacing: court.lineSpacing }).
function builders(profileName = "brief", overrides = {}) {
  const prof = { ...resolveProfile(profileName), ...overrides };
  const withProfile = (o = {}) => ({ profile: prof, ...o });
  return {
    profile: prof,
    t, link, status, bullet, caption, sub, cell, table, box, // typography-neutral helpers pass through
    p: (c, o) => p(c, withProfile(o)),
    numbered: (c, o) => numbered(c, withProfile(o)),
    title: (text, o) => title(text, withProfile(o)),
    heading: (level, text, o) => heading(level, text, withProfile(o)),
    h1: (text, o) => heading(1, text, withProfile(o)),
    h2: (text, o) => heading(2, text, withProfile(o)),
    h3: (text, o) => heading(3, text, withProfile(o)),
    h4: (text, o) => heading(4, text, withProfile(o)),
    section: (o = {}) => section({ profile: profileName, ...o }),
    write,
  };
}

function write(filename, sections, outDir, opts = {}) {
  const doc = new Document({
    styles: styles(),
    numbering,
    sections,
    ...(opts.comments ? { comments: opts.comments } : {}),
  });
  return Packer.toBuffer(doc).then((buf) => {
    const out = path.join(outDir, filename);
    fs.writeFileSync(out, buf);
    return out;
  });
}

// ---- review helpers: real Word comments + tracked changes (redlines) ----
// Used by cite-check (and any skill that marks up a document). All markup is attributed to one
// author so Word shows a single reviewer. Usage:
//
//   const R = D.review();                       // author defaults to "Midpage Cite Check"
//   B.p([ ...R.comment([B.t("Smith v. Jones, 999 F.3d 100")], "Verified — resolves on Midpage: <url>") ])
//   B.p([ R.del("the old wrong quote"), R.ins("the corrected verbatim quote") ])
//   B.write("out.docx", [sec], dir, { comments: R.comments() });   // REQUIRED when comments were used
function review(author = "Midpage Cite Check") {
  const commentList = [];
  let nextComment = 0;
  let nextRev = 0;
  const date = new Date();

  // Tracked-change runs (render as redline insertions/deletions in Word).
  const ins = (text, opts = {}) =>
    new docx.InsertedTextRun({ text: decode(text), id: nextRev++, author, date, font: FONT, size: 24, ...opts });
  const del = (text, opts = {}) =>
    new docx.DeletedTextRun({ text: decode(text), id: nextRev++, author, date, font: FONT, size: 24, ...opts });

  // Wrap anchor run(s) in a comment range. `text` is a string or an array of runs.
  // Returns the runs to splice into the paragraph's children.
  const comment = (anchorRuns, text) => {
    const id = nextComment++;
    const body = Array.isArray(text) ? text : [t(text)];
    commentList.push({ id, author, date, children: [new Paragraph({ children: body })] });
    const anchors = Array.isArray(anchorRuns) ? anchorRuns : [anchorRuns];
    return [
      new docx.CommentRangeStart(id),
      ...anchors,
      new docx.CommentRangeEnd(id),
      new TextRun({ children: [new docx.CommentReference(id)] }),
    ];
  };

  return { ins, del, comment, comments: () => ({ children: commentList }) };
}

// ---- spec-driven builder (ported from build_punchlist_docx.js) ----
// Column definitions: label + relative weight used to auto-size columns to CONTENT_WIDTH.
const COLDEF = {
  requirement: { label: "Requirement",   weight: 3.0 },
  source:      { label: "Source",        weight: 1.8 },
  status:      { label: "Status",        weight: 1.3 },
  action:      { label: "Action needed", weight: 3.1 },
};

function computeWidths(columns) {
  const total = columns.reduce((s, c) => s + COLDEF[c].weight, 0);
  const w = columns.map((c) => Math.round((COLDEF[c].weight / total) * CONTENT_WIDTH));
  w[w.length - 1] += CONTENT_WIDTH - w.reduce((s, x) => s + x, 0); // absorb rounding into last col
  return w;
}

function specCell(content, w, { header = false } = {}) {
  return cell(content, { w, fill: header ? HEADER_FILL : undefined, margins: { top: 80, bottom: 80, left: 120, right: 120 } });
}

function renderSpecCell(col, row, w, opts) {
  if (col === "source") {
    if (!row.sourceUrl) return specCell([t(row.sourceText || "", { size: 18 })], w);
    return specCell([link(row.sourceText || row.sourceUrl, row.sourceUrl, { size: 18 })], w);
  }
  if (col === "status") {
    const v = row.status || "";
    const color = statusColorFor(v);
    // Bold attention (orange) statuses when the profile asks for it, or when the row opts in.
    const bold = row.statusBold === true || (row.statusBold !== false && opts.boldStatus && color === "orange");
    return specCell([status(v, color, { size: 18, bold })], w);
  }
  return specCell([t(row[col] != null ? String(row[col]) : "", { size: 18 })], w);
}

function buildSpecTable(columns, rows, opts) {
  const widths = computeWidths(columns);
  const headerRow = new TableRow({
    tableHeader: true,
    children: columns.map((c, i) => specCell([t(COLDEF[c].label, { bold: true, size: 18, color: BLACK })], widths[i], { header: true })),
  });
  const bodyRows = (rows || []).map((row) =>
    new TableRow({ children: columns.map((c, i) => renderSpecCell(c, row, widths[i], opts)) }));
  return new Table({ width: { size: CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: widths, rows: [headerRow, ...bodyRows] });
}

function groupHeading(group) {
  const runOpts = { bold: true, size: 24 };
  const child = group.headingUrl
    ? link(group.heading, group.headingUrl, runOpts)
    : t(group.heading, runOpts);
  return new Paragraph({ spacing: { before: 240, after: 100 }, children: [child] });
}

// buildSpec(spec, profileName?) → a section ready for write(). Turns a JSON spec into a
// table/checklist/punch-list document. Supports grouped (groups[]) and flat (rows[]) shapes.
function buildSpec(spec, profileName = "table") {
  const prof = profile(profileName);
  const opts = { boldStatus: spec.boldStatus === undefined ? prof.boldStatus : spec.boldStatus };
  const columns = (spec.columns && spec.columns.length ? spec.columns : ["requirement", "source", "status", "action"]).filter((c) => COLDEF[c]);

  const children = [];
  if (spec.title) {
    children.push(new Paragraph({ spacing: { after: spec.subtitle ? 40 : 160 }, children: [t(spec.title, { bold: true, size: 28 })] }));
  }
  if (spec.subtitle) {
    children.push(new Paragraph({ spacing: { after: 120 }, children: [t(spec.subtitle, { italics: true })] }));
  }
  if (Array.isArray(spec.groups) && spec.groups.length) {
    for (const g of spec.groups) {
      children.push(groupHeading(g));
      const cols = g.columns && g.columns.length ? g.columns.filter((c) => COLDEF[c]) : columns;
      children.push(buildSpecTable(cols, g.rows, opts));
    }
  } else {
    children.push(buildSpecTable(columns, spec.rows, opts));
  }
  if (spec.footer) {
    children.push(new Paragraph({ spacing: { before: 220 }, children: [t(spec.footer, { italics: true, size: 18 })] }));
  }

  return section({ header: spec.header, children });
}

// Convenience: build a spec and write it to disk in one call.
function writeSpec(filename, spec, outDir, profileName = "table") {
  return write(filename, [buildSpec(spec, profileName)], outDir);
}

module.exports = {
  docx, // re-export classes for advanced use
  COLORS: { BLACK, LINK, HEADER_FILL, BOX_FILL, BORDER, GREY_TEXT, STATUS },
  PROFILES, profile, resolveProfile, builders,
  decode, statusColorFor,
  // helper API (prose docs)
  t, link, status, p, bullet, numbered, title, caption, sub, heading, h1, h2, h3, h4,
  cell, table, box, section, write,
  // review markup (Word comments + tracked changes)
  review,
  // spec-driven builder (table / checklist / punch-list docs)
  COLDEF, computeWidths, buildSpec, writeSpec,
};
