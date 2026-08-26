# Output templates

## Table of contents
1. Default one-page meeting brief
2. Detailed meeting prep packet
3. Standalone HTML management / IR call sheet
4. Question list
5. Evidence request list
6. Talk track
7. No-context fallback
8. Source log
9. Existing-brief review

## 1. Default one-page meeting brief
Use when the user asks for prep without specifying format.

```markdown
# Meeting prep: [meeting / company / counterparty]

## 1. Objective
- [What we need from the meeting]
- Decision or outcome to drive: [decision / commitment / information / relationship outcome]
- Mode: [management_ir / expert_call / pm_internal_review / investment_committee / client_update / sell_side_call / earnings_call / investor_day / portfolio_watchlist_review / model_review / research_kickoff / post_meeting_follow_up]

## 2. Must-know context
- [Verified fact] ... [source]
- [Verified fact] ... [source]
- [Assumption / inference] ... [why reasonable]

## 3. What matters most
1. [Issue] - [so what]
2. [Issue] - [so what]
3. [Issue] - [so what]

## 4. Must-ask questions
1. [Question] - Why it matters: [decision impact] - Listen for: [answer signal]
2. [Question] - Why it matters: [decision impact] - Listen for: [answer signal]
3. [Question] - Why it matters: [decision impact] - Listen for: [answer signal]

## 4A. If time permits
- [Secondary question] - [why useful]

## 4B. What not to ask or say
- [Topic/wording to avoid] - Reason: [MNPI, disclosure, negotiation, source weakness, or PM strategy sensitivity]

## 5. Evidence needed
- [Request] - Owner/source: [owner] - Needed by: [date if known]

## 6. Likely pushbacks and suggested responses
- If they say: [pushback]
  - Respond with: [response]
  - Follow-up: [question]

## 7. Follow-ups
| Action | Owner | Due | Dependency | Status |
|---|---|---|---|---|
| [action] | [owner] | [date] | [dependency] | [not started] |

## 8. Sources and gaps
- Reviewed: [sources]
- Verify before meeting: [gaps]
```

## 2. Detailed meeting prep packet
Use for high-stakes investor, PM, credit/risk, committee, management, or client meetings.

```markdown
# Meeting prep packet

## Executive view
- Objective:
- Recommended stance:
- Decision needed:
- Highest-risk unknown:
- Best next step:

## Attendees and likely motivations
| Attendee | Role | Likely objective | What they may ask | Prep note |
|---|---|---|---|---|

## Compact context and source-backed facts
| Fact | Source | Date/version | Confidence | Notes |
|---|---|---|---|---|

## Decision architecture
| Decision / issue | Current view | Evidence | Open question | Recommended next step |
|---|---|---|---|---|

## Must-ask question plan
| Priority | Question | Why it matters | Listen for | If evasive | Model / thesis implication |
|---:|---|---|---|---|---|

## If time permits
| Question | Why useful | Evidence to request |
|---|---|---|

## Evidence requests
| Request | Why needed | Source/owner | Timing | Format | Decision supported |
|---|---|---|---|---|---|

## Talking points
- Opening:
- First question:
- Productive follow-up if the answer remains qualitative:
- Close / next public evidence ask:

## Risks and watch-outs
- Do not say/concede:
- Keep internal only:
- Needs verification:
- Escalate to specialist if:

## Follow-up tracker
| Action | Owner | Due | Dependency | Evidence/source | Status |
|---|---|---|---|---|---|
```

## 3. Standalone HTML management / IR call sheet
Use for substantive reusable or explicitly requested HTML prep for a public-company management or investor-relations meeting. This is a live-use brief: keep the call plan above supporting research and do not expand it into an earnings deep dive.

Visible first-read order:

1. Meeting objective, one-sentence investor stance, and core information gap.
2. Four or five source-backed baseline facts or metrics needed to use the questions.
3. Conversation flow: opening frame, first question, follow-up if management remains qualitative, and closing evidence request.
4. Three or four must-ask questions, each with `Why it matters`, `Listen for`, `If evasive`, and `Model / thesis implication`.
5. Compact `If Time Permits` questions and evidence requests.
6. Likely pushbacks, public-disclosure boundary, and what not to ask or say.
7. Follow-up tracker, material open gaps, and readable source notes.

The `Conversation Flow` block must appear before the detailed must-ask question cards. Keep each detailed question subfield to one short sentence when possible and no more than two short sentences when needed for material nuance. Do not place a long earnings or company history section before the must-ask questions. Avoid eight equally weighted question cards, repetitive stance panels, or large tables that do not alter the conversation.

## 4. Question list
Use when the user asks only for questions.

```markdown
## Must-ask questions
1. [Question]
   - Why it matters:
   - Listen for:
   - If evasive:
   - Model / thesis implication:
   - Evidence to request:

## If time permits
- [Question] - Why useful: [decision impact]
```

## 5. Evidence request list
Use when the user needs a sendable or internal evidence request list.

```markdown
## Evidence requests

### Highest priority
| Request | Purpose | Owner/source | Timing | Notes |
|---|---|---|---|---|

### Nice to have
| Request | Purpose | Owner/source | Timing | Notes |
|---|---|---|---|---|

### Questions for the call
- [Question]
```

## 6. Talk track
Use for live-meeting readiness.

```markdown
## Suggested talk track
- Open: [one sentence]
- Frame objective: [one sentence]
- First question: [highest-impact question]
- If the answer remains qualitative: [productive follow-up that stays within disclosure boundaries]
- Next must-ask: [second and third questions]
- Close: [evidence request, next public disclosure, owners, next steps]
```

## 7. No-context fallback
Use when context is sparse.

```markdown
# Starter meeting prep

## Assumed meeting type
- [Assumption based on user wording]

## Useful objective
- [Likely objective]

## Questions to ask
- [Senior generic question tailored to likely meeting type]

## Context that would improve this most
1. Meeting type and attendees
2. Company/counterparty and objective
3. Any pre-read, model, memo, deck, or prior notes
4. Desired output length and audience

## Caveat
- This is a starter brief because no source materials were provided or available.
```

## 8. Source log
Use when citations are unavailable or a traceable audit trail is needed.

```markdown
| Claim / input | Source | Source type | Date/version | Confidence | Notes |
|---|---|---|---|---|---|
```

## 9. Existing-brief review
Use when reviewing a draft prep packet.

```markdown
## Review summary
- Overall readiness: [ready / needs work / not ready]
- Biggest gap:
- Biggest risk:
- Highest-impact fix:

## Recommended edits
| Section | Issue | Proposed fix | Reason |
|---|---|---|---|

## Missing questions
- [Question] - Why it matters:

## Unsupported or stale claims
| Claim | Issue | Source needed | Action |
|---|---|---|---|
```
