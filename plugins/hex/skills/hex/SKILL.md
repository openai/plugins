---
name: hex
description: Search Hex projects and ask Hex Threads questions. Use when the user explicitly references Hex, Hex projects, Hex dashboards, Hex data apps, Hex Threads, or asks to search an existing Hex workspace asset.
---

# Hex

Use Hex when the user explicitly references Hex, Hex projects, Hex dashboards, Hex data apps, Hex analyses, or Hex Threads, or when they ask to search an existing Hex workspace asset.

Do not use Hex as the default owner for generic company metrics, KPI reporting, dashboard creation, report generation, metric diagnostics, or notebook-backed analysis. Route those through the relevant analytics or Data Science skills unless the user asks to do the work in Hex.

## Workflow

1. Classify the request.
   Use Hex only for explicit Hex intent or existing Hex asset discovery. Generic metrics, KPI, dashboard, report, notebook, or company-data prompts belong to the relevant analytics or Data Science skills unless the user names Hex as the target surface. Do not use Hex for generic web research, uploaded-file-only analysis, or questions about how Hex itself works unless the user explicitly wants to search their Hex workspace.

2. Search existing projects first.
   Use [$Hex](app://connector_690a9430a270819196671dcb4c95898e) `search_projects` with the strongest query terms from the user's request. Present relevant project links before starting a new Thread.

3. Use existing threads when provided.
   If the user provides a Hex Thread id or link, use [$Hex](app://connector_690a9430a270819196671dcb4c95898e) `get_thread` to read the thread state and messages before answering or proposing a follow-up.

4. Confirm before write actions.
   `create_thread` and `continue_thread` can start or modify Hex Thread work. Before calling either tool, tell the user what prompt will be sent to Hex and ask for confirmation. After a write call, poll with `get_thread` until the thread is complete or until the user asks you to stop.

5. Answer with provenance.
   When project search returns results, include the project names and links. When using a thread, summarize the final Hex response and include the Hex Thread link or id when available.

## Good Fits

- `Find the Hex dashboard for campaign segmentation.`
- `What Hex projects mention churn analysis?`
- `Ask Hex to analyze revenue drivers for the last quarter.`
- `Check this Hex Thread and summarize the result.`
- `Find the Hex project that has our pipeline forecast.`

## Negative Cases

- Do not use Hex for general market questions, web-only questions, or product documentation lookup.
- Do not use Hex just because the word `data` appears if the user supplied a local file that can be analyzed directly.
- Do not use Hex just because a prompt mentions metrics, KPIs, dashboards, reports, or notebooks. Use the relevant analytics or Data Science skills unless the user asks for Hex.
- Do not use Hex for permission, billing, or workspace-admin questions unless the user asks to search a Hex project or thread about that topic.

## Safety

- Start with read-only operations: `search_projects` and `get_thread`.
- Treat `create_thread` and `continue_thread` as writes.
- Never invent project names, thread status, SQL, charts, or analysis results.
