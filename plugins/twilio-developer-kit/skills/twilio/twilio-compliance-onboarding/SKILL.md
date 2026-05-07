---
name: twilio-compliance-onboarding
description: >
  Registrations required BEFORE Twilio traffic works. Covers messaging
  programs (A2P 10DLC, toll-free verification, WhatsApp WABA, RCS, short
  code, alphanumeric sender) and voice trust programs (STIR/SHAKEN, Voice
  Integrity, Branded Calling, CNAM). Each number/sender type has its own
  program — registration blocks traffic until complete.
---

## Overview

Most Twilio channels require registration or approval before traffic flows. **Skipping this step is the #1 onboarding mistake** — developers build first, then discover messages are blocked or calls labeled as spam.

**Lifecycle:** Choose numbers/senders (`twilio-numbers-senders`) → Register them (this skill) → Follow traffic rules (`twilio-compliance-traffic`)

---

## Decision Tree: What Do I Need to Register?

### Messaging Programs

| Sender type | Registration program | Timeline | Docs |
|-------------|---------------------|----------|------|
| US local (10DLC) | **A2P 10DLC** — brand + campaign | Brand: minutes. Campaign: 10-15 business days | [Overview](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc) \| [Quickstart](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/quickstart) |
| US toll-free | **Toll-free verification** | 3-5 business days | [Console onboarding](https://www.twilio.com/docs/messaging/compliance/toll-free/console-onboarding) \| [Requirements](https://help.twilio.com/articles/5377174717595-Toll-Free-Message-Verification-for-US-Canada) |
| US short code | **Pre-approved at purchase** | 8-12 weeks provisioning | [Guidelines by country](https://www.twilio.com/en-us/guidelines/short-code) \| [What is a short code?](https://help.twilio.com/articles/223182068-What-is-a-Messaging-Short-Code-) |
| WhatsApp | **WABA + Meta Business Verification** | Minutes (sender) + weeks (Meta verification) | [Self sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up) \| [Getting started](https://help.twilio.com/articles/360007721954-Getting-Started-with-Twilio-for-WhatsApp) |
| RCS | **Google + carrier approval** | 4-6 weeks minimum, longer multi-region | [RCS onboarding](https://www.twilio.com/docs/rcs/onboarding) \| [Compliance guide](https://help.twilio.com/articles/49174994355355-RCS-Compliance-Onboarding-Guide) |
| Alpha Sender ID | **Registration in some countries** | Varies by country | [How to register](https://help.twilio.com/articles/20153208099611-How-to-Register-an-Alphanumeric-Sender-ID) |
| International numbers | **Regulatory bundle** (many countries) | Varies | [Getting started](https://www.twilio.com/docs/phone-numbers/regulatory/getting-started) \| [How to submit](https://help.twilio.com/articles/8338625205147-How-to-Submit-a-Regulatory-Bundle-for-Phone-Number-Regulatory-Compliance) |
| Twilio Verify | **Exempt** — no registration needed | Immediate | — |

### Voice Trust Programs

| Program | What it does | Vetting timeline | Docs |
|---------|-------------|-----------------|------|
| **STIR/SHAKEN** | Level A attestation = trusted caller ID | 24hr (Business Profile) + 72hr (Trust Product) | [Overview](https://www.twilio.com/docs/voice/trusted-calling-with-shakenstir) \| [Onboarding](https://www.twilio.com/docs/voice/trusted-calling-with-shakenstir/shakenstir-onboarding) |
| **Voice Integrity** | Registers numbers with carriers to remediate spam labels | 24-48hr (profile) + 24-48hr (remediation) | [Overview](https://www.twilio.com/docs/voice/spam-monitoring-with-voiceintegrity) \| [Onboarding](https://www.twilio.com/docs/voice/spam-monitoring-with-voiceintegrity/voice-integrity-onboarding) |
| **Branded Calling (US)** | Verified name + logo on mobile caller ID | Public Beta (T-Mobile, Verizon) | [Overview](https://www.twilio.com/docs/voice/branded-calling) \| [FAQ](https://help.twilio.com/articles/22312096414363-Branded-Calls-FAQ) |
| **Branded Calling (Non-US)** | Verified caller ID branding for international numbers | Availability varies by country/carrier | [Overview](https://www.twilio.com/docs/voice/branded-calling) |
| **CNAM** | Business name on outbound caller ID | 48-72hr propagation | [Overview](https://www.twilio.com/docs/voice/brand-your-calls-using-cnam) \| [Getting started](https://help.twilio.com/articles/360051670533-Getting-Started-with-CNAM-Caller-ID) |

**Voice trust priority:** STIR/SHAKEN first (required for Level A attestation) → Voice Integrity (spam label remediation) → Branded Calling (mobile only, beta) → CNAM (simplest, lowest impact). All voice programs require an approved Trust Hub Business Profile as prerequisite.

---

## A2P 10DLC — Deep Dive

A2P 10DLC is the most common program and the most common source of onboarding delays.

### Registration Flow

1. **Create Customer Profile** — Business identity in Trust Hub (required for all programs)
2. **Register Brand** — EIN, business name, address, website. TCR typically approves within minutes. Respond to OTP verification within 24 hours. [Brand best practices](https://help.twilio.com/articles/4405758341659-A2P-10DLC-Brand-Approval-Best-Practices)
3. **Register Campaign** — Use case, 2+ sample messages, opt-in proof, privacy policy. Review takes 10-15 business days. [Campaign best practices](https://help.twilio.com/articles/11847054539547-A2P-10DLC-Campaign-Approval-Best-Practices)
4. **Associate phone numbers** — Link numbers to campaign via Messaging Service

### Message Flow (Opt-In Documentation)

The message flow field is the #1 reason campaigns get rejected. Reviewers click your links and follow your opt-in steps. If submitting via API, the field must be 40–2049 characters.

**4 required elements:**
1. Description of opt-in method(s) with clear language inviting users to sign up (no pre-checked boxes)
2. Message frequency (e.g., "Up to 4 msgs/month")
3. "Message and data rates may apply" disclosure
4. Link(s) to opt-in image/mockup (must be publicly accessible)

**Example of a strong message flow:**
> "Customers opt in by texting JOIN to 55555, or by checking the SMS opt-in box during checkout at shop.acme.com. The checkout page displays: 'Check this box to receive exclusive deals via text. Up to 4 msgs/month. Message and data rates may apply. Reply STOP to opt out. Reply HELP for help. Privacy Policy: acme.com/privacy. Terms: acme.com/tc.' In-store signage also promotes keyword opt-in with full disclosures. Screenshot of signage: [Google Drive link]"

**How to document opt-in by scenario:**
| Scenario | What to provide |
|----------|----------------|
| Public website form | URL to your sign-up page |
| Form behind login/paywall | Screenshot uploaded to Google Drive/OneDrive (set to "anyone with link"), include public link |
| Verbal/phone opt-in | Full script of what you say and how customer confirms consent |
| Paper form | Scan/photograph the form, upload publicly, include link |
| Text keyword campaign | Screenshot of marketing materials showing keyword, upload publicly |

**All links must be publicly accessible.** Non-English disclosures need a translated version included.

### Consent Requirements

Three tiers of consent (CTIA guidelines):

| Tier | Required for | How to obtain |
|------|-------------|---------------|
| **Implied consent** | Transactional messages (order confirmations, account alerts) | Customer provides phone number during a transaction |
| **Express consent** | Informational messages (appointment reminders, service updates) | Customer actively opts in (checkbox, keyword, form) |
| **Express written consent** | Marketing/promotional messages | Signed consent with brand name, message frequency, "Msg & data rates apply," opt-out instructions |

**Critical rules:**
- Consent is per-campaign. Signing up for order updates does NOT grant consent for promotions. Separate opt-ins required.
- Consent must be voluntary. If customers must opt in to messaging to complete a purchase or create an account, the registration **will be rejected**.
- Brand name must appear in the consent disclosure — generic "you agree to receive texts" is insufficient.

### Privacy Policy & Terms and Conditions

Both are required. Registrations without them are rejected.

**Privacy policy must include:**
- What data you collect and how it's used
- That mobile information will NOT be shared with third parties for marketing (CTIA requirement)

**Terms and conditions must include:**
- Program/brand name and description
- "Message and data rates may apply"
- Message frequency or recurring message disclosure
- Customer support contact information
- **HELP and STOP opt-out instructions (displayed in bold)**
- Link to privacy policy
- "Carriers are not liable for any delayed or undelivered messages"

**Pro tip:** Create messaging-specific privacy policies and terms rather than updating your main company documents. Dedicated policies are easier to keep current if requirements change.

### Mixed Use Case Campaigns

If you send both marketing and transactional messages (e.g., order confirmations AND promotions), use the **Mixed** campaign use case:

- Select "Mixed" as the campaign use case during registration
- Allows 2-5 sub-use cases within one campaign (e.g., Customer Care, Marketing, Account Notification, 2FA, PSA)
- Describe each sub-use case clearly in the campaign description
- Sample messages must cover each declared sub-use case

**Do NOT register separate campaigns** for each message type unless they use different phone numbers or have different opt-in flows. Mixed is the intended solution for multi-purpose messaging from the same sender.

### Campaign Rejection Gotchas

| Field | Common mistake | Correct approach |
|-------|---------------|-----------------|
| Campaign description | Vague ("We send texts") | Specific ("Order confirmation and shipping updates for e-commerce purchases") |
| Sample messages | Don't match description or missing opt-out | Must reflect declared use case + include opt-out in every sample |
| Opt-in description | "Users sign up on our website" | "Users check SMS consent checkbox during account registration at checkout.example.com" with link to screenshot |
| URL shorteners | Using bit.ly links | Public URL shorteners are forbidden — use branded/vanity domains |
| Privacy policy | States data IS shared | Must state data is NOT shared with third parties |
| Links | Behind login or not accessible | All links must be publicly accessible to reviewers |
| Consent | Single opt-in covering all message types | Each sub-use case in a Mixed campaign still needs its own documented opt-in method |
| Mixed campaign | Leaving sub-use cases undescribed | Each sub-use case must be explained in description |

Failed campaigns can now be edited directly in Console (API editing is private beta).

### Registration Tiers

| Tier | Daily segment limit (T-Mobile) | Notes |
|------|-------------------------------|-------|
| Sole Proprietor | ~1,000/day | Console only, 1 campaign, 1 number |
| Low-Volume Standard | ~2,000/day | Requires EIN |
| Standard | 2,000+ (scales with Trust Score) | Requires verified EIN |
| High-volume (secondary vetting) | 200,000+/day | [Secondary vetting](https://help.twilio.com/articles/4403988619163-Secondary-Vetting-for-A2P-10DLC) |

Russell 3000 companies qualify for 200,000 segments/day automatically.

### Common Errors

| Error | Meaning | Fix |
|-------|---------|-----|
| `30034` | Message from unregistered number | Complete A2P registration |
| `30007` | Message filtered as spam | Check opt-in compliance and content |
| Brand rejected | Business info doesn't match EIN records | Tax ID and business name must match exactly |

---

## Toll-Free Verification

Required for US/Canada toll-free SMS. Simpler than A2P 10DLC.

- Submit via Console (Active Numbers → Regulatory Information tab) or [API](https://www.twilio.com/docs/messaging/compliance/toll-free/api-onboarding)
- Requires: paid account, Customer Profile, business name, website, use case description, sample message, opt-in type
- **Unverified toll-free numbers cannot send SMS to US/Canada** — status shows "Restricted"
- If rejected: resubmit within 7 days for priority review. After 7 days, number reverts to Restricted and resubmission goes to back of queue
- ISVs must have an approved Primary Business Profile before submitting for secondary customers
- 527 political organizations require Campaign Verify tokens before Console submission
- Don't use multiple toll-free numbers for the same use case ("snowshoeing")

**Docs:** [Console onboarding](https://www.twilio.com/docs/messaging/compliance/toll-free/console-onboarding) | [Why rejected?](https://help.twilio.com/articles/9321443984155-Why-Was-My-Toll-Free-Verification-Rejected-)

---

## WhatsApp WABA Registration

### Self-Signup Flow (Direct Customers)

1. Console → Messaging → Senders → WhatsApp Senders → "Create new sender"
2. Select phone number (Twilio or non-Twilio — must not already be registered with WhatsApp)
3. Click "Continue with Facebook" → Meta Embedded Signup popup
4. Create or select Meta Business Portfolio
5. Create or select WABA (all senders on same Twilio account must share one WABA)
6. Set display name, category, description — Meta reviews display name post-registration
7. Phone verification via OTP (SMS or voice)
8. Registration completes within minutes

### Post-Registration Requirements

- **Meta Business Verification required** before production messaging — can take several weeks
- If display name rejected by Meta, messaging is limited to 250 messages/24 hours
- Outbound messages require pre-approved **Message Templates** (submitted to Meta, 24-48hr approval)
- Free-form messages only within 24-hour service window after customer initiates

### ISV Path

Enroll in Meta's **Tech Provider Program** to onboard customers. Different flow from self-signup.

**Docs:** [Self sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up) | [WhatsApp hub](https://www.twilio.com/docs/whatsapp)

---

## RCS Onboarding

4-6 weeks minimum. RCS has a detailed 7-part compliance process covering sender profile, privacy/ToS, eligibility, campaign details, opt-in/consent, sample messages, and common rejection reasons.

**See `twilio-rcs-messaging` for the full onboarding guide, sending patterns, and device support.**

Quick summary: Create RCS Sender in Console → complete compliance submission → Twilio specialist reviews → Google + carrier approval → add to Messaging Service → go live.

**Docs:** [RCS onboarding](https://www.twilio.com/docs/rcs/onboarding) | [Compliance guide](https://help.twilio.com/articles/49174994355355-RCS-Compliance-Onboarding-Guide) | [Regional availability](https://www.twilio.com/docs/rcs/regional)

---

## CANNOT

- **Cannot skip A2P registration for US 10DLC** — Mandatory for all senders, no exceptions for small volume
- **Cannot register Sole Proprietor A2P via API** — Console only
- **Cannot combine unrelated use cases without Mixed campaign** — Use the "Mixed" use case category to register 2-5 sub-use cases under one campaign
- **Cannot require A2P registration for Verify traffic** — Twilio Verify is exempt from A2P registration
- **Cannot use voice trust programs without Trust Hub** — All voice programs require an approved Trust Hub Primary Customer Profile
- **Cannot use Branded Calling on landlines** — Mobile-only. US: Public Beta (T-Mobile, Verizon). Non-US: availability varies by country and carrier — check eligibility for your specific numbers. Use CNAM for landlines.

---

## Next Steps

- **Channel overview and onboarding guide:** `twilio-messaging-overview`
- **Choose the right number type first:** `twilio-numbers-senders`
- **Follow traffic rules after registration:** `twilio-compliance-traffic`
- **Set up Messaging Services for number pools:** `twilio-messaging-services`
- **Send SMS after registration:** `twilio-sms-send-message`
- **Secure your account:** `twilio-security-hardening`
