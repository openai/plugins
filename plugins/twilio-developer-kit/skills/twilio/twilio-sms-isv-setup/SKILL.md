---
name: twilio-isv-sms-best-practices
description: >
  Best practices for ISVs (Independent Software Vendors) building SMS
  features into multi-tenant SaaS platforms using Twilio. Covers customer
  onboarding for A2P and toll-free compliance, subaccount architecture, sender management, billing patterns, and common ISV pitfalls. Use this when building SMS
  capabilities that your customers will use to message their end users.
---

## Overview

ISVs face unique challenges when building SMS into their platforms: each customer needs their own number registration, sender pool management, compliance isolation, and usage tracking. This skill consolidates the architectural patterns and operational knowledge specific to multi-tenant SMS platforms.

---

## Are You an ISV?

Before following this skill, determine whether you are an Independent Software Vendor (ISV) or a direct customer.

### Direct Customer

Your company sends messages for your own products and services. Your end users know they are interacting with your brand.

**Example:** A shoe company called CoolShoes sends marketing messages and order updates for their own products. Even if CoolShoes owns multiple brands (CoolShoes and CoolShirts), they are still a direct customer because both brands are operated by the same company.

**Follow the direct customer onboarding process** — not this ISV skill.

### ISV (Independent Software Vendor)

Your company provides messaging services to other businesses, who are represented by their own brands. Your end users think they are interacting with your client's brand, not yours.

**Example:** HotelTech Inc. sells a technology platform for hotels. When hotel SleepWell Inn uses the service, hotel visitors receive messages that appear to come from SleepWell Inn. Visitors likely don't know HotelTech powers the interaction.

**Follow this ISV skill.**

### Still Not Sure? Two Key Questions

**1. Who do your end users think they are receiving messages from?**
- **Your brand** → You are a direct customer
- **Your client's brand** → You are an ISV

**2. How much control do your clients have over message contents?**

| Scenario | Classification | Example |
|----------|---------------|---------|
| **Templated messages with little/no customization** | Direct customer | EventSite sends templated event reminders to attendees. Event organizers can only customize basic details (event name, date). End users interact with EventSite brand. |
| **Clients can customize and send messages on their own behalf** | ISV | PoweringEvents provides a platform where car dealership CarWorld can write and send customized messages about their Cars & Coffee events. Attendees don't know PoweringEvents exists — messages appear to come from CarWorld. |

**If you give clients the ability to send customized messages that end users perceive as coming directly from your client, you are an ISV.**

---

## Prerequisites

- Twilio parent account (for your platform)
- Understanding of A2P 10DLC requirements
  — See `twilio-compliance-onboarding` for registration basics
- Understanding of Messaging Services
  — See `twilio-messaging-services` for sender pool management
- Environment variables:
  - `TWILIO_ACCOUNT_SID` (parent account)
  - `TWILIO_AUTH_TOKEN` (parent account)
  — See `twilio-iam-auth-setup` for credential security
- SDK: `pip install twilio` / `npm install twilio`

---

## Key Architecture Patterns

### Subaccount Strategy

**Recommended approach:** Create one Twilio subaccount per customer.

**Why subaccounts:**
- **Billing isolation:** Each customer's usage appears on their own Twilio account, making cost tracking and pass-through billing straightforward
- **Compliance isolation:** One customer's compliance violations or spam complaints do not affect other customers
- **Credential isolation:** Each customer has their own Account SID and Auth Token, limiting the blast radius if credentials are compromised
- **Separate rate limits:** Each subaccount has its own throughput and sending limits

---

## Customer Onboarding Flow: A2P 10DLC

Use this flow when your customer needs to send SMS via 10-digit long code (local) numbers in the United States or Canada.

The [full onboarding overview](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/onboarding-is) includes all necessary API calls to complete A2P campaign registration for your customers.

**Timeline:** 13-20 business days total (3-5 days for Brand + 10-15 days for campaign). Start early.

**Do not skip this step.** Unregistered traffic gets blocked (error 30034).

### Step 1: Create Secondary Customer Profile

As an ISV, you create a Secondary Customer Profile for each of your clients in their own subaccount. This profile contains your client's business information.

### Step 2: Register Brand

**Required fields for Standard Brand:**
- Legal business name (must match EIN records exactly)
- EIN (Employer Identification Number) or business tax ID
- Business type (private, public, non-profit, government)
- Business address
- Website URL (must be publicly accessible)
- Business registration country
- Contact: first name, last name, email, phone

Once you have customer's business information, submit Brand registration using the Customer Profile Bundle SID from Step 1.

Each Standard Brand is assigned a Trust Score, which affects each campaign's throughput and the T-Mobile daily message limit for the Brand.

**Timeline:** 3-5 business days.

### Step 3: Create Campaign

Create a campaign for your customer's use case.

**Critical ISV consideration:** Each customer needs their own campaigns. Do NOT share campaigns across customers — it violates carrier policies and creates compliance risk.

Create the campaign with:
- Brand registration SID
- Use case (e.g., "2FA", "MARKETING", "MIXED")
- Clear description matching the actual use case
- 2+ sample messages that match the use case exactly
- Opt-in/opt-out details
- Whether messages contain embedded links or phone numbers

**Timeline:** 10-15 business days.

### Step 4: Provision Numbers and Create Messaging Service

1. Buy 10DLC numbers for the customer
2. Create a Messaging Service
3. Link the campaign to the Messaging Service
4. Add the number to the Messaging Service

---

## Customer Onboarding Flow: Toll-Free Verification

Use this flow when your customer needs to send SMS via toll-free numbers (800, 888, etc.).

**Timeline:** 3-5 business days.

**Do not skip this step.** Unregistered traffic gets blocked (error 30032).

**When to use toll-free vs. 10DLC:**
- **Toll-free:** Lower throughput (~3 SMS/sec **per number**, can be raised via Traffic Optimization Engine), one number per use case
- **10DLC:** Higher throughput (3.75 - 225 SMS/sec **per campaign**), can have multiple numbers per campaign

### Step 1: Buy Toll-Free Number

Purchase a toll-free number for the customer in their subaccount.

### Step 2: Submit Toll-Free Verification

Submit toll-free verification with:
- Business name and website
- Notification email
- Use case summary and categories
- Production message sample
- Opt-in type (VERBAL, WEB_FORM, etc.)
- Opt-in image URLs (screenshots of opt-in flow)
- Expected monthly message volume
- Toll-free phone number SID
- Status callback URL

**Timeline:** 3-5 business days.

---

## Multi-Tenancy Patterns

### API Key Isolation

**Create API keys per customer instead of sharing parent account credentials.**

Generate API keys per customer with a descriptive friendly name. Store the API key SID and secret securely; use them to provision resources in the customer's account on their behalf.

Only use a customer's dedicated API key — not your parent account credentials. This limits the blast radius if a customer's key is compromised.

---

## Operational Patterns

### Throughput Management

**Throughput per Brand type:**

| Brand type | SMS/sec per campaign | T-Mobile SMS daily cap (per Brand) | Total SMS daily cap (per Brand) |
|-----------|-------------------|---------------------------| ---------------------------|
| Sole Proprietor | ~1 | 1,000 messages | 3,000 messages |
| Low-Volume Standard | ~3.75 | 2,000 messages | 6,000 messages |
| Standard | ~12-225 (varies by Trust Score) | 2,000+ messages (varies by Trust Score)| Unlimited |

**ISV strategy:**
- **Use Standard Brands for your customers** unless they lack an EIN (use Sole Proprietor) or you are sure they will never send more than 6,000 SMS per day (use Low Volume Standard Brand)
- **Submit a support case to apply for secondary vetting** if you want to upgrade from a Low Volume Standard Brand to a Standard Brand

---

## Common ISV Pitfalls

### 1. Sharing Campaigns Across Customers

**DON'T:** Use a single shared campaign SID for all customers in your parent account.

**Problem:** Violates carrier policies. One customer's spam complaint affects all customers. Campaign rejection or shutdown blocks everyone.

**DO:** Each customer has their own campaigns in their own subaccount.

### 2. Building Before Registering

**DON'T:**
- Launch SMS feature to customers
- Let them send messages
- Register for A2P later when messages start failing

**Problem:** Messages blocked immediately (error 30034). Customers can't send. Scramble to register takes 10-15 business days.

**DO:**
- Build A2P registration into customer onboarding flow
- Block SMS feature until Brand + campaign approved
- Show registration status in customer dashboard
- Set expectation: "SMS will be available in 10-15 business days"

### 3. Missing Mandatory Registration Fields

**Common rejections:**

| Field | Common mistake | Fix |
|-------|---------------|-----|
| Opt-in description | "Users can opt in on our website" | "Users check 'I agree to receive SMS' checkbox at checkout.acme.com/register" |
| Message samples | Generic ("We send notifications") | Exact examples matching use case ("Your order #12345 has shipped") |
| Business name | Marketing name instead of legal name | Must match EIN records exactly |
| Website URL | Localhost, staging URL, or 404 page | Live, publicly accessible production URL |

### 4. Storing Credentials Insecurely

**DON'T:** Store credentials in plain text.

**Problem:** Credential leaks expose customer accounts.

**DO:** Encrypt credentials at rest using strong encryption (e.g., Fernet). Store encrypted values and decrypt only when needed for API calls.

See `twilio-iam-auth-setup` for credential security best practices.

---

## Constraints

- A2P campaign registration is **per customer use case in their own subaccount** — cannot be shared across tenants
- Campaign approval takes 10-15 business days — factor into onboarding timeline
- Each campaign supports only one use case; customers with multiple use cases need to use a "Mixed" use case or multiple campaigns
- Trial accounts cannot complete A2P registration — must upgrade first

---

## Next Steps

- **A2P registration details:** `twilio-compliance-onboarding`
- **Messaging Service configuration:** `twilio-messaging-services`
- **Send SMS patterns:** `twilio-sms-send-message`
- **Credential security:** `twilio-iam-auth-setup`
- **Subaccount architecture:** `twilio-account-setup`
- **General compliance guidance:** `twilio-compliance-traffic`
