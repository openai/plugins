# heygen

OpenAI Codex plugin for [HeyGen](https://heygen.com) — create AI avatar videos and personalized video messages. Give your agent a face, a voice, and the ability to send video like a message.

## What's included

Two skills that chain together, plus the official HeyGen MCP server:

- **heygen-avatar** — turn a photo into a persistent digital twin. Handles avatar lookup, instant-avatar creation, voice selection (or voice cloning), and writes an `AVATAR` file the video skill reads back.
- **heygen-video** — generate identity-first presenter videos via the HeyGen v3 Video Agent pipeline. Encodes the prompting, asset routing, aspect-ratio correction, and avatar/voice resolution that good HeyGen videos need.
- **HeyGen MCP** (`https://mcp.heygen.com/mcp/v1/`) — official HTTP MCP server bundled via `.mcp.json`. The skills auto-detect it and use it instead of the CLI.

## Requirements

Installing the plugin wires up the HeyGen MCP server automatically (OAuth on first use), and that's enough for the skills to work end-to-end.

If you'd rather not use MCP, the skills also support the HeyGen CLI: install it from <https://static.heygen.ai/cli/install.sh> and export `HEYGEN_API_KEY` (get one at <https://app.heygen.com/api>). The skills detect MCP first and fall back to the CLI.

## Source of truth

The skills are authored in [`heygen-com/skills`](https://github.com/heygen-com/skills) (under `heygen-avatar/` and `heygen-video/` at the repo root) and mirrored here. File issues about skill content on that repo.

## License

MIT
