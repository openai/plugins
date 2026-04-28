# heygen

OpenAI Codex plugin for [HeyGen](https://heygen.com) — create AI avatar videos and personalized video messages. Give your agent a face, a voice, and the ability to send video like a message.

## What's included

Two skills that chain together, wired to the HeyGen ChatGPT app:

- **heygen-avatar** — turn a photo into a persistent digital twin. Handles avatar lookup, instant-avatar creation, voice selection (or voice cloning), and writes an `AVATAR` file the video skill reads back.
- **heygen-video** — generate identity-first presenter videos via the HeyGen v3 Video Agent pipeline. Encodes the prompting, asset routing, aspect-ratio correction, and avatar/voice resolution that good HeyGen videos need.
- **HeyGen app reference** — `.app.json` points at the curated [HeyGen ChatGPT app](https://chatgpt.com/apps/heygen/asdk_app_69418aad55e08191aa5e437b649ca2e4). The skills detect the app's tools at runtime and use them.

## Requirements

Installing the plugin connects the HeyGen ChatGPT app automatically (OAuth on first use). That's enough for the skills to work end-to-end — runs on the user's existing HeyGen plan credits.

If you'd rather not use the app, the skills also support the HeyGen CLI: install it from <https://static.heygen.ai/cli/install.sh> and export `HEYGEN_API_KEY` (get one at <https://app.heygen.com/api>). The skills detect the app first and fall back to the CLI.

## Source of truth

The skills are authored in [`heygen-com/skills`](https://github.com/heygen-com/skills) (under `heygen-avatar/` and `heygen-video/` at the repo root, each with its own `references/` subdirectory) and mirrored here. The only structural delta in this mirror is the wrapping `skills/` parent directory required by the Codex plugin convention. File issues about skill content on that repo.

## License

MIT
