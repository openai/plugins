# Cloud SAML and SCIM

SAML enables single sign-on (SSO) by allowing your identity provider to authenticate users into Temporal Cloud. SCIM automatically creates, updates, and removes users and groups in Temporal Cloud based on changes in your identity provider.

Temporal-side SAML/SCIM enablement is performed by Temporal Support (internal IAM/cloud-iam), not via `tcld`.

---

## SAML SSO

SAML 2.0 integration allows you to authenticate users of your Temporal Cloud account using your organization's IdP. This enforces corporate identity policies such as multi-factor authentication (MFA) and password complexity.

SAML is included in the Business, Enterprise, and Mission Critical plans.

### Configuration overview

1. Locate your Temporal Cloud Account Id (5-6 characters after the period in your Namespace Id, e.g., `f45a2`).
2. Configure SAML with your IdP (Microsoft Entra ID or Okta).
3. Share connection information with Temporal and test the connection.

### Entity identifier format

```
urn:auth0:prod-tmprl:ACCOUNT_ID-saml
```

Example:

```
urn:auth0:prod-tmprl:f45a2-saml
```

### Callback URL format

```
https://login.tmprl.cloud/login/callback?connection=ACCOUNT_ID-saml
```

Example:

```
https://login.tmprl.cloud/login/callback?connection=f45a2-saml
```

### Sign on URL format (Entra ID only)

```
https://cloud.temporal.io/login/saml?connection=ACCOUNT_ID-saml
```

### Microsoft Entra ID configuration

1. Sign in to Microsoft Entra ID.
2. **Manage Microsoft Entra ID** > **View** > **Add > Enterprise application**.
3. **Create your own application** > name it (e.g., `temporal-cloud`) > select **Integrate any other application you don't find in the gallery**.
4. **Getting Started** > **Set up single sign on** > **SAML**.
5. In **Basic SAML Configuration**:
   - Set **Identifier (Entity ID)** to the entity identifier above.
   - Set **Reply URL (Assertion Consumer Service URL)** to the callback URL above.
   - Set **Sign on URL** to the sign on URL above.
6. In **Attributes & Claims**:
   - Set **Unique User Identifier (NameID)** to `user.userprincipalname`.
   - Set **NameID format** to `emailAddress`.
   - Ensure **Email** and **Name** are present under Additional claims.
7. Collect for Temporal: download **Certificate (Base64)** and copy **Login URL**.

### Okta configuration

1. Sign in to Okta Admin Console.
2. **Applications** > **Create App Integration** > **SAML 2.0** > **Next**.
3. Name the application (e.g., `temporal-cloud`).
4. In **Configure SAML**:
   - Set **Single sign on URL** to the callback URL above.
   - Set **Audience URI (SP Entity ID)** to the entity identifier above.
   - Set **Name ID format** to `EmailAddress`.
   - Set **Attribute Statements**: `email` and `name`.
5. In the **Feedback** section, select **Finish**.
6. On the application page > **Sign On** tab > **View SAML setup instructions**. Copy IdP settings and download the active certificate.

### Finish SAML configuration

Create a support ticket with:

- The sign-in URL from your application
- The X.509 SAML sign-in certificate (PEM or Base64 are both acceptable)
- One or more IdP domains to map to the SAML connection

The IdP domain is generally the same as your email domain. Multiple IdP domains can be provided.

After Temporal confirms configuration is complete, go to the Cloud login page, enter your email, choose **Enterprise identity**, then click **Continue**. Do **not** use **Continue with Google** or **Continue with Microsoft** for SAML SSO.

### SAML-only enforcement

Enabling SAML alone does **not** block other login methods. SAML-only is a **separate setting**, configured by Temporal Support when requested.

When SAML-only is enabled, **only** SAML login is allowed — it blocks email+password+MFA and social login (Google/Microsoft).

---

## SCIM user provisioning

SCIM lets you integrate your identity provider with Temporal Cloud to automate user provisioning and access. Changes in the IdP are reflected in Temporal Cloud:

- User creation / onboarding
- User deletion / offboarding
- User membership in groups

SCIM requires SAML. Pricing:

- **Business:** SCIM is a paid add-on (+$500/mo)
- **Enterprise / Mission Critical:** SCIM included

### Supported IdP vendors

- Okta
- Microsoft Entra ID (Azure AD)
- Google Workspace
- OneLogin
- CyberArk
- JumpCloud
- PingFederate
- Any SCIM 2.0-compliant provider

### Prerequisites

1. Configure SAML SSO first.
2. Identify your organization's IdP administrator and specify their contact details in the support ticket (that admin completes Directory Sync setup; they do not need broad Cloud admin rights for SCIM setup alone).
3. Submit a support ticket to enable SCIM.

### Cloud-managed vs SCIM-managed lifecycle

| Subject | Who manages create/delete | Who manages group membership | Who assigns Temporal roles |
|---------|---------------------------|------------------------------|----------------------------|
| **Cloud-managed users** | Cloud UI/API invite and delete, until user lifecycle management is disabled | Cloud (or SCIM if later synced into groups) | Cloud UI / `tcld` / Terraform |
| **SCIM-managed users** | IdP-owned; offboard in the IdP. Once **user lifecycle management** is disabled, Cloud UI/API can no longer create/delete users | IdP only | Roles still assigned in Cloud (directly or via synced groups) |
| **SCIM-synced groups** | IdP creates/updates/deletes groups | IdP only | Assign roles in Cloud **after** sync (UI / `tcld` / Terraform). IdP does **not** map Temporal roles |

Whether users can be added or removed from the Cloud UI/API is governed by the account-level **user lifecycle management** setting: while enabled, you can still invite and remove users outside of SCIM; once disabled, user create/delete is IdP-only. Account Roles can always be changed from the Cloud interface.

### Okta onboarding flow

1. Temporal Support enables the SCIM integration on your account. Enabling integration automatically emails a configuration link to the Okta administrator.
2. The Okta administrator opens the link, which leads to step-by-step configuration instructions.
3. Once configured, Temporal Cloud begins receiving SCIM messages and automatically onboards/offboards users and groups.

### Key behaviors

- User and group change events are applied within **10 minutes** of being made in the IdP.
- User lifecycle management with SCIM also allows user roles to be derived from group membership (roles assigned on the group in Cloud).
- Once a group has been synced in Temporal Cloud, assign roles to the group via the **Cloud UI**, **`tcld`**, or **Terraform**. See [User Group Management](https://github.com/temporalio/tcld?tab=readme-ov-file#user-group-management).
- Disabling SCIM does **not** remove already-synced users or groups.

---

## Access model context

Access to Temporal Cloud is governed by role-based access control (RBAC). Each access principal has one account-level role and optionally one or more Namespace-level permissions.

Access principals:

- **Users** — Individual user accounts
- **User Groups** — Groups for simplified access management
- **Service Accounts** — Automated access
- **Custom Roles** — Customer-defined permission sets assignable to principals

SAML and SCIM are identity integration features, not access principals.

Multiple accounts can coexist on the same email domain, each with its own SAML configuration tied to its unique Account ID. However, each email address can only be associated with a single Temporal Cloud account.

### Troubleshooting

- **Lost MFA access:** Click **Try another method** on the MFA screen. Enter your recovery code or receive a verification code via email. Then remove the authenticator via **My Profile** > **Password and Authentication** > **Authenticator App** > **Remove method** (not "reset").
- **Password reset:** If logged in: **My Profile** > **Password and Authentication** > **Reset Password**. If not logged in: enter email, click **Continue**, then **Forgot password**.
- **Email domain changes:** If your organization changed its email domain, create a support ticket with your previous and new email addresses and your Account Id.

### Common pitfalls

| Symptom / trap | Cause / fix |
|----------------|-------------|
| Social login (Google/Microsoft) still visible after SAML | SAML ≠ SAML-only. Ask Temporal Support to enable SAML-only if you need to block non-SAML methods |
| Wrong login path | Prefer **Enterprise identity** → **Continue**, or the Sign on URL with `connection=ACCOUNT_ID-saml` (Entra). Do not use Continue with Google/Microsoft for SAML |
| Stale permissions after role/group change | SCIM events apply within ~10 minutes; role/permission visibility in Cloud may lag briefly after that |
