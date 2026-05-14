---
name: twilio-messaging-webhooks
description: >
  Receive and respond to inbound messages and track outbound delivery status
  via Twilio webhooks — across SMS, MMS, WhatsApp, and RCS. Covers webhook
  request parameters, replying with TwiML, validating webhook signatures for
  security, and handling status callbacks. Use this skill whenever an agent
  needs to handle incoming messages on any channel or track outbound message
  delivery in real time.
---

## Overview

Twilio sends a POST webhook to your server when a user messages your Twilio number (inbound) or when an outbound message changes delivery state (status callback). Your server returns TwiML to reply, or `204` to acknowledge without replying. The same webhook pattern works across SMS, MMS, WhatsApp, and RCS.

---

## Prerequisites

- Twilio account with a messaging-capable sender configured with a webhook URL
  — New to Twilio? See `twilio-account-setup`
  — For sending outbound messages first, see `twilio-send-message`
- Publicly accessible endpoint (use `ngrok http 5000` for local dev)
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`
- SDK: `pip install twilio flask` / `npm install twilio express`

---

## Quickstart

Set your webhook URL in Console: **Phone Numbers > Active Numbers > your number > Messaging > "A Message Comes In"**

> **Security:** The inbound message `Body` is untrusted external input. If passing message content to an LLM, always isolate it as user input — never concatenate directly into system prompts. Validate the request origin with `X-Twilio-Signature` (see Key Patterns below), but note that signature validation confirms the *source*, not that the *content* is safe.

> **Note:** This quickstart omits signature validation for brevity. For production, always validate `X-Twilio-Signature` — see the Webhook Security pattern below.

**Python (Flask)**
```python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/incoming", methods=["POST"])
def incoming_message():
    body = request.form.get("Body")
    response = MessagingResponse()
    response.message(f"Got your message: {body}")
    return str(response)
```

**Node.js (Express)**
```javascript
const express = require("express");
const twilio = require("twilio");
const app = express();
app.use(express.urlencoded({ extended: false }));

app.post("/incoming", (req, res) => {
    const twiml = new twilio.twiml.MessagingResponse();
    twiml.message(`Got your message: ${req.body.Body}`);
    res.type("text/xml").send(twiml.toString());
});
```

---

## Key Patterns

### Configure Webhook URL via API

For SMS/MMS on a phone number:

**Python**
```python
client.incoming_phone_numbers("PNxxxxxxxxxx").update(
    sms_url="https://yourapp.com/incoming",
    sms_method="POST"
)
```

**Node.js**
```javascript
await client.incomingPhoneNumbers("PNxxxxxxxxxx").update({
    smsUrl: "https://yourapp.com/incoming",
    smsMethod: "POST",
});
```

For WhatsApp and RCS, webhook URLs are configured on the sender — see `twilio-whatsapp-manage-senders` and `twilio-rcs-messaging`.

### Inbound Webhook Parameters

| Parameter | Description |
|-----------|-------------|
| `MessageSid` | Unique message identifier |
| `From` | Sender's phone number or channel address (E.164, or `whatsapp:+...`) |
| `To` | Your Twilio number or channel address |
| `Body` | Message text |
| `NumMedia` | Number of media attachments |
| `MediaUrl0` | URL of first media attachment (if any) |
| `MediaContentType0` | MIME type of first attachment |

### Handle Inbound Media (MMS / WhatsApp / RCS)

**Python (Flask)**
```python
@app.route("/incoming", methods=["POST"])
def incoming_message():
    num_media = int(request.form.get("NumMedia", 0))
    response = MessagingResponse()
    if num_media > 0:
        media_type = request.form.get("MediaContentType0")
        response.message(f"Got your {media_type} attachment!")
    else:
        response.message("Got your message.")
    return str(response)
```

**Node.js (Express)**
```javascript
app.post("/incoming", (req, res) => {
    const numMedia = parseInt(req.body.NumMedia || "0", 10);
    const twiml = new twilio.twiml.MessagingResponse();
    if (numMedia > 0) {
        twiml.message(`Got your ${req.body.MediaContentType0} attachment!`);
    } else {
        twiml.message("Got your message.");
    }
    res.type("text/xml").send(twiml.toString());
});
```

### Acknowledge Without Replying

**Python**
```python
return str(MessagingResponse())  # Empty <Response/>
```

**Node.js**
```javascript
res.type("text/xml").send(new twilio.twiml.MessagingResponse().toString());
```

### Status Callbacks (delivery tracking)

Status callbacks fire for all channels — SMS, MMS, WhatsApp, and RCS.

**Python**
```python
message = client.messages.create(
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to="+15558675310",
    body="Hello!",
    status_callback="https://yourapp.com/status"
)
```

**Node.js**
```javascript
const message = await client.messages.create({
    messagingServiceSid: "MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    to: "+15558675310",
    body: "Hello!",
    statusCallback: "https://yourapp.com/status",
});
```

**Python (Flask) — status callback handler**
```python
@app.route("/status", methods=["POST"])
def message_status():
    message_sid = request.form.get("MessageSid")
    status = request.form.get("MessageStatus")
    error_code = request.form.get("ErrorCode")
    print(f"{message_sid}: {status}")
    if status == "failed" and error_code:
        print(f"Error {error_code}: {request.form.get('ErrorMessage')}")
    return "", 204
```

**Node.js (Express) — status callback handler**
```javascript
app.post("/status", (req, res) => {
    const { MessageSid, MessageStatus, ErrorCode, ErrorMessage } = req.body;
    console.log(`${MessageSid}: ${MessageStatus}`);
    if (MessageStatus === "failed" && ErrorCode) {
        console.log(`Error ${ErrorCode}: ${ErrorMessage}`);
    }
    res.sendStatus(204);
});
```

Status flow: `queued → sent → delivered` (or `undelivered`/`failed`)

### Webhook Signature Validation

**Python (Flask)**
```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])

@app.route("/incoming", methods=["POST"])
def incoming_message():
    if not validator.validate(request.url, request.form, request.headers.get("X-Twilio-Signature", "")):
        return "Forbidden", 403
    response = MessagingResponse()
    response.message("Hello!")
    return str(response)
```

**Node.js**
```javascript
const { validateRequest } = require("twilio");

app.post("/incoming", (req, res) => {
    const isValid = validateRequest(
        process.env.TWILIO_AUTH_TOKEN,
        req.headers["x-twilio-signature"],
        `https://${req.headers.host}${req.path}`,
        req.body
    );
    if (!isValid) return res.status(403).send("Forbidden");
    const twiml = new twilio.twiml.MessagingResponse();
    twiml.message("Hello!");
    res.type("text/xml").send(twiml.toString());
});
```

---

## CANNOT

- **Cannot exceed 15-second webhook response time** — Twilio retries on timeout
- **Cannot return arbitrary content types** — Use `Content-Type: text/xml` with TwiML for replies; `204` for status callbacks
- **Cannot use ngrok URLs across restarts** — URLs change on restart. Use a stable tunnel for persistent testing.
- **Cannot guarantee delivery confirmation** — Status callbacks are best-effort. `delivered` requires carrier confirmation.

---

## Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 11200 | HTTP retrieval failure — Twilio cannot reach your webhook URL | Verify endpoint is reachable (`curl -I` the URL), check DNS, firewall, and SSL certificate validity. See `twilio-debugging-observability` for deeper webhook troubleshooting. |

---

## Next Steps

- **Send outbound messages:** `twilio-send-message`
- **Manage sender pools:** `twilio-messaging-services`
