# FA Customer Onboarding - Sub-flow Reference

**Tools used:** `fa_search_tool`, `query_portfolio`, `get_company_report`, `get_live_report`,
`application_decisioning_tool`, `get_company_ownership_tree`, `manage_folder`

This file defines the full FA customer onboarding pipeline. It is loaded by the master
`SKILL.md` when user intent resolves to customer onboarding or new account creation.

**Core question answered by this pipeline:**

> "I want to onboard [Company X] - what credit limit should I give them, and where should
> I file them in my portfolio?"

The pipeline moves a customer from an unverified name or DUNS through identity resolution,
credit assessment, automated credit decisioning, and portfolio organisation in a single run.

---

## Pipeline Overview

```
Stage 1:  Find and Verify Company
  -> Stage 2:  Company Overview
    -> Stage 3:  Credit Decisioning
      -> Stage 4:  Approve and Onboard
```

Each stage is gated. A stage must complete successfully and produce its required outputs
before the next stage begins. The pipeline runs autonomously - do not pause between stages
to ask the user whether to proceed, unless a blocking ambiguity (e.g. multiple unresolvable
company candidates) prevents the next stage from starting.

---

## Visual Pipeline Tracker (Mandatory)

At the start of every pipeline run and at the start of every stage, render the visual
pipeline tracker below. The tracker must:

- Show all 4 stages as named boxes in order:
  **Find & Verify -> Co. Overview -> Decisioning -> Approve & Onboard**
- Clearly indicate which stage is **active** (blue), which are **completed** (green -),
  and which are **pending** (grey)
- Be rendered inline before the narrative for that stage
- Update at every stage transition

**State colour rules:**

| State | Fill | Stroke | Text colour |
|---|---|---|---|
| Pending | `var(--color-background-secondary)` | `var(--color-border-tertiary)` | `var(--color-text-secondary)` |
| Active | `#E6F1FB` | `#185FA5` stroke-width 1.5 | title `#0C447C`, sub `#185FA5` |
| Complete | `#EAF3DE` | `#3B6D11` stroke-width 1.5 | title `#27500A`, sub `#3B6D11` |

### Arrow fix - mandatory SVG pattern

Use `<polyline>` connectors with `marker-end` referencing the shared `<defs>` arrow block.
The `<defs>` block **must** be the first child of `<svg>`. Do **not** use `<line>` elements.

**Required `<defs>` block (copy verbatim into every tracker SVG):**
```xml
<defs>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M1 1 L9 5 L1 9" fill="none" stroke="context-stroke"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

### Full 4-stage tracker template

Copy this template at the start of every stage, replacing only the `[STATE_*]` and
`[*_COLOUR]` placeholders per the colour rules above. Do not alter box positions,
connector coordinates, or the `<defs>` block.

```xml
<svg width="100%" viewBox="0 0 680 120" role="img">
  <title>FA Onboarding Pipeline Tracker</title>
  <desc>Four-stage FA onboarding pipeline tracker showing stage states.</desc>
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M1 1 L9 5 L1 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Connectors -->
  <polyline points="190,44 210,44" fill="none" stroke="var(--color-border-secondary)" stroke-width="1.5" marker-end="url(#arr)"/>
  <polyline points="330,44 350,44" fill="none" stroke="var(--color-border-secondary)" stroke-width="1.5" marker-end="url(#arr)"/>
  <polyline points="470,44 490,44" fill="none" stroke="var(--color-border-secondary)" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- Stage 1: Find and Verify Company -->
  <rect x="70"  y="20" width="120" height="48" rx="8" fill="[STATE_FILL]" stroke="[STATE_STROKE]" stroke-width="[STATE_SW]"/>
  <text x="130" y="38" text-anchor="middle" dominant-baseline="central" font-size="11" font-family="var(--font-sans)" font-weight="500" fill="[TITLE_COLOUR]">Stage 1</text>
  <text x="130" y="54" text-anchor="middle" dominant-baseline="central" font-size="10" font-family="var(--font-sans)" fill="[SUB_COLOUR]">Find &amp; Verify</text>

  <!-- Stage 2: Company Overview -->
  <rect x="210" y="20" width="120" height="48" rx="8" fill="[STATE_FILL]" stroke="[STATE_STROKE]" stroke-width="[STATE_SW]"/>
  <text x="270" y="38" text-anchor="middle" dominant-baseline="central" font-size="11" font-family="var(--font-sans)" font-weight="500" fill="[TITLE_COLOUR]">Stage 2</text>
  <text x="270" y="54" text-anchor="middle" dominant-baseline="central" font-size="10" font-family="var(--font-sans)" fill="[SUB_COLOUR]">Co. Overview</text>

  <!-- Stage 3: Credit Decisioning -->
  <rect x="350" y="20" width="120" height="48" rx="8" fill="[STATE_FILL]" stroke="[STATE_STROKE]" stroke-width="[STATE_SW]"/>
  <text x="410" y="38" text-anchor="middle" dominant-baseline="central" font-size="11" font-family="var(--font-sans)" font-weight="500" fill="[TITLE_COLOUR]">Stage 3</text>
  <text x="410" y="54" text-anchor="middle" dominant-baseline="central" font-size="10" font-family="var(--font-sans)" fill="[SUB_COLOUR]">Decisioning</text>

  <!-- Stage 4: Approve and Onboard -->
  <rect x="490" y="20" width="120" height="48" rx="8" fill="[STATE_FILL]" stroke="[STATE_STROKE]" stroke-width="[STATE_SW]"/>
  <text x="550" y="38" text-anchor="middle" dominant-baseline="central" font-size="11" font-family="var(--font-sans)" font-weight="500" fill="[TITLE_COLOUR]">Stage 4</text>
  <text x="550" y="54" text-anchor="middle" dominant-baseline="central" font-size="10" font-family="var(--font-sans)" fill="[SUB_COLOUR]">Approve &amp; Onboard</text>

  <!-- Legend -->
  <rect x="70"  y="84" width="10" height="10" rx="2" fill="#EAF3DE" stroke="#3B6D11" stroke-width="1"/>
  <text x="84"  y="93" font-size="10" font-family="var(--font-sans)" fill="var(--color-text-secondary)">Complete</text>
  <rect x="152" y="84" width="10" height="10" rx="2" fill="#E6F1FB" stroke="#185FA5" stroke-width="1"/>
  <text x="166" y="93" font-size="10" font-family="var(--font-sans)" fill="var(--color-text-secondary)">Active</text>
  <rect x="218" y="84" width="10" height="10" rx="2" fill="var(--color-background-secondary)" stroke="var(--color-border-tertiary)" stroke-width="1"/>
  <text x="232" y="93" font-size="10" font-family="var(--font-sans)" fill="var(--color-text-secondary)">Pending</text>
</svg>
```

---

## Stage 1 - Find and Verify Company

**Purpose:** Resolve the user's input to a canonical, verified company record with a DUNS.
Check whether the company already exists in the portfolio.

**Inputs:** Company name, country, or DUNS (if provided directly)

**Tool call sequence:**

1. If user provides a DUNS directly: skip `fa_search_tool`, proceed to tool call 3.
2. If user provides only a company name: call `fa_search_tool` with name and country.
   Then apply the match-resolution rules below before proceeding.
3. Call `query_portfolio` with the resolved DUNS to check whether the company already
   exists in the portfolio and retrieve any current account data.

**Match-resolution rules (applied after `fa_search_tool` returns):**

- **Exactly one high-confidence match:** proceed automatically with that DUNS. No pause.
- **No matches:** report that no record was found. Ask the user to verify the company
  name spelling, provide a country, or supply the DUNS directly. Do not proceed to Stage 2.
- **Multiple matches or any match with lower confidence:** present the full candidate list
  as a numbered table. **This is the only permitted pause point in Stage 1.**

**Multiple-match table - format:**

| # | Company Name | DUNS | Country | City | Status | Confidence |
|---|---|---|---|---|---|---|
| 1 | [name] | [duns] | [country] | [city] | [active/inactive] | [High/Medium/Low] |
| 2 | ... | ... | ... | ... | ... | ... |

Include all candidates returned by `fa_search_tool`. Do not pre-filter or auto-select.

**Selection prompt (use this exact wording):**

> "I found several companies that match your search. To make sure we're working with
> the right one, could you help me confirm the correct entity?
>
> You can do so by:
> - Entering the **row number** from the table above (e.g. `2`), or
> - Providing the **DUNS number** directly if you have it to hand (e.g. `123456789`).
>
> Once confirmed, I'll continue with the onboarding."

**Hard stop - do not proceed to tool call 3 until the user has made a selection.**
Once the user responds, resolve their input:
- If they entered a row number: use the DUNS from that row.
- If they entered a DUNS: confirm it matches one of the candidates, then use it.
- If the input is ambiguous or does not match any row/DUNS: ask once more. If still
  unresolved after one re-prompt, stop and advise the user to provide the DUNS directly.

**Required outputs:**

- Resolved company name (as returned by D&B)
- DUNS number
- Country of registration
- Portfolio status: **existing** (company is already in portfolio) or **new** (not yet present)
- If existing: brief summary of current portfolio record (account type, risk level, outstanding)

**Narrative:** Confirm the company was identified. State name, DUNS, and country. Note
whether this is an existing portfolio customer or a new onboarding. If multiple candidates
were returned, state which row or DUNS the user selected and confirm the chosen entity.

**Failure condition:** If the company cannot be resolved to a single confirmed record, stop
and request clarification. Do not proceed to Stage 2 with an unresolved entity.

---

## Stage 2 - Company Overview

**Purpose:** Retrieve and present an executive-level snapshot of the resolved company using
the D&B company report combined with portfolio data. This summary feeds Stage 3 decisioning
and forms the basis of the final decision document.

**Inputs:** Resolved DUNS and portfolio status from Stage 1.

**Tool call sequence:**

1. Call `get_company_report` with the resolved DUNS to pull the full D&B report.

2. Render the Executive Summary table below using data from the `get_company_report` response.

3. If ownership structure is relevant (large exposure, complex corporate structure, or
   user request): call `get_company_ownership_tree` with the DUNS and include a brief
   ownership note in the Executive Summary.

**Executive Summary - render this as the Stage 2 output:**

| Field | Value |
|---|---|
| Company Name | [from report] |
| DUNS | [resolved DUNS] |
| Country | [country of registration] |
| Industry | [industry / SIC code] |
| Business Vintage | [years in business] |
| Registration Status | [active / inactive / other] |
| Overall Business Risk | [rating + class - plain-language descriptor] |
| Max Credit Recommendation | [amount + currency] |
| PAYDEX / Payment Score | [score + descriptor] |
| Failure Score | [score + class] |
| Delinquency Score | [score + class] |
| Bankruptcy Present | [Yes / No] |
| Key Legal Flags | [suits / liens / judgments - or "None"] |
| Total Outstanding (portfolio) | [from query_portfolio - or "N/A - not in portfolio"] |
| Total Past Due (portfolio) | [from query_portfolio - or "N/A - not in portfolio"] |
| Credit Limit Utilisation | [% - from query_portfolio - or "N/A - not in portfolio"] |

Render each field using the active language layer loaded at Step 2.5 of the master skill.
Translate score codes to plain-language descriptors before surfacing them to the user.
Mark any unavailable field as "N/A - not available" with a brief reason.

**Required outputs:**

- Formatted Executive Summary table (all fields above)
- Entity ID from `query_portfolio` (internal - pass to Stage 3; do not surface to user)
- Data gaps clearly identified
- Ownership note (if `get_company_ownership_tree` was called)

**Narrative:** Present the Executive Summary. Highlight the two or three most significant
risk signals. Note any data gaps and their impact on decisioning confidence.

**Failure condition:** If `get_company_report` / `get_live_report` fails after one retry,
fall back to `query_portfolio` data only and annotate the gap. Do not fabricate report data.

---

## Stage 3 - Credit Decisioning

**Purpose:** Run the configured credit decisioning model against the resolved company and
requested exposure to produce a formal credit decision: Approved, Declined, or Review.

**Inputs:** Resolved DUNS, Entity ID from Stage 2, enrichment data from Stage 2, requested
credit amount (if provided by user), and currency.

**Tool:** `application_decisioning_tool` - used for all onboarding decisioning,
whether the company is new or existing in the portfolio.

**Tool call sequence:**

1. Call `application_decisioning_tool` with:
   - DUNS (required)
   - `credit_limit` (if provided by user; omit if not specified)
   - `currency` (if provided; default to portfolio currency if not specified)
2. Parse the response for:
   - Decision status: `Approved`, `Declined`, or `Review`
   - Approved credit limit (if applicable)
   - Decision narrative and rule conditions triggered
   - Any flags or conditions attached to the decision

**Fallback - if decisioning tool fails:**

If `application_decisioning_tool` fails after one retry:

1. Document the failure.
2. Fall back to `query_portfolio` risk data (OBR, MCR, failure score, delinquency score)
   from Stage 2.
3. Produce a manual decision guidance output based on the available risk signals.
4. Clearly label the output as "Manual Guidance - automated decisioning unavailable."
5. Do not present manual guidance as an equivalent to a formal decisioning tool output.

**Decision outcomes:**

| Outcome | Meaning | Next action |
|---|---|---|
| Approved | Company meets credit criteria - credit limit granted | Proceed to Stage 4; save to Approved folder |
| Declined | Company does not meet credit criteria | Proceed to Stage 4; save to Declined or High Risk folder |
| Review | Insufficient certainty for auto-decision - human review required | Proceed to Stage 4; save to Under Review folder; generate escalation brief |

**Required outputs:**

- Decision status (Approved / Declined / Review)
- Approved credit limit and currency (if Approved)
- Decision narrative from the decisioning tool
- Rule conditions that triggered the decision
- If Review: escalation brief with the specific question(s) a human reviewer must answer

**Narrative:** State the decision clearly. Explain what rules or risk signals drove the
outcome. If Approved, confirm the credit limit. If Declined, name the primary reason. If
Review, state what is unresolved and what the reviewer needs to decide.

**Failure condition:** If decisioning fails and manual guidance cannot be produced from
available risk data, stop and advise the user that decisioning is unavailable and manual
review is required.

---

## Stage 4 - Approve and Onboard

**Purpose:** Approve the onboarding decision and place the entity into the correct portfolio
folder so that it can be monitored, tracked, and actioned by the credit team.

**Inputs:** Decision outcome from Stage 3, resolved DUNS, entity identity from Stage 1.

**Tool call sequence:**

1. Call `manage_folder` with action `LIST` to retrieve the current list of portfolio folders.
2. Based on the Stage 3 decision outcome, identify the appropriate target folder:

   | Decision | Suggested folder |
   |---|---|
   | Approved | "Approved Customers" (or equivalent active customer folder) |
   | Declined | "Declined" or "High Risk" |
   | Review | "Under Review" or "Pending Review" |

3. If an appropriate folder exists: call `manage_folder` with action `COPY` or `MOVE` to
   place the entity in that folder.
4. If no appropriate folder exists: call `manage_folder` with action `CREATE` to create
   the folder, then call `COPY` or `MOVE` to place the entity.
5. Confirm placement with a `LIST_ENTITY` call if needed to verify the entity appears in
   the target folder.

**Required outputs:**

- Target folder name
- Confirmation that the entity was successfully placed in the folder
- Folder action taken (created new / moved to existing)

**Narrative:** Confirm where the entity has been filed. State the folder name and the
reason for that classification. If a new folder was created, note it.

**Failure condition:** If folder operations fail, document the failure and advise the user
that the entity was not placed in a folder. Do not retry indefinitely - one retry per action.

---

## Handoff Contracts

| Handoff | Payload |
|---|---|
| Stage 1 -> Stage 2 | Resolved company name, DUNS, country, portfolio status (existing/new), portfolio summary if existing |
| Stage 2 -> Stage 3 | Executive Summary table, Entity ID (internal), OBR, MCR, PAYDEX, failure score, delinquency score, outstanding amounts, legal flags, ownership summary, data gaps |
| Stage 3 -> Stage 4 | Decision status (Approved/Declined/Review), credit limit (if Approved), decision narrative, rule conditions, escalation brief (if Review) |
| Stage 4 -> Output | Final decision document, folder placement confirmation, complete audit trail |

---

## Final Output - Decision Document

The onboarding output must include all of the following:

1. **Company snapshot:** Name, DUNS, country, industry, business vintage, registration status.
2. **Risk summary:** OBR, MCR, PAYDEX, failure score, delinquency score - with plain-language
   context for each. Note any legal flags (bankruptcy, suits, liens, judgments).
3. **Ownership summary:** If ownership tree was pulled, summarise the corporate structure and
   note any significant parent entities.
4. **Credit decision:** Approved / Declined / Review - with the credit limit (if Approved)
   and the primary reasons for the decision.
5. **Portfolio placement:** Folder the entity was saved to and why.
6. **Escalation brief (if Review):** The specific question(s) requiring human judgment, the
   two possible paths forward, and who should own the decision.
7. **Audit trail:** Complete log of every stage, tool called, data retrieved, gaps noted,
   and decisions made.

---

## Known Tool Integration Notes

| Tool | Issue | Handling |
|---|---|---|
| `fa_search_tool` | May return multiple candidates for common company names | Present a selection table; ask user to confirm. Do not auto-select when confidence is ambiguous. |
| `query_portfolio` | Returns multiple accounts per DUNS when a company has more than one credit file | Aggregate outstanding and past due across all accounts. Retain account-level split for the final output. |
| `get_live_report` | Used only for companies not yet in the portfolio - pulls current D&B data without requiring a prior portfolio entry | Call in place of `get_company_report` for new onboardings where no portfolio record exists |
| `get_company_report` | Use for companies already in portfolio where a D&B report was purchased | Do not call if the portfolio already contains all required fields - avoid unnecessary report pulls |
| `application_decisioning_tool` | Requires DUNS; `credit_limit` and `currency` improve decision quality but are not always mandatory | Always pass requested credit amount if the user provided one |
| `manage_folder` | `LIST` must be called before `COPY` or `MOVE` to identify valid target folders | Never assume folder names - always LIST first |
| `get_company_ownership_tree` | Optional at Stage 2; recommended for large exposures or complex structures | Call when: exposure exceeds MCR, corporate structure appears complex, or user requests it |

---

## Behavioural Requirements (Onboarding-specific)

- Never make a binding credit approval or decline. The decisioning tool output is a
  recommendation - the credit manager retains final authority.
- Missing data from Stage 2 must be annotated and carried forward into the final
  decision document and audit trail.
- Do not call `aging_forecast` in this pipeline - aging forecast is a separate workflow.
- Do not call `query_alerts` in this pipeline - alerts are a separate workflow.
- The pipeline runs autonomously. The only permitted pause points are:
  1. Stage 1: multiple unresolvable company candidates
  2. Stage 3: Review outcome requiring human escalation brief


