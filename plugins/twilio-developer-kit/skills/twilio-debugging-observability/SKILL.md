---
name: twilio-debugging-observability
description: >
  Debug Twilio integrations and set up production observability. Covers the
  Console Debugger, Monitor Alerts API, Event Streams for error log streaming,
  status callback tracking, common error codes, and a systematic debugging
  workflow. Use this skill whenever a Twilio integration produces errors,
  messages fail to deliver, calls drop unexpectedly, or you need to set up
  monitoring for a production deployment.
---

## Overview

Twilio provides several layers of debugging and observability: the Console Debugger for interactive troubleshooting, the Monitor REST API for programmatic alert queries, Event Streams for real-time error streaming, and status callbacks for per-resource delivery tracking. This skill covers the systematic approach to diagnosing issues and setting up production monitoring.


---

## Prerequisites

- Twilio account with `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` -- see `twilio-iam-auth-setup`
- SDK: `pip install twilio requests` / `npm install twilio`
- For Event Streams: a publicly accessible HTTPS endpoint or AWS Kinesis stream

---

## Quickstart

Check for recent errors on your account using the Monitor Alerts API.

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

alerts = client.monitor.alerts.list(log_level="error", limit=10)
for alert in alerts:
    print(f"{alert.date_created}: [{alert.error_code}] {alert.alert_text}")
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const alerts = await client.monitor.alerts.list({ logLevel: "error", limit: 10 });
alerts.forEach(a => {
    console.log(`${a.dateCreated}: [${a.errorCode}] ${a.alertText}`);
});
```

---

## Key Patterns

### 1. Systematic Debugging Workflow

When something fails, work through these layers in order:

```
1. Check status callbacks FIRST
   (Did your endpoint receive delivery/call status? What error code?)
   |
2. Check the resource directly via REST API
   (GET /Messages/{sid} or /Calls/{sid} — current state + error_code)
   |
3. Check number reputation / sender registration
   (Is the number spam-flagged? Is A2P 10DLC registered? Toll-free verified?)
   |
4. Check the Console Debugger for webhook/TwiML errors
   (Console > Monitor > Errors — shows HTTP request/response details)
   |
5. Check your webhook endpoint
   (Is it reachable? Responding within 15s? Returning valid TwiML/200?)
   |
6. Query Monitor Alerts API or Event Streams
   (For patterns across many messages/calls, or historical analysis)
```

**Why status callbacks first:** Status callbacks tell you the exact error code for the specific message or call that failed. The Console Debugger aggregates errors across your account and may not surface the one you're looking for. Start specific, then broaden.

**Number reputation checklist:**
- SMS 30007 (carrier filtering) → Check A2P 10DLC registration status, content for spam triggers
- SMS 30034 → Sender not registered for A2P 10DLC — register brand + campaign
- Calls going to voicemail / "Spam Likely" → Check STIR/SHAKEN attestation, Voice Integrity status (see `twilio-numbers-senders`)
- Toll-free SMS blocked → Check toll-free verification status

**Rule of thumb:** If status callbacks show `delivered` but the user says they didn't receive it, the issue is on the carrier/device side (not Twilio). If the Console Debugger shows no errors at all, the problem is in your application (webhook, TwiML, business logic).

### 2. Console Debugger

The [Console Debugger](https://console.twilio.com/us1/monitor/logs/debugger) shows errors and warnings for your account in real time.

Each entry includes:
- The exact error or warning that occurred
- Potential causes and suggested solutions
- The full HTTP request and response for the associated webhook

**Configure a Debugger webhook** for real-time alerting:

Console > Monitor > Logs > Debugger > (gear icon) > set Callback URL

Debugger webhook POST parameters:

| Parameter | Description |
|---|---|
| `Sid` | Debugger event identifier |
| `AccountSid` | Account that generated the event |
| `Level` | `Error` or `Warning` |
| `Timestamp` | ISO 8601 time |
| `Payload` | JSON: `resource_sid`, `error_code`, `more_info`, `webhook` (full request/response) |

**Python (Flask) -- debugger webhook handler**
```python
import json, os
from flask import Flask, request
from twilio.request_validator import RequestValidator

app = Flask(__name__)
validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])

@app.route("/debugger", methods=["POST"])
def debugger_event():
    sig = request.headers.get("X-Twilio-Signature", "")
    if not validator.validate(request.url, request.form, sig):
        return "Forbidden", 403
    level = request.form.get("Level")
    payload = json.loads(request.form.get("Payload", "{}"))
    error_code = payload.get("error_code")
    resource_sid = payload.get("resource_sid")
    msg = payload.get("more_info", {}).get("msg", "")
    print(f"[{level}] Error {error_code} on {resource_sid}: {msg}")
    return "", 204
```

**Node.js (Express) -- debugger webhook handler**
```node
const express = require("express");
const twilio = require("twilio");
const app = express();
app.use(express.urlencoded({ extended: false }));

app.post("/debugger", (req, res) => {
    const valid = twilio.validateRequest(
        process.env.TWILIO_AUTH_TOKEN,
        req.headers["x-twilio-signature"],
        `https://${req.headers.host}${req.originalUrl}`,
        req.body
    );
    if (!valid) return res.status(403).send("Forbidden");
    const payload = JSON.parse(req.body.Payload || "{}");
    const { error_code, resource_sid } = payload;
    const msg = payload.more_info?.msg || "";
    console.log(`[${req.body.Level}] Error ${error_code} on ${resource_sid}: ${msg}`);
    res.sendStatus(204);
});
```

### 3. Monitor Alerts API

The Monitor REST API (`monitor.twilio.com/v1/Alerts`) provides programmatic access to error and warning logs. Individual alert instances include the full HTTP request and response data.

**Python -- query alerts with date filtering**
```python
from datetime import datetime, timedelta

# Alerts from the last 24 hours
start = datetime.utcnow() - timedelta(days=1)
alerts = client.monitor.alerts.list(
    start_date=start,
    log_level="error",
    limit=50
)

for alert in alerts:
    print(f"{alert.date_created} [{alert.error_code}]")
    # Fetch full details including HTTP request/response
    detail = client.monitor.alerts(alert.sid).fetch()
    print(f"  Request URL: {detail.request_url}")
    print(f"  Response body: {detail.response_body}")
```

**Node.js -- query alerts with date filtering**
```node
const startDate = new Date(Date.now() - 24 * 60 * 60 * 1000);
const alerts = await client.monitor.alerts.list({
    startDate,
    logLevel: "error",
    limit: 50,
});

for (const alert of alerts) {
    console.log(`${alert.dateCreated} [${alert.errorCode}]`);
    const detail = await client.monitor.alerts(alert.sid).fetch();
    console.log(`  Request URL: ${detail.requestUrl}`);
    console.log(`  Response body: ${detail.responseBody}`);
}
```

**Retention:** Enterprise accounts: 13 months. Free accounts: 30 days.

### 4. Monitor Events API

The Events resource (`monitor.twilio.com/v1/Events`) tracks all changes to Twilio resources -- phone number provisioning, account settings, recording access, API key creation, and more.

**Python -- audit recent account changes**
```python
events = client.monitor.events.list(limit=20)
for event in events:
    print(f"{event.event_date}: {event.event_type}")
    print(f"  Resource: {event.resource_type} ({event.resource_sid})")
    print(f"  Actor: {event.actor_type} ({event.actor_sid}) from {event.source_ip_address}")
```

Each event captures: event type, resource, actor (who triggered it), source (API / Console / Twilio admin), and IP address.

**Use cases:**
- Audit who changed a phone number's webhook URL
- Track API key creation and deletion
- Detect unexpected configuration changes
- Feed events into a SIEM for security monitoring

### 5. Event Streams for Error Log Streaming

For production monitoring, stream errors to your infrastructure in real time using Event Streams. The Twilio SDK does not wrap Event Streams -- use `requests` / `fetch` directly.

**Python -- set up error log streaming to a webhook**
```python
import os, requests

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

# Step 1: Create a webhook sink
sink = requests.post(
    "https://events.twilio.com/v1/Sinks",
    auth=(account_sid, auth_token),
    data={
        "Description": "Error monitoring sink",
        "SinkType": "webhook",
        "SinkConfiguration": '{"destination": "https://yourapp.com/twilio-errors", "method": "POST"}'
    }
).json()

# Step 2: Subscribe to error log events
subscription = requests.post(
    "https://events.twilio.com/v1/Subscriptions",
    auth=(account_sid, auth_token),
    data={
        "Description": "Error log subscription",
        "SinkSid": sink["sid"],
        "Types": '[{"type": "com.twilio.error-logs.error.logged"}]'
    }
).json()

print(f"Sink: {sink['sid']}, Subscription: {subscription['sid']}")
```

**Sink types:** `webhook`, `kinesis`, `segment`

**Useful event types for observability:**

| Event type | Description |
|---|---|
| `com.twilio.error-logs.error.logged` | All errors and warnings on account |
| `com.twilio.messaging.message.delivered` | Message delivered successfully |
| `com.twilio.messaging.message.undelivered` | Message delivery failed |
| `com.twilio.voice.insights.call-summary` | Post-call quality and status summary |

### 6. Status Callback Monitoring

Status callbacks are the most granular observability mechanism -- they fire for individual resource state changes.

**Message delivery tracking:**
```python
# Attach when sending
message = client.messages.create(
    to="+15558675310", from_="+15017122661", body="Hello!",
    status_callback="https://yourapp.com/msg-status"
)
```

**Call lifecycle tracking:**
```python
call = client.calls.create(
    to="+15558675310", from_="+15017122661",
    url="https://yourapp.com/voice",
    status_callback="https://yourapp.com/call-status",
    status_callback_event=["initiated", "ringing", "answered", "completed"]
)
```

**Recording completion tracking:**
```python
# In TwiML
response = VoiceResponse()
response.record(
    recording_status_callback="https://yourapp.com/recording-status",
    recording_status_callback_event="completed absent failed"
)
```

Recording status values: `in-progress`, `completed`, `absent`, `failed`. The `RecordingUrl` is available when status is `completed`.

### 7. Debugging Webhooks

When Twilio can't reach your webhook or receives an error, the problem is often in your infrastructure.

**Common causes and fixes:**

| Symptom | Likely cause | Fix |
|---|---|---|
| Error 11200 in Debugger | Webhook URL returned non-200 / unreachable | Verify endpoint is live: `curl -I https://yourapp.com/sms` |
| Error 11205 | HTTP connection failure (port closed, refused, firewall) | Verify server is running and port is open: `curl -I https://yourapp.com/sms` |
| Error 12100 | TwiML document could not be parsed | Check for debug output, BOM characters, or malformed XML |
| Parameters missing after redirect | HTTP 301/302 strips POST body | Fix URL to avoid redirect (add/remove `www.`, use HTTPS directly) |
| Webhook works locally but not deployed | Tunnel expired or firewall | Use `curl` from an external host to test |
| Intermittent failures | ngrok session expired / recycled | Deploy to a stable host for anything beyond quick tests |

**Test webhooks manually:**
```bash
# Simulate an inbound SMS webhook
curl -X POST https://yourapp.com/sms \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "Body=Test message" \
  -d "MessageSid=SM00000000000000000000000000000000"
```

**Browser testing:** Visit your webhook URL in Firefox -- it highlights XML errors in the response.

### 8. Common Error Codes

| Code | Name | Cause | Fix |
|---|---|---|---|
| 11200 | HTTP retrieval failure | Twilio cannot reach your webhook URL | Check URL, DNS, firewall, SSL cert |
| 11205 | HTTP connection failure | Webhook endpoint refused connection | Verify server is running and port is open |
| 11751 | Media download failure | MMS media URL unreachable | Check media URL accessibility |
| 12100 | Document parse failure | TwiML is not valid XML | Validate XML; remove debug output |
| 12200 | Schema compliance failure | TwiML verbs/attributes are invalid | Check TwiML reference for correct syntax |
| 20003 | Authentication error | Invalid Account SID or Auth Token | Verify credentials in environment |
| 21211 | Invalid `To` number | Number not in E.164 format | Use `+` country code + number |
| 21608 | Unverified number (trial) | Trial accounts can only send to verified numbers | Verify number or upgrade account |
| 30003 | Unreachable destination | Carrier cannot deliver message | Check number validity; retry later |
| 30006 | Landline or unreachable | Destination is a landline | Use voice channel instead |
| 30007 | Carrier filtering | Message filtered by carrier | Review content; register for A2P 10DLC |
| 30008 | Unknown error | Carrier returned generic error | Retry; contact support if persistent |

Full error reference: https://www.twilio.com/docs/api/errors

### 9. Querying Resource State Directly

When you need the current state of a message or call (not waiting for a callback):

**Python**
```python
# Check message delivery status
message = client.messages("SMxxxxxxxxxx").fetch()
print(f"Status: {message.status}, Error: {message.error_code}")

# Check call status
call = client.calls("CAxxxxxxxxxx").fetch()
print(f"Status: {call.status}, Duration: {call.duration}")
```

**Node.js**
```node
const message = await client.messages("SMxxxxxxxxxx").fetch();
console.log(`Status: ${message.status}, Error: ${message.errorCode}`);

const call = await client.calls("CAxxxxxxxxxx").fetch();
console.log(`Status: ${call.status}, Duration: ${call.duration}`);
```

### 10. CLI Debugging

The Twilio CLI supports debug logging:

```bash
# Verbose output for any CLI command
twilio api:core:messages:list --limit 5 -l debug

# Log levels: debug, info, warn, error
```

Debug output goes to stderr, so you can pipe normal output while still seeing diagnostics.

---

## Monitoring Checklist

Set up before going to production:

| What to monitor | How | Alert threshold |
|---|---|---|
| Webhook errors | Debugger webhook or Event Streams (`com.twilio.error-logs.error.logged`) | Any error |
| Message delivery failures | Status callback `failed`/`undelivered` | > 2% failure rate |
| Call completion rate | Status callback `completed` vs total | < 95% completion |
| Webhook response time | Your APM (DataDog, New Relic) | p95 > 5 seconds |
| 429 rate limit hits | Count in your backoff handler | > 5% of requests |
| Account configuration changes | Monitor Events API | Any unexpected change |
| Recording failures | Recording status callback `failed`/`absent` | Any failure |

---

## CANNOT

- **Cannot fetch more than 10,000 alerts per request** — Use date range filters for large accounts
- **Cannot get full HTTP request/response from alert list** — Only available when fetching a single alert by SID
- **Cannot combine multiple filters on Events API** — One additional field (ResourceSid, ActorSid, SourceIpAddress) plus date range per request
- **Cannot delete an Event Streams sink before its subscription** — Must delete the subscription first
- **Cannot guarantee status callback delivery or order** — Best-effort. Use composite keys for idempotency.
- **Cannot rely on a static error code list** — New error codes are added without notice. Always link to the full reference rather than hardcoding.

---

## Next Steps

- **Webhook architecture:** `twilio-webhook-architecture`
- **Scale webhook handling:** `twilio-reliability-patterns`
- **Compliance monitoring:** `twilio-compliance-traffic`
- **Credential security:** `twilio-iam-auth-setup`
