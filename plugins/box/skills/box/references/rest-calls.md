# Direct REST Fallback

Use this reference only when:

1. Box MCP is unavailable after setup attempts, and
2. Box CLI is unavailable, not allowed, or explicitly declined by the user, and
3. The user explicitly confirms they want REST fallback.

Direct REST is a fallback path for agent operations, not the default. MCP and CLI remain preferred.

## Source of truth

- Use Box API endpoint docs as the authority for endpoint coverage and operation details: https://developer.box.com/reference
- Use the Box OpenAPI spec as the authority for request and response shapes.
- OpenAPI repository: https://github.com/box/box-openapi
- Versioning note: Box introduced API versioning in 2025. `openapi.json` remains for compatibility, and versioned specs live under `openapi/` in the same repository.

When this file and current Box docs disagree, follow current Box docs and OpenAPI.

## Auth and base URLs

- API base URL: `https://api.box.com/2.0`
- Upload base URL: `https://upload.box.com/api/2.0`
- Required auth header: `Authorization: Bearer $BOX_ACCESS_TOKEN`
- Recommended default header: `Accept: application/json`

Before sending requests:

1. Ask the user to set `BOX_ACCESS_TOKEN` in their environment.
2. If `BOX_ACCESS_TOKEN` is missing or expired, follow `references/auth-and-setup.md` to choose and complete the appropriate auth flow, then set `BOX_ACCESS_TOKEN` for the current session.
3. Confirm the token is present without printing it:
   - `test -n "$BOX_ACCESS_TOKEN" && echo "BOX_ACCESS_TOKEN is set"`
4. Never echo or log token values.

## Safe request templates

Read folder:

```bash
curl -sS \
  -H "Authorization: Bearer $BOX_ACCESS_TOKEN" \
  -H "Accept: application/json" \
  "https://api.box.com/2.0/folders/0?fields=id,name,item_collection"
```

List folder items:

```bash
curl -sS \
  -H "Authorization: Bearer $BOX_ACCESS_TOKEN" \
  -H "Accept: application/json" \
  "https://api.box.com/2.0/folders/<FOLDER_ID>/items?limit=100&offset=0&fields=id,name,type"
```

Create folder:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $BOX_ACCESS_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  "https://api.box.com/2.0/folders" \
  -d '{"name":"<FOLDER_NAME>","parent":{"id":"<PARENT_ID>"}}'
```

Move file:

```bash
curl -sS -X PUT \
  -H "Authorization: Bearer $BOX_ACCESS_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  "https://api.box.com/2.0/files/<FILE_ID>" \
  -d '{"parent":{"id":"<TARGET_FOLDER_ID>"}}'
```

## Request structure guidelines

- Request only fields you need (`fields=...`).
- In Box APIs, setting `fields` changes the default response projection: only mini fields plus the explicitly requested fields are returned.
- Use pagination (`limit`, `offset`) for list/search endpoints.
- Some list endpoints also support marker pagination. Check the endpoint schema in OpenAPI before choosing offset vs marker for large traversals.
- For writes, follow with a read-after-write call using the same actor.
- For uploads, use the upload base URL and multipart form-data with `attributes` + file content at `POST /files/content`.
- In multipart uploads, the `attributes` part must come before the `file` part, or Box can return `400 metadata_after_file_contents`.
- Sanitize filenames in multipart `Content-Disposition` headers (escape quotes and backslashes, strip CR/LF).

Upload example skeleton:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $BOX_ACCESS_TOKEN" \
  -H "Accept: application/json" \
  -F 'attributes={"name":"<FILE_NAME>","parent":{"id":"<PARENT_ID>"}}' \
  -F "file=@<LOCAL_PATH>" \
  "https://upload.box.com/api/2.0/files/content"
```

## Error handling and retries

- `401/403`: wrong actor, expired token, missing scope, or wrong app permissions.
- `404`: wrong ID or object not visible to actor.
- `409`: conflict (for example duplicate folder name in same parent).
- `429`: respect `Retry-After`, wait, then retry the same request.

For `429`, do not continue sending other requests during cooldown if the same actor/token is being throttled.

## Guardrails

- Do not use REST fallback silently. Confirm with the user first.
- Do not widen access (shared links/collaborations) without explicit confirmation.
- Keep access tokens and secrets out of logs and chat output.
- Record actor context and touched IDs in verification output and final summaries.
