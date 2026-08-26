# Cloud Notifications

Temporal Cloud sends notifications about system status and important administrative events.

---

## Status page subscriptions

In the event of an incident, Temporal updates the [Temporal Cloud status page](https://status.temporal.io/). Users can subscribe to updates in their preferred mode (e.g. email, Slack, SMS, etc.) by visiting this page.

---

## Administrative email notifications

Temporal Cloud sends emails to notify users of important administrative events.

| Reason for email | Who receives email |
|---|---|
| Certificate Expiring in 15 days | Global Administrator, Namespace Administrator, Account Owner |
| Certificate Expiring in 10 days | Global Administrator, Namespace Administrator, Account Owner |
| Certificate Expiring in 5 days | Global Administrator, Namespace Administrator, Account Owner |
| API Key Expiring in 30 days | Global Administrator, Account Owner, individual user (if API Key has an owner) |
| API Key Expiring in 20 days | Global Administrator, Account Owner, individual user (if API Key has an owner) |
| API Key Expiring in 10 days | Global Administrator, Account Owner, individual user (if API Key has an owner) |
| Sign up credit expiring in 30 days | Account Owner, Finance Administrator |
| Sign up credit expiring in 14 days | Account Owner, Finance Administrator |
| Sign up credit expiring in 7 days | Account Owner, Finance Administrator |
| Sign up credit expiring in 1 day | Account Owner, Finance Administrator |
| Sign up credit is 50% consumed | Account Owner, Finance Administrator |
| Sign up credit is 90% consumed | Account Owner, Finance Administrator |
| Account plan type changed | Global Administrator, Account Owner, Finance Administrator |
| Namespace Failover Completed/Failed | Global Administrator, Namespace Administrator, Account Owner |

---

## Quick reference: notification thresholds

| Resource | Notification schedule |
|---|---|
| Certificate expiry | 15, 10, 5 days before expiry |
| API Key expiry | 30, 20, 10 days before expiry |
| Sign up credit expiry | 30, 14, 7, 1 day(s) before expiry |
| Sign up credit consumption | 50%, 90% consumed |

---

## Email sender

To ensure you receive email notifications, configure your junk-email filters to permit email from `noreply@temporal.io`.

---

## Providing feedback

To provide feedback on notifications or request changes, create a support ticket.
