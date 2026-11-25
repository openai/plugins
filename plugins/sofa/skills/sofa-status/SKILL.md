---
description: 'Use to inspect the hosted SOFA plugin''s authenticated connection, selected-agent
  identity, plugin-guidance compatibility, current capabilities and scopes, or active-session
  activity summary. This skill does not create or modify SOFA knowledge or public
  state.

  '
name: sofa-status
---

# Check Hosted SOFA Status

Use this skill when the user asks about the authenticated connection, the
selected-agent identity, plugin-guidance compatibility, current capabilities
and scopes, connection expiry or publication policy, or what happened in the
current SOFA session.

## Connection Status

1. Whenever beginning or resuming a SOFA session, read the installed package's
   `plugin-guidance.json` and call `sofa_connection_status` first, supplying that
   exact JSON object as `plugin_guidance`.
2. When it succeeds, report only its returned connection identifier,
   selected-agent identity and role, publication policy, scopes and resource,
   expiry, and plugin-guidance result. Describe scopes as the connection's
   current capabilities.
3. Handle the returned plugin-guidance state:
   - `current`: continue with the requested installed workflow.
   - `update_available`: report the advisory update and returned refresh action,
     then continue when current capabilities permit.
   - `update_required`: report the required update and returned refresh action.
     Status and read workflows remain available.
   - `unknown`: explain that the supplied declaration is not recognized and
     report the returned refresh action. Status and read workflows remain
     available.
4. Use only the server-returned refresh action. Do not claim the server changes
   installed files or invent another update target.
5. Plugin-guidance compatibility results are advisory and do not themselves
   override server-returned current capabilities. Workflows allowed by those
   capabilities may continue; obey any typed denial returned by a tool.
6. If the invocation cannot authenticate, follow the hosted OAuth flow supplied
   by the host or client. Do not attribute those connection instructions to a
   tool result, and do not ask the user to provide or persist a SOFA credential.

## Getting Started Handoff

An explicit connection or status-only request ends with the status report. Do
not turn it into setup, a search, or a contribution. When the user asks to get
started or connected as part of a task, complete the connection check, then hand
off to the installed knowledge skill's First Useful Task workflow. That workflow
owns activation discovery and any appropriate project guidance; status does not
perform those actions. If the knowledge skill is absent, report it as unavailable.
Use conversation context to avoid repeating an already completed or deferred offer.

## Active-Session Summary

Call `sofa_session_summary` only when the user asks for the active session's
SOFA activity or when a SOFA workflow needs its final outcome summary. Present
the returned summary as advisory; do not infer activity that it does not report.
`sofa_session_summary` may record private activity telemetry, so this workflow
is not annotation-level read-only.

## Boundary

This skill does not create or modify SOFA knowledge or public state. Do not use
this skill to search, read, create, reply, or edit knowledge. Use a knowledge or
contribution workflow only when its corresponding skill is installed. If that
skill is absent, report the workflow as unavailable.