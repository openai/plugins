---
name: twilio-webhook-architecture
description: >
  Design, secure, and operate Twilio webhook endpoints. Covers inbound event
  handling, status callbacks, signature validation, connection overrides for
  retry and timeout tuning, local development tunneling, and production
  hardening. Use this skill whenever an agent needs to receive HTTP callbacks
  from Twilio for any product -- messaging, voice, verify, or event streams.
---

## Overview

Twilio delivers events to your application via HTTP callbacks (webhooks). Inbound messages and calls trigger webhooks that expect a TwiML response; status callbacks and event streams push delivery and lifecycle data asynchronously. This skill covers the cross-product patterns that apply to every webhook integration.

---

## Prerequisites

- Twilio account with a phone number or service configured with a webhook URL
  -- New to Twilio? See `twilio-account-setup`
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` -- see `twilio-iam-auth-setup`
- SDK: `pip install twilio flask` / `npm install twilio express`
- Publicly accessible HTTPS endpoint (see Local Development section below)

---

## Quickstart

Receive an inbound SMS and validate the request signature before replying.

**Python (Flask)**
```python
import os
from flask import Flask, request, abort
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])

@app.route("/sms", methods=["POST"])
def incoming_sms():
    sig = request.headers.get("X-Twilio-Signature", "")
    if not validator.validate(request.url, request.form, sig):
        abort(403)
    resp = MessagingResponse()
    resp.message(f"Got: {request.form.get('Body')}")
    return str(resp), 200, {"Content-Type": "text/xml"}
```

**Node.js (Express)**
```node
const express = require("express");
const twilio = require("twilio");
const app = express();
app.use(express.urlencoded({ extended: false }));

app.post("/sms", (req, res) => {
    const valid = twilio.validateRequest(
        process.env.TWILIO_AUTH_TOKEN,
        req.headers["x-twilio-signature"],
        `https://${req.headers.host}${req.originalUrl}`,
        req.body
    );
    if (!valid) return res.status(403).send("Forbidden");
    const twiml = new twilio.twiml.MessagingResponse();
    twiml.message(`Got: ${req.body.Body}`);
    res.type("text/xml").send(twiml.toString());
});
```

Set your webhook URL in Console: **Phone Numbers > Active Numbers > (your number) > Messaging > "A Message Comes In"**.

---

## Key Patterns

### 1. Webhook Types Across Products

| Webhook type | Trigger | Expected response | Products |
|---|---|---|---|
| Inbound event | Message received / call answered | TwiML (XML) | Messaging, Voice |
| Status callback | Resource state change | `200` or `204` (no body required) | Messaging, Voice, Verify, Video |
| Action URL | TwiML verb completes (`<Gather>`, `<Record>`) | Next TwiML | Voice |
| Recording status | Recording processing completes | `200` or `204` | Voice |
| Debugger event | Error or warning on account | `200` or `204` | All |
| Event Streams | Any subscribed event | `200` or `204` | All (via Sink) |

### 2. Signature Validation

Twilio signs every webhook with an `X-Twilio-Signature` header (HMAC-SHA1 using your Auth Token). Always validate before processing.

**Form-encoded requests (`application/x-www-form-urlencoded`):**

Pass the full URL and POST body parameters to the validator.

**Python**
```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
is_valid = validator.validate(request.url, request.form, request.headers.get("X-Twilio-Signature", ""))
```

**Node.js**
```node
const { validateRequest } = require("twilio");

const isValid = validateRequest(
    process.env.TWILIO_AUTH_TOKEN,
    req.headers["x-twilio-signature"],
    `https://${req.headers.host}${req.originalUrl}`,
    req.body
);
```

**JSON requests (`application/json`):**

Twilio appends a `bodySHA256` query parameter to your URL. Use the SDK's JSON-specific validation.

**Python**
```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
is_valid = validator.validate_body(
    request.url,
    request.get_data(as_text=True),
    request.headers.get("X-Twilio-Signature", "")
)
```

**Node.js**
```node
const twilio = require("twilio");

// Use express.raw() or a verify callback to preserve the raw body
const isValid = twilio.validateRequestWithBody(
    process.env.TWILIO_AUTH_TOKEN,
    req.headers["x-twilio-signature"],
    `https://${req.headers.host}${req.originalUrl}`,
    req.rawBody  // must be the exact bytes Twilio sent, not JSON.stringify(req.body)
);
```

**Critical:** Use the SDK validator. Do not implement your own -- Twilio may add parameters without notice, and the exact algorithm (including port handling) has edge cases the SDK handles.

### 3. Status Callback Handling

Status callbacks are asynchronous POST requests Twilio sends when a resource changes state. They do not expect TwiML -- return `200` or `204`.

**Messaging status flow:** `queued` -> `sent` -> `delivered` (or `undelivered` / `failed`)

When using Messaging Services, the flow starts with `accepted` -> `queued` -> ...

**Voice status events:** `initiated`, `ringing`, `answered`, `completed`

Subscribe to specific events via `StatusCallbackEvent` parameter.

Status callbacks are signed with `X-Twilio-Signature` like all Twilio webhooks. Validate before acting on the payload -- an unvalidated endpoint lets anyone forge delivery status and drive downstream logic.

**Python (Flask) -- messaging status handler**
```python
@app.route("/status", methods=["POST"])
def message_status():
    sig = request.headers.get("X-Twilio-Signature", "")
    if not validator.validate(request.url, request.form, sig):
        return "Forbidden", 403
    sid = request.form.get("MessageSid")
    status = request.form.get("MessageStatus")
    error_code = request.form.get("ErrorCode")
    if status in ("failed", "undelivered") and error_code:
        print(f"Delivery failed {sid}: error {error_code}")
    return "", 204
```

**Node.js (Express) -- voice status handler**
```node
app.post("/call-status", (req, res) => {
    const valid = twilio.validateRequest(
        process.env.TWILIO_AUTH_TOKEN,
        req.headers["x-twilio-signature"],
        `https://${req.headers.host}${req.originalUrl}`,
        req.body
    );
    if (!valid) return res.status(403).send("Forbidden");
    const { CallSid, CallStatus, Duration } = req.body;
    console.log(`${CallSid}: ${CallStatus} (${Duration}s)`);
    res.sendStatus(204);
});
```

**Attach status callbacks when creating resources:**

```python
# Messaging
message = client.messages.create(
    to="+15558675310", from_="+15017122661", body="Hello!",
    status_callback="https://yourapp.com/status"
)

# Voice
call = client.calls.create(
    to="+15558675310", from_="+15017122661",
    url="https://yourapp.com/voice",
    status_callback="https://yourapp.com/call-status",
    status_callback_event=["initiated", "ringing", "answered", "completed"],
    status_callback_method="POST"
)
```

### 4. Connection Overrides (Retry and Timeout Tuning)

Append URL fragments to any webhook URL to override default connection behavior. Fragments are not included in signature computation.

**Format:** `https://yourapp.com/webhook#key=value&key=value`

| Parameter | Key | Default | Range | Description |
|---|---|---|---|---|
| Connect Timeout | `ct` | 5000ms | 100-10000 | TCP connection timeout |
| Read Timeout | `rt` | 15000ms | 100-15000 | Time to wait for first response byte |
| Total Time | `tt` | 15000ms | 100-15000 | Total time for all retries |
| Retry Count | `rc` | 1 | 0-5 | Number of retry attempts |
| Retry Policy | `rp` | `ct` | `4xx`, `5xx`, `ct`, `rt`, `all` | What triggers a retry |
| Edge Location | `e` | `ashburn` | `ashburn`, `dublin`, `frankfurt`, `sao-paulo`, `singapore`, `sydney`, `tokyo`, `umatilla` | Egress edge |

**Examples:**

```text
# Retry up to 3 times on connection or read timeout
https://yourapp.com/sms#rc=3&rp=ct,rt

# Fast failover: 1s connect timeout, 2 retries
https://yourapp.com/voice#ct=1000&rc=2

# Rotate edge locations on retry
https://yourapp.com/status#e=ashburn,dublin&rc=1
```

Twilio adds an `I-Twilio-Idempotency-Token` header on retries for deduplication.

**Limitations:** Connection overrides are not available on Twilio Conversations or Frontline webhooks. Voice webhooks have a hard 15-second ceiling regardless of override values.

### 5. Configure Webhook URLs via API

**Python**
```python
# Phone number -- messaging
client.incoming_phone_numbers("PNxxxxxxxxxx").update(
    sms_url="https://yourapp.com/sms",
    sms_method="POST",
    sms_fallback_url="https://yourapp.com/sms-fallback",
    sms_fallback_method="POST"
)

# Phone number -- voice
client.incoming_phone_numbers("PNxxxxxxxxxx").update(
    voice_url="https://yourapp.com/voice",
    voice_method="POST",
    voice_fallback_url="https://yourapp.com/voice-fallback",
    voice_fallback_method="POST",
    status_callback="https://yourapp.com/call-status",
    status_callback_method="POST"
)
```

**Node.js**
```node
// Phone number -- messaging
await client.incomingPhoneNumbers("PNxxxxxxxxxx").update({
    smsUrl: "https://yourapp.com/sms",
    smsMethod: "POST",
    smsFallbackUrl: "https://yourapp.com/sms-fallback",
    smsFallbackMethod: "POST",
});

// Phone number -- voice
await client.incomingPhoneNumbers("PNxxxxxxxxxx").update({
    voiceUrl: "https://yourapp.com/voice",
    voiceMethod: "POST",
    voiceFallbackUrl: "https://yourapp.com/voice-fallback",
    voiceFallbackMethod: "POST",
    statusCallback: "https://yourapp.com/call-status",
    statusCallbackMethod: "POST",
});
```

### 6. Local Development with Tunnels

Twilio cannot reach `localhost`. Use a tunnel to expose your local server.

**ngrok (recommended for development):**
```bash
ngrok http 5000
# Copy the HTTPS URL, e.g. https://abc123.ngrok-free.app
```

Then set the ngrok URL as your webhook in Console or via API.

**Twilio CLI:**
```bash
# Install and use the CLI webhook plugin
twilio phone-numbers:update +15017122661 \
  --sms-url="https://abc123.ngrok-free.app/sms"
```

**ngrok caveats:**
- Free tier URLs change on restart -- update Twilio config each time
- Free tier sessions expire after hours -- use a stable host for anything beyond quick tests
- For persistent local dev, use ngrok with a custom domain (paid) or deploy to a cloud host

### 7. Event Streams (Webhook Sink)

For high-volume or cross-product event delivery, use Event Streams instead of per-resource status callbacks. Event Streams deliver events to a Sink (webhook, Kinesis, or Segment). The Twilio SDK does not wrap Event Streams -- use `requests` / `fetch` directly.

**Python -- create a webhook sink and subscribe to error events**
```python
import os, requests

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

# Create a webhook sink
sink = requests.post(
    "https://events.twilio.com/v1/Sinks",
    auth=(account_sid, auth_token),
    data={
        "Description": "Error log sink",
        "SinkType": "webhook",
        "SinkConfiguration": '{"destination": "https://yourapp.com/events", "method": "POST"}'
    }
).json()

# Subscribe to error log events
requests.post(
    "https://events.twilio.com/v1/Subscriptions",
    auth=(account_sid, auth_token),
    data={
        "Description": "Error log subscription",
        "SinkSid": sink["sid"],
        "Types": '[{"type": "com.twilio.error-logs.error.logged"}]'
    }
)
```

Sink types: `webhook`, `kinesis`, `segment`. Subscriptions filter which event types route to which sinks.

### 8. HTTP Authentication for Webhook URLs

Twilio supports HTTP Basic and Digest authentication. Embed credentials in the URL:

```text
https://username:password@yourapp.com/sms
```

This provides an additional layer of protection beyond signature validation. Note: these credentials are visible in Console webhook configuration and may appear in server access logs -- rotate them independently of your Auth Token.

---

## Common Webhook Parameters

### Inbound SMS

| Parameter | Description |
|---|---|
| `MessageSid` | Unique message identifier |
| `AccountSid` | Your Twilio account SID |
| `From` | Sender phone number (E.164) |
| `To` | Your Twilio number |
| `Body` | Message text |
| `NumMedia` | Number of media attachments |
| `MediaUrl0..N` | URL of each media attachment |
| `MediaContentType0..N` | MIME type of each attachment |

### Inbound Voice Call

| Parameter | Description |
|---|---|
| `CallSid` | Unique call identifier |
| `AccountSid` | Your Twilio account SID |
| `From` | Caller phone number (E.164) |
| `To` | Your Twilio number |
| `CallStatus` | `queued`, `ringing`, `in-progress`, `completed`, `busy`, `failed`, `no-answer`, `canceled` |
| `Direction` | `inbound` |
| `ForwardedFrom` | Number that forwarded the call (if applicable) |

### Message Status Callback

| Parameter | Description |
|---|---|
| `MessageSid` | Unique message identifier |
| `MessageStatus` | `accepted`, `queued`, `sending`, `sent`, `delivered`, `undelivered`, `failed`, `read` |
| `ErrorCode` | Twilio error code (present on `failed`/`undelivered`) |
| `ErrorMessage` | Human-readable error description |

### Debugger Event Callback

| Parameter | Description |
|---|---|
| `Sid` | Debugger event identifier |
| `AccountSid` | Account that generated the event |
| `Level` | `Error` or `Warning` |
| `Timestamp` | ISO 8601 time of occurrence |
| `Payload` | JSON with `resource_sid`, `error_code`, `more_info`, `webhook` (request/response details) |

---

## CANNOT

- **Cannot exceed 15-second voice webhook response time** — Twilio hangs up or falls back. Messaging webhooks retry on timeout.
- **Cannot use HTTP in production** — HTTPS required. No self-signed certificates. Do not pin Twilio certificates — they rotate without notice.
- **Cannot allowlist Twilio by IP** — Webhooks come from dynamic IPs. Use signature validation instead.
- **Cannot guarantee status callback delivery or order** — Best-effort. Implement idempotency using `MessageSid` + `MessageStatus` or `CallSid` + `CallStatus` as composite keys.
- **Cannot redirect without losing POST parameters** — HTTP 301/302 redirects cause Twilio to follow with GET, dropping `Digits`, `RecordingUrl`, etc.
- **Cannot use connection overrides on Conversations or Frontline webhooks** — Not supported for these products

---

## Next Steps

- **Receive inbound SMS:** `twilio-messaging-webhooks`
- **Voice call handling:** `twilio-voice-twiml`
- **Scale webhook handling:** `twilio-reliability-patterns`
- **Debug webhook failures:** `twilio-debugging-observability`
- **Secure credentials:** `twilio-iam-auth-setup`
