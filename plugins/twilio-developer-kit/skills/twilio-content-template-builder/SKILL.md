---
name: twilio-content-template-builder
description: >
  Create, manage, and send message templates using Twilio's Content API.
  Covers template creation for WhatsApp, SMS, RCS, and MMS; variable usage;
  WhatsApp Meta approval; and sending templates via ContentSid. Use this skill
  when building structured messages that require pre-approval or consistent
  formatting across channels.
---

## Overview

The Content API creates channel-agnostic templates identified by a `ContentSid` (`HX...`). WhatsApp templates must be approved by Meta before use outside the 24-hour service window.

---

## Prerequisites

- Twilio account — New to Twilio? See `twilio-account-setup`
- For WhatsApp templates: active WhatsApp sender
  — See `twilio-whatsapp-send-message` (sandbox) or `twilio-whatsapp-manage-senders` (production)
- Environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  — See `twilio-iam-auth-setup` for credential setup and best practices
- SDK: `pip install twilio` / `npm install twilio`

---

## Quickstart

**Step 1 — Create a template via Console** (simplest)

Console > Messaging > Content Template Builder > Create new. Use `{{1}}`, `{{2}}` for variables. Save to get a `ContentSid`.

**Step 2 — Send the template**

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

message = client.messages.create(
    from_="whatsapp:+14155238886",
    to="whatsapp:+15558675310",
    content_sid="HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    content_variables='{"1": "Sarah", "2": "March 28", "3": "10:00 AM"}'
)
print(message.sid)
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const message = await client.messages.create({
    from: "whatsapp:+14155238886",
    to: "whatsapp:+15558675310",
    contentSid: "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    contentVariables: JSON.stringify({ "1": "Sarah", "2": "March 28", "3": "10:00 AM" }),
});
```

---

## Key Patterns

### Create a Template via API

**Python**
```python
template = client.content.v1.contents.create(
    friendly_name="appointment-reminder",
    language="en",
    types={
        "twilio/text": {
            "body": "Hi {{1}}, your appointment is on {{2}} at {{3}}. Reply YES to confirm."
        }
    }
)
print(template.sid)  # HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Node.js**
```node
const template = await client.content.v1.contents.create({
    friendlyName: "appointment-reminder",
    language: "en",
    types: {
        "twilio/text": {
            body: "Hi {{1}}, your appointment is on {{2}} at {{3}}. Reply YES to confirm.",
        },
    },
});
console.log(template.sid);
```

### Submit for WhatsApp Approval

**Python**
```python
approval = client.content.v1 \
    .contents(template.sid) \
    .approval_requests \
    .create(name="appointment-reminder", category="UTILITY")
print(approval.status)  # PENDING
```

**Node.js**
```node
const approval = await client.content.v1
    .contents(templateSid)
    .approvalRequests.create({ name: "appointment-reminder", category: "UTILITY" });
console.log(approval.status);
```

Categories: `UTILITY`, `MARKETING`, `AUTHENTICATION`

### Check Approval Status

**Python**
```python
content = client.content.v1.contents(template.sid).fetch()
print(content.approval_requests.status)  # APPROVED | REJECTED | PENDING
```

**Node.js**
```node
const content = await client.content.v1.contents(templateSid).fetch();
console.log(content.approvalRequests.status);
```

Approval typically takes under 1 hour.

### List and Delete Templates

**Python**
```python
for template in client.content.v1.contents.list():
    print(template.sid, template.friendly_name, template.language)

client.content.v1.contents("HXxxxxxxxxxx").delete()
```

**Node.js**
```node
const templates = await client.content.v1.contents.list();
templates.forEach(t => console.log(t.sid, t.friendlyName, t.language));

await client.content.v1.contents("HXxxxxxxxxxx").remove();
```

### Supported Content Types

| Type | `types` key | Channels |
|------|------------|---------|
| Plain text | `twilio/text` | All |
| Media (image, video) | `twilio/media` | WhatsApp, MMS, RCS |
| Quick reply buttons | `twilio/quick-reply` | WhatsApp, RCS |
| Call-to-action buttons | `twilio/call-to-action` | WhatsApp, RCS |
| List picker | `twilio/list-picker` | WhatsApp |
| Card | `twilio/card` | RCS |
| Carousel | `twilio/carousel` | RCS |

### RCS Fallback Text

When sending a rich RCS template (card, carousel, quick reply) via a Messaging Service with SMS fallback configured, Twilio uses the template's `twilio/text` body as the SMS fallback copy. Any template intended for RCS should include a `twilio/text` entry so recipients on non-RCS devices still receive a readable message.

---

## Variable Rules

- Use `{{1}}`, `{{2}}` — sequential, no skipping
- Max 100 variables per template
- Provide sample values for WhatsApp submissions
- Non-variable to variable ratio must be at least `(2x + 1) : x`

---

## CANNOT

- **Cannot use WhatsApp templates without Meta approval** — Plan for up to 24 hours review time
- **Cannot resubmit a rejected template with the same name** — Use a different name for resubmission
- **Cannot include custom variables in AUTHENTICATION templates** — Fixed format required by Meta

---

## Next Steps

- **Channel overview and onboarding guide:** `twilio-messaging-overview`
- **Send WhatsApp messages:** `twilio-whatsapp-send-message`
- **Register a production WhatsApp sender:** `twilio-whatsapp-manage-senders`
