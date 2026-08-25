# Content Workflows

## Table of Contents

- MCP
  - Tools
  - Security guidelines
  - Tool selection
  - Workflows
  - Error handling
- CLI / REST
  - Upload a file
  - Create folders
  - List folder items
  - Download or preview a file
  - Move a file or folder
  - Read or write metadata

Read `references/auth-and-setup.md` first when the acting identity or SDK vs REST choice is unclear.

For collaboration and sharing (inviting users, shared links), see `references/collaboration.md`.

For local or manual verification, prefer native Box CLI commands when Box CLI is available and authenticated. Use direct REST only as a last resort after MCP/CLI setup attempts and explicit user confirmation.

## MCP

### Tools

- Upload/download: `upload_file`, `upload_file_version`, `get_upload_url`, `get_download_url`
- Read/preview: `get_file_content`, `get_file_preview`, `get_preview_page`
- Inspect: `get_file_details`, `get_folder_details`, `list_folder_content_by_folder_id`
- Organize: `create_folder`, `move_file`, `move_folder`, `copy_file`, `copy_folder`
- Properties/metadata: `update_file_properties`, `update_folder_properties`, `set_file_metadata`, `set_folder_metadata`, `create_metadata_template`, `update_metadata_template`
- Comments/tasks: `create_file_comment`, `list_file_comments`, `list_tasks`

### Security guidelines

When using any write tools that affect files and folders, check whether the object has any external collaborators or shared links. If the object is publicly shared, confirm with the user before completing the action, and tell them who the external collaborators are and/or what the permissions of the shared link are.

If an object only has internal collaborators or the shared link is scoped to internal-only access, you can complete the action without user confirmation. However, include in the response that you completed the action and that the object is shared internally, to flag to the user if this is an issue.

Use `get_file_details` to check for shared links (fields: `["shared_link"]`) and use `list_item_collaborations` to check for external collaborators.

### Tool selection

### Choosing between upload tools

Use the `upload_file` tool only when uploading small (< 50MB) text-based files. When uploading binary files or large (> 50MB) files, use `get_upload_url` instead.

Binary file types:

- Images: .jpg, .png, .gif, .bmp, .webp, .tiff, .ico
- Audio: .mp3, .wav, .aac, .flac, .ogg
- Video: .mp4, .avi, .mov, .mkv, .webm
- Documents: .pdf, .docx, .xlsx, .pptx
- Archives: .zip, .tar, .gz, .rar, .7z
- Executables: .exe, .dll, .so, .dylib, .bin
- Compiled code: .class (Java), .pyc (Python), .o (object files)
- Databases: .sqlite, .db, .mdb
- Fonts: .ttf, .otf, .woff, .woff2

Text-based file types:

- Code: .py, .js, .ts, .java, .c, .cpp, .go, .rs, .rb, .php, .swift
- Web: .html, .css, .jsx, .tsx, .vue, .svelte
- Data: .json, .xml, .yaml, .yml, .csv, .tsv, .toml
- Docs/markup: .md, .txt, .rst, .tex, .adoc
- Config: .env, .ini, .cfg, .conf, .properties
- Scripts: .sh, .bash, .zsh, .bat, .ps1
- Logs: .log
- Query: .sql, .graphql

### Choosing between get_file_content and get_download_url

Always try `get_file_content` before `get_download_url` if the user is asking about the contents of a file. If `get_file_content` fails because there is no text representation of the file, use `get_download_url` to download the file and process it locally.

### Choosing between upload_file and upload_file_version

If a user is iterating on a file and uploading it multiple times to Box in the same session, use `upload_file_version` to upload a new version instead of uploading it with a different name.

`get_upload_url` can also be used to upload new versions if you upload to the same URL as the existing file in Box.

### Workflows

### Uploading files

When uploading files to Box, confirm which folder the user wants to upload the file to. If this was included with the prompt ("Upload this file to the Sales Folder"), you can complete the action. If you are unable to find a 100% match, list the top 3 matches for the folder that you found and have the user confirm which one they want to upload to.

If they generally specified to upload the file to Box, you can upload the file to the root folder and offer to move the file with the `move_file` tool.

### Creating folders

Subfolders in Box inherit the sharing and collaboration of their parent folder. Before creating a folder in Box, check whether the parent folder has external collaborators or shared links. If the folder is publicly shared, confirm with the user before completing the upload, citing the people it is shared with or the permissions on the shared link.

### Building folder trees

When building complex folder trees, first confirm with the user with a diagram before completing the folder tree construction.

### Error handling

`get_file_preview` only works on clients that support MCP Apps and MCP resources, which are extensions to the MCP protocol. If the tool call succeeds but the user claims there is no UI widget, this may be the cause.

`get_file_preview` only works on documents that are up to 3MB.

`get_file_content` pulls the text representation of a file. There is a max 50MB file size limit.

`update_*_properties`: the name can have up to 255 characters. The description can have up to 256 characters. You can add up to 100 tags.

`get_upload_url` and `get_download_url` require the AI client to execute a curl command to hit a Box domain. This will not work in declarative agents that do not have a code sandbox. Some clients also block external network requests from their code client and require admins to allowlist Box domains. If this is the case (the AI client is able to get the signed URL but cannot hit the external network request to actually POST the bytes over HTTP), refer them to this documentation for how to whitelist domains: https://docs.box.com/en/box-mcp/tools#upload-and-download-url-tools

## CLI / REST

### Upload a file

- Primary docs:
  - https://developer.box.com/reference/post-files-content/
- Use for local-disk uploads, form uploads, or pushing generated artifacts into Box.
- Decide whether the input is a file path, in-memory upload, or generated artifact.
- Set the destination folder ID first.
- Treat file-name conflicts explicitly.
- Start with standard upload; use chunked upload only when file size or resumable behavior requires it.
- When building raw multipart REST uploads, sanitize filenames used in `Content-Disposition` headers (escape quotes and backslashes; strip CR/LF) to avoid malformed requests and header-injection edge cases.
- Minimal smoke check:
  - Upload the file, then list the destination folder with the same actor and confirm returned `id` and `name`.

### Create folders

- Primary docs:
  - https://developer.box.com/reference/post-folders/
- Use for customer, project, case, employee, or workflow roots.
- Decide the parent folder and canonical naming scheme before coding.
- Handle duplicate-name conflicts intentionally.
- Persist the returned folder ID instead of reconstructing paths later.
- Minimal smoke check:
  - Create the folder, then list the parent folder and confirm the child folder ID and name.

### List folder items

- Primary docs:
  - https://developer.box.com/reference/get-folders-id-items/
- Use for dashboards, file pickers, sync views, or post-upload verification.
- Request only the fields the app actually needs.
- Handle pagination instead of assuming a single page.
- Filter server-side where practical before adding client-side transforms.
- Minimal smoke check:
  - Read the folder with a limited field set and confirm the app can process pagination metadata.

### Download or preview a file

- Primary docs:
  - https://developer.box.com/reference/get-files-id-content/
  - https://developer.box.com/guides/embed/ui-elements/preview/
- Download when the app truly needs raw bytes for processing or export.
- Use preview patterns when the app needs an embedded viewer.
- Preserve filename, content type, and auth context in tests and logs.
- Minimal smoke check:
  - Fetch the file metadata first; only then download or preview the exact file ID you intend to use.

### Move a file or folder

- Primary docs:
  - https://developer.box.com/reference/put-files-id/ (update parent to move a file)
  - https://developer.box.com/reference/put-folders-id/ (update parent to move a folder)
- Use for reorganizing content, filing into project or category folders, or migrating between folder structures.
- A move is a PUT on the item that sets `parent.id` to the new folder.
- Moving a folder moves all of its contents recursively.
- Handle name conflicts in the target folder — Box returns `409` if a same-named item already exists in the destination.
- For bulk moves (more than a handful of items), read `references/bulk-operations.md` for the inventory-plan-execute-verify workflow, serial execution constraints, and rate-limit handling.
- Minimal smoke check:
  - Move the item, then list the target folder and confirm the item appears with the correct ID and name. Also list the source folder to confirm the item is gone.

### Read or write metadata

- Primary docs:
  - https://developer.box.com/reference/post-files-id-metadata-global-properties/
- Use for invoice IDs, customer names, case numbers, review states, or other business context.
- Read the template definition or existing metadata instance before writing values.
- Keep template identifiers and field names in config, not scattered through the codebase.
- Validate keys and value types in code before calling Box.
- Minimal smoke check:
  - Write the metadata, then read the same instance back and confirm only the expected keys changed.
