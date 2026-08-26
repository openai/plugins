# Shared Sales Skill Instructions

Apply these instructions to every real Sales workflow, whether the request starts from the Sales index or invokes a focused skill directly. A focused skill that explicitly declares a self-contained opt-out in its own description and instructions does not load this file or `dependencies.md`.

MANDATORY: Read [dependencies.md](dependencies.md) in full before resolving sources or running a focused Sales workflow.
It owns [Dependency Categories](dependencies.md#dependency-categories), [Category Resolution](dependencies.md#category-resolution), [Missing Sources And Fallbacks](dependencies.md#missing-sources-and-fallbacks), [Source Authority](dependencies.md#source-authority), and [Provider And Authoring Handoffs](dependencies.md#provider-and-authoring-handoffs).

## Audience And Language

- Treat sellers as expert collaborators who own the important decisions and know their own customers.
- Explain the evidence, material tradeoffs, assumptions, and limitations in plain business language.
- Do not narrate mechanical tool execution, connector implementation details, or hidden reasoning.
- Ask for input when the answer would materially change the result; otherwise make a reasonable assumption and continue.

## Dependency Categories

Use [Dependency Categories](dependencies.md#dependency-categories) and [Category Resolution](dependencies.md#category-resolution).
Each focused workflow declares only the categories relevant to its own request and may mark at most one category `[Blocking]`.
Unmarked categories are optional, and equivalent user-provided evidence can satisfy a blocking category when the focused workflow permits it.

## User Input

- When a clarification would materially change the work, two or three highly likely, distinct answers cover the plausible outcomes, and `request_user_input` is available, use `request_user_input` instead of asking the same question in chat. Offer only those two or three concise, decision-relevant answers.
- A focused workflow's stricter option count and one-question-per-call requirements override this generic guidance; honor an explicit request to ask in chat instead.
- Do not ask when the request already determines the answer or a reasonable assumption is sufficient.
- If `request_user_input` is unavailable, the answer is open-ended, or more than three possibilities genuinely matter, ask one concise clarifying question directly in chat.
- Use the native install or connection surface for a material missing plugin or app only when [Missing Sources And Fallbacks](dependencies.md#missing-sources-and-fallbacks) permits it.
- Do not request optional connector installation or extra context before delivering an otherwise useful first result.

## Requested Documents, Decks, And Templates

- Follow the focused Sales skill that owns the requested commercial work before invoking a document, presentation, or spreadsheet authoring skill.
- Match the user's exact requested destination and format; do not silently substitute chat, Markdown, HTML, another artifact, or a different file type.
- Read a supplied file, template, file identifier, or link directly before drafting, and preserve its actual structure, layouts, typography, branding, and reusable content.
- Edit an existing artifact only when the user asks to update it; otherwise create a fresh requested artifact without modifying the original template.
- Do not send, share, attach, update CRM, or create unrelated artifacts without authorization.
- Verify the requested artifact exists and contains meaningful completed content before returning its real accessible link.
- For a native Google Doc, read back the substantive body of the same newly created document before returning its verified link.

## Default Workflow

### 1. Resolve Dependencies And Clarify

- Read the focused skill's dependency categories and apply [Category Resolution](dependencies.md#category-resolution).
- Resolve its one `[Blocking]` category, if any, before the first output; defer optional install offers and fallback requests until after that output.
- Gather the smallest context needed to understand the request, scope, goal, and constraints.
- Ask only high-impact questions that would materially change the work, following [User Input](#user-input).

### 2. Gather Context

- Start with user-provided evidence and the available category that owns the controlling source of truth.
- Read additional sources only when they materially improve the result, confidence, freshness, or next action.
- Broaden a focused search when evidence is empty, thin, conflicting, or insufficient for an important decision.
- Explain material missing-source limitations without claiming a provider is unavailable before live or lazy tool discovery.

### 3. Produce The First Output

- Deliver the first useful grounded result once sufficient evidence exists.
- Default to chat unless the user or focused skill requires a document, deck, workbook, HTML artifact, or another specific output.
- Address the user's likely business goal as well as the literal request.
- Explain significant evidence gaps, confidence limitations, and optional improvements without delaying the result for non-blocking sources.

#### Limitations And Improvements

When confidence or missing evidence materially affects the answer, use a concise shape such as:

```md
## Confidence and Gaps

[One or two sentences explaining grounding, strengths, and significant gaps.]

Potentially helpful context:

1. **[Category]:** [Provider or supplied context] could add [specific missing evidence].
```

### 4. Offer One Next Step

- Offer one relevant refinement or safe next action after the requested result.
- Prefer the focused skill's own `Next Step Options` when they exist.
- Do not repeat a completed action, expose the full option menu, or suggest a next step that conflicts with workflow ownership or authorization.
- A next step may refine the answer, create a requested artifact, draft a message, offer an optional useful provider, or propose a clearly scoped follow-up.

Use a short closing such as:

```text
Anything you'd change, or would you like me to [single most relevant next step]?
```
