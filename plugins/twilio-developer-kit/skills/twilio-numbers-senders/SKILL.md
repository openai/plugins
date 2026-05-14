---
name: twilio-numbers-senders
description: >
  Choose the right Twilio number type and sender BEFORE building. Covers
  phone numbers (local, toll-free, short code, mobile), alphanumeric sender
  IDs, WhatsApp senders, RCS agents, international availability, and
  regulatory bundles. Each number type has its own compliance program —
  choosing wrong means rebuilding. Use this skill first.
---

## Overview

Choosing the right number type and sender is the **first decision** in any Twilio project. Each number type comes with its own compliance/verification program, throughput limits, and capabilities. Developers who skip this step buy numbers first, build their app, then discover they chose the wrong type.

**Lifecycle:** Choose numbers/senders (this skill) → Register them (`twilio-compliance-onboarding`) → Follow traffic rules (`twilio-compliance-traffic`)

---

## US Number Types — Comparison

| | **Local (10DLC)** | **Toll-Free** (800/888/877) | **Short Code** (5-6 digits) |
|---|---|---|---|
| **SMS** | Yes | Yes | Yes |
| **MMS** | Yes | Yes | Yes |
| **Voice** | Yes | Yes | No |
| **Two-way** | Yes | Yes | Yes |
| **Throughput** | ~1-75+ SMS/sec (varies by trust score) | ~3 SMS/sec | 10-100 SMS/sec |
| **Compliance program** | **A2P 10DLC** (brand + campaign) | **Toll-Free Verification** | **Pre-approved at purchase** (carrier review) |
| **Approval timeline** | 10-15 business days | 3-5 business days | 8-12 weeks provisioning |
| **Best for** | Transactional, marketing, support | Notifications, support, verification | High-volume marketing, 2FA |
| **Cost** | Lowest | Medium | Highest (setup + monthly + per-msg) |

Source: [US/Canada SMS comparison](https://help.twilio.com/articles/360038173654-Comparison-of-SMS-messaging-in-the-US-and-Canada-for-long-codes-short-codes-and-toll-free-phone-numbers)

### Compliance Programs Per Number Type

Every US number type requires its own verification before traffic flows:

- **Local 10DLC → A2P 10DLC registration:** Brand registration (EIN, business identity) + Campaign registration (use case, sample messages, opt-in flow). Trust Score determines throughput. Sole Proprietors: ~1 SMS/sec, 1 campaign. Standard: ~15+ SMS/sec, scales with secondary vetting. [A2P overview](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc) | [Quickstart](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/quickstart)

- **Toll-Free → Toll-Free Verification (TFV):** Business name, website, use case description, sample messages, opt-in type. Unverified toll-free numbers **cannot send SMS to US/Canada**. [Console onboarding](https://www.twilio.com/docs/messaging/compliance/toll-free/console-onboarding) | [Requirements](https://help.twilio.com/articles/5377174717595-Toll-Free-Message-Verification-for-US-Canada)

- **Short Code → Carrier review at purchase:** Application reviewed during 8-12 week provisioning. Available in 14 countries: US, Canada, UK, Germany, France, India, Brazil, Mexico, Argentina, Colombia, Dominican Republic, New Zealand, Spain, Sweden. [Short code guidelines by country](https://www.twilio.com/en-us/guidelines/short-code) | [What is a short code?](https://help.twilio.com/articles/223182068-What-is-a-Messaging-Short-Code-)

- **Twilio Verify → Exempt.** No registration needed — Verify handles compliance automatically.

See `twilio-compliance-onboarding` for full registration details and gotchas.

---

## How to Choose (US)

- **Need voice + SMS from same number?** → Local (10DLC) or toll-free. Short codes are SMS-only.
- **Marketing at scale (>15 SMS/sec)?** → Short code (highest throughput) or 10DLC with secondary vetting + Messaging Service number pool
- **Fastest time to send?** → Toll-free (3-5 day verification) or Twilio Verify (immediate, no registration)
- **Customer support with local presence?** → Local number in customer's area code
- **Transactional notifications?** → Toll-free (simpler registration) or 10DLC
- **Verification OTPs?** → Twilio Verify (exempt from A2P, built-in Fraud Guard)
- **Budget-constrained?** → 10DLC (lowest cost) — but plan for 10-15 day registration

---

## Non-Phone Senders

### Alphanumeric Sender IDs

A branded name (up to 11 characters) displayed instead of a phone number. **One-way only — recipients cannot reply.**

- **Not supported in the US or Canada**
- Supported in 100+ countries; some require pre-registration with documentation
- Some carriers impose minimum length — short IDs may display as "unknown"
- Add to Messaging Services for automatic sender selection by destination country

**Docs:** [Alpha Sender in Messaging Services](https://www.twilio.com/docs/messaging/services/alphanumeric-sender-ids-in-messaging-services) | [International support by country](https://help.twilio.com/articles/223133767-International-support-for-Alphanumeric-Sender-ID) | [How to register](https://help.twilio.com/articles/20153208099611-How-to-Register-an-Alphanumeric-Sender-ID)

### WhatsApp Business Senders

A phone number registered with Meta's WhatsApp Business Platform via Twilio.

- Requires WABA (WhatsApp Business Account) + sender approval
- Outbound requires pre-approved Message Templates (outside 24-hour service window)
- Direct customers: self-service Console signup or Senders API
- ISVs: Meta Tech Provider Program for customer onboarding

**Docs:** [WhatsApp hub](https://www.twilio.com/docs/whatsapp) | [Getting started](https://help.twilio.com/articles/360007721954-Getting-Started-with-Twilio-for-WhatsApp) | [Self sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up)

### RCS Agents

Branded sender with logo, rich cards, carousels, and suggested actions. Falls back to SMS automatically.

- Requires carrier-level approval per country
- Testing phase: RCS only delivers to added test devices; others get SMS fallback
- Each RCS sender can only belong to ONE Messaging Service

**Docs:** [RCS onboarding](https://www.twilio.com/docs/rcs/onboarding) | [RCS compliance guide](https://help.twilio.com/articles/49174994355355-RCS-Compliance-Onboarding-Guide) | [Regional availability](https://www.twilio.com/docs/rcs/regional)

---

## Voice Trust: Number Reputation Programs

If making outbound voice calls, these programs improve answer rates:

| Program | What it does | Carriers | Prerequisites |
|---------|-------------|----------|---------------|
| **STIR/SHAKEN** | Level A attestation = trusted caller ID | US and Canada | Trust Hub Business Profile + EIN |
| **Voice Integrity** | Remediates spam/scam labels | T-Mobile, AT&T, Verizon (coming) | Approved Business Profile + US address |
| **Branded Calling** | Shows name + logo on caller ID | T-Mobile, Verizon (Public Beta) | STIR/SHAKEN + Trust Hub profile |
| **CNAM** | Displays business name on caller ID | US long codes only (not toll-free) | EIN or DUNS number |

**Priority order:** STIR/SHAKEN first (required for Level A attestation) → Voice Integrity (spam label remediation) → Branded Calling (visual caller ID, mobile only) → CNAM (simplest, lowest impact, landlines by default).

**Docs:** [STIR/SHAKEN overview](https://www.twilio.com/docs/voice/trusted-calling-with-shakenstir) | [Voice Integrity overview](https://www.twilio.com/docs/voice/spam-monitoring-with-voiceintegrity) | [Branded Calling overview](https://www.twilio.com/docs/voice/branded-calling) | [CNAM overview](https://www.twilio.com/docs/voice/brand-your-calls-using-cnam)

### Branded Calling: Prerequisites & Display Standards

The call trust stack is layered — each product builds on the one below:

```
Layer 4: Enhanced Branded Calling  (name + logo + call reason)
         ↑ requires
Layer 3: Basic Branded Calling     (business name display)
         ↑ requires
Layer 2: Voice Integrity           (spam label remediation)
         ↑ requires
Layer 1: SHAKEN/STIR               (attestation — auto-applied with approved profile)
         ↑ requires
Layer 0: Primary Customer Profile  (Trust Hub business identity)
```

**Prerequisites for Basic Branded Calling:**
1. Approved Primary Customer Profile in Trust Hub (EIN, business name, address, authorized rep) — 1-3 business days
2. SHAKEN/STIR — automatic once profile is approved
3. Signed Letter of Authorization (LOA) for the phone numbers
4. Basic Branded Calling trust product submitted + approved — 2-4 weeks

**Additional prerequisites for Enhanced Branded Calling:**
5. Approved Voice Integrity trust product — 3-7 business days carrier propagation
6. Enhanced Branded Calling trust product — 3-6 weeks

**Phone number eligibility:**
- Local and mobile numbers only — **toll-free numbers are NOT eligible**
- Must be Twilio-owned (not ported-in numbers pending transfer)
- Calls must originate via Programmable Voice (API or TwiML) — **SIP Trunking calls are not branded**
- Each number can only belong to one Branded Calling trust product at a time

**Display standards:**

| Asset | Basic | Enhanced |
|-------|-------|----------|
| **Display name** | Business name, ~32 char carrier limit, must match Trust Hub profile | Same |
| **Logo** | N/A | Square, min 300x300px, max 1MB, PNG/JPG, no text overlays |
| **Call reason** | N/A | Free-text, ~40 char carrier display limit (e.g., "Appointment Reminder") |

**Display name rules:**
- Must match registered business name or documented trade name/DBA
- No phone numbers, URLs, or special characters
- Misleading names are rejected during review

**Call reason guidelines (Enhanced only):**
- Must accurately describe the call purpose
- Cannot be generic ("Important Call") or misleading
- Set per trust product — cannot be changed per-call
- Keep under 40 characters for consistent carrier display

**Carrier support:**
- T-Mobile: Basic + Enhanced (native)
- AT&T, Verizon: Voice Integrity spam remediation; Branded Calling display expanding
- Apple/iOS: Enhanced only, limited support

**CNAM** (traditional caller ID): 15-character limit, text-only, works on landlines, propagates in 24-48 hours, no approval process needed.

---

## International Numbers

- ~25 countries have GA (self-service) SMS numbers. Many major markets are **Private Offering** — requires a request form and 1-6 week delivery.
- MMS only available in US, Canada, and Australia. Use WhatsApp or RCS for rich media elsewhere.
- Many countries require **Regulatory Bundles** (identity/address verification) before provisioning numbers. Non-compliant numbers risk deprovisioning.

**Docs:** [Country SMS guidelines](https://www.twilio.com/en-us/guidelines/sms) | [Regulatory compliance](https://www.twilio.com/docs/phone-numbers/regulatory/getting-started) | [How to submit a bundle](https://help.twilio.com/articles/8338625205147-How-to-Submit-a-Regulatory-Bundle-for-Phone-Number-Regulatory-Compliance) | [Country regulatory requirements](https://www.twilio.com/en-us/guidelines/regulatory)


---

## CANNOT

### Phone Numbers
- **No mobile number type in the US** — `availablePhoneNumbers('US').mobile.list()` returns 404. US numbers are classified as local or toll-free only.
- **Cannot use both `voiceApplicationSid` and `voiceUrl`** — Setting one auto-clears the other. Same for `smsApplicationSid` vs `smsUrl`.
- **Cannot use `voiceApplicationSid` and `trunkSid` simultaneously** — Setting one auto-deletes the other.
- **`contains` pattern requires minimum 2 characters** — Single-character patterns return 400. Wildcards `*` mid-pattern also fail.
- **Geographic search is US/Canada only** — `nearNumber`, `nearLatLong`, `inPostalCode`, `inRegion`, `inRateCenter`, `inLata` are ignored for non-US/CA numbers.
- **No undo for number release** — Once released, the number goes back to the pool. No grace period or reclaim mechanism.
- **Address required for many international numbers** — `addressRequirements` can be `none`, `any`, `local`, or `foreign`. Purchase fails without the required address/bundle.

### Voice Trust
- **Cannot guarantee call delivery** — Carrier spam filters operate independently. Even Level A + Branded Calling + Voice Integrity can still be filtered.
- **Cannot brand inbound calls** — Branded Calling applies to outbound calls only.
- **Cannot use Voice Integrity or Branded Calling outside the US** — Voice Integrity and Branded Calling are currently US-only. STIR/SHAKEN is available in the US and Canada (CRTC-mandated since Nov 2021).
- **Cannot bypass manual approval** — Trust Hub vetting involves human review (1-3 business days for profiles, 2-6 weeks for Branded Calling).
- **Cannot preserve attestation through `<Dial>`** — CallToken forwarding requires the Calls API or Conference Participants API.
- **Cannot use Branded Calling with SIP Trunking** — Calls must originate via Programmable Voice.
- **Cannot use toll-free numbers with Branded Calling** — Local and mobile numbers only.

---

## Common Mistakes

1. **Buying numbers before understanding compliance** — Each number type has its own registration program. Choosing 10DLC means 10-15 days of A2P registration before you can send.
2. **Using local numbers for marketing without A2P** — Messages get filtered (error 30034). All US 10DLC requires A2P registration.
3. **Expecting toll-free to work immediately** — Unverified toll-free numbers cannot send SMS to US/Canada at all.
4. **Assuming MMS works internationally** — Only US, Canada, Australia. Use WhatsApp or RCS elsewhere.
5. **Choosing short code for voice** — Short codes are SMS/MMS only. No voice capability.

---

## Next Steps

- **Register your numbers:** `twilio-compliance-onboarding`
- **Set up Messaging Services with number pools:** `twilio-messaging-services`
- **Follow traffic rules after registration:** `twilio-compliance-traffic`
- **WhatsApp sender management:** `twilio-whatsapp-manage-senders`
