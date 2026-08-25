## Recommendation output template and component mapping

Use this reference to generate the recommendation output. It defines the full output structure, section requirements, fee guidance rules, and template formatting.

### Output requirements

Output MUST include all of these sections:

- Account configuration (`dashboard`, `fees_collector`, `losses_collector`) with explicit Accounts v2 declaration, no legacy `type`
- `merchant` configuration for direct charges
- `recipient` configuration for destination or separate charges
- Charge pattern with 2-3 sentence rationale
- Seller and provider onboarding flow with onboarding method choice and rationale
- Dashboard access flow and rationale by access mechanism (`express` login links, `full` direct `dashboard.stripe.com` access, `none` embedded-components-primary interface)
- OAuth scope guidance when connecting existing Stripe accounts (only when user mentions OAuth or existing accounts; see compatibility-matrix section 4a)
- Fee structure with platform fee model, fee-payer recommendation, funds-flow diagram, and stripe.com/pricing link
- Embedded component recommendations tied to charge-pattern compatibility, with required `notification_banner` and charge-pattern caveats
- Webhook integration section (one sentence only; details deferred to build skill)
- Onboarding status gating using v2 capability paths
- Loss liability explanation separate from risk management
- Use separate headings for negative balance liability and risk management (don’t combine into one paragraph)
- For destination or separate with `losses_collector: "application"`, explain the causal chain in plain language: platform owns negative balance liability, connected-account balances can go negative when needed, and transfer reversals can be used for dispute recovery
- SaaS monetization choices (transaction fees vs recurring SaaS fees), with `customer_account` guidance only for SaaS billing connected accounts
- `application_fee_amount` explanation and calculation mode

If any section is missing, add it before moving on.

### Canonical recommendation template

```markdown
## Recommended Connect integration

### A. Account configuration
Accounts API: `/v2/core/accounts`
Legacy account `type`: not used
Dashboard: [express / full / none]
Fee collection: [Stripe / platform]
Negative balance liability: [Stripe / platform]
[2-3 sentence explanation of why these settings fit]

[Include for direct charges only:]
Each connected account needs merchant configuration (`configuration.merchant`) for direct charges.

[Include for destination or separate charges only:]
Each connected account needs recipient configuration (`configuration.recipient`) with `stripe_transfers` on `stripe_balance` requested, so the account can receive transfers from the platform.

### B. Charge pattern: [destination / direct / separate charges and transfers]
[2-3 sentence explanation of why this fits]

### C. {sellerRole} onboarding flow
Onboarding method: [embedded / Stripe-hosted]
[2-3 sentence explanation of why this method was chosen over the alternative.]

[Describe the full onboarding flow: sign up, create account, onboarding with the chosen method, Stripe verification, capability status verification, handling ongoing requirements, checking capability status on an ongoing basis. Only enable live transactions when the necessary capabilities are active.]

### D. Payments dashboard access for {sellerRole}
- If dashboard=express: explain connected accounts access the Express dashboard through platform-generated Express login links, with embedded components for in-app workflows
- If dashboard=full: explain connected accounts log in directly at `dashboard.stripe.com`
- If dashboard=none: explain connected accounts don't use Stripe Dashboard login and embedded components are the primary interface for connected accounts

### E. Embedded components
Recommended [Connect embedded components](https://docs.stripe.com/connect/supported-embedded-components):
- `account_onboarding`
- `notification_banner` [required; keeps connected accounts aware of new requirements so they stay enabled]
- `account_management`
- `payments`
- `payouts`
[Add optional standalone components only when explicitly needed]
[Note any charge-pattern caveats, if relevant]

### F. Webhook integration
Use webhooks for reliable payment confirmation, especially for async payment methods. Always verify incoming webhook signatures before processing event data ([webhook signature verification](https://stripe.com/docs/webhooks/signatures)). Specific events and implementation details are covered in the build skill.

### G. Onboarding status gating
Verify capability statuses with `stripe.v2.core.accounts.retrieve(id)` before enabling payouts and transfers:
- Direct: `configuration.merchant.capabilities.card_payments.status === 'active'`
- Destination or separate: `configuration.recipient.capabilities.stripe_balance.stripe_transfers.status === 'active'`
- Also check payouts capability status in the relevant subtree

### H. Fee structure
- Platform fee model: [percentage / flat / tiered / mixed]
- `application_fee_amount` strategy: [platform fee only | platform fee + estimated Stripe processing fee]
- [Describe the fee structure, whether customers pay the connected account (seller) or platform, whether fees are paid to Stripe or to the platform, and whether anything is transferred from the platform to the seller. Pricing varies by region or payment method — check [stripe.com/pricing](https://stripe.com/pricing).]
- [Funds flow diagram with seller or provider net amount explanation:]

   {customerRole} pays ${amount}
         │
         ▼
  ┌───────────────┐
  │  {platform}   │ ─── keeps {X}% minus processing fees
  └──────┬────────┘
         │ transfer ({amount} minus {X}%)
         ▼
  ┌───────────────┐
  │  {sellerRole} │ ─── receives {amount} minus {X}%
  └───────────────┘

### I. SaaS monetization (if applicable)
State the monetization choice clearly: transaction fees (`application_fee_amount` or Platform Pricing Tool, not both), recurring SaaS or service fees, or both when justified.
Use `customer_account` only when charging recurring SaaS or service fees to connected accounts (v2 SetupIntent/Subscription calls).
Do NOT apply `customer_account` guidance to marketplace subscription or fan-to-creator recurring-payment flows.
Do NOT recommend creating a separate v1 Customer object for SaaS billing connected accounts.

### J. Implementation plan
1. [Account setup tasks]
2. [Onboarding flow tasks]
3. [Payments and fund-flow tasks]
4. [Webhook and readiness-gating tasks]
5. [Go-live checks]

### K. Risk and liability
- Negative balance liability owner: [your platform / Stripe]
- Risk controls owner: [your platform / Stripe]
- [Any required warnings from compatibility checks]

### L. Why this fits your business
- [2-4 bullets linking business model, merchant of record, and operational constraints to the configuration choices above]

### M. Open questions
- [Any unresolved assumptions to confirm before implementation]
```

### Required wording snippets

#### Recipient configuration wording (destination or separate)

Include this wording (adapted to context) when charge pattern is destination or separate charges and transfers:

“Each connected account needs the recipient configuration (`configuration.recipient`) with `stripe_transfers` on `stripe_balance` requested, so the account can receive transfers from the platform. Marketplace connected accounts should NOT request merchant configuration or `card_payments` capability — this is unnecessary and causes longer onboarding.”

#### Webhook section guardrails

- Keep webhook section to one sentence that defers event details to the `connect-build` skill.
- Do NOT list concrete webhook event names in recommend output.
- Do NOT create a “Required Webhooks” section.
- Do NOT mention embedded components in the webhook section.

### Risk and loss liability guidance

Always present loss liability and risk management as separate concepts:

- **Loss liability** (`losses_collector`): who is financially responsible for negative balances on connected accounts.
- **Risk management**: who detects and prevents fraud (Stripe Radar vs platform-managed).

When `losses_collector: application` (platform owns loss liability), emphasize that Radar is essential — fraudulent charges that slip through come directly out of the platform’s balance. For marketplaces using destination charges, the platform is merchant of record and must manage risk.

### Fee guidance rules

- When `fees_collector: "stripe"` and using direct charges, the connected account is charged the processing fee directly. The `application_fee_amount` is in addition to that and goes directly to the platform.

- With destination or separate charges, the platform ALWAYS pays Stripe’s processing fees.

- Do NOT hardcode Stripe fee amounts (rates vary by region, card type, method, and negotiated pricing).

- Do NOT make absolute profit and loss guarantees.

- Do NOT recommend `application_fee_amount` for separate charges and transfers (instead, retain fee by transferring less than charge amount).

- Do NOT set explicit `application_fee_amount` when Platform Pricing Tool is used (doing so will override tool logic).

- Always link to [stripe.com/pricing](https://stripe.com/pricing).

- For platform-owned pricing, recommend [Platform Pricing Tool](https://dashboard.stripe.com/settings/connect/platform_pricing) and [margin report](https://docs.stripe.com/connect/margin-reports.md). Platform Pricing Tool and explicit `application_fee_amount` are mutually exclusive — don’t recommend both.

- Mention Brazil or Malaysia cross-border fee-collection constraints where relevant.

- For low flat fees on variable amounts, warn about margin compression at larger ticket sizes.

- For very small transactions, warn about currency minimums and fee-to-proceeds effects.

#### Fee output requirements

Every recommendation MUST explicitly:

- Name the `applicationFeeIncludes` value (`stripe_fee_estimate` or `platform_fee_only`) and explain what it means for the platform’s margin
- Show a funds flow diagram with the platform fee
- Recommend the single most appropriate fee approach for the scenario; explain both approaches only when the platform’s margin goal or constraints are genuinely unclear (see Funds-flow comparison guidance below)

#### Low-margin warning template

This section only applies when the platform is NOT using direct charges with Stripe-owned pricing (`fees_collector: "stripe"`). In that configuration, the connected account pays Stripe fees directly and this concern doesn’t apply.

When platform fee appears low relative to processing fees, keep this order:

1. **Warn first**: explicitly state that the selected platform fee may be below Stripe processing fees, so the platform may lose money per transaction when it absorbs fees.
2. **Show downside before fix**: include one concise illustrative example of net margin without fee passthrough (label assumptions clearly and link to [stripe.com/pricing](https://stripe.com/pricing)).
3. **Then provide the fix**: recommend margin-preserving `application_fee_amount` logic (platform fee + estimated Stripe fee) and explain why it preserves margin.
4. **Close with validation path**: link to [stripe.com/pricing](https://stripe.com/pricing) and recommend monitoring the margin report.

Suggested warning phrasing:

> **Warning:** Your platform fee may be below Stripe processing fees at standard rates. With this charge pattern, your platform pays Stripe processing fees on every transaction. If you absorb those fees, your net per transaction may be negative. Check [stripe.com/pricing](https://stripe.com/pricing) for your region and payment-method mix.

#### Funds-flow comparison guidance

**Recommend the option that fits the user’s margin goal.** Present both options only when the margin goal or constraints are genuinely unclear.

To disambiguate, ask: “Are you trying to make X% margin, or do you want your users to pay X%?” The answer determines which option to recommend.

When destination or direct flow uses `application_fee_amount`, choose guidance as follows:

- Margin-preserving recommendation: `application_fee_amount = platform fee + estimated Stripe processing fee` (still an approximation — actual rates vary by region, card type, and payment method)
- Platform-absorbs-fees recommendation: `application_fee_amount = platform fee only`
- If unclear: present both options concisely with the tradeoff and call out what assumption decides the recommendation

### Onboarding status gating details

Always include gating guidance to prevent transfers and payouts for unready accounts. `stripe_balance.payouts` is auto-requested when `card_payments` or `stripe_transfers` is requested, so do NOT explicitly request `stripe_balance.payouts` in account create/update calls.

Use:

- `configuration.merchant.capabilities.card_payments.status`
- `configuration.merchant.capabilities.stripe_balance.payouts.status`
- `configuration.recipient.capabilities.stripe_balance.stripe_transfers.status`
- `configuration.recipient.capabilities.stripe_balance.payouts.status`

Do NOT rely on v1 `charges_enabled` or `payouts_enabled` booleans for this flow.

### Embedded component template notes

The embedded components section should list the components selected during Step 4b (see SKILL.md for selection logic and charge-pattern compatibility caveats). See [Connect embedded components](https://docs.stripe.com/connect/supported-embedded-components.md) for documentation.
