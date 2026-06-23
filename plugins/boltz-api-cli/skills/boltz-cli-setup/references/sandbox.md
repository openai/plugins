# Sandbox and Browser Login

Read this when a sandbox blocks `boltz-api` installation, temp files, OAuth browser login, credential storage, or later API calls.

## Default: User-Wide Install

For normal user setup, keep `boltz-api` in the user's real environment. Before
running an installer or requesting a sandbox bypass for it, show the exact
command and obtain explicit confirmation that the user accepts mutable remote
code from `install.boltz.bio` executing as their user outside the sandbox. A
general request to install Boltz is not sufficient confirmation.

Prefer a version-pinned release artifact with a verified checksum or signature
when Boltz publishes one for the user's platform. Use the mutable installer only
as a confirmed fallback. If sandboxing blocks browser login, OAuth callback,
credential storage, temp files, network access, or the user-wide install path,
request only the host access needed for the confirmed command or auth flow.

If the sandbox bypass is unavailable, explain the blocker and give the user the exact install/auth command to run in their terminal.

After confirmation, run the applicable command in the user's real environment:

```sh
curl -fsSL https://install.boltz.bio/boltz-api/install.sh | sh
boltz-api auth login --device-code
```

For device-code auth, assume the CLI can auto-open the browser and run:

```sh
boltz-api auth login --device-code
```

Keep the user's real CLI auth state available for later `boltz-api` calls, because every API command resolves auth from the normal CLI locations.
