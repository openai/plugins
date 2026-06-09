---
name: brighthire
description: Use BrightHire tools when a user asks about BrightHire interview intelligence, calls, candidates, roles, scorecards, transcripts, hiring decisions, or organization-level interview data.
---

# BrightHire

Use BrightHire tools when the user asks for information stored in BrightHire or asks Codex to reason about interview intelligence from BrightHire data.

Good fits include:

- Finding calls, interviews, candidates, roles, interviewers, scorecards, or transcripts.
- Summarizing interview context for a hiring decision.
- Looking up evidence from BrightHire before answering questions about a candidate or role.
- Comparing interview feedback, themes, concerns, or evidence across calls.

Before using BrightHire data, identify what entity the user means: candidate, role, organization, call, interviewer, or date range. If the request is ambiguous and multiple BrightHire records may match, ask a concise clarifying question or search broadly and present the likely matches.

Treat BrightHire content as sensitive customer data. Do not expose more candidate, interviewer, or organization information than the user asked for. Prefer concise summaries with links or identifiers when available, and avoid copying long transcript passages unless the user explicitly needs exact evidence.

If a BrightHire tool fails because authentication is missing or expired, tell the user they need to connect or re-authenticate the BrightHire plugin. Do not ask for raw API tokens in chat.
