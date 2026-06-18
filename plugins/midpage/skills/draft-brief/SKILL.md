---
name: draft-brief
description: "Drafts court filings — motions, memoranda of law, appellate briefs — as court-ready .docx, with Midpage research behind every citation. Use to \"draft a motion to dismiss,\" \"write the brief.\""
metadata:
  version: 0.2.0
  author: midpage
---

# Draft Brief

Draft and format a court-ready filing and hand back the `.docx`. Briefs, motions, memoranda of
law, oppositions, replies, appellate briefs. **Complaints and other pleadings are out of
scope** — if asked to draft one, say so and stop. Read the shared guides first — they carry
the method this skill assumes: `references/litigation-writing.md` (how to write it),
`references/court-rules.md` (how to find the governing rules), `references/citations.md` (how
every cite links), and `references/legal-docx.md` (rendering). The research method is below —
it is the heart of this skill.

## Workflow

1. **Get up to speed.** Read any relevant uploads and consult the relevant record documents
   (`analyzeDocketReport` for posture and the operative filings, `analyzeDocketFiling` to read
   what they actually say). Every record fact you later assert carries a linked filing cite.
2. **Preliminary research.** Don't jump to conclusions about what to argue; research with
   Midpage to determine what the strongest arguments are and what makes procedural sense.
3. **Craft the research-based narrative structure.** Consult
   `references/litigation-writing.md`. Before doing even more research, settle on structure
   and arguments based on your preliminary research.
4. **MOST IMPORTANT: Exhaustive, iterative research per issue.** Make a research plan and
   follow it, using the method below. The goal is not to surface and analyze the obvious
   opinions only; you want to find the strongest, most favorable cases that will carry each
   argument the extra mile. Don't settle for any case supporting your proposition — find the
   favorable ones with devastating language, framings, facts, and the right outcomes. Each
   argument needs to be dense with case-law citations and compelling analysis. Find the cases
   and arguments that HURT and confront them head on — distinguish them or argue they are not
   determinative.
5. **Get the governing rules** per `references/court-rules.md`: case orders → judge's
   individual practices → local/ECF rules → federal baseline. Capture length limits,
   font/margins/spacing, required sections, caption form, certificates, TOC/TOA triggers —
   each linked to its source. Surface conflicts (the more specific layer controls; show both).
6. **Write it** per `references/litigation-writing.md`: theme stated up front, point headings
   that argue, rule synthesis not book reports, quotes woven into prose, adverse authority
   confronted head-on.
7. **Render** with the `brief` profile (`references/legal-docx.md`). Thread any rule-set
   spacing/font/margin through `D.builders("brief", { lineSpacing })`; defaults stand when
   rules are silent. Validate the rendered file against the verifiable requirements (length,
   font, margins, spacing, required sections, certificates).

## Research with Midpage (the method)

All law comes from the Midpage tools this session. `search` finds candidates; `findInOpinion`
previews; **`analyzeOpinion` is what permits a citation** — no case is cited without it.

- **Frame before you search.** Pin the forum (court, circuit, state) — it controls what binds
  and how to filter. Reduce each question to the operative element actually in dispute ("does
  an eight-month delay defeat likely irreparable harm in the Ninth Circuit?" — not "can we get
  an injunction?"). Each distinct issue gets its own searches and its own section. For every
  issue, write down what the other side will argue — that defines half your research targets.
- **Search semantic, parallel, filtered.** Concept- and proposition-style queries, never
  boolean. One issue per query, up to four in parallel. Filter to the forum
  (`jurisdictionType`, `circuits`/`courts`/`states`, dates when recency matters); binding
  authority first, persuasive labeled as such. If you filter `publishStatus`, run a parallel
  `unknown` query too (for California, default to `published` plus `unknown`). Need exact
  wording? Stop guessing in `search` — run `findInOpinion` on a promising case.
- **Triage before you spend analysis.** `highlights` show why a case matched — previews only,
  never quote them. `treatment` gauges whether it's good law and how heavily relied on.
  `findInOpinion` is the free double-click before an `analyzeOpinion` call.
- **Branch from the best case.** When a strong case surfaces, mine it: `analyzeOpinion` it and
  pull the authorities the opinion itself leans on (the rule it states usually quotes the case
  you actually want); then search its key holding language as its own query to find later
  cases applying it. A case the court's own opinions repeatedly cite is worth more than three
  you found cold.
- **Iterate until it's scorched earth.** Re-query each issue with new framings — the best
  case's holding language, the opposing side's framing, narrower fact patterns, the remedy
  angle — until new queries keep returning the same leading cases. That saturation is the
  signal you've mapped the field; anything less is settling.
- **The `analyzeOpinion` gate, on every case you cite.** Pass a `question` naming the exact
  element. Check **`doesNotAddress` first** — if your point is listed, the case does not stand
  for it, however close the language looks. Build sentences from `supportedPropositions`
  (each carries a cite-ready proposition, a verified quote, and a `deeplinkURL`). Lead with
  `core_holding` over `supporting_analysis`; never sell `background` as the holding. Carry
  `scope` qualifiers into your sentence. A concurrence or dissent (`opinionSection`) is never
  presented as the court's holding. Surface negative `treatment` honestly — if you must use a
  caution/negative case, say so.
- **Research the other side as hard as your own.** For every issue, run searches framed from
  the opposing position; identify the case they will lead with and `analyzeOpinion` it too —
  that's what step 4's confrontation is built from.
- **Silence and splits are findings.** No controlling authority on point, or a genuine split,
  gets reported as such — never papered over with an off-point or out-of-jurisdiction cite.

## Scope discipline

- **Format, required sections, and limits are always in scope.** When a rule forces a change,
  name the rule and link the source.
- **Drafting substance** (argument, facts) is in scope when drafting from scratch or when
  asked.
- **Working from the user's existing draft: do not rewrite their arguments, reorder their
  theories, or change their voice** unless they ask or a rule requires it (get sign-off before
  cutting argument to meet a limit). Note substantive problems you spot as a brief, separate
  observation — never silently implement them.

## Hard rules

- Never recall a rule, holding, quote, or record fact from memory. Rules come from sources
  retrieved this session; case law from `analyzeOpinion`; record facts from
  `analyzeDocketFiling`. No invented case, quote, pin cite, statute, or rule, ever.
- Honor `doesNotAddress`, distinguish holdings from dicta and majority from
  concurrence/dissent, surface negative treatment.
- The attorney owns the filing. Flag open items and judgment calls plainly; never imply the
  document is filing-ready without their review.
- Brief-writing is research-led. Do thorough, iterative research with Midpage.
