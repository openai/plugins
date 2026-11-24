# Upload knowledge documents

Use this workflow for a selected PDF, image, Office document, or Markdown file
destined for an existing knowledge volume. Use the live Tool's allowed formats
and size limits, including the selected Space's stricter limits.

MCP selects the current Space's Knowledge Runtime for knowledge SQL. Omit
Compute arguments from upload and status calls. If a knowledge tool reports
that the Space has no Knowledge Runtime, stop knowledge calls and direct the
user to **Compute → Knowledge Warehouse → Enable** in that Space's web console.
Resume only after the warehouse is enabled. For permission or service errors,
report the returned error.

1. Resolve the actual source and the conversation's Space. Reuse a readable
   workspace file, attachment, or task-generated document. Inspect only what is
   needed to verify its format, size, and the user's requested preparation;
   preserve the original when producing a prepared output.
2. Resolve the exact destination Catalog, Schema, and knowledge volume. Inspect
   `cognitivedb_knowledge_context_get` and the bounded volume listings as needed.
   A knowledge volume is distinct from a Table. Ask about ambiguous targets
   before uploading, and obtain approval for the exact source and destination.
3. Call `cognitivedb_knowledge_file_stage_upload` with the selected file and Space.
   Use `fileName` only when the source lacks filename metadata. Retain the
   returned `source`, suggested `path`, and `tempFileId`. This stages a temporary
   object; each successful call creates a new object. After an uncertain result,
   report the uncertainty rather than repeating the staging operation.
4. With the requested destination and write approval, call
   `cognitivedb_knowledge_upload` with the staged `source` and `path`, and the approved
   Catalog, Schema, and volume. Preserve the suggested path unless the user requested a
   different destination. Replacing an existing document needs explicit
   approval: overwrite deletes the old document first and is not atomic.
5. Preserve the returned execution and upload task identifiers. If the SQL
   execution is pending, obtain its result with
   `cognitivedb_knowledge_execution_result_get`; then query
   `cognitivedb_knowledge_upload_status_get` for the same uploader, volume, and task.
   Wait at least three seconds between checks, increase the interval, and stop
   automatic polling after twenty checks or when user action is required.
6. Report publication only after task status `SUCCEEDED` or external result
   `UPLOAD_SUCCEEDED`. A staged object or successful SQL execution alone does not
   establish publication. Include the exact destination and verified task state;
   retain the temporary identifier for any separately authorized cleanup.

If the upload outcome is uncertain after submission, use its task or execution
identifier to inspect the same operation. Any intentional resubmission must
follow the live Tool's idempotency contract and preserve the original arguments.
