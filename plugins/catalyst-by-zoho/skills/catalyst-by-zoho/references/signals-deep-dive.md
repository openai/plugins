# Signals Deep-Dive Reference

## When to use this file
Load this file when the user asks about: Signals architecture, publishers, custom publishers,
event rules, event filtering, dispatch policies, event transformation, webhooks, Signals
dashboard/logs, or any detailed Signals configuration beyond what `services.md` covers.

External docs: https://docs.catalyst.zoho.com/en/serverless/signals/

---

## Architecture Overview

The Signals pipeline flows as:

**Publisher → Event → Rule → Target → Dispatch Policy**

1. A **Publisher** emits an **Event** (a JSON payload).
2. A **Rule** listens for a specific event from a specific publisher.
3. The rule applies **filters** (optional) to decide if the event qualifies.
4. If the event passes filters, it is optionally **transformed**.
5. The event is dispatched to one or more **Targets** according to the **Dispatch Policy**.

---

## Publishers

Publishers are the sources that emit events into Signals. There are three types.

### 1. Zoho Publishers

Pre-built publishers from 17+ Zoho services. Events and schemas are predefined.

**Supported Zoho services include:** CRM, Books, Desk, Survey, Inventory, People, Recruit,
Projects, Analytics, Creator, Invoice, Subscriptions, Mail, Campaigns, Forms, Flow, and others.

**Constraints:**
- Max **100** Zoho publishers per Catalyst account
- Max event payload size: **100 KB**
- The Zoho service and the Catalyst project must belong to the **same Zoho organization**
- Events and schemas are predefined by the Zoho service — you cannot modify them

### 2. Catalyst Publishers

Built-in publishers from Catalyst Cloud Scale infrastructure services. These fire automatically
when data changes occur in your project.

**Catalyst services that emit events:**
- **Authentication** — user signup, login, password reset events
- **Cache** — cache segment operations (put, delete, flush)
- **Data Store** — table row insert, update, delete events
- **File Store** — file/folder create, update, delete events
- **Stratus** — Stratus component lifecycle events

**Event ordering:** Catalyst publisher events are **not guaranteed to arrive in order**. Design
your targets to handle out-of-order delivery (use timestamps or sequence numbers in your logic).

### 3. Custom Publishers

Your own applications or third-party services that emit events via REST API.

**Constraints:**
- Max **25** custom publishers per Catalyst account
- API rate limit: **500 requests/minute** per publisher
- Max individual event payload: **64 KB**
- Max array event payload: **256 KB** (when sending multiple events in one request)
- Max **25 publishers per deployment operation**

**Schema generation methods:**
- **Manual**: Define the event schema by hand in the console (JSON schema editor)
- **Live Events**: Send a sample event to the publisher endpoint and Signals auto-generates
  the schema from the live payload. This is the recommended approach — it avoids schema
  mismatches and saves time.

---

## Events

An event is the JSON payload emitted by a publisher. Each event has metadata and a body.

### Event Schema Structure

```json
{
  "event_id": "unique-event-id",
  "publisher_id": "publisher-id",
  "event_type": "event-name",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    // Event-specific payload fields
  }
}
```

### Event Statuses (8 total)

| Status | Description |
|--------|-------------|
| **Received** | Event received by Signals |
| **In Queue** | Event queued for rule evaluation |
| **In Progress** | Event being processed by a target |
| **Success** | Event successfully delivered to target |
| **Failed** | Target execution failed (may be retried) |
| **Unmatched** | No rule matched the event |
| **Unprocessed** | Event matched a rule but was not dispatched (e.g., rule disabled) |
| **Dropped** | Event dropped due to TTL expiry or policy |

### Limits
- Max **200 events** per publisher (event type definitions, not event instances)

---

## Rules

Rules control how events flow from a publisher to targets.

### Constraints
- Max **100 rules** per Catalyst account
- Max **5 targets** per rule
- Max **25 filters** per rule
- Each rule listens to exactly **1 event** from 1 publisher

### Filter Operators by Data Type

**String filters:**
- `equals`, `not_equals`, `contains`, `not_contains`, `starts_with`, `ends_with`,
  `is_empty`, `is_not_empty`

**Integer / Number filters:**
- `equals`, `not_equals`, `greater_than`, `less_than`, `greater_than_or_equal`,
  `less_than_or_equal`, `between`

**Boolean filters:**
- `equals`, `not_equals`

**DateTime filters:**
- `equals`, `not_equals`, `before`, `after`, `between`

Filters are combined with **AND** logic — all filters must match for the event to pass.

---

## Targets

Targets are the destinations that receive dispatched events. Three types are supported.

### 1. Webhooks
- HTTP endpoints (external or internal URLs)
- **Timeout**: 5 seconds (the webhook must respond within 5 seconds)
- Max **100 webhooks** per project
- Configure HTTP method, headers, parameters, and authentication
- Invocation rate: **1 to 300 requests/second** (configurable per webhook)
- **Authentication**: Use Catalyst Connections for OAuth-based auth to external services

**Header and parameter value types:**
- **Static**: A fixed string value
- **Dynamic**: A value extracted from the event payload (JSON path expression)
- **Placeholder**: A Catalyst system placeholder (e.g., project ID, environment)

### 2. Functions
- Catalyst Event Functions
- **Timeout**: 15 minutes max execution time
- Full access to Catalyst SDK within the function

### 3. Circuits
- Catalyst Circuit workflows
- **Timeout**: 5 seconds for the initial invocation (the Circuit itself runs asynchronously)

### Retry Policy

Two retry modes:

- **Automatic (exponential backoff)**: Signals retries failed deliveries automatically with
  increasing delays between attempts. The system determines the retry count and intervals.
- **Manual retry**: Failed events appear in the Signals logs. You can manually trigger a
  retry from the console for specific failed events.

---

## Dispatch Policies

Dispatch policies control when and how events are sent to targets.

### Instant Dispatch
- Events are dispatched to targets immediately upon rule match
- **TTL (Time To Live)**: 24 hours — undelivered events are dropped after 24 hours
- **Single event option**: When enabled, each event is dispatched individually (no batching)

### Batch Dispatch

Events are collected and dispatched in batches. Four batch trigger types:

| Batch Type | Configuration | Description |
|------------|--------------|-------------|
| **Count** | 2 to 100 events | Dispatch when N events accumulate |
| **Size** | Up to 100 KB | Dispatch when batch reaches size threshold |
| **Interval** | 2 to 12 hours | Dispatch every N hours regardless of count |
| **Schedule** | Daily at specific time | Dispatch once per day at a configured time |

When using batch dispatch, the target receives an array of events rather than a single event.

---

## Event Transformation

Transform the event payload before it reaches the target. Configured in the rule using a
three-pane visual editor in the console.

### Transformation Types

**Extraction (JSON Path)**
- Extract specific fields from the event payload using JSON path expressions
- Example: `$.data.deal.amount` extracts just the deal amount from a CRM event

**Transformation (Rebuild)**
- Rebuild the payload structure entirely
- Map fields from the source event to a new target schema
- Combine, rename, or restructure fields as needed

**For-each**
- When the event payload contains an array, apply the transformation to each element
- Useful for batch events or events with nested arrays

---

## Webhooks (Detailed)

### HTTP Methods Supported
- GET, POST, PUT, PATCH, DELETE

### Configuration Options
- **URL**: The target endpoint URL
- **Method**: HTTP method
- **Headers**: Custom headers with static, dynamic, or placeholder values
- **Parameters**: Query parameters with static, dynamic, or placeholder values
- **Body**: Request body (for POST/PUT/PATCH) — can use transformation output
- **Authentication**: Via Catalyst Connections (OAuth 1.0, OAuth 2.0, API Key, etc.)
- **Invocation rate**: 1 to 300 requests per second

### Constraints
- Max **100 webhooks** per project
- Response timeout: **5 seconds**
- The webhook must return an HTTP 2xx status to be considered successful

---

## Dashboard and Logs

### Dashboard
- Overview of all rules with event counts
- Success/failure rates per rule
- Event volume over time
- Filter by publisher, rule, target, time range

### Logs
- Detailed execution logs for each event delivery
- Includes: event payload, target response, status, timestamp, duration
- Filter by rule, status, time range
- Failed events can be retried from the logs view

---

## Deployment Notes

- Signals configuration is **environment-specific** — dev and prod have separate publishers,
  rules, and targets
- Deploying to production requires **admin permissions** on the Catalyst project
- Max **25 publishers** can be included in a single deployment operation
- Custom publisher endpoints must be accessible from the target environment (dev URLs won't
  work in prod and vice versa)
- Zoho publisher connections must be re-authorized in production if the Zoho service uses
  different credentials per environment

---

## Limits Summary

| Resource | Limit |
|----------|-------|
| Zoho publishers per account | 100 |
| Custom publishers per account | 25 |
| Custom publisher API rate | 500 req/min |
| Individual event payload (custom) | 64 KB |
| Array event payload (custom) | 256 KB |
| Zoho event payload | 100 KB |
| Event type definitions per publisher | 200 |
| Rules per account | 100 |
| Targets per rule | 5 |
| Filters per rule | 25 |
| Events per rule | 1 |
| Webhooks per project | 100 |
| Webhook timeout | 5 seconds |
| Webhook invocation rate | 1-300 req/sec |
| Function target timeout | 15 minutes |
| Circuit target timeout | 5 seconds (invocation) |
| Instant dispatch TTL | 24 hours |
| Batch count range | 2-100 events |
| Batch size max | 100 KB |
| Batch interval range | 2-12 hours |
| Publishers per deployment | 25 |
