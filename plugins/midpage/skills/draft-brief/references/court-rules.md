# Court rules — finding what actually governs a filing

How to find the rules that govern a specific filing in a specific case before a specific
judge. Several layers apply at once; the operational rule is **specific beats general**, and
the non-negotiable is **never recall a rule from memory** — local rules and judge practices
change, vary by district and division, and training data is exactly the wrong source. Every
requirement comes from a source retrieved this session, with its effective date confirmed and
a working link, presented per the citations guide.

## The four layers, most to least controlling

1. **Case-specific orders on this docket** — scheduling orders, briefing orders, one-off
   orders. If the scheduling order caps the opposition at 15 pages, that controls over the
   local rule's 25. Find them with `analyzeDocketReport` (ask a targeted question — "is there
   a scheduling or briefing order setting page limits?"; it returns `case.caseId` and
   `relevantEntries[].filingId`), then read the order's actual text with `analyzeDocketFiling`.
   A description is not the order. When `doesNotAddress` shows the docket is silent on a
   point, say so and fall back to the next layer — don't imply the docket resolved it.
2. **The assigned judge's individual practices / standing orders** — the layer most often
   missed and most likely to change the answer: altered page/word limits, pre-motion letter or
   conference requirements, courtesy-copy rules, font/spacing specs, footnote and proposed-
   order rules. Find them on the court's site under the judge's page ("Individual Practices,"
   "Standing Orders," "Chambers Rules"). Match the right set — **civil vs. criminal**, and the
   **referred magistrate's** rules if a magistrate is handling the motion. A newer standing
   order on the docket beats a stale web posting.
3. **The district's Local Rules plus the ECF/CM-ECF procedures** — on the court's official
   `*.uscourts.gov` site (e.g. `nysd.uscourts.gov`). Web-search the court, then fetch the
   **official page** — never a third-party reprint. Confirm the effective/amended date. Don't
   overlook the ECF administrative procedures: accepted formats (text-searchable PDF,
   sometimes PDF/A), per-file size limits and splitting, exhibit attachment and labeling,
   `/s/ Name` signatures, proposed-order submission, FRCP 5.2 redaction.
4. **The Federal Rules** (FRCP, FRCrP, FRAP, FRBP) — the national baseline the layers above
   usually displace. Stable, but confirm specifics against official text when they drive the
   answer; link the official rule or Cornell LII when no official link exists.

When two layers conflict, follow the more specific one — and **surface both**, noting the
override, so the reader sees that the specific source displaces the default. When a genuine
conflict is unclear, say so rather than silently picking.

## Where to look, by court

- **District courts:** `[abbrev].uscourts.gov` → "Local Rules"; judge pages for individual
  practices. Search: `S.D.N.Y. local civil rules`, `[judge] individual rules [district]`.
- **Courts of appeals:** `ca[N].uscourts.gov`; FRAP 32 is the form/length baseline
  (type-volume limits, certificate of compliance, 14-pt proportional font) but circuit local
  rules vary — cover colors, disclosures, section order are circuit-specific.
- **State courts:** search `[state] [court] local rules` / `rules of civil procedure` on the
  judiciary's own site; county, departmental, and individual-judge layers may stack. The
  Midpage docket tools are federal — for state matters the case-specific-orders layer may be
  unavailable; say so and lower confidence accordingly.
- **Specialized:** bankruptcy (district bankruptcy local rules + FRBP), Tax Court
  (`ustaxcourt.gov`), Court of Federal Claims, agency tribunals — same method.

## Fallback defaults (only when a real search comes up empty)

US Letter, 1″ margins, Times New Roman 12 pt, double-spaced body, single-spaced indented
block quotes and footnotes, page numbers per local practice. Flag any default plainly as a
fallback — "no court-specific rule found; using the conventional federal default" — never as
a confirmed requirement.

## Traps

- **Division-specific standing orders** in large districts — match the division.
- **Wrong civil/criminal set** of individual rules — silently wrong answers; match case type.
- **Stale postings** — a docketed order outranks the judge's web page.
- **Page vs. word limits** are different regimes; confirm which, and what's excluded from the
  count (caption, TOC/TOA, signature block, certificates, sometimes footnotes).
- **Third-party reprints** (commercial outlines, law-firm summaries, even Cornell for local
  rules) are leads to verify, never sources to cite.

## What a rules lookup produces

For each requirement: the requirement stated plainly, its layer, the exact citation ("Local
Civil Rule 7.1(c)"), a working link to the source actually retrieved, and whether it is
objectively verifiable (word count, font, margins, a required certificate) or needs the
attorney's judgment. Honest gaps included: "the docket and the judge's rules are silent on X;
the local-rule default applies" is a result. An unsourced requirement is worse than none.
