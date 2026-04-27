# heygen

OpenAI Codex plugin for [HeyGen](https://heygen.com) — create AI avatar videos and personalized video messages. Give your agent a face, a voice, and the ability to send video like a message.

## What's included

Two skills that chain together:

- **heygen-avatar** — turn a photo into a persistent digital twin. Handles avatar lookup, instant-avatar creation, voice selection (or voice cloning), and writes an `AVATAR` file the video skill reads back.
- **heygen-video** — generate identity-first presenter videos via the HeyGen v3 Video Agent pipeline. Encodes the prompting, asset routing, aspect-ratio correction, and avatar/voice resolution that good HeyGen videos need.

## Requirements

The skills shell out to the HeyGen CLI and require a HeyGen API key. Either:

- Install the CLI from <https://static.heygen.ai/cli/install.sh> and export `HEYGEN_API_KEY` (get one at <https://app.heygen.com/api>), **or**
- Connect HeyGen via MCP if your agent supports it — the skills will detect MCP and skip the CLI/API key path.

## Source of truth

The skills are authored in [`heygen-com/skills`](https://github.com/heygen-com/skills) (under `heygen-avatar/` and `heygen-video/` at the repo root) and mirrored here. File issues about skill content on that repo.

## License

MIT
