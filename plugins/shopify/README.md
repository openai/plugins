# Shopify Codex Plugin

Build with Shopify from Codex.

This plugin gives Codex access to Shopify's documentation, API schemas, code validation, app and theme guidance, and store management workflows through Shopify CLI and UCP instructions. For more info, [see the docs](https://shopify.dev/docs/apps/build/ai-toolkit).

## Install

In Codex, open `/plugins`, search for **Shopify**, and select **Add to Codex**.

## What you get

- **Docs and API schemas**: Search Shopify's documentation and API schemas without leaving your editor
- **Code validation**: Validate GraphQL queries, Liquid templates, and UI extensions against Shopify's schemas
- **Store management**: Manage your Shopify store through the CLI's store execute capabilities
- **Auto-updates**: The plugin updates automatically as new capabilities are released

## Telemetry

The skill scripts (`scripts/search_docs.mjs`, `scripts/validate.mjs`) send a usage event to `https://shopify.dev/mcp/usage` on each invocation. The payload includes:

- tool name, skill name and version
- model name, client name, and client version (when supplied as flags)
- the search query text and search response or error text (for `search_docs.mjs`)
- the validation result, the validated code when present, and validator-specific context such as API name, extension target, filename, file type, theme path, and file list (for `validate.mjs`)
- artifact ID and revision number (when supplied)

This is **on by default**. To opt out, set the environment variable:

```
OPT_OUT_INSTRUMENTATION=true
```

## Contributing

This package is mirrored from [Shopify/Shopify-AI-Toolkit](https://github.com/Shopify/Shopify-AI-Toolkit) and adapted for the OpenAI Codex plugin marketplace.
