# Cloud Billing

Temporal Cloud provides billing and costs information for your account. Use this information to assess spending patterns, inspect your credit ledger, check invoice histories, update payment details, and manage your current plan.

---

## Tools for measuring usage and billing

| Tool | What it provides | Who can view |
|---|---|---|
| **Billing Center** | Summary invoices, credits, plan management, account deletion | Account Owners, Finance Admin |
| **Billing API** | Namespace-level cost attribution down to hourly granularity, enriched with Tags and Projects; FOCUS-friendly CSV format | Account Owners, Finance Admin |
| **Usage Dashboards** | Aggregate Actions on a Namespace level with Action categories | Account Owners, Finance Admin, Global Admin (account level); Namespace access holders (namespace level) |
| **Actions in Event History** | Highlights Actions in a given Event History via the Cloud UI (some Actions are not measured in Workflow histories) | Account Owners, Global Admin, Namespace Admin, Developers, Read-Only |
| **Actions Metrics** | High-cardinality billable action metric with labels for Category, Action Type, Workflow Type, Namespace (minute granularity) | Metrics Read-Only service account role |

---

## Billing Center

Access: Account Owners and Finance Admins.

### Current balance

Shows the balance for the current billing cycle and the date it was last updated. This balance adjusts with use.

Billing cycles normally begin on the first of the month (UTC). The minimum plan fee for your first month is prorated based on your sign-up date.

### Recent bill

Displays the previous bill amount. If the account pays through Stripe, a **Pay Now** button appears. Auto-payment accounts do not need to manually pay.

### Invoices table

| Column | Description |
|---|---|
| Date (UTC) | Date range covered by the invoice |
| Type | Type of invoice (e.g., credit purchase, cloud usage) |
| Status | Current status (e.g., paid, pending) |
| Credit Granted | Total credits added to the account |
| Credit Purchase Amount | Amount paid for purchasing credits |
| Credit Usage | Credits used during the billing cycle |
| Subtotal | Total amount before adjustments |
| Balance Due | Amount to pay after applying credits |

Invoices prior to the current calendar month can be downloaded. The current billing period invoice is not finalized and cannot be downloaded.

### Credits table

| Column | Description |
|---|---|
| Effective At (UTC) | Date when the credit grant became effective |
| Type | Whether the transaction was a deduction, expiry, or grant |
| Amount | Credit amount granted, deducted, or expired |
| Credits Remaining | Remaining credit available |

### Plans

Account Owners and Finance Admins can view plan information, pricing details, entitlements, available plans, and Pay-as-You-Go pricing rates. On a standard agreement they can also upgrade and downgrade between available plans.

- Upgrades are processed immediately with pro-rated billing. Monthly entitlements reflect the full volume of the upgrade plan for that billing month. After an upgrade, a downgrade cannot be processed until the following billing period.
- Downgrades are processed immediately. Billing and entitlements are backdated to the beginning of the billing period.

### Account cancellation

- **Accounts managed by sales team:** Submit a support ticket.
- **Self-signup accounts:** Account owners can delete their accounts on the Billing page, under the **Plan** tab. Permanently deleted accounts immediately cease billing and are scheduled for full deletion within 72 hours. Account Data and Active Storage are permanently deleted. Retained Storage is deleted per its configured retention period.

---

## Usage Dashboards

Actions usage is tracked across an account in the usage dashboard and is visible to Account Owners, Finance Admin, and Global Admin. Per-namespace usage is visible on the Namespace pages to those with access.

### Actions in Workflows

When viewing an Event History, events that represent a Billable Action are annotated with the number consumed by the event in the **Billable Actions** column. These Actions are summarized at the top of the workflow.

This estimate is useful for projecting cost. Example: 20 Actions per run, 100 runs/day, 30 days = 60,000 Billable Actions per month.

> **Treat the estimate as an estimate.** The Billable Action estimate is an **experimental feature** and only measures Billable Actions that exist within Workflow event histories. If billable events exist outside of event history, the actual Actions count could be higher. Workflows with the `TemporalNamespaceDivision` Search Attribute set may not have accurate estimates.

Excluded from the Billable Actions estimate:

- Query
- Activity Heartbeats
- Rejected Update Workflow Executions
- Export
- Schedule
- Replicated Actions in Namespace replication

---

## Billing API

The Billing API is part of the Cloud Operations API. It provides Namespace-level cost attribution through on-demand billing reports in CSV format, for ingestion into FinOps tooling and cloud cost management platforms.

Reports contain:

- Accurate Namespace-level cost attribution
- Hourly, daily, and monthly granularities
- A FOCUS-friendly data format

### Report generation flow

Report generation is **asynchronous**.

1. Create a billing report using `CreateBillingReport`. The response includes a `billing_report_id` and `async_operation_id`.
2. Poll `GetBillingReport` using the `billing_report_id`.
3. When the report state becomes `BILLING_REPORT_STATE_GENERATED`, retrieve the download URL.
4. Download the report before the URL expires.

Key identifiers:

| Identifier | Purpose |
|---|---|
| `billing_report_id` | Identifies the billing report; used to retrieve metadata and download URLs |
| `async_operation_id` | Identifies the background operation responsible for generating the report |

The async operation follows the standard Cloud Operations async model. See [cloud-ops-api.md](cloud-ops-api.md).

### Allowed date ranges

Date ranges must use billing-month boundaries (MM/YYYY). Requests may include the current billing month. Finalized reports include usage up to `current_time` - 24 hours (rounded down to the granularity level).

Data range limits by granularity:

| Granularity | Available range |
|---|---|
| Hourly | Current billing month + previous billing month |
| Daily | Current billing month + previous two billing months |
| Monthly | Current billing month + previous eleven billing months |

### Rate limits and concurrency

Within a single account, only one billing report is generated at a time. Additional requests are accepted but queued.

Report generation time varies and is not guaranteed. Factors include the size of the requested date range and overall platform load.

### Best practices

- Provide an idempotency key (`async_operation_id`) when retrying requests.
- Poll `GetBillingReport` using exponential backoff.
- Download reports immediately after generation (URLs expire).
- Avoid frequent generation of large overlapping ranges in the current billing period.

### Report schema (27 columns)

Each row represents a charge record.

| Column Name | Description | Example |
|---|---|---|
| `BillingAccountID` | Temporal Cloud account ID | `a2dd6` |
| `BillingAccountName` | Temporal Cloud account name | `temporal` |
| `BillingCurrency` | The currency an account is billed in | `USD (cents)` |
| `BillingPeriodEnd` | Exclusive end bound of a billing period | `2024-02-01T00:00:00Z` |
| `BillingPeriodStart` | Inclusive start bound of a billing period | `2024-01-01T00:00:00Z` |
| `ChargeCategory` | Highest-level classification based on how it is billed | `Usage` |
| `ChargeDescription` | Self-contained summary of the charge's purpose | `Actions - Tier 1` |
| `ChargeFrequency` | How often a charge occurs | `Usage-Based` |
| `ChargePeriodEnd` | Time period end for the charge (correlates to data granularity) | `2025-10-01T01:00:00.000Z` |
| `ChargePeriodStart` | Time period start for the charge (correlates to data granularity) | `2025-10-01T00:00:00.000Z` |
| `ContractedCost` | Cost calculated by multiplying `ContractedUnitPrice` and `PricingQuantity` | `100.00` |
| `ContractedUnitPrice` | Agreed-upon unit price for a single pricing unit, inclusive of negotiated discounts | `10.00` |
| `InvoiceID` | ID of the invoice for this billing period | `in_XXXXXXXXXXXXXXXXXXXX` |
| `InvoiceIssuer` | Entity responsible for issuing payable invoices | `stripe` |
| `PricingQuantity` | Volume of a given SKU used or purchased | `10.00` |
| `PricingUnit` | Measurement unit for `PricingQuantity` | `1 Million Actions` |
| `Provider` | Provider of purchased resources or services | `Temporal Technologies` |
| `Publisher` | Publisher of purchased resources or services | `Temporal Technologies` |
| `ResourceID` | Namespace name + Temporal Cloud account ID | `production.a2dd6` |
| `ResourceName` | Namespace name + Temporal Cloud account ID | `production.a2dd6` |
| `ResourceType` | Type of resource the charge applies to | `Namespace` |
| `ServiceCategory` | Highest-level classification based on core function | `Temporal Cloud` |
| `ServiceName` | Offering that can be purchased from a provider | `Temporal Cloud` |
| `ServiceSubcategory` | Secondary classification based on core function | `Actions` |
| `SKUID` | Unique identifier for a specific SKU | `essentials-actions` |
| `SKUMeter` | Functionality being metered by a particular SKU | `Actions` |
| `Tags` | Provider and customer defined tags associated with resources | `{"$tmprl_project":["project-id"],"namespace-tag-key":["namespace-tag-value"]}` |

**Key schema notes:**

- `ResourceID` is `namespace_name.account_id` (e.g., `production.a2dd6`), not just the namespace name.
- `BillingCurrency` values are in cents (e.g., `USD (cents)`).
- The cost column is `ContractedCost`, not `Cost` or `TotalCost`.
