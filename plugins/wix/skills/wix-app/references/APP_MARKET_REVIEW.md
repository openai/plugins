# Wix App Market Review

Use this reference when preparing a Wix CLI app for App Market submission,
auditing review feedback, or checking whether an implementation is likely to
pass technical review. Keep the review evidence-based: classify what the app
actually does, then mark each relevant requirement as `Confirmed`,
`Not applicable`, or `Needs confirmation`.

This page covers code-facing and repository-verifiable requirements. App
Dashboard, pricing-page setup, company profile, and listing-copy checks require
separate dashboard or listing verification unless the user provides direct
evidence.

---

## Review Workflow

1. Identify the app surfaces first: billing model, auth/password usage, cookie
   usage, extension types, live-site surfaces, dashboard/setup surfaces, Wix
   business-solution dependencies, and webhooks.
2. Start with a report-only pass. List confirmed gaps, why they matter, and
   official Wix documentation links where available.
3. Do not mark a requirement as missing unless code, config, user statements,
   runtime behavior, or explicit absence supports that finding. Otherwise mark
   it `Needs confirmation`.
4. Before flagging secrets, config leakage, or similar security issues, verify
   the exposure is in a tracked file, the current diff, build artifacts, or
   another review-relevant surface. Do not treat a local-only workspace file by
   itself as repository exposure.
5. Do not infer app billing configuration from Wix Business Solutions Pricing
   Plans SDK/API usage. Business-solution Pricing Plans are for a Wix user
   selling plans to customers; App Billing/App Plans are for charging site
   owners for the app.
6. For any code-facing gap the user asks you to fix, implement the fix through
   the relevant `wix-app` extension reference first, then run validation.

## Expected Output

Group findings by priority:

- Technical blockers: confirmed issues that are likely decline reasons.
- Should-fix items: high review risk, but not enough evidence to call them
  definite decline reasons.
- Nice-to-have hardening: improvements that reduce risk without blocking
  submission.
- Needs confirmation: requirements that cannot be verified from available
  evidence.

For each finding include:

- `Applicability`
- `Evidence`
- `Impact`
- `Recommended fix`
- `Verification`
- `Confidence`

Preserve qualifiers from the taxonomy and docs. Do not upgrade `recommended`,
`if applicable`, or surface-specific guidance into a universal requirement.

---

## Technical Checklist

Work through this before submission. Only applicable unchecked items are
potential decline reasons.

### Billing and Payments

- [ ] All in-app purchases route through Wix Billing unless Wix explicitly
      approved the app as Partner Billed; approved Partner Billed apps report
      charges through External Billing Events.
- [ ] No external purchase buttons, links, QR codes, license keys, or other
      custom mechanisms unlock paid content.
- [ ] Full checkout flow tested for every plan.
- [ ] If the app has premium features, there is a clear in-product upgrade link
      or CTA.
- [ ] Credits do not expire.

### Setup and Access

- [ ] App configuration URLs are public and do not use localhost.
- [ ] A usable setup/settings UI exists. Embedded Script apps need a dashboard
      page.

### Instance and Identity

- [ ] `instanceId` is used for user/site identification, not cookies or sessions.
- [ ] Billing is separated per `instanceId`.
- [ ] Auto-login works when the user reopens the app from Manage Apps.
- [ ] Site duplication is handled through `originInstanceId`: treat the copied
      site as a new install linked to the original and copy applicable
      settings/content where possible.
- [ ] Required Wix apps, such as Stores or Bookings, are checked through Get App
      Instance and surfaced clearly if missing.
- [ ] If the app supports Wix Stores catalog data, both Catalog V1 and Catalog
      V3 are supported. See [STORES_VERSIONING.md](STORES_VERSIONING.md).

### Webhooks

- [ ] Any implemented webhook returns HTTP 200 on successful receipt.
- [ ] App Installed and App Removed webhooks are considered for lifecycle
      provisioning and cleanup. They are recommended, not a universal hard
      requirement.

### Permissions

- [ ] Only minimum required permissions are requested.
- [ ] Redundant or overlapping permissions are removed.

### Security

- [ ] Signed `instance` verification happens server-side before trusting
      user/site context.
- [ ] Signed-instance-backed edit/save actions validate `signDate`; stale
      signatures require refresh before continuing.
- [ ] All endpoints are HTTPS with no HTTP fallback.
- [ ] In-product flows avoid `alert()` and `confirm()`; use Wix modal,
      inline status, toast, or another surface-appropriate feedback pattern.
- [ ] XSS protection covers all user input fields.
- [ ] Passwords are stored as salted hashes, such as bcrypt or SHA-256 with a
      unique salt per password.
- [ ] Password reset uses an expiring email link and never sends raw passwords.
- [ ] Sensitive data is not stored in cookies and is encrypted where needed.

### UX and Display

- [ ] In-product flows use Wix popup/modal patterns where appropriate.
      OAuth and documented Wix pricing-page upgrade CTAs are exceptions.
- [ ] First install shows realistic demo data, not placeholder lorem ipsum.
- [ ] Ads are not shown to site visitors unless ad display is the app purpose
      and the app has the required permits.
- [ ] Review prompts, if present, are non-blocking and do not force or
      incentivize reviews.
- [ ] Plugin content relates to the host app's core functionality.

### Performance and Quality

- [ ] Startup and load times meet App Market expectations.
- [ ] No known bugs or console errors remain.
- [ ] Supported-browser matrix is tested.
- [ ] Live-site extensions are responsive across screen sizes.
- [ ] Dashboard surfaces support the required desktop layout.

### SEO, Accessibility, and Localization

- [ ] Widget components do not render `<h1>` tags.
- [ ] User-facing images expose alt-text customization where applicable.
- [ ] App output is UTF-8 encoded.
- [ ] Website components meet accessibility standards.

### Cookie Consent

- [ ] Cookie consent workflow activates/deactivates cookies per visitor
      preferences.

---

## Implementation Notes

### Payment and Billing

All apps that collect money must route payments through Wix Billing unless Wix
granted a formal exception. Approved Partner Billed apps still need to report
charges/refunds through External Billing Events and submit revenue reports.

| Requirement | Notes | Docs |
| --- | --- | --- |
| Implement Wix Billing (#25) | Use Billing API for subscriptions unless Wix approved Partner Billing. | [App Billing APIs](https://dev.wix.com/docs/api-reference/app-management/app-billing/introduction) |
| No custom unlock mechanisms (#29, #30) | Content gating and purchase flows must go through Wix Billing only. | [Billing API](https://dev.wix.com/docs/api-reference/app-management/app-billing/billing/introduction) |
| Test checkout per plan (#33) | Verify purchase, upgrade, cancellation, and entitlement UX. | [Billing sample flows](https://dev.wix.com/docs/api-reference/app-management/app-billing/billing/sample-flows) |
| Upgrade path (#125) | Premium features need a clear upgrade link or CTA. Do not treat Business Solutions Pricing Plans SDK usage as evidence for app billing decisions. | [Identify and Manage App Users](https://dev.wix.com/docs/build-apps/launch-your-app/pricing-and-billing/identify-and-manage-app-users) |
| Usage-based or one-time charges | Billing API handles subscriptions; use Custom Charges for other approved billing flows. | [Custom Charges Service Plugin](https://dev.wix.com/docs/api-reference/app-management/app-billing/custom-charges-service-plugin/introduction) |
| Partner Billed reporting | Required only for apps with written approval from Wix. | [External Billing Events API](https://dev.wix.com/docs/api-reference/app-management/app-billing/external-billing-events/introduction) |

### App Instance and Identity

The `instanceId` uniquely identifies an app installation on a site. Use it for
identity, app data, and billing. Site duplication creates a new `instanceId`;
use `originInstanceId` to relate the copied site to the original.

| Requirement | Notes | Docs |
| --- | --- | --- |
| Identify by `instanceId` (#115) | Each site installation gets a unique ID. | [App Instance API](https://dev.wix.com/docs/api-reference/app-management/app-instance/introduction) |
| Separate billing per site (#116) | One plan must not silently unlock multiple sites. | [App Instance API](https://dev.wix.com/docs/api-reference/app-management/app-instance/introduction) |
| Auto-login (#118) | Restore the app session from the current site instance. | [Get App Instance](https://dev.wix.com/docs/api-reference/app-management/app-instance/get-app-instance) |
| Check required apps (#120) | Verify required Wix apps and show clear setup guidance if missing. | [Get App Instance](https://dev.wix.com/docs/api-reference/app-management/app-instance/get-app-instance) |
| Site duplication (#122) | Copy relevant settings/content to the new instance where possible. | [App Instance API](https://dev.wix.com/docs/api-reference/app-management/app-instance/introduction) |
| Stores catalog compatibility (#130) | Support both Catalog V1 and Catalog V3. | [Catalog Versioning API](https://dev.wix.com/docs/api-reference/business-solutions/stores/catalog-versioning/introduction) |

### Webhooks, Setup, and Permissions

| Requirement | Notes | Docs |
| --- | --- | --- |
| App lifecycle webhooks (#113) | Recommended for provisioning and cleanup; if implemented, return HTTP 200. | [App Instance Installed](https://dev.wix.com/docs/api-reference/app-management/app-instance/app-instance-installed) |
| Webhook success response (#114) | Any implemented webhook must return HTTP 200 on successful receipt. | [App Instance Removed](https://dev.wix.com/docs/api-reference/app-management/app-instance/app-instance-removed) |
| Settings/setup UI (#107) | Provide a dashboard page, widget, or another relevant setup surface. Embedded Script apps need a dashboard page. | [About Extensions](https://dev.wix.com/docs/build-apps/develop-your-app/extensions/about-extensions) |
| No localhost URLs (#108) | App configuration URLs must be public. | [Self-hosted dashboard extensions](https://dev.wix.com/docs/build-apps/develop-your-app/frameworks/self-hosting/supported-extensions/dashboard-extensions/add-self-hosted-dashboard-page-extensions) |
| Minimum permissions (#111, #112) | Request only scopes used by app functionality and remove overlap. | [App Permissions API](https://dev.wix.com/docs/api-reference/app-management/app-permissions/introduction) |

### Security

| Requirement | Notes | Docs |
| --- | --- | --- |
| Verify signed instance (#74) | Decode and verify the signed `instance` parameter server-side. | [App Instance API](https://dev.wix.com/docs/api-reference/app-management/app-instance/introduction) |
| Validate `signDate` (#76) | For signed-instance-backed state changes, reject signatures older than one day and require refresh. | [Security and Privacy Best Practice](https://dev.wix.com/docs/build-apps/launch-your-app/legal-and-security/security-and-privacy-best-practice) |
| HTTPS everywhere (#65, #77) | Dashboard, editor, and live-site URLs must use HTTPS. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| CSRF and XSS (#64, #78) | Sanitize every user input field. Regex tag stripping is only partial mitigation; use context-appropriate encoding and maintained sanitizers when HTML is supported. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Password storage (#63, #79, #80) | Store salted hashes; never store raw passwords. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Password reset (#81) | Send expiring email links; never send raw passwords. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Sensitive data (#69) | Keep sensitive data out of cookies and encrypt it at rest when needed. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |

### UX, Performance, and Accessibility

| Requirement | Notes | Docs |
| --- | --- | --- |
| Wix popup/modal patterns (#39) | Use Wix-appropriate surfaces for in-product flows. OAuth and documented pricing-page upgrade CTAs are exceptions. | [Dashboard extension guidelines](https://dev.wix.com/docs/build-apps/develop-your-app/frameworks/self-hosting/supported-extensions/dashboard-extensions/guidelines-for-self-hosted-dashboard-extensions) |
| No browser-native interruptions (#45) | Replace `alert()` or `confirm()` with inline status, toast, modal, or other appropriate feedback. | [UX/UI Best Practices](https://dev.wix.com/docs/build-apps/develop-your-app/design/ux-and-ui-best-practices) |
| Demo data (#37) | Show realistic fictional content on first install. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| No visitor ads (#47) | Unless ad display is the app purpose and required permits exist. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Performance (#48, #49) | Run a performance audit and clear known bugs/console errors before submission. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Responsive design (#52, #54) | Live-site extensions need responsive layouts; dashboard surfaces need the required desktop layout. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Accessibility and SEO (#53, #55, #57, #58) | Avoid widget `<h1>` tags, provide relevant alt-text controls, use UTF-8, and meet accessibility expectations. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |
| Cookie consent (#92, #97) | Activate/deactivate cookies dynamically per visitor consent choice. | [App Market Guidelines](https://dev.wix.com/docs/build-apps/launch-your-app/app-distribution/app-market-guidelines) |

---

## Technical Review Taxonomy

Use these IDs for traceability when mapping findings to review feedback.

| # | Requirement | Area |
| --- | --- | --- |
| 25 | Apps collecting money must implement Wix Billing unless an exception is granted. | Billing |
| 29 | Do not use custom mechanisms to unlock content. | Billing |
| 30 | Do not link to purchase mechanisms other than Wix Billing. | Billing |
| 31 | Credits purchased through in-app purchase must not expire. | Billing |
| 33 | Test the checkout flow for each plan. | Billing |
| 35 | No direct user downgrade through the pricing page. | Billing |
| 37 | Display realistic demo data on first install. | UX |
| 39 | Use Wix popup/modal patterns for in-product flows; OAuth and documented upgrade CTAs are exceptions. | UX |
| 44 | Plugin extension content must relate to the host app's core functionality. | Functionality |
| 45 | Avoid disruptive behavior and browser-native `alert()`/`confirm()` boxes. | UX |
| 46 | Do not show ads to site owners except unobtrusive cross-promotion of your own apps. | Advertising |
| 47 | Do not show ads to site visitors unless that is the app purpose and permits exist. | Advertising |
| 48 | Meet startup and load-time expectations. | Performance |
| 49 | Clear known bugs and console errors before submission. | Quality |
| 50 | Multiple website components on the same site must have separate settings. | Multi-instance |
| 51 | Site copy should copy applicable app content/settings, not reset to default state. | Multi-instance |
| 52 | Live-site extensions must be responsive across screen sizes and devices. | Responsive |
| 53 | Website components must be accessible to visitors with disabilities. | Accessibility |
| 54 | Dashboard app surfaces must support the required desktop layout. | Dashboard |
| 55 | Widget components must not render `<h1>` tags. | SEO |
| 56 | Optimize SEO-meaningful content per industry best practices. | SEO |
| 57 | Include accessibility customization such as alt text where applicable. | Accessibility |
| 58 | Use UTF-8 encoding for multilingual text support. | Localization |
| 59 | Test supported desktop browsers. | Browser support |
| 60 | Test live-site extensions on supported mobile browsers. | Browser support |
| 61 | Test live-site extensions on supported tablet browsers. | Browser support |
| 62 | Never request more permissions than required. | Permissions |
| 63 | Store salted password hashes instead of raw passwords. | Security |
| 64 | Protect against CSRF, XSS, and other security vulnerabilities. | Security |
| 65 | Serve the app over HTTPS with a valid certificate. | Security |
| 66 | Do not force login or personal information unless core to the app. | Security |
| 67 | Let users revoke connected social credentials in the app. | Security |
| 68 | Secure and verify each user's identity through the instance. | Identity |
| 69 | Encrypt sensitive data and do not store it in cookies. | Security |
| 72 | Keep app secret key and OAuth tokens secure. | Security |
| 73 | Apps collecting financial data must comply with PCI-DSS and PA-DSS. | Security |
| 74 | Verify signed instance signature server-side. | Security |
| 76 | Validate `signDate` for signed-instance-backed edit/save actions. | Security |
| 77 | All dashboard, editor, and live-site endpoints must support HTTPS. | Security |
| 78 | Prevent XSS in input fields such as comments, forms, search, and titles. | Security |
| 79 | Use secure password hashing. | Security |
| 80 | Add a unique random salt/nonce to each stored password. | Security |
| 81 | Password reset must use an expiring email link, not a raw password. | Security |
| 92 | Comply with site visitor consent policies. | Privacy |
| 97 | Implement cookie consent behavior per visitor preferences. | Privacy |
| 107 | Provide a settings/setup UI. | Setup |
| 108 | Do not use localhost URLs in app configuration. | Setup |
| 111 | Request only minimum necessary permissions. | Permissions |
| 112 | Remove permissions already included in added scopes. | Permissions |
| 113 | App Installed and App Removed webhooks are recommended for lifecycle handling. | Webhooks |
| 114 | Implemented webhooks must return HTTP 200 on successful receipt. | Webhooks |
| 115 | Identify users by `instanceId`, not session/cookies. | Identity |
| 116 | Separate billing for each site. | Billing |
| 117 | Support multi-site account switching or one-account-per-site flows. | Identity |
| 118 | Auto-login when the user reopens the app through Manage Apps. | Identity |
| 119 | Forgotten-password flow must send reset links and avoid raw passwords. | Security |
| 120 | Check required Wix apps and notify the user if missing. | Setup |
| 121 | Review prompts are recommended only; keep them non-blocking if implemented. | UX |
| 122 | Handle site duplication through `originInstanceId`. | Multi-instance |
| 123 | External pricing page is broken or used instead of Wix internal billing. | Billing |
| 125 | Premium features require a clear upgrade path; do not infer app billing from Business Solutions Pricing Plans API usage. | Billing |
| 130 | Apps supporting Wix Stores catalog data must support both Catalog V1 and Catalog V3. | Stores |
| 132 | App installation process fails or results in errors. | Installation |
| 133 | Login/session issues occur during or after installation. | Identity |
| 151 | Custom element has quality issues such as pixelated images or missing descriptions. | Component quality |
| 152 | Embedded script has syntax errors, missing parameters, or the wrong type. | Embedded script |
| 154 | Component configuration has a general issue. | Components |
| 158 | Custom element extension is missing settings or does not appear in the editor. | Extensions |
| 159 | Dashboard modal extension purpose is unclear or unnecessary. | Extensions |
| 160 | Dashboard page extension is blank, broken, or violates Wix guidelines. | Extensions |
| 161 | Embedded script is not loading, syncing, or configured correctly. | Extensions |
| 162 | External URL does not open in a new tab or references a non-Wix platform. | Extensions |
| 163 | Required service plugin for a dropshipping app is missing. | Service plugin |
| 166 | Widget extension image or configuration is incorrect. | Extensions |
| 167 | Extension configuration has a general issue. | Extensions |
| 168 | Automations email template contains incorrect text or is active too early. | Automations |
| 169 | App does not follow UX best practices such as defaults or validation warnings. | UX |
| 170 | App behavior is confusing in editor preview compared with the published site. | UX |
