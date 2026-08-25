---
name: collect-files-with-request
description: Create, inspect, and manage Dropbox file requests for collecting uploads from other people. Use when the user asks to collect files, request uploads, create an upload portal, check a file request, or list existing file requests.
---

# Collect Files With Request

Use this skill to help users collect files from others through Dropbox file requests.

## Tools

- `create_file_request`
- `get_file_request`
- `list_file_requests`
- `create_folder`
- `get_file_metadata`
- `list_folder`

## Workflow

1. Determine whether the user wants to create a new file request, inspect one request, or list existing requests.
2. For a new request, identify the destination folder.
3. Do not use a team root, such as `/`, or the user's personal root, such as `/FirstName LastName`, as the destination. Dropbox requires the file request destination to be a child folder under that folder, such as `/FirstName LastName/Invoices`.
4. If the requested destination is a team root or the user's personal root, ask the user to confirm a child folder under that folder.
5. If the destination folder does not exist and the user wants it created, use `create_folder` only after explicit confirmation.
6. Before calling `create_file_request`, confirm the title, destination folder, deadline if applicable, and whether the request should be open or closed if that option is available.
7. Use `get_file_request` for a known raw request ID.
8. Use `list_file_requests` when the user asks for existing requests or cannot identify one.
9. After creating or finding a request, explain the request URL and where uploaded files will land.

## Confirmation Required

Before creating a file request, confirm:

- Request title
- Destination folder, confirmed to be a child folder under any requested team root or the user's personal root
- Deadline, if requested
- Any access or open/closed setting supported by the tool

Before creating a destination folder, confirm:

- Exact folder path
- Whether parent folders already exist
- That the folder is not a team root, such as `/`, or the user's personal root

## Output

Return:

- File request title
- Request URL or identifier
- Destination folder
- Status
- Deadline, if any
- Any action the user still needs to take

## Safety

Do not create folders or file requests without explicit confirmation. Do not assume uploaded files are private or reviewed; describe the destination and access implications clearly. Dropbox does not allow file requests at a team root, such as `/`, or the user's personal root; ask the user to confirm a child folder under that folder and do not retry with a guessed folder.

## Good Triggers

- "Create a Dropbox file request for vendor invoices."
- "Make an upload link for candidates to submit portfolios."
- "Show my open file requests."
- "Check the status of this file request."

## Do Not Use When

- The user wants to share existing content. Use `share-dropbox-content`.
- The user wants to organize existing files. Use `organize-dropbox-folder`.
- The user wants to recover deleted files. Explain that recovery is unavailable until the Dropbox restore tool is exposed.
