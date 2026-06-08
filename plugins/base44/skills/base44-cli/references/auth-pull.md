# base44 auth pull

Pull the auth configuration from Base44 to local files.

## Syntax

```bash
npx base44 auth pull
```

## Examples

```bash
npx base44 auth pull
```

## Notes

- Overwrites the local auth config file with the remote configuration.
- The auth config file is written to `base44/auth/` (the `authDir` configured in `config.jsonc`).
