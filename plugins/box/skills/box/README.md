# Box Content API — Codex Skill

An [OpenAI Codex](https://openai.com/index/openai-codex/) skill that helps Codex build and troubleshoot Box integrations: uploads, folders, downloads, shared links, collaborations, search, metadata, webhooks, and Box AI retrieval.

## Installation

Copy or clone this folder into your Codex skills directory:

```bash
# Example: install into the default Codex skills location
cp -r box-content-api ~/.codex/skills/
```

Once installed, invoke the skill in any Codex conversation with `$box-content-api`.

## What's included

```
├── SKILL.md                          # Entry point — workflow, guardrails, and verification
├── agents/openai.yaml                # UI metadata for skill lists and chips
├── references/
│   ├── auth-and-setup.md             # Auth paths, SDK vs REST, codebase inspection
│   ├── box-cli.md                    # CLI-first local verification
│   ├── workflows.md                  # Quick router when the task is ambiguous
│   ├── content-workflows.md          # Uploads, folders, shared links, collaborations, metadata, moves
│   ├── bulk-operations.md            # Batch moves, folder restructuring, serial execution, rate limits
│   ├── webhooks-and-events.md        # Webhook setup, events, idempotency
│   ├── ai-and-retrieval.md           # Search-first retrieval and Box AI
│   └── troubleshooting.md            # Common failure modes and debugging
├── scripts/
│   ├── box_cli_smoke.py              # Smoke tests via Box CLI
│   └── box_rest.py                   # Smoke tests via Box REST API (stdlib only)
└── examples/
    └── box-content-api-prompts.md    # Example prompts
```

## Prerequisites

- **Python 3.10+** — both scripts use only the standard library.
- **Box CLI** (optional) — install from [developer.box.com/guides/cli](https://developer.box.com/guides/cli) for CLI-first verification. If unavailable, the skill falls back to `scripts/box_rest.py` with a `BOX_ACCESS_TOKEN`.

## Quick smoke test

```bash
# With Box CLI installed and authenticated:
python3 scripts/box_cli_smoke.py check-auth
python3 scripts/box_cli_smoke.py list-folder-items 0 --max-items 5

# With a bearer token instead:
export BOX_ACCESS_TOKEN="your-token"
python3 scripts/box_rest.py get-item --item-type folder --item-id 0
```

## License

See [LICENSE](LICENSE) if present, or contact the repository owner.
