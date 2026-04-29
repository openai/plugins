# Supabase Plugin for Codex

The Supabase plugin for [Codex](https://codex.openai.com) gives Codex the tools and skills needed to work effectively with Supabase projects.

## What's Included

- **MCP Server** — Remote connection to the [Supabase MCP server](https://supabase.com/mcp) for project management, SQL execution, migrations, and more
- **Skills** — Agent skills from [supabase/agent-skills](https://github.com/supabase/agent-skills) (e.g. `postgres-best-practices`)

## Development

This repo uses a git submodule for shared agent skills.

After cloning, initialize the submodule:

```bash
git submodule update --init --recursive
```

To update the submodule:

```bash
git submodule update --remote submodules/agent-skills
git add submodules/agent-skills
git commit -m "chore: update agent-skills submodule"
```

## Releasing

This repo uses [Release Please](https://github.com/googleapis/release-please) for automated releases.

1. Merge commits with `feat:` or `fix:` prefixes to trigger a release (see [How should I write my commits?](https://github.com/googleapis/release-please#how-should-i-write-my-commits))
2. Release Please opens a "Release PR" with version bump and changelog
3. Merge the Release PR to publish
4. `supabase-codex-plugin.tar.gz` is uploaded to the GitHub release

Note: Release Please is configured to only bump patch versions (0.1.x) until project is more stable.
