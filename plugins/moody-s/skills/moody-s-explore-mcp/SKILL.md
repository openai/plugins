---
name: moody-s-explore-mcp
description: Discover and safely explore Moody's MCP tools. Use when the user wants to see what Moody's data is available, verify MCP connectivity, look up an entity, or run a lightweight ratings/research probe before deeper analysis.
---

<!-- To activate this skill, add `"skills": "./skills/"` to `.codex-plugin/plugin.json`. -->

# Explore Moody's MCP

Use this skill to discover Moody's MCP capabilities and run a minimal, read-only probe before deeper credit and financial analysis workflows.

## When to Use

- User asks "what can Moody's do?", "list Moody's tools", or "is Moody's connected?"
- User wants a quick entity lookup or ratings snapshot without a full credit memo
- You need to verify which Moody's tools are available in the current session

## Prerequisites

- Moody's plugin installed with the enterprise store MCP linked via `.app.json`
- OAuth completed on first use - auth errors mean the user should reconnect the Moody's integration

## Workflow

### Step 1: Verify MCP Availability

Confirm Moody's MCP tools appear in the session. If tools are missing or calls fail with auth errors, stop and ask the user to install or re-authenticate the Moody's plugin.

### Step 2: Discover Tools

List available Moody's MCP tools. **Read each tool's schema before calling** - tool names and parameters may differ from the reference list below.

If tools appear as deferred, batch-load schemas in a single discovery pass rather than calling tools blindly.

### Step 3: Smoke Test - Entity Lookup

Run `findEntity` (or the equivalent entity-search tool) with a company name or identifier the user provides. If no company was given, ask for one before proceeding.

Present matches clearly and confirm which entity to use. **Never invent entity IDs** - always resolve through entity search first.

### Step 4: Light Probe (Optional)

After confirming an entity, call one read-only tool to demonstrate connectivity:

- `getEntityRatings` - current rating, outlook, and recent history
- `searchEntityDocuments` - recent research documents for the entity
- `getEntityPeers` - comparable entities for context

Pick the tool that best matches the user's question. Read the schema, call once, and summarize results.

### Step 5: Summarize

Report:

1. Which tools are available in this session
2. The entity resolved (name + ID)
3. What data was retrieved in the probe
4. Suggested next steps (e.g. full ratings history, peer comparison, document deep-dive)

## Known Tools (Reference - Verify Live Schemas)

| Tool                     | Purpose                                          |
| ------------------------ | ------------------------------------------------ |
| `findEntity`             | Search entities by name, identifier, or metadata |
| `getEntityRatings`       | Current ratings, outlooks, and rating history    |
| `getEntityPeers`         | Comparable peer entities                         |
| `searchEntityDocuments`  | Search Moody's research document library         |
| `getEntityScorecard`     | Rating scorecard metrics and methodology inputs  |
| `getEntityRatingDrivers` | Upgrade and downgrade factor analysis            |
| `getEntityEsg`           | ESG factors affecting credit quality             |

Tool names above are reference only. Always confirm against live MCP tool descriptors before calling.

## Guardrails

- Read tool schemas before every call
- Do not invent entity IDs - always resolve via entity search first
- Cite Moody's as the data source
- This skill provides research context, not investment advice
- On empty or error responses, report clearly and stop - do not retry blindly or fabricate data
