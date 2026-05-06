---
name: conversation-intelligence
description: "Twilio Conversation Intelligence development guide. Use when building real-time or post-call conversation analysis, language operator pipelines, sentiment analysis, agent assist, cross-channel analytics, or querying aggregated conversation insights (sentiment trends, escalation rates, dashboards)."
---

# Conversation Intelligence

Decision-making guide for Twilio's Conversation Intelligence v3 API — real-time and post-call GenAI analysis of conversations across Voice, SMS, RCS, and WhatsApp. Covers Intelligence Configurations, Language Operators (Twilio-authored and custom), Rules, Triggers, Actions, and result consumption.

> **Security:** All inbound messages captured by the Orchestrator are untrusted external input. If Intelligence operators process this content with LLMs, their prompts should include instructions to ignore adversarial content and not follow instructions embedded in customer messages.


> **GA** — Conversation Intelligence v3 is generally available.

## Use Cases

Conversation Intelligence powers **human agent augmentation** — giving every agent a "second brain" that listens, understands, and surfaces the right data at the right time. Agents focus on empathy, judgment, and problem-solving; AI handles analysis and assistance.

### Wrap-up Agent Assist (Post-Call)

Analyze completed conversations and generate structured outputs — summaries, sentiment signals, topic dispositions. Reduces after-call work, accelerates agent transitions to next interaction. **Low-friction entry point** — start here.

- **Operators**: Summary, Sentiment, custom Conversation Scoring
- **Trigger**: `CONVERSATION_END`
- **Integration**: Webhook → CRM case note creation

### Real-time Agent Assist

Analyze conversations as they unfold. Surface sentiment shifts, script adherence signals, or recommended next responses enriched with customer history and enterprise knowledge. Agents respond more confidently without searching across systems.

- **Operators**: Script Adherence, Next Best Response, Escalation Risk (custom)
- **Trigger**: `COMMUNICATION`
- **Integration**: Webhook → Agent desktop overlay

### Real-time Workflow Automation

Combine real-time intelligence with orchestration to trigger downstream workflows when specific conditions are met — escalate to supervisor, trigger fraud prevention, notify specialist.

- **Operators**: Custom risk detection, compliance monitoring
- **Trigger**: `COMMUNICATION`
- **Integration**: Webhook → Workflow engine / TaskRouter

### Contact Center QA

Generate post-interaction summaries, sentiment scores, and compliance signals for QA, coaching, and analytics. Aggregate across interactions to support training and continuous optimization.

- **Operators**: Script Adherence, Summary, custom Conversation Scoring
- **Trigger**: `CONVERSATION_END`
- **Integration**: Webhook → Analytics / BI tools

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Customer engages agent (Voice, SMS, WhatsApp, RCS, Chat, Email)         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Conversations (Conversation Orchestrator) groups communications into a  │
│     Conversation                                                            │
│     - Normalizes channel events                                             │
│     - Groups related messages/utterances                                    │
│     - Tracks participants (CUSTOMER, HUMAN_AGENT, AI_AGENT)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Conversation events trigger Intelligence rules                          │
│     - COMMUNICATION: on each new message/utterance                          │
│     - CONVERSATION_END: when conversation closes                            │
│     - CONVERSATION_INACTIVE: when conversation goes idle                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Language Operators analyze the conversation                             │
│     - Twilio-authored: Sentiment, Summary, NBR, Script Adherence            │
│     - Custom: domain-specific analysis with your prompts                    │
│     - Context: enriched with Customer Memory + Enterprise Knowledge         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Results delivered via webhook + REST API                                │
│     - Real-time: Agent desktop, workflow triggers                           │
│     - Post-call: CRM notes, QA systems, analytics                           │
│     - Aggregated: Conversational Insights for cross-conversation analysis   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key insight**: Real-time and post-conversation intelligence use the **same underlying model**. Start with low-friction post-call summaries, then progressively introduce real-time assist using the same components.

## Scope

### CAN

- Analyze conversations in real-time (per-message) and post-conversation (at close/inactive) via Language Operators
- Use 4 Twilio-authored operators: Sentiment, Summary, Next Best Response, Script Adherence
- Create custom Language Operators with natural language prompts and structured output (TEXT, JSON, CLASSIFICATION) — `EXTRACTION` is a read-only format returned by some Twilio-authored operators; it cannot be set on custom operators you create
- Define up to 5 rules per Intelligence Configuration, each with 1-5 operators (minimum 1 required), 0 or 1 trigger, and 0-2 webhook actions
- Throttle real-time triggers with `count` parameter (run every N communications, min 1, max 20)
- Deliver results via webhook (POST) and query historically via REST API
- Track conversations across SMS, Voice, RCS, WhatsApp, Chat, and Email channels via Conversation Orchestrator (Conversations v2) integration
- Create custom operators with parameters (`{{parameters.name}}` syntax), including knowledge base references (`KNOWLEDGE_BASE_AND_SOURCE_IDS` type — value format: `knowledge_base_id:knowledge_source_id`)
- Enrich operators with Customer Memory (`context.memory.enabled: true`) and Enterprise Knowledge (`context.knowledge.bases: [...]`) at the rule or operator level
- Add `trainingExamples` (input/output pairs) to custom operators to improve accuracy
- Pin a specific operator version in a rule via `operators[].version`; omit to use latest
- Query OperatorResults filtered by `intelligenceConfigurationId`, `conversationId`, or `operatorId`
- Query operator versions and fetch specific version details
- Delete Intelligence Configurations, custom Operators, and individual OperatorResults via REST API
- Use ETag/If-Match headers for optimistic locking on **Operator** updates (returns 412 on mismatch) — ETag is not supported on Configuration updates
- Filter Conversations by `status`, `channels`, `createdAtBefore`/`createdAtAfter`, `channelId`, `intelligenceConfigurationIds`, `operatorIds`
- Authenticate with both Account SID/Auth Token and API Key/Secret
- Define rules without a trigger (trigger is optional per spec; runs on all events if omitted)

### CANNOT

- **JSON-only API** — All v3 endpoints require `Content-Type: application/json`. Form-encoded bodies return HTTP 415 with error 20422.
- **No standalone operation** — v3 requires Conversation Orchestrator (Conversations v2) for conversation capture. You cannot feed raw messages or recordings into v3 directly.
- **No per-message sentiment** — Sentiment is conversation-level, accumulating across all messages. A conversation with one positive and one negative message returns "mixed", not separate results per message.
- **No deleting Twilio-authored operators** — DELETE returns 404 "Operator not found" for Twilio-authored operators, not 403. They are not treated as "yours" to delete.
- **No editing Twilio-authored operator prompts** — Twilio-authored operators have `prompt: null` when retrieved via GET. The prompt is hidden and not configurable.
- **No more than 2 actions per rule** — The API enforces `size must be between 0 and 2` for actions.
- **No more than 5 rules per configuration** — API enforces `size must be between 0 and 5`.
- **No PCI or HIPAA compliance** — Conversation Intelligence v3 is not PCI compliant or HIPAA Eligible. Do not use for payment data or protected health information.
- **No GET/PUT/DELETE on v3 Conversations** — The Conversations endpoint is read-only (GET list, GET by ID). Conversation lifecycle is controlled by Conversation Orchestrator, not by the Intelligence API.
- **No unsupported JSON schema features** — The following are rejected in `outputSchema`: `minLength`/`maxLength` (strings), `patternProperties` (objects), `uniqueItems` (arrays). Use basic types only.
- **Cannot use PUT to update a live configuration** — PUT creates an inactive version with no activation API. Operators silently stop returning results. Workaround: DELETE the configuration and POST to recreate it.
- **Silent Memory Store linkage failures** — If `memoryStoreId` points to a deleted or invalid store, capture still works but identity resolution and extraction silently fail with no error. Implement periodic health checks to verify Memory Store linkage is functioning.

## Quick Decision

| Need | Use | Why |
|------|-----|-----|
| Real-time agent assist during live calls/chats | v3 + COMMUNICATION trigger + Next Best Response operator | Real-time webhook delivery per utterance |
| Post-call QA scoring | v3 + CONVERSATION_END trigger + Script Adherence operator | Runs once at conversation close, returns detailed score |
| Conversation sentiment tracking | v3 + Sentiment operator (Twilio-authored) | Conversation-level classification: positive/negative/neutral/mixed |
| Post-call recording transcription + analysis | v2 Voice Intelligence (existing) | v3 does not ingest recordings directly — v2 pipeline handles recording→transcript→operators |
| Custom domain-specific analysis | v3 + Custom operator with JSON output | Define prompt, parameters, structured output schema |
| Cross-channel conversation history | Conversations v2 (Conversation Orchestrator) alone | v3 adds analysis on top; Conversation Orchestrator handles capture and history |
| Simple keyword extraction | v3 + Custom operator (EXTRACTION format) | Structured extraction with custom prompt |

## Decision Frameworks

### v2 (Voice Intelligence) vs v3 (Conversation Intelligence)

| Dimension | v2 (Voice Intelligence) | v3 (Conversation Intelligence) |
|-----------|------------------------|-----------------------------------|
| Input source | Recording SIDs (audio) | Conversation Orchestrator conversations (text/transcriptions) |
| Channels | Voice only | SMS, Voice, RCS, WhatsApp, Chat, Email |
| Operator management | Console only (attach to Intelligence Service) | REST API (full CRUD on custom operators) |
| Trigger model | Post-transcription (async) | Real-time (per-message) or post-conversation |
| Result delivery | Webhook (`voice_intelligence_transcript_available`) | Webhook (per-rule action) + REST query |
| SDK support | `client.intelligence.v2.transcripts` | Twilio Node.js SDK supported |
| SID prefix | `GA` (service), `GT` (transcript), `LY` (operator) | `intelligence_configuration_*`, `intelligence_operator_*` |
| Status | GA | GA |
| Coexistence | Works alongside v3 | Works alongside v2 |

Use v2 when: You need post-call transcription from recordings, or need GA stability.
Use v3 when: You need real-time analysis, cross-channel support, or API-managed custom operators.

### Real-Time vs Post-Conversation

| Factor | COMMUNICATION trigger | CONVERSATION_END trigger | CONVERSATION_INACTIVE trigger |
|--------|----------------------|-------------------------|-------------------------------|
| When it fires | On each new message/utterance | When conversation closes | When conversation goes idle |
| Latency | Near real-time | Seconds after close | After inactive timeout |
| Use cases | Agent assist, escalation detection, live compliance | QA scoring, summaries, CRM updates | Idle conversation follow-up |
| Operator context | Accumulating — sees all messages so far | Complete conversation | Messages up to inactivity point |
| Throttling | `count` parameter (every N messages) | N/A | N/A |
| Cost implication | Runs per message (more executions) | Runs once per conversation | Runs once per inactivity event |

### Operator Version Lifecycle

| Status | Behavior | When |
|--------|----------|------|
| `PREVIEW` | Normal execution, restricted visibility | Internal/testing versions |
| `ACTIVE` | Normal execution, full availability | Production-ready versions |
| `DEPRECATED` | Executes with Warn event via Watch | Migration window — update to newer version |
| `RETIRED` | Hard failure, Error logged in Watch | Must update Intelligence Configuration manually |

### Custom Operator Output Formats

| Format | Use When | Result Shape | Schema Support |
|--------|----------|-------------|----------------|
| TEXT | Free-form analysis, summaries, translations | `{"text": "..."}` | Auto-generated (not customizable) |
| JSON | Structured extraction with custom fields | User-defined via `outputSchema` | Full JSON Schema (max 100 props, 10 nesting levels, 1000 enum values max) |
| CLASSIFICATION | Category labeling (sentiment, intent, topic) | `{"label": "..."}` | Auto-generated |
| EXTRACTION | Returned by some Twilio-authored operators only — cannot be set on custom operators | `{"entities": [{"text": "...", "label": "..."}]}` | N/A (read-only) |

### Twilio-Authored Operator Reference

Ready-to-use operators maintained by Twilio. Use these IDs directly in rules — no custom prompt required.

| Operator | ID | Best Trigger | Use Case |
|----------|-----|--------------|----------|
| **Sentiment** | `intelligence_operator_01kcrvw16kfa88qvgrfmr7y151` | COMMUNICATION | Real-time sentiment tracking (positive/negative/neutral/mixed) |
| **Summary** | `intelligence_operator_01kcv35pnkeysaf6z6cqtbpegn` | CONVERSATION_END | Post-call conversation summary |
| **Next Best Response** | `intelligence_operator_01kea27sy7ffsafmtsfp17nzx4` | COMMUNICATION | Real-time agent assist with suggested responses |
| **Script Adherence** | `intelligence_operator_01kf34tcyefpyb1t4m0nbd8rxg` | CONVERSATION_END | QA scoring for script compliance |

**Note**: Twilio-authored operators have `author: "TWILIO"` and `prompt: null` when retrieved via GET. Prompts are hidden and not configurable. Use custom operators if you need control over the prompt.

## Integration Patterns

Code samples use raw `fetch()` for clarity, but the Twilio Node.js SDK is also supported for v3.

### Authentication Helper

```javascript
const INTELLIGENCE_V3_BASE = 'https://intelligence.twilio.com/v3';

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

### Create Intelligence Configuration with Rules

```javascript
// Step 1: Create configuration (empty rules initially)
const configResponse = await fetch(
  `${INTELLIGENCE_V3_BASE}/ControlPlane/Configurations`,
  {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      displayName: 'Customer Support Analytics',
      description: 'Real-time sentiment + post-call summary',
      rules: [],
    }),
  }
);
const config = await configResponse.json();
// config.id = "intelligence_configuration_..."

// Step 2: Add rules via PUT (replaces all rules)
const updateResponse = await fetch(
  `${INTELLIGENCE_V3_BASE}/ControlPlane/Configurations/${config.id}`,
  {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      displayName: 'Customer Support Analytics',
      rules: [
        {
          operators: [
            { id: 'intelligence_operator_01kcrvw16kfa88qvgrfmr7y151' }, // Sentiment
          ],
          triggers: [{ on: 'COMMUNICATION' }],
          actions: [
            { type: 'WEBHOOK', method: 'POST', url: 'https://your-app.com/realtime-results' },
          ],
        },
        {
          operators: [
            { id: 'intelligence_operator_01kcv35pnkeysaf6z6cqtbpegn' }, // Summary
          ],
          triggers: [{ on: 'CONVERSATION_END' }],
          actions: [
            { type: 'WEBHOOK', method: 'POST', url: 'https://your-app.com/post-call-results' },
          ],
        },
      ],
    }),
  }
);
const updatedConfig = await updateResponse.json();
// updatedConfig.version = 2 (auto-incremented)
```

### Link to Conversation Orchestrator Conversation Configuration

```javascript
// Intelligence config must be linked to a Conversation Orchestrator conversation config
// See conversation-orchestrator skill for full Conversation Orchestrator setup
const convConfigResponse = await fetch(
  'https://conversations.twilio.com/v2/ControlPlane/Configurations',
  {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      displayName: 'Support Config',
      memoryStoreId: 'mem_store_...',  // Required — create via Memory API first
      conversationGroupingType: 'GROUP_BY_PARTICIPANT_ADDRESSES',
      intelligenceConfigurationIds: [config.id],
      channelSettings: {
        SMS: {
          statusTimeouts: { inactive: 5, closed: 10 },
          captureRules: [{ from: '*', to: '+1XXXXXXXXXX', metadata: {} }],
        },
      },
    }),
  }
);
```

### Consume Operator Results

```javascript
// Query all results for an intelligence configuration
const resultsResponse = await fetch(
  `${INTELLIGENCE_V3_BASE}/OperatorResults?intelligenceConfigurationId=${config.id}`,
  { headers: getAuthHeaders() }
);
const results = await resultsResponse.json();

for (const operatorResult of results.items) {
  console.log(`Operator: ${operatorResult.operator.id}`);
  console.log(`Format: ${operatorResult.outputFormat}`);
  console.log(`Payload: ${JSON.stringify(operatorResult.result)}`); // e.g. { text: "..." } or { label: "..." }
  console.log(`Conversation: ${operatorResult.conversationId}`);
  console.log(`Trigger: ${operatorResult.executionDetails.trigger.on}`);
  // Context that was actually used at runtime (single source of truth):
  console.log(`Memory profile: ${operatorResult.executionDetails.resolvedContext?.memory?.profileId}`);
  console.log(`Knowledge sources: ${JSON.stringify(operatorResult.executionDetails.resolvedContext?.knowledge?.sources)}`);
  // Cost/perf metadata:
  console.log(`Model: ${operatorResult.metadata.system.resolvedModel}, latencyMs: ${operatorResult.metadata.system.latencyMs}`);
}
```

### Paginate Through Results

All list endpoints (`/OperatorResults`, `/Conversations`, `/Operators`, `/Configurations`) use cursor-based pagination. Default page size is 50; maximum is 1000.

```javascript
async function* getAllOperatorResults(configId) {
  let pageToken = undefined;
  do {
    const url = new URL(`${INTELLIGENCE_V3_BASE}/OperatorResults`);
    url.searchParams.set('intelligenceConfigurationId', configId);
    url.searchParams.set('pageSize', '1000');
    if (pageToken) url.searchParams.set('pageToken', pageToken);

    const response = await fetch(url, { headers: getAuthHeaders() });
    const data = await response.json();

    yield* data.items;
    pageToken = data.meta?.nextToken; // null/undefined when no more pages
  } while (pageToken);
}

// Usage:
for await (const result of getAllOperatorResults(config.id)) {
  console.log(result.operator.id, result.result);
}
```

### Enable Customer Memory and Enterprise Knowledge on a Rule

```javascript
// Context is configured at the rule level (not the operator level)
rules: [
  {
    operators: [{ id: 'intelligence_operator_01kea27sy7ffsafmtsfp17nzx4' }], // NBR
    triggers: [{ on: 'COMMUNICATION' }],
    actions: [{ type: 'WEBHOOK', method: 'POST', url: 'https://your-app.com/nbr' }],
    context: {
      memory: { enabled: true },          // inject customer profile from Memory Store
      knowledge: {
        bases: ['knowledge_base_id_here'], // inject enterprise KB articles
      },
    },
  },
]
```

### Create a Custom Operator with Training Examples and Parameters

```javascript
const operatorResponse = await fetch(
  `${INTELLIGENCE_V3_BASE}/ControlPlane/Operators`,
  {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      displayName: 'Escalation Risk Detector',
      prompt: `Analyze this conversation between a customer and agent.
Product context: {{parameters.productName}}
Classify escalation risk as LOW, MEDIUM, or HIGH based on customer frustration signals.`,
      outputFormat: 'CLASSIFICATION',
      parameters: {
        productName: { type: 'STRING', required: true, description: 'Product line being discussed' },
        // KNOWLEDGE_BASE_AND_SOURCE_IDS parameters are passed as "kb_id:source_id" at rule time
        knowledgeContext: { type: 'KNOWLEDGE_BASE_AND_SOURCE_IDS', required: false },
      },
      trainingExamples: [
        {
          input: 'Customer: This is the third time I have called about this issue',
          output: 'HIGH',
        },
        {
          input: 'Customer: Thanks, I think that might work',
          output: 'LOW',
        },
      ],
    }),
  }
);
const operator = await operatorResponse.json();
// Pin this operator to a specific version in your rule:
// operators: [{ id: operator.id, version: operator.version }]
```

## Gotchas

### Setup

1. **Memory Store is required for Conversation Orchestrator**: You cannot create a Conversations v2 Configuration without a `memoryStoreId`. The Memory API returns `"memoryStoreId: must not be null"` (error 20001). Create the Memory Store first via `POST memory.twilio.com/v1/ControlPlane/Stores`.

2. **JSON-only API**: All v3 endpoints require `Content-Type: application/json`. Form-encoded bodies return HTTP 415 with error 20422 ("does not support this payload format"). This matches Conversation Orchestrator but differs from most Twilio APIs.

3. **v2 and v3 coexist independently**: Creating v3 configurations does not affect v2 Intelligence Services (`GA*` SIDs). Both are accessible on the same account simultaneously. They share the `intelligence.twilio.com` host but use different URL paths (`/v2/Services` vs `/v3/ControlPlane/Configurations`).

### Configuration

4. **PUT creates an inactive version — operators stop returning results**: When you PUT to update an Intelligence Configuration, the new version is created in an **inactive state**. There is no activation API to make it live. Your operators will silently stop producing results. **Workaround: DELETE the configuration and POST to recreate it** with the updated rules/operators. This is the only reliable way to update a live configuration.

5. **PUT replaces all rules**: Updating a configuration replaces the entire `rules` array. There is no PATCH or per-rule update. Always include all rules in the PUT body, not just the changed one.

6. **Config version auto-increments**: Each PUT bumps the `version` field. Conversation Orchestrator conversation configs use `version` for optimistic locking, but Intelligence configs accept PUT without version checks.

7. **Rules get their own IDs**: When rules are created via PUT, each gets an auto-generated ID (`intelligence_configurationrule_*`). These IDs appear in OperatorResult references but are not user-settable.

8. **Trigger count parameter throttles execution**: Setting `{"on":"COMMUNICATION","parameters":{"count":3}}` runs the operator every 3 messages instead of every message.

### Runtime

9. **Dual capture rules cause duplicate processing**: If both inbound (`from: *, to: +1XXX`) and outbound (`from: +1XXX, to: *`) capture rules match the same SMS, Conversation Orchestrator creates two Communications for one message, and Intelligence produces two OperatorResults. Use unidirectional capture rules unless you specifically want both.

10. **Twilio number is auto-typed HUMAN_AGENT**: In Conversation Orchestrator conversations, the Twilio number is automatically assigned `type: "HUMAN_AGENT"` and the external number gets `type: "CUSTOMER"` with automatic memory profile resolution (`mem_profile_*`).

11. **Sentiment accumulates across messages**: The Sentiment operator analyzes the full conversation context, not individual messages. After a positive message, sentiment was "positive". After adding a negative message to the same conversation, it became "mixed".

12. **Near real-time delivery for COMMUNICATION trigger**: Results are delivered via webhook shortly after each utterance — the full pipeline is Conversation Orchestrator capture → Intelligence trigger → Operator execution → webhook delivery.

13. **Custom operator TEXT output auto-wraps**: Custom operators with `outputFormat: "TEXT"` always return `{"text": "..."}` regardless of the prompt. The outputSchema is auto-generated and not customizable for TEXT format.

### Observability

14. **conversationConfigurationId returns "unused"**: The v3 Conversations endpoint returns `"conversationConfigurationId": "unused"` instead of the actual Conversation Orchestrator config ID. Use `intelligenceConfigurationIds` array instead for linking.

15. **No isTwilioAuthored field**: Twilio-authored operators are distinguished by `author: "TWILIO"`, custom operators by `author: "SELF"`. There is no boolean `isTwilioAuthored` field.

16. **Twilio-authored operator prompts are hidden**: GET on a Twilio-authored operator returns `prompt: null`. You cannot inspect or modify the system prompt. Custom operators return the full prompt.

17. **Two separate metadata sections**: OperatorResults carry both `metadata.system` and `executionDetails.resolvedContext` — they serve different purposes:
   - `metadata.system`: cost and performance — `resolvedModel` (LLM used), `latencyMs`, `inputCharacters`/`outputCharacters` (billing units), `inputTruncated`
   - `executionDetails.resolvedContext`: what context was actually injected at runtime — `memory` (`profileId`, `memoryStoreId`) and `knowledge` (`sources`: array of `{baseId, sourceId}`). This is the single source of truth for context resolution.

### Error Handling

18. **Error codes are consistent**: v3 uses Twilio standard error codes: `20001` (bad request/validation), `20404` (not found), `20422` (unsupported format), `70001` (operator validation). All include `userError: true` and descriptive messages.

19. **Invalid operator ID gives specific error**: Using a non-existent operator ID in a rule returns 400 with code `70001` and message identifying the exact invalid operator.

### JSON Schema

20. **All JSON schema fields are required by default — and Twilio auto-sets this**: Twilio automatically sets `additionalProperties: false` and marks all provided fields as required in `outputSchema`. Do not add `required` or `additionalProperties` yourself — Twilio overwrites any values you provide. The practical consequence: if the LLM cannot populate a field, the operator execution fails. Use union types for nullable fields: `"type": ["string", "null"]`.

21. **Nullable field pattern**: To make a field optional/nullable in JSON output, use array type union:
```json
{
  "outputSchema": {
    "type": "object",
    "properties": {
      "requiredField": { "type": "string" },
      "optionalField": { "type": ["string", "null"] }
    }
  }
}
```
This allows the operator to return `null` for fields where the LLM has insufficient context.

21. **Unsupported JSON schema features cause silent or hard failures**: The following JSON Schema features are NOT supported in `outputSchema` and will be rejected. Stick to `type`, `enum`, `properties`, `items`, `anyOf`, `$defs`/`$ref`.
   - Strings: `minLength`, `maxLength`
   - Objects: `patternProperties`, `unevaluatedProperties`, `propertyNames`, `minProperties`, `maxProperties`
   - Arrays: `unevaluatedItems`, `contains`, `minContains`, `maxContains`, `uniqueItems`

22. **`executionDetails.context` was removed**: Older docs and some live responses may show `executionDetails.context`. This field was removed in a breaking change. Use `executionDetails.resolvedContext` — it contains `memory` (profileId, memoryStoreId) and `knowledge` (array of baseId/sourceId pairs).

23. **Operator result query param is `intelligenceConfigurationId`** (not `intelligenceConfiguration`): The REST API filter parameter for listing OperatorResults by config is `intelligenceConfigurationId`. Using the shorter form returns unfiltered results.

24. **`KNOWLEDGE_BASE_AND_SOURCE_IDS` parameter values must use colon-separated format**: When passing a knowledge base parameter to an operator at rule time, the value must be formatted as `"knowledge_base_id:knowledge_source_id"`. Passing just the KB ID or using any other separator returns a validation error. Only plaintext KB sources are supported.

25. **`KNOWLEDGE_BASE_AND_SOURCE_IDS` parameters do not support `default`**: Unlike `STRING`, `INTEGER`, `NUMBER`, and `BOOLEAN` parameter types which all allow a `default` value, `KNOWLEDGE_BASE_AND_SOURCE_IDS` does not. Defining a `default` on a KB parameter will be ignored or rejected.

26. **Each rule requires at least 1 operator**: The `operators` array on a rule has `minItems: 1`. Submitting a rule with an empty operators array on create or update returns a 400 validation error.

27. **List endpoints are paginated — don't assume you got all results**: All list endpoints (`/OperatorResults`, `/Conversations`, `/Operators`, `/Configurations`) return a max of 50 items by default (max 1000 with `pageSize`). The response `meta.nextToken` is non-null when more pages exist. Always paginate when querying production data sets.

## Conversational Insights (Cross-Conversation Analytics)

Where the Intelligence API gives you per-conversation OperatorResults, the **Insights API v3** is the query layer for aggregating across thousands of conversations — grouping, filtering, and counting by dimensions like sentiment, channel, language, and operator output.

Base URL: `https://insights.twilio.com`

> **Public Beta** — Insights v3 is currently in public beta. The query schema is subject to change.

### When to Use Insights vs Intelligence REST API

| Goal | Use |
|------|-----|
| Get the result for a specific conversation | Intelligence API: `GET /v3/OperatorResults?conversationId=...` |
| Count conversations by sentiment over time | Insights API: query with `OperatorResult.Value` dimension |
| Find all conversations where agent went off-script | Insights API: filter on `OperatorResult.Value` |
| Build a sentiment trend dashboard | Insights API: group by `DateCreated` + `OperatorResults` |
| Discover available metrics and dimensions | Insights API: `GET /v3/InsightsDomains/Conversations/Metadata` |

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/v3/InsightsDomains/Conversations/Query` | Execute a semantic query, returns first page |
| `GET` | `/v3/InsightsDomains/Conversations/Query?pageToken=...` | Fetch subsequent pages |
| `GET` | `/v3/InsightsDomains/Conversations/Metadata` | Discover available cubes, measures, dimensions |

Same Basic Auth as Intelligence API. JSON-only (`Content-Type: application/json`).

### Query a Sentiment Distribution

```javascript
const INSIGHTS_BASE = 'https://insights.twilio.com';

const response = await fetch(
  `${INSIGHTS_BASE}/v3/InsightsDomains/Conversations/Query`,
  {
    method: 'POST',
    headers: getAuthHeaders(), // same helper as Intelligence API
    body: JSON.stringify({
      domain: 'Conversations',
      query: {
        measures: ['Conversation.Count'],
        dimensions: ['OperatorResults', 'Channels', 'DateCreated'],
        filters: [{
          op: 'AND',
          expressions: [
            { op: 'IN', field: 'OperatorResult.Value', values: ['positive', 'negative'] },
          ],
        }],
        orderBy: [{ field: 'OperatorResults.CreatedDate', direction: 'DESC' }],
      },
    }),
  }
);
const data = await response.json();
// data.items = [{ Id: 'conv1', OperatorResults: 'positive', Channels: ['voice'], ... }]
// data.meta.nextToken — use for next page (null if last page)
```

**Query fields:**

| Field | Description |
|-------|-------------|
| `query.measures` | What to aggregate — e.g. `"Conversation.Count"`, `"OperatorResult.Count"` |
| `query.dimensions` | What to group by — e.g. `"OperatorResults"`, `"Channels"`, `"Languages"`, `"DateCreated"` |
| `query.filters` | Nested filter tree with `op` + `expressions`. Filter ops: `AND`, `OR`, `EQ`, `NE`, `GT`, `LT`, `IN` |
| `query.orderBy` | Sort by field + `ASC`/`DESC` |

### Pagination

POST returns the first page. Subsequent pages use GET with `pageToken`. Stop when `meta.nextToken` is null.

```javascript
async function* queryAll(queryBody) {
  const first = await fetch(`${INSIGHTS_BASE}/v3/InsightsDomains/Conversations/Query`,
    { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(queryBody) }
  ).then(r => r.json());
  yield* first.items;

  let nextToken = first.meta?.nextToken;
  while (nextToken) {
    const page = await fetch(
      `${INSIGHTS_BASE}/v3/InsightsDomains/Conversations/Query?pageToken=${nextToken}`,
      { headers: getAuthHeaders() }
    ).then(r => r.json());
    yield* page.items;
    nextToken = page.meta?.nextToken;
  }
}
```

### Discover Available Dimensions and Measures

```javascript
const meta = await fetch(
  `${INSIGHTS_BASE}/v3/InsightsDomains/Conversations/Metadata`,
  { headers: getAuthHeaders() }
).then(r => r.json());

for (const cube of meta.cubes) {
  console.log('Measures:', cube.measures.map(m => m.name));
  console.log('Dimensions:', cube.dimensions.map(d => d.name));
}
```

Known dimensions: `DateCreated`, `OperatorResults`, `OperatorResult.Value`, `Channels`, `Languages`, `Conversation.AccountSid`

Known measures: `Conversation.Count`, `OperatorResult.Count`

### Insights CANNOT
- Return raw OperatorResult payloads — use Intelligence `GET /v3/OperatorResults` for that
- Write anything — read-only
- Query in real-time — data mart has indexing lag vs. the live Intelligence API
- Query domains other than `Conversations`

## Related Resources

- [Conversation Orchestrator Skill](../twilio-conversation-orchestrator/SKILL.md) — Conversation Orchestrator setup: Memory Store, Conversation Configuration, capture rules, participant types
- [Customer Memory Skill](../twilio-customer-memory/SKILL.md) — Memory Store, profiles, traits, observations, Recall
