---
name: twilio-verify-send-otp
description: >
  Send and verify one-time passcodes (OTPs) via Twilio Verify over SMS, RCS,
  voice, email, or WhatsApp. Covers creating a Verify Service, sending tokens,
  checking submitted codes, automatic WhatsApp-to-SMS fallback, and service
  configuration. TOTP is supported via the Factors API (a separate family from
  channel-based OTP). Use this skill to add phone or email verification or
  two-factor authentication to any application.
---

## Overview

Use **Twilio Verify** to manage the full OTP lifecycle: code generation, delivery, expiry, rate limiting, and Fraud Guard protection. Use the **Programmable Messaging API** to build your own OTP message infrastructure and access features such as SMS Pumping Protection.

| | Twilio Verify | Programmable Messaging API |
|---|---|---|
| Code generation + expiry | Built-in (10min default, configurable). Also supports custom codes. | Build yourself |
| Rate limiting | Built-in (per-phone, per-service) | Build yourself |
| Fraud protection | Fraud Guard (geo-permissions, rate anomaly) | SMS Pumping Protection |
| A2P registration | Exempt — no 10DLC needed | Required — must register campaign |
| Multi-channel | One API, change `channel` param (SMS/Voice/Email/WhatsApp/RCS) | Separate integration per channel |
| Cost | [Per confirmed verification + channel fee](https://www.twilio.com/en-us/verify/pricing) | Per-message pricing + build cost |
| Delivery confirmation | Yes — via List Attempts or Events API | Yes (via StatusCallback) |

**When Programmable Messaging is justified:** You need full control over message content, custom delivery logic, or SMS Pumping Protection features. For standard OTP/2FA flows, use Verify.

Verify supports SMS, voice, email, WhatsApp, and RCS — only the `channel` parameter changes per delivery method. TOTP (authenticator apps) is supported via the Verify Factors API, a separate implementation from channel-based OTP.

---

## Prerequisites

- Twilio account (free trial works for testing)
  — New to Twilio? See `twilio-account-setup`
  — Verify requires no separate product activation — just create a Service below
- Environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `VERIFY_SERVICE_SID` (created in Quickstart step 1)
  — See `twilio-iam-auth-setup` for credential setup and best practices
- SDK: `pip install twilio` / `npm install twilio`
- For WhatsApp channel only: a registered production WhatsApp sender — see `twilio-whatsapp-manage-senders`

---

## Quickstart

**Step 1 — Create a Verify Service (one-time)**

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

service = client.verify.v2.services.create(
    friendly_name="My App Verification"
)
print(service.sid)  # VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx — save as VERIFY_SERVICE_SID
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const service = await client.verify.v2.services.create({
    friendlyName: "My App Verification",
});
console.log(service.sid);  // VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Store the Service SID — reuse it for all verifications, do not recreate it each time.

**Step 2 — Send a verification token**

**Python**
```python
verification = client.verify.v2 \
    .services(os.environ["VERIFY_SERVICE_SID"]) \
    .verifications \
    .create(to="+15558675310", channel="sms")

print(verification.status)  # pending
```

**Node.js**
```node
const verification = await client.verify.v2
    .services(process.env.VERIFY_SERVICE_SID)
    .verifications.create({ to: "+15558675310", channel: "sms" });

console.log(verification.status);  // pending
```

**Step 3 — Check the submitted code**

**Python**
```python
check = client.verify.v2 \
    .services(os.environ["VERIFY_SERVICE_SID"]) \
    .verification_checks \
    .create(to="+15558675310", code="123456")

if check.status == "approved":
    print("Verified!")
else:
    print("Invalid or expired code")
```

**Node.js**
```node
const check = await client.verify.v2
    .services(process.env.VERIFY_SERVICE_SID)
    .verificationChecks.create({ to: "+15558675310", code: "123456" });

if (check.status === "approved") {
    console.log("Verified!");
} else {
    console.log("Invalid or expired code");
}
```

---

## Key Patterns

### Supported Channels

| Channel | `channel` value | Notes |
|---------|----------------|-------|
| SMS | `sms` | Default, widest coverage |
| Voice call | `voice` | Reads code aloud |
| Email | `email` | Use email address in `to` |
| WhatsApp | `whatsapp` | Requires own WhatsApp sender (see below) |
| RCS | `rcs` | Rich messaging, Android devices |

> **TOTP (authenticator apps):** Supported via the Verify Factors API — a separate implementation from channel-based OTP. See [Verify TOTP docs](https://www.twilio.com/docs/verify/quickstarts/totp).

### WhatsApp OTP

Change `channel` to `"whatsapp"` — the send/check flow is identical to SMS.

> **Requires:** A registered production WhatsApp sender. As of March 2024, Twilio no longer provides a shared sender for Verify. See `twilio-whatsapp-manage-senders`.

**Python**
```python
verification = client.verify.v2 \
    .services(os.environ["VERIFY_SERVICE_SID"]) \
    .verifications \
    .create(to="+15558675310", channel="whatsapp")
```

**Node.js**
```node
const verification = await client.verify.v2
    .services(process.env.VERIFY_SERVICE_SID)
    .verifications.create({ to: "+15558675310", channel: "whatsapp" });
```

### WhatsApp with Automatic SMS Fallback

**Python**
```python
verification = client.verify.v2 \
    .services(os.environ["VERIFY_SERVICE_SID"]) \
    .verifications \
    .create(
        to="+15558675310",
        channel="whatsapp",
        channel_configuration={
            "whatsapp": {"enabled": True},
            "sms": {"enabled": True}   # falls back to SMS if WhatsApp undelivered
        }
    )
```

**Node.js**
```node
const verification = await client.verify.v2
    .services(process.env.VERIFY_SERVICE_SID)
    .verifications.create({
        to: "+15558675310",
        channel: "whatsapp",
        channelConfiguration: {
            whatsapp: { enabled: true },
            sms: { enabled: true },
        },
    });
```

With fallback enabled, your UI can say "a verification code was sent" without specifying the channel.

### Service Configuration

**Python**
```python
service = client.verify.v2.services.create(
    friendly_name="My App",
    code_length=6,              # 4–10 digits (default: 6)
    lookup_enabled=True,        # Validate number before sending
    do_force_check_once=True,   # Code can only be checked once
    ttl=600,                    # Code expiry in seconds (default: 600)
)
```

**Node.js**
```node
const service = await client.verify.v2.services.create({
    friendlyName: "My App",
    codeLength: 6,
    lookupEnabled: true,
    doForceCheckOnce: true,
    ttl: 600,
});
```

### Verification Status Values

| Status | Meaning |
|--------|---------|
| `approved` | Code is correct |
| `pending` | Code is wrong or not yet submitted |
| `expired` | Code has expired (default TTL: 10 minutes) |
| `canceled` | Verification was canceled |

---

## Debugging

**Primary debugging tool:** Console > Verify > Logs (per-Service). Shows every verification attempt, delivery status, channel used, and error codes. Check here first before writing custom monitoring code.

### Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 60200 | Invalid parameter | Check `to` format and `channel` value |
| 60202 | Max send attempts reached | Wait before retrying |
| 60203 | Max check attempts reached | Issue a new verification |
| 60212 | Service not found | Verify `VERIFY_SERVICE_SID` is correct |
| 60410 | Geo-permission not enabled | Enable country in Console |

**Built-in protections (no custom code needed):**
- Rate limiting: 5 verifications per phone per service per 10 minutes
- Max check attempts: 5 per verification (6th attempt → error 60203)
- Phone number validation: Verify checks line type before sending (if `lookup_enabled=True`)
- Fraud Guard: geo-permissions, rate anomaly detection, SMS pumping protection

**International OTP traffic warning:** International numbers are high-risk for SMS pumping — fraudsters trigger OTPs to premium-rate destinations to generate revenue. Verify's Fraud Guard handles this automatically when enabled. If you're building custom OTP with Programmable Messaging instead, enable SMS Pumping Protection on your Messaging Service (see `twilio-messaging-services`). Always restrict geo-permissions to only countries where you have real users.

---

## CANNOT

- **No built-in channel fallback** — Must implement retry logic manually (e.g., SMS → voice → email). Use `channel_configuration` for WhatsApp→SMS only.
- **No webhook on verification completion** — Must poll `verification_checks`. Rate-limited: 60/min, 180/hr, 250/day.
- **Cannot retrieve the actual code sent** — Code is never returned in any API response. By design.
- **Cannot change channel mid-verification** — Starting on a new channel reuses the same Verification SID and token. Create a new verification instead.
- **Cannot extend TTL on an existing verification** — Default 10 minutes. Customizable only at Service level, not per-verification.
- **Verification SID deleted after approval** — Fetching an approved verification returns 404. Canceled verifications remain fetchable.
- **`auto` channel not universally available** — Returns error 60200 on accounts without Fraud Guard enabled.
- **Email channel requires Mailer configuration** — `channel: 'email'` without a configured Mailer returns error 60217.
- **No real-time delivery push notification** — Delivery status is available via List Attempts or Events API (pull-based), not via a push webhook.
- **FriendlyName rejects 5+ consecutive digits** — Service names containing 5+ digits trigger error 60200. Use words or fewer digits.
- **Wrong code does not throw an exception** — Check returns `status: "pending"`, not an error. You must check `status === "approved"` explicitly.
- **Cannot re-check an approved verification** — Each verification is single-use. Once `approved`, subsequent checks return 404.
- **Cannot send to arbitrary numbers on trial accounts** — Trial accounts have limited verification destinations
- **Cannot customize WhatsApp OTP template** — Uses a fixed Meta authentication template
- **Cannot use WhatsApp channel for PSD2 compliance mode** — PSD2 payee/amount parameters not supported on WhatsApp

---

## Next Steps

- **Register a WhatsApp sender:** `twilio-whatsapp-manage-senders`
- **Validate phone numbers before sending:** `twilio-lookup-phone-intelligence`
- **Credential setup:** `twilio-iam-auth-setup`
