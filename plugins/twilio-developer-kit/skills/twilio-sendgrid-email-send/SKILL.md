---
name: twilio-sendgrid-email-send
description: >
  Send transactional and bulk email via the SendGrid v3 Mail Send API.
  Covers single sends, personalized batch sends with dynamic templates,
  scheduled sends with cancellation, attachments, and sandbox mode for
  testing. Use this skill when the caller has a SendGrid API key (SG.-prefix).
  Do NOT use this skill if the caller is using the Twilio Email API
  (comms.twilio.com) — that is a separate product with different credentials.
---

## Overview

> **Agent safety:** Always confirm recipients, subject, and content with the user before sending. Email is irreversible once delivered. Never send email autonomously without explicit user approval — especially for batch sends to multiple recipients.

All email sending goes through `POST /v3/mail/send`. This endpoint returns `202 Accepted` (queued) — NOT `200 OK` (delivered). Delivery confirmation comes asynchronously via Event Webhook. See `twilio-sendgrid-webhooks`.

---

## Basic Send

**Python**
```python
import os, sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
message = Mail(
    from_email="verified@yourdomain.com",
    to_emails="recipient@example.com",
    subject="Order Confirmation",
    html_content="<p>Your order #1234 is confirmed.</p>"
)
response = sg.send(message)
print(f"Status: {response.status_code}")  # 202 = queued
```

**Node.js**
```javascript
const sgMail = require("@sendgrid/mail");
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const [response] = await sgMail.send({
    to: "recipient@example.com",
    from: "verified@yourdomain.com",
    subject: "Order Confirmation",
    html: "<p>Your order #1234 is confirmed.</p>",
});
console.log(`Status: ${response.statusCode}`); // 202 = queued
```

---

## Personalized Batch Send with Dynamic Templates

Dynamic templates use Handlebars syntax. Template IDs start with `d-`. Create templates in SendGrid Console > Email API > Dynamic Templates.

**Python**
```python
from sendgrid.helpers.mail import Mail, To

message = Mail(
    from_email="noreply@yourdomain.com",
    to_emails=[
        To("alice@example.com", dynamic_template_data={"name": "Alice", "order_id": "123"}),
        To("bob@example.com", dynamic_template_data={"name": "Bob", "order_id": "456"}),
    ],
)
message.template_id = "d-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
sg.send(message)
```

**Node.js**
```javascript
await sgMail.send({
    from: { email: "noreply@yourdomain.com" },
    template_id: "d-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    personalizations: [
        { to: [{ email: "alice@example.com" }], dynamic_template_data: { name: "Alice", order_id: "123" } },
        { to: [{ email: "bob@example.com" }], dynamic_template_data: { name: "Bob", order_id: "456" } },
    ],
});
```

**Recipients in the same `to` array within a single personalization can see each other.** For private sends, use separate personalizations (one per recipient).

---

## Scheduled Sends

Schedule up to 72 hours in advance. Cancellation requires a batch ID assigned *before* sending.

**Python**
```python
import time, requests

headers = {"Authorization": f"Bearer {os.environ['SENDGRID_API_KEY']}", "Content-Type": "application/json"}

# Get batch ID first
batch = requests.post("https://api.sendgrid.com/v3/mail/batch", headers=headers).json()

# Include batch_id and send_at in the message
send_at = int(time.time()) + 3600  # Unix SECONDS, not ms

# Cancel if needed (before send_at)
requests.post("https://api.sendgrid.com/v3/user/scheduled_sends",
    headers=headers,
    json={"batch_id": batch["batch_id"], "status": "cancel"})
```

---

## Attachments

Base64-encode files in the `attachments` array. Total limit: 30MB per request (~22MB before encoding overhead).

```python
import base64
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

with open("invoice.pdf", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

message = Mail(from_email="billing@yourdomain.com", to_emails="customer@example.com",
               subject="Your Invoice", html_content="<p>Invoice attached.</p>")
message.attachment = Attachment(FileContent(encoded), FileName("invoice.pdf"),
                                FileType("application/pdf"), Disposition("attachment"))
sg.send(message)
```

---

## Categories and Custom Args

**Categories** tag sends for analytics segmentation (up to 10 per message):
```python
message.category = ["transactional", "order-confirmation"]
```

**Custom Args** pass metadata through to Event Webhooks (key-value strings only):
```python
message.custom_args = {"order_id": "1234", "env": "production"}
```

These appear in webhook event payloads, enabling you to correlate delivery events back to your application data.

---

## Sandbox Mode (Testing)

Validates the request without delivering. Returns `200 OK` (not `202`).

```python
message.mail_settings = {"sandbox_mode": {"enable": True}}
response = sg.send(message)  # 200 = validated, not sent
```

---

## CANNOT

- **Cannot send more than 1,000 recipients per API call** — Hard limit. Split into multiple requests.
- **Cannot schedule sends more than 72 hours in advance** — `send_at` rejects timestamps beyond 72h.
- **Cannot cancel a send after processing** — Only scheduled messages with a pre-assigned batch ID can be cancelled.
- **Cannot use `send_at` with milliseconds** — JS `Date.now()` returns ms. Divide by 1000 or the timestamp is silently rejected (>72h).
- **The `subject` field in personalizations is a plain string override** — To use dynamic subjects, set Handlebars variables (e.g., `{{{subject}}}`) in the Dynamic Template's subject field and pass values via `dynamic_template_data`. The personalizations `subject` key bypasses the template subject entirely.
- **Undefined template variables render as empty strings** — No error for typos in `dynamic_template_data` keys. Silent failures.
- **`413 Payload Too Large` returns nginx HTML, not JSON** — Exceeding 30MB returns HTML error page. Check Content-Type before parsing.
- **Empty `content` when using `template_id`** — Omit the `content` field. If you include both, `template_id` takes precedence and `content` is ignored.

> **Agent usage:** When sending email on behalf of a user, always report back what was sent — recipients, subject, and the API response status code. Maintain an application-level audit log for all sends.

---

## Next Steps

- **Account setup and domain auth:** `twilio-sendgrid-account-setup`
- **Templates and settings:** `twilio-sendgrid-email-settings`
- **Delivery tracking via webhooks:** `twilio-sendgrid-webhooks`
- **Manage bounces and unsubscribes:** `twilio-sendgrid-suppressions`
