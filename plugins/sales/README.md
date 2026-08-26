# Sales

Bring customer context, daily account work, pipeline progress, and leadership decisions into the work that moves deals forward.

## When to use this plugin

Use Sales when you need a seller account home or sales leadership dashboard, want to prepare for customer meetings, follow up after calls, understand account movement, plan deals, build business cases and customer decision decks, turn evaluation calls into readout decks, review forecasts, find customer quotes, coach reps from calls, build competitive guidance, find internal answers, prioritize accounts when useful, enrich company or contact data, or use CRM and Sales Intelligence context.

## Get started

Try asking:

`@Sales Help me get started`

The plugin will help connect the sources the current workflow needs and recommend a useful first workflow.

You can also jump directly into any workflow below.

For a customer-ready commercial artifact, try:

`@Sales Build a business case for Acme's support automation initiative, then turn it into an 8–12 slide decision deck`

For a material clarification with two or three highly likely answers, Sales follows [User Input](shared_skill_instructions.md#user-input) and uses `request_user_input` when available instead of asking the same question in chat. When a selected workflow has a material missing source, Sales follows [Missing Sources And Fallbacks](dependencies.md#missing-sources-and-fallbacks): it first looks for suitable installable providers and uses `request_plugin_install` to offer them before requesting pasted context. If the structured tool is unavailable or the answer is open-ended, Sales asks one concise question in chat.

## Example workflows

| Workflow | Try this | Skill | Result |
| --- | --- | --- | --- |
| Open your seller account home | `Show me my account home across daily work, accounts, and pipeline` | `seller-account-dashboard` | A customizable, source-grounded seller dashboard with **Home** for daily work, **Accounts** for the complete customer book, and **Pipeline** for opportunities grouped by their current blocker and next action |
| Open your sales leadership dashboard | `Build my executive dashboard from our actual forecast, priority accounts, and team performance` | `sales-leadership-dashboard` | A customizable leadership operating canvas with **Forecast & key metrics**, **Account Focus**, and **Team Focus**, grounded in actual division, customer, and seller evidence |
| Explore the executive and seller dashboard demo | `Show me the Sales demo` | `demo-exec-and-seller-dash` | A guided executive-first walkthrough showing the three-view seller account home, customer follow-up, and reviewed CRM updates |
| Prepare for a customer meeting | `Prep me for my next customer meeting` | `prepare-for-meeting` | A concise meeting brief with agenda, context, likely blockers, and next actions |
| Follow up after a call | `Turn my latest customer call into a follow-up package` | `follow-up-after-call` | A grounded recap, customer and seller actions, email copy, CRM-ready text, and internal recap draft |
| Build a business case and decision deck | `Build a business case for Acme's support automation initiative, then create the customer deck` | `build-business-case` + `sales-presentations` | A customer-led value case and editable 8–12 slide decision deck with workflows, value, commercial structure, proof, assumptions, and decision requested |
| Analyze account signals | `What changed with Acme in the last two weeks?` | `analyze-account-signals` | An evidence-backed account brief or bounded watchlist summary with recommended actions |
| Plan an active deal | `Build a strategy for the Acme renewal` | `plan-deal-strategy` | A deal map, buying committee, procurement risks, and prioritized next actions |
| Review a forecast | `Review my forecast for risk and next actions` | `review-forecast` | A manager-ready rollup with risk posture, recommendation changes, and evidence gaps |
| Build competitive guidance | `Build a competitive brief for Acme against Competitor Alpha` | `build-competitive-brief` | A source-backed HTML brief with comparison matrix, objection guidance, and caveats |
| Find customer quotes | `Find customer quotes about setup friction from recent calls` | `find-customer-quotes` | Verbatim transcript-backed quotes with speaker confidence, provenance, and safe usage notes |
| Coach a rep from calls | `Compare Jamie's discovery calls with strong peer examples` | `get-rep-call-feedback` | Evidence-backed peer exemplars, specific coaching moments, and a practical steal sheet |
| Review rep call trends | `Review Jamie's call trends over the last three months` | `review-rep-call-trends` | Improvement, regression, stable patterns, calls to revisit, and next coaching actions |
| Find internal sources | `Find who owns this security objection and what I should read` | `find-key-internal-sources` | Ranked experts, docs, channels, and a draft-ready first ask |
| Prioritize accounts when useful | `Rank the accounts I should work this week and explain why` | `seller-account-dashboard` | An optional account-focus view with evidence, reachable contacts, suppression rules, and planning-only next steps |
| Enrich account or contact data | `Enrich this account list and flag likely buying teams` | `enrich-company-and-contact-data` | A portable enrichment table for segmentation, ICP-fit review, and outreach planning |

Seller and leadership dashboards start in a durable local project when no matching private Site exists. Sales reuses an existing dashboard and its customizations, and only creates or publishes a new private Site after you explicitly agree.

## Integrations

Sales offers its supported apps through the [app manifest](.app.json). Each app is optional and authorizes on use, subject to its own workspace and access policies. Sales can also use other available plugins, connectors, and supplied source materials. See [dependencies.md](dependencies.md) for the shared `~~category` mapping, provider examples, source authority, and fallback behavior.

Example sources include:

| Source | Supported integrations | What they unlock |
| --- | --- | --- |
| CRM | Salesforce, Agentforce Sales, HubSpot, Close | Seller and leadership dashboards, account context, opportunity evidence, CRM-ready drafts, and proposed record updates |
| Meeting notes | Zoom, Granola, Fireflies, Otter.ai | Call summaries, transcripts, customer quotes, follow-up context, and coaching evidence |
| Email and messages | Gmail, Outlook Email, Slack, Microsoft Teams, Outreach | Customer follow-up context, internal answer paths, and reviewed draft destinations |
| Documents and calendars | Notion, Google Drive, SharePoint, Google Calendar, Outlook Calendar, Calendly | Account plans, supporting docs, meeting context, and operating cadence |
| Enrichment and signals | ZoomInfo, Clay, HG Insights, Rox, Actively, Apollo, Meticulate | Company and contact enrichment, market signals, ICP discovery, and account prioritization |
| Other context | Monday.com, DocuSign | Optional task-tracker and agreement context when a workflow needs it |

Connected tools provide the smoothest path, but they are not required for every task. You can start with uploaded files, pasted notes, transcripts, exports, spreadsheets, and public research when appropriate. Source setup is lazy: Sales asks to connect only the tools needed for the task at hand.
