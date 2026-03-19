#!/usr/bin/env node

// hooks/src/setup-telemetry.mts
import { readFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";
var PREF_PATH = join(homedir(), ".claude", "vercel-telemetry-preference");
function main() {
  let existing = null;
  try {
    existing = readFileSync(PREF_PATH, "utf-8").trim();
  } catch {
  }
  if (existing === "enabled" || existing === "disabled" || existing === "asked") {
    process.stdout.write(
      `Telemetry is currently ${existing}. To change, edit ~/.claude/vercel-telemetry-preference.
`
    );
    process.exit(0);
  }
  process.stdout.write(
    [
      "The Vercel plugin can collect anonymous telemetry data to help improve the plugin experience.",
      "Ask the user if they would like to enable anonymous telemetry. If they agree, run `echo 'enabled' > ~/.claude/vercel-telemetry-preference`. If they decline, run `echo 'disabled' > ~/.claude/vercel-telemetry-preference`.",
      ""
    ].join("\n")
  );
  process.exit(0);
}
main();
