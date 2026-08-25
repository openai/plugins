## Connect integration compatibility reference

This document encodes known Connect integration incompatibilities — combinations of account controller properties and charge types that cause serious issues for platforms. Use this as a validation checklist when recommending or reviewing any Connect configuration.

### 1. Controller Property + Charge Type Compatibility Matrix

Significant compatibility issues arise when account controller properties (dashboard, fees_collector, losses_collector) are paired with incompatible charge types. Each combination below is rated:

- **BLOCKED** — Incompatible combination. Never recommend. Can cause liability-model mismatch, fee-model mismatch, or inability to manage key payment operations.
- **CAUTION** — Technically functional but has significant drawbacks. Present with explicit warnings.
- **ALLOWED** — Supported combination. Proceed normally.
- **OUT OF SCOPE** — Not supported by this guide. Redirect to Stripe docs or sales.
- **Reasoning depth vs output brevity** — This reference is intentionally detailed so the assistant can reason about liability and transfer mechanics. User-facing warnings should stay concise and action-oriented.
- **Output guardrail** — Keep recommendation warnings concise (typically one to two sentences). Use the mechanism details in this document to choose the right warning and alternative path, not to dump every detail verbatim.

#### Core Rule

> **For GA configurations with `losses_collector: "stripe"`, ONLY direct charges are safe.**
> 
> For destination charges and separate charges and transfers, use `losses_collector: "application"` so responsibility aligns with dispute and transfer-reversal flows. In this guide, combinations that pair these charge patterns with `losses_collector: "stripe"` are marked BLOCKED.
> 
> **Exception:** Express dashboard with `losses_collector: "stripe"` (regardless of fees_collector) is blocked for ALL charge types including direct — these configs are still in beta. Don’t recommend them.

> **Note:** `on_behalf_of` configurations aren’t supported by this guide. `on_behalf_of` columns are retained in the matrix for compatibility detection only — if the assistant encounters `on_behalf_of` requirements, it should redirect to Stripe docs or sales.

#### Full Matrix (v2 field names)

| Dashboard | Fees Collector | Losses Collector | Direct | Destination | Destination `on_behalf_of` | Separate charges and transfers | Separate charges and transfers `on_behalf_of` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `full` | `stripe` | `stripe` | ALLOWED | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `full` | `stripe` | `application` | BLOCKED | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `full` | `application` | `application` | SALES-GATED | SALES-GATED | OUT OF SCOPE | SALES-GATED | OUT OF SCOPE |
| `full` | `application` | `stripe` | SALES-GATED | SALES-GATED | OUT OF SCOPE | SALES-GATED | OUT OF SCOPE |
| `express` | `application` | `application` | ALLOWED | CAUTION | OUT OF SCOPE | CAUTION | OUT OF SCOPE |
| `express` | `stripe` | `stripe` | BLOCKED* | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `express` | `stripe` | `application` | BLOCKED | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `express` | `application` | `stripe` | BLOCKED* | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `none` | `stripe` | `stripe` | BLOCKED | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `none` | `stripe` | `application` | BLOCKED | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `none` | `application` | `stripe` | BLOCKED | BLOCKED | OUT OF SCOPE | BLOCKED | OUT OF SCOPE |
| `none` | `application` | `application` | ALLOWED | ALLOWED | OUT OF SCOPE | ALLOWED | OUT OF SCOPE |

\*Express dashboard with `losses_collector: "stripe"` configs are still in beta. Even when GA, destination charges and separate charges and transfers still require platform-run dispute or refund recovery (including transfer reversals), which aligns with `losses_collector: "application"` instead.

#### CAUTION Details

**express + application + application + destination charges (without `on_behalf_of`) and separate charges and transfers:**

- Connected accounts can’t manage refunds, disputes, or Radar rules from their Express dashboard for these charge types (see [Express dashboard payments docs](https://docs.stripe.com/connect/express-dashboard/payments.md))
- Stripe debits disputes to the platform first for these charge patterns; recovery depends on reversing prior transfers back from connected accounts
- This pattern is only viable when the platform owns losses (`losses_collector: "application"`) and runs webhook-driven refund or dispute recovery workflows
- Platform must handle failure modes (for example, insufficient connected-account balance) and negative-balance remediation
- `on_behalf_of` is out of scope for this guide. Redirect to Stripe docs or sales instead of recommending it.

#### Blessed Paths (Safe Defaults)

| Business Model | Dashboard | Fees | Losses | Charge Type | Rating | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| **Marketplace** | `express` | `application` | `application` | Destination | CAUTION | Recommended path — CAUTION applies: connected accounts have limited dispute or refund visibility from their Express dashboard; platform must run webhook-driven recovery workflows. Always include the Express dispute-visibility warning. |
| **SaaS** | `full` | `stripe` | `stripe` | Direct | ALLOWED | Stripe-managed fee and loss defaults; connected accounts are independent merchants |
| **Enterprise or White-label** | `none` | `application` | `application` | Destination or Direct | ALLOWED | Full platform control |

### 2. Why Blocked Combos Fail

When `losses_collector: "stripe"` is combined with non-direct charges (destination or separate charges and transfers), this guide marks the combination as BLOCKED for three documented reasons:

1. **Liability settings should align with where disputes are debited.** For destination charges and separate charges and transfers, disputes are debited from the platform balance. Use `losses_collector: "application"` so the liability model matches this funds flow.

2. **Payment fees for these charge types are assessed on the platform.** For destination charges or separate charges and transfers, Stripe collects payment fees from the platform account regardless of `fees_collector`. (Rates vary by region — see [stripe.com/pricing](https://stripe.com/pricing).) Note: Legacy types behave differently, see [Fee behavior](https://docs.stripe.com/connect/direct-charges-fee-payer-behavior.md).

3. **Recovery from connected accounts requires explicit transfer-reversal handling.** For destination and separate disputes, Stripe debits the platform first; the platform then recovers funds by reversing transfers through the API or Dashboard. Refunds can auto-reverse transfers when `reverse_transfer: true`, but dispute recovery isn’t automatic and requires explicit logic.

### 3. Merchant of record enforcement gap

Whoever provides the good or service at the transaction level should be the merchant of record. The charge type dictates who the merchant of record is:

- **Direct charges** → Connected account is merchant of record (their name on bank statements)
- **Destination charges and separate charges and transfers** → Platform is merchant of record
- **`on_behalf_of` variants** → Connected account is merchant of record (despite charge living on platform account)

**CRITICAL:** Platforms declare their intended merchant-of-record setup during platform onboarding, but can then create charges with any pattern regardless. Stripe will NOT enforce this selection at the API level. The recommendation must ensure the charge type matches the user’s actual business relationship (who provides the goods and services).

### 4. Additional compatibility risks

#### 4a. OAuth or Connecting Existing Stripe Accounts

**Risk level:** OUT OF SCOPE

Connecting existing Stripe accounts through OAuth is a v1-only pattern primarily used in sales-assisted integrations. This guide doesn’t support OAuth-based onboarding.

**Why OAuth is problematic:**

- Connected accounts can disconnect at any time, severing the platform’s ability to process payments
- Platform loses visibility into the connected account’s state and requirements
- Less platform control over onboarding flow and requirement collection
- Not compatible with all embedded components

**If the user mentions OAuth, “connect existing Stripe accounts,” or “link existing accounts”:** Direct them to the [Connect documentation](https://docs.stripe.com/connect.md) and recommend [contacting Stripe sales](https://stripe.com/contact/sales). This guidance only supports creating new connected accounts with embedded onboarding.

#### 4b. Custom Onboarding Complexity

**Risk level:** CAUTION

Platforms that choose `dashboard: "none"` and build custom onboarding underestimate the ongoing burden:

- **KYC lifecycle ownership** shifts fully to the platform: initial collection, ongoing requirement monitoring, and remediation when verification fails.
- **Country-specific legal entity requirements** change frequently. What works for US entities doesn’t work for EU, and new countries add new requirements.
- **Ongoing requirement collection** is required, not one-time. When regulatory and compliance requirements change (updated KYC rules, new regulatory requirements, and more), the platform must update collection flows and prompt existing accounts.
- **Invalid information** from connected accounts leads to accounts stuck in restricted states. Without Stripe’s built-in validation, platforms end up manually remediating stuck accounts.
- **Higher remediation and maintenance burden** compared to embedded or hosted onboarding, because API-based onboarding requires custom collection logic and ongoing updates as requirements evolve.

**Recommendation:** Use embedded onboarding components or Stripe-hosted onboarding unless the platform has dedicated compliance engineering resources AND a specific branding requirement that embedded components can’t meet. This reduces compliance and maintenance burden (see [Onboard your connected account](https://docs.stripe.com/connect/marketplace/tasks/onboard.md)).

#### 4c. Dashboard DIY (Missing Refund or Dispute Flows)

**Risk level:** CAUTION

Platforms that build their own connected-account dashboard (`dashboard: "none"`) commonly build earnings and payout views but **neglect refund and dispute management flows**. Without these:

- Connected accounts can’t initiate refunds, leading to customer complaints escalating to chargebacks
- Connected accounts can’t respond to disputes, causing auto-losses
- Connected accounts can’t easily identify or remediate KYC requirement failures, causing prolonged restrictions

**Recommendation:** If building a custom dashboard, day-one scope should include refund initiation, dispute response, and KYC requirement status and remediation with country-aware requirement handling. Strongly recommend using embedded components for these. If the platform can’t commit to this, use `dashboard: "express"` instead.

#### 4d. Product compatibility by charge type

**Risk level:** INFORMATIONAL (long-term gap)

Not all Stripe products work with all Connect integration configurations.

**Recommendation:** If the platform plans to use Billing, Invoicing, or Payment Links, recommend direct charges.

For other charge types, when encountering Billing (Subscriptions, Invoicing), Tax, Payment Links, or Checkout Sessions, proceed with caution and look things up in the Stripe docs or recommend contacting sales.

#### 4e. Geo Expansion Limitations

**Risk level:** INFORMATIONAL (long-term gap)

Certain integration paths have geographic restrictions:

- **Cross-border payouts** have currency and timing limitations that vary by connected account country.
- **Instant payouts** are only available in select countries and may require specific account configurations.

**Recommendation:** If the user mentions international expansion plans, their charge pattern and account configuration may need adjustment for new countries. Recommend checking Stripe’s country availability documentation.

#### 4f. Taking on Pricing Without Expertise

**Risk level:** CAUTION

Platforms that choose `fees_collector: "application"` (platform owns pricing) should model Stripe processing fees explicitly, because unmodeled fees can reduce margins.

**Recommendation:** This is already well-covered by the skill’s mandatory fee economics breakdowns. Reinforce during discovery: if the platform doesn’t have dedicated pricing expertise, recommend `fees_collector: "stripe"` and use `application_fee_amount` for platform revenue.

#### 4g. Destination Charges + Disputes: Missing Transfer Reversals

**Risk level:** CAUTION

When a dispute occurs on a destination charge:

1. The charge lives on the **platform’s** account (platform is merchant of record)
2. Stripe debits the **platform’s** balance for the disputed amount
3. However, the platform has already transferred funds to the connected account using `transfer_data`

The platform’s balance is reduced but the connected account still has the funds. **A common implementation issue:** platforms fail to initiate a **transfer reversal** to recover the disputed amount from the connected account.

**What should happen:**

- Platform listens for `charge.dispute.created` webhook
- Platform creates a transfer reversal to pull funds back from the connected account
- If the connected account’s Stripe balance is insufficient, the reversal creates a negative balance on the connected account (requires `losses_collector: "application"`)

**What commonly goes wrong:**

- Platform doesn’t listen for dispute webhooks at all
- Platform processes disputes manually but forgets the transfer reversal step
- Platform assumes Stripe automatically reverses the transfer (it does NOT — `reverse_transfer` defaults to `false` on both refunds and disputes)
- Connected account balance is zero, and without `losses_collector: "application"`, there’s no mechanism to recover

**Recommendation:**

- Always verify incoming webhook signatures before processing — see [Verify webhook signatures](https://docs.stripe.com/webhooks.md#verify-events). Optionally restrict requests to [Stripe’s published IP addresses](https://docs.stripe.com/ips.md).
- Always implement a `charge.dispute.created` webhook handler that automatically reverses the associated transfer
- Use `reverse_transfer: true` on refunds to make transfer reversal automatic for voluntary refunds
- For disputes, build explicit transfer reversal logic — automatic reversal only happens for refunds, not disputes
- Ensure `losses_collector: "application"` is set so the connected account balance can go negative, enabling recovery
- Consider alerting on unrecovered dispute amounts where transfer reversal failed (for example, connected account already withdrew funds)

### 5. Compatibility checks during discovery

When generating a recommendation in the discovery flow, validate the final configuration against this checklist:

1. **Compatibility matrix check:** Look up `(dashboard, fees_collector, losses_collector)` + `chargePattern` in the matrix above. If BLOCKED, don’t present. Explain why and recommend the nearest allowed alternative.
2. **Merchant-of-record consistency check:** Verify the recommended charge type matches who actually provides goods or services. Direct charges = connected account is merchant of record. Destination and separate charges and transfers = platform is merchant of record.
3. **OAuth check:** If the user mentions OAuth for connecting accounts, warn about tradeoffs and recommend Account Links.
4. **Custom onboarding check:** If `dashboard: "none"` and the user plans custom onboarding, warn about ongoing KYC collection and remediation burden and country-specific requirement drift.
5. **Dashboard scope check:** If `dashboard: "none"`, confirm the platform plans to build refund or dispute operations, not just earnings views.
6. **Fee expertise check:** If `fees_collector: "application"`, ensure the fee economics section includes explicit breakeven analysis.
7. **Warning brevity check:** Keep user-facing warnings concise (typically one to two sentences), using this document as reasoning context.
