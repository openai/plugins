# Follow-up and action tracking

## Table of contents
1. When to switch from prep to debrief
2. Debrief structure
3. Action item taxonomy
4. Follow-up email and message drafting
5. Tracker fields
6. Carry-forward logic

## 1. When to switch from prep to debrief
If the user provides notes, transcript, or says the meeting already happened, create a debrief. Do not keep preparing for a meeting that is over unless the user asks for a retroactive prep or next-call prep.

## 2. Debrief structure
A useful debrief answers:
- What was decided?
- What new facts were learned?
- What assumptions changed?
- What remains open?
- What evidence was promised or requested?
- What commitments were made by each party?
- What should happen next, by whom, and by when?

Default debrief:

```markdown
# Meeting debrief

## Decisions and outcomes
- [Decision / outcome]

## New facts learned
- [Fact] - Source: meeting notes / transcript / attendee

## Open questions
- [Question] - Owner: [owner] - Needed for: [decision]

## Follow-up asks
| Ask | Owner/source | Due | Why needed | Status |
|---|---|---|---|---|

## Action tracker
| Action | Owner | Due | Dependency | Status | Notes |
|---|---|---|---|---|---|

## Draft follow-up
[Draft email or message]
```

## 3. Action item taxonomy
Classify each item so the tracker is useful:
- **Decision**: a choice to be made by a person or committee.
- **Evidence request**: evidence, document, data, or support needed.
- **Analysis task**: work the user or team must perform.
- **Relationship follow-up**: message, thank-you, intro, or stakeholder update.
- **Process milestone**: committee date, earnings event, investor day, rating action, court/regulatory milestone, model update, or client deadline.
- **Watch item**: event or trigger to monitor.
- **Escalation**: issue that needs senior, legal, compliance, accounting, tax, or specialist review.

## 4. Follow-up email and message drafting
Draft follow-ups with the correct circulation mode.

### External-clean follow-up
Use for counterparties, management teams, issuers, clients, investors, experts, or advisors. Include:
- thanks and purpose;
- concise recap of agreed next steps;
- specific asks with owners and deadlines;
- neutral language;
- no internal strategy, valuation bottoms, privileged views, trading intent, position sizing, or restricted information.

### Internal follow-up
Use for team, PM, committee, credit/risk group, or investment team. Include:
- candid readout;
- what changed;
- risks and concerns;
- recommended actions;
- owners, deadlines, and escalation items;
- what not to share externally.

Do not send messages automatically unless the current environment and user instruction explicitly support sending. Prefer drafting for review.

## 5. Tracker fields
For high-stakes meetings, use these fields:

| Field | Purpose |
|---|---|
| Action | What needs to happen |
| Type | Decision, ask, analysis, process, relationship, watch item, escalation |
| Owner | Named person or team if known |
| Counterparty owner | External owner if applicable |
| Due date | Concrete date or relative milestone |
| Dependency | What must happen first |
| Source | Where action came from |
| Status | Not started, requested, in progress, blocked, complete |
| Decision supported | Why it matters |
| Notes | Context or risk |

## 6. Carry-forward logic
When updating a tracker or prior prep:
- preserve existing open items unless marked complete or user asks to remove them;
- add a status-change log if materially changing items;
- do not delete historical items from a source tracker by default;
- distinguish old unresolved asks from new asks;
- call out stale or orphaned actions with no owner or due date.
