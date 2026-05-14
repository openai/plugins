---
name: twilio-compliance-traffic
description: >
  Rules you must follow for Twilio messaging and voice traffic. Covers
  TCPA (consent tiers, quiet hours, DNC), GDPR (EU consent, right to
  deletion), PCI DSS (payment recording, Pay verb), HIPAA (BAA, PHI),
  FDCPA (debt collection limits), CAN-SPAM, WhatsApp policies,
  SHAKEN/STIR, and consent management patterns. Use this skill proactively
  when developers have working traffic to ensure they follow the rules.
---

## Overview

Compliance failures block sends, get numbers suspended, and expose your customer to legal liability. This skill covers the **ongoing rules** that apply to live traffic — what you can send, when, and to whom.

**Lifecycle:** Choose numbers (`twilio-numbers-senders`) → Register them (`twilio-compliance-onboarding`) → Follow traffic rules (this skill) → Secure everything (`twilio-security-hardening`)

For registrations required before traffic works (A2P 10DLC, toll-free verification, WhatsApp/RCS sender approval, voice trust programs), see `twilio-compliance-onboarding`.

---

## TCPA (Telephone Consumer Protection Act)

Applies to all US voice calls and SMS.

### Consent Requirements

| Communication type | Consent required | Notes |
|-------------------|-----------------|-------|
| Informational SMS (order updates) | Prior express consent | Providing phone number during transaction usually qualifies |
| Marketing SMS | Prior express written consent | Must be clear and conspicuous, separate from T&C |
| Manual voice calls | None for existing business relationship | 18-month window |
| Autodialed / prerecorded voice | Prior express consent (informational) or written (marketing) | AI voice agents typically count as autodialed and must disclose who is calling |
| Emergency / fraud alerts | No consent required | Must be genuinely urgent |

### Quiet Hours

- **8:00 AM – 9:00 PM** in the recipient's local time zone
- Applies to telemarketing and non-emergency calls
- Your application must determine the recipient's time zone — Twilio does not enforce this
- Use `twilio-lookup-phone-intelligence` to determine carrier/region for time zone inference

### Do Not Call

- Maintain an internal Do Not Call list
- Honor opt-outs within 10 business days (best practice: immediately)
- Scrub against the National Do Not Call Registry for telemarketing

---

## GDPR (EU/EEA)

### Consent for Communications

| Basis | When it applies | Requirements |
|-------|----------------|-------------|
| Explicit consent | Marketing messages, new customer outreach | Must be freely given, specific, informed, unambiguous. Pre-checked boxes do NOT qualify. |
| Legitimate interest | Transactional messages, existing customer relationship | Requires documented balancing test. Must offer opt-out. |
| Contractual necessity | Order confirmations, shipping updates | Directly related to contract performance |

### Right to Deletion

Applies to ALL data stored by your application via Twilio:
- Call recordings and transcripts
- SMS/messaging logs
- Conversation Memory observations and profiles
- Conversation Intelligence operator results
- Customer profiles in your database

**Implementation:** Build a deletion endpoint that removes data from all systems. Twilio retains message logs for 400 days — you can delete recordings via API but cannot delete message logs from Twilio's system before the retention window.

### Call Recording Consent

- EU calls require explicit consent before recording, or a documented legitimate interest basis
- Play a recording notice at the start of every call: `<Say>This call may be recorded for quality assurance.</Say>`
- Store consent records with timestamp

---

## PCI DSS (Payment Card Industry)

### Never Record Card Numbers

- If recording calls, **pause recording** during payment:

**Python**
```python
# Pause recording when customer gives card number
client.calls(call_sid).recordings(recording_sid).update(status="paused")

# Use <Pay> verb instead of collecting card numbers verbally
response = VoiceResponse()
response.pay(
    payment_connector="stripe_connector",
    charge_amount="49.99",
    currency="usd",
    status_callback="https://yourapp.com/pay-status"
)
```

- Never let an LLM process, log, or repeat card numbers
- Never store card numbers in Conversation Memory observations or Conversation Intelligence transcripts

### PCI Mode Warning

**PCI Mode is IRREVERSIBLE and account-wide.** Once enabled:
- All recordings are encrypted
- Transcript access is restricted
- Cannot be disabled — ever

**Recommendation:** If you need PCI compliance for one use case, create a separate sub-account. See `twilio-account-setup`.

---

## HIPAA (Healthcare)

### Requirements

- **BAA required:** Execute a Business Associate Agreement with Twilio before handling PHI
- **Recording encryption:** Mandatory for any call recording containing PHI
- **PHI minimization in TTS:** Don't speak full patient details via `<Say>`. Use minimum necessary information.
- **API key rotation:** Regular rotation required. See `twilio-iam-auth-setup`
- **Access controls:** Restrict who can access recordings and transcripts

### Safe Notification Content

| Channel | Safe | Unsafe |
|---------|------|--------|
| SMS | "Your appointment is tomorrow at 2pm" | "Your appointment with Dr. Smith for diabetes follow-up" |
| Voice IVR | "Press 1 to confirm your upcoming appointment" | "Press 1 to confirm your cardiology appointment" |
| Email | Can include more detail if encrypted/authenticated | Never send PHI in subject line |

---

## FDCPA / Regulation F (Debt Collection)

### Requirements

- **Mini-Miranda disclosure** required on every communication: "This is an attempt to collect a debt and any information obtained will be used for that purpose."
- **Call attempt limits:** Max 7 call attempts per debt per 7-day rolling window
- **Voicemail:** Must include disclosure or use limited-content message (name, phone number, request to call back — no mention of debt)
- **SMS consent:** Requires separate consent from voice consent
- **Time restrictions:** Same as TCPA quiet hours (8am-9pm local time)
- **Developer responsibility:** Twilio does NOT enforce FDCPA limits. Your application must track attempt counts and timing.

**Python**
```python
# Track call attempts per debt
def can_attempt_call(debt_id, db):
    seven_days_ago = datetime.now() - timedelta(days=7)
    attempts = db.count_attempts(debt_id, since=seven_days_ago)
    return attempts < 7

# Include Mini-Miranda in IVR
response = VoiceResponse()
response.say("This is an attempt to collect a debt and any information obtained will be used for that purpose.")
response.pause(length=1)
response.say("Please press 1 to speak with a representative.")
response.gather(num_digits=1, action="/handle-keypress")
```

---

## WhatsApp Compliance

### Template Requirements
- Outbound messages require pre-approved Message Templates (submitted to Meta, 24-48 hour approval)
- Free-form messages only within 24-hour service window after customer initiates
- Template rejections: vague descriptions, missing variables, promotional language in utility templates

### Quality Rating
- WhatsApp enforces quality scoring — too many blocks/reports = rate limited or suspended
- Monitor quality in WhatsApp Manager dashboard
- Opt-in required before sending any WhatsApp messages

### Opt-In Best Practices
- Collect WhatsApp-specific consent (separate from SMS consent)
- Clearly state what types of messages will be sent
- Provide easy opt-out (reply STOP)

---

## CAN-SPAM (Email)

- Physical mailing address required in every marketing email
- One-click unsubscribe required (SendGrid handles automatically via List-Unsubscribe header)
- Honor unsubscribe within 10 business days
- Subject line must not be misleading
- "From" address must be accurate

See `twilio-sendgrid-email-send` for SendGrid-specific compliance features.

---

## SHAKEN/STIR (Caller ID Verification)

### Attestation Levels

| Level | Meaning | Caller ID display |
|-------|---------|-------------------|
| **A (Full)** | Carrier vouches for caller identity and right to use number | Green checkmark ✅ |
| **B (Partial)** | Carrier vouches for caller but not number ownership | Neutral display |
| **C (Gateway)** | Carrier knows where call entered network, nothing else | May show "Spam Likely" |

- Only Level A produces a trusted caller ID display
- Affects answer rates significantly for outbound campaigns
- E.164 formatting required for proper attestation
- Twilio signs outbound calls automatically when you own the number

---

## Consent Management Pattern

### Store Consent Records

```python
# Minimum consent record
consent_record = {
    "phone": "+15558675310",
    "channel": "sms",                    # sms, voice, whatsapp, email
    "consent_type": "marketing",         # marketing, transactional, debt_collection
    "consent_method": "web_form",        # web_form, verbal, paper, api
    "consent_timestamp": "2026-04-13T14:30:00Z",
    "consent_source": "checkout_page",   # where consent was collected
    "ip_address": "203.0.113.42",        # for web consent
    "opted_out": False,
    "opt_out_timestamp": None
}
```

### Opt-Out Handling

- Process STOP/CANCEL/UNSUBSCRIBE/END/QUIT keywords immediately
- Messaging Services handle keyword opt-out automatically for SMS
- For voice: maintain your own Do Not Call list
- For WhatsApp: handle via webhook when user blocks
- For email: SendGrid manages suppression lists automatically

---

## CANNOT

- **Cannot rely on Twilio to enforce compliance rules** — Your application must implement TCPA, GDPR, PCI, and other rules. Twilio provides tools, not enforcement.
- **Cannot apply A2P 10DLC registration outside the US** — Other countries have their own regimes
- **Cannot use public link shorteners (bit.ly, tinyurl, goo.gl, short.io, etc.)** — Messages with public short links are categorically filtered by carriers. Use a branded/vanity short domain (e.g., `go.yourcompany.com`) configured in your Messaging Service. Twilio's shared `twil.io` domain is not sufficient — you must register your own branded domain in Console under Messaging > Link Shortening.
- **Cannot reverse PCI Mode** — Irreversible and account-wide once enabled
- **Cannot fully clear message logs via GDPR deletion** — Twilio retains internal message logs for 400 days regardless of deletion requests
- **Cannot assume regulations are static** — Compliance requirements change. Verify current regulations before launch.
- **Cannot apply this skill's guidance outside US/EU** — India TRAI DLT, Brazil LGPD, Australia Spam Act, and other jurisdictions require additional research

---

## Next Steps

- **Registration before traffic works:** `twilio-compliance-onboarding`
- **WhatsApp sender setup:** `twilio-whatsapp-manage-senders`
- **Credential security:** `twilio-iam-auth-setup`
- **Account structure for PCI isolation:** `twilio-account-setup`
