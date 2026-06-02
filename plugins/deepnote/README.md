# Deepnote Plugin

OpenAI plugin for Deepnote. It packages Deepnote skills for searching workspaces, inspecting notebooks, generating project and notebook links, mapping integration usage and cached table structure, reading Deepnote docs, creating, updating, and reorganizing notebook structure, running notebooks, and summarizing run history, status, and outputs.

## What's Included

- `skills/deepnote` - routing guidance for Deepnote app tool workflows
- `skills/deepnote-links` - workspace-aware project and notebook link construction
- `skills/deepnote-notebooks` - notebook inspection, review, inputs, blocks, SQL, and outputs
- `skills/deepnote-notebook-editing` - project, notebook, and block creation, block updates, and block reordering workflows
- `skills/deepnote-data-execution` - notebook run, run history, input, integration, and snapshot-output workflows

## Requirements

- A Deepnote account with access to the target workspace
- The Deepnote app connected
- OAuth authorization for the Deepnote workspace account you want OpenAI to use

Authentication is handled by OAuth through the connected Deepnote app. No local credential setup is required for this official app-backed plugin.

## Behavior Notes

The OAuth connection acts with the permissions of the connected Deepnote user. A viewer can read viewer-accessible resources; editor and admin accounts can perform the matching write workflows when the relevant app tools are available.

The current tool surface supports cached integration table structure, but does not promise live database schema refreshes, row previews, single-block execution, environment mutation, permission changes, publishing, or scheduling changes. Skills should say when a requested capability is not exposed by the current app tools.

## Good First Prompts

- `Search my Deepnote workspace for customer retention notebooks.`
- `Which Deepnote workspace am I connected to?`
- `Give me links to my Deepnote projects.`
- `Inspect this Deepnote notebook and summarize its inputs.`
- `Create a Deepnote project named Revenue Analysis.`
- `Create a notebook in this Deepnote project and add starter markdown and code blocks.`
- `Update this Deepnote notebook block with the revised SQL.`
- `Add a SQL block to this notebook using my Snowflake integration.`
- `Move these Deepnote notebook blocks to the top of the notebook.`
- `Show me the recent runs for this Deepnote notebook.`
- `Run this Deepnote notebook with customer_name set to Acme.`
- `List Deepnote integrations matching Snowflake.`
- `Show cached tables for my Snowflake integration.`
- `Show me where this Deepnote integration is used.`
- `Look up the Deepnote docs for scheduled notebooks.`
