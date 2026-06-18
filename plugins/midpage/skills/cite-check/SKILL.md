---
name: cite-check
description: "Cite-checks a brief, motion, or memo (PDF/Word): verifies each cited case is real, supports the proposition, is good law, and quoted accurately. Returns one marked-up .docx with comments and redlines."
metadata:
  version: 0.2.0
  author: midpage
---

# Cite-check

Audit every citation in an uploaded document against ground truth, and hand back **one
deliverable**: a `.docx` that recreates the document exactly, marked up with Word comments and
tracked-change suggestions. AI-drafted briefs invent cases, misstate holdings, and alter
quotes; human drafts cite stale law and miscite the record. Every citation gets checked
through the Midpage tools and every finding lands in the document itself, anchored where it
occurs. Read `references/citations.md` for citation form and `references/legal-docx.md` for
the renderer (including the `D.review()` comment/redline helpers).

## Workflow

### 1. Intake (PDF or Word)

Read the uploaded file faithfully — full text, in order: for a PDF, extract the text; for a
`.docx`, read the document body. Then extract every authority: case citations (with the
proposition each is cited for and any quotation attributed to it) and record citations (ECF
numbers, page/¶ pins, declarations, exhibits). Build the complete citation inventory **before**
checking anything — exhaustiveness starts here; a citation missed at intake is a citation
never checked. If the document is a federal filing, note the court and docket number from the
caption; ask for the docket if record cites are present and you don't have it.

### 2. Run the five checks — on every citation, no exceptions

Work citation by citation; run independent `analyzeOpinion` calls in parallel. Never assert a
cite is good until a tool confirms it this session.

1. **The case is real.** Resolve via `analyzeOpinion` — `reporterCitation` exactly as cited,
   or the `docket` tuple (court abbreviation + docket number, no "No." prefix) for
   unpublished cases, or a known `opinionId`. Set `question` to the cited proposition so the
   same call feeds check 2. Resolves → real; use the returned `citation` and `url`. Won't
   resolve → **Review**: it may be a fabrication or a case the resolver missed — the attorney
   must check. Never substitute a "corrected" cite from memory. A real but mis-formatted cite
   that still resolves: existence confirmed, formatting flagged with the tool's exact
   citation string as the suggested correction.
   **WL / LEXIS / other commercial-database citations:** Midpage cannot verify a citation to
   another commercial database. Resolve the case itself (by case name + court/docket tuple)
   and run the remaining checks against the version Midpage has; the comment must say so (see
   Comment format). Any suggested correction uses the reporter or docket-number citation the
   tool returns — never WL/LEXIS.
2. **The proposition isn't mischaracterized.** Check `**doesNotAddress` first** — if the
  document's point is listed, the case does not stand for it → **Fix** (the most damaging
   miscite). Otherwise match against `supportedPropositions`: honor `scope` qualifiers;
   central reliance on a `background`/`secondary_matter` match → **Review** (weak support);
   a concurrence or dissent (`opinionSection`) sold as the court's holding → **Fix**. A
   fair-but-aggressive reading the tool can't settle → **Review**, saying what the case
   actually supports.
3. **Treatment / favorability.** `treatment` negative (reversed, overruled, criticized) →
  **Fix**, flagged prominently; caution → **Review**. Separately: does the case actually
   help the position citing it? Positive treatment with a holding that cuts against the use →
   **Review**, explained.
4. **Quotes are verbatim.** Compare each quotation to the verified `quote` in
  `supportedPropositions`; if not covered, `findInOpinion` with keywords from the quote.
   Verbatim → **OK**. Altered → **Fix** with the correct language. Not found → **Review**
   (keyword search can miss) — never assert a quote is accurate just because the case exists.
5. **Record cites** (federal filings, docket provided). `analyzeDocketReport` to locate the
  entry (missing from the docket → **Fix**), then `analyzeDocketFiling` asking whether the
   cited content is actually in that filing. Present → **OK**; absent or different → **Fix**,
   noting what the filing actually says. No docket / not federal → every record cite is
   **Review** with a comment that it could not be checked without the docket.

### 3. Build the marked-up .docx (the deliverable)

One Word document, rendered through `scripts/legal_docx.js`, in three layers:

**Cover page** (centered, then a page break):

- Title: **Midpage Cite Check**
- Subtitle: the filing name, *Party X v. Party Y*, Case No. XX-XXXXX (from the document's
caption; leave a clearly marked placeholder for anything the document doesn't supply —
never invent it).
- **Scope line** (one or two lines, only what's needed): which portions of the document were
reviewed if not the whole thing (e.g. "Scope of this review: the facts section (¶¶ 8–11,
pp. 5–6) and the argument section (¶¶ 18–27, pp. 10–15)."), plus this fixed sentence:
*Pin-cite page accuracy is not verified.*
- Disclaimer, exactly: *This cite check only flags potential errors detected by Midpage. It
is not intended to replace an attorney cite check. AI makes mistakes and outputs should be
verified independently.*

That is the whole cover — no "what was checked / what was not checked" essay, no methodology
narration, no per-category inventory. The honesty lives where the reader needs it: each
citation's own comment says what was confirmed or why it couldn't be checked, and the chat
report carries the counts and the uncheckable items.

**Exact recreation.** Recreate the uploaded document's substantive content **exactly** —
same text, same order, same headings, same numbering. The unmarked text must read identically
to the original: recreate first, mark up second. You may omit a table of contents, table of
authorities, and the case caption if present — it's the substantive content being checked.
Match the document's structure with the builder API (headings via `B.h1`–`B.h4` or bold
paragraphs to mirror the original's levels; body via `B.p`; numbered paragraphs via
`B.numbered`).

**The markup.** Every finding goes in (a) a Word comment and/or (b) an inline tracked
change — nothing else, and nothing in the body text itself:

```js
const D = require("./scripts/legal_docx.js");
const B = D.builders("brief");          // mirror the original's register
const R = D.review();                   // author: "Midpage Cite Check"

// a comment anchored to a citation:
B.p([ ...R.comment([B.t("Smith v. Jones, 999 F.3d 100 (9th Cir. 2021)")],
      "OK — cited proposition supported (core holding).\nhttps://app.midpage.ai/…") ])

// a redline suggestion (paired with a short comment explaining the basis):
B.p([ B.t("harm must be "), R.del("possible"), R.ins("likely"), B.t(".") ])

// write — passing the comments is required:
B.write("Midpage Cite Check - <filing name>.docx", [cover, body], outDir, { comments: R.comments() });
```

- **Every citation in the inventory gets a comment** — including the clean ones. A verified
cite gets "OK — …" with the verified Midpage link; that is how the reader knows it was
checked rather than skipped. Prefix every comment with its status: `OK`, `Fix`, or
`Review`.
- **Concrete corrections are tracked changes**: a mis-formatted citation (delete the cited
string, insert the tool's exact `citation`), an altered quote (delete the altered words,
insert the verbatim language). Every tracked change gets a companion comment explaining the
basis. Judgment items (won't-resolve, weak support, negative treatment, unverifiable
quote) are **comment-only** — never "fix" what a tool didn't establish.
- **Never silently change the user's text.** Every alteration is a visible tracked change the
attorney can accept or reject.

## Comment format — short, scannable, no fat

Comments are read in a narrow margin pane. Three lines is the target; five is the ceiling.

- **Line 1: the status and the finding**, in plain words. **Then at most 1–3 short
  sentences** of basis — only what the attorney needs to decide. Cut tool narration ("two
  keyword searches found…"), case summaries, and Bluebook commentary.
- **The link goes on its own line at the end.** One link; the verified Midpage URL.
- **Don't restate what the redline already shows.** If the tracked change displays the
  correction, the comment states the status and the basis — not a prose description of the
  edit.
- **Don't fix the brief in the margins.** Substitute authority only if it was verified this
  session, and name it in one line — no editorializing.

> **Too long:** "Fix — the case does not appear to stand for the proposition cited.
> Midpage's analysis of 503 B.R. 571 lists this point among matters the opinion does not
> address, and two keyword searches found no passage applying the preliminary-injunction
> standard with 'particular emphasis' on preventing dissipation…; the only 'dissipation'
> passage quotes the movants' own TRO motion in a footnote. Soundview concerns the automatic
> stay's immediate and extraterritorial effect… Verify the cited pages or substitute
> supported authority — e.g., verified this session: In re Netia Holdings…"
>
> **Right:** "Fix — proposition unsupported. Midpage lists this point as *not addressed*,
> and keyword searches found no matching language; 'dissipation' appears only in a footnote.
> https://app.midpage.ai/document/in-re-soundview-elite-ltd-8496643"

> **Too long:** "OK — case verified; quote verbatim except capitalization. Midpage confirms
> the sentence '…' 'courts' is lowercase mid-sentence in the original; the redline brackets
> the case change ('[C]ourts') per Bluebook R5.2. https://app.midpage.ai/…"
>
> **Right (the redline already shows the bracket fix):** "OK — case verified; quote verbatim
> except capitalization. Confirm against the case:
> https://app.midpage.ai/document/matter-of-m4-enterprises-inc-1912384"

> **WL/LEXIS cite:** "OK — Midpage cannot verify citations to other commercial databases, but
> found this case. The proposition appears supported but worth reviewing.
> https://app.midpage.ai/document/iovate-health-sciences-international-inc-11137541"

### 4. Report back in chat

A few sentences: how many citations were checked, the counts by status, the worst findings
first (unresolvable cites, `doesNotAddress` miscites, negative treatment, altered quotes),
and what could not be checked and why. Then hand over the `.docx`.

## Honesty rules (the point of the skill)

- **OK** only when a tool confirmed it this session. **Fix** only for a concrete tool-found
defect. Everything else — including any cite that won't resolve — is **Review**.
- **Exhaustive means accounted for.** Every citation in the inventory appears in the markup
with a status. If something couldn't be checked (tool failure, no docket, ambiguous cite),
its comment says so explicitly — a silent skip is a lie of omission.
- **Never fabricate or repair a citation from memory.** An unresolvable cite is a finding,
not a gap to fill.
- **Pin cites are out of scope — don't even attempt them.** Never mark a pin cite correct or
incorrect, never "correct" a page number; the cover page says so.
- Be explicit about what a tool confirmed versus what needs the attorney's judgment. This
skill flags; it does not bless.
