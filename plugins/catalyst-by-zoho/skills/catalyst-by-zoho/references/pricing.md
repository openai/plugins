# Catalyst Pricing Reference & Cost Estimation Guide

> **Pricing data last verified: May 2026.** Catalyst pricing can change. Always verify current rates at https://catalyst.zoho.com/pricing.html before quoting estimates to clients.

Use this reference when the user asks about Catalyst pricing, cost estimation, or wants to generate
a pricing spreadsheet for their project. This file contains the complete pricing data and instructions
for building dynamic Excel pricing models.

---

## Table of Contents
1. [Pricing Model Overview](#pricing-model-overview)
2. [Complete Pricing Table](#complete-pricing-table)
3. [Free Tier Limits](#free-tier-limits)
4. [Billing Rules](#billing-rules)
5. [GB-Seconds Calculation](#gb-seconds-calculation)
6. [Generating a Pricing Spreadsheet](#generating-a-pricing-spreadsheet)

---

## Pricing Model Overview

Catalyst uses **pay-per-use** pricing. Key facts:
- **Free tier:** Generous monthly limits that renew every month, applied at account level (across all projects).
- **Free trial:** New customers get $250 USD wallet credits valid for 180 days.
- **Minimum billing:** $5/project/month once any free tier limit is exceeded.
- **No upfront commitments.** Cancel anytime.
- **Subscription option** also available for predictable billing — details at
  https://www.zohowebstatic.com/sites/zweb/images/catalyst/subscription-plan.pdf
- Invoicing currency matches the credit card on file.

---

## Complete Pricing Table

All prices listed below are in **USD**. See the [Currency & Regional Pricing](#currency--regional-pricing)
section at the bottom for INR and other currency guidance.

### Serverless

| Component | Operation | Unit Price (USD) | Unit |
|---|---|---|---|
| Functions | Execution | 0.000016 | per GB-second |
| Circuits | State transition | 0.00002 | per transition |
| AppSail | Runtime | 0.08 | per GB-hour |

### Backend — Data Store

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| SELECT | 0.00006 | per request |
| INSERT | 0.0001 | per request |
| UPDATE | 0.00008 | per request |
| DELETE | 0.00008 | per request |
| Storage | 0.02 | per GB/month |

### Backend — Cache

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| GET | 0.00004 | per request |
| PUT | 0.00006 | per request |
| UPDATE | 0.00006 | per request |

### Backend — File Store (deprecated, removal date TBD)

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Upload | 0.000005 | per request |
| Download | 0.0000004 | per request |
| Storage | 0.02 | per GB/month |

### Backend — Stratus (Object Storage)

> **Note:** Stratus has its own pricing structure. The values below are estimates — verify current Stratus rates at https://catalyst.zoho.com/pricing.html before using in client-facing estimates.
| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Upload | 0.000005 | per request |
| Download | 0.0000004 | per request |
| Storage | 0.02 | per GB/month |

### Backend — Other

| Component | Unit Price (USD) | Unit |
|---|---|---|
| API Gateway | 0.000001 | per request |
| Web Client Hosting | 0.0000004 | per request |
| Mail | 0.001 | per email |
| Push Notifications | 0.00002 | per notification |
| Search | 0.00004 | per query |

### SmartBrowz

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Headless Browser | 0.1188 | per hour |
| PDF Conversions | 0.0033 | per PDF |
| BrowserLogic | 0.000002 | per invocation |

### DevOps

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| APM | 0.00002 | per request |
| Automation Testing | 0.005 | per test case |
| Application Alerts | 0.0005 | per alert |
| Pipeline Build & Deploy | 0.00016 | per GB-second |

### AI/ML — Zia APIs

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Face Analytics | 0.001 | per request |
| Image Moderation | 0.001 | per request |
| OCR | 0.001 | per request |
| Object Recognition | 0.001 | per request |
| Barcode Scanner | 0.001 | per request |
| AutoML Prediction | 0.001 | per request |
| Text Analytics | 0.001 | per request |

### AI/ML — ConvoKraft

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Messages | 0.0006 | per message |

### AI/ML — QuickML

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Model Inference (0–25K) | 0.0025 | per API call |
| Model Inference (25K–100K) | 0.002 | per API call |
| Model Inference (>100K) | 0.001 | per API call |
| Data Storage | 0.00003 | per GB/hour |
| Single Prediction | 0.0005 | per call |
| Bulk Prediction | 0.0025 | per 100 records |
| LLM Input Tokens | 0.2 | per million tokens |
| LLM Output Tokens | 0.4 | per million tokens |
| VLM Input Tokens | 0.8 | per million tokens |
| VLM Output Tokens | 1.2 | per million tokens |

### Slate

| Operation | Unit Price (USD) | Unit |
|---|---|---|
| Build & Deploy (2vCPU 4GB) | 0.00016 | per GB-second |
| Hosting Storage (CDN) | 0.0001 | per MB |
| Functions invocations | 0.000016 | per GB-second |
| Requests (CDN & Origin) | 0.000004 | per request |
| ISR Read | 0.0000003 | per request |
| ISR Write | 0.000003 | per request |

---

## Free Tier Limits

These are monthly limits applied at the **account level** (across all projects). Renew every month.

### Serverless
| Component | Free Allowance |
|---|---|
| Functions | 25,000 GB-seconds |
| Circuits | 2,000 state transitions |
| AppSail | 15 GB-hours |

### Backend — Data Store
| Operation | Free Allowance |
|---|---|
| SELECT | 10,000 requests |
| INSERT | 5,000 requests |
| UPDATE | 1,000 requests |
| DELETE | 1,000 requests |
| Storage | 5 GB |

### Backend — Cache
| Operation | Free Allowance |
|---|---|
| GET | 1,000 requests |
| PUT | 5,000 requests |
| UPDATE | 5,000 requests |

### Backend — File Store / Stratus
| Operation | Free Allowance |
|---|---|
| Upload | 2,000 requests |
| Download | 10,000 requests |
| Storage | 5 GB |

### Backend — Other
| Component | Free Allowance |
|---|---|
| API Gateway | 100,000 requests |
| Web Client Hosting | 300,000 requests |
| Mail | 100 emails |
| Push Notifications | 500 notifications |
| Search | 1,000 queries |

### SmartBrowz
| Operation | Free Allowance |
|---|---|
| Headless | 5 hours |
| PDF Conversions | 50 PDFs |
| BrowserLogic | 25,000 GB-seconds |

### DevOps
| Operation | Free Allowance |
|---|---|
| APM | 5,000 requests |
| Automation Testing | 100 test cases |
| Application Alerts | 100 alerts |
| Pipeline Build & Deploy | 72,000 GB-seconds |

### AI/ML — Zia APIs
All Zia APIs combined: 100 calls free (shared across all Zia services)

### AI/ML — ConvoKraft
| Component | Free Allowance |
|---|---|
| Messages | 1,000 messages |

### AI/ML — QuickML
| Operation | Free Allowance |
|---|---|
| Model Inference | 500 API calls |
| Data Storage | 1 GB |

### Slate
| Operation | Free Allowance |
|---|---|
| Build & Deploy | 72,000 GB-seconds |
| Hosting Storage | 500 MB |
| Functions | 25,000 GB-seconds |
| CDN & Origin Requests | 300,000 requests |
| ISR Read | 100,000 requests |
| ISR Write | 50,000 requests |

---

## Billing Rules

1. **Free tier is account-wide**, not per-project. If you have 3 projects, the free tier is shared
   across all three.
2. **Minimum billing of $5/project/month** kicks in once ANY free tier limit is exceeded. This $5
   is not additional — it's the floor. If your usage costs $7 across 2 projects, you pay $7 + $5
   (minimum for the second project) = $12.
3. **Billable = Max(0, Usage - Free Tier)**. Cost = Billable × Unit Price.
4. **GB-seconds** is the billing unit for functions — see calculation below.
5. **Free trial credits ($250)** are applied against invoices. Once exhausted or expired (180 days),
   normal billing begins.

---

## GB-Seconds Calculation

Functions and Slate are billed in GB-seconds:

```
GB-seconds = (Memory in MB / 1024) × Execution Time in Seconds × Number of Invocations
```

Example: 500 invocations of a function with 512MB memory running for 2 seconds each:
```
GB-seconds = (512/1024) × 2 × 500 = 500 GB-seconds
Cost = 500 × $0.000016 = $0.008
```

The free tier of 25,000 GB-seconds is shared across ALL function executions regardless of memory size.

### Cost per invocation by memory tier

The base rate is $0.000016 per GB-second. Since different functions use different memory sizes,
here's what a **single 1-second invocation** costs at each memory tier:

| Memory (MB) | GB fraction | Cost per 1-sec invocation (USD) | 10K invocations/month (USD) | 100K invocations/month (USD) |
|-------------|-------------|-------------------------------|----------------------------|------------------------------|
| 128 | 0.125 | $0.000002 | $0.02 | $0.20 |
| 256 | 0.250 | $0.000004 | $0.04 | $0.40 |
| 384 | 0.375 | $0.000006 | $0.06 | $0.60 |
| 512 | 0.500 | $0.000008 | $0.08 | $0.80 |
| 640 | 0.625 | $0.000010 | $0.10 | $1.00 |
| 768 | 0.750 | $0.000012 | $0.12 | $1.20 |
| 896 | 0.875 | $0.000014 | $0.14 | $1.40 |
| 1024 | 1.000 | $0.000016 | $0.16 | $1.60 |

**Formula:** `Cost per invocation = (Memory MB / 1024) × Execution seconds × $0.000016`

**Key insight:** A 128MB function is **8× cheaper per second** than a 1024MB function. Choose the
smallest memory that doesn't cause timeouts — this has a significant impact at scale.

> **Example:** An app makes 50,000 API calls/month, each function runs for 1.5 seconds:
> - At 1024MB: 50,000 × 1.5 × 1.0 = 75,000 GB-sec → (75,000 - 25,000 free) × $0.000016 = **$0.80/month**
> - At 256MB: 50,000 × 1.5 × 0.25 = 18,750 GB-sec → **$0.00/month** (within free tier!)

When building pricing estimates, always ask about the function's configured memory size — defaulting
to 1024MB will significantly overestimate costs for most workloads.

---

## Generating a Pricing Spreadsheet

When a user asks to estimate Catalyst costs or generate a pricing sheet, follow this workflow:

### Step 1: Gather Requirements

Understand the user's application and map it to Catalyst components. Ask about:
- **What the app does** (data processing, web app, API backend, ML, etc.)
- **Data volumes** (rows, records, files, sizes)
- **Operation patterns** (reads vs writes, batch vs real-time)
- **User/traffic scale** (requests/day, concurrent users, growth projections)
- **Compute needs** (function count, execution time, memory)
- **Storage needs** (DB size, file storage, cache)
- **AI/ML usage** (OCR, predictions, chatbots)
- **Growth trajectory** (1-year, 3-year, scaling assumptions)

### Step 2: Map to Catalyst Components

Using the user's requirements, identify which Catalyst components are needed and estimate usage.
Use the relevant equivalents file (`references/equivalents-aws.md`, `references/equivalents-gcp.md`, etc.) to translate if they describe needs in terms of another platform.

Common patterns:
- **Data processing pipeline** → Job Scheduling + Data Store + Stratus + Circuits
- **Web app with auth** → Slate + Functions + Data Store + Auth + Cache
- **API backend** → Functions (Advanced I/O) + Data Store + API Gateway + Cache
- **ML pipeline** → QuickML + Data Store + Functions
- **Chatbot** → ConvoKraft + Functions + Data Store

### Step 3: Build the Excel Pricing Model

Generate an `.xlsx` file using openpyxl (read the xlsx SKILL.md first) with these sheets:

#### Sheet 1: "Key Assumptions"
- All editable inputs in **blue text** with **yellow background**
- Organized by category (data volume, compute, storage, etc.)
- Year 1 / Year 2 / Year 3 columns for growth scenarios
- Rationale column explaining each assumption
- Header note: "Yellow cells = editable assumptions. All downstream pricing updates automatically."
- Include a processing multiplier where applicable (each user action may trigger multiple
  internal operations — e.g., 1 API call → 3 DB reads + 1 cache check + 1 log write)

#### Sheet 2: "Pricing - Year 1" (repeat for Year 2, Year 3 if needed)
- Columns: Component/Operation | Unit Price (USD) | Free Tier/Month | Est. Monthly Usage |
  Billable (Excess) | Monthly Cost (USD) | Calculation Notes
- **Unit Price**: Hardcoded from the pricing table above (black text)
- **Free Tier**: Hardcoded from the free tier table above (black text)
- **Est. Monthly Usage**: Formula referencing Key Assumptions sheet (black text)
- **Billable**: `=MAX(0, Usage - FreeTier)` formula
- **Monthly Cost**: `=Billable × UnitPrice` formula
- Group by service category with subtotals
- Grand total at bottom
- Minimum billing row: `=MAX(5, TotalCost)` (only applies if any free tier is exceeded)
- Include a cost breakdown section showing % by category

#### Sheet 3: "3-Year Projection"
- Quarterly columns (Y1-Q1 through Y3-Q4)
- Key metrics row (suppliers, users, requests, etc.) ramping over time
- Monthly cost by component
- Quarterly cost (monthly × 3)
- Annual summary
- 3-year total
- Per-unit metrics (cost per user/month, cost per transaction, etc.)

#### Sheet 4: "Pricing Range Summary" (optional but recommended)
- Side-by-side comparison of scenarios (conservative vs optimistic)
- Highlight the biggest cost drivers
- Per-unit metrics for client positioning
- Recommended client messaging

### Step 4: Excel Formatting Requirements

Follow the xlsx SKILL.md formatting standards:
- **Blue text** for editable assumptions
- **Black text** for all formulas
- **Yellow background** for assumption cells the user should change
- **Currency format**: $#,##0.00 or $#,##0 depending on magnitude
- **Percentage format**: 0.0%
- **Number format**: #,##0 with thousands separators
- All formulas must use cell references (never hardcoded values in formulas)
- Named ranges for key assumptions (makes formulas readable)
- Freeze panes for headers
- Column widths auto-adjusted or manually set for readability
- Conditional formatting for costs > threshold (red highlight for large costs)
- Print area and page setup configured

### Step 5: Key Formulas Pattern

```
# For each line item:
Billable = MAX(0, EstUsage - FreeTier)
MonthlyCost = Billable * UnitPrice

# For subtotals:
SubTotal = SUM(costs in section)

# For grand total:
GrandTotal = SUM(all subtotals)

# For minimum billing:
InvoiceValue = MAX(5 * NumProjects, GrandTotal)

# For 3-year projection with growth:
MonthlyUsage_Q = BaseUsage * (1 + GrowthRate * QuarterIndex)
# or use the specific assumptions for each year
```

### Common Cost Estimation Pitfalls to Watch For

1. **Processing multiplier**: A single user action often triggers multiple Catalyst operations.
   E.g., one "save record" might be: 1 INSERT + 2 SELECTs (validation) + 1 Cache PUT + 1 event.
   Always ask about or estimate this multiplier.

2. **Datastore is often the dominant cost** for data-heavy applications. At scale, INSERT and
   UPDATE operations at $0.0001 and $0.00008 per request add up fast with millions of rows.
   Flag this explicitly in the spreadsheet.

3. **Cache reduces Datastore costs**: Include cache hit rate as an assumption. Higher cache hit
   rates significantly reduce Datastore SELECT costs.

4. **APM costs scale with function executions**: Every function execution monitored by APM adds
   $0.00002. At millions of executions, this becomes material.

5. **Bulk vs per-row billing**: For Data Store, billing is per-request (per row operation). If
   Catalyst offers bulk write APIs that bill per-job rather than per-row, costs could be
   dramatically lower. Flag this uncertainty and show both scenarios if relevant.

6. **Free tier erodes at scale**: The free tier is generous for small apps but becomes negligible
   at enterprise scale. Don't over-optimize for free tier savings in large projections.

7. **GB-seconds math**: Memory × time × invocations. Higher memory = faster execution but higher
   cost per second. Find the sweet spot.

---

## Quick Reference: Typical Monthly Costs by App Type

These are rough order-of-magnitude estimates for orientation:

| App Type | Monthly Cost Range | Primary Cost Drivers |
|---|---|---|
| Simple web app (< 1K users) | $0–$10 | Within or near free tier |
| API backend (10K req/day) | $5–$50 | Data Store, Functions, API Gateway |
| Data processing (1M rows/mo) | $50–$500 | Data Store writes, Job Scheduling |
| Data processing (100M rows/mo) | $2,000–$30,000+ | Data Store writes dominate |
| ML-powered app | $10–$200 | Zia APIs, QuickML, Data Store |
| Chat application | $5–$50 | ConvoKraft, Functions, Cache |
| E-commerce (medium) | $20–$200 | Data Store, Cache, Functions, Mail |

These are illustrative only — always build a detailed estimate for the specific use case.

---

## Currency & Regional Pricing

### How Catalyst billing currency works

Catalyst invoices in the **currency attached to the credit card on file**. The pricing page at
https://catalyst.zoho.com/pricing.html automatically displays prices in the user's regional currency
(USD, INR, EUR, etc.) based on the account's data center.

- **US data center** → USD pricing
- **IN data center** → INR pricing
- **EU data center** → EUR pricing
- **AU, JP, SA, CA** → respective local currencies

### INR pricing guidance

Catalyst's pricing page shows INR rates when accessed from an India DC account. The exact INR values
are set by Zoho and are **not simply USD × exchange rate** — they are region-specific rates.

**When a user asks for INR pricing:**
1. Direct them to https://catalyst.zoho.com/pricing.html (it auto-detects region)
2. If they need a programmatic check, the pricing calculator on that page shows INR values for IN DC accounts
3. For estimates in this skill, all values are in USD. Add a note:
   > "These estimates are in USD. For INR pricing, visit https://catalyst.zoho.com/pricing.html
   > from your Catalyst account — it will show rates in your account's billing currency."

**When building a pricing spreadsheet for an INR user:**
- Add a "Currency" cell in the Key Assumptions sheet (default: USD)
- Add an "Exchange Rate" cell (for approximate conversion if exact INR rates are unavailable)
- Note that the user should verify against the official pricing page for exact INR rates
- The minimum billing of $5/project/month translates to the INR equivalent shown on the pricing page
