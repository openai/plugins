// ── Composer skeleton: astro.config.mjs ───────────────────────────────────────
// UNLIKE the other skeletons, this one is a MERGE TARGET, not a clobber. The
// scaffold's generated astro.config.mjs varies (integrations args, image.domains,
// vite.server settings differ run to run). Composer must NOT overwrite it with
// this file — it applies exactly two mutations to the scaffold's own config and
// preserves everything else (see COMPOSE.md § "2. astro.config.mjs"):
//
//   (1) register the Tailwind v4 Vite plugin   → vite.plugins: [tailwindcss()]
//   (2) fix the bare `process.env` reference    → globalThis guard (TS-safe)
//
// The shape below is the canonical post-mutation result for a typical scaffold —
// use it as the reference for what those two edits should produce.
// @ts-check
import { defineConfig } from "astro/config";
import wix from "@wix/astro";
import wixPages from "@wix/astro-pages";
import react from "@astrojs/react";
import cloudProviderFetchAdapter from "@wix/cloud-provider-fetch-adapter";
import tailwindcss from "@tailwindcss/vite"; // (1) added by Composer

// (2) `process.env` guarded so strict `tsc --noEmit` does not fail with
//     "Cannot find name 'process'" without an @types/node dependency.
const isBuild =
  (/** @type {any} */ (globalThis)).process?.env?.NODE_ENV === "production";

// https://astro.build/config
export default defineConfig({
  integrations: [wix(), wixPages(), react()],
  security: { checkOrigin: false },
  ...(isBuild && { adapter: cloudProviderFetchAdapter({}) }),

  image: {
    domains: ["static.wixstatic.com"],
  },

  vite: {
    plugins: [tailwindcss()], // (1) merge into any existing vite config
  },

  output: "server",
});
