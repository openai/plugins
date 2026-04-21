# hyperframes

OpenAI Codex plugin for [HyperFrames](https://hyperframes.heygen.com) — an open-source video rendering framework where HTML is the source of truth for video.

## What's included

Five skills for authoring and rendering video:

- **hyperframes** — composition authoring (HTML + CSS + GSAP), visual styles, palettes, house style, motion principles, transitions, captions, audio-reactive visuals
- **hyperframes-cli** — `hyperframes init / lint / preview / render / transcribe / tts / doctor / browser`
- **hyperframes-registry** — `hyperframes add` to install reusable blocks and components (social overlays, shader transitions, data viz, effects)
- **gsap** — tweens, timelines, easing, stagger, performance
- **website-to-hyperframes** — 7-step pipeline that captures a URL and produces a finished video

## Requirements

The skills invoke the `hyperframes` CLI via `npx hyperframes`, which needs:

- Node.js ≥ 22
- FFmpeg on `PATH`

See [hyperframes.heygen.com/quickstart](https://hyperframes.heygen.com/quickstart) for full setup.

## Source of truth

The skills are authored in [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) (under `skills/` at the repo root) and mirrored here. File issues about skill content on that repo.
