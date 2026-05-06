---
name: twilio-account-setup
description: >
  Create and configure a Twilio account from scratch. Covers free trial signup,
  trial limitations, getting credentials (Account SID and Auth Token), buying
  a phone number, verifying recipient numbers for trial use, SDK installation,
  first API call, subaccount management (creation, inheritance, credential
  isolation, limits), and enabling specific products (AI Assistants,
  Conversations, Verify, ConversationRelay, WhatsApp). Use this skill before
  any other Twilio skill if you do not yet have a Twilio account or need to
  enable a product. For Organization-level governance (SSO, SCIM, multi-team),
  see `twilio-organizations-setup`.
---

## Overview

Every Twilio skill requires an active Twilio account and credentials. This skill covers the one-time setup steps that are prerequisites for all other Twilio skills.

---

## Quickstart

1. Sign up at [twilio.com/try-twilio](https://www.twilio.com/try-twilio) -- enter name, email, password
2. Verify your email and personal phone number
3. Get your credentials from [Console > Account > API keys & tokens](https://console.twilio.com/us1/account/keys-credentials/api-keys):

```bash
export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export TWILIO_AUTH_TOKEN=your_auth_token
```

4. Buy a phone number at [Console > Phone Numbers > Buy a number](https://console.twilio.com/us1/develop/phone-numbers/search)

5. Install the SDK and send your first message:

**Python**
```bash
pip install twilio
```
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
message = client.messages.create(
    to="+15558675310",  # must be verified on trial accounts
    from_="+15017122661",  # your Twilio number
    body="Hello from Twilio!"
)
print(f"Sent: {message.sid}")
```

**Node.js**
```bash
npm install twilio
```
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const message = await client.messages.create({
    to: "+15558675310",  // must be verified on trial accounts
    from: "+15017122661",  // your Twilio number
    body: "Hello from Twilio!",
});
console.log(`Sent: ${message.sid}`);
```

You're ready to use any Twilio skill. Trial accounts have restrictions -- see Constraints below.

---

## Key Patterns

### Verify Recipient Numbers (trial accounts only)

Trial accounts can only send to **verified phone numbers** (up to 5 per account).

1. Go to [Console > Phone Numbers > Verified Caller IDs](https://console.twilio.com/us1/develop/phone-numbers/verified-caller-ids)
2. Click **Add a new Caller ID** and verify via SMS code

Verified numbers work across both messaging and voice. Remove this restriction by upgrading your account.

### Enable Specific Products

Some products require explicit activation:

| Product | How to enable |
|---------|--------------|
| AI Assistants | [Console > Explore Products > AI Assistants](https://console.twilio.com/us1/develop/ai-assistants) > **Get started** |
| Conversations | [Console > Conversations > Manage > Overview](https://console.twilio.com/us1/develop/conversations/manage/overview) > **Enable Conversations** |
| Verify | [Console > Verify > Services](https://console.twilio.com/us1/verify/services) > **Create new** |
| WhatsApp (sandbox) | [Console > Messaging > Try it out > Send a WhatsApp message](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn) |
| ConversationRelay | [Console > Voice > ConversationRelay](https://console.twilio.com/us1/voice/conversation-relay) > complete onboarding form |

### SDK Installation

| Language | Install | SDK package |
|----------|---------|-------------|
| Python | `pip install twilio` | `twilio` |
| Node.js | `npm install twilio` | `twilio` |
| Java | Maven/Gradle | `com.twilio.sdk:twilio` |
| C# | `dotnet add package Twilio` | `Twilio` |
| Ruby | `gem install twilio-ruby` | `twilio-ruby` |
| PHP | `composer require twilio/sdk` | `twilio/sdk` |
| Go | `go get github.com/twilio/twilio-go` | `twilio-go` |

### Initialize the Client

Always load credentials from environment variables -- never hardcode them.

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
```

For production, use API Keys instead of Auth Token. See `twilio-iam-auth-setup`.

### Twilio CLI Setup

The CLI is useful for quick operations and local webhook testing.

```bash
# Install (macOS)
brew tap twilio/brew && brew install twilio

# Install (npm -- all platforms)
npm install -g twilio-cli

# Login (creates an API key automatically)
twilio login

# Verify setup
twilio phone-numbers:list
```

The CLI stores profiles for switching between accounts:
```bash
# List profiles
twilio profiles:list

# Switch active profile
twilio profiles:use my-project

# Use environment variables instead of profiles
export TWILIO_ACCOUNT_SID=ACxxxxxxxx
export TWILIO_AUTH_TOKEN=xxxxxxxx
```

Precedence: `--profile` flag > environment variables > active profile.

### Accounts and Subaccounts

**Creating a new Twilio account:** Accounts can only be created from the Console UI — there is no API for creating top-level accounts. A new account is automatically created when a user signs up. Additional accounts can be created from Console > My Accounts (or "View all accounts").

**To see all your accounts:** Console > My Accounts shows all accounts and subaccounts you have access to. For Organization-wide visibility, see Console > Admin > Accounts (requires Organization admin role). See `twilio-organizations-setup` for Organization-level governance.

### Subaccounts

Subaccounts are child accounts under your main (parent) account. Use them for multi-tenant apps, per-customer isolation, or team separation.

**How they differ from the parent account:**
- Resources (numbers, calls, messages) are **isolated** — a subaccount cannot see the parent's resources or other subaccounts' resources
- Billing is **consolidated** to the parent — a single Twilio balance for all subaccounts
- Voice and SMS permissions **inherit** from the parent
- Phone numbers can be transferred between parent and subaccounts

**Create via Console:** Console > My Accounts > Create Subaccount

**Create via API:**

**Python**
```python
subaccount = client.api.accounts.create(friendly_name="Customer A")
print(f"Subaccount SID: {subaccount.sid}")
# Store securely — auth_token is only shown at creation time
# e.g., secrets_manager.store("subaccount_auth_token", subaccount.auth_token)
```

**Node.js**
```javascript
const subaccount = await client.api.accounts.create({ friendlyName: "Customer A" });
console.log(`Subaccount SID: ${subaccount.sid}`);
```

### Subaccount Credential Isolation

**Always use the subaccount's own credentials** (API Keys or Auth Token) when accessing subaccount resources — do NOT use the parent account's credentials as a shortcut.

**Python — access subaccount resources**
```python
# Correct: use subaccount credentials
sub_client = Client(subaccount.sid, subaccount.auth_token)
call = sub_client.calls.create(
    to="+15558675310",
    from_="+15017122661",  # number owned by this subaccount
    url="https://yourapp.com/voice"
)

# Also correct: parent credentials with subaccount SID (v2010 API only)
parent_client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
calls = parent_client.api.accounts(subaccount.sid).calls.list()
```

**Critical:** Resources on separate subdomains (`studio.twilio.com`, `taskrouter.twilio.com`) **require subaccount-specific credentials**. Parent account credentials will not work on these subdomains.

### Subaccount Limits

- **Default limit:** 1,000 subaccounts per parent account
- **Trial accounts:** Can create only 1 subaccount — upgrade to create more
- **At the limit:** Contact Twilio Support with your use case to request an increase
- **Closing:** Set status to `closed` via API or Console. Closed subaccounts are automatically deleted after 30 days
- **Suspension cascade:** Suspending the parent account automatically suspends ALL subaccounts

### Upgrade from Trial

1. Click **Upgrade** at the top of the Console, or go to [Console > Admin > Account billing](https://console.twilio.com/us1/admin/billing)
2. Provide name, address, and payment details
3. Your trial phone number carries over; trial balance does not

---

## Trial Restrictions at a Glance

| Feature | Trial | Upgraded |
|---------|-------|----------|
| Phone numbers | 1 | Unlimited |
| Send to unverified numbers | No | Yes |
| Outbound message prefix | Yes (visible to recipient) | No |
| Verified caller IDs | Up to 5 | Not needed |
| A2P 10DLC registration | No | Yes |
| Daily WhatsApp messages | 50 | Unlimited |
| ConversationRelay | No | Yes (after onboarding) |
| Voice: outbound calls | Domestic only | International |

---

## CANNOT

- **Cannot create top-level accounts via API** — Only Console UI. A new account is created at signup; additional accounts from Console > My Accounts.
- **Cannot create more than 1 subaccount on trial** — Upgrade your account first, then you can create up to 1,000.
- **Cannot access subdomain resources with parent credentials** — Studio, TaskRouter, and other subdomain APIs require subaccount-specific credentials. Parent credentials return auth errors.
- **Cannot undo a closed subaccount after 30 days** — Closed subaccounts are permanently deleted. Suspension is reversible; closure is not.
- **Cannot transfer trial balance to a paid account** — Trial credits are forfeited on upgrade.
- **Cannot send to unverified numbers on trial** — Only verified Caller IDs (up to 5) can receive messages or calls.
- **Auth Token rotation invalidates ALL API keys** — This is a one-way door. Use API Keys from day one. See `twilio-security-api-auth`.
- **API Key secrets shown only once at creation** — Store them immediately. Cannot be retrieved afterward.
- **AI Assistants and ConversationRelay require approval** — Limited access products. Activation is not instant.

---

## Next Steps

- **Organization governance (SSO, SCIM, multi-team):** `twilio-organizations-setup`
- **Secure credential management and API Keys:** `twilio-security-api-auth`
- **Send your first SMS:** `twilio-sms-send-message`
- **Send your first WhatsApp message:** `twilio-whatsapp-send-message`
- **Receive incoming messages:** `twilio-messaging-webhooks`
- **US SMS compliance (A2P 10DLC):** `twilio-compliance-onboarding`
- **Webhook setup:** `twilio-webhook-architecture`
