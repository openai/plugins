# Canonical Sales Demonstration Flow

This reference is the sole owner of the conversation's user-visible states, exact message framing, numbered menus, transitions, optional branches, approval boundaries, and completion behavior. Run the Meridian Cloud scenario as a natural executive-first conversation: Maya Chen first sees a focused division-wide sales-leadership dashboard; Riley Morgan then sees his complete seller account home across **Home**, **Accounts**, and **Pipeline** using the same customer evidence; an optional Northstar Health meeting-preparation response recommends a buyer strategy and opens the exact existing pilot-readiness Google Slides deck; an optional customer email proposes a pilot-readiness discussion; Riley reviews a completed Northstar meeting and a proposed Salesforce opportunity update; the walkthrough ends by suggesting useful workflows with the user's own data. A separately and explicitly requested simulated save remains available without ever changing Salesforce.

The scenario and all customer evidence are fictional; no live systems are accessed. Disclose the scenario's nature prominently in the opening response only. After the first message, remain in character without repeatedly saying fictional, demo, or sample in user-facing copy; mention the approved Salesforce save is simulated only once in the terminal response. If the user explicitly asks about provenance or whether a write happened, answer truthfully and precisely.

For WORK MODE/PUBLISHED DEMOS, ChatGPT Web, and headless runtimes, always send both personas to the already-published Sites: https://meridian-sales-operating-views.openai.chatgpt.site/leadership and https://meridian-sales-operating-views.openai.chatgpt.site/seller. The exact existing Northstar customer deck is https://docs.google.com/presentation/d/1JM3bmarfM9neOoTOBtGW12wGUYuYeLqT9HWKdDlMamU/edit?slide=id.p1#slide=id.p1. DEVELOPMENT may use a verified loopback preview only when explicitly selected outside Work Mode. Never start a local server in ChatGPT Web or Work Mode; never replace these destinations with the Google homepage, a placeholder, another deck, or localhost, and never fabricate hosting or publish without explicit authorization.

## State Machine

| State | Enter when | Available actions or continuation | Completion or return |
| --- | --- | --- | --- |
| `leadership_dashboard` | The user starts the guided Sales scenario. | Continue to the seller account dashboard or learn how Codex gathers context to improve its answer. | Return from an explicitly requested explanation without repeating topics already answered, or advance to `account_priority_view`; dashboard publication is never a demo action. |
| `account_priority_view` | The user opens the seller account home. | Naturally suggest preparing the existing customer deck for the upcoming Northstar meeting; do not display numbered seller choices. | Enter the existing Northstar presentation branch when the user continues; advance to `meeting_followup` only when separately requested, and never offer seller-dashboard publication. |
| `meeting_followup` | The user accepts the presentation's meeting-follow-up transition or explicitly requests the completed Northstar meeting from the seller overview or outreach draft. | Explain that the reviewed CRM updates could be saved after approval, then suggest building a seller dashboard and trying other real-data workflows; do not show a save menu. | Exit the fictional walkthrough when the user chooses a real workflow; enter `salesforce_review_complete` only for a separate explicit request to save the exact displayed changes. |
| `salesforce_review_complete` | The user selects `Save it to Salesforce` for the exact reviewed proposal. | After the demo is complete, offer up to three optional real-data workflows: build an account home, prepare for a customer meeting, or review meeting follow-up and CRM updates. | Confirm no Salesforce records were changed, explain which example connectors each real workflow needs, and offer to guide setup only after the user chooses a workflow. |

Track the active state, current role, selected account, active dashboard URL, and interrupted return state only in the existing conversation. Do not create persistent workflow state. All generated drafts, follow-up questions, recommendations, approval requests, and next steps appear in chat; dashboards remain read-only artifacts and the walkthrough never initiates a deployment. Show no more than three numbered options, including the optional real-workflow choices offered after completion. An invalid number receives a concise correction and the same numbered choices. A free-form question gets a direct grounded answer and the interrupted state's valid menu. Return immediately after sending each final message.

### Step 1: leadership_dashboard

- **Entry:** The user requests the guided Sales walkthrough.
- **Type:** Executive-first overview with optional forecast-risk and leadership-decision branches; future dashboard publishing is informational only.
- **Before responding:** For the explicitly requested canned walkthrough, use `scripts/start_demo_fast.py --step leadership` through the focused skill's one-call **Fast Demo Start**, passing the user's current local date or IANA timezone as instructed there; the no-argument default reuses both existing workspace-visible hosted Sites without a local server, so ChatGPT web and browserless runtimes always receive usable published links. Only explicitly selected DEVELOPMENT or an already-visible valid loopback URL may refresh and start a local preview. Resolve current dates and extract this exact prepared opening; do not separately read company/source fixtures, inspect project commands, probe Sites/connectors, launch browser automation, or perform redundant preview checks before the first answer. The prevalidated executive dashboard contains exactly **Forecast & key metrics**, **Account Focus**, and **Team Focus**, with immediately visible briefings, a full-width priority account table and responsive right-side detail drawer spanning multiple verified division sellers, practical unblock guidance, team coaching context, and no segment or manager filters.
- **Final message:**

Note: This walkthrough uses fictional data to demonstrate what's possible before you connect your own company context.

**Scenario**

You're **Maya Chen, Vice President of Sales for Meridian Cloud's North America Enterprise division**. Meridian Cloud builds governed enterprise AI assistants, reusable workflows, and administration controls; your division spans three regional teams, 38 accounts, and 31 opportunities.

It's 8:30 AM on Monday and you'd like to review your team's progress towards your revenue targets and learn where you can be most helpful. Your Exec Dashboard is ready with the latest context.

**Connected context**

| Connector | What was found | Example resource |
| --- | --- | --- |
| CRM: Salesforce | Division forecast, 31 opportunities, owners, and account stages | Opportunity: Northstar Health — FY{{fiscal_year}} Governed Workflow Expansion — $420,000 |
| Call notes: Granola | Pilot-success criteria, customer uptime feedback, buyer concerns, and meeting outcomes | Call: Northstar Health Expansion & Security Review — {{two_business_days_ago}} |
| Email: Gmail | Customer decision timing, pilot questions, uptime feedback, and sponsor changes | Email: Re: Northstar Health deployment decision — Jordan Lee — {{previous_business_day}} |
| Calendar: Google Calendar | Decision checkpoints, investment committees, and executive reviews | Event: Northstar Health Executive Deployment Decision — {{next_thursday}} |
| Internal communication: Slack | External customer questions, internal pilot/uptime coordination, billing guardrails, and UserOps readiness | #ext-northstar-health: customer uptime feedback ({{previous_business_day}}); #acct-northstar-health: Priya's review; #billing-deal-desk: pricing guardrails; #userops-enterprise-rollouts: rollout readiness ({{today}}) |
| Account documents: Google Drive | Existing pilot-readiness deck, prior customer pricing deck, account plan, and approved CRM-update guidance | Slides: Northstar Health — Pilot Completion & Company-Wide Rollout Readiness \| FY26; Deck: Northstar Health — FY{{fiscal_year}} Pricing & Packaging Options — Customer Working Session; CRM update guidance |

**Overview**

- **Forecast:** $13.52M against a $14.0M target; close the $480K gap without promoting unresolved deals.
- **Protect Northstar's $420K expansion:** Its 1,200-user pilot has mostly met engagement, repeat-usage, and deployment goals, but Jordan Lee and Casey Patel need unresolved customer uptime feedback clarified before recommending a broader rollout; ask Riley Morgan and Priya Shah to review the existing pilot-readiness deck with them.
- **Unblock two other deals:** Atlas's $680K deal needs Priya Shah and Devon Brooks to investigate a performance issue. Solstice's $310K deal needs Leila Chen to confirm whether the product meets the customer's admin requirements.

Click here to open your **[sales leadership dashboard](https://meridian-sales-operating-views.openai.chatgpt.site/leadership)**. After you've reviewed:

1. Next demo showing the seller account dashboard
2. Learn more about how Codex gathers context to give a better answer

- **Reply `1`:** Enter `account_priority_view` and explicitly change perspective to Riley Morgan.
- **Reply `2`:** Enter `connector_explanation`; explain how Codex combines and reconciles relevant customer context, then offer only the unvisited seller-dashboard continuation.
- **Free-form forecast-risk request:** Enter `forecast_risk_explanation` only when the user explicitly asks about forecast risk; never re-suggest a question that was already answered.
- **Output boundaries:** Show exactly one first-message disclosure, the Maya persona and company framing, and the concise Monday-morning **Scenario** before showing any connected-source inventory. Follow it with one six-row three-column connector table, an **Overview** containing no more than three executive-insight bullets, one prominent working dashboard link, and exactly two numbered choices. Keep publishing out of the numbered actions and do not initiate it. Keep the complete priority-sorted account list, account-monitoring/unblock detail, and team coaching context inside the dashboard. Do not describe or display segment, manager, period, region, or product filters; the account and forecast briefings are visible immediately. Do not promise a release date, feature availability, quantified performance target, on-site date, staffing commitment, customer attendance, or automatically scheduled action. Do not imply actual live connector reads, expose operation names, list full opportunity rows in chat, or advance automatically.

### Step 2: account_priority_view

- **Entry:** The user selects `Next demo showing the seller account dashboard` from Maya's leadership view.
- **Type:** Broad seller account home with exactly three views—**Home**, **Accounts**, and **Pipeline**—plus optional existing Northstar customer presentation, pilot-readiness outreach, and source-grounded account-evidence branches. The compatibility state name does not define the product framing.
- **Before responding:** Explicitly switch perspective to Riley Morgan. Reuse the verified loopback seller dashboard during DEVELOPMENT or the existing verified hosted seller Site in WORK MODE/PUBLISHED DEMOS, and confirm the account home shows **Home**, **Accounts**, and **Pipeline**, with the same ten accounts represented in Maya's West-region evidence. **Home** brings together customer requests, meetings, follow-ups, recent changes, and items needing review; **Accounts** holds the complete customer book with relationship status, descending grounded priority scores, verified open replies, and next actions; **Pipeline** groups opportunities by their current pilot, security, commercial-alignment, or renewal blocker and identifies the next action to advance each deal. Account details separately show verified upcoming meetings and recent communications. Review Northstar's executive sponsor Jordan Lee, technical buyer Casey Patel, solutions architect Priya Shah, {{next_thursday}} decision, existing 12-slide pilot-readiness deck, prior pricing deck, original pilot goals, and unresolved customer uptime feedback. Do not assume approval, schedule a meeting, or create a presentation.
- **Final message:**

**Switching gears: Riley Morgan's account home**

**Scenario**

You're now **Riley Morgan, Strategic Enterprise Account Executive at Meridian Cloud**. You'd like help prioritizing your top 3 accounts to focus on this week.

**Key context**

- **Your accounts:** Salesforce confirms ten owned accounts, $3.37M in opportunities, and Northstar's $420,000 expansion still in Security review.
- **The customer concern:** Email, Slack, and call notes show that Jordan Lee needs the original pilot scorecard and clarification of unresolved customer uptime feedback.
- **The next milestone:** Google Calendar confirms Northstar's {{next_thursday}} pilot-readiness discussion with Jordan Lee, Casey Patel, and Priya Shah; Google Drive contains your existing 12-slide pilot-readiness deck.

**Overview**

- **Northstar Health — prepare for the pilot review:** Revisit the original 1,200-user pilot scorecard, clarify the unresolved uptime concern, and bring Jordan Lee, Casey Patel, and Priya Shah into the {{next_thursday}} discussion.
- **Atlas Manufacturing — investigate a performance issue:** Ask Priya Shah and Devon Brooks to review the customer's concerns before advancing the $680K deal.
- **Solstice Financial — confirm the product fits:** Ask Leila Chen whether the product meets the customer's admin requirements before advancing the $310K deal.

Click here to open your **[Seller Account Dashboard](https://meridian-sales-operating-views.openai.chatgpt.site/seller)**

After you've taken a look, let's make a deck to prep for the meeting to make sure it lands

- **Reply `1`:** Treat an affirmative response, request to continue, or request to prepare the deck as entry to `northstar_presentation_draft`; inspect the existing pilot-readiness deck and corroborating customer evidence, then provide the exact existing Google Slides link without creating a replacement.
- **Explicit meeting-follow-up request:** Enter `meeting_followup` only when the user separately asks to skip to the completed Northstar meeting.
- **Explicit email request:** Enter `launch_reengagement_draft` only if the user separately asks to draft customer outreach; do not create, save, or send email.
- **Free-form question:** Answer directly from the relevant source evidence, then restore the exact seller meeting-preparation transition without changing persona or skipping the meeting review.
- **Output boundaries:** Introduce Riley's goal of focusing on his top three accounts, summarize key customer context in exactly three grounded bullets, and provide an **Overview** with exactly three practical account-specific actions; never repeat the opening connector table. Keep the seller account home broadly useful across **Home**, **Accounts**, and **Pipeline**, make its link the primary action, and retain detailed account rows, customer context, and opportunity data inside the interactive dashboard. Grounded priority scores may order the complete Accounts table but must never become the home heading, exclude owned accounts, or define the dashboard identity. End with the single natural Northstar deck-preparation transition and no numbered seller menu; route an explicitly requested customer email to Northstar's verified executive sponsor rather than Harbor. Never offer Sites publication from the seller view, repeat the initial disclosure, create a replacement deck, or treat the seller's account book as the full division forecast.

### Step 3: meeting_followup

- **Entry:** The user selects completed-meeting follow-up from the Northstar customer-deck branch, continues from the Northstar email branch, or explicitly asks to skip ahead from Riley's account overview.
- **Type:** Compact meeting review, read-only Salesforce proposal, and real-data workflow handoff.
- **Before responding:** Keep the Riley Morgan seller perspective. Review `northstar-followup-meeting.md`, `crm-update-rules.md`, and the matching Salesforce, meeting-notes, email, Slack, and account-document references; identify the exact Opportunity and the user's approved update policy before presenting a proposed diff.
- **Final message:**

Your messaging landed well with the customer. Jordan Lee and Casey Patel confirmed that the 1,200-user pilot mostly met its engagement, repeat-usage, and deployment goals, but the $420,000 expansion cannot advance until the reported uptime concern and Casey's remaining controls questions are resolved, but there's a path to a solve.

**What happens next**

- Sync with engineering on their reliability roadmap
- **Salesforce update:** Make sure your CRM is up to date for your team's visibility

**Salesforce Opportunity — proposed updates**

| Field | Current | Proposed |
| --- | --- | --- |
| Next Step | Validate pilot success and open uptime feedback before the decision. | Riley reviews the pilot scorecard and customer-reported uptime concern with Casey and Priya before {{next_thursday}}'s decision. |
| Deal Notes | Pilot-readiness and uptime questions pending. | Engagement, repeat usage, and deployment milestones are mostly met; broader rollout depends on validating unresolved customer uptime feedback. |
| Decision Criteria | Pilot success and Security review required. | Validate the original pilot goals, customer uptime concern and observed impact, and Casey's supporting controls questions before the expansion decision. |
| Risks and Asks | Pilot feedback pending validation. | Rollout approval remains open until Riley and Priya clarify the customer uptime feedback with Jordan Lee and Casey Patel. |

**Unchanged:** $420,000 amount, Security review stage, {{next_thursday}} close date, Best Case forecast, and Riley Morgan as owner.

**These updates could be saved to Salesforce after your approval; nothing has been applied.**

**Next:** Build your seller dashboard and try meeting prep, account planning, and other workflows with your real data.

- **Reply `1`:** Legacy compatibility only. Enter `salesforce_review_complete` only if the user separately requests saving and has explicitly approved the exact displayed proposal; explain that the bundled save is simulated without calling Salesforce or changing an external record. Never treat `okay`, a bare number, or acceptance of the real-data next step as CRM approval.
- **CRM rules request:** Enter `crm_update_rules` only when the user explicitly asks about source authority or protected fields; then restore the read-only proposal and real-data next step without a save menu.
- **Account-overview request:** Return to `account_priority_view` only when explicitly requested; restore Riley's exact Northstar meeting-preparation transition without offering publication.
- **Changed proposal:** A changed record, owner, due date, field, stage, amount, or forecast requires a revised visible diff and fresh approval.
- **Real-data request:** Exit the walkthrough before any live Salesforce action; resolve the actual writable record and supported fields, display current/proposed values, obtain separate approval, and verify an explicitly authorized real write.
- **Output boundaries:** Start with the concise customer-outcome paragraph, then show exactly two next actions: syncing with engineering on the reliability roadmap and keeping Salesforce up to date for team visibility. Do not add a title, scenario framing, output/goal labels, source inventory, connector table, separate CRM-guidance explanation, or save menu. Preserve the four-field before/after diff and unchanged commercial facts; explain that the updates could be saved after approval and nothing has been applied, then suggest building a seller dashboard and trying other workflows with real data.

### Step 4: salesforce_review_complete

- **Entry:** The user selected `Save it to Salesforce` for the exact proposal shown in `meeting_followup`.
- **Type:** Terminal.
- **Before responding:** Keep the conclusion short and outcome-first. Offer only relevant real seller workflows and describe their typical connector requirements as examples, not as claims that particular integrations are installed, connected, authorized, or installable. Do not probe customer records, inspect connector inventories, perform an installation, request a plugin, publish a Site, or launch a CRM write.
- **Final message:**

**Demo complete**

The Salesforce update was simulated. **No Salesforce records were changed.**

**Try it with your own data**

1. **Build your seller account home** — Connect Salesforce, Gmail, Google Calendar, and Slack to review your real accounts, upcoming meetings, and open customer requests.
2. **Prepare for a customer meeting** — Connect Google Calendar, Gmail, and Google Drive to pull together account context, customer concerns, and existing materials.
3. **Review meeting follow-up and CRM updates** — Connect Salesforce and meeting notes to draft next steps and review proposed CRM changes before approving anything.

Tell me which workflow you'd like to run, and I'll walk you through connecting the tools it needs.

- **Workflow selection:** Treat the numbered options as optional real-workflow handoffs after the fictional walkthrough has finished, not additional demo states. After the user chooses one, exit the canned scenario, resolve the actual appropriate production Sales workflow, inspect only the connectors genuinely needed, and offer specific setup or authorization when available. Never claim a provider is already connected or available without verification, and do not install, authorize, publish, send, create a record, or update Salesforce without the separate action-specific approval it requires.
- **Completion:** Keep the message outcome-first and concise: confirm the demo is complete, state that no Salesforce records were changed, show no more than three practical real-workflow choices with example connector needs, and offer to guide setup. Do not include a connector inventory, connection-status report, personalized provider list, unresolved placeholders, or an automatic continuation.

### Branch: connector_explanation

- **Parent:** The leadership dashboard's context-explanation choice, `account_priority_view`, or a free-form question during either dashboard state.
- **Type:** Optional and repeatable.
- **Response:** Explain that customer data can stay distributed across CRM, call notes, email, calendar, internal communication, documents, approved local files, and custom systems. Describe careful account and contact matching, source-specific authority, uncertain matches, conflicting records, incomplete connectivity, and cleanup that requires human approval. Use Harbor's former sponsor and still-unconfirmed replacement as the concrete example.
- **Return:** After the leadership context-explanation choice has been answered, offer only `1. Next demo showing the seller account dashboard`; never repeat the context-explanation option or any other topic already answered. For a seller interruption, restore the unnumbered meeting-preparation transition. Do not claim information was centralized, rewritten, or retrieved from a live customer source.

### Branch: northstar_presentation_draft

- **Parent:** `account_priority_view`.
- **Type:** Optional, explicitly requested review of the exact existing Northstar customer presentation.
- **Before responding:** Read `northstar-presentation-brief.md`, `sources/granola.md`, `sources/google-drive.md`, `sources/gtm-resource-hub.md`, and `sources/salesforce.md`; add scoped Gmail or Slack evidence only when it clarifies the buyer's pilot goals, customer uptime feedback, or decision owner. Use the canonical Northstar customer presentation, exactly as linked in the brief. Do not create, copy, edit, export, rewrite, upload, publish, send, or replace that presentation; do not invoke Sales Presentations, Presentation Authoring, or another deck builder.
- **Final message:**

**Northstar Health: pilot-completion and rollout-readiness presentation**

Okay, I've built a draft of a deck you can go through with the customer.

**[Open the Northstar pilot-readiness presentation](https://docs.google.com/presentation/d/1JM3bmarfM9neOoTOBtGW12wGUYuYeLqT9HWKdDlMamU/edit?slide=id.p1#slide=id.p1)**

**Recommended approach**

- **What's going well:** The 1,200-user pilot has largely met its engagement, repeat-usage, and deployment goals.
- **Their core objection is:** Jordan Lee and Casey Patel need to understand the unresolved customer-reported uptime feedback and its operational impact before considering a broader rollout.
- **To address this:**
  - **Potential mitigations:** Ask Casey to clarify the reported uptime concern, have Priya verify its operational impact, and agree on the evidence needed before any rollout decision.
  - **Messaging:** "The pilot is showing strong engagement and repeat usage. Let's review the uptime feedback together and agree on what needs to be validated before we discuss scaling."
  - **Who to pull into the meeting and what they should say:** Jordan Lee, the executive sponsor, should define the decision criteria; Casey Patel, the technical buyer, should explain the concern; Priya Shah, the solutions architect, should outline the validation plan; and Riley Morgan, the account owner, should connect the pilot scorecard to the next steps.

**Next:** Let’s fast-forward to after the customer meeting and review the follow-up and proposed Salesforce updates.

- **Artifact link:** Use the exact supplied Google Slides URL above, unchanged. Never substitute a generated PowerPoint, copied presentation, PDF preview, repository placeholder, or another deck.
- **Requested outreach:** Enter `launch_reengagement_draft` only when the user asks for an email; do not create, save, send, or schedule anything.
- **Requested next demo:** Treat `okay`, `yes`, `continue`, or another acceptance of the suggested next step as a direct transition to `meeting_followup`; do not display an intermediate choice menu.
- **Requested clarification:** Explain the original pilot-success criteria, unresolved customer uptime feedback, known buyer roles, or still-unconfirmed rollout decision without changing the supplied presentation.
- **Output boundaries:** Show only the title, one-sentence deck handoff, exact Google Slides link, grounded recommended approach, and the single natural transition to meeting follow-up. Cover pilot progress, the unresolved objection, potential mitigations, customer messaging, and who should attend and what each person should say. Do not add scenario framing, a source or connector inventory, opportunity figures, a presentation description, or a numbered follow-up menu. Never expose private deal-desk messages, unapproved services, internal staffing, unsupported case-study outcomes, an invented uptime incident or SLA, a guaranteed fix, a booked meeting, or an approved expansion.

### Branch: launch_reengagement_draft

- **Parent:** `account_priority_view` or `northstar_presentation_draft`.
- **Type:** Optional, review-only.
- **Final message:**

**Northstar Health pilot-readiness and customer-sync draft**

-----

**To:** Jordan Lee, Vice President of Clinical Operations

**Subject:** Northstar pilot readiness and the remaining uptime question

Hi Jordan,

Ahead of {{next_thursday}}'s deployment decision, I'd like to review the existing pilot against its original engagement, repeat-usage, and deployment-milestone goals. Those areas are mostly met, but I understand your team still has customer uptime feedback that needs to be clarified before we discuss a broader rollout.

Would you and Casey be open to a short pilot-readiness discussion with our solutions architect Priya Shah and me? We can walk through the existing presentation, understand the reported uptime concern and its operational impact, and cover any supporting administrator-audit or retention questions without assuming your team has approved the rollout.

Best,
Riley Morgan

-----

After iterating on this draft, I could create a draft in Gmail or even send it on your behalf if requested.

Next, let's fast forward to after your meeting so we can handle the followup.

- **Reply `1`:** On the user's next affirmative continuation, enter `meeting_followup` without creating, saving, or sending the email; no numbered customer-email menu is shown.
- **Explicit revision request:** Revise the review-only Northstar draft using the same documented customer evidence. Creating a Gmail draft or sending an email requires a separate, explicit action-specific request and approval.
- **Additional free-form question:** If asked `Which other accounts match last week's launch?`, explain documented Solstice and Harbor relevance while preserving Northstar as the default customer follow-up and Harbor's restricted outreach posture.
- **Do not:** Contact Harbor by default, send or create an email, schedule a meeting, promise Casey's sign-off, invent an outage, SLA breach, root cause, guaranteed fix, product feature, or retention commitment, expose internal-only Slack messages, or alter the Salesforce opportunity.

### Branch: site_publication

- **Status:** Retained as a compatibility identifier only; publishing is not a numbered choice or an action within the canned walkthrough.
- **User-facing behavior:** The canned leadership and seller responses do not mention dashboard publication or offer it as an action.
- **Explicit future request:** If the user separately asks to publish their own real dashboard, exit the fictional demo and follow the available Sites workflow for the specifically authorized artifact, intended audience, and verified hosting capabilities. Do not publish the canned dashboard, claim a localhost preview is hosted, invent a Site URL, or deploy anything automatically.

### Branch: forecast_risk_explanation

- **Parent:** `leadership_dashboard`.
- **Type:** Optional, explicitly requested; never suggest the same answered question again.
- **Response:** Explain the division forecast gap and the specific buyer-backed risks behind it: Northstar's unresolved pilot success and customer uptime feedback, Atlas's customer-reported workflow performance, Solstice's role-based-access review, and Harbor's missing executive buyer. Distinguish the broader division forecast from Riley's account-level exposure, cite the relevant source categories, and retain conservative forecast categories.
- **Return:** Offer only leadership continuations the user has not already explored; never suggest the forecast-risk question again or add a Sites-publication choice. Do not advance the meeting or promote unresolved deals.

### Branch: crm_update_rules

- **Parent:** `meeting_followup`.
- **Type:** Optional, repeatable.
- **Response:** Explain the editable rules in `crm-update-rules.md`: Salesforce owns current opportunity fields; the selected transcript owns actual commitments; Calendar, email, Slack, and account notes provide scoped corroboration; only supported changed fields enter the proposal; stage, amount, close date, forecast, and owner stay unchanged without verified evidence; exact record/field values must be reviewed and explicitly approved before a real update.
- **Return:** Restore the same review-only proposal and real-data next step without adding a save menu. Do not silently modify or execute the proposal.
