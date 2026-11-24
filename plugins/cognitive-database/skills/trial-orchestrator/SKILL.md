---
name: trial-orchestrator
description: >-
  Guide a three-question experience when the user asks to try Cognitive
  Database (CognitiveDB or CogDB), start the DABstep payment analytics
  experience, or start the OfficeQA financial document Q&A experience.
  Use for explicit guided experience requests.
metadata:
  version: "dev-5.8.4-chatgpt.12"
---

# Marketplace Trial Orchestration

Run the trial as a conversation, not a form. Keep round counting, profile
resolution, and recommendation grouping internal; user-visible copy never
mentions rounds, quotas, or trials.

## Boundaries

- Own trial activation, profile resolution, question recommendation, round
  counting, and wrap-up. For OfficeQA, own experience guidance only;
  the agent determines how to answer questions.
- The DABstep trial never performs DML, DDL, imports, uploads, or resource
  mutations. It consumes an already-approved Compute and never creates,
  starts, or stops one; Compute sizing/lifecycle questions follow
  Task Routing.
- The trial ends after three answered rounds or an explicit user stop; a
  round counts once its question is answered. Afterwards, hand same-product
  requests to the ordinary Q&A path
  in Task Routing without question-group recommendations; a trigger
  naming a different trialed product starts a fresh trial.

## Product Profiles

For an explicit request to try Cognitive Database without naming an experience,
offer DABstep and OfficeQA in the conversation. Recognize CognitiveDB, CogDB,
and the localized product name. If the user names one experience, open that
experience directly. Route product information questions and ordinary analysis
or document Q&A through their usual paths.

Before Space-scoped resource discovery or execution, follow `cognitivedb-discipline`.
Prepare the first choice in one step: read the local question pools for the
eligible experiences and resolve Space candidates on the intended connection.
Reuse a Space already selected in this conversation; otherwise call
`cognitivedb_space_list`. Stop if no Space is available. Defer sample-data,
Catalog and Compute discovery until the user submits a Space.

Render one [experience picker](references/setup-card.html) for experience, first
question and Space. Preserve the embedded stylesheet when rendering the picker
or later question buttons. Read both profiles when offering a choice. With a
named profile, show it selected and include only that profile. Repeat the radio
row for the first three verbatim questions in each offered profile. Honor a supplied custom question
by including it selected. Populate Space options with the returned project IDs,
names and organizations. Preselect only a resolved user choice. Replace SETUP
with a unique instance ID, escape attribute values and label text, and localize
the controls. Switching profiles updates the questions locally. A single submit
sends the chosen profile, question and Space together. Resolve the submitted
Space ID against those candidates; use it for the answer without a second picker.
Use the analysis Skill's interactive-first approval for read-only SQL on the
resolved target and Compute. Submitting the experience picker selects the question
within the chosen Space. Obtain SQL approval separately. If all choices
were already explicit, proceed directly. Accept custom choices in chat.
Without GenUI follow-ups, collect the outstanding choices in one chat message
using profile-grouped questions and the same Space candidates.

Use the selected experience's sample sources in `cognitive_database_sample_data`:
the `dabstep` schema or the `officeqa.benchmark_v1` knowledge volume. If the
required data cannot be accessed in the selected Space, explain the limitation
and offer the other experience. Count only evidence-backed answers.

Resolve the profile from the user's choice and keep it fixed until the trial ends:

- `dabstep` — DABStep Payment Analytics. For analysis, follow the guidance in [Finance analytics
  profile](references/finance-analytics-profile.md).
- `officeqa` — OfficeQA Financial Document Q&A. Read
  [OfficeQA profile](references/officeqa-profile.md) for the introduction
  and built-in questions.

The only available profiles are `dabstep` and `officeqa`. If an explicit
experience request names both, offer both in the picker.
Never mix products in a session. The profile is fixed until the trial ends:
a mid-trial same-product trigger never restarts it; a mid-trial trigger for
the other trialed product is an explicit stop that starts a fresh trial.

## Core Instructions

- Introduce the experience briefly. Use the experience picker for the first question.
  For subsequent groups in the same experience and Space, render the
  [question buttons](references/question-buttons.html) with a unique ROUND ID
  and three HTML-escaped labels. Accept a custom reply in chat. If inline
  follow-ups are unavailable, offer the same questions in chat.
- Recommend three built-in questions in profile order, preferring never-shown
  entries, then previously shown but unanswered entries; reuse answered entries
  only after every question has been shown. Keep question labels verbatim.
  Invite a selection or a custom question without an extra yes/no continuation gate.
- Track answered questions within this trial, not tool calls, approvals, or
  messages. Count each answered question once;
  corrections and brief follow-ups belong to that same question. An independent
  in-domain custom question counts; an out-of-domain request does not: explain
  the scope briefly and offer an in-pool alternative. Unanswered, failed, or
  abandoned questions do not count.
- For DABstep, analyze independently through `cognitivedb-data-analysis`.
  Follow `cognitivedb-data-analysis` for target and Compute approval, reuse,
  failures, and replacement; add no approval or retry exception. If that Skill
  cannot be loaded, report the analysis service unavailable and stop the question
  without counting it or substituting memory or ungoverned SQL.
- Keep progress brief and user-relevant. Show material choices or delays, not
  catalog-discovery narration, Skill loading, query construction, or tool details.
- Lead with the independently computed answer value, followed by one short
  explanation of the result. Omit standalone source/metric/scope lines and
  technical provenance footers unless the user asks for them. For DABstep,
  retain supporting evidence internally.
  Built-in `guidelines` and formatting clauses constrain that
  value (units, rounding, yes/no, comma lists), not the surrounding experience
  explanation or recommendation.
  An explicit user request limiting the entire reply takes precedence: keep that
  reply answer-only without a question group or wrap-up. On a later message,
  honor the user's new request and the existing answered count; do not
  interpret a built-in formatting clause alone as such a request.
- After the first or second answered question, deliver the answer and brief explanation
  in a continuing message, then present the next question group using the
  interaction rule above. The answer and next selection form one complete
  interaction; wait for the selection instead of ending at the answer alone.
- After the third answered question, include a brief wrap-up inviting further
  questions in the same final response, with no new question group. Read the
  current Space's project id once via `cognitivedb_space_current_get` and include
  `https://console.transwarp-cloud.com/saas/project/<project_id>/marketplace`.
  Use only an explicitly returned project id. If unavailable, failed, or missing,
  still deliver the wrap-up without the link; do not retry. Example:
  "You've explored what these data can reveal. Ask me another question whenever
  you're ready, or explore more applications in the Marketplace." Append the
  verified link when available.
- On an explicit user stop, acknowledge briefly and end without recommendations,
  a completion congratulation, or pending continuation. After the normal wrap-up,
  use Task Routing for further requests; do not repeat the wrap-up.

## Task Routing

- For DABstep, route analysis to `cognitivedb-data-analysis`;
  on load failure follow the unavailable-service behavior in Core Instructions.
- For DABstep, route Compute sizing, lifecycle, or compatibility questions to
  `cognitivedb-manage-computes`.
- After the trial, stop recommending pool question groups. DABstep continues
  through `cognitivedb-data-analysis`.
  For OfficeQA, end experience guidance and leave subsequent questions to the agent.
- Outside OfficeQA, route unrelated ordinary database analysis to
  `cognitivedb-data-analysis`.

## Allowed MCP Tools

- `cognitivedb_space_current_get`
- `cognitivedb_space_list`
