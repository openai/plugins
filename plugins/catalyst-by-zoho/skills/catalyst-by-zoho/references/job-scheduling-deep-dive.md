# Job Scheduling Deep-Dive Reference

## When to use this file
Load this file when the user asks about: Job Scheduling, job pools, cron jobs, cron expressions,
dynamic cron, scheduled tasks, job execution history, or migrating from deprecated Cron to Job
Scheduling.

External docs: https://docs.catalyst.zoho.com/en/serverless/job-scheduling/

---

## Architecture Overview

**Job Pool → Jobs/Cron → Targets**

1. A **Job Pool** is a container that groups related jobs and defines the target type.
2. **Jobs** are individual task submissions to a pool (on-demand or scheduled).
3. **Cron** schedules define when jobs are automatically submitted.
4. **Targets** are the Catalyst components that execute the job logic.

---

## Job Pools

A Job Pool is the top-level container. Each pool is bound to a specific target type and
memory allocation.

### Pool Types (4 types — immutable after creation)

| Pool Type | Target | Description |
|-----------|--------|-------------|
| **Function** | Job Function | Executes a Catalyst Job Function |
| **Webhook** | HTTP endpoint | Calls an external URL |
| **Circuit** | Catalyst Circuit | Triggers a Circuit workflow |
| **AppSail** | AppSail service | Calls an AppSail endpoint |

**Important:** The pool type is **immutable** — once created, you cannot change a pool from
Function to Webhook or any other type. Create a new pool if you need a different target type.

### Memory Allocation
- Max **10 GB** memory per job pool
- Memory is shared across all concurrent job executions in the pool
- Configure based on expected parallel workload

### Parallel Triggers
- Max **10 parallel triggers** per job pool
- If all 10 slots are occupied, new job submissions queue until a slot frees up

---

## Jobs

### Configuration Fields
- **Job name**: Identifier for the job
- **Input data**: JSON payload passed to the target (stringified)
- **Priority**: Execution priority within the pool queue
- **Timeout**: Max execution time for the job

### Submission Methods
- **Console**: Submit a job manually from the Catalyst console
- **SDK**: Submit programmatically from Catalyst functions or AppSail
- **REST API**: Submit via the Job Scheduling REST API
- **Cron**: Automatic submission on a schedule

### Execution States

| State | Description |
|-------|-------------|
| **Queued** | Job submitted and waiting for an available slot |
| **In Progress** | Job is currently executing |
| **Success** | Job completed successfully |
| **Failed** | Job execution failed |
| **Timed Out** | Job exceeded its configured timeout |
| **Cancelled** | Job was cancelled before execution |

---

## Cron

Cron schedules automatically submit jobs to a pool at defined intervals.

### Pre-defined Cron
- Created via the **Catalyst Console**
- Configured in the console UI with a visual schedule builder
- **Migrates to production** when you deploy to prod
- Recommended for stable, recurring schedules

### Dynamic Cron
- Created via the **Catalyst SDK** at runtime
- Configured programmatically in your function/AppSail code
- **Does NOT migrate to production** — must be created separately in each environment
- Recommended for schedules that depend on runtime data or user configuration

---

## Schedule Types

### One-Time
- Executes once at a specified date and time
- Automatically removed after execution

### Recurring
- Executes repeatedly based on a cron expression
- Minimum interval: **1 minute**
- Continues until disabled or deleted

---

## Cron Expressions

5-field cron format:

```
┌───────── minute (0-59)
│ ┌───────── hour (0-23)
│ │ ┌───────── day of month (1-31)
│ │ │ ┌───────── month (1-12)
│ │ │ │ ┌───────── day of week (0-6, 0=Sunday)
│ │ │ │ │
* * * * *
```

### Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Every value | `* * * * *` = every minute |
| `,` | List of values | `0,15,30,45 * * * *` = every 15 minutes |
| `-` | Range | `0-5 * * * *` = minutes 0 through 5 |
| `/` | Step | `*/10 * * * *` = every 10 minutes |

### Common Cron Expression Examples

| Expression | Schedule |
|------------|----------|
| `* * * * *` | Every minute |
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour (at minute 0) |
| `0 0 * * *` | Daily at midnight |
| `0 9 * * 1-5` | Weekdays at 9:00 AM |
| `0 0 1 * *` | First day of every month at midnight |
| `0 0 * * 0` | Every Sunday at midnight |
| `30 8 * * 1` | Every Monday at 8:30 AM |
| `0 */6 * * *` | Every 6 hours |
| `0 9,17 * * *` | At 9:00 AM and 5:00 PM daily |

---

## Dynamic Cron SDK Examples

### Node.js

```javascript
const jobScheduling = catalystApp.jobScheduling();
const pool = jobScheduling.pool(POOL_ID);

// Every / Periodic — every 10 minutes
await pool.createCron({
  cron_name: 'periodic-sync',
  cron_type: 'periodic',
  every: { minutes: 10 },
  input: JSON.stringify({ task: 'sync-data' })
});

// Daily — at 9:00 AM
await pool.createCron({
  cron_name: 'daily-report',
  cron_type: 'daily',
  time: '09:00',
  input: JSON.stringify({ task: 'generate-report' })
});

// Monthly — 1st of every month at midnight
await pool.createCron({
  cron_name: 'monthly-cleanup',
  cron_type: 'monthly',
  day_of_month: 1,
  time: '00:00',
  input: JSON.stringify({ task: 'cleanup' })
});

// Expression — custom cron expression (weekdays at 8:30 AM)
await pool.createCron({
  cron_name: 'weekday-task',
  cron_type: 'expression',
  cron_expression: '30 8 * * 1-5',
  input: JSON.stringify({ task: 'weekday-process' })
});

// One-Time — execute once at a specific time
await pool.createCron({
  cron_name: 'one-time-migration',
  cron_type: 'one_time',
  execution_time: '2025-06-15T14:00:00Z',
  input: JSON.stringify({ task: 'migrate-data' })
});
```

### Java

```java
JobScheduling jobScheduling = catalystApp.jobScheduling();
JobPool pool = jobScheduling.pool(POOL_ID);

// Every / Periodic — every 10 minutes
JSONObject periodicCron = new JSONObject();
periodicCron.put("cron_name", "periodic-sync");
periodicCron.put("cron_type", "periodic");
periodicCron.put("every", new JSONObject().put("minutes", 10));
periodicCron.put("input", "{\"task\":\"sync-data\"}");
pool.createCron(periodicCron);

// Daily — at 9:00 AM
JSONObject dailyCron = new JSONObject();
dailyCron.put("cron_name", "daily-report");
dailyCron.put("cron_type", "daily");
dailyCron.put("time", "09:00");
dailyCron.put("input", "{\"task\":\"generate-report\"}");
pool.createCron(dailyCron);

// Monthly — 1st of every month at midnight
JSONObject monthlyCron = new JSONObject();
monthlyCron.put("cron_name", "monthly-cleanup");
monthlyCron.put("cron_type", "monthly");
monthlyCron.put("day_of_month", 1);
monthlyCron.put("time", "00:00");
monthlyCron.put("input", "{\"task\":\"cleanup\"}");
pool.createCron(monthlyCron);

// Expression — custom cron expression
JSONObject exprCron = new JSONObject();
exprCron.put("cron_name", "weekday-task");
exprCron.put("cron_type", "expression");
exprCron.put("cron_expression", "30 8 * * 1-5");
exprCron.put("input", "{\"task\":\"weekday-process\"}");
pool.createCron(exprCron);

// One-Time
JSONObject oneTimeCron = new JSONObject();
oneTimeCron.put("cron_name", "one-time-migration");
oneTimeCron.put("cron_type", "one_time");
oneTimeCron.put("execution_time", "2025-06-15T14:00:00Z");
oneTimeCron.put("input", "{\"task\":\"migrate-data\"}");
pool.createCron(oneTimeCron);
```

### Python

```python
job_scheduling = catalyst_app.job_scheduling()
pool = job_scheduling.pool(POOL_ID)

# Every / Periodic — every 10 minutes
pool.create_cron({
    "cron_name": "periodic-sync",
    "cron_type": "periodic",
    "every": {"minutes": 10},
    "input": '{"task": "sync-data"}'
})

# Daily — at 9:00 AM
pool.create_cron({
    "cron_name": "daily-report",
    "cron_type": "daily",
    "time": "09:00",
    "input": '{"task": "generate-report"}'
})

# Monthly — 1st of every month at midnight
pool.create_cron({
    "cron_name": "monthly-cleanup",
    "cron_type": "monthly",
    "day_of_month": 1,
    "time": "00:00",
    "input": '{"task": "cleanup"}'
})

# Expression — custom cron expression
pool.create_cron({
    "cron_name": "weekday-task",
    "cron_type": "expression",
    "cron_expression": "30 8 * * 1-5",
    "input": '{"task": "weekday-process"}'
})

# One-Time
pool.create_cron({
    "cron_name": "one-time-migration",
    "cron_type": "one_time",
    "execution_time": "2025-06-15T14:00:00Z",
    "input": '{"task": "migrate-data"}'
})
```

---

## Cron Management

### Edit
- Pre-defined crons can be edited in the console (schedule, input, name)
- Dynamic crons must be updated via the SDK

### Enable / Disable
- Toggle cron active state without deleting
- Disabled crons retain their configuration but do not submit jobs

### Execution History
- **Development**: Last **15 days** of execution history retained
- **Production**: Last **30 days** of execution history retained
- History shows: execution time, status, duration, input/output

### Delete
- Permanently removes the cron and its history
- Active jobs submitted by a deleted cron continue to execute

---

## Application Alerts

Configure automatic email alerts for job pool failures.

### Function Pool Triggers
- Job execution failure
- Job timeout
- Code exception in the job function

### Circuit / AppSail / Webhook Pool Triggers
- Target invocation failure
- Target timeout
- HTTP error responses (for Webhook/AppSail targets)

### Alert Configuration
- Set recipients (email addresses)
- Configure frequency (every failure, or batched)
- Available in Console → DevOps → Application Alerts or from the job pool details page

---

## Dashboard Metrics

The Job Scheduling dashboard shows:
- Total jobs submitted, succeeded, failed, timed out
- Job execution duration distribution
- Pool utilization (active slots vs. total capacity)
- Cron execution success/failure rates
- Queue depth and wait times

---

## REST API Endpoints

### Job Pool APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/server/jobscheduling/pool` | List all job pools |
| GET | `/server/jobscheduling/pool/{pool_id}` | Get pool details |
| POST | `/server/jobscheduling/pool` | Create a job pool |
| PUT | `/server/jobscheduling/pool/{pool_id}` | Update a job pool |
| DELETE | `/server/jobscheduling/pool/{pool_id}` | Delete a job pool |

### Job APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/server/jobscheduling/pool/{pool_id}/job` | List jobs in a pool |
| GET | `/server/jobscheduling/pool/{pool_id}/job/{job_id}` | Get job details |
| POST | `/server/jobscheduling/pool/{pool_id}/job` | Submit a job |
| DELETE | `/server/jobscheduling/pool/{pool_id}/job/{job_id}` | Cancel a job |

### Cron APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/server/jobscheduling/pool/{pool_id}/cron` | List crons in a pool |
| GET | `/server/jobscheduling/pool/{pool_id}/cron/{cron_id}` | Get cron details |
| POST | `/server/jobscheduling/pool/{pool_id}/cron` | Create a cron |
| PUT | `/server/jobscheduling/pool/{pool_id}/cron/{cron_id}` | Update a cron |
| DELETE | `/server/jobscheduling/pool/{pool_id}/cron/{cron_id}` | Delete a cron |
| PUT | `/server/jobscheduling/pool/{pool_id}/cron/{cron_id}/enable` | Enable a cron |
| PUT | `/server/jobscheduling/pool/{pool_id}/cron/{cron_id}/disable` | Disable a cron |

---

## Limits Summary

| Resource | Limit |
|----------|-------|
| Job pools per project | Varies by plan |
| Memory per pool | 10 GB max |
| Parallel triggers per pool | 10 |
| Minimum cron interval | 1 minute |
| Execution history (dev) | 15 days |
| Execution history (prod) | 30 days |
| Pool type | Immutable after creation |
| Dynamic cron migration | Does NOT migrate to production |
| Pre-defined cron migration | Migrates to production on deploy |
