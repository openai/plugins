---
name: deepnote-links
description: Use when a task asks for Deepnote URLs, links, project links, notebook links, workspace links, share links, UTM/campaign links, or when a Deepnote response should include clickable links built from Deepnote app project, notebook, or workspace data.
---

# Deepnote Links

Use this skill to build user-facing Deepnote web links from Deepnote app tool data. Prefer links grounded in `get_me`, `list_projects`, `search`, and `get_notebook` responses instead of guessing from names alone. Every project and notebook link built from Deepnote app data must include the UTM parameters below.

## Inputs To Resolve

1. Call `get_me` when workspace-aware links are useful. Use `workspace.id` and `workspace.slug`; do not use OAuth tokens, user email, or other auth details in links or summaries.
2. Resolve the project with `list_projects` or `search`. Use the project `id`, `name`, and `slug` if the app response exposes one.
3. Resolve notebook links with `get_notebook` when possible. Use the notebook `id`, `name`, and parent project data.
4. If the exact project or notebook is ambiguous, ask a short clarification or provide a compact candidate list with links only for unambiguous matches.

## Creation Link Rules

When linking after a creation workflow, use the resource IDs returned by the write tools as the source of truth:

- If `create_notebook` returned a notebook, build the notebook link for that returned notebook ID. Do not substitute the first notebook on the project or the default notebook created by `create_project`.
- If `create_project` created a project and no separate `create_notebook` call was made, use the default notebook created with the project only when a notebook link is needed for that active notebook.
- If both the project default notebook and a later `create_notebook` result are present, the later `create_notebook` result is the notebook to link unless the user explicitly asks for the default notebook.
- If parent project data is missing for the created notebook, call `get_notebook` for the target notebook ID or use the known project ID from the creation workflow before constructing the link.

## URL Shapes

Use the production web origin `https://deepnote.com` for Deepnote app links. Do not derive the web origin from API or tool hosts.

Prefer workspace-scoped links when `get_me` returns both `workspace.slug` and `workspace.id`:

```text
workspaceSlugWithId = {workspace.slug}-{workspace.id}
workspace link = {origin}/workspace/{workspaceSlugWithId}
project link = {origin}/workspace/{workspaceSlugWithId}/project/{projectSegment}
notebook link = {origin}/workspace/{workspaceSlugWithId}/project/{projectSegment}/notebook/{notebookSegment}
```

If workspace data is not available, use the non-workspace project route:

```text
project link = {origin}/project/{projectSegment}
notebook link = {origin}/project/{projectSegment}/notebook/{notebookSegment}
```

## Slug Segments

Use the most canonical segment available:

1. If the app response exposes a `slug`, use it.
2. Otherwise, for simple names, build a readable segment as `{slugifiedName}-{id}`.
3. If exact slugification is uncertain, the name is missing, or the name has unusual characters, use the ID alone.

Deepnote project routing accepts UUID-only project segments, so `{project.id}` is the safest fallback. Notebook routing uses ID-only segments when a notebook name is not available, so `{notebook.id}` is the safest notebook fallback.

Deepnote's readable slugs are created with strict slugification: spaces become hyphens, `/` becomes `-`, unsafe characters are stripped or normalized, and case is preserved. Examples:

```text
Subject Tracker + 0508fc64-b2c8-4982-b6a0-2590c94b6000
=> Subject-Tracker-0508fc64-b2c8-4982-b6a0-2590c94b6000

folder/notebook 10% + a1b2c3d4
=> folder-notebook-10percent-a1b2c3d4
```

## Optional Suffixes

- File paths, when exposed and requested, append after the project segment as `/{encodeURIComponent(filePath)}`.
- Cell or block anchors append as `#anchor`.
- Only generate published app links such as `/app/{authorSlug}/{projectSegment}` or `/streamlit-apps/{streamlitAppId}` when Deepnote app data explicitly exposes the published author slug or Streamlit app ID.

## UTM Parameters

For every project and notebook link built from Deepnote app data, add OpenAI attribution query parameters:

```text
https://deepnote.com/<path>?utm_source=openai&utm_medium=mcp&utm_campaign=openaimcp&utm_content={notebook_id}&utm_term={tool_name}
```

Use these values exactly; braces mark placeholders and are not part of the final URL:

- `utm_source=openai`
- `utm_medium=mcp`
- `utm_campaign=openaimcp`
- `utm_content={notebook_id}`
- `utm_term={tool_name}`

For notebook links, set `utm_content` to the notebook ID. For project-only links, set `utm_content` to the project ID; when a project link represents a specific notebook's parent project, use that notebook ID instead.

Set `utm_term` to the Deepnote app tool or workflow that produced or grounded the link, such as `list_projects`, `search`, `get_notebook`, or `workspace_summary`. Use lowercase snake_case values and URL-encode if needed.

For links to newly created notebooks, set `utm_content` to the created notebook ID and prefer `utm_term=create_notebook`; use `utm_term=get_notebook` when a follow-up `get_notebook` call provided the fields needed to construct the link.

Add UTM parameters before any URL fragment. Use `?` when the URL has no existing query string, otherwise use `&`. Preserve non-UTM query parameters if they already exist, and replace any existing `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, or `utm_term` values instead of duplicating them.

## Response Style

Return Markdown links with human-readable labels:

```markdown
[Project Name](https://deepnote.com/workspace/workspace-slug-workspace-id/project/project-id?utm_source=openai&utm_medium=mcp&utm_campaign=openaimcp&utm_content=project-id&utm_term=list_projects)
[Notebook Name](https://deepnote.com/workspace/workspace-slug-workspace-id/project/project-id/notebook/notebook-id?utm_source=openai&utm_medium=mcp&utm_campaign=openaimcp&utm_content=notebook-id&utm_term=get_notebook)
```

For lists, inventories, and workspace summaries, put links in the `Project` or `Notebook` column and keep IDs in a separate column only when they help disambiguate. When a table has a `Notebook` column, hyperlink the notebook name itself. If a link cannot be built safely because workspace, project, or notebook data is missing, say which field is missing and how to resolve it.
