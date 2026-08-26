# Safety and integrations

## Table of contents
1. Non-destructive artifact rules
2. Internal versus external outputs
3. Sensitive finance and compliance topics
4. Integration with other skills
5. Editing and export guidance
6. Final quality checks

## 1. Non-destructive artifact rules
Default to preserving source artifacts.

Do:
- create a new meeting brief, notes section, slide, tab, tracker, or memo section;
- append comments or speaker notes instead of replacing content;
- create a copy before broad rewrites;
- provide a change log for edits;
- preserve formulas, source links, hidden tabs, comments, footnotes, and existing citations.

Do not:
- delete source data, notes, formulas, slides, sections, citations, or trackers unless explicitly asked;
- overwrite a live model, deck, memo, research tracker, or action tracker without confirmation;
- hide uncertainty by rewriting assumptions as facts;
- modify numbers for style or simplicity;
- remove inconvenient risks, caveats, or open questions from senior-facing prep.

## 2. Internal versus external outputs
Choose a circulation mode.

### Internal strategy mode
Use for internal research team, investment team, PM, risk committee, credit committee, or client-prep work. It may include candid views, concerns, pushback strategy, valuation sensitivity, evidence gaps, risk limits, and what not to share.

### External-clean mode
Use for client, counterparty, management, issuer, investor, expert, or advisor-facing materials. Remove internal strategy, valuation bottoms, trading intent, position sizing, restricted-list issues, privileged mental impressions, sensitive internal messages, and anything not appropriate to circulate.

### Review mode
Use when the user provides a draft. Flag where the draft mixes internal and external content, creates record risk, overstates facts, lacks evidence, or buries a key decision.

## 3. Sensitive finance and compliance topics
Flag and handle carefully:
- material non-public information, selective disclosure, or trading restrictions;
- insider lists, wall-crossing, restricted lists, or confidential process information;
- expert-call topics that could solicit prohibited information;
- antitrust, competition, sanctions, export controls, tax, accounting, audit, employment, privacy, healthcare, insurance, bank regulatory, or legal issues needing specialist review;
- personal data, customer-level data, patient data, or employee data;
- trading intent, internal thesis, position sizing, hedge strategy, or restricted-list issues that should not be written externally.

When in doubt, preserve the issue as an escalation item and draft clean questions that seek observable, non-restricted facts.

## 4. Integration with other skills
Use the relevant companion skill rather than duplicating deep analysis:
- `financial-source-of-truth`: source hierarchy, stale-data checks, citations, and fact/assumption labeling.
- `company-tearsheet`: baseline public company, issuer, listed fund/manager, peer, or counterparty overview.
- `style-guide-adapter`: firm/client tone, precedent format, and clean presentation style.
- `memo-builder`: decision memo or committee memo based on prep.
- `deck-report-qc`: presentation materials and pre-read review.
- `model-audit-tieout`: model integrity, formulas, hardcodes, and source tie-outs.
- `scenario-sensitivity-generator`: downside, upside, breakeven, and stress-test questions.
- Public Equity Investing vertical skills: use earnings, model update, valuation, event-driven equity, thesis-tracking, risk/sizing, hedge, macro-impact, or `sector-context-overlay` when the meeting is part of those workflows.

## 5. Editing and export guidance
When the user wants an artifact:
- For a doc or memo: create a new document or section; preserve citations and source log.
- For slides: create meeting-ready talking points, speaker notes, or appendix pages; do not distort template style.
- For spreadsheets: add a new "Meeting Prep" or "Action Tracker" tab; do not change calculations unless explicitly asked.
- For email/chat: draft the message and wait for user review unless the environment explicitly allows sending and the user instructs it.
- For research/thesis/action trackers: propose updates or create an importable tracker; avoid writing directly to production records unless explicitly asked.

## 6. Final quality checks
Before finalizing, confirm:
- the output is usable five minutes before the meeting;
- top three questions are not generic;
- open asks are tied to a decision;
- facts are sourced and assumptions are labeled;
- no internal-only content appears in an external-clean output;
- no source artifact was overwritten;
- follow-ups have owner and due date when available;
- missing sources are stated rather than hidden.
