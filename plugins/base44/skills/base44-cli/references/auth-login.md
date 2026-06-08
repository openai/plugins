# base44 login

Authenticate with Base44 using device code flow.

## Syntax

```bash
npx base44 login
```

## Authentication

**Required**: No (this is the login command itself)

## How It Works

The login command uses OAuth 2.0 device code flow for authentication:

1. Generates a device code for authentication
2. Displays a verification code and verification URI
3. Directs you to visit the URI and enter the code
4. Polls for authentication completion (up to device code expiration)
5. Retrieves access and refresh tokens upon successful authentication
6. Fetches and displays your user information
7. Saves authentication data locally with expiration timestamp

## Interactive Flow

```bash
$ npx base44 login

Please visit: https://auth.base44.com/device
Enter code: ABCD-EFGH

Waiting for authentication...
✓ Successfully authenticated!

Logged in as: user@example.com
```

## Session Management

- Authentication tokens are stored locally on your device
- Tokens include expiration timestamps
- The session persists across CLI sessions
- Other commands will automatically use your stored credentials
- Use `npx base44 logout` to clear your session
- Use `npx base44 whoami` to check your current authentication status

## Notes

- You only need to login once per device
- If your session expires, you'll be prompted to login again when running authenticated commands
- The CLI automatically prompts for login when you run commands that require authentication
