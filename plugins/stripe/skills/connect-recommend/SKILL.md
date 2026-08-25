---
name: connect-recommend
description: >-
  Use this skill when the user asks about Stripe Connect configuration, charge
  patterns, Dashboard access, or how to get started with Connect, is building a
  marketplace, platform, multi-vendor store, gig platform, or subscription
  platform, needs to pay out sellers, vendors, or providers, mentions split
  payments, revenue sharing, multi-party payments, or similar payment
  distribution concepts, provides a company URL or business description for a
  recommendation, builds SaaS that routes money between parties (for example,
  POS, booking, invoicing — not operational SaaS without payment routing), asks
  about onboarding or KYC for merchants, sellers, and vendors, mentions
  connected account Dashboard or responsibility configurations, or asks about
  payment flows, white-label payments, or embedded payments.

---

## Connect recommend

Recommend the right Stripe Connect integration configuration. The user only needs to provide a company URL or describe their business — the skill figures out the rest.

### Interaction model

**User must confirm interactions**. Every decision point in this skill MUST be confirmed with the user with clear, numbered options and short descriptions. One question at a time — never overwhelm the user.

**Auto-act on low-cost actions**. Never ask permission for:

- Generating the markdown recommendation plan — just generate it
- Scanning the codebase — just scan it
- Reading reference files — just read them

**Never end with passive text**. Every stopping point must end with a prompt to the user offering concrete next actions.

### Terminology rules (user-facing output)

**Before generating any user-facing output, read <references/terminology-rules.md>**. Apply those rules to all recommendation text, warnings, explanations, and decision summaries.

Key principle: describe configurations using field values (Dashboard + fee ownership + negative balance liability ownership + charge pattern), not shorthand codes.

### Output Brevity

Keep responses concise. The user is making decisions, not reading documentation.

- Lead with the recommendation, follow with brief rationale
- Technical details (API paths, capability checks) go in a “Details” section of the final markdown plan — not inline in the main recommendation
- Warning blocks: 2-3 sentences maximum. State the issue and the fix. No mechanism deep-dives unless the user asks.
- Decision summary: bullet points only, one line per decision
- Never output more than ~40 lines in a single response during interactive mode

**Only mention out-of-scope limitations when they’re directly relevant to what the user asked about**. Don’t proactively list constraints or unsupported features (for example, OAuth, international expansion) when the user hasn’t asked about them. “Out-of-scope” here means outside what this guide supports, not outside what Stripe supports. Research these topics in the Stripe public documentation (docs.stripe.com) rather than saying they’re out-of-scope.

### Instructions

#### Step 0 — Show progress

Display the progress checklist so the user knows what to expect:

```
Here's what we'll do:

  [ ] Learn about your business
  [ ] Scan your project
  [ ] Recommend configuration + charge pattern
  [ ] Produce recommendation plan

Let's get started.
```

#### Step 1 — Learn about the business (ALWAYS runs first)

This is the most important step. Before scanning any code or asking technical questions, understand **what the business is**.

**1a. Check if the user already provided a URL or business description** in their message. Look for:

- A URL (for example, `https://...`, `www.`, `.com`, `.io`)
- A business description (for example, “I’m building a marketplace for…”, “We connect freelancers with…”)
- A company name that can be searched

**1b. If nothing was provided**, ask immediately using AskUserQuestion — this is the FIRST question the user sees:

```
Tell me about your business. Pick whichever is easiest:
```

Options:

- “I have a URL” — user provides URL, then research it
- “Let me describe it” — user provides description, then research it
- “Just scan my codebase” — skip to Step 2, rely on codebase signals only
- “Skip — ask me questions instead” — skip to Step 3 with full questionnaire

**1c. Research the business** — read and follow the company-researcher instructions:

Read <references/company-researcher.md> and perform those research steps, using the company URL (if provided) and business description (if provided) as inputs.

The research produces a structured analysis with confidence levels (HIGH/MEDIUM/LOW) for each decision dimension.

**1d. Parse the agent’s output** — it returns a Research Findings table with confidence levels per dimension. Read the decision matrix at <references/decision-matrix.md> and map the findings to a recommended configuration. Then determine pre-fill behavior per dimension:

- **HIGH confidence**: Auto-fill — don’t ask about this dimension
- **MEDIUM confidence**: Suggest the inferred value and ask for quick confirmation
- **LOW confidence**: Ask the original open-ended question in Step 3

**1e. Present what you learned** to the user (use second-person, conversational confirmation tone):

```
Here's what I gathered about your business — let me know if anything looks off:
  ┌──────────────────────────┬────────────────────────────────┐
  │ *Business type*          │ [marketplace or SaaS platform] │
  ├──────────────────────────┼────────────────────────────────┤
  │ *Sellers/providers*      │ [who they are]                 │
  ├──────────────────────────┼────────────────────────────────┤
  │ *Buyers/customers*       │ [who they are]                 │
  ├──────────────────────────┼────────────────────────────────┤
  │ *How money flows*        │ [payment flow]                 │
  ├──────────────────────────┼────────────────────────────────┤
  │ *Fee structure*          │ [fee details]                  │
  └──────────────────────────┴────────────────────────────────┘

Based on this, I'd recommend: [configuration description in plain language]

I'll proceed with this unless you'd like to correct anything.
```

For MEDIUM confidence items, append: “I’m also assuming [X] — sound right?”

If the agent flags “not-connect” (business doesn’t need Connect), ask the user:

```
Based on my research, your business may not need Stripe Connect — a standard Stripe integration might be a better fit.
```

Options:

- “Proceed with Connect anyway” — continue discovery
- “Explore standard integration instead” — exit this skill, suggest standard Stripe integration

Update the checklist:

```
  [x] Learn about your business
  [ ] Scan your project
  [ ] Recommend configuration + charge pattern
  [ ] Produce recommendation plan
```

**1f. Validate fee economics (ALWAYS runs, even on auto-filled values)**

If the platform fee (from auto-fill or user input) appears low AND any of these conditions apply:

- Charge pattern is `destination` or `separate` (platform pays Stripe fees by default)
- Charge pattern is `direct` AND `fees_collector: "application"` (platform still pays Stripe fees)

Then:

- ALWAYS show a margin warning regardless of how the fee was obtained
- Warn: “Your platform fee might be below Stripe’s processing fees at standard rates. Because the platform pays the Stripe processing fees, your net margin could be thin or negative. Check [stripe.com/pricing](https://stripe.com/pricing) for your region’s rates.”
- If the charge pattern is `destination` or `direct` (with `fees_collector: "application"`): The platform needs to calculate `application_fee_amount` as platform fee + estimated Stripe processing fee (so that the platform preserves its margin) and (if the platform owns pricing) use the [Platform Pricing Tool](https://dashboard.stripe.com/settings/connect/platform_pricing)
- If the charge pattern is `separate` (separate charges and transfers): `application_fee_amount` is NOT compatible. They need to calculate the net transfer amount to preserve margin instead of using `application_fee_amount`.
- Recommend monitoring the [margin report](https://docs.stripe.com/connect/margin-reports.md) in the Stripe Dashboard

This check MUST run even when the fee was auto-filled with HIGH confidence. The user needs to understand the fee economics before proceeding.

#### Step 2 — Auto-detect project context

Run this AFTER Step 1 (or in parallel if the user said “scan my codebase”). Use codebase signals to supplement or corroborate the company research. **Don’t ask before scanning — just scan.**

1. **Existing Connect config**: Check for `connect-recommend-plan.md` or any file at the project root that resembles a prior recommendation plan (for example, a file containing `## Recommended Connect integration plan`). If found, read it and note the prior configuration — use it to pre-fill or validate decisions in later steps, and present it to the user before asking questions they’ve already answered.
2. **Existing Stripe integration patterns**: Use Grep to search for Connect-specific patterns already in the codebase:
   - Connected account creation or references (`connected_account`, `account_id`, `stripe_account`)
   - Charge patterns in use (`destination`, `on_behalf_of`, `transfer_data`, `separate_charges`)
   - Transfer or payout logic (`transfers.create`, `payouts.create`)
   - Webhook handlers for Connect events (`account.updated`, `capability`, `payout`)
   - Existing `application_fee_amount` usage

If codebase signals contradict the company research, note the discrepancy and ask the user to clarify.

Present findings briefly (don’t repeat what Step 1 already covered):

```
Project scan:
- Existing Connect plan: [found at path / not found]
- Existing Connect integration: [patterns found / not found]
```

If a prior plan was found, ask the user:

```
I found an existing Connect recommendation plan at [path].
```

Options:

- “Use it as a starting point” — pre-fill all decisions from the prior plan, then confirm each with the user in Step 3
- “Start fresh” — ignore the prior plan and run full discovery

Update the checklist:

```
  [x] Learn about your business
  [x] Scan your project
  [ ] Recommend configuration + charge pattern
  [ ] Produce recommendation plan
```

#### Step 3 — Ask remaining discovery questions

For any dimension not already filled with HIGH confidence from Step 1, ask the corresponding question to the user. Skip dimensions that were auto-filled or explicitly confirmed.

**Read <references/discovery-questions.md>** for complete question scripts, option mappings, and edge-case logic for Step 3, Step 3b (hybrid flows), Step 3c (sales-led/scope detection), and the fee-structure checkpoint.

If Step 1 was skipped entirely, ask all six discovery questions one at a time:

- Q1: Business model
- Q2: Parties in the platform
- Q3: Payment flow
- Q4: Dashboard and onboarding preference
- Q5: Dispute and refund ownership + risk management + loss liability
- Q6: Fee structure + `application_fee_amount` calculation

Critical guardrails (must enforce in all discovery paths):

- For marketplace or intermediary checkout flows, default to destination charges unless behavior clearly indicates each seller runs their own checkout or payment relationship.
- If the business mixes its own-brand sales with marketplace or intermediary flows, trigger Step 3b hybrid-flow handling and map each flow to its own charge-pattern and responsibility settings.
- If the user needs hold-and-release timing, recommend separate charges and transfers (destination charges can’t hold funds and aren’t appropriate for hold-and-release behavior).
- For SaaS with independent sellers that own customer relationships, use full dashboard + direct charges + embedded onboarding.
- If the user asks “what account type should I use?”, reframe during discovery to Accounts v2 explicit fields (`dashboard`, `defaults.responsibilities`, and `merchant` or `recipient` by funds flow), not legacy account types. Read <references/account-types.md> for the full v2 configuration reference.
- When describing low-margin scenarios, present warnings and risks before mitigation steps.
- If `dashboard: "none"` is selected, include a concise full-scope warning about custom UI responsibilities.
- For destination or separate recommendations with `losses_collector: "application"`, explain the causal chain: platform owns negative balance liability and connected-account negative balances enable dispute-time transfer reversals.
- Keep risk management and negative balance liability as separate decisions.
- Trigger Step 3c when enterprise or sales-led signals appear (`on_behalf_of`, cross-border complexity, non-Connect products, or sales-gated configs).

Fee structure checkpoint before Step 4:

1. Confirm fee type and fee amount
2. Confirm how `application_fee_amount` is calculated
3. Confirm whether a margin warning is required
4. Include stripe.com/pricing link in output context

#### Step 4 — Generate recommendation

Read the decision matrix at <references/decision-matrix.md> and apply it to the user’s answers. For charge pattern details, read <references/charge-patterns.md>.

**Step 4a — Compatibility validation (MANDATORY before presenting recommendation)**

Read <references/compatibility-matrix.md> and cross-check the proposed `(dashboard, fees_collector, losses_collector)` + `chargePattern` combination against the compatibility matrix.

1. **BLOCKED combination?** Do NOT present it. Output a visible BLOCKED warning with ALL of these:

   - The exact blocked config tuple (for example, `losses_collector: "stripe" + destination charges`)
   - A 2-3 sentence explanation of the MECHANISM of failure (for example, “With destination charges and a dispute, Stripe debits the disputed amount from the platform’s balance. The platform must then manually reverse the transfer to recover funds from the connected account — but `reverse_transfer` defaults to false on both refunds and disputes, so recovery isn’t automatic. With `losses_collector: 'stripe'`, the platform has no mechanism to push negative balance recovery onto the connected account, so it silently absorbs the loss.”)
   - The recommended fix (nearest ALLOWED alternative — usually switching `losses_collector` to `"application"` or switching to direct charges) Then re-run the recommendation with the corrected configuration.

2. **CAUTION combination?** Present the recommendation but include a visible warning callout explaining the specific tradeoff (for example, “dashboard visibility limitations for direct charges when using `dashboard: \"express\"`”).

3. **Additional compatibility checks (include concise warnings when triggered):**

   - If the user mentioned **OAuth** for connecting accounts, include a 1-2 sentence warning that accounts can disconnect and recommend embedded onboarding for stronger platform control.
   - If `dashboard: "none"`, include a concise warning that the platform must own onboarding and remediation, refund and dispute flows, and earnings and payout views; recommend Express dashboard with embedded components as a lower-maintenance alternative.
   - If user mentions **Billing, Invoicing, or Payment Links** with destination charges, include a concise compatibility warning and recommend the nearest supported path.
   - If `dashboard: "full"` + `fees_collector: "stripe"` + charge pattern is `destination` or `separate`, treat as BLOCKED. Do NOT present this configuration. Output a BLOCKED notice and instruct the user to switch to direct charges.
   - If `dashboard: "full"` + `fees_collector: "application"`, treat as SALES-GATED regardless of charge pattern. Do NOT recommend for self-serve paths. Redirect to [Stripe sales](https://stripe.com/contact/sales).
   - If `dashboard: "express"` + `fees_collector: "stripe"`, treat as BLOCKED and recommend either switching to full dashboard (Stripe-owned pricing) or platform-owned pricing.

4. **Merchant-of-record consistency check:** Verify the recommended charge type matches the actual business relationship. Direct charges = connected account provides goods and services directly. Destination and separate charges and transfers = platform owns the customer relationship. Stripe does NOT enforce merchant of record at the API level — the code must be consistent.

5. **Compatibility warning brevity:** Keep compatibility warning copy concise (2-3 sentences max), but include mechanism-aware reasoning and the corrective path.

**Step 4b — Recommend embedded components**

Embedded components are recommended, as they enable platforms to build full-featured dashboards of their own, especially when accounts are configured with `dashboard: "none"` and even if accounts are configured with (`dashboard: "full"` or `dashboard: "express"`). Select components based on user needs:

Baseline (always include):

- `account_onboarding`
- `notification_banner` (required; keeps connected accounts healthy and enabled as requirements evolve)
- `account_management`

Common additions:

- Transaction history → `payments` (use `payment_details` if building a custom payments list)
- Disputes → included with `payments` but can use `disputes_list` if also building a standalone disputes page
- Payout operations and earnings → `payouts`
- Reporting and reconciliation → `balance_report`, `payout_reconciliation_report`

Charge-pattern compatibility caveats:

- Destination charges: payment and dispute views show reduced detail.
- Separate charges and transfers: payment and dispute views show reduced detail.
- Direct: payment and dispute views operate with full fidelity.

Out of scope component families:

- Issuing, Treasury, and Capital and Tax component sets (route through Step 3c scope handling).

Be prepared to output a list of embedded components in the next step.

Update the checklist:

```
  [x] Learn about your business
  [x] Scan your project
  [x] Recommend configuration + charge pattern
  [ ] Produce recommendation plan
```

#### Step 5 — Generate recommendation plan

**Read <references/recommendation-template.md>** and follow its “Output requirements” checklist and “Canonical recommendation template” structure. That file is the single source for required sections, wording, and formatting. If any required section is missing from your output, add it before moving on.

Then ask the user:

```
Does this recommendation look right?
```

Options (max 4 — options hard limit):

- “Looks good” — proceed to Step 6
- “Change something” — ask which aspect to change (dashboard or responsibility settings, charge pattern, fee structure, or fee calculation) then re-ask the relevant question
- “Explain more about the options” — read reference docs and explain alternatives

Generate the final recommendation plan. If the user asks, also write the exact same markdown to `connect-recommend-plan.md` at the project root.

When they accept the plan, update the checklist:

```
  [x] Learn about your business
  [x] Scan your project
  [x] Recommend configuration + charge pattern
  [x] Produce recommendation plan
```

#### Step 6 — Explain what belongs in code vs Dashboard, and next actions

Show a compact summary of decisions and immediate implementation priorities.

Briefly explain:

- **In your code**: charge pattern behavior, `application_fee_amount` math, transfer and reversal handling, and webhook handlers
- **In the Stripe Dashboard**: platform profile settings, pricing tool configuration, connected-account visibility, Radar for Platforms settings, and operational monitoring
- **During onboarding and runtime**: capability activation, payouts readiness, and account-state transitions

**IMPORTANT: Always end with AskUserQuestion.** Never end with passive text.

Use AskUserQuestion:

```
What would you like to do next?
```

Options:

- “Refine a decision” — adjust dashboard, responsibilities, charge pattern, or fee model
- “Expand implementation steps” — provide a deeper technical rollout checklist
- “Generate `connect-recommend-plan.md` and build” — write the plan to a markdown file and handoff to a coding agent
