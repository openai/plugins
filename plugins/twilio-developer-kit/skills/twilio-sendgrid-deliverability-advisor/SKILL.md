---
name: twilio-sendgrid-deliverability-advisor
description: >
  Diagnostic and advisory skill for email deliverability problems. Use when
  a developer asks why emails are going to spam, not reaching the inbox,
  getting blocked, bouncing, or how to improve sender reputation — with or
  without a specified platform. Covers SendGrid-specific tooling: SPF, DKIM,
  DMARC, BIMI, IP warmup, list hygiene, bounce/spam rate thresholds, and
  Engagement Quality Score (SEQ). Do NOT use for Twilio Email
  (comms.twilio.com / Account SID + Auth Token) — use
  twilio-email-deliverability-advisor instead. Do NOT use for general email
  sending questions — use twilio-sendgrid-email-send (SendGrid) or
  twilio-email-deliverability-advisor instead.
tier: discover
---

## Role

You are an Email Deliverability Advisor. When a developer describes emails going to spam, bouncing, getting blocked, or asks how to improve inbox placement or sender reputation, use this framework to diagnose and recommend fixes.

## When This Skill Activates

Trigger on any of these signals:
- "Emails going to spam," "landing in junk," "not reaching inbox"
- "Blocked," "rejected," "deferred," "blacklisted," "denylisted"
- "Bounce rate too high," "spam complaints," "reputation score"
- "IP warmup," "dedicated IP," "shared IP"
- "SPF," "DKIM," "DMARC," "BIMI," "domain authentication"
- "SEQ score," "engagement quality," "sender score"
- "List hygiene," "spam traps," "invalid addresses"
- "How do I improve deliverability?"

Do NOT trigger for: general email sending implementation, template questions, webhook setup, suppression list management unrelated to deliverability. Redirect to `twilio-sendgrid-email-send` (SendGrid) for sending questions, `twilio-sendgrid-suppressions` for suppression management, `twilio-email-deliverability-advisor` for Twilio Email deliverability.

---

## Step 0: Identify Platform

Check for platform signals before proceeding:

| Signal | Platform | Action |
|--------|----------|--------|
| API key starts with `SG.` | SendGrid | Proceed |
| Mentions `app.sendgrid.com` | SendGrid | Proceed |
| Mentions `comms.twilio.com`, Account SID, or Auth Token | Twilio Email | Redirect |
| No signal | Unknown | Ask |

**If Twilio Email:** Stop. Respond: "For Twilio Email deliverability, use the `twilio-email-deliverability-advisor` skill — it's scoped to that platform."

**If unclear:** Ask exactly this before proceeding:
> "Are you using SendGrid (API key starting with `SG.`, dashboard at app.sendgrid.com) or Twilio Email (Twilio Account SID / Auth Token)?"

---

## Step 1: Detect the Problem Type

**Acute problem** (emails suddenly blocked, bounce rate spiked, on a denylist):
→ TRIAGE MODE. Something changed — diagnose before recommending.

**Gradual degradation** (deliverability declining over weeks, open rates dropping):
→ AUDIT MODE. Systematic review of authentication, list health, and sending patterns.

**Proactive setup** (new email program, new IP, new domain):
→ FOUNDATION MODE. Build the right infrastructure before problems occur.

---

## Step 2: Qualify the Situation — Key Questions

1. **What symptoms are you seeing?**
   - Bounces (hard vs soft), spam complaints, blocks, deferrals, or inbox placement problems
   - Check via Event Webhooks or SendGrid Activity Feed

2. **Is your domain authenticated?**
   - SPF, DKIM, DMARC all configured? (If any are missing, start here — this is the most common root cause)
   - Domain authentication in `app.sendgrid.com` → Settings → Sender Authentication + link branding

3. **Shared or dedicated IP?**
   - Shared IP (Trial/Essentials plans): reputation influenced by other senders on the pool
   - Dedicated IP (Pro/Premier): full control, but requires warmup before high-volume sending

4. **What does your list look like?**
   - How was it collected? (opt-in, double opt-in, purchased?)
   - When was it last cleaned?
   - Current bounce rate and spam complaint rate?

---

## Step 3: Diagnose by Symptom

### Emails going to spam / junk folder

**First: Is this a new IP/domain or an established sender?**
- **New or under-warmed IP/domain** → Jump to "New IP or domain not delivering well" below. IP warmup is the #1 cause of inbox placement issues for new senders. No amount of authentication fixes will help if your IP has no reputation yet.
- **Established sender (sending for months+)** → Proceed with the list below.

Most likely causes for established senders, in diagnostic order:
1. **Poor sender reputation** — Low SEQ score, high complaint rate, spam trap hits, or denylist appearance. Check SEQ dashboard and Google Postmaster Tools first.
2. **Low engagement** — ISPs interpret low open rates as "unwanted." Segment and send only to engaged subscribers. Sunset unengaged recipients at 6 months.
3. **Content issues** — Spammy subject lines, excessive links, poor text-to-image ratio, missing plain text version.
4. **Missing or misconfigured authentication** — SPF, DKIM, or DMARC not set up. Verify via Settings → Sender Authentication. Gmail, Yahoo, Microsoft, and Apple require DMARC for senders exceeding 5,000 messages/day; SPF and DKIM are required at all volumes.

### High bounce rate

- **Hard bounces > 2%:** List hygiene problem. Hard bounces must be removed immediately — they permanently damage reputation.
- **Soft bounces spiking:** Sending too fast (throttle), or temporary provider issues (retry with backoff).
- **Check:** Are you sending to purchased or old lists? Spam traps look like valid addresses until you hit them.

**Healthy thresholds:**
| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Hard bounce rate | < 1% | 1-2% | > 2% |
| Spam complaint rate | < 0.08% | 0.08-0.1% | > 0.1% |
| Soft bounce rate | < 5% | 5-10% | > 10% |

### Blocked or deferred by specific ISP/domain

- Check if your IP or domain is on a denylist (MXToolbox, Spamhaus)
- Verify DMARC policy — are failures being quarantined or rejected?
- **Deferrals**: SendGrid retries with exponential backoff for up to 72 hours. After 72 hours the message becomes a block. High deferral rates with Yahoo are normal when introducing new sending patterns — slow down volume.
- See **Inbox Provider Requirements** and **Blocklist Quick Reference** sections below for provider-specific guidance.

### New IP or domain not delivering well

This is an **IP/domain warmup** problem. ISPs treat new sending infrastructure with suspicion — no history = no trust.
- Start with your most engaged subscribers (highest open rates)
- Gradually increase volume: slower is better — allows you to spot and fix anomalies early
- SendGrid automated warmup runs a **41-day schedule** (Pro/Premier with dedicated IPs), capping hourly volume and overflowing to your other warm dedicated IPs. Since June 2025, overflow no longer falls back to SendGrid shared pools — if no other dedicated IPs exist, excess mail is retried and expires after 72 hours.
- Warmup applies primarily to **marketing email** — transactional sends are typically excluded from warmup throttling since they cannot be delayed
- ISPs store reputation data for ~30 days — re-warmup required if no traffic for 30+ days
- When hourly limit is hit, SendGrid retries with exponential backoff for up to 72 hours

---

## Step 4: Deliverability Foundation Checklist

### Authentication (do these first — they are table stakes)

| Protocol | What it does | Required? |
|----------|-------------|----------|
| **SPF** | Authorizes sending servers for your domain | Yes |
| **DKIM** | Cryptographic signature proving message integrity | Yes |
| **DMARC** | Policy for SPF/DKIM failures (none/quarantine/reject) | Required for >5,000 msgs/day (Gmail, Yahoo, Microsoft, Apple); >1,000/day for Orange |
| **Link Branding** (SendGrid) | Click-tracked links use your domain, not sendgrid.net | Strongly recommended |
| **Reverse DNS (rDNS)** | IP resolves back to your sending domain | Dedicated IP only |
| **BIMI** | Displays brand logo in inbox — requires DMARC quarantine/reject + strong reputation | Optional but high trust signal |

DMARC recommendation path: `p=none` (monitor) → `p=quarantine` (filter failures) → `p=reject` (block failures). Do not jump straight to `p=reject`.

### List Hygiene

- **Never buy email lists** — purchased lists are a primary source of spam traps and complaints
- Use **double opt-in** for marketing lists — confirms subscriber intent and prevents typos
- Remove hard bounces **immediately** after each send
- Run **reconfirmation/win-back campaigns** for subscribers inactive > 6 months, remove non-responders
- Validate addresses at the point of collection using the SendGrid Email Address Validation API
- Red flags that signal a list cleanup is overdue: bounce rate climbing, open rate declining, SEQ score dropping

### Sending Practices

- Maintain **consistent sending volume** — ISPs flag sudden spikes as suspicious
- **Segment by engagement** — send high-frequency content only to engaged subscribers, not your full list
- Send off-peak for better inbox placement (e.g., 10:53 vs 11:00)
- Use an **email preference center** — lets subscribers control frequency rather than hitting spam

---

## Step 5: Monitoring and Ongoing Health

### Engagement Quality Score (SEQ) — SendGrid

SEQ is the primary health metric for SendGrid accounts. Composite score across 5 dimensions:
1. **Bounce Classification** — type and severity of bounces
2. **Bounce Rate** — percentage of sends that bounce
3. **Engagement Recency** — how recently subscribers have opened/clicked
4. **Open Rate** — percentage of delivered emails opened
5. **Spam Rate** — percentage of emails marked as spam

SEQ score < threshold can trigger sending restrictions and affects shared IP pool placement. The SEQ API (for programmatic access) is available on Pro/Premier plans. Check via SendGrid dashboard or SEQ API.

### Event Webhooks — required for visibility

Without Event Webhooks you have no real-time signal on delivery problems. Every email program needs webhooks tracking:
- `bounce` — hard and soft bounces
- `spam_report` — recipient marked as spam
- `unsubscribe` — global and group unsubscribes
- `deferred` — ISP temporarily rejected (retry happening)
- `dropped` — suppressed before send

See `twilio-sendgrid-webhooks` for setup.

---

## Inbox Provider Requirements

| Provider | Domains | SPF | DKIM | DMARC threshold | Spam limit | FBL | Notes |
|----------|---------|-----|------|----------------|-----------|-----|-------|
| **Gmail** | gmail.com + Workspace | All volumes | All volumes | >5,000/day | <0.10% (enforce), <0.08% (recommended) (per Google) | None | Google Postmaster Tools available; `Feedback-ID` header enables complaint analytics; MPP does NOT apply |
| **Yahoo** | yahoo.com, aol.com, att.net, comcast.net, verizon.net | All volumes | All volumes | >5,000/day | Same as Gmail | DKIM-based; Twilio enrolled | Highest deferral rates — slow down when introducing new patterns; uses Spamhaus for blocklisting |
| **Microsoft** | outlook.com, hotmail.com, live.com, msn.com | All volumes | All volumes | >5,000/day (Outlook consumer); admin-determined (365) | — | JMRP (~72hr) | Reputation shared across all consumer domains; sends to unengaged >6 months triggers reputation issues; use SNDS to investigate; 365 doesn't send DMARC forensic reports |
| **Apple** | icloud.com, me.com, mac.com | All volumes | All volumes | >5,000/day | — | None | **Mail Privacy Protection (MPP)**: pre-fetches images on iOS 15+/macOS 12+, inflating open rates — filter with `sg_machine_open` webhook flag; uses Proofpoint for blocklisting |
| **Comcast** | comcast.net | Recommended | Recommended | Recommended | — | Validity FBL | **Migrating to Yahoo infrastructure** (gradual rollout through 2026) — authentication requirements will align with Yahoo post-migration |
| **Orange** | orange.fr, wanadoo.fr | All volumes | All volumes | >1,000/day | <0.6% | Signal Spam (Twilio not enrolled — audit lists manually) | Tightest spam threshold in the industry |

**Key actions per provider:**
- **Gmail blocks**: Check Google Postmaster Tools for domain/IP reputation. Add `Feedback-ID` header for granular complaint tracking.
- **Microsoft blocks**: Check SNDS for IP status. Use JMRP to get FBL data. Establish sunset policy at 6 months.
- **Apple open rate inflation**: Filter `sg_machine_open: true` events from engagement calculations.
- **Yahoo high deferrals**: Normal for new IPs/patterns — reduce sending rate and warm gradually.
- **Orange complaints**: No FBL signal; rely entirely on proactive list hygiene.

---

## Blocklist Quick Reference

| Provider | Impact | Auto-expires | Delisting |
|----------|--------|-------------|-----------|
| **Spamhaus** | High — affects Yahoo, AOL, Microsoft | No | Shared IPs: Twilio handles. Dedicated IPs: account owner requests. Fix behavior first. |
| **SpamCop** | Moderate | **24 hours** if no new trap hits | No manual delisting — auto-releases only |
| **Proofpoint** | High for Apple domains | No | Email `postmaster@proofpoint.com`; allow 72hr response; ensure rDNS is set and link branding configured |
| **Microsoft** | High for Outlook/365 | No | Submit through Outlook or 365 inquiry forms; include bounce examples |
| **Abusix** | Moderate | No | Abusix Inquiry Form |
| **Return Path / Validity** | Moderate | No | Return Path Inquiry Form / Sender Score |
| **Vade Secure** | Moderate | No | Vade Secure Inquiry Form |
| **UCE Protect** | Minimal | — | Twilio takes no action — listings here have negligible deliverability impact |

**Universal rule:** Fix the root behavior before requesting any delisting. Repeated requests without behavior changes are ignored.

---

## Output Format

After diagnosing, respond with:

```
Diagnosis: [Acute / Gradual / Proactive]
Root Cause: [Most likely issue based on symptoms]

Immediate Actions:
1. [Highest priority fix]
2. [Second fix]
3. [Third fix]

Skills to Install:
- twilio-sendgrid-account-setup (domain auth — SPF, DKIM, DMARC, link branding)
- twilio-sendgrid-engagement-quality (SEQ score — SendGrid Pro/Premier)
- twilio-sendgrid-suppressions (bounce and spam complaint management)
- twilio-sendgrid-webhooks (delivery event monitoring)
```

---

## CANNOT

- **Cannot diagnose deliverability without authentication being set up first** — SPF/DKIM/DMARC issues account for the majority of deliverability problems. Always verify these before investigating other causes.
- **Cannot guarantee inbox placement** — deliverability is probabilistic. ISPs make final delivery decisions. Best practices maximize the probability but do not guarantee outcomes.
- **Cannot recover reputation quickly** — reputation repair takes 2-4 weeks of consistent good sending behavior. There are no shortcuts.
- **Cannot remove from all denylists** — each denylist has its own removal process. Some auto-expire in 24-48 hours, others require manual request after addressing root cause.
- **BIMI cannot be implemented without DMARC quarantine or reject policy** — p=none is not sufficient for BIMI.

