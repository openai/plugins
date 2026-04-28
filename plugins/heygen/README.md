# heygen

OpenAI Codex plugin for [HeyGen](https://heygen.com) — create AI avatar videos and personalized video messages.

## What's included

Two skills that chain together:

- **heygen-avatar** — turn a photo into a persistent digital twin. Handles avatar lookup, instant-avatar creation, voice selection (or voice cloning), and writes an `AVATAR` file the video skill reads back.
- **heygen-video** — generate identity-first presenter videos via the HeyGen v3 Video Agent pipeline. Encodes the prompting, asset routing, aspect-ratio correction, and avatar/voice resolution that good HeyGen videos need.
- **HeyGen app reference** — `.app.json` points at the curated [HeyGen ChatGPT app](https://chatgpt.com/apps/heygen/asdk_app_69418aad55e08191aa5e437b649ca2e4).

## Requirements

Installing the plugin connects the HeyGen ChatGPT app automatically (OAuth on first use). That is enough for the skills to work end-to-end on the user's existing HeyGen plan credits.

If you'd rather not use the app, the skills also support the HeyGen CLI: install it from <https://static.heygen.ai/cli/install.sh> and export `HEYGEN_API_KEY` (get one at <https://app.heygen.com/api>).

## Source of truth

The skills are authored in [`heygen-com/skills`](https://github.com/heygen-com/skills) (under `heygen-avatar/` and `heygen-video/` at the repo root) and mirrored here. The main structural delta in this mirror is the wrapping `skills/` parent directory required by the Codex plugin convention. File issues about skill content on that repo.

## License

MIT
