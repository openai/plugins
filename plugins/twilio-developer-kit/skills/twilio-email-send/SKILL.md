---
name: twilio-email-send
description: >
  Use when the caller has Twilio credentials (Account SID + Auth Token or
  API Key SID + Secret) and needs to send email via comms.twilio.com/v1/Emails.
  This is Twilio-native email — NOT SendGrid. Do NOT use if the caller has a
  SendGrid API key (SG.-prefix) — use twilio-sendgrid-email-send instead.
  Covers single sends, batch sends up to 10,000 recipients, Liquid
  personalization, operation tracking, and error handling.
---

## Overview

> **Agent safety:** Always confirm recipients, subject, and content with the user before sending. Email is irreversible once delivered. Never send email autonomously without explicit user approval — especially for batch sends to multiple recipients.

**Twilio Email is a separate product from SendGrid.** Both send email, but they use different APIs, credentials, templating languages, and endpoints. If you have a SendGrid API key (`SG.`-prefix), use `twilio-sendgrid-email-send` instead.

| | Twilio Email (this skill) | SendGrid |
|---|---|---|
| **Base URL** | `https://comms.twilio.com/v1/emails` | `https://api.sendgrid.com/v3/mail/send` |
| **Auth** | Twilio Account SID + Auth Token (or API Key SID + Secret) | SendGrid API key (`SG.`-prefix) |
| **Templating** | Liquid (`{{variable}}`) | Handlebars (`{{variable}}`) |
| **Max recipients/request** | 10,000 | 1,000 |
| **Max message size** | 10MB (including attachments) | 30MB |
| **Status tracking** | Operation resource (poll `operationLocation`) | Event Webhooks (async POST) |
| **Console** | console.twilio.com | app.sendgrid.com |

---

## Prerequisites

- A Twilio account — see `twilio-account-setup` for signup and credentials
- A **Verified Sender**: an approved domain identity configured in the Twilio console that must match the `from` address domain
- Compliance with regional anti-spam regulations (CAN-SPAM, GDPR)

For a complete setup guide, see the Email Onboarding guide in the Twilio console.

---

## Authentication

The API uses **Basic Authentication** with either:
- Account SID + Auth Token
- API Key SID + API Key Secret

These are standard Twilio credentials — the same ones used for SMS, Voice, and other Twilio APIs.

---

## Send a Simple Email

`POST https://comms.twilio.com/v1/Emails`

The endpoint is **asynchronous** — it returns `202 Accepted` with an `operationId`, not a delivery confirmation.

```bash
curl -X POST "https://comms.twilio.com/v1/Emails" \
  --header "Content-Type: application/json" \
  --data '{
    "from": {
      "address": "support@example.com",
      "name": "Support Team"
    },
    "to": [
      {
        "address": "john.doe@example.com",
        "name": "John Doe"
      }
    ],
    "content": {
      "subject": "Your subject line",
      "html": "<p>Your message content in HTML format.</p>",
      "text": "Your message content in plain text."
    }
  }' \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

Response (`202 Accepted`):
```json
{
  "operationId": "...",
  "operationLocation": "https://comms.twilio.com/v1/Emails/Operations/..."
}
```

Poll `operationLocation` to track delivery status.

---

## Batch Sending

Send the same message to multiple recipients in a single request by adding entries to the `to` array. Maximum **10,000 recipients** per request.

```json
{
  "from": {
    "address": "support@example.com",
    "name": "Support Team"
  },
  "to": [
    {
      "address": "john.doe@example.com",
      "name": "John Doe"
    },
    {
      "address": "jane.smith@example.com",
      "name": "Jane Smith"
    }
  ],
  "content": {
    "subject": "Your subject line",
    "html": "<p>Your message content in HTML format.</p>",
    "text": "Your message content in plain text."
  }
}
```

---

## Liquid Personalization

Use Liquid templating in the `content.subject`, `content.html`, and `content.text` fields. For each variable referenced (e.g. `{{firstName}}`), provide a matching key in the `variables` object for every recipient in the `to` array.

```json
{
  "from": {
    "address": "noreply@example.com",
    "name": "Support Team"
  },
  "to": [
    {
      "address": "alice@example.com",
      "name": "Alice",
      "variables": {"firstName": "Alice", "orderId": "123"}
    },
    {
      "address": "bob@example.com",
      "name": "Bob",
      "variables": {"firstName": "Bob", "orderId": "456"}
    }
  ],
  "content": {
    "subject": "Hi {{firstName}}, your order update",
    "html": "<p>Hi {{firstName}}, order #{{orderId}} has shipped.</p>",
    "text": "Hi {{firstName}}, order #{{orderId}} has shipped."
  }
}
```

Ensure every recipient has all referenced variables defined.

---

## Operation Tracking

After submitting a send, use the Operation resource to monitor batch status.

1. Submit email via `POST /v1/emails` — response includes `operationId` and `operationLocation`
2. Poll status via `GET` to the `operationLocation` URI
3. The operation tracks progress for the entire batch

This is especially important for large recipient lists where processing is not instantaneous.

---

## Error Codes

| Status Code | Description | Action |
|-------------|-------------|--------|
| **202** | Accepted | Request accepted, Operation created. Poll `operationLocation` for status. |
| **400** | Bad Request | Malformed or ambiguous request content. Check JSON payload. |
| **401** | Unauthorized | Verify Account SID and Auth Token / API Key are correct. |
| **429** | Too Many Requests | Rate limited. Back off and retry. |
| **500** | Internal Server Error | Twilio server-side issue. Retry with backoff. |
| **503** | Service Unavailable | Temporarily unavailable. Retry after a short delay. |

Validation errors return as many issues as possible in a single response to help debug quickly.

---

## CANNOT

- **Cannot use SendGrid API keys** — Twilio Email uses Twilio Account SID + Auth Token or API Key SID + Secret. `SG.`-prefix keys do not work. Use `twilio-sendgrid-email-send` for SendGrid.
- **Cannot send more than 10,000 recipients per request** — Split into multiple requests for larger lists.
- **Cannot exceed 10MB per message** — Total size including attachments must be under 10MB (smaller than SendGrid's 30MB limit).
- **Cannot use Unicode in the `from` field** — Unicode encoding is not supported for sender addresses.
- **Cannot use Handlebars templating** — Twilio Email uses Liquid, not Handlebars. If you see `{{#if}}` or `{{#each}}`, that's Handlebars/SendGrid syntax.
- **Cannot get synchronous delivery confirmation** — The API is async. `202 Accepted` means queued, not delivered. Poll the Operation resource for status.
- **Tags total length cannot exceed 10,000 bytes** — Combined length of all tags on a request is limited.

---

## Next Steps

- **Account setup and credentials:** `twilio-account-setup`
- **SendGrid email (separate product):** `twilio-sendgrid-email-send`
- **SMS sending:** `twilio-sms-send-message`
