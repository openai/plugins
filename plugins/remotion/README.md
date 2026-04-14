# @remotion/codex-plugin

OpenAI Codex plugin that packages [Remotion](https://remotion.dev) skills for AI-assisted video creation.

## Building

```bash
bun build.mts
```

This copies skills from `packages/skills/skills/` into the `skills/` directory in the Codex plugin format.

## Installation

See the [official OpenAI Codex plugin docs](https://developers.openai.com/codex/plugins/build) for how to install and test plugins locally.

## Plugin structure

```
.codex-plugin/
  plugin.json          # Plugin manifest
skills/
  remotion/            # Remotion best practices (animations, audio, etc.)
    SKILL.md
    rules/*.md
```

## Contributing

This repository is a mirror of [`packages/codex-plugin`](https://github.com/remotion-dev/remotion/tree/main/packages/codex-plugin) in the [Remotion monorepo](https://github.com/remotion-dev/remotion), which is the source of truth. Please send contributions there.

## Skills included

- **remotion** — Best practices for video creation with Remotion and React. Covers project setup, animations, timing, audio, captions, 3D, transitions, charts, text effects, fonts, and 30+ more topics.
