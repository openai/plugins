---
name: twilio-whatsapp-send-message
description: >
  WhatsApp messaging deep-dive reference. Covers the 24-hour service
  window rules (free-form vs template mode), sandbox setup for testing,
  template approval workflow, production sender requirements, and
  WhatsApp-specific error handling. For sending WhatsApp messages, use
  twilio-send-message instead. Use this skill when setting up WhatsApp
  for the first time or debugging WhatsApp-specific delivery behavior.
---

## Overview

**WhatsApp is one channel in Twilio's Messaging platform.** All channels share the same `messages.create()` API — see `twilio-messaging-overview` for the full channel comparison and onboarding sequence.

Twilio routes WhatsApp through the Programmable Messaging API — all numbers use `whatsapp:+E.164` prefix. Two sending modes apply: **free-form** (within 24 hrs of last inbound) and **template** (anytime). Sending free-form outside the window causes silent delivery failure — always check which mode is required.

| Mode | When allowed | Parameters |
|------|-------------|------------|
| Free-form | Within 24 hrs of last inbound from user | `body`, optional `mediaUrl` |
| Template | Anytime | `contentSid` + `contentVariables` |

---

## Prerequisites

- Twilio account with WhatsApp enabled
  — New to Twilio? See `twilio-account-setup`
- Environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  — See `twilio-iam-auth-setup` for credential setup and best practices
- SDK: `pip install twilio` / `npm install twilio`
- Recipient opted in to receive messages from your WhatsApp Business Account

**Testing (sandbox):** Join by texting `join <your-code>` to `+14155238886`. No registration needed — see [Console > Messaging > Try it out > Send a WhatsApp message](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn). Sandbox participants must re-join every 3 days.

**Production:** Register a WhatsApp Business sender first — see `twilio-whatsapp-manage-senders`.

---

## Quickstart

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

message = client.messages.create(
    from_="whatsapp:+14155238886",   # Sandbox sender (or your production number)
    to="whatsapp:+15005550006",      # Must have joined the sandbox
    body="Your order has been confirmed."
)

print(message.sid)     # MMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
print(message.status)  # queued | sent | delivered | failed
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const message = await client.messages.create({
    from: "whatsapp:+14155238886",
    to: "whatsapp:+15005550006",
    body: "Your order has been confirmed.",
});

console.log(message.sid);
console.log(message.status);
```

---

## Key Patterns

### Send a Template Message (outside service window)

Templates are created in Console > Messaging > Content Template Builder and must be approved by Meta. See `twilio-content-template-builder` for template creation.

**Python**
```python
message = client.messages.create(
    from_="whatsapp:+14155238886",
    to="whatsapp:+15005550006",
    content_sid="HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    content_variables='{"1": "March 25", "2": "2:00 PM"}'
)
```

**Node.js**
```node
const message = await client.messages.create({
    from: "whatsapp:+14155238886",
    to: "whatsapp:+15005550006",
    contentSid: "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    contentVariables: JSON.stringify({ "1": "March 25", "2": "2:00 PM" }),
});
```

### Send Media (free-form only)

Max file size: 16 MB.

**Python**
```python
message = client.messages.create(
    from_="whatsapp:+14155238886",
    to="whatsapp:+15005550006",
    body="Here is your invoice.",
    media_url=["https://example.com/invoice.pdf"]
)
```

**Node.js**
```node
const message = await client.messages.create({
    from: "whatsapp:+14155238886",
    to: "whatsapp:+15005550006",
    body: "Here is your invoice.",
    mediaUrl: ["https://example.com/invoice.pdf"],
});
```

---

## Response Fields

| Field | Description |
|-------|-------------|
| `sid` | Unique message identifier (`MM...`) |
| `status` | `queued`, `sent`, `delivered`, `read`, `failed`, `undelivered` |
| `error_code` | Populated on failure |
| `error_message` | Human-readable error description |
| `date_sent` | UTC timestamp |

---

## Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 63003 | Invalid WhatsApp destination number | Verify number is WhatsApp-enabled and correctly formatted |
| 63018 | Rate limit exceeded on sender | Reduce send rate; default is 80 MPS |
| 63020 | Business hasn't accepted Twilio's Meta invitation | Accept invite in Meta Business Manager |
| N/A | Free-form outside window | Switch to a template message |

---

## CANNOT

- **Cannot exceed 80 messages/second per sender** — Text-only can be raised to 400 MPS on request
- **Cannot queue messages beyond 4 hours** — Undelivered messages fail after 4 hours
- **Cannot exceed sandbox throttle limits** — 1 message per 3 seconds, 50 messages/day on trial, participants expire after 3 days
- **Cannot send without opt-in** — Sending without recipient opt-in risks account suspension
- **Cannot use WhatsApp Groups API** — Deprecated April 2020. Use Conversations API instead.

---

## Next Steps

- **Channel overview and onboarding guide:** `twilio-messaging-overview`
- **Register a production WhatsApp sender:** `twilio-whatsapp-manage-senders`
- **Create and manage message templates:** `twilio-content-template-builder`
- **Multi-channel conversations with history:** `twilio-conversations-api`
