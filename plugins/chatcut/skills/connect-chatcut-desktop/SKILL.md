---
name: connect-chatcut-desktop
description: Install, open, connect, or repair ChatCut Desktop when the chatcut_desktop MCP tools are missing or unavailable. Do not use from a managed agent already running inside ChatCut Desktop, or when chatcut_desktop tools are already available.
---

# Connect ChatCut Desktop

Use the signed production Desktop app as the only source of the local MCP server
and editing skills. This plugin contains instructions only, not an installer or
MCP configuration.

If `chatcut_desktop` tools are already available, call `get_active_project` and
continue with the user's editing request. Do not reinstall the app or change MCP
configuration. If the current host is ChatCut Desktop's managed Codex agent,
stop; its project-pinned MCP and built-in skills are already authoritative.

## Download

Use only the matching official URL:

- macOS Apple Silicon: `https://api.chatcut.io/desktop/download/macos`
- macOS Intel: `https://api.chatcut.io/desktop/download/macos-x64`
- Windows x64: `https://api.chatcut.io/desktop/download/windows`

ChatCut Desktop supports macOS 13 or newer on Apple Silicon or Intel and Windows
on x64. Linux is unsupported. Do not substitute a search result, third-party
mirror, hosted ChatCut MCP, or historical `chatcut@chatcut-inc` plugin.

## Install or repair

Try to complete the ordinary platform installation for the user with the host's
narrow command approval:

1. Detect the operating system and architecture and choose the URL above.
2. Download the official artifact to a temporary directory. If ChatCut is
   already installed but will not open, inspect it before replacing it.
3. On macOS, use native tools to mount a DMG or extract a ZIP, then copy
   `ChatCut.app` to `/Applications` or the user's `Applications` directory. On
   Windows, open the downloaded installer and let the visible installer finish.
4. Open ChatCut Desktop. It registers `chatcut_desktop` and synchronizes its
   editing skills into Codex automatically.

Installing outside the project sandbox or opening an installer may require host
approval. Request only the scoped operation needed for that step; never ask the
user to enable persistent Full access.

For macOS launch or code-signing failures, inspect `codesign`, Gatekeeper,
permissions, and quarantine state. Try remounting or re-extracting a fresh
official download, fixing destination permissions, or clearing stale quarantine
only after the official app's signature validates. Never modify or ad-hoc sign
the app, disable Gatekeeper, or bypass an invalid signature. On Windows, do not
bypass an invalid or unknown Authenticode publisher warning.

Retry one fresh official download if the artifact is incomplete, corrupt, for
the wrong architecture, or fails a normal copy or extraction step. Do not loop.

## User handoff

If the host cannot download, mount, extract, copy, approve, repair, or run the
installer, stop trying. Tell the user what blocked automation and give them the
exact matching official URL above so they can install and open ChatCut with the
visible operating-system flow.

After ChatCut opens, ask the user to sign in there if needed. Do not handle their
credentials or add `chatcut_desktop` to `config.toml` manually. Because Codex
loads MCP tools and skills when a task starts, tell the user to start a new task
after Desktop finishes connecting.
