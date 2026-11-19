# hyperframes

OpenAI Codex plugin for [HyperFrames](https://hyperframes.heygen.com) — an open-source video rendering framework where HTML is the source of truth for video.

## What's included

Imported from `heygen-com/hyperframes` `0.7.25`:

- **hyperframes** - router and capability map for video, animation, and motion-graphics requests
- **product-launch-video**, **website-to-video**, **faceless-explainer**, **pr-to-video**, **general-video** - end-to-end video creation workflows
- **embedded-captions**, **talking-head-recut**, **motion-graphics**, **music-to-video**, **slideshow**, **remotion-to-hyperframes** - specialized production workflows
- **hyperframes-core**, **hyperframes-animation**, **hyperframes-keyframes**, **hyperframes-creative**, **hyperframes-media**, **media-use**, **hyperframes-cli**, **hyperframes-registry** - domain skills for composition, animation, media, CLI usage, and registry components

## Requirements

The skills invoke the `hyperframes` CLI via `npx hyperframes`, which needs:

- Node.js >= 22
- FFmpeg on `PATH`

See [hyperframes.heygen.com/quickstart](https://hyperframes.heygen.com/quickstart) for full setup.

## Source of truth

The skills are authored in [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) (under `skills/` at the repo root) and mirrored here. File issues about skill content on that repo.
