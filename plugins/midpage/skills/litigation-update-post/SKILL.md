---
name: litigation-update-post
description: "Writes public-facing litigation updates — blog posts, client alerts, LinkedIn/X posts — on a federal case or legal development. Use to \"write a blog post about…,\" \"draft a client alert on…\""
metadata:
  version: 0.2.0
  author: midpage
---

# Litigation Update Post

Write the forward-looking, firm-bylined piece a top firm publishes to stay top-of-mind:
what's happening, what's at stake, how the law sees it, what's next — accessible to a
sophisticated lay reader, credible to a lawyer, grounded entirely in public, linkable sources.
Two formats, same research rigor: a **blog post / client alert** (the full piece) or a
**social post** (LinkedIn or similar — the condensed version). Read the shared guides first:
`references/litigation-writing.md` (the register: explains, never breathless),
`references/citations.md` (how every filing, case, and source links), and
`references/court-rules.md` (the procedural-timing layer behind "what's next"). The legal
analysis is researched with Midpage — the method is in step 6.

## Method

1. **Scope the subject and pick the format.** Case mode (pin the court, docket number, and
   the forward-looking hook — a fully-briefed motion, a scheduled argument, an appeal under
   submission) or topic mode (pin the development, jurisdiction, and why it's timely — an
   effective date, a pending appeal that could resolve a split). Format: blog/client alert
   unless the user asked for a social post (or both — they share the research). Asked to
   "come up with" a post? Web-research 2–3 timely angles and confirm one before going deep.
   No live hook on the chosen case? Say so and offer to pivot.
2. **Web-research the hook and primary sources.** Prefer primary (`.gov`, the court, the rule
   text, the opinion) and established legal press over aggregators; capture canonical URLs.
   **Web research sets the scene — it never verifies law.** Every holding still comes from
   `analyzeOpinion`; every docket fact from `analyzeDocketFiling`.
3. **Pull the docket(s) and read the key filings.** `analyzeDocketReport` for posture,
   parties, briefing history, judge; `analyzeDocketFiling` on the operative documents — you'll
   quote and link them. Don't characterize a filing you didn't read.
4. **Pin posture and realistic timing.** "Fully briefed as of [date]; argument [date] / none
   set." Courts rule when they rule: never invent a decision date. Frame timing as commentary
   ("a ruling could come any time; motions like this in this district often take months") and
   state only dates an authority actually set, linked.
5. **One skippable check-in.** Give a two-line read of what you found, then ask whether the
   user wants to steer focus (which issue/angle), structure (their template, a Q&A), or
   analysis (a split, this judge's track record, sector impact). Defaults are fine — if they
   shrug, proceed: center the issue most likely to drive the development, use the anatomy
   below, balanced read of the authority. Don't block on a non-answer.
6. **Research the legal question with Midpage**, scoped to the chosen focus (default: the one
   or two questions the case or development turns on). All law comes from the tools this
   session — `search` finds candidates, `findInOpinion` previews, and **`analyzeOpinion` is
   what permits a citation**. Frame each question as the operative element in dispute, pinned
   to the forum; search with semantic concept-style queries (never boolean), one issue per
   query, up to four in parallel, filtered to the jurisdiction; triage on `highlights`
   (previews only — never quote them) and `treatment`; run searches framed from **both
   sides** and `analyzeOpinion` the strongest case each side leans on. Check `doesNotAddress`
   before citing a case for a point; build statements from `supportedPropositions` (verified
   quote + `deeplinkURL`); never present a concurrence/dissent as the holding; surface
   negative treatment. Capture how courts have come out and any split or trend. Balanced and
   explanatory — informed commentary, not advocacy, not a prediction dressed as fact.
   A social post gets the same verification — shorter output never means weaker grounding.
7. **Write it in the chosen format** (anatomies below). Short paragraphs, plain English,
   terms of art defined inline, one or two linked authorities per point — no string cites.
8. **Deliver.** Publishable markdown by default — ready to paste into the CMS or the
   platform: headline/body/links/disclaimer for a blog; the post text (with link placement
   noted) for a social post. Offer a Word draft via `references/legal-docx.md` only if
   wanted.

## The two formats

**Blog post / client alert (500–900 words).** A specific, forward-looking **headline** (name
the stakes, not just the case) · a one-paragraph **hook** · **what's happening** in lay
terms, each claim linked to its filing or primary source · **what's at stake** beyond these
parties · **what the law says** — the governing rule and key authority with short woven
quotes and links, both sides' best case · **what's next** — posture and honest timing · a
one-paragraph **takeaway** · disclaimer and byline placeholders.

**Social post (LinkedIn or similar, ~100–300 words).** The condensed cut of the same
research: a first line that earns the scroll-stop (the stake or the development, concrete,
no clickbait) · 2–4 tight paragraphs or a short list — what happened, why it matters, what
to watch · a link to the primary source (the opinion, the rule, the docket) and at most one
authority · the short disclaimer line. Professional firm voice — no hashtag spam (0–3
relevant ones at most), no emojis, no engagement bait, no breathless "BIG news." Where the
platform doesn't render inline links well, put the link(s) at the end.

## Disclaimer and bylines (always)

Close every blog/alert with this, verbatim or lightly adapted:

> *This post is for general informational purposes only and is not legal advice. It is based
> solely on public court filings and published decisions and does not reflect any non-public
> information. Reading it does not create an attorney–client relationship. This may constitute
> attorney advertising.*

A social post carries the condensed form, never omitted: *Not legal advice. Based solely on
public filings and published decisions. May constitute attorney advertising.*

Bylines are placeholders — `By [Author], [Firm] — [Date]` — never invented.

## Hard rules

- **Public, linkable sources only**, read this session: the public docket, published
  authority, reputable public web sources. Never privileged strategy, inside information, or
  anything a party hasn't put on the public record — if you happen to know more, it does not
  go in.
- **Link everything**: filings per `references/citations.md` (`ECF No.` + Midpage URL), cases
  with the exact citation `analyzeOpinion` returned, every factual claim to its primary source.
- **Honest about timing and outcome**: no manufactured decision dates, no result predicted as
  if known.
- **Not legal advice**: the disclaimer (full or condensed per format) is never omitted, and
  the post never addresses a specific reader's situation.
