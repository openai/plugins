# Publishing — versioning, releases, test vs live mode, marketplace

## Publishing

How to version, release, and publish your Stripe App.

## Test mode vs live mode

**Plain-language:** “Test mode uses fake data so you can try things safely. Live mode uses real customer data. Always build and test in test mode first.”

| Mode | Data | When to use |
| --- | --- | --- |
| Test mode | Fake (test cards, test customers) | Development and QA |
| Live mode | Real customer and payment data | Production |

**Workflow:** Upload → install in test mode → test thoroughly → install in live mode.

**Do not skip test mode testing.** Even if your app looks correct locally with `stripe apps start`, you must install it in test mode and verify it works with the actual install flow before going live.

## Versioning

Bump `version` in `stripe-app.yaml` before each upload:

```yaml
id: com.example.my-app
version: 1.0.1
name: My App
```

Use semantic versioning:

- `1.0.0` — initial release
- `1.0.1` — bug fix
- `1.1.0` — new feature (backward compatible)
- `2.0.0` — breaking change or major feature

**Rules:**

- Versions must be uploaded in order — if you upload `2.0.0` before `1.0.0`, `2.0.0` won’t be available for release
- You can have multiple uploaded versions; you choose which one to install
- Stripe auto-upgrades installed users to the latest release — they don’t need to do anything **unless** you changed permissions

## Upload and release workflow

```bash
# 1. Bump version in stripe-app.yaml, then:
stripe apps upload

# 2. Go to Dashboard → Apps → your app → version history
# 3. Click the version you want to release
# 4. Click "Set as external test version" (test mode) or "Release" (live mode)
```

## When you change permissions

This is a common source of bugs. When you add new permissions:

1. Update `stripe-app.yaml` with the new permissions
2. Bump the version and upload
3. Existing users are notified by email
4. The **“Review Permissions”** button appears — but only on the **Apps workload page** ([dashboard.stripe.com/apps](https://dashboard.stripe.com/apps)), **not on the app itself**
5. The app returns an **invalid-request error** for the new permissions until the user clicks “Review Permissions” and re-authorizes

**Always warn users about this step** when you change permissions. Many users miss the notification and think the app is broken.

**How to notify users:** Consider adding a banner in your app UI that detects when a required permission is missing and guides the user to re-authorize.

## Publishing to the Stripe Apps Marketplace

For public apps — making your app available to all Stripe users.

### Requirements

Before submitting:

- Verified email address on your Stripe account
- Business details filled in (legal name, address)
- App passes [review requirements](https://docs.stripe.com/stripe-apps/review-requirements.md)
- Connect platform accounts cannot publish marketplace apps

### Submission

1. Go to [Dashboard → Apps](https://dashboard.stripe.com/apps)
2. Select your app
3. Click **Submit for review**

Stripe reviews your app for security, functionality, and compliance with their guidelines.

### Review requirements overview

- App must work correctly in test and live mode
- No prohibited content or misleading claims
- Privacy policy URL required
- Support contact required
- App icon and screenshots required

### After approval

Your app appears in the [Stripe Apps Marketplace](https://marketplace.stripe.com/). Any Stripe user can install it.

## Troubleshooting uploads

**Successful upload looks like:**

```
Uploading... Done
Your app has been uploaded to version 0.0.1.
```

**Common upload failures and fixes:**

| Error | Cause | Fix |
| --- | --- | --- |
| `Invalid manifest` / validation failed | Missing required fields or malformed YAML | Check indentation; ensure `id:`, `version:`, `name:` are present |
| `Build failed` / TypeScript errors | UI component has type/import errors | Run `pnpm build` locally first to see the exact error |
| `Version already exists` | Already uploaded this version number | Bump `version` in stripe-app.yaml (e.g. 0.0.1 → 0.0.2) |
| `Permission denied` / `Not authenticated` | CLI not logged in or wrong account | Run `stripe login` and verify with `stripe config --list` |
| `connect-src` / CSP error | App calls a URL not declared in content_security_policy | Add the URL to `content_security_policy.connect-src` in stripe-app.yaml |
| `extensions field required` | Missing `extensions: []` in stripe-app.yaml | Add `extensions: []` even if you have no backend extensions |
| `Component not found` | Viewport references a component name that doesn’t match your export | Ensure `component:` in stripe-app.yaml matches your default export name |

**Debugging steps when upload fails:**

1. Read the full error message — it usually says exactly what’s wrong
2. Run `pnpm build` to check for TypeScript/build errors locally
3. Validate your stripe-app.yaml has all required fields (id, version, name, declarations)
4. Check that file paths match (ui/src/views/App.tsx, not a renamed file)
5. If still stuck: `stripe apps upload --verbose` for detailed output

## Sandboxes for app development

Sandboxes provide isolated environments for safe app development and testing.

**Benefits of using Sandboxes:**

- Isolated from your live account — test destructive operations safely
- Each sandbox has its own app installation and signing secrets
- Useful for testing onboarding flows, uninstall/reinstall cycles, and permission changes

**How to use:**

1. Create a sandbox from Dashboard → Sandboxes
2. Run `stripe apps start` targeting the sandbox
3. Upload and install your app in the sandbox to test the full install flow
4. When ready, upload to your main account for production use
