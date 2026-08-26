# Fictional Meridian Cloud CRM Update Rules

This editable reference defines the account team's sample Salesforce update policy for the fictional Meridian Cloud demo. It follows source-grounded CRM safety rules: a reviewed opportunity update must stay grounded in the meeting transcript, show exact before-and-after values, preserve authoritative CRM facts, and never execute before the user explicitly approves the exact proposal. No Salesforce records in this demo are real.

## Source Authority

1. Salesforce owns opportunity identity, owner, stage, amount, close date, forecast category, existing contact roles, and the previously recorded next step.
2. The selected transcript owns what attendees actually said, agreed, rejected, or left unresolved; do not infer commitments from account notes or surrounding correspondence.
3. Calendar owns confirmed meeting dates and invite attendees. Email can corroborate buyer intent but cannot silently override the opportunity stage, amount, owner, or forecast.
4. Internal Slack messages and account plans add specialist availability, rollout context, and approval dependencies; they do not prove customer approval.
5. If two sources disagree, show the conflict for review. Never silently rewrite a CRM-owned field to make the story cleaner.

The corresponding seller-facing team document is `sources/google-drive.md` → `Sales Team CRM Update Guidance`. Before displaying a meeting outcome or proposed Salesforce update, identify the five reviewed sources in chat: **CRM: Salesforce**, **Call notes: Granola**, **Email: Gmail**, **Internal communication: Slack**, and **Team guidance: Google Drive**. Keep this source summary compact and place it before the reviewed meeting output.

## Opportunity-Update Policy

| Salesforce field | Update when | Leave unchanged when |
| --- | --- | --- |
| Next Step | The transcript supports a specific owner, action, due date, and expected outcome. Use concise Salesforce-ready bullets or one compact sentence. | The user has not reviewed the proposed text, the owner is unclear, or the due date was not actually stated. |
| Deal Notes | New decisions, requirements, risks, and buying-process changes are explicitly stated during the meeting. Separate agreed facts from proposals and unresolved items. | The note would repeat stale information, reveal unsupported internal-only commentary, or imply a customer commitment that was not made. |
| Stage | The customer explicitly clears the current stage's exit criteria and confirms the next buying step; the exact stage value is supported by the connected Salesforce metadata. | A seller expects progress, a technical discussion went well, security approval is still pending, or the customer's next decision is not confirmed. |
| Amount | The buyer or approved commercial owner explicitly confirms a revised commercial amount and the exact opportunity is identified. | Amount is inferred from seat count, the proposal is preliminary, or approval and pricing are unconfirmed. |
| Close Date | A customer-confirmed purchasing milestone supports the new date and the user approves the exact change. | A date is only an internal aspiration, a calendar placeholder, or a meeting date that is not a buying commitment. |
| Forecast Category | The customer's verified buying decision, approval path, and timing satisfy the organization's documented forecast criteria. | Security approval, economic-buyer commitment, procurement, or decision timing remains uncertain. Never move a deal to Commit based on seller optimism. |
| Decision Criteria & Purchase Process | The meeting explicitly establishes an approver, buying sequence, security requirement, procurement step, or decision checkpoint. | A participant's role, approval authority, or buying process is inferred rather than stated. |
| Risks and Asks | A participant identifies a material blocker, owner, requested support, or unresolved approval dependency. | The risk is speculative, already resolved, or contains a promise not supported by the transcript. |
| Contact Roles / Economic Buyer | A verified attendee explicitly states their own role or an already identified stakeholder's role, and the record/relationship is confirmed. | A title, role, email address, economic-buyer authority, or replacement sponsor is guessed. |
| Tasks / Activities | The user separately authorizes creating a task or logging an activity with a known owner, due date, and linked record. | The action is only a proposed reminder or there is no supported write surface. |

## Review Before Any Write

- Identify the exact Salesforce object and opportunity record. Strategy, discovery, MEDDICC-like qualification, renewal, expansion, and next-step updates normally belong on `Opportunity`, even when the user calls this an account update.
- Show the current value and proposed value for every changed field, a concise meeting-evidence reason, and the fields deliberately left unchanged.
- Confirm that non-standard fields exist and are updateable before proposing their exact API names. Standard examples are `NextStep`, `StageName`, `Amount`, `CloseDate`, and `ForecastCategoryName`; custom discovery or deal-notes field names vary by organization.
- Validate restricted stage and forecast picklist values with Salesforce metadata before a live update. Do not write `Unknown`, `TBD`, or `None` as a placeholder unless that value is valid and supported.
- Ask for approval of the exact displayed proposal. A changed field, target record, due date, or commercial value requires a revised review and fresh approval.
- Send only changed, supported fields. Inspect the action response and verify the record if the response does not prove the update was committed.
- Use `DEMO-NORTHSTAR-OPPORTUNITY` only as the clearly fictional record reference in this sample; it is not a real Salesforce ID and must never be supplied to a live write tool.
- Keep a fictional walkthrough separate from live action: selecting `Save to Salesforce` in this demo explains the approval-gated behavior and simulates the result; it never calls a write tool or updates a real CRM.
- After the explicitly approved walkthrough ends, distinguish actual callable connectors from unverified account connections and recommended-but-uninstalled plugins. Never imply that account-context files grant live Salesforce, Gmail, Calendar, Granola, HubSpot, Apollo, or ZoomInfo access.

## Northstar Health Example Decision

- **Opportunity:** Northstar Health — FY{{fiscal_year}} Governed Workflow Expansion.
- **Current amount:** $420,000; unchanged because the meeting did not approve new pricing.
- **Current stage:** Security review; unchanged because the existing CRM stage is authoritative and neither pilot success, rollout approval, nor Casey Patel's supporting controls sign-off has been established.
- **Current close date:** {{next_thursday}}; unchanged because the meeting confirmed a working checkpoint, not a new contractual close date.
- **Current forecast category:** Best Case; unchanged because pilot readiness, executive approval, and final security sign-off remain open.
- **Proposed next step:** `Riley Morgan: share the existing 1,200-user pilot scorecard and review customer uptime feedback with Jordan Lee, Casey Patel, and Priya Shah by {{next_thursday}}.`
- **Proposed deal note:** `Engagement, repeat usage, and deployment milestones are mostly met, but the potential 4,500-user expansion depends on validating unresolved customer uptime feedback; Priya Shah will support the review. No amount, close date, implementation date, uptime result, or final approval changed.`
- **Proposed decision criteria:** `Validate original pilot-success goals, customer-reported uptime feedback and observed impact, and supporting administrator controls before the executive deployment decision.`
- **Proposed risk:** `Pilot success and broader rollout remain unapproved until Jordan Lee and Casey Patel review the customer uptime feedback with Riley Morgan and Priya Shah.`
- **Not proposed:** stage advancement, forecast upgrade, amount change, close-date change, account-owner reassignment, unverified contact creation, or automatic email/task creation.
