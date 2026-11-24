---
name: cognitivedb-administer-access
description: >-
  Inspect the current user's profile, CognitiveDB access, and Space roles;
  administer Space membership, invitations, roles, Catalog/Schema/Table grants,
  ownership, and access audit evidence. Use for access questions, inspections,
  and confirmed access mutations.
metadata:
  version: "dev-1.8.2"
---

# Administer CognitiveDB Access

Before Space-scoped resource discovery or execution, load and follow
`cognitivedb-discipline`. Continue only within the user-selected Space and any
specified Catalog or object boundaries.

Never invent roles, users, grants, IDs, fields, scopes, actor identity, or authorization.
Use the narrowest MCP read that answers the question. Treat structured MCP
results as authoritative and do not reproduce permission resolution in prose.

## Boundaries

- Keep Organization roles, Space roles, and data-asset grants separate; Space
  roles never imply Catalog ownership or grant authority. Report Organization
  membership or role mutation as unsupported when no dedicated live Tool exists.
- Recognize Organization roles returned by live results; Space built-ins
  `Owner`, `Admin`, `User Admin`, `Role Admin`, and `Member`; and exact returned
  custom roles. Built-in `Owner` is not assignable.
- Route Catalog/Schema lifecycle elsewhere. Never emulate access administration with SQL, resource tools, browser, HTTP, forged headers, or shared identity.
- For a "can I" question, inspect only the authenticated current user's access.
  Do not inspect another user's effective permissions as part of that answer.
  A mutation requires a separate user request and the mutation rules below.
- Do not use a "can I" check as a prerequisite for another Skill. The owning
  Skill or Tool remains responsible for its operation and authorization result.

## Core Instructions

### Current-User Capability Questions

- Use `cognitivedb_user_current_get` for the authenticated user's own profile;
  it needs no Space context and supplies identity, not roles or capabilities.
- For the user's role in a selected Space, use `cognitivedb_space_members_list`
  to match the authenticated identity to one exact member record. Use
  `cognitivedb_space_roles_list` when the role's permission definition is needed.
  If the lookup is denied or no exact match is established, report the role as
  undetermined rather than inferring it from the profile or another member.
- For a current-user capability question, call a preflight only when the live
  contract defines one. If no reliable preflight exists, report that access
  cannot be determined before execution; never execute a mutation merely to
  test access or reconstruct authorization from roles, grants, or ownership.
- Never determine SQL DDL or DML authorization from asset capabilities such as
  `edit_remote` unless the live SQL Tool contract defines that evidence as its
  pre-execution gate. Without such a gate, classify the authorization question
  as undetermined before execution.
- Distinguish `allowed`, `denied`, and `cannot be determined before execution`.
  If the requested Tool is unavailable, report the capability as unavailable
  in this session rather than as a verified denial. A capability answer does
  not authorize or execute the requested action.
- Explain required access or who can grant it only from the live contract or
  structured evidence. Do not expose raw permission codes unless the user asks
  for MCP or API diagnostics.

### Access Inspection

- For member, grant, effective-access, or audit inspection, use the narrowest read
  for the requested subject and scope. Request a Catalog or Schema only when
  the action is target-specific. Report partial evidence as partial; do not
  assemble a verdict from unrelated roles. An inspection request does not authorize changes.
- Catalog grant inspection requires an exact Catalog; never present one Catalog's
  grants as an Organization-wide inventory. Ask once if the requested scope is missing.
- Use metadata search only to find assets by keyword. To browse the Catalog
  hierarchy, use the Catalog and Schema list tools; do not treat search results
  as a complete tree.
- Scope audit reads to one exact resolved data asset and the smallest useful
  time range and filters. Treat actor names and event details as sensitive evidence.
- Scope validation failures and denials to the returned subject, action, and Space;
  an ineligible recipient or denied asset read does not imply no platform access.

### Access Mutations

- Before a mutation, bind the current Space and actor. Use a permission preflight
  when the live contract provides one; otherwise let the requested operation
  enforce authorization. Stop on denial, ambiguity, stale context, or cross-Space
  evidence; confirmation is not authorization.
- Resolve targets from live results: invitation by email, member by username,
  data assets through their exact returned hierarchy, and revocation by direct
  `grantId`. Use `ALL_GRANTS` only for an explicitly confirmed complete removal.
- Confirm the exact target, scope, effect, and rollback before each mutation.
  Space membership changes do not change Organization roles or data-asset grants.
- Never assign `O-Owner` or built-in Space `Owner`. Grant or revoke Catalog,
  Schema, and Table privileges only with verified authority from the
  target-specific capability result. Include
  automatically added `USE_CATALOG` or `USE_SCHEMA` in the stated impact.
- Create custom roles only with live returned permission codes and unique names.
  Never delete a built-in role; state visible membership impact before deleting
  a custom role.
- Execute a confirmed mutation once, then read the exact affected object to
  verify it. After an uncertain result, read that object before any retry.
- For a user-corrected validation input, retain the action and unchanged context;
  resolve the corrected target once, recheck permission, and confirm the changed
  mutation. Never reuse old-target approval. For an uncertain prior outcome, first
  inspect the old target and stop if its outcome remains unknown.

## Allowed MCP Tools

- `cognitivedb_audit_logs_list`
- `cognitivedb_catalog_list`
- `cognitivedb_catalog_metadata_search`
- `cognitivedb_catalog_permissions_get`
- `cognitivedb_catalog_permissions_grant`
- `cognitivedb_catalog_permissions_list`
- `cognitivedb_catalog_permissions_revoke`
- `cognitivedb_catalog_schemas`
- `cognitivedb_owner_transfer`
- `cognitivedb_schema_permissions_get`
- `cognitivedb_schema_permissions_grant`
- `cognitivedb_schema_permissions_revoke`
- `cognitivedb_space_current_get`
- `cognitivedb_space_custom_role_create`
- `cognitivedb_space_custom_role_delete`
- `cognitivedb_space_member_invite_cancel`
- `cognitivedb_space_member_invite_resend`
- `cognitivedb_space_member_remove`
- `cognitivedb_space_member_role_set`
- `cognitivedb_space_members_invite`
- `cognitivedb_space_members_list`
- `cognitivedb_space_roles_list`
- `cognitivedb_table_permissions_get`
- `cognitivedb_table_permissions_grant`
- `cognitivedb_table_permissions_list`
- `cognitivedb_table_permissions_revoke`
- `cognitivedb_user_current_get`
