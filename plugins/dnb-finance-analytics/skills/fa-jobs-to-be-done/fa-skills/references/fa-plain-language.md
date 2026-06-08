# FA Plain-Language Output Layer

**Loaded by:** `SKILL.md` (master skill) - applies to every FA workflow when no
specific persona is detected.

**Purpose:** Translate FA tool outputs and analyst terminology into clear, plain business
language that any stakeholder can read and act on - no credit, financial, or technical
background required.

This file does not change what the pipeline does or what data is collected. It governs
only how results are communicated to the user.

---

## Core Principle

Every output has two audiences: the person reading it right now, and an analyst who may
review it later. Write for the person reading it right now.

**Rule:** If a phrase requires domain knowledge to interpret, replace it. If a number
requires context to be meaningful, add that context. If a status code or internal label
is surfaced raw, translate it.

---

## Tone and Voice

| Instead of... | Say... |
|---|---|
| Formal, passive, process-heavy | Direct, active, outcome-focused |
| "The entity has been added to the portfolio." | "We've added this company to your monitored accounts." |
| "Initiating decisioning workflow." | "We're now running the credit decision for this company." |
| "No adverse signals detected." | "No issues or concerns were found for this company." |
| "Tool call failed; annotating gap." | "We couldn't retrieve [specific data] at this step - we've noted it and continued." |
| "Proceeding to Stage N." | "Next, we'll [describe what happens next in plain terms]." |
| "OBR = Moderate risk." | "Overall business risk is moderate - there are some factors worth monitoring." |

**Voice attributes:** Confident, clear, non-jargon. Never condescending. Never
over-explain - one sentence of context is usually enough.

---

## Term Translations

Apply these translations consistently in all narrative output.

### Entity and Status Terms

| FA / system term | Plain-language replacement |
|---|---|
| Entity | Company |
| DUNS / D-U-N-S | [Company name] - use the name; surface the number only if asked |
| Portfolio | Your monitored accounts / customer list |
| Account | Customer account |
| `ACCOUNT` credit file type | Customer Account |
| `APPLICATION` credit file type | Credit Application |
| `DUNSRIGHT` credit file type | Live Company Data |
| `SNAPSHOT` credit file type | Historical Snapshot |
| Onboard / onboarded | Added to your accounts / brought into your system |
| Entity ID / Account ID | [Do not surface - use internally only] |
| Named principal | Director, officer, or key owner |

### Risk Scores and Ratings

| FA / system term | Plain-language replacement |
|---|---|
| Overall Business Risk (OBR) | Overall Business Risk - a summary of how risky this company is |
| OBR = Low risk | [OK] Low risk - no significant concerns identified |
| OBR = Low-Moderate risk | Low-Moderate risk - a few minor factors to be aware of |
| OBR = Moderate risk | [Monitor] Moderate risk - some factors to monitor before extending credit |
| OBR = Moderate-High risk | Moderate-High risk - notable concerns that should influence the credit decision |
| OBR = High risk | [High] High risk - significant concerns require attention before extending credit |
| OBR = Severe risk | [High] Severe risk - do not extend credit without thorough review |
| MCR / Maximum Credit Recommendation | Maximum Credit Recommendation - the highest credit limit D&B recommends for this company |
| PAYDEX | Payment Reliability Score - how consistently this company pays its bills |
| Failure Score | Risk of this company going out of business in the next 12 months |
| Delinquency Score | Risk of this company falling seriously behind on payments |
| Viability Score | Overall business health and survival likelihood |
| D&B Rating | D&B's overall rating combining financial size and creditworthiness |
| SSI (Supplier Stability Index) | Stability score - how likely this company is to remain in business |
| SER (Supplier Evaluation Risk) | Supplier risk rating |

### Credit and Financial Terms

| FA / system term | Plain-language replacement |
|---|---|
| Credit limit | The maximum credit amount to extend to this company |
| Total outstanding | Total amount currently owed by this company |
| Total past due | Amount overdue - not yet paid past the due date |
| Credit limit utilisation | How much of the allowed credit limit is currently in use |
| MCR | Maximum Credit Recommendation |
| Total Exposure | Total amount at risk if this company were to stop paying |
| Net worth | What the company owns minus what it owes |
| Current assets | Assets the company can turn into cash quickly |
| Current liabilities | Short-term debts due within the next year |
| PAYDEX < 50 | This company tends to pay significantly late |
| PAYDEX 50-79 | This company generally pays within or slightly beyond terms |
| PAYDEX 80+ | This company is a reliable, on-time payer |
| Days Beyond Terms (DBT) | Average number of days late on payments |
| Quick Ratio | Whether the company can pay its immediate debts without selling assets |

### Legal and Public Record Terms

| FA / system term | Plain-language replacement |
|---|---|
| Suit / suit filed | Court case filed against the company |
| Lien | A legal claim on the company's assets, often for unpaid debt |
| UCC filing | A lender has formally registered a claim on company assets |
| Judgment | A court ruling that the company owes money it has not paid |
| Bankruptcy present | The company has filed for bankruptcy - a serious financial warning sign |
| `db_bankruptcy_present = true` | This company has an active or recent bankruptcy filing |
| Public records | Official legal and court filings on record for this company |

### Decisioning Terms

| FA / system term | Plain-language replacement |
|---|---|
| Approved | [OK] Approved - credit can be extended based on current data |
| Declined | [High] Declined - credit is not recommended based on current data |
| Review | [Review] Human review needed - some factors require a decision before proceeding |
| Decisioning | Credit Decision process |
| Account decisioning | Running a credit decision for a customer account |
| Application decisioning | Running a credit decision for a credit application |
| CLM model | Credit decision model |

### Aging Forecast Terms

| FA / system term | Plain-language replacement |
|---|---|
| Aging forecast | Predicted Payment Timeline - when payments are expected based on ML modelling |
| Aging bucket | Payment timing category (e.g. current, 1-30 days overdue) |
| 91-120 days | Significantly overdue - high risk of non-payment |
| 120+ days | Severely overdue - collections action likely required |
| Entity ID (UUID) | [Do not surface - use internally only] |
| Account ID | [Do not surface - use internally only] |

### Alerts Terms

| FA / system term | Plain-language replacement |
|---|---|
| Alert severity = High | Urgent - requires immediate attention |
| Alert severity = Medium | Review this soon - action may be needed |
| Alert severity = Low | Informational - monitor but no immediate action required |
| Unread alert | New alert - not yet reviewed |
| Read alert | Previously reviewed alert |

### Portfolio and Folder Terms

| FA / system term | Plain-language replacement |
|---|---|
| Folder | Portfolio group or category |
| manage_folder: MOVE | Moving this company to [folder name] |
| manage_folder: COPY | Adding this company to [folder name] |
| manage_folder: CREATE | Creating a new group called [folder name] |
| manage_folder: LIST | Checking existing portfolio groups |

### Technical / Process Terms

| FA / system term | Plain-language replacement |
|---|---|
| Tool call / API call | [Do not surface - describe what was done, not how] |
| MCP tool | [Do not surface - describe the underlying action] |
| Stage N | [Use the stage name, not the number] |
| Pipeline | The steps we follow to assess a company |
| FA MCP server | [Do not surface - describe the capability] |

---

## Numeric Context Rules

Raw numbers without context are meaningless to a non-analyst. Always add one sentence
of context when surfacing scores, counts, or financial figures.

| Data point | Contextualise it like this |
|---|---|
| PAYDEX = 80 | "Payment Reliability Score: 80 out of 100 - this is a good score, suggesting the company generally pays on time." |
| PAYDEX = 45 | "Payment Reliability Score: 45 out of 100 - this is below average, suggesting the company tends to pay late." |
| Failure probability = 2.3% | "There is roughly a 2 in 100 chance of this company going out of business in the next year - this is a low level." |
| Failure probability = 18% | "There is an 18 in 100 chance of this company going out of business in the next year - this is an elevated level." |
| MCR = \$250,000 | "Based on D&B's assessment, the maximum recommended credit for this company is \$250,000." |
| Total outstanding = \$120,000 | "This company currently owes \$120,000 in your accounts." |
| Past due = \$35,000 | "\$35,000 of that is overdue - not yet paid past the due date." |
| Credit utilisation = 92% | "This company is using 92% of their allowed credit limit - leaving very little headroom." |
| Aging forecast: 31-60 days bucket increasing | "The model predicts that more of what is owed will fall into the 31-60 day overdue category next month - a sign of slowing payments." |

---

## Status Summaries - Required Format

At the top of every stage output, render a plain-language status block before any
detail. Format:

> **What we did:** [One sentence describing the action taken]
> **What we found:** [One sentence stating the key result]
> **What it means:** [One sentence of plain-English interpretation]
> **What happens next:** [One sentence describing the next step]

**Example - Credit Validation:**
> **What we did:** We looked up this company's credit file and risk data.
> **What we found:** The company has a Moderate risk rating and a maximum recommended credit of \$500,000.
> **What it means:** The requested \$200,000 is well within the recommended limit, with no outstanding past-due amounts.
> **What happens next:** We'll show you the full credit validation summary.

**Example - Aging Forecast:**
> **What we did:** We ran a payment timing forecast for this account using the ML model.
> **What we found:** Payments are predicted to remain stable, with the majority expected to stay in the current or 1-30 day buckets.
> **What it means:** No major payment deterioration is expected over the next month.
> **What happens next:** Here is the detailed breakdown by payment timing category.

---

## No-Result and Error Handling - Plain Language

Never surface raw system errors or empty-state codes. Translate them.

| System state | What to say |
|---|---|
| Tool returned empty / null | "We weren't able to retrieve [data type] for this company at this step. We've noted this and continued with the information we have." |
| Tool call failed | "We ran into a technical issue retrieving [data type]. We tried again and [succeeded / it still wasn't available - we've flagged this]." |
| No match found (company search) | "We couldn't find a confirmed record for a company matching that name. You may want to check the spelling or try providing the DUNS directly." |
| Company not in portfolio | "This company is not currently in your monitored accounts." |
| No alerts found | "There are no alerts matching your search right now." |
| No past-due amounts | "There are no overdue balances on record for this company." |
| Bankruptcy present | "This company has an active or recent bankruptcy filing - a significant warning sign for credit." |
| Entity ID not found | "We couldn't find the account identifier needed to run this forecast. Please check the account reference." |
| Aging forecast data unavailable | "The payment forecast model doesn't have enough data for this account to produce a reliable forecast." |

---

## What Never Gets Surfaced to the User

These are internal system details. They serve the pipeline; they do not belong in
user-facing output. Translate or omit entirely.

- Entity IDs (UUIDs), Account IDs, Account Numbers used as system identifiers
- Raw MCP tool names (`aging_forecast`, `query_portfolio`, `manage_folder`, etc.)
- Credit file types (`ACCOUNT`, `APPLICATION`, `DUNSRIGHT`, `SNAPSHOT`) - use plain equivalents
- `continue_report_pull` parameter details
- Stage numbers used in isolation (`Stage 2`, `Stage 3`) - always pair with the stage name
- FA MCP server connection details
- Internal confidence thresholds - express as "high confidence", "limited data", etc.
- JSON field paths (`scoring.paydex.score`, `header.duns`, etc.)

---

## Decision Outputs - Narrative Template

Every final decision output must follow this structure:

### 1. Company snapshot (2-3 sentences)

Who they are, where they are based, what they do, how long they have been in business.

### 2. What we checked

A plain list of what was assessed - risk level, payment history, financial position,
legal records, outstanding balances.

### 3. What we found - concerns

Each concern, stated plainly with its significance.

### 4. What we found - positive signals

What checked out fine - reassures the reader that the assessment was thorough.

### 5. Our recommendation

The suggested credit decision - stated in one sentence, with the primary reason.

### 6. If human review is needed: what needs a decision

State the specific question, the two options, and what each path means.

### 7. Suggested next step

One concrete action the reader can take.

---

## Credit Validation - Narrative Template

Credit validation outputs use the compact format defined in `fa-credit-validation.md`:
10-15 lines total, following the Subject / Executive Summary / Credit Assessment / Response /
Supporting Factors structure.

---

## Applying This Layer

This file is loaded once at the start of every FA workflow run. Once loaded, every piece
of output produced during that run - stage narratives, status summaries, error messages,
decision documents, and audit trail entries - must comply with these rules.

**Precedence:** Where a sub-flow file specifies a required output format (e.g. the Credit
Validation Output Template), that structure is preserved. These plain-language rules govern
the *language* used inside that structure, not the structure itself.

**Analyst detail on request:** If the user asks for more technical detail, system-level
terminology, or raw scores, provide them. This layer sets the default; it does not
prohibit depth when explicitly requested.


