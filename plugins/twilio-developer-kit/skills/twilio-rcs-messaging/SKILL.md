---
name: twilio-rcs-messaging
description: >
  Send RCS Business Messages via Twilio. Covers compliance onboarding
  (7-part US process), sender profile setup, sending rich cards and
  carousels, SMS fallback, device support (Android + iOS 18 caveats),
  and common errors. Use this skill when building RCS messaging or
  onboarding an RCS sender.
---

## Overview

RCS (Rich Communication Services) Business Messaging delivers branded, rich messages natively in the phone's default messaging app — no separate app needed. Messages show your brand logo, colors, and verified sender name. Supports rich cards, carousels, suggested actions, and media.

**RCS uses the same `messages.create()` API as SMS and WhatsApp.** For the full channel comparison and onboarding sequence, see `twilio-messaging-overview`.

### Device Support

| Platform | Support | Notes |
|----------|---------|-------|
| **Android** | Most devices via Google Messages | Carrier must also support RCS in the region |
| **iOS** | iOS 18+ | **P2P RCS is not the same as RCS Business Messaging.** A device that sends RCS to other people may not receive RCS Business Messages — this depends on both Apple and the carrier. Check via `RcsCapabilityFetcher` before sending. |

### Regional Availability

RCS availability depends on carrier approval per country. See [RCS regional availability](https://www.twilio.com/docs/rcs/regional) for the current list. US carriers (T-Mobile, AT&T, Verizon) are supported. Global support is expanding.

---

## Prerequisites

- Twilio **paid account** — free trials cannot use RCS
- Messaging Service (RCS senders must be added to a Messaging Service)
- Environment variables: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
  — See `twilio-iam-auth-setup` for credential setup
- SDK: `pip install twilio` / `npm install twilio`

---

## Compliance Onboarding (US)

RCS onboarding takes **4-6 weeks minimum**. A Twilio onboarding specialist reviews everything before carrier submission. You won't be charged until you go live.

### Part 1: Sender Profile Setup

Create your RCS Sender in Console with:

| Asset | Requirements |
|-------|-------------|
| **Display name** | Must be unique — carriers reject identical names + logos |
| **Logo** | 224x224px, max 50KB, PNG/JPEG |
| **Banner** | 1140x448px, max 200KB |
| **Accent color** | Hex code, must have 4.5:1 contrast ratio vs white |
| **Description** | What your business does and why you're messaging |
| **Phone number** | Customer support contact number |
| **Website** | Must match business identity |

### Part 2: Privacy Policy & Terms of Service

- Privacy policy URL — must be publicly accessible
- Terms of Service URL — must be publicly accessible
- Both must cover SMS/RCS messaging, data handling, opt-out process
- The privacy policy **must state** that information will be shared with third parties for the purpose of transmitting RCS messages
- Some countries require local-language versions

For US-specific compliance details, see the [RCS Compliance Onboarding Guide](https://help.twilio.com/articles/49174994355355-RCS-Compliance-Onboarding-Guide).

### Part 3: Eligibility & Acceptable Use

US carriers require:
- Legal business name matching EIN records
- EIN (Employer Identification Number)
- Business must not be on restricted industries list (cannabis, firearms, etc.)
- CTIA Messaging Principles and Best Practices handbook compliance

### Part 4: Campaign Details

- Use case category (transactional, promotional, OTP, mixed)
- Traffic volume estimates
- Campaign description with specific messaging scenarios
- For recurring messages: frequency, content types

### Part 5: Opt-In & Consent

- Describe how users opt in to receive RCS messages
- Must show explicit consent collection mechanism
- Opt-in must be specific to RCS/messaging (not buried in general ToS)
- HELP and STOP keyword handling required

### Part 6: Sample Messages

- 2+ sample messages that match your declared use case
- Must include opt-out language
- Must reflect actual message content (not generic)

### Part 7: Common Rejection Reasons

| Rejection reason | Fix |
|-----------------|-----|
| Display name not unique | Choose a distinct name — carriers reject duplicates |
| Logo/banner don't meet specs | Check dimensions and file size exactly |
| Privacy policy doesn't mention messaging | Add RCS/SMS data handling section |
| Sample messages don't match use case | Align samples with campaign description |
| Opt-in process too vague | Show specific UI/flow for consent collection |
| Business info doesn't match EIN | Legal name and EIN must match IRS records exactly |
| Media URLs not publicly accessible | All images/videos must be on public URLs — carriers verify during review |

### Registration Flow

1. **Create RCS Sender** in Console → complete all 7 parts above
2. **Test Phase** — Add test devices, send and receive messages without carrier approval. Non-test devices get SMS fallback.
3. **Compliance Submission** — Twilio specialist reviews, then submits to Google + carriers:
   - **Google registration:** authorized rep details, opt-in/opt-out policy, use case video, interaction flow
   - **US registration (additional):** legal business name + EIN, traffic metrics, CTIA compliance, HELP/STOP examples
4. **Carrier approval** — Per-carrier, per-country. First carrier approval = you can go live in that country.
5. **Go live** — Add RCS Sender to your Messaging Service. Start sending.

---

## Sending RCS Messages

RCS uses the same `messages.create()` API. No address prefix needed — Twilio routes based on the sender type.

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

message = client.messages.create(
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to="+15558675310",
    body="Your order has shipped! Track it here: https://example.com/track/12345"
)
print(message.sid, message.status)
```

**Node.js**
```javascript
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const message = await client.messages.create({
    messagingServiceSid: "MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to: "+15558675310",
    body: "Your order has shipped! Track it here: https://example.com/track/12345",
});
console.log(message.sid, message.status);
```

### Rich Cards & Carousels

Use Content Templates for rich RCS messages (cards with images, titles, descriptions, and action buttons). Create templates via `twilio-content-template-builder`, then send with `contentSid`:

**Python**
```python
message = client.messages.create(
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to="+15558675310",
    content_sid="HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    content_variables='{"1": "Order #12345", "2": "$49.99"}'
)
```

### SMS Fallback

When a recipient's device doesn't support RCS Business Messaging, Twilio automatically falls back to SMS — no code changes needed. This is handled at the Messaging Service level.

- Fallback is automatic when the Messaging Service has both RCS sender and phone numbers
- If you send via `messagingServiceSid`, Twilio checks RCS capability first, then falls back to SMS
- Without Twilio's fallback: the message simply fails to deliver (no automatic retry to SMS)

---

## Multiple RCS Senders

A single brand can have multiple RCS senders, but each must have a **distinct use case** (e.g., one for transactional, one for marketing). The use case must be clearly different — carriers reject duplicate-purpose senders for the same brand.

- Each sender has its own display name, logo, and campaign details
- All senders go through independent carrier approval
- Each sender can only belong to one Messaging Service

## ISV Path

ISVs (Independent Software Vendors) registering RCS senders for client businesses:

- Can register on behalf of clients using the same compliance process
- Each client business needs its own RCS Sender with its own branding
- The ISV's Twilio account can host multiple RCS Senders
- Programmatic sender creation at scale is **not supported** — each sender must be created individually in Console

---

## Common Errors

| Error | Meaning | Fix |
|-------|---------|-----|
| Sender not approved | RCS sender hasn't completed carrier approval | Complete compliance onboarding; use test devices in the meantime |
| Device not capable | Recipient can't receive RCS Business Messages | Twilio falls back to SMS automatically if fallback is configured |
| Media URL inaccessible | Rich card image/video not publicly accessible | Host media on public URLs |
| Display name rejected | Name conflicts with existing RCS sender | Choose a unique display name |

---

## CANNOT

- **Cannot use RCS on free trial accounts** — Paid account required
- **Cannot send RCS without a Messaging Service** — RCS senders must be added to a Messaging Service
- **Cannot add an RCS sender to multiple Messaging Services** — Each sender belongs to one service only
- **Cannot create RCS senders programmatically at scale** — Console-only, one at a time
- **Cannot skip carrier approval** — Even with Google approval, each carrier must independently approve in each country
- **Cannot guarantee RCS delivery to iOS** — iOS 18 supports P2P RCS, but RCS Business Messaging support depends on Apple + carrier. Always have SMS fallback.
- **Cannot control fallback behavior per-message** — Fallback to SMS is automatic at the Messaging Service level when both RCS and SMS senders are present
- **Cannot send RCS to landlines** — Mobile-only channel
- **Cannot use unique display names that match existing senders** — Carriers enforce uniqueness globally
- **Cannot update sender profile after approval without re-review** — Profile changes trigger a new carrier review cycle

---

## Next Steps

- **Channel overview and onboarding guide:** `twilio-messaging-overview`
- **Create rich message templates:** `twilio-content-template-builder`
- **Set up Messaging Service for sender pool + fallback:** `twilio-messaging-services`
- **Compliance registration for other channels:** `twilio-compliance-onboarding`
- **Number and sender type selection:** `twilio-numbers-senders`
