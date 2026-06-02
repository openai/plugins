---
name: twilio-customer-memory
description: >
  Store and retrieve customer context using Twilio Conversation Memory.
  Covers Memory Store provisioning, profile management, traits, observations,
  conversation summaries, and semantic Recall. Use this skill to give AI agents
  or human agents persistent memory of customer interactions across sessions
  and channels.
---

## Overview

Conversation Memory gives your application persistent customer memory. Observations (what happened) and traits (who the customer is) are written automatically from conversations flowing through Conversation Orchestrator/Orchestrator — or posted directly if you run your own extraction. Retrieve relevant context via Recall before responding.

```
Conversation Orchestrator/Orchestrator conversation → auto-extracted observations & summaries → Memory Store
Your App → Recall → relevant context injected into LLM prompt
```

**All Conversation Memory APIs are on `memory.twilio.com`.** Observations, traits, profiles, summaries — everything is on the same host.

**Auth: Basic Auth** — `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.

---

## Prerequisites

- Twilio account with Conversation Memory access (requires enablement)
  — New to Twilio? See `twilio-account-setup`
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`
- **Memory Store must be created before creating a Conversations Service in Conversation Orchestrator/Orchestrator** — the store SID is required in the conversation config
- For conversation orchestration: `twilio-conversation-orchestrator`

---

## Quickstart

### Step 1 — Create a Memory Store

Do this before setting up Conversation Orchestrator/Orchestrator. The Memory Store SID goes into your conversation service config.

**Python**
```python
import os, requests

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

store = requests.post(
    "https://memory.twilio.com/v1/Services",
    auth=(account_sid, auth_token),
    json={
        "uniqueName": "my-app-memory",
        "friendlyName": "My App Memory Store"
    }
).json()

memory_store_sid = store["sid"]
print(memory_store_sid)
```

**Node.js**
```javascript
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;

const store = await fetch("https://memory.twilio.com/v1/Services", {
    method: "POST",
    headers: {
        "Authorization": "Basic " + btoa(`${accountSid}:${authToken}`),
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        uniqueName: "my-app-memory",
        friendlyName: "My App Memory Store",
    }),
}).then(r => r.json());

const memoryStoreSid = store.sid;
```

Use `memory_store_sid` when creating your Conversations Service in Conversation Orchestrator/Orchestrator. The two must be linked for automatic observation and summary extraction to work.

### Step 2 — Profiles

Profiles are **created automatically** when conversations flow through Conversation Orchestrator/Orchestrator — the conversation config determines how participants are resolved into profiles. You can also create or enrich profiles manually using traits.

**Create a profile manually with traits:**

**Python**
```python
profile = requests.post(
    f"https://memory.twilio.com/v1/Services/{memory_store_sid}/Profiles",
    auth=(account_sid, auth_token),
    json={
        "traits": {
            "Contact": {
                "phone": "+15558675310",
                "firstName": "Alyssa",
                "lastName": "Mock",
                "email": "alyssa@example.com"
            }
        }
    }
).json()

profile_id = profile["id"]
```

**Node.js**
```javascript
const profile = await fetch(
    `https://memory.twilio.com/v1/Services/${memoryStoreSid}/Profiles`,
    {
        method: "POST",
        headers: {
            "Authorization": "Basic " + btoa(`${accountSid}:${authToken}`),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            traits: {
                Contact: {
                    phone: "+15558675310",
                    firstName: "Alyssa",
                    lastName: "Mock",
                    email: "alyssa@example.com",
                }
            }
        }),
    }
).then(r => r.json());

const profileId = profile.id;
```

**Look up a profile by phone number** (for inbound calls where you only have the caller's number):

**Python**
```python
lookup = requests.post(
    f"https://memory.twilio.com/v1/Services/{memory_store_sid}/Profiles/Lookup",
    auth=(account_sid, auth_token),
    json={"idType": "phone", "value": "+15558675310"}
).json()

profile_id = lookup["profiles"][0]["id"] if lookup.get("profiles") else None
```

### Step 3 — Observations

Observations are **extracted automatically** from conversations when a conversation becomes inactive or is closed, based on your conversation config. You don't need to write them manually for Conversation Orchestrator-managed conversations.

**If you run your own extraction** (custom pipeline outside Conversation Orchestrator), post results directly:

**Python**
```python
requests.post(
    f"https://memory.twilio.com/v1/Services/{memory_store_sid}/Profiles/{profile_id}/Observations",
    auth=(account_sid, auth_token),
    json={
        "observations": [
            {
                "content": "Customer asked about order #4521. Wants expedited shipping. Prefers SMS updates.",
                "source": "custom_extraction",
                "occurredAt": "2026-04-20T14:30:00Z",
                "conversationIds": [conversation_sid]
            }
        ]
    }
)
```

**Node.js**
```javascript
await fetch(
    `https://memory.twilio.com/v1/Services/${memoryStoreSid}/Profiles/${profileId}/Observations`,
    {
        method: "POST",
        headers: {
            "Authorization": "Basic " + btoa(`${accountSid}:${authToken}`),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            observations: [{
                content: "Customer asked about order #4521. Wants expedited shipping. Prefers SMS updates.",
                source: "custom_extraction",
                occurredAt: new Date().toISOString(),
                conversationIds: [conversationSid],
            }]
        }),
    }
);
```

Batch up to 10 observations in one request.

### Step 4 — Recall Context Before Responding

Recall runs hybrid lexical + semantic search and returns the most relevant observations and summaries for an LLM prompt.

**Recommended: pass a `conversationId` from Conversation Orchestrator/Orchestrator.** Recall builds a contextually relevant query from the active conversation automatically — no need to craft one yourself.

**Python**
```python
recall = requests.post(
    f"https://memory.twilio.com/v1/Services/{memory_store_sid}/Profiles/{profile_id}/Recall",
    auth=(account_sid, auth_token),
    json={
        "conversationId": orchestrator_conversation_sid,
        "observationsLimit": 10,
        "summariesLimit": 3,
    }
).json()

observations = "\n".join(o["content"] for o in recall.get("observations", []))
summaries = "\n".join(s["content"] for s in recall.get("summaries", []))

system_prompt = f"""You are a helpful support agent.

Customer history:
{observations}

Recent summaries:
{summaries}"""
```

**Node.js**
```javascript
const recall = await fetch(
    `https://memory.twilio.com/v1/Services/${memoryStoreSid}/Profiles/${profileId}/Recall`,
    {
        method: "POST",
        headers: {
            "Authorization": "Basic " + btoa(`${accountSid}:${authToken}`),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            conversationId: orchestratorConversationSid,
            observationsLimit: 10,
            summariesLimit: 3,
        }),
    }
).then(r => r.json());

const context = [
    ...recall.observations.map(o => o.content),
    ...recall.summaries.map(s => s.content),
].join("\n");
```

**Other Recall modes:**

| Mode | How | When to use |
|------|-----|-------------|
| Conversation ID (recommended) | `"conversationId": orchestrator_sid` | Active Conversation Orchestrator/Orchestrator conversation — query is generated from conversation context |
| Custom query | `"query": "your question"` | Custom pipelines outside Conversation Orchestrator, or when you need precise control over relevance |
| No query | Omit both `query` and `conversationId` | Returns most recent observations in chronological order — useful for loading history at session start |

---

## Key Patterns

### Trait Groups

Traits are organized into named groups. The `Contact` group is the standard identity anchor — its fields are promoted to profile identifiers for lookup.

| Group | Fields | Use |
|-------|--------|-----|
| `Contact` | phone, email, firstName, lastName | Identity anchor — always include |
| `Account` | accountNumber, tier, region | Business account data |
| `Support` | disposition, caseId, lastIssueType | Support history |

Define your own groups for domain-specific data.

### Summaries

Summaries are written automatically at conversation close or when a conversation goes inactive, based on your conversation config — the same trigger as observations. You can also write them manually:

**Python**
```python
requests.post(
    f"https://memory.twilio.com/v1/Services/{memory_store_sid}/Profiles/{profile_id}/ConversationSummaries",
    auth=(account_sid, auth_token),
    json={
        "conversationId": conversation_sid,
        "content": "Customer called about order #4521. Resolved: approved expedited upgrade.",
        "source": "manual"
    }
)
```

Summaries are returned in the `summaries` array of Recall results.

### Voice Agent Integration

Retrieve memory at call start, store observations at call end. For voice AI agents on ConversationRelay.

**Python (WebSocket handler)**
```python
async def handle_call(websocket):
    setup = json.loads(await websocket.recv())
    caller = setup.get("from", "unknown")

    # Look up profile by caller phone
    lookup = requests.post(
        f"https://memory.twilio.com/v1/Services/{MEMORY_STORE_SID}/Profiles/Lookup",
        auth=(ACCOUNT_SID, AUTH_TOKEN),
        json={"idType": "phone", "value": caller}
    ).json()
    profiles = lookup.get("profiles", [])
    profile_id = profiles[0]["id"] if profiles else None

    context = ""
    if profile_id:
        recall = requests.post(
            f"https://memory.twilio.com/v1/Services/{MEMORY_STORE_SID}/Profiles/{profile_id}/Recall",
            auth=(ACCOUNT_SID, AUTH_TOKEN),
            json={"observationsLimit": 5, "summariesLimit": 2}
        ).json()
        context = "\n".join(o["content"] for o in recall.get("observations", []))

    system_prompt = f"You are a helpful agent.\n\nCustomer history:\n{context}" if context else "You are a helpful agent."

    # ... handle conversation ...

    # Store observation at end if running custom extraction
    if profile_id:
        requests.post(
            f"https://memory.twilio.com/v1/Services/{MEMORY_STORE_SID}/Profiles/{profile_id}/Observations",
            auth=(ACCOUNT_SID, AUTH_TOKEN),
            json={"observations": [{"content": call_summary, "source": "voice_agent", "conversationIds": [orchestrator_conversation_sid]}]}
        )
```

### Multi-Tenant (ISV) Pattern

Use one Memory Store per client. The `uniqueName` doubles as a namespace.

```python
# At client onboarding
store = requests.post(
    "https://memory.twilio.com/v1/Services",
    auth=(account_sid, auth_token),
    json={"uniqueName": f"client-{client_id}", "friendlyName": client_name}
).json()
# Store store["sid"] in your tenant config — pass it to Conversation Orchestrator conversation service setup
```

---

## CANNOT

- **Cannot create Conversation Orchestrator before Memory Store** — Create Memory Store first. Its SID is required when creating the Conversations Service. Reversing this order breaks the linkage.
- **Cannot extract observations mid-conversation** — Automatic extraction happens on conversation close or inactive. For real-time writing, post directly to the Observations endpoint.
- **Cannot read observations immediately after write** — Eventual consistency. Allow ~2 seconds after write before querying Recall.
- **Cannot exceed 15 Memory Stores per account** — ISVs with more than 15 tenants should use sub-accounts
- **Cannot detect misconfigured linkages** — If Memory Store is not correctly linked in Conversation Orchestrator config, observations are silently not extracted. See `twilio-debugging-observability`.
- **Cannot recover deleted profiles** — Profile deletion is irreversible, permanent
- **Cannot exceed 20 observations per Recall query** — `observationsLimit` max 20, default 5. `summariesLimit` and `communicationsLimit` similar.
- **Cannot batch more than 10 observations per request** — Hard limit on batch writes

---

## Next Steps

- **Set up Conversation Orchestrator conversations:** `twilio-conversation-orchestrator`
- **Add real-time intelligence:** `twilio-conversation-intelligence`
- **Enterprise knowledge retrieval (scripts, offers, policies):** `twilio-enterprise-knowledge`
- **Voice agent setup:** `twilio-voice-conversation-relay`
- **Debug integration issues:** `twilio-debugging-observability`
