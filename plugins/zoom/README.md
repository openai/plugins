# Zoom

Zoom is a Codex connector plugin that gives Codex access to live Zoom meeting context through the Zoom app connector.

## What This Plugin Includes

- plugin manifest: [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json)
- repo marketplace entry: [`../../.agents/plugins/marketplace.json`](../../.agents/plugins/marketplace.json)
- Zoom app mapping: [`.app.json`](.app.json)
- branding assets: [`assets/`](assets/)

This plugin contains the Zoom app mapping, connector metadata, and branding assets.

## What Zoom Does In Codex

Use `Zoom` when you want Codex to work with live Zoom context, such as:

- searching meetings by topic, attendee, or content
- retrieving summaries, transcripts, recordings, and related meeting assets
- pulling meeting context into a coding or follow-up workflow
- working with Zoom data through the authenticated app connector

## Using In Codex

1. Install the plugin from `/plugins`.
2. Authenticate the Zoom app connector when Codex prompts for it.
3. Mention `@Zoom` or use natural language requests that need live Zoom meeting context.

The Zoom app connector auth is managed by Codex. It is not exposed as a shell environment variable or raw bearer token.

## Example Prompts

```text
Search my recent Zoom meetings for the discussion about pricing.
```

```text
Find the meeting where we discussed the SDK migration and pull the summary.
```

```text
Get the transcript and recording link for yesterday's engineering sync.
```

```text
Look across my Zoom meetings and identify the action items assigned to me.
```

## Related Plugin

Use this plugin when Codex needs authenticated Zoom meeting context.
