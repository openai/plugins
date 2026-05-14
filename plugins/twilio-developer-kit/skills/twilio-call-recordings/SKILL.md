---
name: twilio-call-recordings
description: >
  Record Twilio voice calls correctly. Covers the critical distinction
  between Record verb (voicemail) and Dial record (call recording),
  dual-channel for QA, mid-call pause for PCI, Conference recording, and
  the ConversationRelay workaround. Use this skill whenever you need to
  capture call audio for compliance, QA, or analytics.
---

## Overview

Twilio offers multiple recording methods. Choosing the wrong one is the **#1 developer mistake** in voice — using `<Record>` when you mean `<Dial record>` produces voicemail behavior instead of call recording.

| Method | What it does | Use when |
|--------|-------------|----------|
| `<Record>` verb | Records the CALLER only (voicemail-style) | Leaving a message, capturing input |
| `<Dial record>` | Records BOTH parties on a call | Call recording for two-party calls |
| `<Start><Recording>` | Starts a recording alongside other verbs | ConversationRelay, multi-verb flows |
| Conference `record` | Records the conference mix | Multi-party calls |
| Recordings REST API | Programmatic control mid-call | Pause during payment (PCI) |

---

## Prerequisites

- Twilio account with a voice-capable phone number — see `twilio-account-setup`
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`
- SDK: `pip install twilio` / `npm install twilio`
- A webhook endpoint for recording status callbacks
- **Compliance check:** Recording consent requirements vary by jurisdiction — see `twilio-compliance-traffic`

---

## Quickstart

### Record a Two-Party Call (Most Common)

Use `<Dial record>` — NOT `<Record>`.

**Python (Flask)**
```python
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def incoming_call():
    response = VoiceResponse()
    response.say("This call may be recorded for quality assurance.")
    dial = response.dial(
        record="record-from-answer-dual",  # dual-channel: agent on one, caller on other
        recording_status_callback="https://yourapp.com/recording-status"
    )
    dial.number("+15558675310")  # agent's phone
    return str(response)
```

**Node.js (Express)**
```node
app.post("/voice", (req, res) => {
    const response = new VoiceResponse();
    response.say("This call may be recorded for quality assurance.");
    const dial = response.dial({
        record: "record-from-answer-dual",
        recordingStatusCallback: "https://yourapp.com/recording-status",
    });
    dial.number("+15558675310");
    res.type("text/xml").send(response.toString());
});
```

### Handle the Recording Status Callback

> **Security:** Validate `X-Twilio-Signature` on recording callbacks in production. Without validation, attackers could POST fake recording URLs to your endpoint.

**Python (Flask)**
```python
@app.route("/recording-status", methods=["POST"])
def recording_status():
    recording_sid = request.form["RecordingSid"]
    recording_url = request.form["RecordingUrl"]
    call_sid = request.form["CallSid"]
    status = request.form["RecordingStatus"]  # "completed", "failed"
    duration = request.form.get("RecordingDuration", 0)

    if status == "completed":
        # Store recording reference
        save_recording(call_sid, recording_sid, recording_url, duration)

    return "", 200
```

---

## Key Patterns

### Recording Modes for `<Dial record>`

| Mode | What's recorded | Use case |
|------|----------------|----------|
| `record-from-answer` | Single channel, both parties mixed | Simple recording |
| `record-from-answer-dual` | Dual channel — caller on left, agent on right | QA (separate agent/caller audio) |
| `record-from-ringing` | Records from ring, not answer | Capture ring time + full call |
| `record-from-ringing-dual` | Dual channel from ring | QA with ring time |

**Always use `dual` for QA and analytics.** Dual-channel lets speech analytics tools (like Conversation Intelligence) distinguish agent from caller.

### Conference Recording

Record multi-party calls via the Conference:

**Python**
```python
response = VoiceResponse()
dial = response.dial()
dial.conference(
    "support-room-123",
    record="record-from-start",  # Records from when conference starts
    recording_status_callback="https://yourapp.com/conf-recording-status"
)
```

**Note:** Conference recording captures the main audio mix. Coach/whisper audio is NOT included. See `twilio-conference-calls`.

### ConversationRelay Recording

**Critical:** `record:true` on the REST API call is **silently ignored** with ConversationRelay. No error. No recording.

**Correct approach:** Use `<Start><Recording>` in TwiML before `<Connect>`:

**Python**
```python
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response.say("This call may be recorded.")
    
    # Start recording BEFORE connecting ConversationRelay
    start = Start()
    start.recording(
        recording_status_callback="https://yourapp.com/recording-status",
        recording_status_callback_event="completed"
    )
    response.append(start)
    
    # Now connect ConversationRelay
    connect = Connect()
    connect.conversation_relay(url="wss://yourapp.com/ws/voice")
    response.append(connect)
    
    return str(response)
```

**Node.js**
```node
app.post("/voice", (req, res) => {
    const response = new VoiceResponse();
    response.say("This call may be recorded.");
    
    const start = response.start();
    start.recording({
        recordingStatusCallback: "https://yourapp.com/recording-status",
        recordingStatusCallbackEvent: "completed",
    });
    
    const connect = response.connect();
    connect.conversationRelay({ url: "wss://yourapp.com/ws/voice" });
    
    res.type("text/xml").send(response.toString());
});
```

### Mid-Call Pause for PCI Compliance

Pause recording when a customer provides payment information:

**Python**
```python
def pause_recording_for_payment(call_sid, recording_sid):
    """Pause recording during credit card capture."""
    client.calls(call_sid).recordings(recording_sid).update(
        status="paused"
    )

def resume_recording(call_sid, recording_sid):
    """Resume recording after payment processed."""
    client.calls(call_sid).recordings(recording_sid).update(
        status="in-progress"
    )
```

**Node.js**
```node
async function pauseForPayment(callSid, recordingSid) {
    await client.calls(callSid).recordings(recordingSid).update({
        status: "paused",
    });
}

async function resumeRecording(callSid, recordingSid) {
    await client.calls(callSid).recordings(recordingSid).update({
        status: "in-progress",
    });
}
```

**PCI DSS:** Never record card numbers. Use Twilio's `<Pay>` verb when possible. If collecting verbally, pause recording for the duration. PCI Mode is IRREVERSIBLE and account-wide — use a sub-account if only some calls need PCI.

### Accessing Recordings

**Python**
```python
# List recordings for a specific call
recordings = client.recordings.list(call_sid=call_sid)

for recording in recordings:
    print(f"SID: {recording.sid}")
    print(f"Duration: {recording.duration}s")
    print(f"URL: https://api.twilio.com{recording.uri.replace('.json', '.mp3')}")

# Download a recording
import requests as req
audio = req.get(
    f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{recording_sid}.mp3",
    auth=(account_sid, auth_token)
)
with open("recording.mp3", "wb") as f:
    f.write(audio.content)

# Delete a recording (GDPR right to deletion)
client.recordings(recording_sid).delete()
```

### Recording Storage & Retention

| Feature | Default | Notes |
|---------|---------|-------|
| Storage location | Twilio cloud | Can configure external storage (S3, GCS) |
| Retention | Indefinite | Delete manually via API or set auto-delete policy |
| Formats | WAV (default), MP3 | Request MP3 by appending `.mp3` to URL |
| Encryption | At rest | Additional encryption with PCI Mode |

---

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Recording captures only caller (no agent) | Used `<Record>` verb instead of `<Dial record>` | Switch to `<Dial record="record-from-answer">` |
| No recording at all | Used REST API `record:true` with ConversationRelay | Use `<Start><Recording>` in TwiML |
| Recording is empty / silent | Webhook endpoint unreachable, recording never started | Check StatusCallback URL reachability |
| Recording has both parties on same channel | Used `record-from-answer` (mono) | Use `record-from-answer-dual` for separate channels |
| Coach audio missing from conference recording | Expected behavior — coach audio isn't in the mix | Record coach's call leg separately |

---

## CANNOT

- **`recordingTrack` has no observable effect via TwiML** — The `<Start><Recording>` TwiML parameter `recordingTrack` does not isolate tracks. Use the Recordings REST API with `recordingTrack` for actual track isolation.
- **Cannot start API recordings on ConversationRelay calls** — REST API `record:true` is silently ignored ("not eligible for recording"). Must use `<Start><Recording>` before `<Connect>` in TwiML.
- **Cannot pause/resume recordings via TwiML** — Only available via the REST API (`update` with `status="paused"` or `status="in-progress"`).
- **Cannot get dual-channel conference recordings** — Conference recording is always mono (mixed).
- **Cannot get dual-channel from Calls API without explicit param** — `Record=true` defaults to mono. Must specify `recordingChannels: 'dual'`.
- **Cannot transcribe PCI-mode recordings** — Recordings created while PCI mode was enabled cannot be transcribed, even after PCI is disabled.
- **Cannot use `<Record>` verb for call recording** — `<Record>` captures the caller only (voicemail-style). Use `<Dial record>` or `<Start><Recording>` for call recording.
- **Cannot capture coach/whisper audio in conference recordings** — Supervisor whisper is excluded from the mix
- **Cannot reverse PCI Mode** — PCI Mode is irreversible and account-wide. Once enabled, all recordings are encrypted.
- **Cannot auto-delete recordings without configuration** — Recordings are retained indefinitely unless you configure auto-deletion
- **Cannot avoid larger file sizes with dual-channel** — Dual-channel recordings are ~2x the size of mono. Factor into storage costs.

---

## Next Steps

- **Conference calls:** `twilio-conference-calls`
- **Agent routing:** `twilio-taskrouter-routing`
- **Compliance:** `twilio-compliance-traffic`
- **Debug recording issues:** `twilio-debugging-observability`
