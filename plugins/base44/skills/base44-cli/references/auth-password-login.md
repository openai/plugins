# base44 auth password-login

Enable or disable username & password authentication for your Base44 app.

## Syntax

```bash
npx base44 auth password-login <enable|disable>
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `<enable\|disable>` | Enable or disable password authentication | Yes |

## Examples

```bash
# Enable username & password authentication
npx base44 auth password-login enable

# Disable username & password authentication
npx base44 auth password-login disable
```

## Notes

- Updates the local auth config file only — run `npx base44 auth push` or `npx base44 deploy` to apply the change to Base44.
- Disabling password auth when no other login methods are enabled will warn you that users will be locked out.
