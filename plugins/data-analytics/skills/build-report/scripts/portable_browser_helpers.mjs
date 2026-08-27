import { existsSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { isAbsolute, join, resolve } from "node:path";

export const PORTABLE_READER_READY_STATE = "ready";
export const PORTABLE_READER_FAILURE_STATES = Object.freeze([
  "failed",
  "missing-runtime",
  "unsupported",
]);

export class PortableBrowserError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.name = "PortableBrowserError";
    this.code = code;
    this.details = details;
  }
}

function expandHome(value, home) {
  if (value === "~") return home;
  if (value.startsWith("~/") || value.startsWith("~\\")) {
    return join(home, value.slice(2));
  }
  return isAbsolute(value) ? value : resolve(value);
}

function cacheRoots({ env, home, platform }) {
  const roots = [];
  const configured = env.PLAYWRIGHT_BROWSERS_PATH?.trim();
  if (configured && configured !== "0") roots.push(expandHome(configured, home));

  if (platform === "darwin") {
    roots.push(
      join(home, "Library/Caches/ms-playwright"),
      join(home, ".cache/ms-playwright"),
    );
  } else if (platform === "win32") {
    if (env.LOCALAPPDATA) roots.push(join(env.LOCALAPPDATA, "ms-playwright"));
    roots.push(join(home, "AppData/Local/ms-playwright"));
  } else {
    roots.push(join(home, ".cache/ms-playwright"));
  }

  return [...new Set(roots)];
}

function executableSuffixes(platform) {
  if (platform === "darwin") {
    return [
      "chrome-headless-shell-mac-arm64/chrome-headless-shell",
      "chrome-headless-shell-mac-x64/chrome-headless-shell",
      "chrome-headless-shell-mac/chrome-headless-shell",
      "chrome-mac-arm64/headless_shell",
      "chrome-mac-x64/headless_shell",
      "chrome-mac/headless_shell",
    ];
  }
  if (platform === "win32") {
    return [
      "chrome-headless-shell-win64/chrome-headless-shell.exe",
      "chrome-headless-shell-win/chrome-headless-shell.exe",
      "chrome-win64/headless_shell.exe",
      "chrome-win/headless_shell.exe",
    ];
  }
  return [
    "chrome-headless-shell-linux64/chrome-headless-shell",
    "chrome-headless-shell-linux/chrome-headless-shell",
    "chrome-linux64/headless_shell",
    "chrome-linux/headless_shell",
  ];
}

function browserRevision(directory) {
  const match = /(?:chromium|chromium_headless_shell|chromium-headless-shell)-(\d+)$/.exec(directory);
  return match ? Number(match[1]) : -1;
}

function installedBrowserDirectories(root, { exists = existsSync, list = readdirSync } = {}) {
  if (!exists(root)) return [];
  return list(root)
    .filter((name) => /^(?:chromium|chromium_headless_shell|chromium-headless-shell)-\d+$/.test(name))
    .sort((left, right) => browserRevision(right) - browserRevision(left));
}

export function resolveChromiumExecutable({
  env = process.env,
  exists = existsSync,
  home = homedir(),
  list = readdirSync,
  packagedExecutable,
  platform = process.platform,
} = {}) {
  const configured = env.CHROMIUM_EXECUTABLE_PATH?.trim() ||
    env.PLAYWRIGHT_EXECUTABLE_PATH?.trim();
  if (configured) {
    const configuredPath = expandHome(configured, home);
    if (exists(configuredPath)) return configuredPath;
    throw new PortableBrowserError(
      "browser_unavailable",
      `Configured Chromium executable does not exist: ${configuredPath}`,
      { configuredPath },
    );
  }

  if (packagedExecutable && exists(packagedExecutable)) return packagedExecutable;

  const suffixes = executableSuffixes(platform);
  const searchedRoots = cacheRoots({ env, home, platform });
  for (const root of searchedRoots) {
    const directories = installedBrowserDirectories(root, { exists, list });
    for (const suffix of suffixes) {
      for (const directory of directories) {
        const candidate = join(root, directory, suffix);
        if (exists(candidate)) return candidate;
      }
    }
  }

  throw new PortableBrowserError(
    "browser_unavailable",
    "No installed Chromium headless-shell executable was found. Set CHROMIUM_EXECUTABLE_PATH " +
      "(or the legacy PLAYWRIGHT_EXECUTABLE_PATH) or preinstall Chromium headless-shell under " +
      "PLAYWRIGHT_BROWSERS_PATH; portable tooling never downloads browsers.",
    { searchedRoots },
  );
}

export async function waitForPortableReader(page, timeoutMs = 2_500) {
  try {
    await page.waitForFunction(
      ({ failures, ready }) => {
        const state = document.documentElement.dataset.dataAnalyticsPortableReader ?? "";
        return state === ready || failures.includes(state);
      },
      { failures: PORTABLE_READER_FAILURE_STATES, ready: PORTABLE_READER_READY_STATE },
      { timeout: timeoutMs },
    );
  } catch (error) {
    const state = await page.evaluate(
      () => document.documentElement.dataset.dataAnalyticsPortableReader ?? "unset",
    ).catch(() => "unavailable");
    throw new PortableBrowserError(
      "reader_timeout",
      `Portable reader did not reach a terminal state within ${timeoutMs}ms (state: ${state}).`,
      { state, timeoutMs, cause: error?.message },
    );
  }

  const state = await page.evaluate(
    () => document.documentElement.dataset.dataAnalyticsPortableReader ?? "unset",
  );
  if (state !== PORTABLE_READER_READY_STATE) {
    throw new PortableBrowserError(
      `reader_${state}`,
      `Portable reader entered terminal failure state: ${state}.`,
      { state },
    );
  }
  return state;
}

export function isLocalPortableRequest(url) {
  try {
    return ["about:", "blob:", "data:", "file:"].includes(new URL(url).protocol);
  } catch {
    return false;
  }
}
