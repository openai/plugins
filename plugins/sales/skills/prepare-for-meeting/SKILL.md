---
name: prepare-for-meeting
description: "Use when the user wants to prepare for one or more upcoming seller meetings with customers, prospects, partners, accounts, or important stakeholders; gives a bare request such as Meeting prep or prep my meetings; requests daily or date-based seller meeting preparation; asks to organize a same-day customer call queue; asks for the most important qualifying meeting of the day; identifies seller meetings only by company, attendee, topic, or date; or wants a customer-facing presentation or deck for a first call, EBC, executive workshop, or upcoming customer meeting. Produce an individual meeting brief, chronological multi-meeting agenda, or deliberate customer presentation as appropriate. Exclude neutral product-discovery interviews and user-research discussion guides without seller, account, opportunity, or commercial intent."
---

# Prepare for Meeting


## Context-Gathering Intake

Whenever this skill needs a material clarification, follow the shared [User Input](../../shared_skill_instructions.md#user-input) guidance.

Prepare a sales person for a critical customer or internal meeting, with all relevant context needed to help them reach the stated or assumed goal of the meeting.

## Common Skill Instructions

MANDATORY: If they are not already in context, read and follow [the shared Sales skill instructions](../../shared_skill_instructions.md).

## Meeting Ranking

Use this priority order for selecting meetings if the specific meeting is ambiguous.

1. Explicit user request, named meeting, named account, named topic, or stated preference
2. Meetings the user owns, leads, presents in, or is expected to drive
3. Customer, prospect, partner, renewal, opportunity, or strategic account meetings
4. Large or cross-stakeholder internal meetings with decisions, dependencies, launches, escalations, or leadership visibility
5. Meetings with buyer, executive, technical decision-maker, or senior stakeholder attendance
6. Meetings with explicit decisions, blockers, risks, commitments, or time-sensitive next steps
7. Meetings where prep is likely to materially improve the user’s next action

Routine internal syncs, 1:1s, recruiting meetings, and performance discussions are lower priority, but may still qualify when explicitly requested, user-owned, or clearly high-stakes.

## Key Dependency Categories

These are particularly important for this workflow; use your best judgment to potentially include other data sources to improve quality.

- [Blocking] ~~Calendar for meeting identity, invite context, agenda, and attendees. It blocks only when the meeting must be discovered or selected.
- ~~Meeting Transcripts for prior decisions, objections, commitments, and continuity
- ~~Email for prior meeting notes, recent questions, and customer-facing context
- ~~Internal Messaging for internal strategy, blockers, owners, and dependencies
- ~~Knowledge & Files for prior meeting notes, strategy docs, and assets
- ~~CRM for account, opportunity, renewal, and contact truth
- ~~Sales Intelligence only when it materially improves preparation

Avoid unsupported claims. If context is missing, stale, or conflicting, state the limitation.

## Workflow Guidance

These meeting-specific steps modify and override the shared [Default Workflow](../../shared_skill_instructions.md#default-workflow).

- 1. Resolve Dependencies and Clarify
    - HARD STOP: For a genuinely bare request such as “Meeting prep” or “prep my meetings,” first ask: “Should I run this as: Prep for an upcoming meeting, Overview of today's meetings, or Overview of tomorrow's meetings?” Do not ask which event to prepare, call any connector, inspect earlier meetings, research an account, or draft until the user selects a mode. Never infer the target from earlier calls.
    - “My next customer meeting,” “my upcoming customer call,” a named meeting, an explicit date, and a supplied invitation already select upcoming-meeting mode. Do not ask the generic mode question. If meeting identity must be discovered and Calendar is unavailable, resolve its blocking dependency before any meeting-choice question: use the native install surface for the user-named or genuinely available provider. If installation is unavailable or declined, immediately follow [User Input](../../shared_skill_instructions.md#user-input): when `request_user_input` is available, offer two or three likely ways to identify the meeting, such as pasting the invitation, giving the customer/account, or naming an attendee; otherwise ask once in chat. Continue from the selected or supplied context and never repeat a declined installation offer.
    - When the user supplies an exact Calendar event ID or link, read that event directly; do not run a broad event search. If the direct read is unavailable, continue from the supplied invitation when sufficient and retain the unverified provenance label below.
    - PROVENANCE HARD REQUIREMENT: When the user supplied the meeting identity and no Calendar event was directly read, the final `**Meeting source:**` must begin with the exact words `User-supplied meeting identity; not Calendar-verified`. A matching email invitation only corroborates that user-supplied identity; cite it after the required label, never instead of it. When the Calendar event was directly read, cite it beside the date and omit the separate source line.
    - When the user asks for their next meeting and Calendar returns exactly one qualifying future customer event, select it directly and read the invite; do not ask the user to reconfirm an already unambiguous request. Ask the user to choose only when multiple credible candidates remain, the user supplied a conflicting candidate, or the selection would materially change the result.
    - When the user supplies an effective or as-of time, treat it as the strict evidence cutoff for email, messages, documents, and transcripts. Apply an instant-precise provider-side cutoff before fetching message bodies; for Gmail, use `before:<Unix epoch seconds>`, not a date-only `before:<date>`. Skip sources whose timestamps cannot be safely bounded.
    - Apply the same effective-time cutoff to CRM records before reading their contents: constrain Salesforce SOQL with `CreatedDate <= <as-of instant>` and `LastModifiedDate <= <as-of instant>`, or use a verified historical snapshot. If the exposed CRM action cannot apply the cutoff or no historical row remains, skip current CRM data and disclose the gap instead of consuming a record modified after the request time.
    - A future calendar invitation may identify the target meeting, but its recording, transcript, generated notes, summaries, and other artifacts created after the effective time are unavailable. Use earlier meetings or messages only when they predate that cutoff.
    - If another request leaves the mode unclear, ask the user via [User Input](../../shared_skill_instructions.md#user-input) rather than assuming upcoming-meeting prep.
    - If intent is "prep for an upcoming meeting" and the user did not supply a meeting, account, attendee, topic, or date, search and rank up to three candidates. Select a sole qualifying future meeting directly; use [User Input](../../shared_skill_instructions.md#user-input) only when multiple credible candidates remain. Do not retrieve deeper context or draft a brief until the target is unambiguous. All suggested events must be in the future relative to the user's current time.
        - This search should just be for the next 3 business days, with 25 max results, and no broad free-text query unless the user supplied an account, attendee, topic, or keyword
    - Resolve the account or workstream from the user request, invite, attendees, attendee domains, and nearby context. If CRM has multiple opportunities, use the one that matches the meeting topic, attendees, product, and recent activity; do not let an unrelated same-account opportunity drive the brief. If no credible anchor exists, state the gap instead of inventing one.
    - After the first draft, offer the most relevant follow-up from the Next Step Options below.

### Requested Meeting Documents And Decks

- For an explicitly requested customer-meeting deck, this selected meeting-preparation skill remains the seller-workflow owner. Read and follow [Sales Presentations](../sales-presentations/SKILL.md) as the downstream presentation partner before a substantive final response, gathering evidence, or invoking an artifact-authoring skill.
- When the user explicitly requests a meeting-prep document or deck, that artifact is the first deliverable, not a later optional next step. Apply this focused meeting-prep workflow before the matching document or presentation authoring skill.
- Directly inspect a supplied existing document, presentation, or template and preserve its actual sections, slide layouts, brand system, and placeholders; update that file only when requested, otherwise create a separate artifact without altering the original.
- Carry the verified meeting goal, attendees, account context, agenda, open questions, risks, decisions, next steps, and source links into the requested artifact. Verify substantive content by reading back the finished document or deck, then return its actual link; never substitute an unverified or invented file.

### Next Step Options

Use these as high-value transitions. Offer one clear transition, not a menu. Suggest ONLY these unless you are very confident another option is more useful:
- Install new connectors if they could materially improve output quality
- Improve or refine the brief based on the user's guidance.
- Add the prep to an existing meeting note or create a new meeting document as a pre-read. If needed and possible, offer to attach the document to the calendar invite. Be mindful of the broader audience when creating this prep doc; don't add your draft verbatim.
- Draft a concise Slack or email update for attendees, owners, or internal stakeholders.
- For a confirmed external meeting, turn the reviewed brief into a 6–9 slide customer presentation using `@presentations`.
- For `Daily Prep Digest` outputs, check whether a matching daily automation already reruns this `prepare-for-meeting` skill in that mode; if none exists, offer to create one that gives the seller a morning view of today's customer meetings, watchouts, and suggested closes.
- Set a heartbeat automation to follow-up with summary and action items after the meeting.

Next steps to avoid:
- Talk tracks or facilitation scripts

### Mandatory Deck Offer

- For a successful `Single Meeting Prep` output about an external customer, prospect, partner, renewal, or opportunity meeting, end with this exact final line: `Would you like me to turn this into a 6–9 slide customer presentation using @presentations?`
- For a successful `Daily Prep Digest` containing at least one qualifying external meeting, end with this exact final line: `Would you like me to turn one of these meeting briefs into a 6–9 slide customer presentation using @presentations?`
- This is the single required transition for qualifying outputs; do not append a competing automation or document offer.
- Skip the offer when the user already requested or received the deck, explicitly declined it, no external meeting qualifies, or the workflow is blocked.

### Automation Offer Guard

For `Daily Prep Digest` outputs where the mandatory deck offer does not apply, a daily meeting-prep brief is the preferred automation offer when the user benefits from starting each day with a seller-ready view of customer, prospect, partner, renewal, opportunity, or high-stakes internal meetings. Frame the value in sales language: knowing which meetings matter today, what account or deal context changed, where the watchouts are, and how to close each meeting toward a concrete next step.

The automation must be a scheduled rerun of this skill, not a separate custom calendar summary. When creating or describing the automation, make the prompt call this skill directly and preserve the same digest shape:

```text
Use the Sales `prepare-for-meeting` skill in `Daily Prep Digest` mode.
Rerun it daily for today's qualifying seller meetings in the user's timezone.
Return the standard Daily Prep Digest output with chronological meeting briefs and priority watchouts.

mode: "Daily Prep Digest"
date: "today"
meeting_scope: "customer, prospect, partner, renewal, opportunity, or high-stakes internal meetings"
```

The recurring output should follow this skill's `Daily Prep Digest` format: today's meetings, each meeting's goal, key context, watchout, suggested close, and cross-meeting priority watchouts. Keep it read-only; it may recommend preparation and follow-up actions, but must not create meeting notes, attach documents, send messages, post updates, or write CRM unless the user separately asks and approves.

Before offering the daily prep brief, check whether the user already has a matching local automation installed. Inspect local automation records under `$CODEX_HOME/automations/*/automation.toml`, or `~/.codex/automations/*/automation.toml` when `CODEX_HOME` is unset, and match by name, prompt, skill name, mode, cadence, meeting scope, or other stable scope details. Treat active and paused matches as already installed.

- If a matching automation exists, do not suggest creating another one. Continue with the next most relevant non-automation follow-up.
- If no matching automation exists and the mandatory deck offer does not apply, end with one clear offer to check/create a daily rerun of `prepare-for-meeting` for the Daily Prep Digest. Describe the recurring output as a morning seller brief for the meetings that need attention, why each matters commercially, and the recommended close or next step. Do not create or update the automation until the user explicitly agrees.
- If the automation surface is unavailable, do not mention tool details; offer to help set up a recurring meeting-prep brief when automations are available.

## Overall Rules
- When a material clarification has two or three highly likely answers, follow [User Input](../../shared_skill_instructions.md#user-input).
- Always cite sources using hyperlinks so users can click through to source docs
- Identify whether each material fact was user-supplied or directly retrieved. Claim that a source was checked, returned no results, or supports a specific link only when a completed source action in this conversation establishes that exact claim; tool discovery, an attempted call, and nearby unrelated results are not evidence.

## Modes
### 1. Single Meeting Prep

- Use when the user names one meeting, account, attendee, invite, or topic.
- You can pull in relevant information from other related meeting and context, but ensure that you make the link to the target meeting clear.
- Preserve Summary, Goal, Open questions, a duration-appropriate Proposed agenda, Recommended posture, and Confidence and gaps even in an executive-concise brief. When the supplied invitation is the only evidence, keep these sections brief and identify missing account history or CRM context without installing or querying an unnecessary provider.
- Keep the opening compact: meeting title, date/time, and sourced attendees. Include `**Meeting source:** User-supplied meeting identity; not Calendar-verified` only when no Calendar event was directly read. Keep that label even when a later email or message corroborates the invitation; corroboration does not replace user-supplied provenance or count as direct Calendar verification. Mention a material decline naturally in the attendee line; do not add separate Format, Accepted, or Declined fields.
- For a demo or walkthrough, include Recommended walkthrough spine: one customer-specific storyline in a Markdown blockquote, followed by a few sourced proof points explaining why it matters. Omit this section for other meetings. Include People to lean on only when evidence supports the named attendees' roles or contributions; do not infer roles from attendance alone. Weave useful background into these sections and the Summary rather than adding a generic Background Context section.
- Use sentence-case headings and a readable numbered agenda. Adapt the heading, timing, and stage count to the actual invite; for a 30-minute meeting, prefer about five well-spaced stages with a bold time range and outcome, then a compact explanation on the following line. Tailor the stages to the meeting, not necessarily a demo. If the duration is unknown, label any suggested duration as a proposal.

#### Output Format

```md
# [Meeting name]

**Date:** [Date/time, with a link to the directly read Calendar event when available]
**Attendees:** [Compact sourced names/roles; mention a material decline naturally]

## Summary

- [Core meeting objective]
- [Current account, opportunity, or workstream signal]
- [Top implication, risk, or source gap]

## Goal

- [Concrete decision, alignment, feedback, commitment, or next step]

## Recommended walkthrough spine

> [One customer-specific storyline connecting the demonstrated workflow to the outcome the customer needs.]

- [Sourced customer priority or workstream signal that makes this story relevant]
- [Sourced proof point, constraint, or prior commitment the walkthrough should address]

## Open questions

- [Most important unresolved question]
- [Question tied to invite, CRM, notes, or message context]
- [Decision or clarification needed]

## Proposed 30-minute agenda

1. **0–3 min — Define the outcome**
   [Confirm the customer decision or result this meeting should enable.]

2. **3–8 min — Align on the starting point**
   [Check the relevant customer context, constraints, and success criteria.]

3. **8–18 min — Work through the core scenario**
   [Use the customer-specific storyline or main decision topic.]

4. **18–25 min — Resolve open questions**
   [Test the risks, objections, or tradeoffs that could change the decision.]

5. **25–30 min — Agree on the next step**
   [Confirm the decision, owner, and next commitment.]

## People to lean on

- **[Person]:** [Sourced role/contribution and a concrete question or ask]

## Recommended posture

[Decision-oriented commercial stance; distinguish recommendations from customer commitments.]

## Confidence and gaps

[Source-quality limits, conflicting or missing evidence, and what would materially improve confidence. Follow [Limitations and Improvements](../../shared_skill_instructions.md#limitations-and-improvements) here without adding a duplicate section.]

{Follow the instructions and output format/conditions in [Next Steps](../../shared_skill_instructions.md#4-offer-one-next-step)}
```

### 3. Customer Presentation

- Use deliberately, only when the user requests a deck or accepts the mandatory deck offer.
- Build for one confirmed external meeting, not an undifferentiated daily meeting set. Good fits include first calls, EBCs, and executive workshops.
- Read and follow [Sales Presentations](../sales-presentations/SKILL.md). Convert the reviewed meeting brief into a 6–9 slide customer-safe narrative using `@presentations`.
- Recommended flow: customer-specific point of view and meeting objective; relevant business priorities; two or three tailored workflows; architecture or operating-model diagram when useful; proof and customer examples; discussion questions; proposed next step.
- Keep unresolved questions visible rather than presenting assumptions as customer facts.

### 2. Daily Prep Digest

Use when the user asks for today’s, tomorrow’s, or another date-based meeting summary.

Start from calendar, apply the shared selection rules, keep qualifying meetings, and order them chronologically. Keep separate briefs for separate meetings.

### Output Format

```md
## Today's Meetings

### [Time] — [Meeting Name]

**Attendees:** [Names + roles]

- **Goal:** [What to accomplish]
- **Key context:** [Relevant account, deal, project, or workstream signal]
- **Watchout:** [Risk, blocker, dependency, or source gap]
- **Suggested close:** [Next step, owner, commitment, or decision]

## Priority Watchouts

- [Most important cross-meeting risk]
- [Meeting needing special preparation]
- [Missing context or follow-up needed before meetings]

---

{Follow the instructions and output format/conditions in [Limitations and Improvements](../../shared_skill_instructions.md#limitations-and-improvements)}

{Follow the instructions and output format/conditions in [Next Steps](../../shared_skill_instructions.md#4-offer-one-next-step)}
```
