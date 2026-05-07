---
name: twilio-lookup-phone-intelligence
description: >
  Look up phone number intelligence via Twilio Lookup v2 API. Covers number
  validation, line type detection (mobile/landline/VoIP), SIM swap detection,
  caller name, identity match, and SMS pumping risk scoring. Use this skill
  to validate numbers or assess fraud risk before sending messages or calls.
---

## Overview

Twilio Lookup validates phone numbers and provides optional intelligence packages. Basic validation is free; data packages (line type, SIM swap, etc.) are paid per lookup.

---

## Prerequisites

- Twilio account (free trial works for basic lookups)
  — New to Twilio? See `twilio-account-setup`
- Environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  — See `twilio-iam-auth-setup` for credential setup and best practices
- SDK: `pip install twilio` / `npm install twilio`

---

## Quickstart

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

phone = client.lookups.v2.phone_numbers("+15108675310").fetch()

print(phone.valid)            # True / False
print(phone.phone_number)     # +15108675310 (E.164)
print(phone.national_format)  # (510) 867-5310
print(phone.country_code)     # US
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const phone = await client.lookups.v2.phoneNumbers("+15108675310").fetch();

console.log(phone.valid);
console.log(phone.phoneNumber);
console.log(phone.nationalFormat);
```

If `valid` is `false`, check `phone.validationErrors` for the reason.

---

## Key Patterns

### Line Type Intelligence (paid)

Identifies mobile, landline, VoIP, toll-free, etc.

**Python**
```python
phone = client.lookups.v2.phone_numbers("+15108675310").fetch(
    fields="line_type_intelligence"
)
print(phone.line_type_intelligence)
# {'type': 'mobile', 'carrier_name': 'T-Mobile USA', ...}
```

**Node.js**
```node
const phone = await client.lookups.v2.phoneNumbers("+15108675310").fetch({
    fields: "line_type_intelligence",
});
console.log(phone.lineTypeIntelligence);
```

Line types: `mobile`, `landline`, `voip`, `toll-free`, `fixedVoip`, `nonFixedVoip`, `personal`, `payphone`, `unknown`

### Multiple Packages in One Request

**Python**
```python
phone = client.lookups.v2.phone_numbers("+15108675310").fetch(
    fields="line_type_intelligence,sim_swap,caller_name"
)
```

**Node.js**
```node
const phone = await client.lookups.v2.phoneNumbers("+15108675310").fetch({
    fields: "line_type_intelligence,sim_swap,caller_name",
});
```

### Validate Before Sending

**Python**
```python
phone = client.lookups.v2.phone_numbers("+invalid").fetch()
if not phone.valid:
    print(f"Invalid number: {phone.validation_errors}")
    # Handle gracefully — do not attempt to send
```

**Node.js**
```node
const phone = await client.lookups.v2.phoneNumbers("+invalid").fetch();
if (!phone.valid) {
    console.log("Invalid number:", phone.validationErrors);
}
```

### Available Data Packages

| Package | `fields` value | Coverage | Use case |
|---------|---------------|----------|----------|
| Line Type Intelligence | `line_type_intelligence` | Worldwide | Route by line type; block VoIP |
| Caller Name | `caller_name` | US only | Show caller ID |
| SIM Swap | `sim_swap` | Select regions | Fraud detection |
| Identity Match | `identity_match` | Select regions | Verify ownership |
| SMS Pumping Risk | `sms_pumping_risk` | Worldwide | Fraud prevention |
| Reassigned Number | `reassigned_number` | US only | Check if recycled |

---

## Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 20404 | Phone number not found | Number may be invalid or unsupported format |
| 60601 | Data package not available for this region | Check regional coverage before requesting package |

---

## CANNOT

- **Cannot look up by name or address** — Input is always a phone number. No reverse search.
- **Cannot get caller_name for non-US numbers** — Returns error 60600 (out of coverage).
- **Cannot detect conditional call forwarding** — Only unconditional forwarding is detected, and only for UK carriers.
- **Cannot guarantee SIM swap data without carrier registration** — Returns error 60606 until carrier approval is in place.
- **Cannot use Reassigned Number outside the US** — US-only dataset with monthly update cadence.
- **Cannot get real-time SMS pumping scores** — Scores are statistical models, not live traffic analysis.
- **Cannot write data** — Lookup v2 is read-only (GET only). The one exception is Line Type Override (POST/DELETE).
- **Cannot batch multiple phone numbers in one request** — One number per API call. Loop for bulk lookups.
- **Cannot avoid billing on caller_name requests that return no data** — Billed per request regardless of whether data is returned.
- **Cannot use Phone Number Quality Score or Pre-fill without provisioning** — Returns 60606. Contact Twilio sales to enable.
- **Cannot guarantee deliverability from a valid lookup** — A valid number may still be unreachable (carrier issues, ported, etc.)

---

## Next Steps

- **Send SMS after validation:** `twilio-sms-send-message`
- **Send OTP after validation:** `twilio-verify-send-otp`
