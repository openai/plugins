---
name: twilio-organizations-setup
description: >
  Set up and manage Twilio Organizations for centralized account and user
  governance. Covers the Organization > Account > Subaccount hierarchy,
  roles (Owner/Admin/Standard), managed vs independent accounts, domain
  registration, SSO enforcement, SCIM provisioning, and Organization
  merging. Use this skill when managing multiple Twilio accounts or users
  across teams.
---

## Overview

Every Twilio customer automatically gets an Organization when they sign up (auto-created since May 2024 for new signups; since June 2024 for existing paying customers). An Organization is the top-level container that groups accounts, users, and security policies. The creation has no effect on existing account functionality. Most developers never need to touch it — but as soon as you have multiple accounts, teams, or compliance requirements (SSO, HIPAA), Organization setup becomes essential.

**Hierarchy:** Organization > Accounts > Subaccounts

| Layer | What it is | When you need it |
|-------|-----------|-----------------|
| **Organization** | Centralized governance: users, accounts, domains, SSO | Multiple teams or accounts, SSO, HIPAA designation |
| **Account** | Application boundary: all Twilio products, resources, billing live here | Always — you need at least one |
| **Subaccount** | Isolated partition under an account: separate resources, consolidated billing | Multi-tenant apps, per-customer isolation |

---

## Organization vs Subaccount — When to Use Which

| Dimension | Organization (Managed Accounts) | Subaccounts |
|-----------|----------------------------------|-------------|
| **Management** | Console UI + Organizations API | REST API (`/2010-04-01/Accounts`) |
| **Billing** | Independent per account | Consolidated to parent account |
| **Account limit** | 10 per Organization (default) | 1 per unupgraded account; 1,000 per upgraded account (contact AE for more) |
| **User management** | Full lifecycle: invite, roles, SSO, SCIM | None — no user concept |
| **SSO/SCIM** | Supported | Not applicable |
| **HIPAA designation** | Per-account toggle in Admin console | Inherits from parent (new only) |
| **Resource isolation** | Separate accounts, separate credentials | Separate but parent can access all |
| **Cost** | Free | Free |

**Rule of thumb:** Use **Organizations** when different teams/users need separate billing and access control. Use **Subaccounts** when your application needs programmatic multi-tenant isolation with consolidated billing.

---

## Organization Roles

| Role | Capabilities | Limit |
|------|-------------|-------|
| **Owner** | Full control + sole authority to delete the Organization | 1 per Organization |
| **Administrator** | Invite/remove users, add/create accounts, modify settings | Unlimited |
| **Standard User** | Access only to specified accounts — no org management | Unlimited (default) |

The Organization creator is automatically assigned the Owner role.

---

## Setting Up Your Organization

### Find Your Organization

All Twilio customers have an Organization (auto-created at signup). Access it via:

- **Console > Settings** (gear icon) — shows Organization settings, or
- **Twilio Admin** link in the top-right navigation — opens the Organization admin panel

### Add Accounts to Your Organization

**Create a new account:**
1. Console > Admin > Accounts
2. Click **Create New Account**
3. Name the account, select Twilio or Flex usage
4. Confirm — the account starts in trial mode with fresh defaults

**Import an existing account:**
1. Console > Admin > Accounts > **Add Existing Account**
2. Enter the account's SID (find it in Console > Account > General settings)
3. The account owner receives an email and must confirm

**Requirement:** The account owner's email must match your Organization's verified domain.

### Account Types

| Type | Description |
|------|-------------|
| **Managed** | Owned by your Organization — full lifecycle control |
| **Independent** | External account your users can access — you do NOT control it |
| **Pending** | Added but awaiting owner confirmation |

### Transfer Account Ownership

Only between managed users in the same Organization:
1. Console > Admin > Accounts > select account
2. Remove current owner, enter new owner's email or User SID
3. Save

---

## Domain Registration

Register your company's email domain to control how employees interact with Twilio.

**Console > Admin > Domains**

| Setting | Behavior |
|---------|----------|
| **Restricted** | Users with your domain email can't sign up unless explicitly invited |
| **Auto-enrollment** | Users who sign up with your domain automatically join your Organization |
| **Blocked** | Users with your domain email cannot join this Organization |

Domain registration also enables Organization merging — the Prime org must have verified domains.

**Important:** Common domains (gmail.com, hotmail.com, etc.) cannot be verified — you cannot invite users from common domains. Enter domains without "www." (e.g., `corporate.com`, not `www.corporate.com`). You can verify the same domain under multiple Organizations (with restrictions) or use subdomains (`stage.corporate.com`).

---

## SSO and SCIM

- **SSO:** Enforce Single Sign-On at the Organization level via your identity provider (Okta, Azure AD, etc.). See [SSO docs](https://www.twilio.com/docs/iam/organizations/sso).
- **SCIM:** Automate user provisioning and deprovisioning via the SCIM 2.0 API. See [SCIM docs](https://www.twilio.com/docs/iam/organizations/scim).

When SSO is enabled on a verified domain, all users with that domain email must authenticate via SSO.

---

## Organization Merging

Combine two Organizations: the **Prime** absorbs the **Candidate**.

**Requirements:**
- Prime must have verified domains
- Candidate Owner's email must match Prime's verified domain
- Candidate must have NO verified domains of its own

**Post-merge:** Candidate ceases to exist. All accounts and users transfer to Prime. Billing and functionality unchanged. If Prime has SSO enabled, it applies to merged users.

---

## HIPAA Designation

Requires an executed BAA with Twilio. After BAA:

1. Console > Admin > Accounts > select account
2. Enable HIPAA flag
3. Save

**Each account must be individually flagged** — existing accounts do NOT auto-inherit. New accounts created after designation DO inherit. See `twilio-security-compliance-hipaa` for full HIPAA guidance.

---

## User Management

**Users are separate from accounts.** A user is defined by their login (email + password) and can own or have access to many accounts.

- **Users can only belong to ONE Organization** — if they need access to multiple orgs, create a dedicated user per org (e.g., `user+org1@corporate.com`)
- **Owner's accounts are auto-added** — any account owned by the Organization Owner is automatically added to that Organization and cannot be "independent"
- **New accounts by managed users are auto-added** — accounts created by any managed user (Owner, Admin, Standard) automatically join the Organization
- **New user signup behavior** is controlled by domain settings (Restricted/Auto-enrollment/Blocked)

**Admin actions for managed users:**
- **Reset password:** Admin Center > Users > Managed Users > select user > Reset Password (logs out user, sends 24-hour reset link)
- **Reset 2FA:** Admin Center > Users > Managed Users > select user > Reset 2FA (removes current 2FA number, prompts for new one on next login)
- **Bulk user import:** Available via Admin Center (contact Support if not enabled on your Organization)

---

## CANNOT

- **Cannot create accounts via API at the Organization level** — Account creation within Organizations is Console-only. Subaccount creation via REST API is separate and lives under the parent account.
- **Cannot close or delete an Organization from Console** — There is no self-service delete. To remove an Organization, merge it into another one.
- **Cannot transfer ownership to an independent user** — Account ownership transfers are restricted to managed users within the same Organization.
- **Cannot merge Organizations if the Candidate has verified domains** — Remove Candidate's domain verification first, or the merge will fail.
- **Cannot assume configurations transfer to new accounts** — New managed accounts start with fresh defaults. Product configurations, phone numbers, and settings do not inherit.
- **Cannot manage independent accounts' lifecycle** — You can grant your users access to independent accounts, but you cannot close, suspend, or modify them.
- **Cannot have multiple Owners per Organization** — Exactly one. Transfer ownership before the current Owner leaves the company.
- **A user cannot belong to multiple Organizations** — One user = one Organization. Use email aliases for multi-org access.
- **Cannot verify common email domains** — gmail.com, hotmail.com, etc. are not supported for domain verification or user invitations.
- **Cannot invite users from unverified domains** — Domain must be verified first before you can invite users with that domain email.
- **Billing is NOT consolidated at the Organization level** — Each managed account is billed independently. For consolidated billing, use subaccounts under a single parent account instead.

---

## Next Steps

- **Account and subaccount setup:** `twilio-account-setup`
- **Authentication methods (API Keys, OAuth2):** `twilio-security-api-auth`
- **HIPAA account configuration:** `twilio-security-compliance-hipaa`
- **Credential security:** `twilio-security-hardening`
- **Docs:** [Organizations overview](https://www.twilio.com/docs/iam/organizations) | [Managed accounts](https://www.twilio.com/docs/iam/organizations/managed-accounts)
