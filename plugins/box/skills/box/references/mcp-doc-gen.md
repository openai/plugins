# Box Doc Gen

## MCP

### Tools

- Templates: `list_docgen_templates`, `get_docgen_template_by_id`, `create_docgen_template`
- Generation: `create_docgen_batch`

### Security guidelines

`create_docgen_template` requires edit permissions on the file — if the call fails on permissions, don't attempt a workaround; tell the user they need edit access to the file to mark it as a template.

Before running `create_docgen_batch`, confirm the `destination_folder_id` with the user if it wasn't explicitly specified — generated documents land there, and misdirecting output (especially into an externally shared folder) is a meaningful side effect.

Confirm `user_input` data with the user before executing a docgen batch.

### Tool selection

`create_docgen_template` only marks an existing file as a Doc Gen template. It takes just a `file_id`; it doesn't write or insert any tags into the file's content.

Before generating documents, confirm a template actually exists for the use case:

- `list_docgen_templates` — check whether a suitable template is already registered.
- `get_docgen_template_by_id` — confirm the template's file reference and friendly name before using its `file_id` in a batch.

Template tags only support English. If a user needs another language, flag this limitation rather than assuming the template will work.

Only .docx and .pptx files can be marked as Doc Gen templates, and the file must already contain valid placeholder tags (e.g. `{{customer_name}}`) created in Microsoft Word, typically via the Doc Gen Template Creator add-in. AI clients cannot author placeholder tags into a file on the user's behalf — tag creation happens in Word, not through the API.

When a user asks to generate documents from a template:

- Confirm the template's placeholder fields (from the template's known tags or by asking the user) before constructing `user_input` — guessing field names that don't match the template's tags will silently fail to populate or error out.
- Always tell the user which template (`file_id` / friendly name) and which output type (pdf or docx) was used for a generation call.

### Doc Gen workflows

### Register a new template

1. Confirm the file is .docx or .pptx and already contains placeholder tags.
2. `create_docgen_template` with the file's ID.
3. Confirm with the user that the template registered correctly via `get_docgen_template_by_id` before generating documents against it.

### Single-document generation

1. Identify the template via `list_docgen_templates` or a known `file_id`.
2. `create_docgen_batch` with one entry in `document_generation_data`, providing a `generated_file_name` and `user_input` matching the template's placeholder tags.

Best suited for one-off documents (e.g., a single offer letter or invoice) rather than recurring batch runs.

### Batch generation from a dataset

1. Gather the dataset (e.g., a list of customers, deals, or line items) the user wants merged into the template.
2. Build one `document_generation_data` entry per record, with distinct `generated_file_name` values so outputs don't collide in the destination folder.
3. `create_docgen_batch` with the full array in a single call rather than looping per-record — unlike `ai_extract_*`, batch generation natively supports multiple documents per request.

Confirm record count and destination folder with the user before submitting large batches, since generation is asynchronous and harder to course-correct mid-run.

### Error handling

If `create_docgen_template` fails because the file isn't .docx/.pptx or lacks valid tags, don't attempt to add tags programmatically — tags must be authored in Word. Tell the user what's missing.

If `create_docgen_batch` returns a mismatch between provided `user_input` keys and the template's expected placeholders, surface the specific field names rather than re-submitting blindly — guessing at corrected field names risks generating documents with silently blank sections.

There is no native multi-template batch call — each `create_docgen_batch` call targets one `file_id` (template). If a user wants documents generated from several different templates, make one batch call per template rather than trying to combine them.
