# AI and Retrieval

## Table of Contents

- General
  - Search-first strategy
  - Content understanding preference order
  - Box AI pacing
  - Choose Box AI vs external AI
  - Retrieval guardrails
- MCP
  - Tools
  - Security guidelines
  - Tool selection
  - Workflows
  - Error handling
- CLI
  - Box AI via CLI
- Verification checklist
- Primary docs

## General

### Search-first strategy

- Use Box search before recursive folder traversal or bulk download.
- Narrow the candidate set with ancestor folders, object type, filenames, owners, or metadata filters whenever possible.
- Return stable IDs and lightweight metadata first, then retrieve content only for the final shortlist.

### Content understanding preference order

When the task requires understanding what a document contains (classification, extraction, summarization, Q&A), prefer Box-native methods first:

1. **Box AI Q&A or Extract** — keeps content server-side, no downloads needed.
2. **Metadata inspection** — check existing Box metadata templates or properties.
3. **Text rep** — use `get_file_content` to pull the text representation of the file for local processing.
4. **Local analysis (OCR, agent-side parsing)** — use `get_download_url` to download files to local file storage and process locally only when the above methods are unavailable, not authorized, or insufficient.

If the first Box AI call fails with a 403 or feature-not-available error, switch to the next method immediately rather than retrying AI for the remaining files.

For content-based classification of many files, use the sample-first strategy in `references/bulk-operations.md` to minimize AI calls.

### Box AI pacing

Box AI endpoints have tighter per-user/per-app rate limits than standard content API calls. Space Box AI tool calls at least 1–2 seconds apart. For bulk classification workflows, use the sample-first strategy described in `references/bulk-operations.md` to minimize the total number of AI calls.

Box AI responses include citations — surface them when possible so the user can verify answers.

### Choose Box AI vs external AI

- Prefer Box AI when the task maps directly to Box-native document question answering, extraction, or summarization.
- Use an external AI pipeline only when the product needs model behavior that Box AI does not provide or the application already owns the reasoning layer.
- Check the current official Box AI docs before changing prompts, capabilities, or supported object flows.

### Retrieval guardrails

- Avoid pulling raw file bodies when metadata, previews, or Box-native answers are enough.
- Keep retrieval scoped to the smallest relevant set of files.
- Preserve traceability with file IDs, names, shared links, or citations when the product needs auditability.
- Confirm with the user before broad retrieval across large folders or sensitive content sets.

## MCP

### Tools

- Q&A: `ai_qa_single_file`, `ai_qa_multi_file`, `ai_qa_hub`
- Extraction: `ai_extract_freeform`, `ai_extract_structured_from_fields`, `ai_extract_structured_from_metadata_template`
- Enhanced extraction (more powerful, more expensive): `ai_extract_structured_from_fields_enhanced`, `ai_extract_structured_from_metadata_template_enhanced`
- Agents: `ask_agent`, `list_custom_agents`

### Security guidelines

For `ai_qa_*` tools, always provide citations with links back to the files in Box when providing answers. If possible, name a section in the file that contains the relevant information. For Hubs, specify which file the information came from.

### Tool selection

When a user asks to extract from a document, check first whether there is an available metadata template that matches their requirements. If not, ask the user whether they want you to create a metadata template for more structured extractions (if they have permissions to use the `create_metadata_template` tool).

Prefer using an `ai_qa_*` tool for simpler extract queries, especially if it is a freeform extract request.

Use `ask_agent` when:

- You need a custom agent's specific configured behavior (check `list_custom_agents`).
- The task is interpretive/judgment-based ("assess the risk here") rather than retrieval-based.
- The question is open-ended, not scoped to a known file set, or includes referencing across files, folders, and hubs.

Even if the extract prompt is in natural language, try to use `ai_extract_structured_from_fields` and define the fields for the user.

Only use the enhanced extract tools if the user explicitly asks you to. Require human in the loop to continue, citing that although the enhanced extract tools are more powerful and good for complex documents, they are also more expensive.

Always tell the user which metadata template was used for an extract tool call.

Always prefer to query a hub instead of doing multi-file Q&A on the files inside of a hub.

### Workflows

### Single-file Q&A

1. Identify the target file (via `search_files_keyword` or a known file ID).
2. `ai_qa_single_file` with the file ID and a specific question.

Best suited for direct lookups ("what's the termination clause in this MSA") rather than open-ended summarization — keep questions narrow, since single-file Q&A works best against one document's actual content rather than inferred context.

### Cross-document Q&A across a known file set

1. Gather the relevant file IDs (e.g., a deal's contract + amendments + addenda) via search or a folder listing.
2. `ai_qa_multi_file` with the file IDs and a comparative or synthesizing question ("which of these contracts has the shortest notice period for termination").

Useful when the question spans documents but you don't want the broader scope of a hub-level Q&A — keep the file list deliberate and small rather than dumping in an entire folder, since relevance and answer quality degrade as the set gets noisier.

### Structured extraction against a metadata template

1. Confirm the template exists via `list_metadata_templates` or `get_metadata_template_schema`; create one with `create_metadata_template` if not.
2. `ai_extract_structured_from_metadata_template` (or the enhanced variant for higher-accuracy extraction) on the target file, referencing the template key.
3. `set_file_metadata` to persist the extracted structured values onto the file, making the data queryable later via `search_files_metadata`.

For batches, loop per-file rather than expecting a multi-file extraction call — there's no native batch extraction tool, so pacing matters.

### General-purpose agent query with custom instructions

1. `ask_agent` for a query that doesn't map cleanly to a single-file, multi-file, or hub Q&A pattern — e.g., a question requiring the agent to reason across loosely structured context rather than strictly retrieve-and-answer.
2. Check `list_custom_agents` first if your org has configured specialized agents (e.g., a legal-review agent), and route to the matching one rather than the default if relevance favors it.

Treat `ask_agent` output as more interpretive/narrative than the extraction tools — better for "what's the overall risk profile of this filing" than for pulling a discrete data point, where `ai_extract_*` is the better fit.

### Error handling

`ai_qa_*` tools use the text representation of a file and only support up to 1MB of text rep. If the text rep of a file is beyond 1MB, download the file into local storage and process it that way.

`ai_extract_*` tools have a 50-file max per request. When more than 50 files need to be extracted, chunk the tool calls and do one call for files 1–50, a second call for 51–100, etc.

## CLI

### Box AI via CLI

**Before the first AI call**, run `box ai:ask --help` to confirm the command exists in the installed CLI version.

Ask a question about a file's content:

```bash
box ai:ask --items=id=<FILE_ID>,type=file \
  --prompt "Summarize this document in one sentence." \
  --json --no-color
```

Extract key-value pairs via a freeform prompt:

```bash
box ai:extract --items=id=<FILE_ID>,type=file \
  --prompt "document_type, vendor_name, date" \
  --json --no-color
```

Extract with typed fields or a metadata template:

```bash
box ai:extract-structured --items=id=<FILE_ID>,type=file \
  --fields "key=document_type,type=enum,options=invoice;receipt;contract;other" \
  --json --no-color
```

Reference: https://github.com/box/boxcli/blob/main/docs/ai.md

An "Unexpected Error" with no HTTP body and exit code 2 may indicate the CLI version does not support AI commands, Box AI is not enabled for the account, or the file type is not supported. Run `box ai:ask --help` to verify the command exists, and try with a known-supported file type (PDF, DOCX) before falling back.


## Verification checklist

- Retrieval quality:
  - Confirm the search filters and candidate set contain the intended documents.
- Answer grounding:
  - Confirm the final answer can point back to the specific file IDs or names used.
- Access control:
  - Confirm the acting identity can only see the content the product is supposed to expose.

## Primary docs

- Search reference:
  - https://developer.box.com/reference/get-search/
- Box AI guides:
  - https://developer.box.com/guides/box-ai/
- Box AI with objects:
  - https://developer.box.com/guides/box-ai/use-box-ai-with-box-objects/
- Box CLI AI commands:
  - https://github.com/box/boxcli/blob/main/docs/ai.md
