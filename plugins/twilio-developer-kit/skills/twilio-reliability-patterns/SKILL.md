---
name: twilio-reliability-patterns
description: >
  Handle rate limits, retries, and failures when building on Twilio at
  scale. Covers 429 exponential backoff with jitter, per-number throughput
  limits, StatusCallback resilience, thin-receiver pattern, and fallback
  chains. Use this skill whenever sending messages or making calls at
  volume, or when building production-grade Twilio integrations.
---

## Overview

Twilio enforces per-resource rate limits. At scale, 429 errors are expected behavior — not bugs. This skill teaches the patterns that prevent production failures: exponential backoff, throughput management, and resilient callback handling.

429 concurrency errors are not well documented — implement exponential backoff with ±10% jitter.

---

## Prerequisites

- A working Twilio integration (any product)
- Understanding of your expected volume (messages/sec, calls/sec)
- StatusCallback URLs configured — see `twilio-messaging-services`, `twilio-sms-send-message`

---

## Key Patterns

### 1. Exponential Backoff with Jitter

When you receive a 429 (Too Many Requests), wait and retry. Naive fixed-interval retry creates thundering herds. Use exponential backoff with randomized jitter.

**Python**
```python
import time, random, requests

def send_with_backoff(client, to, body, messaging_service_sid, max_retries=5):
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                to=to,
                body=body,
                messaging_service_sid=messaging_service_sid,
                status_callback="https://yourapp.com/status"
            )
            return message
        except Exception as e:
            if hasattr(e, 'status') and e.status == 429:
                # Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms
                base_delay = 0.1 * (2 ** attempt)
                # Add ±10% jitter to prevent thundering herd
                jitter = base_delay * 0.1 * (2 * random.random() - 1)
                delay = min(base_delay + jitter, 30)  # cap at 30 seconds
                time.sleep(delay)
            else:
                raise  # Non-429 errors: don't retry, investigate
    raise Exception(f"Failed after {max_retries} retries")
```

**Node.js**
```node
async function sendWithBackoff(client, to, body, messagingServiceSid, maxRetries = 5) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await client.messages.create({
                to,
                body,
                messagingServiceSid,
                statusCallback: "https://yourapp.com/status",
            });
        } catch (err) {
            if (err.status === 429) {
                // Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms
                const baseDelay = 100 * Math.pow(2, attempt);
                // Add ±10% jitter
                const jitter = baseDelay * 0.1 * (2 * Math.random() - 1);
                const delay = Math.min(baseDelay + jitter, 30000); // cap at 30s
                await new Promise(r => setTimeout(r, delay));
            } else {
                throw err; // Non-429: don't retry
            }
        }
    }
    throw new Error(`Failed after ${maxRetries} retries`);
}
```

**Parameters:**
- Initial delay: 100ms
- Multiplier: 2x per attempt
- Jitter: ±10% of base delay (randomized)
- Max delay: 30 seconds
- Max retries: 5 (covers up to ~3.2 second base delay)

### 2. Per-Number Throughput Limits

These limits are not prominently documented:

| Number type | SMS throughput | Voice throughput | Notes |
|-------------|---------------|-----------------|-------|
| Local (long code) | ~1 SMS/sec | 1 concurrent call | Lowest cost, lowest throughput |
| Toll-free | ~3 SMS/sec | — | Faster verification (3-5 days) |
| Short code | 10-100 SMS/sec | — | Highest throughput, 8-12 week provisioning, expensive |
| Messaging Service (pool) | Sum of all numbers in pool | — | Multiply throughput by adding numbers |

**Throughput opacity:** Sending velocity and queue depth are opaque — there is no dashboard showing messages per second. Use Messaging Services to multiply throughput by pooling numbers. A pool of 10 long codes = ~10 SMS/sec.

### 3. Bulk Send Pattern

For sending to large lists, use a rate-limited dispatch loop:

**Python**
```python
import asyncio
from collections import deque

async def bulk_send(client, recipients, body, messaging_service_sid, rate_per_second=10):
    """Send to a list of recipients with rate limiting and backoff."""
    queue = deque(recipients)
    results = []
    
    while queue:
        batch = []
        for _ in range(min(rate_per_second, len(queue))):
            batch.append(queue.popleft())
        
        for recipient in batch:
            try:
                msg = send_with_backoff(client, recipient, body, messaging_service_sid)
                results.append({"to": recipient, "sid": msg.sid, "status": "sent"})
            except Exception as e:
                results.append({"to": recipient, "error": str(e), "status": "failed"})
        
        if queue:  # Don't sleep after last batch
            await asyncio.sleep(1)  # 1 second between batches
    
    return results
```

**Key:** Set `rate_per_second` based on your number pool size, not your desired speed. Sending faster than your pool supports just generates 429s.

> **Compliance:** Before bulk sending, verify recipient consent (opt-in records), respect quiet hours, and implement maximum batch size limits. Monitor for anomalous send patterns that could indicate abuse.

### 4. StatusCallback Resilience

At scale, StatusCallbacks create their own load problem.

**The math:** 50 concurrent calls × 6 status events per call = 300 webhook invocations per second. Twilio Functions allow 30 concurrent executions per service.

**Thin-receiver pattern** — receive, queue, respond immediately:

**Node.js (Express)**
```node
const { Queue } = require("bullmq");
const statusQueue = new Queue("twilio-status");

// Thin receiver: accept callback, queue it, respond 200 immediately
app.post("/status", async (req, res) => {
    await statusQueue.add("status-event", {
        callSid: req.body.CallSid,
        callStatus: req.body.CallStatus,
        timestamp: Date.now(),
    });
    res.sendStatus(200);  // Respond FAST — Twilio will retry on timeout
});

// Process asynchronously
const worker = new Worker("twilio-status", async (job) => {
    const { callSid, callStatus } = job.data;
    await updateDatabase(callSid, callStatus);
});
```

**Python (Flask + Celery)**
```python
@app.route("/status", methods=["POST"])
def status_callback():
    # Queue for async processing
    process_status.delay(
        call_sid=request.form["CallSid"],
        call_status=request.form["CallStatus"]
    )
    return "", 200  # Respond FAST

@celery.task
def process_status(call_sid, call_status):
    update_database(call_sid, call_status)
```

**Idempotency key:** Use `{CallSid}-{CallStatus}` as a composite key. Twilio retries on timeout, which can cause duplicate callbacks. Deduplicate before processing.

### 5. Fallback Chains

When delivery on one channel fails, escalate to the next:

**Python**
```python
async def send_with_fallback(client, to, message, messaging_service_sid):
    """Try SMS → Voice → Email fallback chain."""
    
    # Try SMS first
    try:
        msg = client.messages.create(
            to=to, body=message, messaging_service_sid=messaging_service_sid,
            status_callback="https://yourapp.com/status"
        )
        # Wait for delivery confirmation via StatusCallback
        # If undelivered after timeout, fall through to voice
        return {"channel": "sms", "sid": msg.sid}
    except Exception:
        pass  # SMS failed, try voice
    
    # Fallback to voice
    try:
        call = client.calls.create(
            to=to, from_="+15551234567",
            twiml=f"<Response><Say>{message}</Say></Response>",
            status_callback="https://yourapp.com/call-status"
        )
        return {"channel": "voice", "sid": call.sid}
    except Exception:
        pass  # Voice failed, try email
    
    # Last resort: email
    # Use SendGrid — see twilio-sendgrid-email
    return {"channel": "email", "status": "queued"}
```

### 6. Voice Concurrency Limits

| Resource | Default limit | Notes |
|----------|--------------|-------|
| Concurrent calls per account | 1 (trial) / variable (paid) | Request increase via support |
| Calls per second (CPS) | 1 CPS (default) | Increase via support for outbound campaigns |
| Conference participants | 250 per conference | |
| Twilio Functions concurrent | 30 per service | Use thin-receiver pattern above |

For outbound campaigns, request CPS increase before launch — not during.

### 7. Webhook Timeout Handling

Twilio expects a response within **15 seconds** for voice webhooks and **15 seconds** for messaging webhooks. If your endpoint doesn't respond:
- Voice: Twilio hangs up or falls back to `voiceFallbackUrl`
- Messaging: Twilio retries the callback

**Always configure fallback URLs:**
```python
# On phone number configuration
number = client.incoming_phone_numbers(phone_sid).update(
    voice_url="https://yourapp.com/voice",
    voice_fallback_url="https://yourapp.com/voice-fallback",  # backup endpoint
    sms_url="https://yourapp.com/sms",
    sms_fallback_url="https://yourapp.com/sms-fallback"
)
```

---

## Monitoring Checklist

Set up these alerts before going to production:

| Metric | Alert threshold | How to track |
|--------|----------------|-------------|
| 429 error rate | > 5% of requests | Count 429s in your backoff handler |
| Delivery failure rate | > 2% of messages | StatusCallback `failed`/`undelivered` events |
| Webhook response time | > 5 seconds p95 | Your APM tool (DataDog, New Relic) |
| Queue depth | Growing over 5 minutes | Your message queue metrics |
| Concurrent calls | > 80% of limit | Twilio Usage API or Event Streams |

Twilio's built-in alerting systems are under-used — end-users often discover issues before developers do. Configure StatusCallbacks + Event Streams for delivery failure alerts on every integration.

---

## CANNOT

- **Cannot avoid 429 errors on any Twilio API** — Backoff patterns apply to all APIs (Messaging, Voice, Verify, Lookup)
- **Cannot increase per-number throughput** — Add more numbers via Messaging Services instead
- **Cannot configure StatusCallback retry behavior** — Twilio retries on timeout automatically; not configurable
- **Cannot exceed Twilio Functions limits** — 30 concurrent executions/service, 10-second timeout, 256 MB memory
- **Cannot use a native Twilio rate limiting API** — You must implement rate limiting in your application

---

## Next Steps

- **Messaging at scale:** `twilio-messaging-services`
- **Monitor delivery:** `twilio-sms-send-message` (StatusCallbacks)
- **Debug failures:** `twilio-debugging-observability`
- **Compliance for bulk sends:** `twilio-compliance-traffic`
