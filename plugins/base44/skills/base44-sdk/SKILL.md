---
name: base44-sdk
description: "The base44 SDK is the library to communicate with base44 services. In projects, you use it to communicate with remote resources (entities, backend functions, ai agents) and to write backend functions. This skill is the place for learning about available modules and types. When you plan or implement a feature, you must learn this skill"
---

# Base44 Coder

Build apps on the Base44 platform using the Base44 JavaScript SDK.

## ⚡ IMMEDIATE ACTION REQUIRED - Read This First

This skill activates on ANY mention of "base44" or when a `base44/` folder exists. **DO NOT read documentation files or search the web before acting.**

**Your first action MUST be:**
1. Check if `base44/config.jsonc` exists in the current directory
2. If **YES** (existing project scenario):
   - This skill (base44-sdk) handles the request
   - Implement features using Base44 SDK
   - Do NOT use base44-cli unless user explicitly requests CLI commands
3. If **NO** (new project scenario):
   - Transfer to base44-cli skill for project initialization
   - This skill cannot help until project is initialized

## When to Use This Skill vs base44-cli

**Use base44-sdk when:**
- Building features in an **EXISTING** Base44 project
- `base44/config.jsonc` already exists in the project
- Base44 SDK imports are present (`@base44/sdk`)
- Writing JavaScript/TypeScript code using Base44 SDK modules
- Implementing functionality, components, or features
- User mentions: "implement", "build a feature", "add functionality", "write code for"
- User says "create a [type] app" **and** a Base44 project already exists

**DO NOT USE base44-sdk for:**
- ❌ Initializing new Base44 projects (use `base44-cli` instead)
- ❌ Empty directories without Base44 configuration
- ❌ When user says "create a new Base44 project/app/site" and no project exists
- ❌ CLI commands like `npx base44 create`, `npx base44 deploy`, `npx base44 login` (use `base44-cli`)

**Skill Dependencies:**
- `base44-sdk` assumes a Base44 project is **already initialized**
- `base44-cli` is a **prerequisite** for `base44-sdk` in new projects
- If user wants to "create an app" and no Base44 project exists, use `base44-cli` first

**State Check Logic:**
Before selecting this skill, verify:
- IF (user mentions "create/build app" OR "make a project"):
  - IF (directory is empty OR no `base44/config.jsonc` exists):
    → Use **base44-cli** (project initialization needed)
  - ELSE:
    → Use **base44-sdk** (project exists, build features)

## Quick Start

```javascript
// In Base44-generated apps, base44 client is pre-configured and available

// CRUD operations
const task = await base44.entities.Task.create({ title: "New task", status: "pending" });
const tasks = await base44.entities.Task.list();
await base44.entities.Task.update(task.id, { status: "done" });

// Get current user
const user = await base44.auth.me();
```

```javascript
// External apps
import { createClient } from "@base44/sdk";

// IMPORTANT: Use 'appId' (NOT 'clientId' or 'id')
const base44 = createClient({ appId: "your-app-id" });
await base44.auth.loginViaEmailPassword("user@example.com", "password");
```

## ⚠️ CRITICAL: Do Not Hallucinate APIs

**Before writing ANY Base44 code, verify method names against this table or [QUICK_REFERENCE.md](references/QUICK_REFERENCE.md).**

Base44 SDK has unique method names. Do NOT assume patterns from Firebase, Supabase, or other SDKs.

### Authentication - WRONG vs CORRECT

| ❌ WRONG (hallucinated) | ✅ CORRECT |
|------------------------|-----------|
| `signInWithGoogle()` | `loginWithProvider('google')` |
| `signInWithProvider('google')` | `loginWithProvider('google')` |
| `auth.google()` | `loginWithProvider('google')` |
| `signInWithEmailAndPassword(email, pw)` | `loginViaEmailPassword(email, pw)` |
| `signIn(email, pw)` | `loginViaEmailPassword(email, pw)` |
| `createUser()` / `signUp()` | `register({email, password})` |
| `onAuthStateChanged()` | `me()` (no listener, call when needed) |
| `currentUser` | `await auth.me()` |

### Functions - WRONG vs CORRECT

| ❌ WRONG (hallucinated) | ✅ CORRECT |
|------------------------|-----------|
| `functions.call('name', data)` | `functions.invoke('name', data)` |
| `functions.run('name', data)` | `functions.invoke('name', data)` |
| `callFunction('name', data)` | `functions.invoke('name', data)` |
| `httpsCallable('name')(data)` | `functions.invoke('name', data)` |

### Integrations - WRONG vs CORRECT

| ❌ WRONG (hallucinated) | ✅ CORRECT |
|------------------------|-----------|
| `ai.generate(prompt)` | `integrations.Core.InvokeLLM({prompt})` |
| `openai.chat(prompt)` | `integrations.Core.InvokeLLM({prompt})` |
| `llm(prompt)` | `integrations.Core.InvokeLLM({prompt})` |
| `sendEmail(to, subject, body)` | `integrations.Core.SendEmail({to, subject, body})` |
| `email.send()` | `integrations.Core.SendEmail({to, subject, body})` |
| `uploadFile(file)` | `integrations.Core.UploadFile({file})` |
| `storage.upload(file)` | `integrations.Core.UploadFile({file})` |

### Entities - WRONG vs CORRECT

| ❌ WRONG (hallucinated) | ✅ CORRECT |
|------------------------|-----------|
| `entities.Task.find({...})` | `entities.Task.filter({...})` |
| `entities.Task.findOne(id)` | `entities.Task.get(id)` |
| `entities.Task.insert(data)` | `entities.Task.create(data)` |
| `entities.Task.remove(id)` | `entities.Task.delete(id)` |
| `entities.Task.onChange(cb)` | `entities.Task.subscribe(cb)` |

## SDK Modules

| Module | Purpose | Reference |
|--------|---------|-----------|
| `entities` | CRUD operations on data models | [entities.md](references/entities.md) |
| `auth` | Login, register, user management | [auth.md](references/auth.md) |
| `agents` | AI conversations and messages | [base44-agents.md](references/base44-agents.md) |
| `functions` | Backend function invocation | [functions.md](references/functions.md) |
| `integrations` | AI, email, file uploads, custom APIs | [integrations.md](references/integrations.md) |
| `analytics` | Track custom events and user activity | [analytics.md](references/analytics.md) |
| `appLogs` | Log user activity in app | [app-logs.md](references/app-logs.md) |
| `users` | Invite users to the app | [users.md](references/users.md) |
| `asServiceRole.connectors` | App-scoped OAuth tokens (service role only) | [connectors.md](references/connectors.md) |
| `asServiceRole.sso` | SSO token generation (service role only) | [sso.md](references/sso.md) |

For client setup and authentication modes, see [client.md](references/client.md).

### TypeScript and type registries

Each reference file includes a "Type Definitions" section with TypeScript interfaces and types for the module's methods, parameters, and return values.

**Getting typed entities, functions, and agents:** The Base44 CLI generates types from your project resources (entities, functions, agents), including augmentations to `EntityTypeRegistry`, `FunctionNameRegistry`, and `AgentNameRegistry`, and wires them into your project so you get autocomplete and type checking without manual setup. For how to generate types, use the **base44-cli** skill.

**Manual augmentation:** You can instead augment the registries yourself in a `.d.ts` file; see the Type Definitions sections in [entities.md](references/entities.md), [functions.md](references/functions.md), and [base44-agents.md](references/base44-agents.md).

## Installation

Install the Base44 SDK:

```bash
npm install @base44/sdk
```

**Important:** Never assume or hardcode the `@base44/sdk` package version. Always install without a version specifier to get the latest version.

## Creating a Client (External Apps)

When creating a client in external apps, **ALWAYS use `appId` as the parameter name**:

```javascript
import { createClient } from "@base44/sdk";

// ✅ CORRECT
const base44 = createClient({ appId: "your-app-id" });

// ❌ WRONG - Do NOT use these:
// const base44 = createClient({ clientId: "your-app-id" });  // WRONG
// const base44 = createClient({ id: "your-app-id" });        // WRONG
```

**Required parameter:** `appId` (string) - Your Base44 application ID

**Optional parameters:**
- `token` (string) - Pre-authenticated user token
- `options` (object) - Configuration options
  - `options.onError` (function) - Global error handler

**Example with error handler:**
```javascript
const base44 = createClient({
  appId: "your-app-id",
  options: {
    onError: (error) => {
      console.error("Base44 error:", error);
    }
  }
});
```

## Module Selection

**Working with app data?**
- Create/read/update/delete records → `entities`
- Import data from file → `entities.importEntities()`
- Realtime updates → `entities.EntityName.subscribe()`

**User management?**
- Login/register/logout → `auth`
- Get current user → `auth.me()`
- Update user profile → `auth.updateMe()`
- Invite users → `users.inviteUser()`

**AI features?**
- Chat with AI agents → `agents` (requires logged-in user)
- Create new conversation → `agents.createConversation()`
- Manage conversations → `agents.getConversations()`
- Generate text/JSON with AI → `integrations.Core.InvokeLLM()`
- Generate images → `integrations.Core.GenerateImage()`

**Custom backend logic?**
- Run server-side code → `functions.invoke()`
- Need admin access → `base44.asServiceRole.functions.invoke()`

**External services?**
- Send emails → `integrations.Core.SendEmail()`
- Upload files → `integrations.Core.UploadFile()`
- Custom APIs → `integrations.custom.call()`
- App-scoped OAuth (app builder's account) → `asServiceRole.connectors.getConnection()` (backend only)

**Tracking and analytics?**
- Track custom events → `analytics.track()`
- Log page views/activity → `appLogs.logUserInApp()`

## Common Patterns

### Filter and Sort Data

```javascript
const pendingTasks = await base44.entities.Task.filter(
  { status: "pending", assignedTo: userId },  // query
  "-created_date",                             // sort (descending)
  10,                                          // limit
  0                                            // skip
);
```

### Protected Routes (check auth)

```javascript
const user = await base44.auth.me();
if (!user) {
  // Navigate to your custom login page
  navigate('/login', { state: { returnTo: window.location.pathname } });
  return;
}
```

### Backend Function Call

```javascript
// Frontend
const result = await base44.functions.invoke("processOrder", {
  orderId: "123",
  action: "ship"
});

// Backend function (Deno)
import { createClientFromRequest } from "npm:@base44/sdk";

Deno.serve(async (req) => {
  const base44 = createClientFromRequest(req);
  const { orderId, action } = await req.json();
  // Process with service role for admin access
  const order = await base44.asServiceRole.entities.Orders.get(orderId);
  return Response.json({ success: true });
});
```

### Service Role Access

Use `asServiceRole` in backend functions for admin-level operations:

```javascript
// User mode - respects permissions
const myTasks = await base44.entities.Task.list();

// Service role - full access (backend only)
const allTasks = await base44.asServiceRole.entities.Task.list();
const token = await base44.asServiceRole.connectors.getAccessToken("slack");
```

## Frontend vs Backend

| Capability | Frontend | Backend |
|------------|----------|---------|
| `entities` (user's data) | Yes | Yes |
| `auth` | Yes | Yes |
| `agents` | Yes | Yes |
| `functions.invoke()` | Yes | Yes |
| `functions.fetch()` | Yes | Yes |
| `integrations` | Yes | Yes |
| `analytics` | Yes | Yes |
| `appLogs` | Yes | Yes |
| `users` | Yes | Yes |
| `asServiceRole.*` | No | Yes |
| `asServiceRole.connectors` (app OAuth) | No | Yes |
| `asServiceRole.sso` | No | Yes |

Backend functions use `Deno.serve()` and `createClientFromRequest(req)` to get a properly authenticated client.
