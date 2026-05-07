---
name: twilio-voice-twiml
description: >
  Build voice call logic using TwiML (Twilio Markup Language). Covers the
  core verbs (Say, Play, Gather, Dial, Record, Conference), generating TwiML
  with Python and Node.js SDKs, and a complete inbound call IVR example. Use
  this skill to define call behavior for inbound or outbound calls.
---

## Overview

TwiML is XML that Twilio executes during a call. Your server returns a TwiML document in response to a Twilio webhook POST, and Twilio executes it.

```
Caller → Twilio → POST to your webhook → Your server returns TwiML → Twilio executes it
```

---

## Prerequisites

- Twilio account with a voice-capable phone number
  — New to Twilio? See `twilio-account-setup`
- Webhook endpoint returning TwiML with `Content-Type: text/xml`
- SDK (for programmatic generation): `pip install twilio` / `npm install twilio`

---

## Quickstart

A minimal inbound call handler that greets the caller and presents a menu:

**Python (Flask)**
```python
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def handle_call():
    response = VoiceResponse()
    gather = response.gather(num_digits=1, action="/menu-choice")
    gather.say("Welcome to Acme. Press 1 for sales, 2 for support.")
    response.redirect("/voice")  # Loop if no input
    return str(response)

@app.route("/menu-choice", methods=["POST"])
def menu_choice():
    digit = request.form.get("Digits")
    response = VoiceResponse()
    if digit == "1":
        response.dial("+15551234567")
    elif digit == "2":
        response.say("Connecting to support.")
        response.dial("+15559876543")
    else:
        response.say("Invalid option.")
        response.redirect("/voice")
    return str(response)
```

**Node.js (Express)**
```node
const { VoiceResponse } = require("twilio").twiml;

app.post("/voice", (req, res) => {
    const response = new VoiceResponse();
    const gather = response.gather({ numDigits: 1, action: "/menu-choice" });
    gather.say("Welcome. Press 1 for sales, 2 for support.");
    response.redirect("/voice");
    res.type("text/xml").send(response.toString());
});

app.post("/menu-choice", (req, res) => {
    const digit = req.body.Digits;
    const response = new VoiceResponse();
    if (digit === "1") response.dial("+15551234567");
    else response.say("Invalid option.").redirect("/voice");
    res.type("text/xml").send(response.toString());
});
```

---

## Core Verbs

### Say — Text-to-speech

**Python**
```python
from twilio.twiml.voice_response import VoiceResponse

response = VoiceResponse()
response.say("Your appointment is confirmed.", voice="alice", language="en-US")
```

**Node.js**
```node
const { VoiceResponse } = require("twilio").twiml;
const response = new VoiceResponse();
response.say({ voice: "alice", language: "en-US" }, "Your appointment is confirmed.");
```

Voices: `alice` (default), `man`, `woman`, or Polly/Google TTS (e.g. `Polly.Joanna`).

### Gather — Collect keypad input or speech

**Python**
```python
response = VoiceResponse()
gather = response.gather(num_digits=1, action="/handle-input", method="POST")
gather.say("Press 1 for sales, press 2 for support.")
response.say("We did not receive your input.")  # Fallback if no input
```

**Node.js**
```node
const gather = response.gather({ numDigits: 1, action: "/handle-input", method: "POST" });
gather.say("Press 1 for sales, press 2 for support.");
response.say("We did not receive your input.");
```

Twilio POSTs collected digits to `action` as `Digits` parameter.

### Play — Play an audio file

**Python**
```python
response = VoiceResponse()
response.play("https://example.com/audio/greeting.mp3")
```

**Node.js**
```node
const response = new VoiceResponse();
response.play("https://example.com/audio/greeting.mp3");
```

Supported formats: MP3, WAV. URL must be publicly accessible.

### Dial — Connect to another number

**Python**
```python
from twilio.twiml.voice_response import Dial

response = VoiceResponse()
dial = Dial(action="/dial-complete")
dial.number("+15558675310")
response.append(dial)
```

**Node.js**
```node
const dial = response.dial({ action: "/dial-complete" });
dial.number("+15558675310");
```

### Record — Capture caller audio

**Python**
```python
response = VoiceResponse()
response.say("Leave a message after the beep.")
response.record(
    action="/recording-complete",
    max_length=60,
    transcribe=True,
    transcribe_callback="/transcription-ready"
)
```

**Node.js**
```node
const response = new VoiceResponse();
response.say("Leave a message after the beep.");
response.record({
    action: "/recording-complete",
    maxLength: 60,
    transcribe: true,
    transcribeCallback: "/transcription-ready",
});
```

### Voicemail — Record a message when no one answers

Use `<Dial>` with `action` URL + `<Record>` in the action handler. When the dial times out or the callee is busy, the action URL serves TwiML with `<Record>`.

**Python**
```python
# Primary TwiML — try to connect the call
response = VoiceResponse()
dial = Dial(action="/voicemail", timeout=20)  # 20 seconds before voicemail
dial.number("+15558675310")
response.append(dial)

# /voicemail handler — plays if no answer
def voicemail_handler(request):
    response = VoiceResponse()
    response.say("We missed your call. Please leave a message after the beep.")
    response.record(
        action="/recording-complete",
        max_length=120,
        transcribe=True,
        transcribe_callback="/transcription-ready",
        play_beep=True
    )
    response.say("We didn't receive a recording. Goodbye.")
    return str(response)
```

**Node.js**
```node
// Primary TwiML — try to connect the call
const response = new VoiceResponse();
const dial = response.dial({ action: "/voicemail", timeout: 20 });
dial.number("+15558675310");

// /voicemail handler — plays if no answer
app.post("/voicemail", (req, res) => {
    const response = new VoiceResponse();
    response.say("We missed your call. Please leave a message after the beep.");
    response.record({
        action: "/recording-complete",
        maxLength: 120,
        transcribe: true,
        transcribeCallback: "/transcription-ready",
        playBeep: true,
    });
    response.say("We didn't receive a recording. Goodbye.");
    res.type("text/xml").send(response.toString());
});
```

**Important:** `<Record>` captures the caller only (voicemail-style). It is NOT for recording two-party calls — see `twilio-call-recordings` for that.

### Conference — Multi-party calls

**Python**
```python
response = VoiceResponse()
dial = response.dial()
dial.conference(
    "Daily Standup",
    start_conference_on_enter=True,
    end_conference_on_exit=True
)
```

**Node.js**
```node
const response = new VoiceResponse();
const dial = response.dial();
dial.conference("Daily Standup", {
    startConferenceOnEnter: true,
    endConferenceOnExit: true,
});
```

### Pay — PCI-compliant payment collection

> **Critical warnings:**
> - Pay Connectors are **Console-only** — there is no REST API to create or manage connectors. Set up in Console > Voice > Pay Connectors before coding.
> - **PCI Mode is IRREVERSIBLE** once enabled on an account. Use a dedicated sub-account for payment calls.

**Python**
```python
response = VoiceResponse()
response.say("We'll now collect your payment.")
pay = Pay(
    payment_connector="stripe_connector",  # Name from Console setup
    charge_amount="49.99",
    currency="usd",
    action="/payment-complete",
    status_callback="/payment-status"
)
response.append(pay)
```

**Node.js**
```node
const response = new VoiceResponse();
response.say("We'll now collect your payment.");
response.pay({
    paymentConnector: "stripe_connector",
    chargeAmount: "49.99",
    currency: "usd",
    action: "/payment-complete",
    statusCallback: "/payment-status",
});
```

Supported processors: Stripe, Braintree, CardConnect. Card data routes directly to the processor — never touches your server.

---

## Production Deployment

### Webhook Hosting

For production, do NOT use ngrok. Deploy your TwiML server with HTTPS:

- **Requirement**: Public HTTPS URL, responds within 15 seconds, returns `Content-Type: text/xml`
- **Options**: Cloud Run, AWS Lambda + API Gateway, Railway, Render — any service with TLS and auto-scaling
- **Fallback URL**: Configure in Console (Phone Numbers > Active Numbers > select number) for when your primary server is unreachable

### State Between TwiML Requests

Each webhook request is stateless. To maintain conversation state across interactions:

- **URL query params**: Pass state in `action` URLs — `/next-step?language=es&dept=sales`
- **Session store**: Use Redis or a database keyed by `CallSid`
- **Do NOT use in-memory state** — your server may scale to multiple instances

### Monitoring

- **Status callbacks**: Track call lifecycle events (`statusCallback` on the call or number config)
- **Voice Insights**: Automatic quality metrics per call (Console > Monitor > Insights)
- **Debugger**: Console > Monitor > Errors for TwiML parsing failures and webhook timeouts
- **Fallback URLs**: Always configure a fallback TwiML URL — serves a graceful message if your primary endpoint fails

---

## Webhook Request Parameters

| Parameter | Description |
|-----------|-------------|
| `CallSid` | Unique call identifier |
| `From` | Caller's number |
| `To` | Called number |
| `CallStatus` | Current status |
| `Direction` | `inbound` or `outbound-api` |

---

## CANNOT

- **Cannot return TwiML without correct content type** — Must use `Content-Type: text/xml`
- **Cannot exceed 15-second webhook response time** — Twilio times out and falls back
- **Cannot exceed 4,096 characters in `<Say>` verb** — Split longer text across multiple `<Say>` elements
- **Cannot create Pay Connectors via API** — Pay Connectors are Console-only (Console > Voice > Pay Connectors). No REST API exists for connector management.
- **Cannot reverse PCI Mode** — Once enabled on an account, PCI Mode is permanent and account-wide. Use a dedicated sub-account for payment calls.
- **Cannot use `<Record>` for two-party call recording** — `<Record>` captures the caller only (voicemail-style). For dual-channel recording of both parties, use `record=True` on `calls.create()` or the Recordings API.

---

## Next Steps

- **Place outbound calls (AMD, conferencing):** `twilio-voice-outbound-calls`
- **AI voice agents with real-time speech/LLM:** `twilio-voice-conversation-relay`
