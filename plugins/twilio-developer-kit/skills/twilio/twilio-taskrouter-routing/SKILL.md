---
name: twilio-taskrouter-routing
description: >
  Route tasks to agents using Twilio TaskRouter. Covers Workers, Task
  Queues, Workflows, Reservations, skills-based routing, and common
  gotchas (hyphen attributes, HAS operator, reservation cascade). Use this
  skill for any multi-agent contact center, support queue, or AI agent
  escalation routing.
---

## Overview

TaskRouter is Twilio's skills-based routing engine. Instead of building custom queuing logic, you define Workers (agents), Task Queues (groups), and Workflows (routing rules). TaskRouter matches incoming tasks to the best available worker.

```
Incoming Task → Workflow (routing rules) → Task Queue (skill match) → Worker (agent)
                                                                        ↓
                                                                   Reservation
                                                                   (accept/reject)
```

**Common mistake:** Developers reinvent TaskRouter in custom Node.js — don't. If you're building skills-based routing, queue management, or agent assignment, use TaskRouter.

---

## Prerequisites

- Twilio account — see `twilio-account-setup`
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`
- SDK: `pip install twilio` / `npm install twilio`
- For voice routing: a Twilio phone number with webhook configured — see `twilio-voice-twiml`
- For AI escalation: ConversationRelay with escalation tools — see `twilio-voice-conversation-relay`

---

## Quickstart

**Step 1 — Create a Workspace**

A Workspace is the top-level container for all TaskRouter resources.

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

workspace = client.taskrouter.v1.workspaces.create(
    friendly_name="Support Center",
    event_callback_url="https://yourapp.com/taskrouter-events"
)

workspace_sid = workspace.sid  # WSxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
print(workspace_sid)
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

const workspace = await client.taskrouter.v1.workspaces.create({
    friendlyName: "Support Center",
    eventCallbackUrl: "https://yourapp.com/taskrouter-events",
});

const workspaceSid = workspace.sid;
```

**Step 2 — Create Activities (agent states)**

**Python**
```python
# Available — worker can receive tasks
available = client.taskrouter.v1.workspaces(workspace_sid).activities.create(
    friendly_name="Available", available=True
)

# Offline — worker cannot receive tasks
offline = client.taskrouter.v1.workspaces(workspace_sid).activities.create(
    friendly_name="Offline", available=False
)

# On a task — worker is busy
on_task = client.taskrouter.v1.workspaces(workspace_sid).activities.create(
    friendly_name="On Task", available=False
)
```

**Step 3 — Create Workers (agents)**

> **Security:** Always use `json.dumps()` (Python) or `JSON.stringify()` (Node.js) to construct attribute payloads. String interpolation is vulnerable to JSON injection.

**Python**
```python
worker = client.taskrouter.v1.workspaces(workspace_sid).workers.create(
    friendly_name="Alice",
    attributes='{"skills": ["billing", "technical"], "languages": ["en", "es"], "department": "support"}'
)
```

**Node.js**
```node
const worker = await client.taskrouter.v1.workspaces(workspaceSid).workers.create({
    friendlyName: "Alice",
    attributes: JSON.stringify({
        skills: ["billing", "technical"],
        languages: ["en", "es"],
        department: "support",
    }),
});
```

**Step 4 — Create Task Queues**

**Python**
```python
# Billing queue — matches workers with "billing" skill
billing_queue = client.taskrouter.v1.workspaces(workspace_sid).task_queues.create(
    friendly_name="Billing",
    target_workers='skills HAS "billing"'
)

# Technical queue
tech_queue = client.taskrouter.v1.workspaces(workspace_sid).task_queues.create(
    friendly_name="Technical",
    target_workers='skills HAS "technical"'
)

# Catch-all queue
default_queue = client.taskrouter.v1.workspaces(workspace_sid).task_queues.create(
    friendly_name="Default",
    target_workers='1==1'  # matches all workers
)
```

**Step 5 — Create a Workflow (routing rules)**

**Python**
```python
import json

workflow_config = {
    "task_routing": {
        "filters": [
            {
                "filter_friendly_name": "Billing",
                "expression": "department == 'billing'",
                "targets": [
                    {"queue": billing_queue.sid, "timeout": 120}
                ]
            },
            {
                "filter_friendly_name": "Technical",
                "expression": "department == 'technical'",
                "targets": [
                    {"queue": tech_queue.sid, "timeout": 120}
                ]
            }
        ],
        "default_filter": {
            "queue": default_queue.sid
        }
    }
}

workflow = client.taskrouter.v1.workspaces(workspace_sid).workflows.create(
    friendly_name="Support Routing",
    configuration=json.dumps(workflow_config),
    assignment_callback_url="https://yourapp.com/assignment"
)
```

**Step 6 — Create a Task (from an incoming call)**

**Python**
```python
task = client.taskrouter.v1.workspaces(workspace_sid).tasks.create(
    attributes='{"department": "billing", "caller": "+15558675310", "priority": 1}',
    workflow_sid=workflow.sid
)
```

**Step 7 — Handle the Assignment Callback**

When TaskRouter finds a matching worker, it POSTs to your `assignment_callback_url`:

**Python (Flask)**
```python
@app.route("/assignment", methods=["POST"])
def assignment():
    task_sid = request.form["TaskSid"]
    worker_sid = request.form["WorkerSid"]
    reservation_sid = request.form["ReservationSid"]

    # Option A: Dequeue to the worker's phone
    return jsonify({
        "instruction": "dequeue",
        "from": "+15551234567",  # your Twilio number
        "post_work_activity_sid": available_activity_sid
    })

    # Option B: Conference the caller and agent
    # return jsonify({
    #     "instruction": "conference",
    #     "from": "+15551234567",
    #     "post_work_activity_sid": available_activity_sid
    # })
```

**Node.js (Express)**
```node
app.post("/assignment", (req, res) => {
    res.json({
        instruction: "dequeue",
        from: "+15551234567",
        post_work_activity_sid: availableActivitySid,
    });
});
```

---

## Key Patterns

### Skills-Based Routing

Match tasks to workers based on attributes:

| Worker expression | Matches |
|-------------------|---------|
| `skills HAS "billing"` | Workers whose `skills` array contains "billing" |
| `languages HAS "es"` | Spanish-speaking workers |
| `department == "support"` | Workers in support department |
| `experience > 5` | Workers with 5+ years experience |
| `skills HAS "billing" AND languages HAS "es"` | Spanish-speaking billing agents |

### Priority Routing

Tasks with higher priority are assigned first:

```python
# VIP customer — priority 10 (higher = first)
task = client.taskrouter.v1.workspaces(workspace_sid).tasks.create(
    attributes='{"department": "billing", "priority": 10, "vip": true}',
    workflow_sid=workflow.sid,
    priority=10
)
```

### AI Agent Escalation

When an AI agent (via TAC) escalates to a human, create a TaskRouter task with the AI's context:

```python
# From your escalation webhook handler
def handle_escalation(escalation_data):
    task = client.taskrouter.v1.workspaces(workspace_sid).tasks.create(
        attributes=json.dumps({
            "department": escalation_data["reason_code"],
            "conversation_id": escalation_data["conversation_id"],
            "profile_id": escalation_data["profile_id"],
            "ai_summary": escalation_data["summary"],
            "priority": 5
        }),
        workflow_sid=workflow.sid
    )
```

The human agent receives the AI's conversation summary and customer profile.

### Workflow with Timeout Escalation

Route to specialized queue first, then overflow to general:

```python
workflow_config = {
    "task_routing": {
        "filters": [
            {
                "filter_friendly_name": "Billing Specialist First",
                "expression": "department == 'billing'",
                "targets": [
                    {"queue": billing_queue.sid, "timeout": 60},      # Try billing queue for 60s
                    {"queue": default_queue.sid, "timeout": 120}      # Overflow to general
                ]
            }
        ],
        "default_filter": {
            "queue": default_queue.sid
        }
    }
}
```

### Worker Activity Management

```python
# Set worker to available
client.taskrouter.v1.workspaces(workspace_sid) \
    .workers(worker_sid) \
    .update(activity_sid=available_activity_sid)

# Get real-time worker statistics
stats = client.taskrouter.v1.workspaces(workspace_sid) \
    .workers \
    .statistics() \
    .fetch()

print(f"Available: {stats.realtime['total_available_workers']}")
```

---

## Scale Guidance

| Agents | Architecture | Notes |
|--------|-------------|-------|
| < 10 | Single workflow, one queue per skill | No Flex needed — agents use phone |
| 10-50 | Multi-queue workflows, skills-based routing | Flex recommended for desktop |
| 50+ | Multi-tier workflows, priority routing, real-time monitoring | Full Flex + supervisor tools |

---

## Gotchas

### 1. Hyphens in Attribute Names Break Silently

```python
# WRONG — hyphens in attribute keys break workflow expressions
worker = client.taskrouter.v1.workspaces(workspace_sid).workers.create(
    friendly_name="Alice",
    attributes='{"skill-level": 5}'  # hyphen breaks expression evaluation
)

# RIGHT — use underscores or camelCase
worker = client.taskrouter.v1.workspaces(workspace_sid).workers.create(
    friendly_name="Alice",
    attributes='{"skill_level": 5}'
)
```

No error — the expression silently fails to match.

### 2. HAS Operator on Non-Array Attributes

```python
# WRONG — "billing" is a string, not an array. HAS silently matches nothing.
target_workers = 'department HAS "billing"'

# RIGHT — use == for string attributes
target_workers = 'department == "billing"'

# RIGHT — use HAS only for arrays
target_workers = 'skills HAS "billing"'  # skills: ["billing", "technical"]
```

Tasks sit in queue forever with no error.

### 3. Reservation Timeout Cascade

When a reservation times out:
1. Worker moves to the timeout Activity (often "Offline")
2. Fewer workers available → other reservations also time out
3. Positive feedback loop → entire queue backs up

**Fix:** Set the timeout Activity to a short-duration state, not "Offline". Or implement a reservation timeout handler that keeps the worker available:

```python
@app.route("/taskrouter-events", methods=["POST"])
def taskrouter_event():
    event_type = request.form["EventType"]
    if event_type == "reservation.timeout":
        worker_sid = request.form["WorkerSid"]
        # Keep worker available instead of moving to offline
        client.taskrouter.v1.workspaces(workspace_sid) \
            .workers(worker_sid) \
            .update(activity_sid=available_activity_sid)
    return "", 200
```

### 4. Activity Available Flag

Updating an Activity's `available` flag returns 200 OK but may not change the value if workers are currently in that activity. Create new activities instead of modifying existing ones.

---

## CANNOT

- **Hyphens in attribute names break expressions** — `skill-level` is treated as subtraction (`skill` minus `level`). Error 20001. Always use underscores: `skill_level`.
- **`HAS` on non-array silently matches nothing** — `department HAS "billing"` on a string attribute is accepted at creation but never matches. Tasks sit in queue forever with no error.
- **Expression validation is syntactic only** — Queue creation validates parse but NOT worker matching. Semantically wrong expressions create successfully with zero matching workers.
- **Activity `available` flag is silently immutable** — Updating returns 200 OK but does not change the value. Must delete and recreate the Activity.
- **`multiTaskEnabled` cannot be reverted to false** — Once enabled on a Workspace, cannot be disabled. One-way door.
- **Reservation timeout moves worker to timeout Activity** — Worker automatically moved to Offline. Must manually set back. This cascades: fewer available workers → more timeouts → queue collapse. See Gotcha #3.
- **Workflow target timeout auto-cancels tasks** — When all targets exhaust timeouts, task is canceled. Always include a `default_filter` as catch-all.
- **Worker `friendlyName` is case-insensitive unique** — "alice" collides with "Alice".
- **`workflowSid` is required for task creation** — API does not auto-select a default Workflow.
- **Cannot update task status and attributes in same request** — Must be two separate API calls.
- **Assignment callback must respond in 5 seconds** — If both primary and fallback URLs fail, reservation is canceled.
- **Tasks auto-cancel after 1,000 rejections** — If a task cycles through 1,000 reservation rejections, it is automatically canceled.
- **`page` query param not supported** — Use `PageToken` for pagination. `page` returns error 40153.
- **Cannot use malformed JSON in worker attributes** — Silently breaks matching with no error
- **Cannot use regex in workflow expressions** — Only supports ==, !=, <, >, HAS, IN, CONTAINS, AND, OR, NOT
- **Cannot exceed 50,000 Workers per Workspace** — Hard limit
- **Cannot exceed 250 Task Queues per Workspace** — Hard limit
- **Cannot delay reservation callback response beyond 15 seconds** — Timeout results in reservation failure

---

## Next Steps

- **Conference for transfers:** `twilio-conference-calls`
- **Call recording:** `twilio-call-recordings`
- **AI agent voice integration:** `twilio-voice-conversation-relay`
- **Voice IVR before routing:** `twilio-voice-twiml`
