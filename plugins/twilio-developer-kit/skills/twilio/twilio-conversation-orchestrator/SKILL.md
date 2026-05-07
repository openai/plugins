---
name: twilio-conversation-orchestrator
description: >
  Configure automatic conversation capture and routing with Twilio Conversation
  Orchestrator. Covers Configuration creation, channel capture rules, grouping
  types, status timeouts, Memory Store linkage, Intelligence linkage, and
  conversation lifecycle. Use this skill to automatically capture SMS, voice,
  WhatsApp, RCS, and web chat traffic into unified conversations without
  manually creating conversations or participants.
---

# Conversation Orchestrator

Decision-making guide for Twilio's Conversation Orchestrator (Conversations v2) — automatic conversation capture and routing across Voice, SMS, WhatsApp, RCS, and web chat. Covers Configurations, capture rules, grouping types, channel settings, status timeouts, and linkage to Conversation Memory and Conversation Intelligence.

> **GA** — Conversation Orchestrator is generally available.

## Use Cases

Conversation Orchestrator powers **automatic conversation capture and integration with existing voice implementations** — replacing manual conversation creation with either:
- **Passive ingestion**: Declarative capture rules that automatically capture traffic as it flows
- **Active ingestion**: TwiML parameters or API calls that route existing implementations into conversations

**Note:** Active and passive ingestion can be configured on a per-channel basis. For example, you can use passive capture rules for SMS while using active TwiML parameters for voice calls.

## ⚠️ CRITICAL: Voice Double Billing Warning

> **WARNING: You can be charged for STT (speech-to-text) twice on the same call if misconfigured.**

If you are using voice with ConversationRelay or Transcription in TwiML:

**We do not recommend using passive voice capture rules (`captureRules`) in your Configuration when using active TwiML.**

See the full [Voice Double Billing Warning](#️-critical-voice-double-billing-warning-1) section below for details.

### Unified Customer Context

Capture all channels (voice, SMS, WhatsApp, RCS, CHAT (via Conversation API (classic))) into a single conversation thread per customer. Conversation Memory resolves identity across channels and maintains persistent context. **Start here** — this is the most common pattern.

- **Grouping**: `GROUP_BY_PROFILE`
- **Channels**: SMS + VOICE + WHATSAPP + RCS + CHAT (via Conversation API (classic))
- **Linkage**: Memory Store (identity resolution) + Intelligence (analysis)

### Channel-Isolated Analytics

Keep voice transcripts separate from SMS threads for per-channel analysis. Intelligence operators run independently on each channel's conversation.

- **Grouping**: `GROUP_BY_PARTICIPANT_ADDRESSES_AND_CHANNEL_TYPE`
- **Channels**: SMS + VOICE (separate conversations)
- **Linkage**: Intelligence (per-channel operators)

### Agent Connect Integration

Capture conversations for AI-to-human escalation via Agent Connect (TAC SDK). Uses address-pair grouping required by the SDK.

- **Grouping**: `GROUP_BY_PARTICIPANT_ADDRESSES`
- **Channels**: SMS or VOICE
- **Linkage**: Memory Store + Intelligence + Agent Connect

### Post-Conversation Memory Extraction

Automatically extract observations from conversations into Conversation Memory. Opt-in — configure once, every conversation feeds the memory loop.

- **Config**: `memoryExtractionEnabled: true`
- **Trigger**: INACTIVE and/or CLOSED lifecycle transitions (configurable)
- **Result**: Observations and summaries written to linked Memory Store profiles

## How It Works

### Passive Ingestion (Capture Rules)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Inbound/outbound traffic arrives (SMS, Voice, WhatsApp, RCS)           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Capture rules match on phone number patterns                           │
│     - from/to with wildcards (e.g., from: *, to: +15551234567)             │
│     - Per-channel rules (SMS, VOICE, WHATSAPP, RCS)                        │
│     - Metadata filters (callType for CLIENT/SIP)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Conversation auto-created (or existing one matched via grouping)        │
│     - GROUP_BY_PROFILE: merge by Memory Profile identity                   │
│     - GROUP_BY_PARTICIPANT_ADDRESSES: merge by address pair                │
│     - GROUP_BY_..._AND_CHANNEL_TYPE: separate per channel                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Linked services activate                                               │
│     - Memory Store: identity resolution, profile auto-creation             │
│     - Intelligence: operators fire per Communication or at close           │
│     - Status timeouts: ACTIVE → INACTIVE → CLOSED lifecycle                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. On conversation close                                                  │
│     - Memory extraction: observations written to Memory Store              │
│     - CONVERSATION_END Intelligence operators fire (Summary, etc.)         │
│     - Status callbacks delivered (if configured)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Active Ingestion (TwiML or API)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Voice call arrives OR you create conversation via API                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2a. TwiML: Pass conversationConfiguration or conversationId parameter      │
│      - <ConversationRelay conversationConfiguration="CONFIG_ID">           │
│      - <Transcription conversationId="CONV_ID">                            │
│  2b. API: POST to /v2/Conversations with participants                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Conversation created or matched based on parameter                      │
│     - conversationConfiguration: uses grouping rules                       │
│     - conversationId: routes to specific conversation                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Voice transcription or API communications added                         │
│     - Same linked services activate (Memory Store, Intelligence)           │
│     - Same lifecycle: ACTIVE → INACTIVE → CLOSED                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. On conversation close                                                  │
│     - Memory extraction: observations written to Memory Store              │
│     - CONVERSATION_END Intelligence operators fire (Summary, etc.)         │
│     - Status callbacks delivered (if configured)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Scope

### CAN

- Automatically capture SMS, voice, WhatsApp, RCS, and CHAT (via Conversation API (classic)) into Conversations via passive ingestion (capture rules) OR work with existing voice implementations via active ingestion (TwiML parameters: conversationConfiguration, conversationId)
- Merge multiple channels into one Conversation thread via `GROUP_BY_PROFILE`
- Link Memory Store for automatic identity resolution and observation extraction
- Link multiple Intelligence Configurations for real-time and post-conversation analysis
- Bridge Conversation API (classic) Services for browser SDK chat via `conversationsV1Bridge`
- Configure per-channel capture rules with wildcard matching
- Set independent timeout policies per channel
- Add `statusCallbacks` for webhook notifications on conversation state changes
- Pass `conversationConfiguration` or `conversationId` in `<ConversationRelay>` or `<Transcription>` TwiML to create or route to a conversation (Active TwiML mode) — both parameters supported in both TwiML verbs
- Close conversations explicitly via PATCH to trigger Memory extraction and CONVERSATION_END operators
- List and filter Conversations by status, channel, and date range
- Read Communications (messages + voice utterances) within a Conversation
- Authenticate with Account SID/Auth Token or API Key/Secret

### CANNOT

- **Cannot update Configurations with PATCH** — PUT only, full replacement. Omitting fields deletes them. Always re-fetch before updating.
- **Cannot exceed 10 Configurations per account** — Hard limit at GA. Each config supports up to 100 capture rules per channel. Delete unused configs to make room. Plan Configuration topology for large phone number portfolios accordingly (e.g., 101 numbers for one channel requires 2 configs).
- **Cannot change grouping type after creation** — `conversationGroupingType` is immutable on a Configuration. Create a new config if you need a different grouping.
- **Cannot capture CLIENT or SIP voice calls without explicit callType metadata** — PSTN is captured by default. Browser (Client SDK) and SIP calls require `metadata.callType` in capture rules.
- **Not recommended to combine passive VOICE capture rules with active TwiML voice (ConversationRelay or Transcription with conversation parameters)** — You will be double-charged for STT. The system does not prevent this configuration, but it is not recommended. Passive voice capture uses Real-Time Transcription (RTT) under the hood. If you pass `conversationConfiguration` or `conversationId` in `<ConversationRelay>` or `<Transcription>` TwiML, you are using active ingestion which has its own STT engine. Both engines will run = double STT billing. Use active TwiML (pass conversation parameters) OR passive capture rules (captureRules), not both for the same traffic. See the [Voice Double Billing Warning](#️-critical-voice-double-billing-warning) section above.
- **Cannot detect failed Memory linkage** — If `memoryStoreId` points to a deleted or invalid store, capture still works but identity resolution and extraction silently fail. See `twilio-debugging-observability`.
- **Cannot filter Intelligence operators by participant type** — Operators fire on ALL Communications (customer and agent). Use the operator prompt to specify which participant to analyze.
- **Cannot extract Memory observations mid-conversation (ACTIVE state)** — Extraction is opt-in and can fire on INACTIVE and/or CLOSED lifecycle transitions, but not while the conversation is ACTIVE. For real-time Memory writes during an active conversation, post Observations directly via `twilio-customer-memory`.
- **Cannot have conversations pick up config changes retroactively** — Conversations pin the Configuration version at creation time. Close existing conversations to apply updated rules.
- **Cannot use the POST response to get the Configuration ID** — Creation returns 202 with an operation. Poll the operation's `statusUrl` until `status` is `COMPLETED`, then retrieve the configuration ID from the operation result.
- **No standalone operation** — Requires a Memory Store because Conversation Orchestrator uses profiles for identity resolution. `memoryStoreId` is mandatory when creating a Configuration.
- **JSON-only API** — All Conversation Orchestrator endpoints require `Content-Type: application/json`. Form-encoded bodies are rejected.

## Quick Decision

| Need | Use | Why |
|------|-----|-----|
| Already have ConversationRelay or Transcription voice implementation | Pass `conversationConfiguration` or `conversationId` in TwiML (Active ingestion) — do NOT add passive VOICE capture rules | More granular control over which calls are captured. Avoids double STT billing. |
| Capture all messaging into unified customer conversations | Configuration with passive capture rules + Memory Store + `GROUP_BY_PROFILE` | Automatic capture with cross-channel identity resolution |
| Keep voice and SMS conversations separate | Configuration with `GROUP_BY_PARTICIPANT_ADDRESSES_AND_CHANNEL_TYPE` | Channel-isolated threads for per-channel analytics |
| Auto-extract customer observations from conversations | Set `memoryExtractionEnabled: true` on Configuration | Triggers on conversation close, writes to linked Memory Store |
| Analyze conversations with Intelligence operators | Link `intelligenceConfigurationIds` on Configuration | Operators fire per Communication or at conversation close |
| Capture browser voice calls (Client SDK) | Add VOICE capture rule with `metadata.callType: "CLIENT"` | PSTN-only by default; CLIENT needs explicit rule |
| Capture CHAT (via Conversation API (classic)) | Set `conversationsV1Bridge.serviceId` on Configuration | CHAT flows through a Conversations (v1) Service bridged into Orchestrator |

## ⚠️ CRITICAL: Voice Double Billing Warning

> **WARNING: You can be charged for STT (speech-to-text) twice on the same call if misconfigured.**

**We do not recommend using passive voice capture rules (`captureRules`) in your Configuration when using active TwiML.**

When you pass `conversationConfiguration` or `conversationId` in your TwiML:
- `<ConversationRelay conversationConfiguration="CONFIG_ID">` — Active TwiML mode
- `<ConversationRelay conversationId="CONVERSATION_ID">` — Active TwiML mode  
- `<Transcription conversationConfiguration="CONFIG_ID">` — Active TwiML mode
- `<Transcription conversationId="CONVERSATION_ID">` — Active TwiML mode

You are using **active ingestion**. Your voice is already being captured and transcribed.

**What causes double billing:**
- Passive voice capture rules use Real-Time Transcription (RTT) under the hood
- ConversationRelay/Transcription use their own STT engines
- If both are active on the same call = **you pay for BOTH STT engines**

**Correct configuration for active voice (TwiML):**
```json
{
  "channelSettings": {
    "VOICE": {
      "statusTimeouts": null  // ✅ Define channel settings
      // ❌ NO captureRules — omit this field entirely
    }
  }
}
```

**When to use passive voice capture rules:**
- Human agent calls WITHOUT ConversationRelay or Transcription TwiML
- You want automatic capture with no TwiML changes

**When to use active voice (TwiML parameters):**
- AI voice agents with ConversationRelay
- Adding transcription to existing API-created conversations
- Any scenario where you're already passing conversation parameters in TwiML

## Decision Frameworks

### Conversation Grouping

The `conversationGroupingType` on your configuration controls how new traffic groups into conversations.

| Type | Behavior | When to use |
|------|----------|-------------|
| `GROUP_BY_PARTICIPANT_ADDRESSES_AND_CHANNEL_TYPE` | Separate conversations per channel. SMS and Voice between the same numbers create different conversations. | The default. Keeps channels separate. |
| `GROUP_BY_PARTICIPANT_ADDRESSES` | Same conversation across channels when participants share an address. | Omnichannel on the same addresses—customer can switch between SMS and Voice seamlessly. |
| `GROUP_BY_PROFILE` | Groups by customer profile. The same customer from different devices or channels goes to one conversation. | Preferred for production. Recommended when channels use different addresses (chat and voice). |

**Immutable after creation.** Choose before creating the Configuration. To change grouping, create a new Configuration.

### Supported Channels

Conversation Orchestrator supports voice, SMS, RCS, and WhatsApp channels. You can also bring Chat traffic in through the Conversations API (classic) bridge.

| Channel | Address Format | Example | Ingestion Modes |
|---------|---------------|---------|-----------------|
| Voice (PSTN) | E.164 phone number | `+15559876543` | Passive and active |
| Voice (CLIENT) | Client identity string | `agent-1` | Passive and active |
| Voice (PUBLIC_SIP) | SIP URI or E.164 phone number | `sip:user@example.com` | Passive and active |
| SMS | E.164 phone number | `+15551234567` | Passive and active |
| RCS | E.164 phone number | `+15551234567` | Passive and active |
| WhatsApp | E.164 phone number | `+15551234567` | Passive and active |
| Chat | Identity string | `user123` | Conversations API (classic) bridge only |

### Channel Configuration Details

**Voice:**
- Use `callType` metadata in passive capture rules to distinguish call types:
  - `PSTN` — Standard phone calls over the public network
  - `CLIENT` — In-app calls using Twilio Voice SDK
  - `PUBLIC_SIP` — Calls over a SIP interface
- When you save voice capture rules, Conversation Orchestrator automatically provisions call filtering and Real-Time Transcription
- Each TTS fragment is a separate communication (3-5 per agent response)
- Voice communications have `content.type` of `TRANSCRIPTION`
- **Warning**: For dynamic or numerous client identities, use active TwiML instead of passive capture rules. Don't use wildcard identities with `CLIENT` call type.

**SMS:**
- Bidirectional capture rules needed (from: phone, to: * AND from: *, to: phone)
- Communications have `content.type` of `TEXT`
- Includes `deliveryStatus` in recipients array
- Recommended timeouts: `inactive: 10, closed: 60`

**RCS:**
- Same pattern as SMS
- Text body captured; media attachments are not added to conversations
- Recommended timeouts: `inactive: 10, closed: 60`

**WhatsApp:**
- E.164 format addresses (with or without `whatsapp:` prefix)
- Text and template messages supported
- Media attachments on inbound/outbound messages are not added to conversations
- Recommended timeouts: `inactive: 10, closed: 60`

**Chat (via Conversations API (classic)):**
- Only available through Conversations API (classic) bridge
- Uses customer-defined identity strings
- Configure `conversationsV1Bridge.serviceId` on Configuration
- Classic `ConversationSid` carried on address as `channelId`
- Recommended timeouts: `inactive: 15, closed: 60`

## Integration Patterns

Code samples use raw `fetch()` for clarity. All Conversation Orchestrator APIs use Basic Auth — see `twilio-iam-auth-setup`.

### Authentication Helper

```javascript
const CONVERSATIONS_V2_BASE = 'https://conversations.twilio.com/v2';

function getAuthHeaders() {
  const credentials = Buffer.from(
    `${process.env.TWILIO_ACCOUNT_SID}:${process.env.TWILIO_AUTH_TOKEN}`
  ).toString('base64');
  return {
    'Authorization': `Basic ${credentials}`,
    'Content-Type': 'application/json',
  };
}
```

### Create a Configuration

```javascript
const configResponse = await fetch(
  `${CONVERSATIONS_V2_BASE}/ControlPlane/Configurations`,
  {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      displayName: 'my-app-config',
      description: 'Production conversation config',
      conversationGroupingType: 'GROUP_BY_PROFILE',
      memoryStoreId: 'mem_store_...', // Required — create via Memory API first
      memoryExtractionEnabled: true,
      channelSettings: {
        SMS: {
          captureRules: [
            { from: '+15551234567', to: '*', metadata: {} },
            { from: '*', to: '+15551234567', metadata: {} },
          ],
          statusTimeouts: { inactive: 10, closed: 60 },
        },
        VOICE: {
          captureRules: [
            { from: '*', to: '+15551234567', metadata: {} },
          ],
        },
      },
    }),
  }
);
// May return 202 without config ID — poll GET /ControlPlane/Configurations to find by displayName
```

```python
import os, requests

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone = os.environ["TWILIO_PHONE_NUMBER"]

config = requests.post(
    "https://conversations.twilio.com/v2/ControlPlane/Configurations",
    auth=(account_sid, auth_token),
    json={
        "displayName": "my-app-config",
        "description": "Production conversation config",
        "conversationGroupingType": "GROUP_BY_PROFILE",
        "memoryStoreId": "mem_store_...",
        "memoryExtractionEnabled": True,
        "channelSettings": {
            "SMS": {
                "captureRules": [
                    {"from": twilio_phone, "to": "*", "metadata": {}},
                    {"from": "*", "to": twilio_phone, "metadata": {}}
                ],
                "statusTimeouts": {"inactive": 10, "closed": 60}
            },
            "VOICE": {
                "captureRules": [
                    {"from": "*", "to": twilio_phone, "metadata": {}}
                ]
            }
        }
    }
).json()
```

### Update a Configuration (PUT — Full Replacement)

```javascript
// Step 1: Fetch current config (ALWAYS re-fetch before updating)
const current = await fetch(
  `${CONVERSATIONS_V2_BASE}/ControlPlane/Configurations/${configId}`,
  { headers: getAuthHeaders() }
).then(r => r.json());

// Step 2: Modify the field you need
current.channelSettings.VOICE.captureRules.push(
  { from: '*', to: '+15551234567', metadata: { callType: 'CLIENT' } }
);

// Step 3: PUT the complete object back
await fetch(
  `${CONVERSATIONS_V2_BASE}/ControlPlane/Configurations/${configId}`,
  {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(current),
  }
);
```

```python
# Fetch current config
current = requests.get(
    f"https://conversations.twilio.com/v2/ControlPlane/Configurations/{config_id}",
    auth=(account_sid, auth_token)
).json()

# Modify and PUT the whole thing back
current["channelSettings"]["VOICE"]["captureRules"].append(
    {"from": "*", "to": twilio_phone, "metadata": {"callType": "CLIENT"}}
)

requests.put(
    f"https://conversations.twilio.com/v2/ControlPlane/Configurations/{config_id}",
    auth=(account_sid, auth_token),
    json=current
)
```

### Link Intelligence Configuration

```javascript
// Fetch current config, add Intelligence, PUT back
const current = await fetch(
  `${CONVERSATIONS_V2_BASE}/ControlPlane/Configurations/${configId}`,
  { headers: getAuthHeaders() }
).then(r => r.json());

current.intelligenceConfigurationIds = [intelligenceConfigId];

await fetch(
  `${CONVERSATIONS_V2_BASE}/ControlPlane/Configurations/${configId}`,
  {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(current),
  }
);
```

### Read Conversations and Communications

```javascript
// List active conversations
const conversations = await fetch(
  `${CONVERSATIONS_V2_BASE}/Conversations?Status=ACTIVE&PageSize=10`,
  { headers: getAuthHeaders() }
).then(r => r.json());

for (const conv of conversations.conversations ?? []) {
  // Note: List view has minimal data. For full details, fetch individual conversation
  console.log(`Conversation: ${conv.id}, Created: ${conv.createdAt || 'N/A'}`);
  
  // List communications (messages + voice utterances)
  const comms = await fetch(
    `${CONVERSATIONS_V2_BASE}/Conversations/${conv.id}/Communications`,
    { headers: getAuthHeaders() }
  ).then(r => r.json());

  for (const comm of comms.communications ?? []) {
    // Use optional chaining - channel and body may be undefined in list view
    console.log(`[${comm.channel ?? 'N/A'}] ${comm.body ?? 'N/A'}`);
  }
}
```

```python
conversations = requests.get(
    "https://conversations.twilio.com/v2/Conversations",
    auth=(account_sid, auth_token),
    params={"Status": "ACTIVE", "PageSize": 10}
).json()

for conv in conversations.get("conversations", []):
    conv_id = conv["id"]
    # Note: List view has minimal data. Use .get() for defensive access
    print(f"Conversation: {conv_id}, Created: {conv.get('createdAt', 'N/A')}")
    
    comms = requests.get(
        f"https://conversations.twilio.com/v2/Conversations/{conv_id}/Communications",
        auth=(account_sid, auth_token)
    ).json()

    for comm in comms.get("communications", []):
        # Use .get() - channel and body may be missing in list view
        print(f"  [{comm.get('channel', 'N/A')}] {comm.get('body', 'N/A')}")
```

### Close a Conversation

Closing triggers Memory extraction (if enabled) and CONVERSATION_END Intelligence operators.

```javascript
await fetch(
  `${CONVERSATIONS_V2_BASE}/Conversations/${convId}`,
  {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status: 'CLOSED' }),
  }
);
```

```python
requests.patch(
    f"https://conversations.twilio.com/v2/Conversations/{conv_id}",
    auth=(account_sid, auth_token),
    json={"status": "CLOSED"}
)
```

### Voice Integration Patterns

**Active TwiML (recommended for AI voice agents):** Pass `conversationConfiguration` on `<ConversationRelay>` to create a new conversation. Do NOT add passive VOICE `captureRules` — this avoids double STT billing. See the [Voice Double Billing Warning](#️-critical-voice-double-billing-warning) section above.

```xml
<Response>
  <Connect>
    <ConversationRelay
      url="wss://your-relay/voice"
      conversationConfiguration="CONFIG_ID_HERE"
      ttsProvider="ElevenLabs"
      voice="your-voice-id"
    />
  </Connect>
</Response>
```

Still define VOICE in `channelSettings` for lifecycle/timeouts — just omit `captureRules`:
```json
{
  "channelSettings": {
    "VOICE": {
      "statusTimeouts": null
    }
  }
}
```

**Attach voice to an existing conversation (Real-Time Transcription):** Use `<Transcription>` with `conversationId` to add a voice call's transcription to a conversation you created via API:

```xml
<Response>
  <Start>
    <Transcription conversationId="CONVERSATION_ID"/>
  </Start>
  <Say>Welcome to support. How can I help you today?</Say>
</Response>
```

**Passive voice capture (human agent calls):** Use VOICE `captureRules` to automatically capture calls without TwiML changes. Appropriate for human agent scenarios where ConversationRelay is not used:
```json
{
  "VOICE": {
    "captureRules": [
      { "from": "*", "to": "+15551234567", "metadata": {} }
    ]
  }
}
```

> **Warning:** Do NOT combine passive VOICE capture rules with active TwiML voice. See the [Voice Double Billing Warning](#️-critical-voice-double-billing-warning) section above.

## Gotchas

### Setup

1. **Memory Store is required.** You cannot create a Configuration without a `memoryStoreId`. Create the Memory Store first via `twilio-customer-memory`.

2. **JSON-only API.** All Conversation Orchestrator endpoints require `Content-Type: application/json`. Form-encoded bodies are rejected. This matches Intelligence v3 but differs from most Twilio APIs.

3. **Async creation.** POST to `/ControlPlane/Configurations` returns 202 with an operation. Poll the operation's `statusUrl` until `status` is `COMPLETED`, then retrieve the configuration ID from the operation result.

### Configuration

4. **PUT replaces everything.** The most common bug: fetching a config, modifying one field, PUTting back — but forgetting to include `channelSettings` or `memoryStoreId`. The API accepts the PUT and silently removes the omitted fields. Always re-fetch, modify, PUT.

5. **Grouping type is immutable.** `conversationGroupingType` cannot be changed after creation. To switch grouping, create a new Configuration and close conversations on the old one.

6. **10 Configuration limit per account.** Hard limit at GA (up to 100 capture rules per channel per config). Delete unused Configurations to make room. For customers with large phone number portfolios, partition numbers across multiple Configurations.

7. **CLIENT voice capture is opt-in.** Browser-originated calls via the Twilio Client SDK are not captured by default VOICE rules. You need a separate capture rule with `"metadata": {"callType": "CLIENT"}`. SIP calls similarly need `{"callType": "PUBLIC_SIP"}`. PSTN is the only type captured by default.

8. **`conversationConfiguration` (no "Id" suffix) is the correct TwiML attribute name.** The attribute on `<ConversationRelay>` and `<Transcription>` is `conversationConfiguration`, NOT `conversationConfigurationId`. The incorrect name is silently ignored (unrecognized TwiML attributes produce no error), resulting in no conversation being created.

### Runtime

9. **Timeout precedence across channels.** If a customer is on a voice call and sends an SMS, both channels are active in the same Conversation (with `GROUP_BY_PROFILE`). When the voice call ends, the SMS channel's timeout still governs — the Conversation won't close until the SMS timeout expires. Channel close events are proposals, not commands.

10. **Config versioning pins at creation.** Intelligence rules and capture rules are pinned to the Configuration version at conversation creation time. Upgrading Intelligence (adding operators, changing rules) doesn't affect existing conversations. Close active conversations to pick up the new version.

11. **ConversationRelay TTS fragmentation.** ConversationRelay writes one Communication per TTS fragment, not per complete utterance. A single agent response may produce 3-5 Communications. Intelligence operators fire per Communication, so operator cost scales with fragment count.

12. **Overly broad wildcard VOICE rules match multiple call types.** A rule `{"from": "*", "to": "*", "metadata": {"callType": "PSTN"}}` will match all PSTN calls in your account, not just those to/from specific numbers. If you also have CLIENT capture rules, each call could match multiple rules, leading to unexpected conversation grouping. Always use specific `from` or `to` addresses to limit rule scope.

13. **Active TwiML voice and passive capture rules cause double STT billing.** See the [Voice Double Billing Warning](#️-critical-voice-double-billing-warning) section for full details. Do not use passive VOICE `captureRules` when passing conversation parameters in TwiML.

### Observability

14. **Silent Memory linkage failure.** If `memoryStoreId` points to a deleted or invalid store, capture still works but identity resolution and extraction silently fail. No error is returned. See `twilio-debugging-observability`.

15. **No participant type filtering for Intelligence.** Operators fire on ALL Communications — customer messages AND agent responses. There is no config-level filter. Use the operator prompt to specify which participant to analyze.

16. **Memory extraction is opt-in and fires on INACTIVE and/or CLOSED.** Extraction does not run automatically — it must be enabled. It can be configured to fire on the INACTIVE transition, the CLOSED transition, or both. It does NOT fire while a conversation is ACTIVE. For mid-conversation Memory writes, post directly to the Observations endpoint via `twilio-customer-memory`.

17. **List endpoints return partial data.** When listing Conversations or Communications via GET `/Conversations` or `/Conversations/{id}/Communications`, response objects are missing fields that are present when fetching individual resources. Missing fields include `dateCreated` (list) vs `createdAt` (single GET), `channels`, `body`, and `channel`. Always use defensive field access (`conv?.createdAt` or `conv.get('createdAt')`) and fetch individual resources if you need complete data. Example:
```javascript
// List returns partial data
const list = await fetch(`${BASE}/Conversations?PageSize=10`);
for (const conv of list.conversations) {
  console.log(conv.dateCreated); // undefined
  console.log(conv.createdAt);   // also undefined in list view
  
  // Fetch full details if needed
  const full = await fetch(`${BASE}/Conversations/${conv.id}`);
  console.log(full.createdAt);   // ✅ present (note: 'createdAt' not 'dateCreated')
}
```

## Related Resources

- [Conversation Intelligence Skill](../twilio-conversation-intelligence/SKILL.md) — Intelligence Configuration, Language Operators, real-time and post-conversation analysis
- [Customer Memory Skill](../twilio-customer-memory/SKILL.md) — Memory Store, profiles, traits, observations, Recall
- [ConversationRelay Skill](../twilio-voice-conversation-relay/SKILL.md) — Voice AI agent setup with WebSocket streaming
- [Agent Connect Skill](../twilio-agent-connect/SKILL.md) — AI-to-human escalation via TAC SDK
- [Debugging Skill](../twilio-debugging-observability/SKILL.md) — Error triage, Event Streams, linkage chain verification
