# Example Prompts

- "Use $box-content-api to add the smallest possible endpoint that uploads a generated PDF into a configured Box folder, then tell me which folder ID and file ID were used to verify it."
- "Use $box-content-api to verify my current Box CLI auth context, list the root folder items with CLI-first verification, and tell me which actor the command is running as."
- "Use $box-content-api to debug why this Box folder listing returns 404 in production but works locally; identify the acting auth context and the exact object ID mismatch."
- "Use $box-content-api to wire a webhook handler for new files in a folder, make it idempotent, and include a duplicate-delivery verification step."
- "Use $box-content-api to build a search-first retrieval flow over Box content for invoice lookup, and only download file content if the selected result actually needs it."
