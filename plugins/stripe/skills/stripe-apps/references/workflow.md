# Workflow — end-to-end build order

## MANDATORY — Full development loop (quick reference)

Follow this exact sequence for every new app. Do NOT skip or reorder steps.

```
1. stripe plugin install apps && stripe plugin install generate   ← one-time CLI setup
2. stripe generate app <name> && cd <name>                       ← scaffold (NOT `stripe apps create`)
3. pnpm install                                                   ← install deps
4. [modify scaffolded files + create missing ones]               ← implement (only add what scaffold doesn't provide)
5. pnpm build                                                     ← compile UI (skip for backend-only apps)
6. pnpm test                                                      ← run tests
7. stripe apps start                                             ← local preview in Dashboard
8. stripe apps upload                                            ← publish version (REQUIRED before Secret Store or fetchStripeSignature work)
9. Install in test mode from Dashboard → Apps                    ← test the installed app
10. Dashboard → Apps → Submit for review                         ← marketplace publishing (optional)
```

**BLOCKED:** Do NOT use `stripe apps create` — it does not scaffold correctly. Always use `stripe generate app`.

**MANDATORY:** Do NOT create files manually when `stripe generate app` provides them. The scaffold creates a V2 workspace: `stripe-app.yaml`, `package.json`, `pnpm-workspace.yaml`, and `ui/src/views/App.tsx` with the correct structure. Only create files that the scaffold doesn’t provide (e.g., `server.js` for your backend). Modify scaffolded files as needed — don’t rewrite them from scratch.

## End-to-end build order (detailed)

Follow this sequence exactly. Deviating from it is the #1 source of confusion when building Stripe Apps.

### Step 1 — Prerequisites (one-time setup)

Install the Stripe CLI, then install the required plugins:

```bash
# Install the apps plugin (creates and manages apps)
stripe plugin install apps

# Install the generate plugin (scaffolds new apps)
stripe plugin install generate
```

**Plain-language:** “These are tools that let the Stripe CLI create and manage apps. You only need to do this once.”

Verify your CLI version is 1.25.0 or newer:

```bash
stripe version
```

### Step 2 — Create the app

```bash
stripe generate app <your-app-name>
cd <your-app-name>
```

This creates a new V2 workspace with the correct directory structure, `stripe-app.yaml` manifest, and example UI extension.

**What gets created:**

```
<your-app-name>/
├── stripe-app.yaml          # V2 app manifest (YAML) — name, permissions, viewports
├── package.json             # workspace root
├── pnpm-workspace.yaml      # declares workspace packages
├── ui/
│   ├── package.json
│   └── src/
│       └── views/
│           └── App.tsx      # main UI component
├── extensions/              # script extensions (one subdir per extension)
└── README.md
```

### Step 3 — Install dependencies

```bash
pnpm install
```

### Step 4 — Build and test (UI apps)

For apps with a UI extension, compile TypeScript and run tests:

```bash
pnpm build
pnpm test
```

Backend-only apps without TypeScript can skip this step.

### Step 5 — Develop locally

```bash
stripe apps start
```

**Plain-language:** “This opens your app live in your Stripe Dashboard while you build it. Changes you save show up immediately — you don’t need to upload anything yet.”

**What this does:**

- Opens a browser to your Stripe Dashboard with your app running live
- Watches for file changes and hot-reloads
- Works against your live or test Stripe account

**Notes:**

- `stripe apps start` requires browser access; Safari is not supported — use Chrome or Firefox
- This does **not** persist — your app is only visible while the command is running
- The app is not installed on your account yet; it’s only previewed locally

### Step 6 — Upload a version (when ready to share or test permissions and secrets)

```bash
stripe apps upload
```

**What this does:**

- Creates a new version of your app in the Stripe Dashboard
- Generates the signing secret needed for `fetchStripeSignature` and the Secret Store API
- Makes the version available to install

**After uploading:**

1. Go to [Dashboard → Apps](https://dashboard.stripe.com/apps)
2. Find your app
3. Click **Install in test mode** to install it on your account

**When you need to upload before `stripe apps start`:**

- Using the Secret Store API
- Using `fetchStripeSignature` to authenticate the UI to a backend
- Testing permissions that require the app to be installed

### Step 7 — Install in live mode (when ready to use with real data)

1. Go to the [Dashboard → Apps page](https://dashboard.stripe.com/apps)
2. Select your app
3. Choose “Private to your account”
4. Select the version to install
5. Click Install

**Plain-language:** “Test mode uses fake data so you can try things safely. Live mode uses real customer data. Always test in test mode first.”

### Step 8 — Ship a new version

1. Bump `version` in `stripe-app.yaml` (use semantic versioning: `1.0.0`, `1.0.1`, `2.0.0`)
2. Upload:
   ```bash
   stripe apps upload
   ```
3. Go to Dashboard → Apps → your app → version history → install the new version

**Important:** Versions must be uploaded in order. If you upload `2.0.0` before `1.0.0`, `2.0.0` won’t be available for release.

### Step 9 — Publish to the marketplace (optional)

To submit your app for marketplace review:

1. Go to [Dashboard → Apps](https://dashboard.stripe.com/apps)
2. Select your app
3. Click **Submit for review**

**Requirements:**

- Verified email address on your Stripe account
- Business details filled in
- App passes [review requirements](https://docs.stripe.com/stripe-apps/review-requirements.md)

## Key gotchas

**`stripe apps start` vs `stripe apps upload`**

|  | `stripe apps start` | `stripe apps upload` |
| --- | --- | --- |
| Purpose | Local development | Publish a version |
| Persistence | Not persistent — only while command runs | Persists in Stripe Dashboard |
| Secret Store | Not available | Available after upload |
| `fetchStripeSignature` | Only works after at least one upload | Works after upload |

**After updating permissions:**

- Users must re-authorize the app
- The “Review Permissions” button only appears on the **Apps workload page** — not on the app itself
- The app returns an invalid-request error for undeclared permissions until the user re-authorizes
- Always warn users about this step when you change permissions

**Sandboxes for app development:**

- Use sandboxes for safe testing — they provide isolated environments where you can test without affecting live data
- Each sandbox has its own app installation and signing secrets
- Useful for testing destructive operations or onboarding flows
