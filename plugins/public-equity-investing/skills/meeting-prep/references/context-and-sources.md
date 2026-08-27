# Context and sources

## Table of contents
1. Source hierarchy
2. Connected-source intake
3. Stale-data checks
4. Citation and source-log behavior
5. Conflict handling
6. Fact, assumption, and inference labels
7. No-context and partial-context fallback

## 1. Source hierarchy
Use the highest-quality source available for the specific claim.

### Public Equity Investing meeting logistics and intent
1. User instructions in the current prompt.
2. Current calendar invite, agenda, attachments, attendee list, meeting title, and location/video link.
3. Recent email or chat threads discussing the meeting.
4. Research, project, thesis, or action tracker status.
5. Prior meeting notes or transcripts.
6. Inference from context, labeled as an assumption.

### Company, issuer, or investment facts
1. User-provided source documents and active artifacts.
2. Primary source materials: company financials, management presentations, filings, press releases, earnings releases, transcripts, investor presentations, court/regulatory records, and Credit Markets documents.
3. Connected financial or market data apps available to the user.
4. Internal research, prior memos, prior models, research notes, committee materials, and evidence trackers.
5. Reputable public sources and web search.
6. Model output, third-party summaries, or management claims, labeled and cross-checked.

### People and relationship context
1. Calendar attendee list and invite metadata.
2. Recent emails, chat messages, prior meeting transcripts, research notes, and relationship notes.
3. User-provided background.
4. Public professional profiles or company bios if connected context is unavailable and web use is allowed.

## 2. Connected-source intake
Treat connectors as optional runtime inputs, not guaranteed dependencies. When connectors are enabled and available to the user, gather only what materially improves the prep. Useful connector categories include:
- calendar: timing, attendees, agenda, recurrence, attachments, urgency;
- email and chat: objectives, open issues, relationship tone, prior commitments, last-mile updates;
- drive/docs/slides/sheets: pre-reads, models, decks, memos, evidence trackers, templates;
- transcripts/meeting records: prior questions, commitments, unresolved issues, tone;
- research/project trackers: stage, owners, next milestones, issuer/investor/counterparty status;
- finance/data apps: filings, earnings, consensus, market data, portfolio/risk reports, credit documents, and internal source exports.

Do not claim access to files, calendars, chats, emails, or market-data feeds unless the connector is actually enabled and callable. Do not ask for files or dates that are clearly available in the connected context. If connectors are unavailable or insufficient, say what was missing and proceed with a fallback brief based on user-provided materials, public sources, and clearly labeled assumptions.

## 3. Stale-data checks
Flag data as potentially stale when:
- meeting logistics differ across invite, email, and user prompt;
- financials predate a newer filing, earnings release, forecast, guidance update, investor day, rating action, or credit document;
- market data, share price, spreads, yields, FX, or commodity prices are not current for a market-sensitive meeting;
- consensus, guidance, KPI, or estimate data predates the latest print, guide, investor day, or major announcement;
- catalyst status, event timeline, research action trackers, or evidence requests are older than the latest source communication;
- prior notes are contradicted by newer source documents.

Use concrete language: "potentially stale," "superseded by," "verify before meeting," or "latest available source reviewed."

## 4. Citation and source-log behavior
Cite facts that anchor the prep: financials, security terms, dates, deadlines, guidance, catalyst status, meeting objective, prior commitments, and evidence responses. Generic questions and judgment do not need citations, but should be traceable to the relevant issue.

If the environment supports inline citations, cite factual claims inline. If not, include a source log with fields:
- claim or fact,
- source name,
- source type,
- date or version,
- confidence,
- notes or conflicts.

For external-clean outputs, include citations or source descriptions that are appropriate to share. Keep internal emails, chat threads, and privileged strategy notes out of external-facing source logs unless the user explicitly asks and sharing is appropriate.

## 5. Conflict handling
When sources conflict:
1. identify the conflict plainly;
2. prefer current primary sources over summaries;
3. prefer signed/final/current documents over drafts;
4. prefer direct company or system data over manual notes;
5. preserve the lower-confidence item as a question or verification item;
6. do not silently blend conflicting figures.

Example phrasing:
- "Revenue is shown as $120m in the latest company deck but $116m in the older model. I used $120m for the brief and added a pre-call tie-out item."
- "The calendar invite says this is an issuer update, while the email thread frames it as a liquidity review. Treating liquidity as the likely decision point; verify at the start."

## 6. Fact, assumption, and inference labels
Use these labels consistently:
- **Verified fact**: supported by a cited source.
- **Management claim**: stated by company/issuer/management but not independently verified.
- **Model output**: calculated from a workbook or assumptions; cite model tab/range or describe source.
- **Assumption**: needed to proceed but not verified.
- **Inference**: reasonable conclusion from facts but not directly stated.
- **Question**: open issue to resolve in the meeting.
- **Recommendation**: suggested stance or action.

## 7. No-context and partial-context fallback
If no reliable source is available, still help. Produce:
- a starter objective based on the user's wording,
- a likely meeting-type assumption,
- a short list of missing context that would most improve the brief,
- a generic but senior question set for that meeting type,
- a source log that says "no source provided" rather than inventing provenance.

Do not block completion unless a missing fact is essential to safety, confidentiality, legal compliance, or the user's explicit deliverable.
