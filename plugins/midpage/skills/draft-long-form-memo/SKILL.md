---
name: draft-long-form-memo
description: "Writes a formal objective legal research memo (Questions Presented, Brief Answers, Facts, IRAC Discussion, Conclusion) as a .docx. Use to \"draft a research memo on whether…\" Predicts, never advocates."
metadata:
  version: 0.2.0
  author: midpage
---

# Draft Long-Form Memo

Produce the thorough, objective memorandum a litigator hands a partner: it **predicts, it does
not advocate**. The test for every sentence: would you write it the same way no matter which
side retained you? Read the shared guides first — `references/litigation-writing.md` (the
craft; same point-first discipline, neutral verbs), `references/citations.md` (how every cite
links), and `references/legal-docx.md`. The research method is below — the memo is only as
good as the research under it.

## Research with Midpage (the method)

All law comes from the Midpage tools this session. `search` finds candidates; `findInOpinion`
previews; **`analyzeOpinion` is what permits a citation** — no case is cited without it.

- **Frame each Question Presented as the operative element actually in dispute**, pinned to
  the forum (it controls what binds and how to filter). Split multi-part questions; each issue
  gets its own searches, its own Brief Answer, its own Discussion section.
- **Search semantic, parallel, filtered.** Concept- and proposition-style queries, never
  boolean; one issue per query, up to four in parallel; filtered to the forum
  (`jurisdictionType`, `circuits`/`courts`/`states`, dates). Binding authority first,
  persuasive labeled as such. If you filter `publishStatus`, run a parallel `unknown` query
  too (California: default `published` plus `unknown`).
- **Triage** on `highlights` (previews only — never quote them) and `treatment`; use
  `findInOpinion` as the free double-click before spending an `analyzeOpinion` call.
- **Branch from the best case**: pull the authorities a strong opinion itself leans on, then
  search its key holding language to find later cases applying it. Iterate per issue until new
  queries keep returning the same leading cases — saturation means the field is mapped.
- **Research both sides with equal force — the memo's defining duty.** For every issue, run
  searches framed from each party's position and `analyzeOpinion` the strongest case on each
  side. The prediction is only honest if the contrary line got the same effort.
- **The `analyzeOpinion` gate, on every case cited.** Pass a `question` naming the exact
  element. Check `doesNotAddress` first — if your point is listed, the case doesn't stand for
  it. Build sentences from `supportedPropositions` (verified quote + `deeplinkURL`); rank by
  `centrality` (lead with holdings, never sell background as one); carry `scope` qualifiers;
  never present a concurrence/dissent (`opinionSection`) as the court's holding; surface
  negative `treatment` honestly.
- **Silence and splits are answers.** "No controlling authority on X in this circuit" is a
  finding worth reporting plainly; a genuine split is reported as one, with the best authority
  each way — never resolved by wishful citation.

## Structure

- **Caption block** — `MEMORANDUM`, then To / From / Date / Re: lines. **From is always
  "Midpage Legal Research"** — never an AI assistant's name. Front matter is single-spaced, no
  first-line indent (the body is double-spaced).
- **Question(s) Presented** — one neutral, answerable question per distinct issue, naming the
  forum and the operative element. Framed so the answer is genuinely in doubt, not loaded.
- **Brief Answer(s)** — one-to-one with the questions: lead with the prediction ("Probably
  yes," "Likely not," "Unsettled, but the better view is…") plus the one-line reason. Readable
  on their own.
- **Statement of Facts** — only if the user supplied facts; even-handed; record facts cited.
  Omit the section entirely otherwise.
- **Discussion** — the heart, IRAC per issue under `h1` headings: state the rule with linked
  controlling authority, apply it to the facts, then give the contrary or competing authority
  its fair statement — distinguish it, weigh it, note negative treatment honestly — and
  resolve with a predictive conclusion. Use predictive verbs ("a court would likely hold"),
  never advocacy verbs ("plaintiff plainly fails").
- **Conclusion** — pull the Brief Answers into a candid forecast across all issues, flagging
  open questions and the principal risk on each. No new authority; synthesize.

## Rendering

Per `references/legal-docx.md`, memo profile, double-spaced:

```js
const B = D.builders("memo", { lineSpacing: 480 });
// front matter lines: B.p([...], { lineSpacing: 240, firstLineIndent: 0 })
// Questions Presented: B.numbered(q, { instance: 1 })
// Brief Answers:       B.numbered(a, { instance: 2 })   // distinct instance → restarts at 1
```

Questions and Brief Answers are real numbered lists (hanging indents, wrapped lines aligned
under the text) — never a literal "1." plus a tab.

## Hard rules

- **Objective, not persuasive.** Present both sides fairly; predict. Advocacy is
  `draft-brief`'s job.
- **Tool-grounded only.** Never cite a case, quote, or pin cite not run through
  `analyzeOpinion` this session; `search`/`findInOpinion` alone are not enough. No invented
  authority, ever. Respect `doesNotAddress`, `scope`, `centrality`, and `opinionSection`;
  surface negative treatment.
- **Unsettled is an answer.** A genuine split or open question is reported as one, with the
  best authority each way — never resolved by wishful citation.
- Every proposition carries the exact linked citation per `references/citations.md`; short
  verbatim quotes woven into prose, no block quotes, no short cites.
