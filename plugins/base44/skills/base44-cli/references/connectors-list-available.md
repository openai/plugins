# base44 connectors list-available

List all integration types available in the Base44 connector catalog.

## Syntax

```bash
npx base44 connectors list-available
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

Fetches the catalog of available integration types from Base44 and displays each one with its display name, description, and any required configuration fields.

## Output

```bash
$ npx base44 connectors list-available

✓ Available integrations fetched successfully

Google Calendar
  integrationType: googlecalendar
  description: Access Google Calendar events and schedules
  connectionConfigFields: []

Slack
  integrationType: slack
  description: Send messages and interact with Slack workspaces
  connectionConfigFields: []

Stripe
  integrationType: stripe
  description: Process payments and manage Stripe accounts
  connectionConfigFields: []

Found 14 available integrations.
```

Each integration is displayed in YAML format showing the integration type, description, and any connection configuration fields required for setup.

## Use Cases

- Discover all supported connector types before creating connector files
- Check if a specific integration is available in your Base44 plan
- See what configuration fields (if any) a connector requires

## Related Commands

- [connectors-create.md](connectors-create.md) - How to create connector configuration files
- [connectors-push.md](connectors-push.md) - Push local connectors to Base44
- [connectors-pull.md](connectors-pull.md) - Pull connectors from Base44 to local files
