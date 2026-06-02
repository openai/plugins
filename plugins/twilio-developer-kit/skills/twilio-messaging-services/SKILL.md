---
name: twilio-messaging-services
description: >
  Create and configure Twilio Messaging Services for production messaging.
  Covers sender pools, geo-match, sticky sender, message scheduling,
  compliance toolkit, SMS pumping protection, link shortening, and
  intelligent alerts. Use this skill when setting up production-ready
  messaging infrastructure.
---

## Overview

A Messaging Service groups senders (phone numbers, short codes, toll-free numbers) with shared configuration. Send via `messagingServiceSid` instead of a specific `from` number — Twilio picks the best sender automatically.

**Use a Messaging Service for all production sends.** Beyond sender pools, it unlocks compliance toolkit, SMS pumping protection, link shortening, message scheduling, and intelligent alerts. For channel selection guidance, see `twilio-messaging-overview`.

---

## Prerequisites

- Twilio account with at least one SMS-capable phone number
  — New to Twilio? See `twilio-account-setup`
- Environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  — See `twilio-iam-auth-setup` for credential setup and best practices
- SDK: `pip install twilio` / `npm install twilio`

---

## Quickstart

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

# Step 1: Create the service
service = client.messaging.v1.services.create(
    friendly_name="Production Notifications Service"
)
print(service.sid)  # MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx — save as MESSAGING_SERVICE_SID

# Step 2: Add a phone number
client.messaging.v1 \
    .services(service.sid) \
    .phone_numbers \
    .create(phone_number_sid="PNxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Step 3: Send via the service
message = client.messages.create(
    messaging_service_sid=service.sid,
    to="+15558675310",
    body="Your order has shipped."
)
print(message.sid)
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

// Step 1: Create the service
const service = await client.messaging.v1.services.create({
    friendlyName: "Production Notifications Service",
});
console.log(service.sid);

// Step 2: Add a phone number
await client.messaging.v1
    .services(service.sid)
    .phoneNumbers.create({ phoneNumberSid: "PNxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" });

// Step 3: Send via the service
const message = await client.messages.create({
    messagingServiceSid: service.sid,
    to: "+15558675310",
    body: "Your order has shipped.",
});
console.log(message.sid);
```

---

## Key Patterns

### Create Service with Webhooks and Features

**Python**
```python
service = client.messaging.v1.services.create(
    friendly_name="Marketing Campaigns",
    inbound_request_url="https://yourapp.com/sms/inbound",
    status_callback="https://yourapp.com/sms/status",
    sticky_sender=True,
    area_code_geomatch=True,
    validity_period=14400
)
```

**Node.js**
```node
const service = await client.messaging.v1.services.create({
    friendlyName: "Marketing Campaigns",
    inboundRequestUrl: "https://yourapp.com/sms/inbound",
    statusCallback: "https://yourapp.com/sms/status",
    stickySender: true,
    areaCodeGeomatch: true,
    validityPeriod: 14400,
});
```

### Optional Features

| Feature | Parameter | Description |
|---------|-----------|-------------|
| Sticky Sender | `sticky_sender` | Same sender for same recipient |
| Area Code Geomatch | `area_code_geomatch` | Match sender area code to recipient |
| Validity Period | `validity_period` | Discard undelivered messages after N seconds |
| Smart Encoding | `smart_encoding` | Convert unicode to GSM-7 |
| MMS Converter | `mms_converter` | Convert MMS to SMS if recipient can't receive MMS |
| Message Scheduling | `send_at` on message | Schedule sends up to 7 days ahead (see below) |
| Link Shortening | `shorten_urls` | Shorten links with branded domain + click tracking (see below) |

### List Services and Numbers

**Python**
```python
for service in client.messaging.v1.services.list():
    print(service.sid, service.friendly_name)

for number in client.messaging.v1.services(SERVICE_SID).phone_numbers.list():
    print(number.sid, number.phone_number)
```

**Node.js**
```node
const services = await client.messaging.v1.services.list();
services.forEach(s => console.log(s.sid, s.friendlyName));

const numbers = await client.messaging.v1.services(SERVICE_SID).phoneNumbers.list();
numbers.forEach(n => console.log(n.sid, n.phoneNumber));
```

---

## Production Messaging Features

The features below are platform capabilities that are configured on or require a Messaging Service. They are separate from the sender pool management above.

### Message Scheduling

Schedule messages 15 minutes to 35 days in advance. Requires `messagingServiceSid` (not `from`). Supports SMS, MMS, RCS, and WhatsApp. No additional cost — only charged for messages actually sent.

**Python**
```python
from datetime import datetime, timedelta, timezone

message = client.messages.create(
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to="+15558675310",
    body="Your appointment is tomorrow at 2pm.",
    send_at=(datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
    schedule_type="fixed"
)
print(message.sid, message.status)  # SM..., scheduled
```

**Node.js**
```javascript
const sendAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
const message = await client.messages.create({
    messagingServiceSid: "MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to: "+15558675310",
    body: "Your appointment is tomorrow at 2pm.",
    sendAt,
    scheduleType: "fixed",
});
```

Cancel a scheduled message before it sends:

```python
client.messages("SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx").update(status="canceled")
```

**Limitations:** Scheduled messages don't return a status callback event on creation. WhatsApp templates are validated at send time (not scheduling time) — non-compliant templates fail when `sendAt` fires. Opt-outs received after scheduling don't auto-cancel the message; cancel manually if needed.

---

### Compliance Toolkit (US SMS, Public Beta)

Automated compliance checks for US SMS. Enable in Console: Messaging > Settings > General > Enable Compliance Toolkit.

| Feature | What it does | Error code | Default |
|---------|-------------|-----------|---------|
| **Quiet Hours** | Reschedules non-essential messages sent during TCPA restricted hours (9PM–8AM recipient local time). Uses area code for timezone. 11 states have stricter windows. | 30610 (if block mode) | Enabled (reschedule mode) |
| **Reassigned Number Detection** | Checks FCC reassigned numbers database; re-checks every 30 days | 21610 | Enabled |
| **TCPA Known Litigators** | Blocks non-essential messages to known litigator numbers; re-verifies weekly | 30640 | **Not enabled by default** — requires account rep activation |
| **Opt-out Verification** | Blocks messages to users who replied STOP/UNSUBSCRIBE/END/QUIT/etc. | 21610 | Enabled |

**AI/ML classification:** Compliance Toolkit uses ML to classify messages as essential (OTP, alerts, support) vs non-essential (marketing, promotions). Essential messages bypass quiet hours and litigator checks. Override the classification with `messageIntent`:

**Python**
```python
message = client.messages.create(
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to="+15558675310",
    body="Your order shipped!",
    message_intent="confirm",    # Override ML: mark as essential/transactional
    risk_check="enable"          # Evaluate against all compliance checks
)
```

**Consent Management API** — Programmatically track opt-in/opt-out/re-opt-in status per phone number across SMS/MMS/RCS. Supports bulk upsert. Use alongside Compliance Toolkit to maintain consent records.

**Contact API** — Store recipient ZIP codes for more accurate quiet hours timezone inference (vs area code default).

---

### SMS Pumping Protection

Detects and blocks artificial inflation of SMS traffic (toll fraud where bad actors trigger high volumes of messages to premium-rate numbers they control).

**How it works:**
- Combines behavioral analysis with known fraud scheme identification using Twilio's proprietary model
- Analyzes: messages to regions known for pumping, countries with no prior sending history, patterns suggesting non-human behavior
- Auto-blocks suspected pumping destinations — returns error **30450**
- Enable in Console: Messaging > Settings > General > SMS Pumping Protection
- **Free in US/Canada**; other regions check SMS Pricing page

**Per-message risk check:**

**Python**
```python
message = client.messages.create(
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to="+15558675310",
    body="Your verification code is 123456.",
    risk_check="enable"   # Assess pumping risk for this specific message
)
```

**`riskCheck` parameter values:**
- `enable` (default for OTP/2FA messages): Apply SMS pumping protection
- `disable`: Skip protection (use for marketing messages where false positives are costly)

**Global Safe List API** — Whitelist phone numbers that bypass SMS Pumping Protection, Verify Fraud Guard, and other risk checks. Use for known-good customers and approved recipients.

**False positives:** The ML model may occasionally flag legitimate users. If this happens: add to Global Safe List, switch to WhatsApp/Messenger for those recipients, or contact Twilio Support.

**Note:** This is separate from Verify Fraud Guard, which only protects Verify API sends. SMS Pumping Protection covers all Programmable Messaging sends through a Messaging Service.

---

### Link Shortening & Click Tracking

Automatically shorten URLs in message bodies using a branded domain, with click tracking.

**Setup:**
1. Configure a branded short domain in Console (e.g., `link.yourcompany.com`)
2. Add DNS records as directed
3. Enable `ShortenUrls: true` on your Messaging Service

**Python**
```python
service = client.messaging.v1.services("MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx").update(
    shorten_urls=True
)
```

Once enabled, any URL in the message body is auto-shortened to your branded domain. Click events are delivered via status callback.

- Links are retained for **90 days** after creation
- Click tracking events appear in status callbacks alongside delivery events

---

### Intelligent Alerts

ML-based monitoring that detects unusual error patterns and alerts you before they become outages. This is an account-level feature (not per-service).

**Monitors 5 error codes:**
- 30001 (Queue overflow), 30005 (Unknown destination), 30006 (Landline or unreachable), 30007 (Carrier violation / spam filter), 30008 (Unknown error)

**How it works:**
- Analyzes error patterns in 5-minute windows
- Calculates impact score based on error volume and velocity
- Classifies: **Urgent** (>0.80), **Important** (0.40–0.80), **Warning** (<0.40)
- Alerts via email or webhook

**Free feature** — enable in Console > Messaging > Settings > Intelligent Alerts.

---

## CANNOT

- **Cannot add a phone number to multiple Messaging Services** — A number belongs to one service at a time
- **Cannot determine throughput from the API** — Throughput depends on number type (long code, short code, toll-free) and is not exposed programmatically
- **Cannot schedule messages without a Messaging Service** — `sendAt` requires `messagingServiceSid`, not `from`. Must also set `schedule_type="fixed"`
- **Cannot schedule more than 35 days ahead** — Scheduling window is 15 minutes to 35 days
- **Cannot use compliance toolkit outside the US** — Currently US SMS only, public beta
- **Cannot use compliance toolkit without a Messaging Service** — Features are configured per service
- **Cannot customize SMS pumping ML thresholds** — Auto-blocking sensitivity is not configurable; use Global Safe List to whitelist known-good prefixes
- **Cannot use link shortening without a branded domain** — Must configure a custom short domain first; no default short domain provided
- **Cannot use link shortening for WhatsApp** — Only available for SMS/MMS
- **Cannot customize intelligent alerts error code list** — Fixed to the 5 monitored error codes
- **Messaging Services are required for US A2P 10DLC** — Campaign registration attaches to a Messaging Service
- **Inbound routing is per-service, not per-number** — All inbound messages to numbers in the service go to `inbound_request_url`

---

## Next Steps

- **Channel overview and onboarding guide:** `twilio-messaging-overview`
- **US compliance for A2P traffic:** `twilio-compliance-onboarding`
- **Send SMS:** `twilio-sms-send-message`
- **Handle inbound SMS:** `twilio-messaging-webhooks`
