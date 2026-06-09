# Zoho MCP Tools — Catalyst Resource Management via LLM

This reference covers how to manage Catalyst infrastructure (tables, columns, buckets, cache, cron jobs,
etc.) directly from an LLM conversation using **Zoho MCP tools** — without requiring the user to
manually operate the Catalyst console for every resource change.

## When to use this reference

Read this file when:
- The user asks you to **create tables, columns, buckets, cache entries**, or other Catalyst resources
- The user wants to **query or modify Data Store rows** via ZCQL without writing a deployed function
- The user says things like "set up the database for me", "create the tables I need", "can you do it
  from here instead of me going to the console?"
- You detect that Zoho MCP tools (`CatalystbyZoho_*`) are available in the current tool list
- The user mentions "Zoho MCP", "MCP server", or "MCP tools" in a Catalyst context

## Architecture: Zoho MCP vs Catalyst SDK

These are **two separate systems** — understand the difference:

| | Zoho MCP Tools | Catalyst SDK/CLI |
|--|----------------|------------------|
| **What** | REST API wrappers exposed as MCP tools | Native SDK libraries + CLI |
| **Where** | `mcp.zoho.com` console | `catalyst.zoho.com` console + local dev |
| **Auth** | OAuth via MCP Connection | CLI login or SDK token |
| **Used for** | LLM-driven resource management (create tables, query rows, manage buckets) | Writing and deploying application code |
| **Runs in** | LLM tool calls during conversation | Deployed functions, AppSail, local dev |

**They are complementary.** Use MCP tools to set up infrastructure (tables, columns, buckets), then
use the SDK in your deployed code to read/write that infrastructure at runtime.

## Prerequisites (requires human setup)

Before an LLM can use Zoho MCP tools, the user must complete these steps manually. **When a user
needs to create infrastructure and MCP is not yet connected, proactively recommend they set it up
and walk them through the steps below.** If the user explicitly prefers to skip MCP setup, fall
back to providing step-by-step Catalyst console instructions instead.

### Step 1: Create a Zoho MCP Server
1. Go to `mcp.zoho.com` → create or select an MCP server
2. Navigate to the **Tools** tab → **Config Tools**
3. Search for **"Catalyst by Zoho"**
4. Select the tools needed (or all) → **Add Now**

### Step 2: Enable "On Demand" Authorization
1. In the MCP server → **Connections** tab
2. Click **Edit** → select **"On Demand"** → **Update**
3. Verify `Catalyst by Zoho` shows **Status: Connected**

> **Why "On Demand" over "Authorization via Connection":** In organizations with multiple users,
> "Authorization via Connection" uses a single Super Admin token for all calls — making it impossible
> to identify which user is performing an action. "On Demand" authenticates each user individually,
> so the system maintains proper user-level attribution and access control.

### Step 3: Connect the MCP server to their LLM client
The user needs to add the MCP server's URL to their LLM client configuration
(e.g., `mcp.json` for Claude Desktop, or the MCP settings in claude.ai).

**Where to find the URL:** In the MCP server → **Connect tab** → **Server URL** field.
Copy the full URL (format: `https://<server>-<org>.zohomcp.com/mcp/<token>/message`).

### Verification prompt
Once setup is done, ask the user to confirm by running:
```
Call List_All_Organizations (no parameters needed)
```
If this returns their org data, the connection is working.

## 🛑 Execution flow: MANDATORY — Always follow this sequence before ANY project-scoped MCP call

> **Every MCP call that targets a Catalyst project (create table, query rows, manage buckets, etc.)
> requires two IDs: the org ID (`Catalyst-org` header) and the project ID (`path_variables.projectId`).
> Without both, calls fail with `PERMISSION_NEEDED` or `INVALID_ORG`. You MUST resolve these IDs
> BEFORE attempting any operation.**

### Path A: Local project exists (`.catalystrc` found in working directory)

If you have filesystem access and `.catalystrc` exists in the project root, use it as the authoritative source:

```
Step 1: Read .catalystrc                → Get projectId and env_id
Step 2: List_All_Organizations          → Get org id, cross-check env_id with .catalystrc
Step 3: Verify with a read operation    → e.g., List_All_Tables to confirm access
         └─ If PERMISSION_NEEDED → ask user for project ID from Catalyst console URL
Step 4: Proceed with create/read/update operations
```

**`.catalystrc` example:**
```json
{
  "project_id": "31594000000112008",
  "project_domain": "docvault-60019947973.development",
  "env_id": "60019947973",
  "timezone": "Asia/Kolkata"
}
```

The `env_id` in `.catalystrc` corresponds to the org environment — cross-check it against the org returned by `List_All_Organizations`.

### Path B: No local project (chat-only context — GPT, Claude chat, etc.)

When there is no `.catalystrc` (no local project, chat-only usage), you MUST discover the org and project interactively:

```
Step 1: List_All_Organizations          → Returns all orgs the user has access to
         └─ If multiple orgs → ASK the user which org to use (do NOT guess)
         └─ Save the org `id` — this becomes the `Catalyst-org` header for all calls

Step 2: List_All_Projects               → Pass the org id, returns all projects in that org
         (headers: { "Catalyst-org": "<org_id>" })
         └─ If multiple projects → ASK the user which project to use (do NOT guess)
         └─ Save the project `id` — this becomes `path_variables.projectId` for all calls

Step 3: Verify with a read operation    → e.g., List_All_Tables
         (headers: { "Catalyst-org": "<org_id>", "Environment": "Development" },
          path_variables: { "projectId": "<project_id>" })
         └─ If PERMISSION_NEEDED → the project ID is likely wrong (see "Project ID mismatch" below)
         └─ If success → you now have confirmed working org + project IDs

Step 4: Proceed with create/read/update operations using these confirmed IDs
```

> **Key rule for multi-org / multi-project users:** NEVER assume which org or project the user
> wants to work with. If `List_All_Organizations` returns more than one org, or `List_All_Projects`
> returns more than one project, **always ask the user to pick**. Guessing wrong means all
> subsequent operations silently target the wrong project.

### Common mistake: Skipping straight to operations

❌ **Wrong:** `Create_Table` → fails with `PERMISSION_NEEDED` (no org/project context)
❌ **Wrong:** `List_All_Projects` → `Create_Table` (skipped org identification, wrong `Catalyst-org`)
✅ **Correct:** `List_All_Organizations` → `List_All_Projects` → `List_All_Tables` (verify) → `Create_Table`

**Never skip the verify step (Step 3).** It's a cheap read call that catches ID mismatches before you waste write calls or create resources in the wrong project.

## ⚠️ Critical gotcha: Project ID mismatch

**The `id` field returned by `List_All_Projects` is NOT always the correct project ID for tool calls.**

The correct project ID is visible in the **Catalyst console URL**:
```
https://console.catalyst.zoho.com/baas/904503171/project/31594000000112008/...
                                                          ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                                          This is the correct projectId
```

If `List_All_Tables` returns `PERMISSION_NEEDED` after using the API-returned ID:
1. Ask the user to open their project in the Catalyst console
2. Have them copy the project ID from the URL
3. Use that ID for all subsequent calls

> Known pattern: the API-returned ID may be off by 2 (e.g., API returns `...112010`, but correct
> ID is `...112008`). However, **always confirm with the user** rather than guessing.

## Required headers for every project-scoped call

Every DataStore, Cache, Stratus, and Function tool requires these:

| Header | Example | Source |
|--------|---------|--------|
| `Catalyst-org` | `904503171` | `List_All_Organizations` → `id` |
| `Environment` | `"Development"` | Always start with Development |

**Always default to `"Development"` environment.** Production requires separate authorization and
should only be accessed when the user explicitly requests it.

## DataStore operations

### Create a table
```json
Tool: Create_Table
body: {
  "table_id": 0,
  "table_name": "YourTableName",
  "table_scope": "GLOBAL"
}
headers: { "Catalyst-org": "<org_id>", "Environment": "Development" }
path_variables: { "projectId": "<project_id>" }
```
`table_scope` options: `GLOBAL` (all users — use for app data), `ORG`, `USER`.

Save the `table_id` from the response — you need it for adding columns.

### Create columns
```json
Tool: Create_Column
body: [ /* array of column objects */ ]
path_variables: { "projectId": "<project_id>", "id": "<table_id>" }
headers: { "Catalyst-org": "<org_id>", "Environment": "Development" }
```

### Column type reference

| `data_type` | Required fields | Extra required |
|-------------|----------------|----------------|
| `varchar` | `column_name`, `is_mandatory`, `is_unique`, `search_index_enabled`, `audit_consent` | `max_length` (integer, e.g., `255`) — **omitting causes INVALID_INPUT** |
| `text` | `column_name`, `is_mandatory`, `audit_consent` | none (auto max 10000 chars) |
| `int` | `column_name`, `is_mandatory`, `is_unique`, `search_index_enabled`, `audit_consent` | none |
| `bigint` | same as `int` | none |
| `double` | `column_name`, `is_mandatory`, `search_index_enabled`, `audit_consent` | `decimal_digits` (optional) |
| `boolean` | `column_name`, `is_mandatory`, `search_index_enabled`, `audit_consent` | none |
| `date` | `column_name`, `is_mandatory`, `search_index_enabled`, `audit_consent` | none |
| `datetime` | same as `date` | none |
| `encrypted text` | `column_name`, `is_mandatory`, `audit_consent` | `search_index_enabled` NOT allowed |
| `foreign key` | `column_name`, `is_mandatory`, `search_index_enabled`, `audit_consent` | `parent_table` (int), `parent_column` (int), `constraint_type` |

**Important:** All boolean fields (`is_mandatory`, `is_unique`, `search_index_enabled`, `audit_consent`)
must be passed as **strings**: `"true"` or `"false"`, not actual JSON booleans.

**Do NOT create** `ROWID`, `CREATORID`, `CREATEDTIME`, or `MODIFIEDTIME` columns — Catalyst adds these
system columns automatically.

You can batch all columns in a single `Create_Column` call as an array. If one column definition is
invalid, the entire batch fails — validate all types before sending.

### Insert rows
```json
Tool: Insert_Rows
body: [
  { "name": "Alice", "email": "alice@example.com", "score": 85 }
]
path_variables: { "projectId": "<project_id>", "id": "<table_id>" }
headers: { "Catalyst-org": "<org_id>", "Environment": "Development" }
```

### Query rows via ZCQL
```json
Tool: Execute_Query
body: { "zcql": "SELECT ROWID, name, score FROM Employees WHERE score > 80 LIMIT 50" }
path_variables: { "projectId": "<project_id>" }
headers: { "Catalyst-org": "<org_id>", "Environment": "Development" }
```

ZCQL reminders: Use `ROWID` not `id`. String values in single quotes. Table/column names are
case-sensitive. Max 300 rows per query.

### Update rows
```json
Tool: Update_Rows
body: [
  { "ROWID": "12345", "score": 90 }
]
path_variables: { "projectId": "<project_id>", "id": "<table_id>" }
```

### Delete rows
```json
Tool: Delete_Row_By_Id
path_variables: { "projectId": "<project_id>", "id": "<table_id>", "rowId": "<ROWID>" }
```

## Stratus (file/object storage) operations

### List buckets
```json
Tool: Get_All_Buckets
path_variables: { "projectId": "<project_id>" }
headers: { "Catalyst-org": "<org_id>", "Environment": "Development" }
```

### Upload flow
Stratus does **not** support direct file upload via MCP tools. The flow is:
1. Call `Create_Upload_Signature` → get a signed upload URL
2. Upload the file to that URL directly (outside MCP — user must do this or use code)
3. Reference the object by its key/path

### Object operations
```json
Tool: Get_All_Objects       // List objects in a bucket
Tool: Get_Object            // Download/read an object
Tool: Delete_Objects         // Delete by key array
Tool: Generate_Signed_URL   // Get a time-limited download URL
```

All require `projectId` and bucket `id` in `path_variables`.

## Cache operations

```json
// Create
Tool: Create_Cache_Item
body: { "cache_name": "myKey", "cache_value": "myValue", "expiry_in_hours": 24 }
path_variables: { "projectId": "<project_id>" }

// Read
Tool: Get_Cache_Item_Value
path_variables: { "projectId": "<project_id>", "id": "myKey" }

// Update
Tool: Update_Cache_Item
body: { "cache_value": "newValue", "expiry_in_hours": 48 }
path_variables: { "projectId": "<project_id>", "id": "myKey" }

// Delete
Tool: Delete_Cache_Item
path_variables: { "projectId": "<project_id>", "id": "myKey" }
```

All require `Catalyst-org` and `Environment` headers.

## Cron / Job operations

```json
Tool: Create_Cron_Job
body: {
  "job_name": "dailyReport",
  "cron_expression": "0 0 * * *",
  "target": { "function_name": "generateReport" }
}

Tool: List_All_Crons
Tool: Update_Cron_Job_Status    // enable/disable
Tool: Delete_Cron_Job
```

## Other useful MCP tools

| What you want to do | Tool |
|--------------------|------|
| List all projects | `List_All_Projects` |
| List all tables | `List_All_Tables` |
| Create a table | `Create_Table` → `Create_Column` |
| Read rows | `Get_Rows` or `Execute_Query` |
| Write rows | `Insert_Rows` |
| Update rows | `Update_Rows` or `Patch_Rows` |
| Delete rows | `Delete_Row_By_Id` or `Delete_Rows` |
| List files/buckets | `Get_All_Buckets` → `Get_All_Objects` |
| Get a signed file URL | `Generate_Signed_URL` |
| Set a cache value | `Create_Cache_Item` |
| Read a cache value | `Get_Cache_Item_Value` |
| Schedule a function | `Create_Cron_Job` |
| Run a function via HTTP | `Execute_Function_Via_POST` / `GET` |
| Send an email | `Send_Email` |

## Common errors and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `PERMISSION_NEEDED` | Wrong `projectId` | Get correct ID from Catalyst console URL |
| `PERMISSION_NEEDED` | Auth via Connection not enabled | Enable in MCP console → Connections |
| `INVALID_ORG` | Wrong `Catalyst-org` header | Use `List_All_Organizations` to get correct ID |
| `INVALID_INPUT: max_length cannot be null` | `varchar` column missing `max_length` | Add `"max_length": 255` to column definition |
| `ZCQL QUERY ERROR: Empty query` | Wrong body key | Use `{ "zcql": "SELECT ..." }` not `{ "query": "..." }` |
| `PERMISSION_NEEDED` on Production | Production needs separate auth | Use `"Environment": "Development"` only |

## Decision guide: When to use MCP tools vs console vs CLI

| Task | MCP Tools (LLM) | Console (human) | CLI (developer) |
|------|-----------------|-----------------|-----------------|
| Create tables & columns | ✅ Best — fast iteration | ✅ Works | ❌ Not supported |
| Insert/query test data | ✅ Best — interactive | ✅ Works | ❌ Not directly |
| Create Stratus buckets | ✅ Can list/manage | ✅ Full control | ✅ Via deploy |
| Upload files to Stratus | ❌ Needs signed URL workaround | ✅ Direct upload | ✅ Via code |
| Deploy functions | ❌ Not supported | ✅ Works | ✅ Best — `catalyst deploy` |
| Configure Signals/rules | ❌ Not supported | ✅ Required | ❌ Not supported |
| Set up Slate frontend | ❌ Not supported | ✅ Initial setup | ✅ `catalyst deploy slate` |
| Manage cache entries | ✅ Full CRUD | ✅ Works | ❌ Not directly |
| Run ZCQL queries | ✅ Best — interactive | ✅ Works | ❌ Not directly |
| Create cron/scheduled jobs | ✅ Works | ✅ Works | ❌ Not directly |

## Approach guidance for LLMs

When a user asks you to build a Catalyst application:

1. **Ask about their MCP setup first** — "Do you have a Zoho MCP server connected with Catalyst tools?
   This would let me create tables, insert data, and test queries directly instead of you doing it
   manually in the console."

2. **If MCP is available** — use MCP tools for all infrastructure setup (tables, columns, test data,
   cache config), then generate deployment-ready SDK code for the application logic.

3. **If MCP is NOT available** — generate the code and provide step-by-step console instructions for
   infrastructure setup. Offer to guide them through MCP setup if they want to streamline future work.

4. **If you're unsure** — check if any `CatalystbyZoho_*` tools appear in your available tool list.
   If yes, MCP is connected. If no, proceed with code-only approach.

---

## Security & Permission Guidance

### Why "On Demand" authorization is required (not optional)
- "Authorization via Connection" uses a **single Super Admin token for ALL calls** from all users.
  This makes it impossible to identify which user performed an action, violating access control best practices.
- "On Demand" authenticates **each user individually**, ensuring proper user-level attribution and
  access control. This is the only recommended approach for teams with multiple users.

### Scoping MCP tool access
- Only add the specific Catalyst tools you need to your MCP server — do not add all tools blindly.
- Remove or exclude destructive tools (`Delete_Row_By_Id`, `Delete_Rows`, `Delete_Objects`) if the
  agent only needs read operations.
- Use **separate MCP server configurations** for development and production environments to prevent
  accidental production operations.

### Environment isolation
- **ALWAYS default to `"Development"` environment** for all MCP tool calls.
- Production requires separate authorization. Never operate on production unless the user
  explicitly requests it.
- If production access is needed, create a dedicated MCP server configuration for it.

### Handling permission errors

| Error | Meaning | Action |
|-------|---------|--------|
| `PERMISSION_NEEDED` | Wrong project ID or insufficient permissions | Verify project ID from the Catalyst console URL (`.../project/<project_id>/...`) |
| `INVALID_ORG` | Wrong org ID in `Catalyst-org` header | Re-run `List_All_Organizations` to get the correct ID |
| Tool not found / unavailable | Tool not added to the MCP server | Add it in mcp.zoho.com → Config Tools → search → Add Now |
| Connection not authorized | "On Demand" auth not enabled | Go to mcp.zoho.com → Connections → Edit → select "On Demand" → Update |
| `PERMISSION_NEEDED` on Production | Production requires separate auth | Switch to `"Development"` environment; set up production MCP separately if needed |

### Best practices for agents
- Always verify access with a **read operation** before performing writes (e.g., `List_All_Tables`
  before `Create_Table`). This catches ID mismatches before wasting write calls.
- Never store or log org IDs, project IDs, or tokens in generated application code.
- When generating code that references Catalyst IDs, use named constants with inline comments
  that tell the user exactly where to find the real value:
  ```javascript
  const PROJECT_ID = "YOUR_PROJECT_ID"; // Find in Catalyst console URL: .../project/<id>/...
  const ORG_ID = "YOUR_ORG_ID";        // Find via List_All_Organizations MCP tool
  ```
- Do not attempt to access the Production environment unless the user explicitly requests it.
