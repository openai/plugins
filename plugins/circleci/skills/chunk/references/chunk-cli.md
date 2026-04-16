# Chunk CLI Reference

Use this reference when the user asks for terminal-driven Chunk workflows.

## What `chunk-cli` Is For

- Initialize local projects for agent hooks and validation.
- Run configured validations before pushing.
- Generate AI review context from GitHub PR comments.
- Manage Chunk authentication, sandbox workflows, and task execution from CLI.

## Requirements

- macOS or Linux (arm64/x86_64).
- GitHub CLI (`gh`) installed and authenticated for prompt/context generation.
- CircleCI personal API token available for cloud task and sandbox commands.

## Installation Steps

1. Install with Homebrew:
```bash
brew install CircleCI-Public/circleci/chunk
```
2. Verify install:
```bash
chunk --help
```
3. (Optional) Install shell completion:
```bash
chunk completion install
```
4. Authenticate dependencies you plan to use:
```bash
gh auth status
chunk auth login
```

## Quick-Start Commands

```bash
chunk init
chunk validate
chunk validate tests
chunk validate --list
chunk build-prompt
chunk build-prompt --org myorg --repos api,backend --top 10
chunk skill install
```

## Command Families

- `chunk auth login|status|logout`
- `chunk sandbox list|create|exec|ssh|sync|env|build`
- `chunk sandbox env setup`
- `chunk sandbox template create`
- `chunk init`
- `chunk validate [name]`
- `chunk skill install|list`
- `chunk task config|run`
- `chunk build-prompt`
- `chunk completion install|uninstall`
- `chunk upgrade`

## Configure Cloud Tasks (`chunk task config`)

Use this flow when users want to run Chunk tasks in CircleCI cloud environments from CLI.

1. Export CircleCI token:
```bash
export CIRCLE_TOKEN=your-token-here
```
2. Collect required IDs:
- `org_id`: CircleCI app -> Organization Settings -> Overview
- `project_id`: CircleCI app -> Project Settings -> Overview
- `definition_id`: UUID from the target Chunk pipeline definition page
3. From repository root, run setup wizard:
```bash
chunk task config
```
4. Provide org/project IDs and at least one named definition (for example `dev` or `prod`).
5. Confirm `.chunk/run.json` is created.

Example `.chunk/run.json`:
```json
{
  "org_id": "<circleci-org-uuid>",
  "project_id": "<circleci-project-uuid>",
  "org_type": "github",
  "definitions": {
    "dev": {
      "definition_id": "<pipeline-definition-uuid>",
      "default_branch": "main"
    }
  }
}
```

Run cloud tasks after config:
```bash
# Use a named definition
chunk task run --definition dev --prompt "Fix the flaky test in auth.spec.ts"

# Override branch
chunk task run --definition dev --prompt "Refactor payment retries" --branch my-feature-branch

# Create a new branch
chunk task run --definition dev --prompt "Add type annotations" --new-branch

# Or use a raw definition UUID directly
chunk task run --definition 550e8400-e29b-41d4-a716-446655440000 --prompt "Fix flaky test"
```

## Environment Variables

- `ANTHROPIC_API_KEY`: required for `build-prompt`; optional for `init`.
- `GITHUB_TOKEN`: GitHub PAT (`repo` scope) for `build-prompt`.
- `CIRCLE_TOKEN`: CircleCI personal API token for `sandbox` and `task`.
- `CHUNK_HOOK_ENABLE`: toggle hook automation (`0`/`1`).

## Sandbox Notes

- Sandbox environments and related setup flows may be private preview.
- When using sandbox commands, confirm auth and required tokens before execution.
- Prefer read-first commands (`list`, `status`) before mutating actions (`create`, task runs).

## Sources

- [Chunk CLI README](https://github.com/CircleCI-Public/chunk-cli/)
