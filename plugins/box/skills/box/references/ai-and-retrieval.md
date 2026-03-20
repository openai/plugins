# AI and Retrieval

## Table of Contents

- Search-first strategy
- Content understanding preference order
- Choose Box AI vs external AI
- Retrieval guardrails
- Verification checklist
- Primary docs

## Search-first strategy

- Use Box search before recursive folder traversal or bulk download.
- Narrow the candidate set with ancestor folders, object type, filenames, owners, or metadata filters whenever possible.
- Return stable IDs and lightweight metadata first, then retrieve content only for the final shortlist.

## Content understanding preference order

When the task requires understanding what a document contains (classification, extraction, summarization, Q&A), prefer Box-native methods first:

1. **Box AI Q&A or Extract** — keeps content server-side, no downloads needed.
2. **Metadata inspection** — check existing Box metadata templates or properties.
3. **Previews or thumbnails** — lightweight visual inspection without downloading the full file.
4. **Local analysis (OCR, agent-side parsing)** — download and process locally only when the above methods are unavailable, not authorized, or insufficient.

If the first Box AI call fails with a 403 or feature-not-available error, switch to the next method immediately rather than retrying AI for the remaining files.

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

### Box AI pacing

Box AI endpoints have tighter per-user/per-app rate limits than standard content API calls. Pace AI calls at least 1–2 seconds apart. For bulk classification workflows, use the sample-first strategy described in `references/bulk-operations.md` to minimize the total number of AI calls.

## Choose Box AI vs external AI

- Prefer Box AI when the task maps directly to Box-native document question answering, extraction, or summarization.
- Use an external AI pipeline only when the product needs model behavior that Box AI does not provide or the application already owns the reasoning layer.
- Check the current official Box AI docs before changing prompts, capabilities, or supported object flows.

## Retrieval guardrails

- Avoid pulling raw file bodies when metadata, previews, or Box-native answers are enough.
- Keep retrieval scoped to the smallest relevant set of files.
- Preserve traceability with file IDs, names, shared links, or citations when the product needs auditability.
- Confirm with the user before broad retrieval across large folders or sensitive content sets.

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
