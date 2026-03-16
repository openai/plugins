# Label Actions

Read this file when the user wants to apply labels, relabel matching mail, or do mailbox cleanup that depends on labels.

## Tool Shapes

- `apply_labels_to_emails` expects:
  - `message_ids: list[str]`
  - `add_label_names: list[str]`
  - `remove_label_names: list[str]`
  - `create_missing_labels: bool`
- Even one label name must be wrapped in a list, for example `add_label_names: ["Google Docs"]`.

## Choosing the Label Tool

- Prefer `bulk_label_matching_emails` when the task can be expressed as a clear Gmail query and the user wants to label all matching mail.
- Prefer `apply_labels_to_emails` when you already inspected results and selected a specific shortlist of message IDs.
- Prefer Gmail search refinement before labeling. Tighten the query first rather than labeling a noisy result set and cleaning it up later.

## Labeling Pattern

1. Build or refine a Gmail query that matches the intended set.
2. Inspect a small sample if the classification is heuristic or ambiguous.
3. Use `bulk_label_matching_emails` for broad backfills driven by query logic.
4. Use `apply_labels_to_emails` for hand-picked message lists, and always pass label names as arrays.
5. Keep label changes separate from analysis in the response, and make it clear what was labeled and why.
