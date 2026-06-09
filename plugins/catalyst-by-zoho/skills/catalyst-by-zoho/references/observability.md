# Catalyst Observability & Monitoring

## When to use this file
Load this file when the user asks about: Catalyst Logs, APM, Application Alerts, Audit Logs,
monitoring after deployment, performance debugging, memory optimization, or setting up failure
notifications for cron jobs or event listeners.

---

## DevOps Components Overview

Catalyst DevOps provides tools to operate your application at scale, monitor it post-deployment,
and perform iterative testing and quality checks. All DevOps components are accessible from the
unified Catalyst console.

---

## Logs

**What it provides:**
- Logs of **all function executions** across your project.
- Includes: log levels, responses, statuses, execution details, and exceptions.
- Access: **DevOps → Logs** in the Catalyst console.

**Key behaviors:**
- **Time zone**: configurable per component; defaults to the project's configured time zone.
  The project time zone is set in Settings → General Settings and applies across all components.
- **Auto-filtering**: when you access Logs from a specific function page, AppSail instance, or
  Circuit execution, the filters are automatically applied to show only that component's logs.
- **Circuit logs**: each Circuit execution log provides links to individual function logs and
  to the Catalyst Logs component for the specific function that was executed.
- **AppSail logs**: accessed via AppSail → Instances → click the Logs icon, which redirects
  to Catalyst Logs with the app's filter applied.

**Exporting logs:**
- Available from Settings → Audit Logs → Export Logs.
- Choose Console Logs, Application Logs, or both.
- Catalyst sends a notification when the export is ready; download via the provided link.

---

## Application Performance Monitoring (APM)

**What it provides:**
- In-depth stats and performance reports of function executions.
- Helps identify and resolve bugs and performance bottlenecks.
- Access: **DevOps → APM** in the Catalyst console.

**Available for:**
- Basic I/O functions
- Advanced I/O functions
- Event functions
- Cron functions
- Browser Logic functions
- Job functions

**Key metrics shown:**
- Average response time
- Execution duration distribution
- Memory usage
- Max Instances and number of requests vs time (AppSail)

**Memory optimization workflow using APM:**
1. Start with the lowest memory setting (128 MB for functions).
2. Deploy and execute under realistic load.
3. Check APM for average response time and error patterns.
4. Increase memory if response time is too high or executions are failing.
5. Repeat until you find the optimal balance of cost and performance.
6. APM and Catalyst Logs together are the primary tools for this process.

---

## Application Alerts

**What it provides:**
- Automatic email alerts when a Catalyst component encounters **failure**, **code exception**,
  or **timeout**.
- Access: **DevOps → Application Alerts**, or configure directly from the component's details page.

**Supported components:**
- Cron jobs
- Event Listeners
- Functions

**How to configure (shortcut):**
- Alerts can be configured directly from the **Cron details page** or **Event Listeners rules
  section** — no need to navigate to the Application Alerts component separately.
- From Cron: click **+Configure** in the cron's details section.
- From Event Listeners: click the configure option in the Event Listeners rules section.

**Critical behavior — Cron auto-disable:**
- Third-party URL crons are automatically **disabled after 50 consecutive failures**.
- Cron functions (not URL-based) are NOT auto-disabled regardless of failure count.
- Application Alerts catch these failures early, before the cron is auto-disabled.
- After fixing the issue, re-enable the cron from the console.

**Agent guidance — proactively suggest alerts:**
After helping a user deploy cron jobs or set up event listeners, always suggest:
> "Would you like me to help configure Application Alerts for this? Catalyst can email you
> automatically when the cron fails, times out, or throws an exception — directly from the
> cron details page."

---

## Audit Logs

**What it provides:**
- A record of all activities across your Catalyst account and projects.
- Access: **Settings → Audit Logs**.

**Two types:**
1. **Console Logs** — activities performed in console components (configuration changes,
   resource creation/deletion, permission changes).
2. **Application Logs** — activities at the application level (user actions, data operations
   through the application).

**Permission requirements:**
- Access to Audit Logs requires the "Access Audit Logs" permission in the user's profile.
- If choosing to provide Audit Logs access, you must first provide permissions to Data Store,
  File Store, Event Listeners, and Other Components (since Audit Logs shows their configurations).

**Exporting:**
- Exportable from the Audit Logs page: choose Console Logs, Application Logs, or both.
- A notification is sent when the export is complete.
- The download link for the last exported logs is always shown in the Export Logs popup.

---

## When agents should check monitoring

| After this action | Check this |
|-------------------|-----------|
| Deploying any function | DevOps → Logs (filter by function name, check for errors on first invocation) |
| Deploying AppSail | AppSail → Instances → Logs icon (verify app started, check cold start logs) |
| Running a Circuit | Circuits → Execution History → click execution → View Logs |
| Setting up a Cron job | DevOps → Application Alerts (configure failure notifications immediately) |
| Reporting performance issues | DevOps → APM (compare response times, identify slow functions) |
| Debugging auth issues | DevOps → Logs (look for 401/403 errors, ZAID mismatches) |
| Investigating data errors | DevOps → Logs (look for ZCQL errors, DataStore permission errors) |
| Security / compliance audit | Settings → Audit Logs (Console Logs + Application Logs) |

---

## Accessing logs from specific components

Instead of navigating to DevOps → Logs manually, you can access pre-filtered logs directly:

| Component | How to access its logs |
|-----------|------------------------|
| A function | Functions → select function → click Logs icon |
| An AppSail instance | AppSail → Instances → click Logs icon next to the instance |
| A Circuit execution | Circuits → Execution History → click execution → View Logs |
| A function called inside a Circuit | Circuit execution log → click the function link |
| A Cron job execution | Cron → Details → Execution History (also links to Catalyst Logs) |

---

## Summary: DevOps component quick reference

| Component | Access path | Primary use |
|-----------|-------------|-------------|
| **Logs** | DevOps → Logs | View all function execution logs, debug errors |
| **APM** | DevOps → APM | Performance reports, memory optimization |
| **Application Alerts** | DevOps → Application Alerts | Email alerts on failure/timeout/exception |
| **Audit Logs** | Settings → Audit Logs | Account-level activity trail, compliance |
