# base44 auth push

Push the local auth configuration to Base44.

## Syntax

```bash
npx base44 auth push [options]
```

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `-y, --yes` | Skip confirmation prompt | No |

## Examples

```bash
# Push auth config (interactive confirmation)
npx base44 auth push

# Push auth config without confirmation (for CI/CD)
npx base44 auth push -y
```

## Notes

- Requires a local auth config file to exist. Run `npx base44 auth pull` first if you haven't set up a local auth config.
- If the local config has no login methods enabled, the CLI will warn that pushing will lock out all users.
- In non-interactive mode (CI/CD), `--yes` is required.
