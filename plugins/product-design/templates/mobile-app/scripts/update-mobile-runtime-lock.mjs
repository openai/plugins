#!/usr/bin/env node
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const lockPath = path.join(root, "mobile-runtime.lock.json");
const protectedFiles = [
  "scripts/check-mobile-runtime.mjs",
  "scripts/prepare-sites-build.mjs",
  "scripts/update-mobile-runtime-lock.mjs",
  "vite.config.ts",
  "src/App.tsx",
  "src/main.tsx",
  "src/styles.css",
  "src/mobile/BottomSheet.tsx",
  "src/mobile/Carousel.tsx",
  "src/mobile/Device.tsx",
  "src/mobile/FlowStack.tsx",
  "src/mobile/Keyboard.tsx",
  "src/mobile/MobileCursor.tsx",
  "src/mobile/MobileRuntime.tsx",
  "src/mobile/MobileScroll.tsx",
  "src/mobile/PhoneFrame.tsx",
  "src/mobile/assets.ts",
  "src/mobile/components.tsx",
  "src/mobile/geometry.ts",
  "src/mobile/index.ts",
  "public/assets/iphone/Bezel.png",
  "public/assets/iphone/Keyboard.png",
  "public/assets/android/Pixel10.png",
  "public/assets/android/Keyboard.png",
  "public/assets/android/navigation-bar.svg",
  "public/assets/status/status-icons.svg",
  "public/assets/status/ios-status-icons.svg",
  "worker/index.js",
];

const hashes = {};
for (const relativePath of protectedFiles) {
  const filePath = path.join(root, relativePath);
  if (!existsSync(filePath)) throw new Error(`Protected runtime file is missing: ${relativePath}`);
  hashes[relativePath] = createHash("sha256").update(readFileSync(filePath)).digest("hex");
}

writeFileSync(lockPath, `${JSON.stringify(hashes, null, 2)}\n`);
console.log(`Updated mobile-runtime.lock.json (${protectedFiles.length} protected files).`);
