# Plugin Best Practices Reference

## Contents

- Plugin model
- Build sequence
- App and MCP tool design
- Skills
- Hero prompts and evals
- Auth
- Namespacing and tool specs
- Context-efficient responses
- Maintenance
- Submission checklist
- Simple eval loop

## Plugin Model

A Codex plugin combines:

- App or Connector: a partner-hosted MCP server that exposes product APIs as tools Codex can call after OpenAI review.
- Skills: prompt-layer instructions that teach Codex when and how to use those tools to complete higher-level workflows.

Design for both humans and agents. Humans may invoke a plugin explicitly with `@PluginName`; agents may invoke it implicitly while completing a broader task. A good plugin is discoverable from names and descriptions, works well when directly requested, and composes with other plugins.

There are two common plugin layers:

- Connector plugin: wraps one product or company API with broadly useful skills. Examples: GitHub, Salesforce, Azure.
- Function plugin: uses one or more connector plugins to complete a vertical outcome. Examples: security analyst, data science, bug finder.

Prefer composability. Keep product capabilities in connector plugins and put workflow-specific sequencing in function plugins or skills.

## Build Sequence

1. Build the App: create an MCP server that exposes backend APIs as tools Codex can invoke.
2. Add Skills: write operational instructions for workflows, tool sequencing, terminology, confirmations, summaries, and edge cases.
3. Eval: test hero workflows and golden prompts, ideally with automated loops and realistic fixtures.
4. Submit: package skills plus the approved app, hero prompts, use cases, and review account for plugin review.

Current submission may involve separate app and plugin submissions. Design the materials so they can merge cleanly into a single flow later.

## App And MCP Tool Design

### Meet User Expectations

The app should support the core actions users reasonably expect from the product:

- Shopping: browse products and buy.
- Food delivery or coffee: browse menu and order.
- PaaS: start, stop, list, inspect, and manage servers.

Common capability categories:

- Read/query: fetch records, search data, list items.
- Write/update: create, modify, or delete records.
- Actions: trigger workflows, send notifications.
- Analytics: aggregate data, generate reports, summarize trends.

### Design For Context Efficiency

The best tools are not direct wrappers for every backend endpoint. They reduce the context Codex must inspect, make likely next actions obvious, and return enough information for downstream reasoning.

Prefer workflow-shaped tools over extremely granular endpoint mirrors, but avoid hiding all judgment inside a single opaque "do everything" tool.

Use scoped search and filters by default:

- Prefer `github_search_issues` over `list_all_issues`.
- Prefer `search_logs(query, service_id, start_time, end_time, limit)` over `list_logs(service_id)`.
- Prefer `get_customer_context(customer_id, response_format="concise")` over returning every customer field.

### Leave Workflow Judgment To Skills

Tools should expose clear capabilities. Skills should explain the right order for a workflow, when to inspect before acting, when to ask for confirmation, and how to summarize evidence.

### Tactical Tool Rules

- Design for Codex to reason over, not only for humans to click.
- Use clear names, typed inputs, and structured outputs.
- Separate read tools from write tools.
- Separate data tools from UI or rendering tools.
- Return stable IDs for follow-up calls.
- Include helpful tool annotations such as `readOnlyHint`, `destructiveHint`, `openWorldHint`, and `idempotentHint`.
- Make error messages actionable, including the missing field and a valid example when possible.

Avoid:

- overlapping tools with unclear boundaries
- mixed read/write behavior
- UI-only screenshots when underlying data is needed
- unstable or order-dependent IDs
- vague skills that do not change model behavior

## Skills

Skills are operational instructions for how to use tools and plugins. Use them to teach:

- product terminology
- which tool to use first
- when to inspect before acting
- when to ask for confirmation
- how to summarize results
- how to handle empty states, invalid IDs, auth failures, permissions, and missing data

Example pattern:

```text
When investigating a latency spike, first query metrics to identify the affected service and time window. Then search logs for errors during that window. If the issue appears user-facing or severe, summarize the evidence and ask before creating an incident.
```

Keep workflow sequencing in skills when the same tools support multiple workflows.

## Hero Prompts And Evals

Use evals to test whether Codex can complete realistic workflows, not just whether individual tools execute.

For each hero prompt, define:

- user prompt
- expected final answer or outcome
- expected tools, if tool choice matters
- required facts in the final answer
- safety behavior, especially for write actions
- data fixture or test account state

Verifier options:

- exact match for deterministic IDs, counts, states, and statuses
- contains or field checks for required facts with flexible wording
- structured rubric for summaries, recommendations, and multi-step workflows
- LLM judge when multiple valid answers exist, grounded in a clear rubric

Strong eval tasks:

- require real decision-making
- use realistic data
- often require multiple tool calls
- have a verifiable final answer or outcome

Scenario coverage:

- Capability scenarios: can Codex choose and call the right tool?
- Outcome scenarios: can Codex complete the workflow?
- Write scenarios: does Codex ask for confirmation and verify the result?
- Failure scenarios: auth, permissions, empty states, invalid IDs, missing data.

Track:

- tool choice
- argument quality
- safety behavior
- final answer quality
- latency

Review transcripts, not just pass/fail results. Look for wrong tools, invalid parameters, redundant calls, huge responses, cryptic IDs, ambiguous tool names, and successful but inefficient paths. If Codex always calls the same tools in the same sequence, consider consolidating that workflow into one context-efficient tool.

## Auth

Auth should minimize drop-off while preserving safety.

- Use OAuth 2.0 when user auth is required.
- Prefer tool-level auth over gating the whole plugin.
- Offer guest, demo, or mixed-auth flows where possible.
- Provide a production review account with realistic dummy data when possible.

Good pattern:

- Public search and reads work unauthenticated.
- Private data, comments, commits, checkout, order history, and other sensitive writes request auth only when needed.

Poor pattern:

- Requiring OAuth for public repository search.
- Requiring account auth before a user can browse product inventory.

## Namespacing And Tool Specs

Use names that make ownership and purpose obvious:

- `github_search_repos`
- `github_list_pull_requests`
- `linear_create_issue`
- `datadog_search_logs`

Avoid generic names:

- `search`
- `list`
- `create`
- `get_data`

Tool descriptions are part of the agent experience. Include:

- what the tool is for
- when to use it
- when not to use it
- required IDs or preconditions
- examples of valid inputs
- what the response contains
- whether the tool reads, writes, deletes, or has side effects

Use precise parameter names:

- `user_id` instead of `user`
- `start_time` and `end_time` instead of `date`
- `repository_owner` and `repository_name` instead of `repo`

Example strong tool spec:

```text
github_search_issues(repository_owner, repository_name, query, state, limit)

Search issues in a specific GitHub repository. Use when the user asks about bugs, feature requests, open issues, or issue history. Do not use for pull requests or commits.

Returns issue_id, title, state, author, created_at, url, and summary.
```

## Context-Efficient Responses

Return information Codex can reason over:

- human-readable names
- stable IDs for follow-up calls
- timestamps, statuses, owners, links, and summaries
- a short explanation of why each result matched

Avoid:

- raw UUIDs with no labels
- large opaque blobs
- UI-only screenshots
- technically complete fields that do not help the next decision

Good log result shape:

```json
{
  "log_event_id": "log_123",
  "service": "checkout-api",
  "timestamp": "2026-04-29T10:42:00Z",
  "severity": "error",
  "message": "Payment authorization timed out",
  "why_relevant": "Matches the checkout latency spike window"
}
```

Use:

- search and filters
- pagination
- time ranges
- result limits
- concise versus detailed response modes where useful
- truncation messages that explain how to narrow the query

Avoid returning every object, full records when summaries are enough, or raw errors such as `400 invalid_request` without recovery guidance.

## Maintenance

Treat tools and skills as living product surfaces. Maintain:

- hero prompts and evals as product behavior changes
- tool descriptions when schemas or workflows change
- skills when users discover better workflows
- review/demo accounts with fresh dummy data
- error messages and edge cases from failed evals
- backward compatibility for stable IDs and common tool outputs

Re-run evals when a tool schema changes, a skill changes, auth or permissions change, a backend API changes, tools are added/removed/renamed, or repeated user failures appear.

## Submission Checklist

- App exposes a focused v1 capability set.
- Tools have clear names, schemas, outputs, IDs, annotations, and side-effect boundaries.
- Read/write and data/UI tools are separated.
- Skills are scoped to real workflows.
- Auth, guest/demo path, and review account are ready.
- Hero prompts and repeatable eval scenarios are documented.
- Plugin metadata is complete, including logos and clear value explanation.

## Simple Eval Loop

The smallest useful eval loop gives the agent one task, lets it alternate between model calls and tool calls, then grades the final answer against the golden spec.

```python
def run_eval(case, tools, max_steps=8):
    messages = [
        {"role": "system", "content": "Use tools when needed. Return a final answer."},
        {"role": "user", "content": case["prompt"]},
    ]
    transcript = []

    for _ in range(max_steps):
        response = call_model(messages, tools=tools.schemas)
        transcript.append(response)

        if response.tool_call:
            name = response.tool_call.name
            args = response.tool_call.args
            tool_result = tools[name](**args)
            messages.append(response.to_message())
            messages.append({
                "role": "tool",
                "tool_call_id": response.tool_call.id,
                "content": tool_result,
            })
            continue

        final_answer = response.text
        break

    return {
        "passed": case["expected"] in final_answer,
        "final_answer": final_answer,
        "transcript": transcript,
    }
```

Example case:

```python
case = {
    "prompt": "Find checkout errors from the last hour and summarize the likely cause.",
    "expected": "payment authorization timeout",
}
```

Replace the simple contains check with exact match, field checks, a structured rubric, or a rubric-grounded judge when the workflow needs it.
