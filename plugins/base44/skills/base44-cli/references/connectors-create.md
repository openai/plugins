# Creating Connectors

Connectors are OAuth integrations that let your Base44 app connect to external services like Google Calendar, Slack, Notion, and more. Once connected, you can use access tokens in backend functions to call external APIs directly.

## Key Concepts

- **Direct API Access**: Connectors provide raw OAuth access tokens - you call the external APIs directly from backend functions
- **App Builder's Account**: Connects your account (the app builder), not your end users' accounts
- **Backend Functions Only**: Tokens are only accessible server-side for security

## File Location

Create connector files in the `base44/connectors/` directory (or the directory specified by `connectorsDir` in your config.jsonc).

**File naming:** `{type}.jsonc` or `{type}.json`

Examples:
- `base44/connectors/googlecalendar.jsonc`
- `base44/connectors/slack.jsonc`
- `base44/connectors/notion.json`

## Schema

Each connector file must specify a `type` and optionally a list of `scopes`:

```jsonc
{
  "type": "googlecalendar",
  "scopes": [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events"
  ]
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | The integration type (run `npx base44 connectors list-available` to see options) |
| `scopes` | string[] | No | OAuth scopes to request (defaults to `[]`) |

## Discovering Available Connector Types

Run the following command to get the up-to-date list of supported connector types. Note: `stripe` is also a valid type but is not returned by this command — treat it as supported (see Stripe example below).

```bash
npx base44 connectors list-available
```

This returns a JSON object with all available integrations, their display names, descriptions, and any required connection config fields. Example output (trimmed):

```json
{
    "integrations": [
        {
            "integration_type": "googlecalendar",
            "display_name": "Google Calendar",
            "description": "Access and manage Google Calendar events",
            "connection_config_fields": []
        },
        {
            "integration_type": "slack",
            "display_name": "Slack User",
            "description": "Send messages and interact with Slack as yourself (user integration)",
            "connection_config_fields": []
        },
        {
            "integration_type": "share_point",
            "display_name": "SharePoint",
            "description": "Manage documents, lists, sites, and collaboration content in SharePoint",
            "connection_config_fields": [
                {
                    "name": "subdomain",
                    "display_name": "SharePoint Site",
                    "description": "The name of your SharePoint site (e.g., sites/mysite)",
                    "placeholder": "sites/mysite",
                    "required": true,
                    "validation_pattern": "^[a-zA-Z0-9/_-]+$",
                    "validation_error": "Please enter a valid SharePoint site path"
                }
            ]
        }
    ]
}
```

Use the `integration_type` value from this output as the `type` field in your connector file. Some connectors require additional `connection_config_fields` — check the output for details.

### Stripe (Sandbox)

```jsonc
// base44/connectors/stripe.jsonc
{
  "type": "stripe",
  "scopes": []
}
```

Note: Stripe does not require an OAuth browser flow. When you push this connector, Base44 automatically provisions a Stripe sandbox account on the server side. You may receive a claim URL in the push output to link the sandbox to your Stripe account.

## Rules and Constraints

1. **One connector per type**: You cannot have multiple connectors of the same type (e.g., two `googlecalendar` connectors)

2. **Type must be valid**: The `type` field must be a valid integration type (run `npx base44 connectors list-available` to see available types)

3. **Scopes are provider-specific**: Each service has its own scope format - refer to the provider's documentation

## Next Steps

After creating connector files, push them to Base44:

```bash
npx base44 connectors push
```

This will prompt you to authorize each new OAuth connector in your browser. Stripe is the exception — it is provisioned automatically without a browser flow. See [connectors-push.md](connectors-push.md) for details.

To pull existing connectors from Base44 to local files:

```bash
npx base44 connectors pull
```

See [connectors-pull.md](connectors-pull.md) for details.
