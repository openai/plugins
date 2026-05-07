---
name: twilio-security-compliance-hipaa
description: >
  Configure Twilio accounts for HIPAA compliance. Covers BAA requirements,
  HIPAA Project designation (self-service and support), eligible services
  list, per-product requirements (Voice, SMS, ConversationRelay, Conversation Intelligence,
  Flex, Verify), message redaction, and what is NOT eligible. Use this
  skill when developers are building healthcare workflows on Twilio.
---

## Overview

HIPAA compliance on Twilio is a **shared responsibility** — Twilio provides eligible services and configuration tools, but your application must architect correctly. Getting this wrong means PHI exposure and compliance violations.

**Sequence:** Execute BAA → Designate HIPAA Project(s) → Use only eligible services → Follow per-product requirements

---

## Step 1: Execute a BAA

- Contact your Twilio Account Representative to execute a Business Associate Addendum
- Purchase a **Twilio Editions package** that includes HIPAA Accounts
- BAA is required before any PHI touches Twilio infrastructure

---

## Step 2: Designate HIPAA Project(s)

### Self-Service (BAA initiated after June 6, 2024)

1. Create an Organization in Twilio Console
2. Link accounts/projects/subaccounts to the Organization
3. Console → Twilio Admin → Accounts → Select account → Enable HIPAA flag
4. Save

### Support Ticket (BAA initiated before June 6, 2024)

Open a Support ticket through Console to request HIPAA designation for specific accounts/projects/subaccounts.

### Subaccount Behavior

- **Existing subaccounts are NOT auto-designated** — Must be individually flagged
- **New subaccounts created AFTER designation DO auto-inherit** HIPAA status
- Verify each subaccount's HIPAA flag — don't assume inheritance

### What Changes When HIPAA Is Enabled

- Console auto-logoff after 15 minutes of inactivity
- Account exempt from certain content moderation (but still subject to carrier complaint review)
- No PHI in support tickets — use SIDs (CallSid, MessageSid) instead of phone numbers

---

## HIPAA Eligible Services

### Eligible (use these for PHI workflows)

| Category | Services |
|----------|----------|
| **Voice** | Programmable Voice, Recordings*, Transcription*, Media Streams*, ConversationRelay*, Conversational Intelligence for Voice*, SIP Interface*, Elastic SIP Trunking*, Voice Insights, AMD, `<Pay>`, Conference, Coaching, Transfers |
| **SMS** | Programmable SMS, MMS, Long Codes, Toll-Free, Short Codes, Messaging Services (opt-out, fallback, geomatch, sticky sender, scheduling, link shortening) |
| **Identity** | Verify (SMS + Voice + Push only), Lookup |
| **Conversations** | Chat, SMS, MMS, Group Texting (NOT WhatsApp) |
| **Flex** | Voice, SMS, Chat, Conversations, Webchat 3.x.x*, TaskRouter, Proxy, Flex Insights* |
| **Segment** | Connections (Sources, Destinations*, Functions*), Reverse ETL*, Unify, Engage Foundations*, Protocols, Privacy Portal* |
| **Runtime** | Studio*, Functions, Debugger, API Explorer, Sync, Private Assets*, TwiML Bin* |
| **Data** | Event Streams |

*Items marked with * require additional configuration per "Architecting for HIPAA on Twilio" guidance.*

### NOT Eligible (do NOT use for PHI)

- **WhatsApp** — Meta does not offer a BAA
- **SendGrid Email** (including Email in Flex and Verify Email channel)
- **AI Assistants** (including Voice for AI Assistants)
- **Verify Fraud Guard**
- **Conversational Intelligence for Conversations** (only Voice channel is eligible)
- **Agent Copilot**, **Unified Profiles** in Flex
- **Engage Premier**, **Generative Audiences**, **Campaigns**
- **Twilio Marketplace add-ons** — even with third-party BAA
- **Autopilot**
- **Flex Webchat 2.x.x** (must migrate to 3.x.x)

**Geographic restriction:** Only US area codes for Voice and SMS HIPAA traffic.

---

## Per-Product Requirements

### Voice & Recordings

- **HTTP auth required for recording URLs** — Enable in Console → Voice Settings. Recording URLs are public by default.
- **Voice Recording Encryption recommended** — Encrypts with your public key before cloud storage
- **ConversationRelay:** Your AI Provider must have their own BAA. Cannot use for clinical/medical decision-making.
- **Conversation Intelligence for Voice:** Only Azure OpenAI for generative operators. No PHI in operator prompts. Data use auto-disabled for HIPAA accounts. PII Redaction recommended (auto-redacts 21 PHI field types).

### SMS & MMS

- **HTTP auth required for MMS Media URLs** — Enable in Console → Messaging → Settings → General
- **Message Redaction recommended** — Redacts message bodies and phone numbers from Console/API/support
- **No PHI in Message Tags** — custom attributes in Message Tagging must not contain PHI
- **Message Redaction prerequisites:**
  1. Disable Sticky Sender and Fallback to Long Code on Messaging Services
  2. Contact Support to disable built-in STOP filtering (then implement custom STOP handling)
  3. Set all webhooks to POST (GET logs params for 7 days, defeating redaction)
  4. Incompatible with Studio, Flex, and Conversations

### Verify

- **Only SMS, Voice, and Push channels** — Email channel is NOT eligible
- **Fraud Guard is NOT eligible** — do not enable for HIPAA workflows

### Flex

- **Flex Insights:** Twilio auto-redacts PII from TaskRouter attributes (names, phone, email). Visual waveform and speech metrics disabled.
- **Customer must:** Ensure no PHI in preserved Attribute fields, Comments, or Assessments. Implement session timeout (Flex has no built-in timeout). Secure Flex Plugins for HIPAA.
- **No WhatsApp, Facebook Messenger, or SendGrid Email** in Flex HIPAA workflows

### Event Streams

- Customer responsible for HIPAA-compliant sink configuration (e.g., AWS Kinesis requires Amazon's HIPAA architecture)
- Non-eligible product event types must not process PHI

---

## CANNOT

- **Cannot use WhatsApp for HIPAA workflows** — Meta does not offer a BAA. Applies to all Twilio products (Conversations, Flex, Frontline).
- **Cannot use SendGrid Email** — Not HIPAA eligible in any context (Verify, Flex, standalone).
- **Cannot use Verify Fraud Guard or Email channel** — Not eligible. Only SMS, Voice, Push.
- **Cannot use AI Assistants** — Even with ConversationRelay, AI Assistants integration is not eligible.
- **Cannot use non-US area codes** — Voice and SMS HIPAA traffic limited to US area codes.
- **Cannot put PHI in support tickets** — Use SIDs for troubleshooting. Use Console chat, email, or Support Center.
- **Cannot assume subaccount HIPAA inheritance** — Existing subaccounts must be individually flagged.
- **Cannot use GET webhooks with Message Redaction** — GET parameters are logged for 7 days.
- **Cannot use Marketplace add-ons** — Even with a third-party BAA, Marketplace is not eligible.
- **Cannot use Conversation Intelligence for Conversations** — Only Voice channel is HIPAA eligible.

---

## Next Steps

- **Authentication setup:** `twilio-security-api-auth`
- **Account structure for HIPAA isolation:** `twilio-account-setup`
- **Credential security:** `twilio-security-hardening`
- **Traffic compliance (TCPA, GDPR, PCI):** `twilio-compliance-traffic`

**Official docs:** [HIPAA Eligible Services (PDF)](https://www.twilio.com/content/dam/twilio-com/global/en/other/hipaa/pdf/HIPAA-Eligible-Services.pdf) | [Architecting for HIPAA (PDF)](https://www.twilio.com/content/dam/twilio-com/global/en/other/hipaa/pdf/Architecting-for-HIPAA.pdf) | [HIPAA account flag](https://www.twilio.com/docs/iam/organizations#turn-on-hipaa-and-eligible-accounts) | [Message Redaction](https://www.twilio.com/docs/messaging/guides/privacy-message-redaction)
