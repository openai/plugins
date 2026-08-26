## Discovery questions and decision mappings

Use this reference when running Step 3 discovery. It contains the full user interaction scripts, option mappings, and edge-case logic.

### Step 3 — Ask remaining discovery questions

For any dimension NOT already filled with HIGH confidence from Step 1, ask the corresponding question using AskUserQuestion. Skip questions that were auto-filled. For MEDIUM confidence items where the user confirmed the suggestion, skip those too.

If Step 1 was skipped entirely (user chose “ask me questions instead”), ask all 6 questions one at a time as below. Each question uses AskUserQuestion with clear options.

If the user asks “what account type should I use?” (or similar), reframe during discovery before recommending settings: Accounts v2 uses explicit fields (`dashboard`, `defaults.responsibilities`, and `merchant`/`recipient` by funds flow), not the legacy `type` parameter.

#### Q1: Business model (skip if auto-filled)

Ask the user:

```
What best describes your business?
```

Options:

- “Marketplace (buyers + sellers, for example Etsy, Airbnb)”
- “Platform with service providers (for example Uber, DoorDash)”
- “SaaS enabling payments (for example Shopify, Squarespace)”
- “Crowdfunding, subscription, or other model”

#### Q2: Who are the parties? (skip if auto-filled)

Based on Q1, ask the user:

```
Who are the two sides of your platform?
```

Options (adapted to Q1 answer):

- “Platform + independent sellers”
- “Platform + service providers/contractors”
- “Platform + creators/hosts”
- “Platform + businesses (B2B)”

#### Q3: Payment flow (skip if auto-filled)

Ask the user:

```
How should money flow through your platform?
```

Options:

- “Platform collects, then pays out to sellers automatically (typical marketplace flow)”
- “Buyers pay sellers directly, platform takes a fee”
- “Platform processes payments on behalf of sellers”
- “Platform holds funds, releases to sellers after delivery/confirmation”

Resolving ambiguous payment flow signals: Use the plain-language merchant-of-record definition from the terminology rules: ask who the customer thinks they paid (name on receipt or statement and who handles payment support issues such as refunds and disputes).

**Critical disambiguation rule:** Distinguish payout expectations from checkout ownership. Language like “payments associated with sellers,” “payments belong to sellers,” or “payments tied to their account” usually means sellers should receive their share. That is a payout expectation, not a direct-charge requirement, and destination charges satisfy it through automatic transfers.

When the user’s description contains conflicting signals (for example, “payments should be associated with the seller” but “my platform provides the checkout flow”), treat “platform-provided checkout, booking, or listing UI” as the stronger signal for marketplace flows and default to destination charges. The platform is acting as an intermediary in the customer checkout flow.

Choose direct charges when the behavior matches SaaS enablement: each seller runs their own payment relationship, customers pay the seller directly, seller branding appears on receipts and statements, and seller-side operations handle payment support, refunds, and disputes. Users don’t need to explicitly use merchant-of-record terminology for this to apply.

Hold-and-release detection: If the user selects “Platform holds funds, releases to sellers after delivery/confirmation” OR the business description mentions any of: delivery confirmation before payout, hold-and-release, release on completion, manual transfer trigger, multiple sellers per checkout, or shipping with delayed payout, recommend separate charges and transfers. Destination charges transfer funds automatically upon payment success and can’t hold funds. For hold-and-release, the charge is created on the platform (no `transfer_data`), the platform holds funds in its own balance, and after delivery or service confirmation the platform creates a transfer to the connected account.

Don’t describe destination charges as “holding funds before release” or “initiating transfers after delivery” — that language applies only to separate charges and transfers.

B2B enterprise carve-out: For B2B enterprise platforms with complex billing, multi-vendor purchase orders, or independent settlement timing, prefer separate charges and transfers over destination charges. B2B platforms often need per-vendor invoicing, partial payments, and independent settlement timing that destination charges can’t support. If the user’s needs exceed typical automated patterns (complex multi-vendor billing, purchase orders), trigger Step 3c (sales-led detection).

#### Q4: Dashboard and onboarding (skip if auto-filled or confirmed)

Ask the user:

```
What level of Stripe access should your sellers/providers have?
```

Options:

- “Lightweight Express dashboard — simple view of earnings/payouts (recommended)”
- “Full Stripe dashboard — sellers manage their own Stripe account independently”
- “No dashboard — fully embedded or white-labeled in my platform”

Map answers to v2 config:

- “Lightweight Express” → `dashboard: "express"`, `onboardingMethod: "embedded"`
- “Full Stripe dashboard” → `dashboard: "full"`, `onboardingMethod: "embedded"`
- “No dashboard” → `dashboard: "none"`, `onboardingMethod: "embedded"`

When selecting `dashboard: "none"`, include this warning:

```
WARNING: dashboard: none — Full Scope Warning:
- You must build custom onboarding and ongoing remediation logic (higher operational overhead than embedded/hosted)
- You must build refund management UI (connected accounts have no Stripe dashboard)
- You must build dispute management flows (connected accounts can't manage disputes themselves)
- You must build earnings/payout views for sellers
Consider embedded components as a middle ground for less maintenance.
```

Dashboard access for sellers or providers:

- Express dashboard: provide sellers an Express login link from `stripe.accounts.createLoginLink(accountId)`.
- Full Stripe dashboard: direct sellers to log in at [dashboard.stripe.com](https://dashboard.stripe.com).
- No dashboard: platform uses embedded components or custom UI backed by Stripe API data.

Dashboard selection logic:

- **`dashboard: "full"`** when any of these apply:
  - Sellers or providers “run their own business” or “want independence”
  - SaaS-with-payments model
  - Businesses described as established or enterprise
  - Direct charges pattern
  - User asks for full dashboard / independent account management
  - Fees and losses are both Stripe-managed
- **SaaS-with-payments critical rule:** If the business is SaaS enabling independent sellers to accept payments and sellers are independent, use `dashboard: "full"`, `chargePattern: "direct"`, and `onboarding: "embedded"`.
- **`dashboard: "express"`** when any of these apply:
  - Sellers or providers are individual or less technical
  - Marketplace model with platform-owned checkout
  - Destination charges pattern
  - User wants a lightweight dashboard for sellers
  - Cobranding benefit is desired
- **`dashboard: "none"`** when white-label or fully embedded control is required.

Non-technical user language (“not tech savvy”) is a supporting signal, not a standalone override. It should reinforce a marketplace recommendation (`dashboard: "express"`), but it doesn’t override SaaS classification when sellers are independent businesses that own customer payment relationships.

When recommending, always explain why:

- Express: cobranded seller dashboard with minimal maintenance.
- Full: independent seller control over payments, refunds, and payouts.
- None: white-labeled UX; platform owns all seller UI views (or uses embedded components).

#### Q5: Dispute and refund responsibility (skip if auto-filled or confirmed)

Ask the user:

```
Who handles disputes and refunds?
```

Options:

- “Platform handles disputes and refunds”
- “Sellers handle their own disputes”
- “Shared responsibility”

#### Q5b: Risk and fraud management (conditional on Q1 answer)

There are two risk types: transactional risk (fraudulent payments and chargebacks) and merchant fraud. They can be managed independently.

Key principle: recommend Stripe-managed risk when possible. See the “Risk Management by Business Model” section in `decision-matrix.md` for detailed context.

If Q1 = Marketplace:

- Explain that the platform is merchant of record and typically manages risk controls.
- Ask:
  ```
  How do you want to handle fraud protection?
  ```
- Options:
  - “Radar defaults — Stripe’s ML-based fraud detection (recommended)”
  - “Radar + custom rules — add business-specific rules on top (more setup)”
  - “Use Stripe defaults for now”
- Map:
  - Radar defaults → `riskManagement: { owner: "platform", radarEnabled: true, radarCustomRules: false }`
  - Radar + custom rules → `riskManagement: { owner: "platform", radarEnabled: true, radarCustomRules: true }`
  - Stripe defaults → `riskManagement: { owner: "platform", radarEnabled: true }`

If Q1 = Platform with service providers or SaaS:

- Ask:
  ```
  How do you want to handle fraud protection?
  ```
- Options:
  - “Let Stripe manage it — lower implementation overhead (recommended)”
  - “I’ll manage it with Radar — more control, more complexity”
  - “Use Stripe defaults for now”
- Map:
  - Stripe-managed → `riskManagement: { owner: "stripe", radarEnabled: false }`
  - Platform-managed Radar → `riskManagement: { owner: "platform", radarEnabled: true, radarCustomRules: true }`
  - Stripe defaults → `riskManagement: { owner: "stripe", radarEnabled: false }`

If Q1 = Crowdfunding, subscription, or other:

- Skip and default to `riskManagement: { owner: "stripe", radarEnabled: false }`.

#### Q5c: Loss liability (conditional)

Skip this question if `losses_collector` is already `"stripe"`. Ask only when platform ownership is relevant (destination or separate).

Read the “Loss Liability (Negative Balance Liability)” section in `decision-matrix.md`.

Key rule: negative balance liability (who is financially liable) is separate from risk management (who detects fraud).

Defaults:

- Marketplace destination or separate: platform-owned liability and platform-owned pricing.
- SaaS direct: Stripe-owned liability and Stripe-owned pricing.

Suggested explanation script:

```
One more decision: loss liability.

This determines who bears the financial cost if a customer disputes a charge
or fraud occurs. It's separate from fraud detection (Radar handles that).

Example: A customer disputes a $100 charge.
  → Platform-owned: Stripe debits the platform's balance $100. The platform must
    reverse the prior transfer to recover funds from the connected account — which
    may drive that account's balance negative.
    Required for marketplaces — `losses_collector: "application"` enables connected
    account balances to go negative for transfer reversals.
  → Stripe-owned: If the connected account's balance goes negative and remains
    unresolved, Stripe absorbs the unrecovered amount.
    Recommended for SaaS — simpler, connected account is already merchant of record.
```

For marketplace destination or separate:

- Auto-select platform-owned and explain that transfer reversals require connected account negative balance support.

For non-marketplace models, ask:

```
Who should bear the financial risk for disputes and fraud losses?
```

Options:

- “Stripe — simpler, less financial risk (recommended for SaaS)”
- “My platform — more control, I have a risk team”
- “Explain the tradeoffs”

If user asks for tradeoffs, show side-by-side pros and cons and then re-ask with first two options.

Map answers:

- Marketplace, destination, or separate → `lossLiability.owner = "platform"`
- SaaS or direct + Stripe → `lossLiability.owner = "stripe"`
- SaaS or direct + platform → `lossLiability.owner = "platform"`

Always explain risk management vs liability separately in final recommendation.

#### Q6: Fee structure (skip if auto-filled)

Ask the user:

```
How do you want to charge your platform fee?
```

Options:

- “Percentage of each transaction (for example, 8%)”
- “Flat fee per transaction (for example, $2)”
- “Tiered/custom pricing”
- “Subscription + transaction fee”

If user chose percentage or flat fee, ask:

```
What's your platform fee?
```

Options:

- “5%”
- “10%”
- “15%”
- “Other (I’ll specify)”

#### Q6b: `application_fee_amount` calculation (conditional)

Ask only when charge pattern is destination. Don’t ask about `application_fee_amount` for separate charges and transfers — use transfer math instead. For direct charges with Stripe-owned pricing (`fees_collector: "stripe"`), the connected account pays Stripe fees and this question is moot. For direct charges with platform-owned pricing (`fees_collector: "application"`), the platform pays Stripe fees — use the Platform Pricing Tool.

Read the “Fee Calculation & Fee Economics” section in `decision-matrix.md` for full context.

Key rule: with destination charges, Stripe processing fees are deducted from the platform balance. The platform can’t make connected accounts pay those fees directly.

Set `applicationFeeIncludes`:

- `"stripe_fee_estimate"` if application fee includes estimated Stripe processing fee plus platform fee.
- `"platform_fee_only"` if platform absorbs Stripe processing fees from margin.

Store:

```json
"feeStructure": {
  "type": "percentage",
  "platformFeePercent": <value>,
  "applicationFeeIncludes": "stripe_fee_estimate" | "platform_fee_only",
  "description": "application_fee_amount = X% platform fee [+ estimated Stripe processing fee | only]"
}
```

Fee language interpretation rules:

- “X% inclusive of all fees” / “X% total take” → absorb Stripe fees (`platform_fee_only`).
- “X% on top of processing fees” / “X% above Stripe fees” → include Stripe estimate (`stripe_fee_estimate`).
- “X% platform fee” without qualifier → ask preferred option, or default to `stripe_fee_estimate`.

Critical rule: if `applicationFeeIncludes = "stripe_fee_estimate"`, `application_fee_amount` must include both platform fee and Stripe fee estimate.

### Step 3b — Hybrid business model detection

If the business has two distinct payment flows (for example, SaaS + marketplace), don’t force one charge pattern.

1. Identify both sides and expected charge pattern.
2. Include this warning:
   ```
   **Dual charge patterns add significant complexity.** Supporting both direct and
   destination charges means two separate payment flows, two sets of webhook handlers,
   and more testing scope. Consider launching with the side that's most critical to
   your business first, then adding the second once the first is stable.
   ```
3. Explain shared account reality: the same connected account may participate in multiple flows.
4. Show fee arithmetic separately for each side.

### Step 3c — Sales-led and scope detection

Trigger this check when any of these appear:

- `dashboard: "full"` + `fees_collector: "application"` request
- `on_behalf_of` requirements
- Fully custom API onboarding
- OAuth or connecting existing Stripe accounts
- Cross-border fund intermediation requirements
- Complex B2B multi-vendor billing and settlement timing
- Regulated finance, remittance, or segregation signals
- Issuing, Treasury, Capital, Tax, or Terminal alongside Connect

For non-payments products (Issuing, Treasury, Capital, Tax, Terminal):

- State that this guidance covers Connect payments integration only.
- Point to product docs and mention possible interoperability considerations.

For enterprise or sales-assisted signals:

- Ask whether they’re already working with a Stripe sales or account team.
- If yes: ask whether the account team already recommended an integration pattern.
- If yes with a recommendation: align to it, call out any compatibility constraints, and suggest confirming final details with that team.
- If no: produce a recommendation but remind them to check with their Stripe representative before implementation.
