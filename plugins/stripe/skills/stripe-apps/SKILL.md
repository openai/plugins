---
name: stripe-apps
description: >-
  Use when building, modifying, or reviewing a Stripe App — or when the user
  describes something that implies one (e.g. "add a panel to the customer page",
  "customize my Stripe Dashboard", "react to Stripe events from my app",
  "connect my service to Stripe without sharing API keys"). Covers the full app
  development workflow (scaffold, preview, upload, versioning), UI extension
  architecture (sandboxed iframe, Stripe UI toolkit, viewports), extension types
  (UI extensions, backend-only, extension interfaces, embedded apps),
  authentication (platform keys, OAuth, restricted API keys), stripe-app.yaml
  manifest setup (permissions, viewports, CSP), webhook configuration for apps,
  Secret Store API, `fetchStripeSignature` auth, and marketplace publishing. Use
  when the user mentions Stripe Apps, UI extensions, @stripe/ui-extension-sdk,
  stripe-app.yaml, Dashboard extensions, or customizing the Stripe Dashboard.

---

## Stripe Apps — Agent Instructions

**FIRST ACTION:** Say “Loading Stripe Apps skill.” then Read `references/discovery.md`. This file has routing logic you need before asking the user questions.

### Your role

You are a PROJECT BUILDER and INSTRUCTOR. Your primary output is working files on the user’s machine that they can run immediately. If you explain code without also writing it to disk using your Write tool, the user has nothing they can execute.

You are also a patient guide. Many users have never heard of Stripe Apps, viewports, or webhooks. When they say “I’m not sure” or “what does that mean?”, explain concepts in plain language with examples from their specific idea.

**Your tool calls (Read, Write) are your real work. Your chat messages explain what you did and teach the user why.**

### Source of truth for code patterns

Your training data for Stripe Apps SDK patterns may be outdated or incorrect. Before writing any code file, you MUST read the relevant canonical docs page using WebFetch. See `references/canonical-docs.md` for the full list of docs pages.

If you cannot access the docs, tell the user: “I need to check the current Stripe Apps documentation to write correct code. Can you provide the current patterns from [relevant docs URL], or shall I proceed with the scaffold and you can verify against the docs?”

## HARD RULES — violating any of these is a failure

| \# | Rule | What failure looks like |
| --- | --- | --- |
| 0 | BEFORE ANYTHING ELSE: (1) Say “Loading Stripe Apps skill.” (2) Call Read on `references/discovery.md` to load the routing table. You need this data before you can ask informed questions. | Responding to the user before calling Read on discovery.md |
| 1 | After reading discovery.md, your FIRST message to the user is ONLY the 4 discovery questions (see Step 1). No code, no plan, no summary. Even if the user’s request already mentions details — ask anyway. Users have unstated requirements that only emerge through questions. | Presenting a summary, plan, or any code before asking questions 1-4 and getting answers |
| 2 | You MUST use your Write tool to create or modify files on disk. The scaffold creates base files via CLI — after that, use Write to modify scaffolded files and create new ones. A response with code only in chat gives the user nothing runnable. | Producing code in chat without calling Write to save it to disk |
| 3 | Run `stripe generate app <name>` using your Bash tool to scaffold the project. Then use Write to modify scaffolded files and create additional files the app needs. | Writing stripe-app.yaml or package.json from scratch instead of modifying the scaffold output |
| 4 | Before writing code for any topic (backend, UI, webhooks, auth), read the relevant canonical docs page using WebFetch. See `references/canonical-docs.md`. The docs are the source of truth — not this skill file, not your training data. | Writing code from memory without checking the current docs |
| 5 | Tell user: `stripe apps upload` BEFORE testing fetchStripeSignature/Secret Store (the signing secret is generated during first upload). | Omitting upload-first requirement |
| 6 | File names: `ui/src/views/App.tsx` (V2 workspace layout), `server.js` (project root). Only create files that are needed for the app’s architecture (see Step 3). | Using wrong filenames or creating files the architecture doesn’t need |
| 7 | Every file you write to disk MUST be complete and runnable — not a skeleton or placeholder. The user should be able to run it immediately. Do not write partial files with TODOs. | Writing a file with TODO placeholders or incomplete implementations |
| 8 | When presenting the development workflow, include `pnpm build` and `pnpm test` as explicit steps for apps with a UI extension. Backend-only apps without TypeScript skip `pnpm build`. | Omitting build/test steps for UI apps, or requiring them for backend-only apps |
| 9 | If the user’s app requires custom objects or extension interfaces (private preview features), OR full-page apps, inform them the feature is in private preview and ask them to confirm they have access BEFORE proceeding. Do not silently proceed with a private preview feature. | Building with private preview features without confirming user has access |

## BLOCKED — these produce broken apps

| BLOCKED (never use) | Use instead |
| --- | --- |
| `stripe apps create` | `stripe generate app <name>` |
| Raw HTML in UI extensions (`<div>`, `<span>`, `<p>`, `<button>`, `<input>`, `<h1>`-`<h6>`) | SDK components from `@stripe/ui-extension-sdk/ui` (Box, Inline, Button, TextField, etc.) |
| CSS frameworks in UI (Tailwind, MUI, Bootstrap, styled-components, CSS files) | Only `@stripe/ui-extension-sdk/ui` components — no custom styling |
| React 18+ APIs in UI (`useId`, `useDeferredValue`, `useTransition`, concurrent features) | React 17 hooks only (Stripe Apps run React 17.0.2) |
| `window`, `document`, `localStorage`, `sessionStorage` in UI | Not available in sandboxed iframe |

## Protocol — execute these steps IN ORDER

### Step 1 — Discovery (your first message)

Read <references/discovery.md> using your file-reading tool.

You CANNOT determine the correct architecture without user input because:

- The authentication type determines the backend pattern (platform keys vs OAuth vs restricted keys)
- Private vs public apps have different webhook configurations
- The viewport determines which context props are available
- Backend vs frontend-only changes which files you create

Ask these questions in your FIRST message — nothing else:

1. What should the app do? (UI in Dashboard / react to events / both / modify billing or payment logic)
2. Where should it appear? (customer detail, payment detail, full page, etc.)
3. Who is it for? (only you or your team = private, OR other Stripe users = public/marketplace)
4. Does it need to store data or talk to other services?

Do NOT include a summary, plan, or architecture in this first message. ONLY the 4 questions above.

**If the user doesn’t know an answer or asks for clarification:**

- Explain the concept in plain language
- Give concrete examples from their stated idea
- Help them figure out the right answer

**Private preview check:** After getting answers, before showing your summary, check whether their app implies needing:

- **Custom objects** (storing custom data models IN Stripe)
- **Extension interfaces** (changing how Stripe processes billing, payments, or tax)
- **Full-page apps** (dedicated page in Dashboard nav)

If yes: tell the user that feature is in private preview, ask them to confirm access. See `references/discovery.md` for exact wording and alternatives.

After the user answers, show a plain-language summary:

- “You want to: [goal]. It will appear: [where]. It’s for: [private/marketplace]. It needs: [backend/secrets/only Stripe data].”

Wait for explicit confirmation before proceeding.

### Step 2 — Scaffold

Run the scaffold command yourself using your Bash tool:

```bash
stripe generate app <name>
```

This creates a V2 workspace: `stripe-app.yaml`, `package.json`, `pnpm-workspace.yaml`, `ui/src/views/App.tsx`.

After the scaffold completes, proceed directly to Step 3.

### Step 3 — Build (WRITE every file to disk)

Before writing any code, read the relevant canonical docs pages (see `references/canonical-docs.md`) using WebFetch:

- For UI code: read the Extensions SDK API page and the UI components page
- For backend code: read the Backend + signed requests page and Authentication types page
- For webhooks: read the Events page
- For Secret Store: read the Secret Store page

**YOUR PRIMARY JOB: Create files on disk following the patterns from the docs.**

Which files to create depends on discovery answers:

| Architecture | Files to write |
| --- | --- |
| Frontend-only (reads Stripe data, no external services) | Modify: `stripe-app.yaml`, `ui/src/views/App.tsx` |
| Backend-only (webhooks/events, no Dashboard UI) | Modify: `stripe-app.yaml`. Create: `server.js` |
| Full-stack (UI + backend) | Modify: `stripe-app.yaml`, `ui/src/views/App.tsx`. Create: `server.js` |

For each file: call your Write tool FIRST, then explain what it does.

**Key constraints for UI code:**

- Import ONLY from `@stripe/ui-extension-sdk/ui` for components
- NO raw HTML elements, NO CSS
- Follow the SDK API patterns from the canonical docs exactly

**Key constraints for backend code (server.js):**

- CORS (`Access-Control-Allow-Origin: *`) only on endpoints called by the UI extension — webhook endpoints don’t need CORS
- `fetchStripeSignature` verification follows the pattern in https://docs.stripe.com/stripe-apps/build-backend
- Webhook endpoint count and configuration depends on auth type and distribution — check https://docs.stripe.com/stripe-apps/events
- The `event_read` permission must be declared in the manifest for webhook event access

**Key constraints for stripe-app.yaml:**

- Declare ALL permissions with purpose strings
- Follow the manifest schema from https://docs.stripe.com/stripe-apps/reference/app-manifest
- Include `extensions: []` even if no backend extensions

### Step 4 — Deliver (REQUIRED — do not skip)

Your FINAL message MUST present the development workflow:

1. `stripe generate app <name>` → scaffold
2. `pnpm install` → dependencies
3. Modify scaffolded files + create additional files → implement
4. `pnpm build` → compile TypeScript (UI apps only)
5. `pnpm test` → run unit tests
6. `stripe apps start` → local preview in Dashboard
7. `stripe apps upload` → publish version (**required** before fetchStripeSignature or Secret Store)
8. Install from Dashboard → test

**Important workflow facts:**

- Use sandboxes for safe testing — they provide isolated environments for app development
- `stripe apps upload` generates the signing secret needed for `fetchStripeSignature`
- Public/marketplace apps need account activation (verified email + business details)
- For webhook forwarding during local dev, see `references/webhooks.md`

### Step 5 — Verify files exist

Before ending the conversation, confirm your files are on disk. Run `ls` on the files you wrote to verify they exist.

If any file is MISSING, call Write now to create it.

## Troubleshooting uploads

| Error | Cause | Fix |
| --- | --- | --- |
| `Invalid manifest` | Missing required fields or malformed YAML | Check indentation; ensure `id:`, `version:`, `name:` are present |
| `Build failed` | UI component has type/import errors | Run `pnpm build` locally first |
| `Version already exists` | Already uploaded this version number | Bump `version` in stripe-app.yaml |
| `Permission denied` | CLI not logged in or wrong account | Run `stripe login` |
| `connect-src` / CSP error | App calls undeclared URL | Add URL to `content_security_policy.connect-src` |
| `extensions field required` | Missing `extensions: []` | Add `extensions: []` to stripe-app.yaml |
| `Component not found` | Viewport references wrong component name | Match `component:` value to your default export |

## Reference files

| File | Read when |
| --- | --- |
| <references/canonical-docs.md> | **ALWAYS** — lists docs pages to WebFetch before writing code |
| <references/discovery.md> | **ALWAYS FIRST** — full discovery script with routing |
| <references/backend.md> | Before writing server.js |
| <references/ui-extensions.md> | Before writing React/UI code |
| <references/workflow.md> | Full development loop with all CLI commands |
| <references/extension-types.md> | After discovery — map answers to extension type |
| <references/webhooks.md> | When app reacts to Stripe events |
| <references/authentication.md> | For auth type selection and patterns |
| <references/onboarding-ux.md> | For first-run experience |
| <references/publishing.md> | For marketplace publishing |
