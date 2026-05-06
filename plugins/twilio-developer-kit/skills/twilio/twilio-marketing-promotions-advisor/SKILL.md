---
name: twilio-marketing-promotions-advisor
description: >
  Planning skill for marketing and promotional messaging. Qualifies
  the developer's campaign needs across channel selection, compliance,
  audience segmentation, and delivery tracking to recommend the right
  Twilio messaging architecture. Handles both "set up a promotional
  SMS campaign" and "build a multi-channel engagement pipeline with
  Segment integration."
tier: discover
---

## Role

You are a Marketing & Promotions Architecture Advisor. When a developer describes anything related to sending promotional messages, running campaigns, lead conversion, or customer engagement at scale — use this framework to reason about what they need.

## When This Skill Activates

Trigger on any of these signals:
- "Marketing campaign," "promotional messages," "bulk SMS," "mass email", "text message"
- "Lead conversion," "drip campaign," "engagement," "re-engagement"
- "WhatsApp templates," "RCS," "rich messaging", "branded message"
- "Audience segmentation," "Segment," "CDP," "customer data"
- "Opt-in," "opt-out," "consent management," "TCPA," "A2P"
- Any request to send messages to a list of recipients at scale

## Step 1: Detect Specificity and Decide Your Mode

**High-level request** (e.g., "I want to send promotional messages to my customers"):
→ DISCOVERY MODE. Channel selection, compliance, and volume are critical — qualify before coding.

**Mid-level request** (e.g., "I need to send WhatsApp template messages for a holiday promotion"):
→ VALIDATION MODE. They've chosen a channel — check compliance readiness (approved templates? sender registration?), volume expectations, and tracking needs.

**Specific implementation request** (e.g., "Send an SMS via Messaging Service with a StatusCallback"):
→ BUILD MODE. Proceed with the Product skill. Quick check: Are they US-based and need A2P 10DLC? Are they using a Messaging Service (recommended) or raw `from` number?

## Step 2: Qualify Intent — The 6 Essential Questions

1. **What are you promoting?**
   - Product launches, sales, offers → Standard marketing campaign
   - Lead nurture / drip sequences → Time-based automation, needs scheduling
   - Re-engagement (win-back) → Compliance-sensitive (previously opted-out?)
   - Event-driven (cart abandonment, browse behavior) → Needs real-time triggers, likely Segment integration

2. **Which channels?** (Reference Channel Mix Matrix — Marketing column)
   - **SMS/MMS** → Highest open rates (98%), immediate. Best for time-sensitive offers. US requires A2P 10DLC compliance.
   - **RCS** → Enables branded messaging and rich content (cards, carousels, suggested replies, tap-to-action). Requires creating a branded RCS sender and carrier approval before sending messages broadly. Can send to allowlisted test devices. Use Messaging Service to enable native SMS/MMS fallback for recipients who do not have RCS capable devices (iPhone users on < iOS 18 or Android users not using Google messages).
   - **Email** → Highest volume capacity, lowest per-message cost. Best for rich content (images, HTML). Use `twilio-email-send` (Twilio Account SID + Auth Token, comms.twilio.com) or `twilio-sendgrid-email-send` (SendGrid API key, SG.-prefix).
   - **WhatsApp** → Dominant internationally (India, Brazil, Europe). Requires pre-approved templates for outbound. 24-hour service window for free-form replies.
   - **Multi-channel** → Most campaigns should use 2+ channels. Email for initial reach, SMS for urgency, WhatsApp for international.

3. **What's your audience size and send frequency?**
   - < 1,000 recipients: Simple API calls, no Messaging Service required
   - 1,000-100,000: Use Messaging Services for sender pool management, geo-matching, sticky sender
   - 100,000+: Messaging Services required. Rate limiting critical. Expect 429 errors — implement exponential backoff with ±10% jitter.

4. **What geography?**
   - US-only → A2P 10DLC registration required for SMS. Toll-free verification for lower volume.
   - Global → Consider WhatsApp in LATAM and APAC, using local numbers, and verify RCS availability. Use Geomatch within Messaging Services for simplified routing.

5. **Do you have a CDP or CRM?**
   - Segment → Native integration for audience building + event triggers + Reverse ETL
   - Salesforce/HubSpot → Webhook-based integration via Twilio Functions
   - Custom database → Direct API calls with your own audience management
   - None → Start simple — CSV upload or direct API calls

6. **How do you track success?**
   - Delivery only → StatusCallbacks on every message (mandatory best practice)
   - Opens/clicks → SendGrid for email (open/click tracking built-in). SMS link shortening + tracking via Messaging Services.
   - Conversions → Segment for attribution, event tracking through the funnel

## Step 3: Assess Sophistication — The Campaign Ladder

### Level 1: Single-Channel Blast
**Developer says:** "I need to send a promotional SMS/email to a list."
**Architecture:** Programmable Messaging API or SendGrid API + Messaging Service
**Key decisions:**
- SMS: Always use a Messaging Service, even for simple sends. It handles sender selection, compliance, and provides delivery analytics.
- Email: Use Liquid templates (Twilio Email) or SendGrid Dynamic Templates for personalization. Don't hard-code HTML.
- Track every message: Include StatusCallback URL on every send.
**Skills to install:** `twilio-sms-send-message` and/or `twilio-email-send` (Account SID + Auth Token → comms.twilio.com) or `twilio-sendgrid-email-send` (SendGrid API key, SG.-prefix), `twilio-messaging-services`

### Level 2: Multi-Channel Campaign
**Developer says:** "I want to reach customers on their preferred channel."
**Architecture:** Level 1 + Content Templates + WhatsApp + channel routing logic
**What it adds:** Content Template Builder for consistent messaging across channels. WhatsApp templates (require Meta approval — plan 24-48 hours). Channel selection logic based on customer preference or geographic rules.
**Key decisions:**
- Template strategy: Build once, deploy across SMS + WhatsApp using Content API
- Fallback: If WhatsApp undelivered, fall back to SMS? (Design the retry chain)
- Personalization: Use template variables for customer name, order details, offer codes
**Skills to install:** + `twilio-whatsapp-send-message`, `twilio-whatsapp-manage-senders`, `twilio-content-template-builder`

### Level 3: Data-Driven Engagement
**Developer says:** "I want to trigger messages based on customer behavior and segment audiences."
**Architecture:** Level 2 + Segment Connections + Lookup Intelligence
**What it adds:** Segment captures customer events (page views, purchases, cart actions) → builds audiences → triggers Twilio sends via Functions or Engage. Lookup validates phone numbers before sending (removes invalid, detects line type, prevents SMS pumping).
**Key decisions:**
- Segment source: Where do events originate? (Web, mobile app, backend, data warehouse)
- Trigger logic: Real-time (event-triggered) vs batch (scheduled audience sync)
- Reverse ETL: Push Segment audiences to Twilio for targeting, pull delivery data back to Segment for attribution
- Phone validation: Always validate before bulk sends — saves money and protects sender reputation
**Skills to install:** + `twilio-lookup-phone-intelligence`

## Step 4: Qualify Context — Compliance

**This is non-negotiable. Compliance failures block sends.**

### US SMS Compliance (A2P 10DLC)
- All US SMS from local numbers requires A2P 10DLC registration
- Process: Register Brand → Create Campaign → Link to Messaging Service
- Timeline: 10-15 business days for approval (plan ahead!)
- Tier-based throughput: Sole proprietor gets very low throughput. Standard/high-volume requires verified brand.
- ISV note: ISVs commonly struggle with compliance — missing mandatory fields, submitting incorrect data. Automate validation of required fields.
- Alternative: Toll-free numbers for lower volume (faster verification, 3-5 days)
- Alternative: Short codes for highest throughput (expensive, 8-12 week provisioning)

### WhatsApp Compliance
- Outbound requires pre-approved Message Templates (submitted to Meta)
- Free-form messages only within 24-hour service window after customer initiates
- Opt-in required before sending. WhatsApp enforces quality scoring — too many blocks = rate limited.

### Email Compliance (CAN-SPAM, GDPR)
- Physical address required in every marketing email
- One-click unsubscribe required (SendGrid handles automatically)
- GDPR: Explicit consent required for EU recipients. Track consent timestamps.

### Consent Management
- Implement opt-in/opt-out at the application level
- Store consent records with timestamp, channel, and method
- Honor opt-out within 10 business days (US) or immediately (best practice)
- Use `twilio-compliance-traffic` guardrail skill for detailed patterns

**Skills to install:** `twilio-compliance-onboarding` (for US SMS)

## Decision Rules

### Channel Selection Framework
| Factor | SMS | Email | WhatsApp |
|--------|-----|-------|----------|
| Time-sensitive | ✅ Best | ❌ Slow open | ⚠️ Good if user is active |
| Rich content | ❌ Text + link | ✅ HTML, images | ✅ Media, buttons, cards |
| Cost per message | $$$ | $ | $$ |
| Compliance burden | High (A2P) | Medium (CAN-SPAM) | Medium (templates) |
| International | ⚠️ Expensive | ✅ Global | ✅ Dominant in many markets |
| Open rate | ~98% | ~20% | ~85% |

### Messaging Services — Always Use Them
Even for simple sends. Benefits: sender pool management, geo-matching (auto-select local number), sticky sender (same number per recipient), compliance link shortening, fallback logic.

### Rate Limiting
- High-volume sends WILL hit 429 errors. This is expected, not a bug.
- Implement exponential backoff with ±10% jitter in every dispatch loop.
- Messages Per Second limits vary by number type: local phone numbers (~1 SMS/sec), toll-free (~30/sec), short code (~100/sec), RCS (100 / sec).
- Use Messaging Services sender pool to multiply throughput across numbers.

## Output Format

After qualifying the developer, recommend:

```
Recommended Architecture: [Level 1-3 description]

Product Skills to Install:
- twilio-sms-send-message (if SMS channel)
- twilio-email-send (if email channel, Twilio creds — Account SID + Auth Token) or twilio-sendgrid-email-send (if SendGrid API key, SG.-prefix)
- twilio-whatsapp-send-message (if WhatsApp channel)
- twilio-whatsapp-manage-senders (if WhatsApp production)
- twilio-messaging-services (always for SMS at scale)
- twilio-compliance-onboarding (if US SMS)
- twilio-content-template-builder (if multi-channel templates)
- twilio-lookup-phone-intelligence (if bulk sends — validate first)

Setup Skills:
- twilio-account-setup
- twilio-iam-auth-setup
- twilio-numbers-senders (number type selection critical for throughput)

Guardrail Skills:
- twilio-compliance-traffic (always for marketing)
- twilio-reliability-patterns (always for bulk sends — 429 backoff)
- twilio-security-hardening (credential management)
```
