# Function Automations

Automations are triggers attached to backend functions. They cause a function to run automatically on a schedule (CRON, simple interval, or one-time) or when entity data changes (create, update, delete). Automations are defined in the `automations` array inside each function's `function.jsonc` and are deployed together with the function via `npx base44 functions deploy`.

## Overview

- **Where**: `base44/functions/<function-name>/function.jsonc` — optional `automations` array
- **Deploy**: Automations are deployed with the function; no separate command
- **Types**: Scheduled (one-time, CRON, simple interval) and entity hooks

## Common Fields (All Automation Types)

Every automation shares these base fields:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Display name for the automation (min 1 char) |
| `description` | string \| null | No | Optional description |
| `function_args` | object \| null | No | Key-value args passed to the function when it runs |
| `is_active` | boolean | No | Whether the automation is active (default: `true`) |

## Automation Types

### 1. Scheduled One-Time

Runs the function once at a specific date/time.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | `"scheduled"` | Yes | Must be `"scheduled"` |
| `schedule_mode` | `"one-time"` | Yes | One-time execution |
| `one_time_date` | string | Yes | ISO date/time when the function should run (e.g. `"2024-01-15T10:00:00"`) |

**Example:**

```jsonc
{
  "name": "my-function",
  "entry": "index.ts",
  "automations": [
    {
      "name": "Launch reminder",
      "type": "scheduled",
      "schedule_mode": "one-time",
      "one_time_date": "2026-03-01T09:00:00.000Z",
      "description": "One-time reminder on launch day"
    }
  ]
}
```

### 2. Scheduled CRON (Recurring)

Runs the function on a cron schedule. **Minimum interval is 5 minutes.**

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | `"scheduled"` | Yes | Must be `"scheduled"` |
| `schedule_mode` | `"recurring"` | Yes | Recurring execution |
| `schedule_type` | `"cron"` | Yes | Use cron expression |
| `cron_expression` | string | Yes | Standard cron: `minute hour day-of-month month day-of-week` |
| `ends_type` | `"never"` \| `"on"` \| `"after"` | No | When the schedule stops (default: `"never"`) |
| `ends_on_date` | string \| null | No | When `ends_type` is `"on"`, ISO date to stop |
| `ends_after_count` | number \| null | No | When `ends_type` is `"after"`, number of runs then stop |

**End conditions** (apply to both CRON and simple recurring):
- `ends_type="never"` — Run indefinitely (default)
- `ends_type="on"` — Run until a date: set `ends_on_date` (e.g. `"2024-12-31T23:59:59"`)
- `ends_type="after"` — Run N times: set `ends_after_count` (e.g. `10`)

**Cron format:** `minute hour day-of-month month day-of-week`

**Examples:**
- `"*/5 * * * *"` — every 5 minutes (minimum interval)
- `"0 9 * * *"` — 9am daily
- `"0 9 * * 1-5"` — 9am every weekday (Mon–Fri)

**Example:**

```jsonc
{
  "name": "daily-report",
  "entry": "index.ts",
  "automations": [
    {
      "name": "Daily Report",
      "type": "scheduled",
      "schedule_mode": "recurring",
      "schedule_type": "cron",
      "cron_expression": "0 9 * * *",
      "description": "Run every day at 9:00 UTC",
      "is_active": true
    }
  ]
}
```

### 3. Scheduled Simple (Recurring Interval)

Runs the function on a simple repeat (every N minutes/hours/days/weeks/months). **Minimum interval for minutes is 5** (e.g. every 5 minutes).

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | `"scheduled"` | Yes | Must be `"scheduled"` |
| `schedule_mode` | `"recurring"` | Yes | Recurring execution |
| `schedule_type` | `"simple"` | Yes | Use simple interval |
| `repeat_unit` | `"minutes"` \| `"hours"` \| `"days"` \| `"weeks"` \| `"months"` | Yes | Unit of repetition |
| `repeat_interval` | number | No | Positive integer; interval within the unit (default 1). For minutes, minimum is 5. |
| `start_time` | string \| null | No | Time of day (e.g. `"09:00"`, `"00:00"`) |
| `repeat_on_days` | number[] \| null | No | For weeks: 0–6 (0 = Sunday, 6 = Saturday) |
| `repeat_on_day_of_month` | number \| null | No | For months: 1–31 |
| `ends_type` | `"never"` \| `"on"` \| `"after"` | No | When the schedule stops (default: `"never"`) |
| `ends_on_date` | string \| null | No | When `ends_type` is `"on"`, ISO date to stop |
| `ends_after_count` | number \| null | No | When `ends_type` is `"after"`, number of runs then stop |

**End conditions:** Same as for CRON — `ends_type` / `ends_on_date` / `ends_after_count` (see Scheduled CRON above).

**Simple schedule examples:**
- Every 5 minutes: `repeat_interval=5`, `repeat_unit="minutes"` (minimum)
- Hourly: `repeat_interval=1`, `repeat_unit="hours"`
- Daily at specific time: `repeat_interval=1`, `repeat_unit="days"`, `start_time="09:00"`
- Weekly on specific days: `repeat_unit="weeks"`, `repeat_on_days=[1, 5]`, `start_time="10:00"` (e.g. Mon and Fri)
- Monthly on specific day: `repeat_unit="months"`, `repeat_on_day_of_month=15`, `start_time="00:00"`

**Example:**

```jsonc
{
  "name": "weekly-cleanup",
  "entry": "index.ts",
  "automations": [
    {
      "name": "Weekly Cleanup",
      "type": "scheduled",
      "schedule_mode": "recurring",
      "schedule_type": "simple",
      "repeat_unit": "weeks",
      "repeat_interval": 1,
      "repeat_on_days": [1],
      "start_time": "02:00",
      "description": "Every Monday at 2:00"
    }
  ]
}
```

### 4. Entity Hook

Runs the function when entity records are created, updated, or deleted.

**Required:** `entity_name`, `event_types` (array of `"create"`, `"update"`, `"delete"` — at least one).

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | `"entity"` | Yes | Must be `"entity"` |
| `entity_name` | string | Yes | Entity name (matches entity schema name, e.g. `Order`, `Task`) |
| `event_types` | `("create" \| "update" \| "delete")[]` | Yes | At least one; which events trigger the function |

**Example use cases:**
- Send email on new order: `entity_name="Order"`, `event_types=["create"]`
- Track status changes: `entity_name="Order"`, `event_types=["update"]`
- Cleanup on delete: `entity_name="User"`, `event_types=["delete"]`
- Multiple events: `entity_name="Order"`, `event_types=["create", "update"]`

**Example config:**

```jsonc
{
  "name": "on-order-created",
  "entry": "index.ts",
  "automations": [
    {
      "name": "On Order Created",
      "type": "entity",
      "entity_name": "Order",
      "event_types": ["create"],
      "description": "Run when a new order is created"
    },
    {
      "name": "On Order Update or Delete",
      "type": "entity",
      "entity_name": "Order",
      "event_types": ["update", "delete"]
    }
  ]
}
```

**Note:** `entity_name` must match the entity schema `name` in `base44/entities/` (e.g. entity file `order.jsonc` with `"name": "Order"` → use `"entity_name": "Order"`).

#### Entity hook payload

The function receives a JSON body with:

| Field | Description |
|-------|-------------|
| `event` | `{ type, entity_name, entity_id }` — event type, entity name, and record id |
| `data` | Current entity data. `null` if `payload_too_large` is true |
| `old_data` | Previous entity data (only for `"update"` events). `null` if `payload_too_large` is true or for create/delete |
| `payload_too_large` | `true` when entity data exceeded 200KB and was omitted. Use the Base44 SDK to fetch: `await base44.entities.<EntityName>.get(entity_id)` (or the dynamic API) to load the record. |

**Authentication / user identity:** When an automation runs (scheduled or entity hook), the request is authenticated as the **user who created the automation**, not as the user who performed the action. So `await base44.auth.me()` returns the automation creator. **There is no way to get the user who triggered the entity change** (e.g. who created, updated, or deleted the record). If you need to attribute actions, store a user reference on the entity (e.g. `created_by`, `updated_by`) and read it from `data` / `old_data` in the payload.

## Full Examples

### Daily CRON report

**base44/functions/daily-report/function.jsonc:**

```jsonc
{
  "name": "daily-report",
  "entry": "index.ts",
  "automations": [
    {
      "name": "Daily Report",
      "type": "scheduled",
      "schedule_mode": "recurring",
      "schedule_type": "cron",
      "cron_expression": "0 9 * * *",
      "is_active": true
    }
  ]
}
```

**base44/functions/daily-report/index.ts:**

```typescript
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  // Scheduled runs get auth context; use asServiceRole if you need full access
  const base44Admin = base44.asServiceRole;

  const orders = await base44Admin.entities.Orders.list({ limit: 100 });
  const summary = { total: orders.length, date: new Date().toISOString() };

  // e.g. send to Slack, email, or store in another entity
  return Response.json({ success: true, summary });
});
```

### Entity hook: on order created

**base44/functions/on-order-created/function.jsonc:**

```jsonc
{
  "name": "on-order-created",
  "entry": "index.ts",
  "automations": [
    {
      "name": "On Order Created",
      "type": "entity",
      "entity_name": "Order",
      "event_types": ["create"],
      "is_active": true
    }
  ]
}
```

**base44/functions/on-order-created/index.ts:**

```typescript
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  const payload = await req.json();
  const { event, data, old_data, payload_too_large } = payload;

  // event: { type, entity_name, entity_id }
  const entityId = event.entity_id;
  const eventType = event.type;

  // If payload was too large, data/old_data are null — fetch via SDK
  let current = data;
  if (payload_too_large && eventType !== "delete") {
    current = await base44.asServiceRole.entities.Orders.get(entityId);
  }

  // e.g. send confirmation email on create, or compare old_data vs data on update
  return Response.json({ success: true, orderId: entityId, eventType });
});
```

### Weekly cleanup (simple schedule)

**base44/functions/weekly-cleanup/function.jsonc:**

```jsonc
{
  "name": "weekly-cleanup",
  "entry": "index.ts",
  "automations": [
    {
      "name": "Weekly Cleanup",
      "type": "scheduled",
      "schedule_mode": "recurring",
      "schedule_type": "simple",
      "repeat_unit": "weeks",
      "repeat_interval": 1,
      "repeat_on_days": [1],
      "start_time": "02:00",
      "description": "Every Monday at 2:00"
    }
  ]
}
```

## Common Patterns

| Pattern | Use | Automation type |
|--------|-----|------------------|
| Daily report / digest | Email or Slack at 9am | CRON with `cron_expression`: `0 9 * * *` |
| On new record | Notify, sync, or validate when entity is created | Entity hook with `event_types`: `["create"]` |
| On update/delete | Audit, cache invalidation, or cleanup | Entity hook with `event_types`: `["update"]` or `["delete"]` |
| Weekly job | Cleanup or aggregation every Monday | Simple with `repeat_unit`: `"weeks"`, `repeat_on_days`: `[1]` |
| One-time run | Launch task or migration at a fixed time | One-time with `one_time_date` |

## Deploying

Automations are deployed with their function. There is no separate automation deploy command.

```bash
npx base44 functions deploy
```

This deploys all functions in `base44/functions/` and their `automations` arrays. For more on deployment, see [functions-deploy.md](functions-deploy.md).

## Common Mistakes

| Wrong | Correct | Why |
|-------|---------|-----|
| `entity_name: "order"` when schema name is `Order` | `entity_name: "Order"` | Entity name must match schema `name` exactly |
| `event_types: []` or missing | `event_types: ["create"]` (at least one) | At least one event type is required for entity hooks |
| Assuming `base44.auth.me()` is the user who triggered the entity change | Use `data` / `old_data` (e.g. `created_by`, `updated_by`) if you need who did the action | In automations, `auth.me()` is the user who **created the automation**. The triggering user is not available. |
| `schedule_type: "cron"` without `cron_expression` | Always set `cron_expression` for cron | Cron schedules require a valid cron expression |
| Putting automations in a separate file | Put `automations` inside `function.jsonc` | Automations are part of the function config |
| Expecting a separate `base44 automations deploy` | Use `npx base44 functions deploy` | Automations deploy with the function |
