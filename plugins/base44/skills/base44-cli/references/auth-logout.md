# base44 logout

Logout from current device and clear stored authentication data.

## Syntax

```bash
npx base44 logout
```

## Authentication

**Required**: No

## What It Does

- Deletes stored authentication data from your device
- Clears your local session
- Removes access and refresh tokens

## Output

```bash
$ npx base44 logout
Logged out successfully
```

## Notes

- You can logout even if you're not currently logged in (no error)
- After logout, you'll need to run `npx base44 login` again to use authenticated commands
- This only affects the current device; your Base44 account remains active
