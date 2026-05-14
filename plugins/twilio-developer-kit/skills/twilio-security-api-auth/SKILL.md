---
name: twilio-security-api-auth
description: >
  Choose the right Twilio authentication method and implement it correctly.
  Covers Auth Token (testing only), API Keys (production standard), OAuth2
  client_credentials (time-limited bearer tokens), Access Tokens (client-side
  SDKs), and test credentials. Use this skill before making any Twilio API
  calls in production.
---

## Overview

Twilio supports four authentication methods. Choosing the wrong one is a security risk — Auth Tokens in production code are the most common credential leak.

| Method | Use for | Token lifetime | Revocable individually |
|--------|---------|---------------|----------------------|
| **Auth Token** | Local testing only | Permanent (until rotated) | No — rotation breaks ALL API keys |
| **API Key + Secret** | Production server-side | Permanent (until deleted) | Yes |
| **OAuth2 Bearer Token** | Production server-side (enhanced) | 1 hour | Expires automatically |
| **Access Token (JWT)** | Client-side SDKs (Voice, Video, Chat) | Up to 24 hours | No — delete issuing API key |

**Decision framework:**
- **Building a quick prototype?** → Auth Token (but switch to API Key before deploying)
- **Production server-side code?** → API Key + Secret (simplest production auth) or OAuth2 (time-limited tokens)
- **Browser/mobile client needs to connect?** → Access Token (JWT) generated server-side
- **Running tests without charges?** → Test credentials with magic numbers

---

## API Key Authentication (Production Standard)

**Create:** Console → Account → API keys & tokens → Create API key

| Key type | Access | Create via |
|----------|--------|-----------|
| **Main** | Full account access | Console only |
| **Standard** | All resources except /Accounts and /Keys endpoints | Console or API |
| **Restricted** | Specific resources only (up to 100 permissions) | Console or v1 IAM API only |

**Python**
```python
import os
from twilio.rest import Client

client = Client(
    os.environ["TWILIO_API_KEY"],      # SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    os.environ["TWILIO_API_SECRET"],
    os.environ["TWILIO_ACCOUNT_SID"]   # required as third argument
)
```

**Node.js**
```node
const client = require("twilio")(
    process.env.TWILIO_API_KEY,
    process.env.TWILIO_API_SECRET,
    { accountSid: process.env.TWILIO_ACCOUNT_SID }
);
```

---

## OAuth2 Authentication (Client Credentials)

Time-limited bearer tokens that expire after 1 hour. More secure than permanent API keys for server-to-server communication.

### Step 1 — Create an OAuth App

Create an OAuth App in the Twilio Console to get a Client ID and Client Secret.

### Step 2 — Request a Bearer Token

**cURL**
```bash
curl -X POST 'https://oauth.twilio.com/v2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'client_id={ClientID}' \
  -d 'client_secret={ClientSecret}' \
  -d 'grant_type=client_credentials'
```

**Response:**
```json
{
    "access_token": "{BearerToken}",
    "token_type": "Bearer",
    "expires_in": 3600
}
```

### Step 3 — Use the Bearer Token

```bash
curl 'https://api.twilio.com/2010-04-01/Accounts/{AccountSID}/Messages.json' \
  -H 'Authorization: Bearer {BearerToken}'
```

### SDK Support

OAuth2 is supported in all Twilio SDKs:

| Language | Minimum version |
|----------|----------------|
| Java | 10.6.0 |
| C#/.NET | 7.6.0 |
| Node.js | 5.4.0 |
| Python | 9.4.1 |
| Ruby | 7.4.0 |
| PHP | 8.5.0 |
| Go | 1.25.1 |

**Docs:** [OAuth access tokens](https://www.twilio.com/docs/iam/oauth-apps/oauth-access-token) | [Segment OAuth connections](https://www.twilio.com/docs/segment/connections/oauth)

---

## Access Tokens (Client-Side SDKs)

Short-lived JWTs for authenticating browser/mobile clients. Generate server-side, pass to the client.

**Python**
```python
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

token = AccessToken(
    os.environ["TWILIO_ACCOUNT_SID"],
    os.environ["TWILIO_API_KEY"],
    os.environ["TWILIO_API_SECRET"],
    identity="user-123",
    ttl=3600
)
token.add_grant(VoiceGrant(outgoing_application_sid="APxxxx"))
print(token.to_jwt())
```

Grant types: `VoiceGrant`, `VideoGrant`, `ChatGrant` (Conversations), `SyncGrant`

---

## Test Credentials

Make API calls without charges. Find at Console → Account → API keys & tokens → Test credentials.

Magic numbers: `+15005550006` (valid), `+15005550001` (invalid, error 21211), `+15005550007` (no SMS, error 21612)

---

## CANNOT

- **Standard keys cannot access /Accounts or /Keys endpoints** — Returns 20003 (401). Use Auth Token or Main key.
- **Cannot create restricted keys via v2010 API** — Silently creates a standard key instead. Use v1 IAM API.
- **Restricted keys cannot generate Access Tokens** — Only Standard and Main keys can.
- **Cannot revoke individual Access Tokens** — Valid until expiration (max 24h). Delete the issuing API key to revoke all.
- **OAuth2 only supports `client_credentials` grant** — No refresh tokens, no authorization code flow.
- **OAuth2 tokens expire after 1 hour** — Your application must handle token refresh.
- **API Key Secret shown only at creation** — Cannot be retrieved afterward.
- **Auth Token rotation breaks ALL API keys** — One-way door. This is why you should use API keys from day one.
- **Test credentials work with only 4 endpoints** — Messages, Calls, IncomingPhoneNumbers, Lookups. All others return 403.

---

## Next Steps

- **Account setup and sub-accounts:** `twilio-account-setup`
- **HIPAA account configuration:** `twilio-security-compliance-hipaa`
- **Webhook signature validation:** `twilio-webhook-architecture`
- **Credential security patterns:** `twilio-security-hardening`
