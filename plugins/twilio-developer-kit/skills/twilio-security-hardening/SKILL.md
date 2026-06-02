---
name: twilio-security-hardening
description: >
  Secure Twilio applications against common attacks. Covers credential
  management (API keys vs auth tokens), request validation (webhook
  signature verification), PCI DSS compliance, HIPAA account requirements,
  SMS pumping prevention, geo-permissions, and account isolation patterns.
  Use this skill when developers are building or deploying Twilio apps.
---

## Overview

Security hardening is an **ongoing** concern — not a one-time setup. This skill covers account-level security decisions and application-level protection patterns that prevent credential leaks, fraud, and compliance violations.

**Lifecycle:** Choose numbers (`twilio-numbers-senders`) → Register (`twilio-compliance-onboarding`) → Follow traffic rules (`twilio-compliance-traffic`) → Secure everything (this skill)

---

## Credential Management

### API Keys vs Auth Tokens

| Credential | Scope | Revocable | Use when |
|-----------|-------|-----------|----------|
| **Auth Token** | Full account access | Only by rotating (invalidates ALL API keys) | Never in production — use API keys instead |
| **API Key + Secret** | Scoped, revocable individually | Yes — revoke one without affecting others | Production applications, CI/CD, server-side code |
| **Access Tokens** | Short-lived, client-specific | Expire automatically | Client-side SDKs (Voice, Video, Conversations) |

**Critical gotcha:** Rotating your Auth Token **invalidates ALL existing API keys**. This is a one-way door that can break every integration simultaneously. Use API keys from the start so you never need to rotate the Auth Token.

### Best Practices

- Store credentials in environment variables or a secrets manager — never in code
- Use different API keys per application/environment
- Rotate API keys on a schedule (quarterly minimum, monthly for HIPAA)
- Use sub-accounts to isolate customer credentials for ISV platforms — see `twilio-account-setup`

**Docs:** See `twilio-iam-auth-setup` for full credential setup patterns.

---

## Request Validation (Webhook Security)

Verify that webhook requests actually come from Twilio — not spoofed by attackers.

### X-Twilio-Signature Validation

Always use the SDK validator — don't implement HMAC-SHA1 manually:

**Node.js**
```javascript
const twilio = require("twilio");

app.post("/sms", (req, res) => {
    const valid = twilio.validateRequest(
        process.env.TWILIO_AUTH_TOKEN,
        req.headers["x-twilio-signature"],
        `https://yourdomain.com/sms`,
        req.body
    );
    if (!valid) return res.status(403).send("Forbidden");
    // Process webhook...
});
```

**Common mistakes:**
- Using HTTP URL when Twilio sends to HTTPS (URL must match exactly)
- Forgetting to include query string parameters in validation URL
- Not validating in production because "it worked in dev without it"

**Docs:** See `twilio-webhook-architecture` for full webhook security patterns.

---

## Account-Level Compliance

### PCI DSS (Payment Card Industry)

**PCI Mode is IRREVERSIBLE and account-wide.** Once enabled, it cannot be disabled — ever.

- All recordings are encrypted
- Transcript access is restricted
- Affects every service on the account

**Recommendation:** If you need PCI compliance for one use case, create a **separate sub-account** dedicated to payment-related calls. See `twilio-account-setup` for sub-account patterns.

For call recording during payment, pause recording when the customer gives card numbers:
```python
client.calls(call_sid).recordings(recording_sid).update(status="paused")
```

Or use the `<Pay>` verb to handle payments without your application touching card data:
```xml
<Pay paymentConnector="stripe_connector" chargeAmount="49.99" currency="usd" />
```

### HIPAA (Healthcare)

Before handling Protected Health Information (PHI):
- **Execute a BAA** (Business Associate Agreement) with Twilio — contact your account manager or [submit a sales request](https://www.twilio.com/en-us/help/sales) if you don't have one
- **Encrypt all recordings** containing PHI
- **Minimize PHI in TTS** — don't speak full patient details via `<Say>`
- **Rotate API keys** on a regular schedule
- **Restrict access** to recordings and transcripts

---

## Fraud Prevention

### SMS Pumping Protection

Attackers trigger thousands of OTP messages to premium-rate numbers, generating toll charges.

**Layered defense:**
1. **Twilio Verify Fraud Guard** — built-in fraud detection (enable on Verify Service)
2. **Lookup pre-check** — call `twilio-lookup-phone-intelligence` to check line type + SMS pumping risk score before sending
3. **Geo-permissions** — restrict SMS/voice to countries where you have customers ([Console > Messaging > Geo Permissions](https://console.twilio.com))
4. **Rate limiting** — limit verification attempts per IP, per phone number, per time window

### Geo-Permissions

Restrict which countries can receive messages or calls from your account:
- Disable all countries you don't serve (SMS and Voice separately)
- Re-enable only as needed — [configure in Console](https://www.twilio.com/docs/messaging/guides/sms-geo-permissions)
- This is the single most effective anti-fraud measure for SMS pumping

**SMS pumping impact:** Incidents can climb into tens of thousands of dollars. Twilio does not publish most-targeted prefixes — the general guidance is to restrict message termination to countries where you do business via geo-permissions. Customers using Fraud Guard can view estimated fraud savings in their [Fraud Guard reports](https://www.twilio.com/docs/verify/preventing-toll-fraud/sms-fraud-guard).

---

## Common Mistakes

1. **Auth Token in code** — Pushed to GitHub, leaked. Use environment variables + API keys.
2. **No webhook validation** — Attackers can send fake webhook requests to your endpoints.
3. **PCI Mode on main account** — Irreversible. Use a sub-account for payment use cases.
4. **No geo-permissions** — Account is open to SMS pumping from any country.
5. **Auth Token rotation without planning** — Breaks all API keys simultaneously.

---

## Credential Rotation (Zero-Downtime)

Both API keys and Auth Tokens follow the same workflow:

1. **Create secondary** — generate a new API key (or note the new Auth Token)
2. **Operationalize secondary** — deploy the new credential to all services
3. **Promote secondary to primary** — verify all traffic uses the new credential
4. **Delete old primary** — revoke the previous credential

Manage keys at: `https://console.twilio.com/account/keys-credentials/api-keys` (per account).

**Key enabler: use a secrets manager** (AWS Secrets Manager, HashiCorp Vault, etc.) to inject credentials at runtime. This makes rotation near-instantaneous with no downtime — no code changes, no redeployments. Organizations that hard-code credentials into repos, deployment scripts, or `.env` files must manually update every location before deleting the old key.

For ISVs managing many sub-accounts, automate this with the API Keys REST API across accounts.

---

## Next Steps

- **Credential setup and API key management:** `twilio-iam-auth-setup`
- **Webhook security and signature validation:** `twilio-webhook-architecture`
- **Account structure and sub-accounts:** `twilio-account-setup`
- **Phone intelligence for fraud scoring:** `twilio-lookup-phone-intelligence`
- **Traffic compliance rules:** `twilio-compliance-traffic`
