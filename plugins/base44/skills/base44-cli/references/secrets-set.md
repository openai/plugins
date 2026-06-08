# base44 secrets set

Set one or more project secrets (environment variables stored in Base44).

## Syntax

```bash
npx base44 secrets set [entries...] [options]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `entries...` | One or more `KEY=VALUE` pairs (e.g. `KEY1=val1 KEY2=val2`) | Yes (unless `--env-file` is used) |

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `--env-file <path>` | Path to a `.env` file to bulk-import secrets from | No |

## Examples

```bash
# Set one secret
npx base44 secrets set API_KEY=my-secret-value

# Set multiple secrets at once
npx base44 secrets set API_KEY=abc123 DB_PASSWORD=secret

# Import from a .env file
npx base44 secrets set --env-file .env.production
```

## Notes

- Provide `KEY=VALUE` pairs **or** `--env-file`, not both
- Keys must be non-empty; values may be empty strings
- Overwrites existing secrets with the same name
- Requires authentication
