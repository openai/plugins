# `connection browse` (capability-gated)

```
workspace_shell("connection browse <name> [--remote-path <provider-path>] [--detailed] --json")
```

List files at a provider-side path on storage connections (S3, Azure
Blob, Google Drive, etc.).

## Capability rule

Only call `browse` if the connection's `capabilities` array (from
`connection list --json`) includes `browse`. Calling it on a connection
that doesn't advertise browse is an error and clutters the workspace's
audit trail.

## Flags

- `--remote-path <provider-path>` — provider-side folder or file path.
  Without this, the response may list the root, or for connections that
  require explicit bucket selection, return a list of available buckets.
- `--detailed` — include extra metadata in each entry.
- `--json` — always pass.

## Response shape

Standard listing:

```json
{
  "success": true,
  "operation": "browse",
  "data": [{ "name": "...", "type": "file" | "folder", ... }, ...]
}
```

Bucket selection required:

```json
{
  "success": true,
  "operation": "browse",
  "execution_mode": "bucket_selection_required",
  "available_buckets": ["bucket-a", "bucket-b", ...]
}
```

When you see `bucket_selection_required`, surface the buckets to the
user, get their choice, and re-call `browse` with `--remote-path
<bucket>/<path>`.

## Pairing with download

`browse` is read-only; it doesn't pull files. Once you've found the file
you want, use `connection download` to fetch it into the workspace.
