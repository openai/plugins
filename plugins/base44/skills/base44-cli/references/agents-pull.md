# base44 agents pull

Pull AI agent configurations from Base44 to local files. Agents are conversational AI assistants that can interact with users, access your app's entities, and call backend functions.

## Syntax

```bash
npx base44 agents pull
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Fetches all agents from Base44
2. Writes agent files to the `base44/agents/` directory
3. Deletes local agent files that don't exist remotely
4. Reports written and deleted agents

## Prerequisites

- Must be run from a Base44 project directory
- Project must be linked to a Base44 app

## Output

```bash
$ npx base44 agents pull

Fetching agents from Base44...
✓ Agents fetched successfully

Syncing agent files...
✓ Agent files synced successfully

Written: support_agent, order_bot
Deleted: old_agent

Pulled 2 agents to base44/agents
```

When agents are already up to date (no changes):
```bash
$ npx base44 agents pull

Fetching agents from Base44...
✓ Agents fetched successfully

Syncing agent files...
✓ Agent files synced successfully

All agents are already up to date

Pulled 3 agents to base44/agents
```

## Agent Synchronization

The pull operation synchronizes remote agents to your local files:

- **Written**: Agent files created or updated from remote
- **Deleted**: Local agent files removed (didn't exist remotely)

**Warning**: This operation replaces all local agent configurations with remote versions. Any local changes not pushed to Base44 will be overwritten.

## Use Cases

- Sync agent configurations to a new development machine
- Get the latest agent configurations from your team
- Restore local agent files after accidental deletion
- Start working on an existing project with agents

## Notes

- This command syncs agent configurations, not conversation data
- Agent files are stored as `.jsonc` in the `base44/agents/` directory
- The directory location is configurable via `agentsDir` in `config.jsonc`
- Use `base44 agents push` to upload local changes to Base44
