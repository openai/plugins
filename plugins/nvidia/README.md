# Official NVIDIA Plugin

This plugin is **not** part of the `nvidia/skills` self-hosted marketplace. It is curated for delivery to the official OpenAI Bundled and Anthropic Official marketplaces.

The contents here (skills, plugin manifests) are generated from `plugins.d/nvidia.yml` by `.github/scripts/build-plugins.sh`. The yaml sets `marketplace_enabled.{claude,codex}: false`, which keeps it out of `.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json` while still producing a self-contained plugin folder ready to ship upstream.

To change which skills this plugin bundles, edit `plugins.d/nvidia.yml` and re-run the build script. Hand-maintained inside this directory: `assets/` (logo) and this README.
