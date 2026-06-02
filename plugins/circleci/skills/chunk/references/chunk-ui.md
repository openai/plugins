# Chunk UI Reference

Use this reference when the user asks about CircleCI web-app setup and usage of Chunk.

## Core Capability

Chunk in CircleCI provides chat-driven CI/CD assistance and proactive task scheduling for repository and pipeline maintenance.

## Prerequisites

- CircleCI GitHub App installed for the organization.
- Organization setting enabled: `Allow Chunk tasks`.
- Model provider configured:
- CircleCI-managed provider (no API key), or
- Bring-your-own provider (Anthropic, OpenAI, or Amazon Bedrock credentials).

## Setup Flow In CircleCI App

1. Open your organization in CircleCI.
2. Open `Chunk` from the sidebar.
3. Select `Set up Chunk`.
4. Confirm GitHub App install status.
5. Choose model provider.
6. Enter credentials when required and continue onboarding.

## Fix Buttons (Failure-Context Actions)

- Chunk can be launched directly from failure surfaces:
- `Fix error` on failing step output.
- `Fix job` on job surfaces.
- `Fix workflow` on workflow/pipeline surfaces.
- These buttons prefill failure context so users do not need to restate failing details.

## Environment Setup For Better Verification

- Add `.circleci/cci-agent-setup.yml` on default branch.
- Include exactly one workflow and one job named `cci-agent-setup`.
- Use this file only for environment provisioning (not full test execution).
- Chunk can pick this up automatically when default environment is selected.

## Contexts And Variables

- Project environment variables are available automatically.
- Context variables must be attached in `cci-agent-setup` job to be accessible.
- Additional Chunk environment secrets are stored in context names prefixed with `chunk-`.

## Troubleshooting Cues

- Missing Chunk sidebar option: verify `Allow Chunk tasks` toggle.
- OpenAI verification blockers: use documented fallback model-variable path when applicable.
- If Chunk is not configured, selecting a fix button can start setup automatically.

## Source

- [Chunk overview and setup (CircleCI docs)](https://circleci.com/docs/guides/toolkit/chunk-setup-and-overview/)
