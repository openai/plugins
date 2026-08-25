# Gmail

This plugin packages OpenAI-maintained Gmail workflows for searching mail,
reading threads, drafting and organizing messages, and triaging an inbox.

Pasted Gmail mailbox links use a deliberately bounded best-effort workflow.
The skill extracts an opaque token only from known mailbox URL shapes, tries
exact message and thread reads, and stops with fetchable alternatives when the
token cannot be resolved. Gmail does not document a general browser URL token
to API ID mapping, so arbitrary Gmail URLs are not claimed as supported.
