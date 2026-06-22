---
name: boltz-cli-setup
description: Boltz CLI setup and auth. Use when installing, updating, verifying, or authenticating `boltz-api`, or fixing missing CLI, PATH, sandbox, browser login, or auth errors.
---

# Boltz CLI Setup

Use this skill for `boltz-api` installation, version, PATH, and authentication issues. The workflow skills assume `boltz-api` is already installed.

## Verify Installation

Check that the CLI is available:

```sh
boltz-api --version
```

If `boltz-api` is missing or too old, prefer a version-pinned release artifact
whose checksum or signature can be verified. If Boltz does not publish one for
the user's platform, its official installer is the fallback.

Before downloading or running either installer, show the exact platform command
and obtain the user's explicit confirmation. Explain that the command downloads
mutable remote code, executes it as the user outside the sandbox, and therefore
trusts `install.boltz.bio` at execution time. A general request to use or install
Boltz is not confirmation for this specific risk.

macOS and Linux:

```sh
curl -fsSL https://install.boltz.bio/boltz-api/install.sh | sh
```

Windows PowerShell:

```powershell
irm https://install.boltz.bio/boltz-api/install.ps1 | iex
```

The installer updates an existing `boltz-api` on `PATH`. If no binary is found, it installs to a user-local bin directory. Add the installed binary to `PATH` if `boltz-api --version` is still not found after install.

The sandbox can block browser login, OAuth callbacks, temp files, credential
storage, and user-wide install paths. Request the host sandbox bypass/escalation
needed for installation only after the installer confirmation above. The host
approval must cover the exact command; do not treat an ordinary setup request as
authorization to execute mutable remote code outside the sandbox.

Read [references/sandbox.md](references/sandbox.md) when an agent sandbox blocks the installer, browser auto-open, OAuth callback, credential storage, temp files, or global install path.

## Authenticate

Check the current auth state with:

```sh
boltz-api auth status
```

If `auth status` reports unauthenticated, or any Boltz command fails because authentication is missing or expired, start device-code login on the user's behalf before retrying:

```sh
boltz-api auth login --device-code
```

Do not ask the user for permission before starting device-code login; relaying the login URL/code and waiting for the CLI to complete is part of auth recovery. When sharing the authentication login URL/code, tell the user to use exactly `boltz-api auth login --device-code`.

For auth recovery, assume the CLI can auto-open the browser and run the exact command above. In sandboxed environments, request the host sandbox bypass/escalation needed for browser auto-open, OAuth callbacks, credential storage, or temp files.

For automation, an API key is still supported when it is already provisioned in
the environment:

```sh
test -n "${BOLTZ_API_KEY:+configured}" && echo "BOLTZ_API_KEY is configured"
```

Never ask the user to paste an API key into chat or a command, and never print,
log, or persist it in shell history or generated files. If the variable is not
already provisioned, direct the user to their host's secret-management facility.

## Version Checks

Do not hard-code expected commands or minimum versions in this skill. Treat the CLI's own update check as the source of truth.

When `boltz-api` reports that an update is available or required, relay that message and the install command it provides. The CLI may get this from a Boltz-hosted version metadata endpoint such as `/cli/version`, returning latest version, minimum supported version, whether an update is required, and platform-appropriate install instructions.

If a user asks why the CLI thinks it is stale, explain the split:

- GitHub Releases define which CLI binaries are available to install.
- The Boltz version endpoint defines API compatibility, including the minimum supported CLI version.

Respect user or CI opt-outs such as `BOLTZ_API_NO_UPDATE_CHECK=1`; do not force update checks when the environment disables them.
