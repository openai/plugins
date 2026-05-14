---
name: twilio-iam-auth-setup
description: >
  Set up and manage Twilio authentication credentials: Auth Tokens, API keys
  (Standard, Main, Restricted), Access Tokens for client-side SDKs, and
  credential rotation. Use this skill as a prerequisite foundation before
  making any Twilio API calls.
---

## Overview

Twilio supports multiple authentication methods. For most developers: use Auth Token for local prototyping, then move to API Keys in production.

| Method | Use for | Security |
|--------|---------|----------|
| Account SID + Auth Token | Local prototyping, initial testing | Full account access — avoid in production |
| Account SID + API Key (Standard) + Secret | All production code | Recommended — revocable, no access to /Accounts or /Keys |
| Account SID + API Key (Restricted) + Secret | Fine-grained production access | Best — limit to specific resources only |
| Account SID + API Key (Main) + Secret | Account management automation | Full access like Auth Token, but revocable |

**For beginners / vibe-coders:** Start with Auth Token to get your first API call working, then create a Standard API Key before deploying anything. The key difference: if an API Key leaks, you revoke just that key. If your Auth Token leaks, your entire account is exposed until you rotate it.

---

## Prerequisites

- Twilio account — see `twilio-account-setup` if you don't have one
- Access to the [Twilio Console](https://console.twilio.com)

---

## Quickstart

Find your Account SID and Auth Token in the Console dashboard.

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
```

**Node.js**
```node
const client = require("twilio")(
    process.env.TWILIO_ACCOUNT_SID,
    process.env.TWILIO_AUTH_TOKEN
);
```

**Never commit Auth Token to version control or use in production.**

---

## Key Patterns

### API Keys (production)

**Create:** Console > Account > API keys & tokens > Create API key

| Key type | Access | Use case |
|----------|--------|----------|
| **Standard** | All resources except /Accounts and /Keys endpoints | Default for production apps |
| **Restricted** | Only the specific resources you grant | Multi-tenant apps, microservices, least-privilege |
| **Main** | Full account access (like Auth Token) | Account management automation (Console-only creation) |

After creation, copy the **API Key SID** (`SK...`) and **Secret** — the secret is shown only once.

**Python**
```python
client = Client(
    os.environ["TWILIO_API_KEY"],      # SK...
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

### Restricted API Keys

Restricted keys grant access only to specific Twilio API resources you define. Use them for least-privilege access in production.

**Create via the v1 IAM API** (not the v2010 /Keys.json endpoint — see CANNOT section):

**Python**
```python
key = client.iam.v1.api_key.create(
    account_sid=os.environ["TWILIO_ACCOUNT_SID"],
    friendly_name="messaging-only-key",
    key_type="restricted",
    policy={
        "allow": [
            "/2010-04-01/Accounts/{AccountSid}/Messages*"
        ]
    }
)
# Store key.sid and key.secret securely — secret shown only once
```

**Example permission patterns:**
| Permission | Grants access to |
|-----------|-----------------|
| `/2010-04-01/Accounts/{AccountSid}/Messages*` | Send and read messages |
| `/2010-04-01/Accounts/{AccountSid}/Calls*` | Make and manage calls |
| `/v2/Services/*/Verifications*` | Verify API only |

**Docs:** [Restricted API keys](https://www.twilio.com/docs/iam/api-keys/restricted-api-keys)

### Test Credentials

Make API calls without charges or sending real messages. Find at Console > Account > API keys & tokens > Test credentials.

**Python**
```python
client = Client(
    os.environ["TWILIO_TEST_ACCOUNT_SID"],
    os.environ["TWILIO_TEST_AUTH_TOKEN"]
)
```

**Node.js**
```node
const client = require("twilio")(
    process.env.TWILIO_TEST_ACCOUNT_SID,
    process.env.TWILIO_TEST_AUTH_TOKEN
);
```

Magic test numbers:
- `+15005550006` — valid, can receive messages
- `+15005550001` — invalid number (triggers error 21211)
- `+15005550007` — number that cannot receive SMS (triggers error 21612)

### Auth Token Rotation

Rotate your Auth Token if it's been exposed or as periodic security hygiene. Twilio uses a **secondary token promotion** model:

1. Console > Account > API keys & tokens > Request a secondary Auth Token
2. Update your application to use the secondary token
3. Once confirmed working, promote the secondary to primary
4. The old primary token is immediately invalidated

**Python**
```python
# Promote secondary Auth Token to primary via API
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
account = client.api.accounts(os.environ["TWILIO_ACCOUNT_SID"]).update(
    auth_token_promotion="promote"
)
```

**Important:** Auth Token rotation invalidates all active sessions using that token. Plan the switchover to minimize downtime.

**API Keys cannot be rotated** — if an API Key is compromised, delete it and create a new one:
- Console > Account > API keys & tokens > select key > Delete
- Or via API: `client.keys(key_sid).delete()`

**Docs:** [Auth Token REST API](https://www.twilio.com/docs/iam/api/authtoken)

### Access Tokens (client-side SDKs)

Short-lived JWTs for authenticating browser/mobile clients (Voice JS SDK, Conversations SDK, Video SDK). Generate server-side and pass to the client.

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

**Node.js**
```node
const { AccessToken } = require("twilio").jwt;
const { VoiceGrant } = AccessToken;

const token = new AccessToken(
    process.env.TWILIO_ACCOUNT_SID,
    process.env.TWILIO_API_KEY,
    process.env.TWILIO_API_SECRET,
    { identity: "user-123", ttl: 3600 }
);
token.addGrant(new VoiceGrant({ outgoingApplicationSid: "APxxxx" }));
console.log(token.toJwt());
```

Available grant types: `VoiceGrant`, `VideoGrant`, `ChatGrant` (Conversations), `SyncGrant`

### Environment Variable Reference

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Option 1: Auth Token (testing only)
TWILIO_AUTH_TOKEN=your_auth_token

# Option 2: API Key (production)
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your_api_secret

# Test credentials
TWILIO_TEST_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TEST_AUTH_TOKEN=your_test_auth_token
```

---

## CANNOT

- **Standard keys cannot access /Accounts or /Keys endpoints** — Returns error 20003 (401). Must use Auth Token or Main API Key for account management.
- **No restricted key creation via v2010 API** — The v2010 `/Keys.json` endpoint silently ignores `KeyType=restricted` and `Policy` parameters, creating a standard key instead. Use the v1 IAM API.
- **Restricted keys cannot generate Access Tokens** — Only Standard and Main keys can create client SDK tokens.
- **No individual Access Token revocation** — Tokens are valid until expiration (max 24h). To revoke early, delete the API key that issued them.
- **Subaccount credentials cannot access parent or sibling resources** — Each subaccount has its own Auth Token and API Keys. Use the subaccount's own credentials to access its resources — never the parent account's credentials.
- **API Keys cannot be rotated** — No key rotation API exists. To replace a compromised key: create a new key, update your app, then delete the old key.
- **PKCV is an advanced feature for compliance-heavy industries** — Public Key Client Validation adds client-certificate-style auth. Incompatible with Flex, Studio, and TaskRouter. Once enforcement is enabled, Auth Token authentication is disabled (one-way door). See [PKCV docs](https://www.twilio.com/docs/iam/pkcv) — consider this only if your security team requires mutual TLS-equivalent authentication.
- **Test credentials work with only 4 endpoints** — Messages, Calls, IncomingPhoneNumbers, and Lookups. All other endpoints return 403.
- **API Key Secret shown only at creation** — Cannot be retrieved afterward. If lost, create a new key.
- **FriendlyName max 64 characters for keys** — 65+ characters returns error 70001.
- **Restricted keys limited to 100 permissions per key** — Exceeding this limit is rejected at creation.
- **Cannot create Main API Keys via REST API** — Console only
- **Cannot set Access Token TTL beyond 24 hours** — Maximum lifetime is 24h
- **Cannot use test credentials with real numbers** — Test credentials only work with test magic numbers

---

## Next Steps

- **Account setup and phone numbers:** `twilio-account-setup`
- **Security best practices (credential management, key rotation):** `twilio-security-hardening`
- **Restricted API keys (fine-grained permissions):** [Docs](https://www.twilio.com/docs/iam/api-keys/restricted-api-keys)
- **Auth Token rotation:** [REST API](https://www.twilio.com/docs/iam/api/authtoken)
