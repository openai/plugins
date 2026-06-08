# Wix documentation lookups

Operational calls in this skill use `npx @wix/cli@latest token --site "$SITE_ID"` + `curl` against `wixapis.com` (see `AUTHENTICATION.md`). When a bundled recipe falls short and you need to look up an endpoint, method schema, or article body, use the public unauthenticated REST endpoints below. **No MCP, no SDK** — these are plain `curl` calls.

## Doc search

| Need | Endpoint |
|---|---|
| Search REST / SDK / headless docs | `GET https://www.wixapis.com/mcp-docs-search/v1/search?kbName=<KB>&searchTerm=<q>&maxResults=<n>` |
| Read a full article | `GET https://dev.wix.com/rawdocs/api/get-article-content?articleUrl=<url>&schema=false` |
| Read method schema | Same URL with `schema=true` |
| Browse REST docs menu | `GET https://dev.wix.com/docs/api/v1/get-menu-content?url=<url>&format=markdown` |

**kbName values** (common): `REST_METHODS_KB_ID`, `SDK_KB_ID`, `HEADLESS_KB_ID`.

Example — search REST docs for app install:

```bash
curl -sS --get 'https://www.wixapis.com/mcp-docs-search/v1/search' \
  --data-urlencode 'kbName=REST_METHODS_KB_ID' \
  --data-urlencode 'searchTerm=install app instance' \
  --data-urlencode 'maxResults=3'
```

Example — fetch article body:

```bash
curl -sS --get 'https://dev.wix.com/rawdocs/api/get-article-content' \
  --data-urlencode 'articleUrl=https://dev.wix.com/docs/...' \
  --data-urlencode 'schema=false'
```

No auth headers required on these endpoints.

## Prefer bundled references

Your skill directory includes `.md` reference files with API recipes and error handling for your scope. **Read those first.** Use the doc endpoints above only when you hit an error or endpoint not covered by the bundled recipe — each external doc read costs a tool call and 15–30 s.

## Absolute paths

Subagents run with the **project directory** as CWD, not the skill root. Every dispatch prompt must include `Instruction file (absolute path): <SKILL_ROOT>/references/<scope>/INSTRUCTIONS.md`. Read that path only; use the absolute sibling paths it lists. Never resolve `references/...` against the project CWD.
