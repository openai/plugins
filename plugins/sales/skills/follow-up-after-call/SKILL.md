---
name: follow-up-after-call
description: "Use after a completed customer, prospect, partner, or important internal sales call, discovery session, demo, or conversation, including when the user supplies or uploads a transcript, notes, recording summary, or other grounded evidence. Advise on, assess, qualify, recap, produce seller-ready follow-up actions and drafts, or build a completed-call discovery, pilot, evaluation, or customer-readout deck."
---

# Follow Up After Call


## Context-Gathering Intake

Whenever this skill needs a material clarification, follow the shared [User Input](../../shared_skill_instructions.md#user-input) guidance.

Turn grounded call evidence into a seller-ready follow-up package that preserves what was actually said, makes ownership visible, and gives the seller copy they can use immediately. This skill owns the post-call synthesis and drafts, including an explicitly requested document; it does not send, post, create email drafts, or update CRM.

## Common Skill Instructions

MANDATORY: If they are not already in context, read and follow [the shared Sales skill instructions](../../shared_skill_instructions.md).

## Key Dependency Categories

These categories are particularly important for this workflow; use other sources only when they materially improve the package.

- [Blocking] ~~Meeting Transcripts for the primary transcript, grounded notes, participant language, decisions, commitments, objections, and source links. It blocks the default live-source follow-up path; explicit grounded call evidence already in context satisfies the need.
- ~~Calendar for recent-call identification, attendees, timing, and upcoming related meetings
- ~~CRM for account, opportunity, contact, owner, and CRM-ready next-step context
- ~~Email for customer-facing thread context when the call evidence or promised follow-up lives there
- ~~Internal Messaging for internal account context and a safe suggested destination for the team recap
- ~~Knowledge & Files for exported transcripts, call notes, account notes, and follow-up assets

Grounded call evidence is required. CRM, calendar, files, and messages can enrich the package but cannot substitute for a transcript, grounded notes, or a customer-facing thread that records the call. If evidence is missing, stale, or conflicting, state the limitation rather than reconstructing the call.

## Reference Loading

`SKILL.md` owns the normal evidence-first workflow, chat-first draft behavior, and output package. Load references only when their extra detail changes the decision:

- Use [references/request-schema.yaml](references/request-schema.yaml) when normalizing structured input, relative call dates, meeting-recording identifiers, or fallback evidence paths.
- Use [references/opportunity-and-channel-selection.md](references/opportunity-and-channel-selection.md) when opportunity ranking or internal destination safety is ambiguous.

## Workflow Guidance

### 1. Resolve the call and evidence

- If the user supplies a transcript, notes, link, or clearly identified call, start there.
- If supplied context identifies multiple plausible calls but the request asks for one follow-up, ask which call to use before searching, enriching, combining calls, or drafting; offer the supplied call or account names as choices.
- If the call-resolution path isn't clear, ask the user via [User Input](../../shared_skill_instructions.md#user-input). For a bare invocation such as “Follow up after my call,” do not assume a meeting; offer:
  - `Use my most appropriate recent grounded call`
  - `Use a call, account, attendee, or date I specify`
  - `Use transcript or notes I provide`
- For “my latest call,” “today’s call,” “earlier today,” “yesterday,” “last week,” “my most appropriate recent meeting,” or a named account without a source, treat the wording as a retrievable anchor: search the narrowest recent window in ~~Calendar and ~~Meeting Transcripts, then offer up to three concrete candidates via [User Input](../../shared_skill_instructions.md#user-input). Do not retrieve deeper context or draft a package until the user selects one.
- When the call or account anchor is ambiguous, make at most three source reads to produce concrete candidates; do not gather broad enrichment before the user chooses.
- Treat ambiguous company-like names, partner names, and account shorthands as possible account anchors. When ~~CRM is available and account identity affects which call to retrieve, use a bounded ~~CRM lookup to disambiguate the account before relying on weaker account context; it never substitutes for grounded call evidence.
- If exactly one plausible grounded candidate remains, ask the user to confirm it via [User Input](../../shared_skill_instructions.md#user-input) before drafting. If no grounded evidence can be found, ask for the transcript, notes, or specific call rather than producing a recap from surrounding account context.
- Treat pasted notes, uploads, and user-linked material as valid working evidence; label them as user-provided when they cannot be verified.

### 2. Gather only useful enrichment

- Prefer grounded evidence in this order: ~~Meeting Transcripts transcript; retrievable meeting-recording transcript; other exported transcript; pasted transcript or grounded notes; ~~Knowledge & Files meeting notes; then an ~~Email thread or message as a recovery lane.
- Fetch a user-provided call or transcript handle directly. Otherwise search with the account plus date or timeframe and at most two meeting-topic terms, then fetch the best match.
- Preserve supplemental source-of-truth, call-notes, or transcript links alongside the primary evidence rather than replacing it.
- For an external account call, use ~~CRM when available to resolve the relevant account or opportunity and sharpen names, commercial context, and the one-sentence CRM next step.
- Check ~~Calendar for a related upcoming meeting when timing changes the next step. Use ~~Email, ~~Internal Messaging, and ~~Knowledge & Files only when they add promised actions, blockers, owners, links, or destination context.
- If the transcript explicitly names a meeting or file that could affect the follow-up, do one targeted lookup in ~~Calendar or ~~Knowledge & Files using the exact title and date when available. Include the link if found; otherwise say it was not found in that checked source/window rather than claiming no such meeting or file exists.
- Stop once the package is grounded and the highest-value account/timing context is covered; name missing enrichment instead of continuing broad searches.

### 3. Classify the call and extract commitments

- Decide whether the call is external customer/partner-facing or internal. External email copy and CRM text apply only to external calls.
- Extract decisions, commitments, asks, objections, blockers, owners, and dates. Use `Unknown` or `TBD` when the evidence does not establish them.
- If multiple CRM opportunities are plausible, choose the one matching the call topic, attendees, product, timing, and recent activity. If none is credible, keep the CRM sentence generic and append `(paste into the relevant opp)`.
- When opportunity intent, candidate ranking, or the safest internal channel is not obvious, use [references/opportunity-and-channel-selection.md](references/opportunity-and-channel-selection.md).

### 4. Deliver in the requested format

- Return the package in chat by default, even when an email or internal channel is available. When the user explicitly asks for a Google Doc, Word document, existing meeting note, or supplied template, deliver that requested artifact instead of substituting chat.
- Complete this focused follow-up workflow before invoking the matching document authoring skill. Directly inspect the exact supplied file or template, preserve its structure and branding, update an existing document only when requested, and otherwise create a fresh separate document.
- Preserve the grounded recap, action owners, decisions, commitments, dates, and source links in the document. Read back meaningful finished content before returning the actual document link; do not invent a file, link, source, or completed write.
- Do not create an email draft, send outreach, post an internal message, or write CRM in this workflow.
- Keep verbatim email and internal-message copy in Markdown block quotes so the seller can review and copy it.

### 5. Build the Customer Readout Deck

- For an explicitly requested completed-call discovery, pilot, evaluation, or customer-readout deck, this selected follow-up skill remains the seller-workflow owner. Read and follow [Sales Presentations](../sales-presentations/SKILL.md) as the downstream presentation partner before a substantive final response, gathering evidence, or invoking an artifact-authoring skill.
- For a substantive external call, when the user requests a deck or accepts the deck offer, read and follow [Sales Presentations](../sales-presentations/SKILL.md). Turn the grounded call package into a 6-10 slide customer readout; do not create this mode for a routine or internal call unless the user explicitly asks for an internal presentation.
- After a substantive evaluation, pilot, security, commercial, or deployment call, prefer this as the single next-step offer unless another requested action is clearly more useful.
- Cover: what we heard and agreed; requirements by theme; direct answers to commercial, security, integration, and rollout questions; open questions with owners; proposed evaluation or deployment plan; recommendation; and the next decision.
- Preserve the customer's wording and distinguish `Agreed`, `Proposed`, `Open`, and `Unverified`. Never turn seller follow-up intent into a customer commitment.

### Next Step Options

After the first output, offer the most relevant follow-up from the options below. Offer one clear transition, not a menu. Suggest ONLY these unless you are very confident another option is more useful:
- Refine the external email, internal recap, CRM sentence, or action list using the user's guidance.
- Create the reviewed email draft or post the reviewed internal recap when the user explicitly requests it.
- Add the reviewed recap and action items to an existing meeting note or create a new follow-up note.
- Prepare CRM-ready updates for review.
- Turn a substantive external evaluation call into a 6-10 slide customer readout deck using `@presentations`.
- Offer a scheduled follow-up only when the user requests ongoing follow-up or a full package contains a grounded future commitment, decision date, or meeting.

Next steps to avoid:
- Sending, posting, or updating CRM before the user reviews and explicitly requests the action.

### Mandatory Deck Offer

- End every successful non-deck output with this exact final line: `Would you like me to turn this into a 6–10 slide readout deck using @presentations?`
- Treat this as the one required next-step transition; do not append a competing menu or another offer after it.
- Skip it only when the user already requested or received the deck, explicitly declined slides, or the workflow is blocked before producing grounded follow-up material.

### Automation Offer Guard

Offer a follow-up automation only when the mandatory deck offer is skipped and the user requests a reminder, scheduled check, monitoring, or recurring follow-up, or when a full follow-up package contains a grounded future commitment, decision date, or next meeting. For a one-time recap, decision summary, action list, or focused draft, choose a relevant non-automation next step; do not inspect automation records or suggest recurring work merely because the source mentions a future date. When scheduling is useful, use the grounded timing anchor and frame the automation as a rerun of this skill for the same call/account and standard follow-up package.

Only after establishing that an automation is relevant, check whether a matching local automation already exists under `$CODEX_HOME/automations/*/automation.toml`, or `~/.codex/automations/*/automation.toml` when `CODEX_HOME` is unset. Match by prompt, skill name, account, meeting title, attendee, opportunity, trigger time, or other stable scope details. Treat active and paused matches as already installed.

- If a matching automation exists and the mandatory deck offer is skipped, offer to review or adjust it rather than creating another one.
- If no matching automation exists and the mandatory deck offer is skipped, end with one clear offer to create the automation, describing the output as a seller-ready follow-up package produced after the next call or at the agreed follow-up time. Do not create or update the automation until the user explicitly agrees.
- If the automation surface is unavailable, avoid tool details and simply offer to help set up a recurring or scheduled follow-up check when automations are available.

## Modes

### 1. Full Follow-Up Package

Default when the user asks to follow up after a call. Return every section below in order.

### 2. Focused Draft

Use when the user asks only for an email, internal recap, CRM note, or next-step extraction. Still ground it in call evidence; return the requested section plus a compact `Call Summary`, material gaps, and the status line.

### 3. Customer Readout Deck

Use only when explicitly requested or accepted for a substantive external evaluation, discovery, pilot, or deployment conversation. Follow the deck guidance above instead of the normal chat output format.

## Output Format

Use bold section labels, not top-level headings, for the normal package.

```md
**Call Summary**

- **Primary evidence:** [Clickable transcript/notes link or source label]
- **TL;DR:** [2-4 grounded bullets]
- **Context / Goal:** [Why the call happened]
- **Key Points:** [Important customer/internal signals]
- **Decisions / Commitments:** [What was agreed]
- **Risks / Blockers:** [What could slow follow-through]

**Next Steps**

**Customer**
- [ ] [Action] — [Owner or Unknown] — [Due date or TBD] — [Notes]

**Seller**
- [ ] [Action] — [Owner or Unknown] — [Due date or TBD] — [Notes]

**External Comms**

Subject options (recommended first):
1. [Subject]
2. [Subject]
3. [Subject]

Recommended subject: [Subject]

> Hi <FirstName>,
>
> [150-220 word grounded follow-up email]
>
> Best,
> [Seller]

Draft link: Not created; copy drafted in chat only.

**CRM Next Steps**

[Exactly one sentence with call date, seller action, customer action, and outcome/success criterion.]

**Internal Follow-Up**

Suggested destination: [Safe internal channel/link, or “No verified internal channel found”]

> **[Meeting title]**
>
> [One concise summary paragraph]
>
> **Attendees:** [Names or Unknown]
>
> **Key Notes**
> - [Grounded note]
>
> **Decisions**
> - [Decision or None confirmed]
>
> **Action Items**
> - [Action] — [Owner or TBD] — [Due date or TBD]
>
> **Open Questions / Risks**
> - [Question or risk]
>
> **Source**
> - [Clickable call-notes/transcript link, or no useful link available]

No email draft, Slack post, or CRM update was created.

---

{Follow the instructions and output format/conditions in [Limitations and Improvements](../../shared_skill_instructions.md#limitations-and-improvements)}

{Follow the instructions and output format/conditions in [Next Steps](../../shared_skill_instructions.md#4-offer-one-next-step)}
```

## Output Rules

- Bias toward decisions, risks, next steps, buying process, procurement, technical blockers, and stakeholder movement.
- For an internal call, write exactly `Not applicable: this was an internal call.` under both `External Comms` and `CRM Next Steps`; do not draft external copy.
- Keep the external email concise, customer-safe, and free of sensitive internal language. Never invent recipients, commitments, pricing, dates, or draft links.
- Keep the CRM text to exactly one sentence. For an unresolved opportunity, append `(paste into the relevant opp)`.
- Suggest an internal destination only when it appears internal and relevant. If channel safety is unclear, say to verify before posting; never fabricate a channel URL.
- Before saying no verified internal destination exists, search ~~Internal Messaging once for the account, meeting title, or workstream when that source is available.
- Use useful clickable source links when available, and name source gaps that materially lower confidence.
- Default to one consolidated internal recap; split it into a top-level message plus thread only when the user asks or a verified channel norm requires it.
- Use native mentions for attendees and owners when the selected app supports them; otherwise use readable names.
- Keep the internal draft free of `##` headings. Its opening summary should name the launch path, business impact, decision point, or main follow-through theme without repeating the TL;DR.
- Keep the internal recap compact, de-duplicated, and team-facing; include owners or `TBD` rather than implying ownership.
- Always include the plain status line above after `Internal Follow-Up` unless the user explicitly asks for a different status format.

## Failure Handling

If the call cannot be grounded, state the blocker in one line, say what evidence is needed, and return only safe partial material such as candidate calls or a blank fill-in structure. If optional enrichment is unavailable, still produce the grounded package and label the missing lane.
