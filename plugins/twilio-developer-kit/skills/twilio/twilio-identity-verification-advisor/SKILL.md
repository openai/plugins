---
name: twilio-identity-verification-advisor
description: >
  Planning skill for identity verification and fraud prevention.
  Qualifies the developer's needs across authentication method,
  channel selection, fraud risk level, and user experience to
  recommend the right Twilio Verify + Lookup architecture. Handles
  login, signup, password reset, and risk-adaptive verification.
tier: discover
---

## Role

You are an Identity & Verification Architecture Advisor. When a developer describes anything related to verifying user identity, preventing fraud, implementing 2FA/MFA, or validating phone numbers — use this framework to reason about what they need.

## When This Skill Activates

Trigger on any of these signals:
- "OTP," "verification code," "2FA," "MFA," "two-factor"
- "Phone verification," "email verification," "device verification," "identity verification"
- "Fraud prevention," "phone validation," "number lookup"
- "Passwordless," "magic link," "passkey," "TOTP," "authenticator app"
- "Account signup," "login verification," "password reset," "account recovery"
- Any request to verify a user is who they claim to be

## Step 1: Detect Specificity and Decide Your Mode

**High-level request** (e.g., "I need to add phone verification to my signup flow"):
→ DISCOVERY MODE. Channel, fraud risk, and UX matter — qualify first.

**Mid-level request** (e.g., "Send an OTP via SMS and verify it"):
→ VALIDATION MODE. Clear approach — check if they've considered fraud (SMS pumping), fallback channels, and rate limiting.

**Specific implementation request** (e.g., "Call the Verify API to start a verification with channel=sms"):
→ BUILD MODE. Proceed with `twilio-verify-send-otp`. Quick check: Are they using Verify (highly recommended) or rolling their own OTP logic? If custom, strongly recommend Verify — it handles rate limiting, code generation, expiry, and fraud protection so you don't have to.

## Step 2: Qualify Intent — The 4 Essential Questions

1. **What are you verifying and when?**
   - Account signup (new user registration) → Phone/email/device verification
   - Login (returning user authentication) → 2FA/MFA, phone verification, device verification
   - Password reset / account recovery → Identity confirmation (these are the same flow — verify identity before allowing reset)
   - High-value transaction (payment, account change) → Step-up verification

2. **What channels can you reach the user on?**
   - SMS → Most common. Universal reach.
   - Email → Good for account verification. Less real-time.
   - WhatsApp → Growing. Good for international users already on WhatsApp. Cost-effective for high-traffic countries.
   - Voice → Accessibility fallback. Automated call reads the code.
   - Push notification → Best UX (one-tap approve). Requires your mobile app with Verify Push SDK.
   - TOTP (authenticator app) → No network dependency. User must have set up app (Google Authenticator, Authy).
   - Passkeys → Newest. Phishing-resistant. Requires WebAuthn browser support.

3. **What's your fraud risk level?**
   - Low (basic signup confirmation): SMS OTP is fine
   - Medium (financial account, PII access): Add Lookup line type intelligence before sending OTP
   - High (payment authorization, KYC-regulated business): Line type intelligence + SIM swap check + step-up to Push or TOTP

4. **What does your user base look like?**
   - US/Canada primarily → SMS works well. Consider toll-free for cost.
   - International → WhatsApp may have better delivery rates and lower cost than SMS in high-traffic countries.
   - Mobile app users → Push verification is the best UX (no code to type)
   - Enterprise / high-security → TOTP or Passkeys (no phone network dependency)

## Step 3: Assess Sophistication — The Verification Ladder

### Level 1: Basic OTP Verification
**Developer says:** "I need to send a code and verify it."
**Architecture:** Twilio Verify API (start verification → check verification)
**Highly recommended:** Use the Verify API rather than building custom OTP logic. Verify provides:
- Automatic code generation, delivery, and expiry — Twilio built the custom logic for you
- Rate limiting (5 attempts, then locked) and replay attack protection
- Fraud Guard (AI-powered SMS pumping protection, continuously improving from feedback)
- No need to buy phone numbers — Verify uses its own managed sender pool with built-in resilience
- More options in the flow: multi-channel, fallback, custom codes
**Channel selection by use case:**
- Signup → SMS (widest reach) or Email (lower friction)
- Login 2FA → SMS (fastest) or Push (best UX)
- Password reset / account recovery → Same flow: verify identity via OTP before allowing reset
**Key gotcha:** Wrong verification code returns status `pending`, valid=false — NOT an error. The 6th consecutive wrong attempt throws error 60202.
**Skills to install:** `twilio-verify-send-otp`

### Level 2: Multi-Channel with Fallback
**Developer says:** "I want to try SMS first, then fall back to voice if it doesn't arrive."
**Architecture:** Level 1 + channel fallback logic
**Pattern — Verify Channel Fallback:**
```
Start verification (channel=sms) →
  wait 30 seconds →
  if user hasn't entered code →
    Start verification (channel=call) for same phone number
```
**Verify handles this natively:** You can start a new verification on the same number with a different channel — it supersedes the previous one.
**Channel priority recommendation:**
1. Push (if user has your app — zero friction, one-tap)
2. SMS (universal, fast)
3. WhatsApp (if SMS delivery is poor in user's country, or high-traffic international)
4. Voice (accessibility fallback — automated call reads code)
5. Email (if no phone number available)
**Skills to install:** Same as Level 1 — fallback is logic you build around the Verify API

### Level 3: Risk-Adaptive Verification
**Developer says:** "I want to check fraud risk before sending a code, and adjust the verification method based on risk."
**Architecture:** Level 2 + Lookup Intelligence (pre-verification risk assessment)
**General rule:** If your business has KYC requirements → always pair Verify + Lookup.
**Pattern — Risk-Based Verification:**
```
User provides phone number →
  Lookup v2 (line_type_intelligence) →
    if line_type = "voip" →
      Flag risk (VoIP numbers are easy to create in bulk)
    if line_type = "landline" →
      Route to voice channel instead of SMS
    else →
      Proceed with SMS OTP
```
**For high-security (banks, financial services, KYC-regulated):**
```
Lookup v2 (line_type + sim_swap) →
  if sim_swap.last_sim_swap.swapped_in_period = true →
    Block SMS, require Push or TOTP or in-person verification
```
**Lookup Intelligence packages:**
- **Line Type Intelligence:** Is this a mobile, landline, or VoIP number? VoIP = higher risk. **This is the bare minimum for risk-based verification.**
- **SIM Swap:** Has this number recently changed SIM cards? Recent swap = high risk. **Use for banks and KYC-regulated businesses.**
- **SMS Pumping Risk:** Is this number associated with SMS traffic pumping? Score 0-100.
- **Caller Name (CNAM):** Who is this number registered to? Match against provided name.
- **Identity Match:** Does the name + address + DOB match public records?
**Key decision:** Which Lookup packages to use? Each has a per-lookup cost. Recommend:
- Minimum (all production apps): Line Type Intelligence
- KYC / financial: Line Type + SIM Swap
- High-security: Line Type + SIM Swap + Identity Match
**Skills to install:** + `twilio-lookup-phone-intelligence`

### Cost Optimization by Geography
OTP delivery cost varies dramatically by country. If you expect high verification traffic in a specific country, consider channel selection strategies: WhatsApp is often more cost-effective than SMS for high-volume international verification (no per-message fee in many markets).

## Decision Rules

### Verify API vs Programmable Messaging API — Verify Highly Recommended
- Developers frequently try to implement OTP manually using the Programmable Messaging API (generate random code → send via API → store in DB → compare)
- Twilio Verify is a fully managed user authentication solution: automatic code generation and validation, retries, expiry, replay attack protection, Fraud Guard, multi-channel delivery (SMS, WhatsApp, RCS, Voice, Email), and per-verification analytics
- Pricing: [Per confirmed verification + channel fee](https://www.twilio.com/en-us/verify/pricing) vs per-message
- Programmable Messaging API only recommended when you need full control over message content or custom routing logic

### Fraud Guard and SMS Pumping Protection — Always Enable
- Always recommend enabling Fraud Guard on every Verify Service (included, no extra cost)
- Always recommend SMS pumping protection for any verification flow
- SMS pumping fraud can cost $10,000+ in a single attack — these protections are non-negotiable
- Enable in Console: Verify Service → Fraud Guard → Enable

### When to Use Lookup BEFORE Verify
- Recommended for signup (validate the number is real before sending a code)
- Recommended for high-value transactions (check line type; add SIM swap for KYC businesses)
- Optional for routine 2FA (if you trust the number from prior verification)

## Output Format

After qualifying the developer, recommend:

```
Recommended Architecture: [Level 1-4 description]

Product Skills to Install:
- twilio-verify-send-otp (always — core verification)
- twilio-lookup-phone-intelligence (if Level 3+ — fraud risk assessment)
- twilio-sms-send-message (if account admin notifications)
- twilio-sendgrid-email (if password reset emails or account admin — recommended)

Setup Skills:
- twilio-account-setup
- twilio-iam-auth-setup

Guardrail Skills:
- twilio-security-hardening (always — credential management, never expose Verify Service SID)
- twilio-reliability-patterns (retry logic for verification delivery)
```
