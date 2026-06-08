# base44 whoami

Display the currently authenticated user.

## Syntax

```bash
npx base44 whoami
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

- Reads stored authentication data
- Displays the email of the currently logged-in user

## Output

```bash
$ npx base44 whoami
Logged in as: user@example.com
```

## Use Cases

- Verify you're logged in before running other commands
- Check which account you're currently using
- Confirm authentication is working properly
- Useful in scripts or automation to verify credentials

## Notes

- If you're not logged in, the command will prompt you to authenticate first
- The email displayed matches your Base44 account email
