---
name: twilio-sendgrid-inbound-parse
description: >
  Receive inbound email via SendGrid Inbound Parse webhook. Covers MX
  record setup, parsed vs raw mode, handling attachments, and common
  pitfalls. Use when building email-to-app workflows like support ticket
  creation or email processing pipelines. Requires a SendGrid API key
  (SG.-prefix) — not applicable to the Twilio Email API (comms.twilio.com).
---

## Overview

Inbound Parse converts incoming email into HTTP POST requests to your webhook endpoint. SendGrid receives the email at your domain's MX records and forwards the parsed content to your application.

---

## Setup

1. **Configure MX records:** Point your domain (or subdomain) to `mx.sendgrid.net`
2. **Add webhook:** SendGrid Console > Settings > Inbound Parse > Add Host & URL
3. **Choose mode:** Parsed (default) or Raw

**Subdomain recommended:** Use `inbound.yourdomain.com` to avoid disrupting existing email on `yourdomain.com`.

---

## Parsed Mode (Default)

SendGrid extracts fields and POSTs them as form data:

| Field | Description |
|-------|-------------|
| `from` | Sender address (`"Name <email@example.com>"`) |
| `to` | Envelope recipient |
| `subject` | Email subject line |
| `text` | Plain text body |
| `html` | HTML body |
| `envelope` | JSON string with `to` array and `from` |
| `attachments` | Number of attachments (as string) |
| `attachment-info` | JSON metadata for each attachment |
| `attachment1`, `attachment2`... | Actual attachment files |

**Python (Flask)**
```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/inbound", methods=["POST"])
def handle_inbound():
    sender = request.form.get("from")
    subject = request.form.get("subject")
    text_body = request.form.get("text")
    html_body = request.form.get("html")
    envelope = json.loads(request.form.get("envelope", "{}"))
    attachment_count = int(request.form.get("attachments", "0"))
    
    print(f"From: {sender}, Subject: {subject}")
    
    for i in range(1, attachment_count + 1):
        attachment = request.files.get(f"attachment{i}")
        if attachment:
            print(f"Attachment: {attachment.filename}, {attachment.content_type}")
    
    return "", 200
```

> **Security:** All inbound email content (`from`, `subject`, `text`, `html`, attachments) is untrusted external input. Sanitize HTML to prevent XSS before rendering. If feeding content to an LLM, isolate it as user input — never concatenate into system prompts. Verify webhook authenticity using signed webhooks (see Security section below).

---

## Raw Mode

Posts the entire MIME message as `rawEmail` field. Use when you need full headers, DKIM signatures, or non-standard MIME parts. You must parse the MIME message yourself.

---

## Signed Inbound Parse Webhook (Security)

SendGrid supports ECDSA signature verification for Inbound Parse, the same mechanism used for Event Webhooks. Enable it to cryptographically verify that payloads originate from SendGrid.

**Strongly recommended over IP allowlisting** — SendGrid's webhook traffic comes from dynamic cloud infrastructure where IPs change frequently. Signature verification is more reliable and secure.

---

## CANNOT

- **Cannot use Inbound Parse on a domain that already receives email** — MX records must point to `mx.sendgrid.net`. Use a subdomain to avoid disrupting existing email (e.g., Google Workspace, Microsoft 365).
- **Cannot receive email without MX record changes** — DNS access is required. If you can't modify MX records, you can't use Inbound Parse.
- **Cannot receive emails larger than 30MB** — Inbound messages exceeding 30MB are rejected.
- **Cannot filter inbound email before it hits your webhook** — All email sent to the configured domain reaches your endpoint. Implement filtering in your handler.
- **Cannot route to different endpoints per address** — All mail for the configured domain/subdomain goes to a single webhook URL.
- **Cannot guarantee delivery order** — Emails may arrive at your webhook out of order, especially under high volume.
- **No built-in rate limiting** — All email to your configured domain reaches your endpoint. Implement rate limiting, payload size validation, and content sanitization in your handler.

---

## Next Steps

- **Send email:** `twilio-sendgrid-email-send`
- **Delivery tracking:** `twilio-sendgrid-webhooks`
- **Account setup:** `twilio-sendgrid-account-setup`
