# Label Actions

Read this file when the user wants to apply labels, relabel matching mail, or do mailbox cleanup that depends on labels.

## Tool Shapes

- `archive_emails` expects:
  - `message_ids: list[str]`
- `delete_emails` expects:
  - `message_ids: list[str]`
- `apply_labels_to_emails` expects:
  - `message_ids: list[str]`
  - `add_label_names: list[str]`
  - `remove_label_names: list[str]`
  - `create_missing_labels: bool`
- Even one label name must be wrapped in a list, for example `add_label_names: ["Google Docs"]`.

## Choosing the Label Tool

- Prefer `bulk_label_matching_emails` when the task can be expressed as a clear Gmail query and the user wants to label all matching mail.
- Prefer `apply_labels_to_emails` when you already inspected results and selected a specific shortlist of message IDs.
- Prefer `archive_emails` or `delete_emails` when the user directly asks to clean up, archive, delete, remove, or trash a selected set of messages.
- Prefer Gmail search refinement before labeling. Tighten the query first rather than labeling a noisy result set and cleaning it up later.

## Confirmation Boundary

- A direct cleanup instruction in the current request is enough approval to apply labels, archive, or move messages to Trash after the matching set is reasonably identified.
- For heuristic categories such as recruiter cold emails, inspect a sample or shortlist first, then act on high-confidence matches. Ask only if the remaining matches are uncertain enough that acting would likely surprise the user.
- For broad cleanup such as calendar updates, build a narrow Gmail query, inspect enough results to verify the pattern, then use the selected message IDs or a bulk label action. Do not ask for a second confirmation just because the action changes mailbox state.
- Ask before acting when the search scope is vague, many unrelated messages appear in the result set, the request could affect another mailbox, or the user asked for recommendations rather than an action.

## Labeling Pattern

1. Build or refine a Gmail query that matches the intended set.
2. Inspect a small sample if the classification is heuristic or ambiguous.
3. Use `bulk_label_matching_emails` for broad backfills driven by query logic.
4. Use `apply_labels_to_emails` for hand-picked message lists, and always pass label names as arrays.
5. Use `archive_emails` or `delete_emails` for hand-picked cleanup lists.
6. Keep mailbox changes separate from analysis in the response, and make it clear what changed and why.
