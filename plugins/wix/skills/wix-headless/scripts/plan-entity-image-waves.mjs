#!/usr/bin/env node
// Build a deterministic execution plan for Image Phase 2 from a slim image
// agent's prompt array + the orchestrator's per-product / per-cms-item GETs.
//
// The slim image agent's only job is to return a list of brand-aligned prompts
// (one per entity). This script transforms that list (plus the entity details
// the orchestrator pre-fetched) into a structured plan the orchestrator can
// execute as a sequence of concurrent batches:
//
//   waves     — Runware generation requests, grouped into waves of <waveSize>
//               (default 3) to match the google:4@2 throttle. Each wave is
//               one orchestration step with N parallel curls in one shell,
//               backgrounded with `&`; each curl sends one task in the body array.
//
//   imports   — POST /site-media/v1/files/import requests, one per generated
//               image. Indexed by taskUUID so the orchestrator threads the
//               wave-result URL through to the import body.
//
//   patches   — Per-entity-type write requests (PATCH for products & blog
//               posts; PUT for CMS items). Bodies use placeholders the
//               orchestrator substitutes with import results:
//                 __IMAGE_URL__       — the full wixstatic URL (file.url)
//                 __IMAGE_FILE_ID__   — the file ID (file.fileUrl)
//
//   publishes — Re-publish calls for blog posts ONLY (PATCHing a published
//               draft un-publishes it). One per blog-post entity.
//
// Usage:
//   echo "$INPUT_JSON" | node plan-entity-image-waves.mjs
//
// The script is pure data transformation — no I/O beyond stdin / stdout, no
// MCP, no network. The encoded knowledge is the per-entity-type body shapes
// (frozen from references/images/INSTRUCTIONS.md so a single source of truth).

import { readFileSync } from "node:fs";

// Body shape constants — keep aligned with references/images/INSTRUCTIONS.md.
const RUNWARE_DEFAULTS = {
  taskType: "imageInference",
  outputType: "URL",
  outputFormat: "PNG",
  model: "google:4@2",
  numberResults: 1,
};

const DEFAULT_WAVE_SIZE = 3;

let input;
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch (e) {
  console.error(`plan-entity-image-waves: stdin is not valid JSON (${e.message})`);
  process.exit(2);
}

const prompts = Array.isArray(input.prompts) ? input.prompts : [];
if (prompts.length === 0) {
  console.error("plan-entity-image-waves: no prompts in input — nothing to plan");
  process.exit(2);
}

const productDetails = input.productDetails ?? {};
const cmsDetails = input.cmsDetails ?? {};
const waveSize = Math.max(1, Math.min(input.waveSize ?? DEFAULT_WAVE_SIZE, 8));
const model = input.model ?? RUNWARE_DEFAULTS.model;

// ---- 1. Runware waves (gen-side parallelism, throttle-bucketed) -----------
const waves = [];
for (let i = 0; i < prompts.length; i += waveSize) {
  const slice = prompts.slice(i, i + waveSize);
  waves.push(slice.map((p) => ({
    taskUUID: p.taskUUID,
    body: [{
      ...RUNWARE_DEFAULTS,
      model,
      taskUUID: p.taskUUID,
      positivePrompt: p.positivePrompt,
      width: p.width ?? 1024,
      height: p.height ?? 1024,
      outputFormat: p.outputFormat ?? RUNWARE_DEFAULTS.outputFormat,
    }],
  })));
}

// ---- 2. Wix Media imports (one per generated image) -----------------------
const imports = prompts.map((p) => ({
  taskUUID: p.taskUUID,
  mimeType: p.outputFormat === "JPG" ? "image/jpeg" : "image/png",
  displayName: p.displayName ?? `${p.entityId}.${(p.outputFormat ?? "PNG").toLowerCase()}`,
}));

// ---- 3. Per-entity-type write requests ------------------------------------
const patches = [];
const publishes = [];

for (const p of prompts) {
  if (p.entityType === "product") {
    const detail = productDetails[p.entityId];
    if (!detail) {
      console.error(`plan-entity-image-waves: missing productDetails for entityId=${p.entityId}`);
      process.exit(1);
    }
    if (detail.revision === undefined || detail.revision === null) {
      console.error(`plan-entity-image-waves: productDetails[${p.entityId}].revision is required (mandatory per Update-Product endpoint)`);
      process.exit(1);
    }
    patches.push({
      taskUUID: p.taskUUID,
      entityType: "product",
      entityId: p.entityId,
      method: "PATCH",
      url: `https://www.wixapis.com/stores/v3/products/${p.entityId}`,
      // Body echoes options + variantsInfo (mandatory — see images/INSTRUCTIONS.md
      // §428-prevention) and embeds the URL via __IMAGE_URL__ placeholder.
      body: {
        product: {
          revision: detail.revision,
          media: {
            itemsInfo: {
              items: [{ url: "__IMAGE_URL__", altText: p.displayName ?? p.entityId }],
            },
          },
          ...(detail.options !== undefined ? { options: detail.options } : {}),
          ...(detail.variantsInfo !== undefined ? { variantsInfo: detail.variantsInfo } : {}),
        },
      },
    });
  } else if (p.entityType === "blogPost") {
    patches.push({
      taskUUID: p.taskUUID,
      entityType: "blogPost",
      entityId: p.entityId,
      method: "PATCH",
      url: `https://www.wixapis.com/blog/v3/draft-posts/${p.entityId}`,
      // Blog uses the file ID (fileUrl), not the wixstatic URL.
      body: {
        draftPost: {
          media: { wixMedia: { image: { id: "__IMAGE_FILE_ID__" } } },
        },
      },
    });
    publishes.push({
      entityId: p.entityId,
      method: "POST",
      url: `https://www.wixapis.com/blog/v3/draft-posts/${p.entityId}/publish`,
    });
  } else if (p.entityType === "cmsItem") {
    const detail = cmsDetails[p.entityId];
    if (!detail) {
      console.error(`plan-entity-image-waves: missing cmsDetails for entityId=${p.entityId}`);
      process.exit(1);
    }
    if (!detail.collectionId || !detail.imageField || !detail.data) {
      console.error(`plan-entity-image-waves: cmsDetails[${p.entityId}] requires collectionId, imageField, and data (existing item record)`);
      process.exit(1);
    }
    // Read-merge-PUT: echo every existing data field, set the image field
    // to the placeholder URL. Echoing every existing field is what prevents wiping the rest of the record.
    const mergedData = { ...detail.data, [detail.imageField]: "__IMAGE_URL__" };
    patches.push({
      taskUUID: p.taskUUID,
      entityType: "cmsItem",
      entityId: p.entityId,
      method: "PUT",
      url: `https://www.wixapis.com/wix-data/v2/items/${p.entityId}`,
      body: {
        dataCollectionId: detail.collectionId,
        dataItem: { id: p.entityId, data: mergedData },
      },
    });
  } else {
    console.error(`plan-entity-image-waves: unknown entityType "${p.entityType}" for entityId=${p.entityId} — must be product | blogPost | cmsItem`);
    process.exit(1);
  }
}

const plan = {
  meta: {
    promptCount: prompts.length,
    waveCount: waves.length,
    waveSize,
    model,
  },
  waves,
  imports,
  patches,
  publishes,
};

console.log(JSON.stringify(plan, null, 2));
