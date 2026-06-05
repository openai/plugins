#!/usr/bin/env node

import { createHash, randomUUID } from "node:crypto";
import { existsSync, readFileSync, watch } from "node:fs";
import { copyFile, mkdir, open, rm, writeFile } from "node:fs/promises";
import { basename, dirname, join, relative, resolve } from "node:path";
import { execFile, execFileSync, spawn } from "node:child_process";
import { tmpdir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { promisify } from "node:util";
import {
  createPackageProjectFile,
  generatedPackageConfigurationSwiftSource,
} from "./lib/xcode-project.mjs";

const TARGET_NAME = "PreviewHost";
const PACKAGE_PLUGIN_TARGET_NAME = "PreviewReloadPlugin";
const BUNDLE_ID = "dev.swiftui-preview-browser.host";
const HOT_RELOAD_NOTIFICATION = "dev.swiftui-preview-browser.reload";
const TEMPLATE_ROOT = join(dirname(fileURLToPath(import.meta.url)), "templates");
const TEMPLATE_FILE_NAMES = [
  "FocusedPreviewApp.swift",
  "FocusedPreviewHotReloadRuntime.swift",
  "PreviewBrowserEntries.swift",
];
const CONFIGURATION_FILE_NAME = "PreviewBrowserConfiguration.swift";
const execFileAsync = promisify(execFile);

/**
 * Runs the preview-browser workflow from command-line arguments.
 *
 * This resolves the Swift Package module, launches a generated host app in
 * Simulator, and starts watching the package for hot reloads.
 *
 * @param {string[]} argv Command-line arguments excluding `node` and script path.
 * @returns {Promise<void>}
 */
export async function main(argv) {
  const options = parseArgs(argv);
  if (options.help) {
    printHelp();
    return;
  }

  const packageSwiftPath = resolvePackageSwiftPath(options.packageSwiftPath);
  const packagePreviewConfiguration = resolvePackagePreviewConfiguration(packageSwiftPath, options);
  const scratchRoot = defaultScratchRoot(packageSwiftPath, packagePreviewConfiguration);
  const buildRoot = join(scratchRoot, "build");
  const projectRoot = join(scratchRoot, "GeneratedPreviewHost");
  const udid = options.device;

  const state = {
    projectRoot,
    buildRoot,
    packagePreviewConfiguration,
    udid,
    dataContainer: null,
    appPid: null,
    previewName: packagePreviewConfiguration.previewFilters?.join(", ")
      ?? `${packagePreviewConfiguration.packageModule} previews`,
    hotReloading: false,
    hotReloadQueued: false,
  };

  log(`Package.swift: ${packageSwiftPath}`);
  log(`package: ${packagePreviewConfiguration.packageRoot}`);
  log(`product: ${packagePreviewConfiguration.packageProduct}`);
  log(`module: ${packagePreviewConfiguration.packageModule}`);
  if (packagePreviewConfiguration.previewFilters) {
    log(`preview filters: ${packagePreviewConfiguration.previewFilters.join(", ")}`);
  }
  log(`simulator: ${udid}`);
  await ensureBooted(udid);
  await buildAndLaunchPackage(state);
  console.log(`swiftui-preview-browser ready on simulator ${udid}`);

  const handleChange = async () => {
    log("change detected; hot reloading");
    await enqueueHotReload(state);
  };

  watchPackageTree(state.packagePreviewConfiguration.packageRoot, handleChange);
}

/**
 * Parses supported CLI flags into the options consumed by the launcher.
 *
 * @param {string[]} argv Raw command-line arguments.
 * @returns {object} Normalized launcher options.
 */
function parseArgs(argv) {
  const options = {
    packageSwiftPath: null,
    device: null,
    packageTarget: null,
    previewFilters: null,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      options.help = true;
    } else if (arg === "--device" || arg === "-d") {
      options.device = argv[++index];
    } else if (arg === "--package-target") {
      options.packageTarget = argv[++index];
    } else if (arg === "--preview-filter") {
      options.previewFilters = parsePreviewFilters(argv[++index]);
    } else if (!options.packageSwiftPath) {
      options.packageSwiftPath = arg;
    } else {
      throw new Error(`Unexpected argument: ${arg}`);
    }
  }

  if (!options.help && !options.packageSwiftPath) {
    throw new Error("Pass the path to Package.swift.");
  }
  if (!options.help && !options.packageTarget) {
    throw new Error("Pass --package-target <target> to choose which Swift Package target to preview.");
  }
  if (!options.help && !options.device) {
    throw new Error("Pass --device <simulator-udid> to choose the Simulator explicitly.");
  }
  return options;
}

/**
 * Prints the command-line usage and supported flags.
 *
 * @returns {void}
 */
function printHelp() {
  console.log(`swiftui-preview-browser

Render SwiftUI previews from one Swift Package target in an iOS Simulator.

Usage:
  swiftui-preview-browser <Package.swift> --package-target <target> --device <simulator-udid>

Options:
  --package-target  Swift Package target to scan. Required.
  --preview-filter  Comma-separated regex filters matched against preview names and identifiers.
  --device, -d      Simulator UDID. Required.
`);
}

/**
 * Resolves and validates the `Package.swift` file selected by the user.
 *
 * @param {string} file User-provided `Package.swift` path.
 * @returns {string} Absolute path to an existing `Package.swift`.
 */
function resolvePackageSwiftPath(file) {
  const resolved = resolve(file);
  if (!existsSync(resolved) || basename(resolved) !== "Package.swift") {
    throw new Error(`Package.swift not found: ${resolved}`);
  }
  return resolved;
}

/**
 * Creates a stable scratch-directory path for one module preview selection.
 *
 * Including selection details lets separate sessions from one package avoid
 * rewriting each other's generated project.
 *
 * @param {string} packageSwiftPath Absolute path to `Package.swift`.
 * @param {object} packagePreviewConfiguration Resolved preview selection and build metadata.
 * @returns {string} Generated scratch directory.
 */
function defaultScratchRoot(packageSwiftPath, packagePreviewConfiguration) {
  const identity = JSON.stringify({
    packageSwiftPath,
    packageModule: packagePreviewConfiguration.packageModule,
    previewFilters: packagePreviewConfiguration.previewFilters,
  });
  const scratchId = createHash("sha256").update(identity).digest("hex").slice(0, 12);
  return join(tmpdir(), "swiftui-preview-browser", scratchId);
}

/**
 * Generates, builds, installs, and launches the disposable preview host app.
 *
 * @param {object} state Mutable launcher state for the current preview session.
 * @returns {Promise<void>}
 */
async function buildAndLaunchPackage(state) {
  try {
    await rm(state.projectRoot, { recursive: true, force: true });
    await mkdir(join(state.projectRoot, `${TARGET_NAME}.xcodeproj`), { recursive: true });
    await mkdir(join(state.projectRoot, TARGET_NAME), { recursive: true });

    await copySwiftTemplates(state.projectRoot);
    await writeFile(
      join(state.projectRoot, TARGET_NAME, CONFIGURATION_FILE_NAME),
      generatedPackageConfigurationSwiftSource({
        packageModule: state.packagePreviewConfiguration.packageModule,
        previewFilters: state.packagePreviewConfiguration.previewFilters,
      }),
    );
    await writeFile(
      join(state.projectRoot, `${TARGET_NAME}.xcodeproj`, "project.pbxproj"),
      createPackageProjectFile({
        targetName: TARGET_NAME,
        bundleId: BUNDLE_ID,
        packageRelativePath: relative(state.projectRoot, state.packagePreviewConfiguration.packageRoot) || ".",
        packageProduct: state.packagePreviewConfiguration.packageProduct,
        pluginTargetName: PACKAGE_PLUGIN_TARGET_NAME,
        deploymentTarget: state.packagePreviewConfiguration.deploymentTarget,
      }),
    );

    const buildLogPath = join(state.buildRoot, "logs", "preview-host.log");
    await run(
      "xcodebuild",
      [
        "-project",
        join(state.projectRoot, `${TARGET_NAME}.xcodeproj`),
        "-scheme",
        TARGET_NAME,
        "-configuration",
        "Debug",
        "-destination",
        `id=${state.udid}`,
        "-sdk",
        "iphonesimulator",
        "-derivedDataPath",
        state.buildRoot,
        "CODE_SIGNING_ALLOWED=NO",
        "build",
      ],
      {
        cwd: state.projectRoot,
        timeoutMs: 900_000,
        outputFile: buildLogPath,
      },
    );
    log(`built preview host; build log: ${buildLogPath}`);

    const appPath = join(
      state.buildRoot,
      "Build/Products/Debug-iphonesimulator",
      `${TARGET_NAME}.app`,
    );
    if (!existsSync(appPath)) {
      throw new Error(`Build succeeded but app bundle was not found: ${appPath}`);
    }

    await run("xcrun", ["simctl", "terminate", state.udid, BUNDLE_ID], {
      allowFailure: true,
      logOutput: true,
    });
    await run("xcrun", ["simctl", "install", state.udid, appPath], { logOutput: true });
    state.dataContainer = await appDataContainer(state.udid);
    await rm(join(state.dataContainer, "Documents", "swiftui-preview-browser"), {
      recursive: true,
      force: true,
    });
    const launchResult = await run(
      "xcrun",
      ["simctl", "launch", state.udid, BUNDLE_ID],
      { logOutput: true },
    );
    state.appPid = launchPid(launchResult);
    await waitForHostReady(state);

    log(`launched package preview host for ${state.previewName}`);
  } catch (error) {
    log(error instanceof Error ? error.message : String(error));
    throw error;
  }
}

/**
 * Copies the reusable Swift preview host sources into the disposable project.
 *
 * Only the package import and filter values are generated per run; the
 * runtime, preview UI, and reload bridge remain ordinary Swift source files.
 *
 * @param {string} projectRoot Root directory of the generated Xcode project.
 * @returns {Promise<void>}
 */
async function copySwiftTemplates(projectRoot) {
  await Promise.all(
    TEMPLATE_FILE_NAMES.map((fileName) =>
      copyFile(join(TEMPLATE_ROOT, fileName), join(projectRoot, TARGET_NAME, fileName)),
    ),
  );
}

/**
 * Starts a hot reload while converting failures into already-logged events.
 *
 * This is used by the file watcher so a failed edit does not terminate watch
 * mode and the next edit can recover.
 *
 * @param {object} state Mutable launcher state.
 * @returns {Promise<void>}
 */
async function enqueueHotReload(state) {
  try {
    await hotReload(state);
  } catch {
    // hotReload already logged the failure.
  }
}

/**
 * Serializes hot reload work and queues one follow-up reload when edits race.
 *
 * @param {object} state Mutable launcher state.
 * @returns {Promise<void>}
 */
async function hotReload(state) {
  if (state.hotReloading) {
    state.hotReloadQueued = true;
    return;
  }

  state.hotReloading = true;

  try {
    await hotReloadPackage(state);
  } finally {
    state.hotReloading = false;
    if (state.hotReloadQueued) {
      state.hotReloadQueued = false;
      void enqueueHotReload(state);
    }
  }
}

/**
 * Compiles the updated package-backed preview into a dylib and injects it.
 *
 * The host reads a reload manifest from its documents directory, loads that
 * dylib in process, and reports the PID so this method can prove no relaunch
 * occurred.
 *
 * @param {object} state Mutable launcher state.
 * @returns {Promise<void>}
 */
async function hotReloadPackage(state) {
  try {
    const hostBefore = readHostStatus(state);
    const expectedPid = hostBefore?.pid ?? state.appPid;

    const token = randomUUID();
    const buildLogPath = join(state.buildRoot, "logs", "hot-reload.log");
    await run(
      "xcodebuild",
      [
        "-project",
        join(state.projectRoot, `${TARGET_NAME}.xcodeproj`),
        "-scheme",
        PACKAGE_PLUGIN_TARGET_NAME,
        "-configuration",
        "Debug",
        "-destination",
        `id=${state.udid}`,
        "-sdk",
        "iphonesimulator",
        "-derivedDataPath",
        state.buildRoot,
        "CODE_SIGNING_ALLOWED=NO",
        "build",
      ],
      {
        cwd: state.projectRoot,
        timeoutMs: 900_000,
        outputFile: buildLogPath,
      },
    );
    log(`built hot reload plugin; build log: ${buildLogPath}`);

    const dylibPath = join(
      state.buildRoot,
      "Build/Products/Debug-iphonesimulator",
      `lib${PACKAGE_PLUGIN_TARGET_NAME}.dylib`,
    );
    if (!existsSync(dylibPath)) {
      throw new Error(`Package hot reload build succeeded but dylib was not found: ${dylibPath}`);
    }

    const reloadDir = join(state.dataContainer, "Documents", "swiftui-preview-browser");
    await mkdir(reloadDir, { recursive: true });
    const containerDylibPath = join(reloadDir, `lib${PACKAGE_PLUGIN_TARGET_NAME}-${token}.dylib`);
    await copyFile(dylibPath, containerDylibPath);
    const manifestPath = join(reloadDir, "reload.json");
    await writeFile(manifestPath, JSON.stringify({ token, dylibPath: containerDylibPath }));
    await run("xcrun", ["simctl", "spawn", state.udid, "notifyutil", "-p", HOT_RELOAD_NOTIFICATION], {
      logOutput: true,
    });

    const hostAfter = await waitForHostReload(state, token);
    if (expectedPid && hostAfter.pid !== expectedPid) {
      throw new Error(`Hot reload changed PID from ${expectedPid} to ${hostAfter.pid}`);
    }

    state.appPid = hostAfter.pid;
    log(`hot reloaded package preview ${state.previewName} in pid ${hostAfter.pid}`);
  } catch (error) {
    log(error instanceof Error ? error.message : String(error));
    throw error;
  }
}

/**
 * Derives all build and selection information for a Swift Package preview.
 *
 * The target is selected explicitly by the user, while the linkable library
 * product is selected internally from `Package.swift`.
 *
 * @param {string} packageSwiftPath Absolute path to `Package.swift`.
 * @param {object} options Parsed CLI options.
 * @returns {object} Package target, product, filters, and build settings.
 */
function resolvePackagePreviewConfiguration(packageSwiftPath, options) {
  const packageRoot = dirname(packageSwiftPath);
  const packageDump = runJson("swift", ["package", "dump-package", "--package-path", packageRoot]);
  const packageTarget = resolvePackageTarget(options.packageTarget, packageDump);
  const packageProduct = inferPackageProduct(packageTarget, packageDump);
  const packageDescription = runJson(
    "swift",
    ["package", "--package-path", packageRoot, "describe", "--type", "json"],
  );
  const packageModule = resolvePackageModule(packageTarget, packageDescription);
  const previewFilters = options.previewFilters;
  const deploymentTarget = inferPackageDeploymentTarget(packageDump);

  return {
    packageRoot,
    packageProduct,
    packageModule,
    previewFilters,
    deploymentTarget,
  };
}

/**
 * Validates the package target/module requested for preview discovery.
 *
 * @param {string} requestedTarget Requested module name.
 * @param {object} packageDump Parsed `swift package dump-package` output.
 * @returns {string} Swift package target/module name.
 */
function resolvePackageTarget(requestedTarget, packageDump) {
  const target = (packageDump.targets ?? []).find((candidate) =>
    candidate.name === requestedTarget && candidate.type === "regular",
  );
  if (target) {
    return target.name;
  }

  throw new Error(`Swift package does not contain a regular target named "${requestedTarget}".`);
}

/**
 * Resolves the importable module identifier computed by Swift Package Manager.
 *
 * SwiftPM target names may contain characters such as hyphens that are invalid
 * in Swift imports, so use the target's described C99-compatible module name.
 *
 * @param {string} packageTarget Selected Swift package target name.
 * @param {object} packageDescription Parsed `swift package describe --type json` output.
 * @returns {string} Swift module name to use in generated imports.
 */
function resolvePackageModule(packageTarget, packageDescription) {
  const target = (packageDescription.targets ?? []).find((candidate) =>
    candidate.name === packageTarget,
  );
  if (target?.c99name) {
    return target.c99name;
  }

  throw new Error(`Swift package target "${packageTarget}" does not expose an importable module name.`);
}

/**
 * Finds the exported library product that contains the preview target.
 *
 * Product selection is internal because users select modules rather than link
 * artifacts. Prefer a product named after the target, then the smallest
 * product exporting it, then alphabetical order for deterministic builds.
 * Explicit dynamic products are unsupported because hot reload only replaces
 * the generated preview plugin dylib, leaving an already-loaded framework stale.
 *
 * @param {string} packageTarget Target/module containing the preview.
 * @param {object} packageDump Parsed `swift package dump-package` output.
 * @returns {string} Product name to link into the generated host.
 */
function inferPackageProduct(packageTarget, packageDump) {
  const products = (packageDump.products ?? [])
    .filter((product) =>
      product.type?.library != null && (product.targets ?? []).includes(packageTarget),
    );
  const supportedProducts = products.filter((product) => !product.type.library.includes("dynamic"));
  const product = supportedProducts.find(({ name }) => name === packageTarget)
    ?? supportedProducts.sort((left, right) =>
      (left.targets?.length ?? 0) - (right.targets?.length ?? 0)
      || left.name.localeCompare(right.name)
    )[0];
  if (product) {
    return product.name;
  }
  if (products.length > 0) {
    throw new Error(
      `Swift package target "${packageTarget}" is only exported by dynamic library products. `
      + "Dynamic library products are not supported because hot reload only replaces the generated preview plugin dylib.",
    );
  }
  throw new Error(`Swift package target "${packageTarget}" is not exported by a library product.`);
}

/**
 * Uses at least iOS 17 for the generated host because it uses Observation.
 * A package that supports earlier systems can still be linked into that host.
 *
 * @param {object} packageDump Parsed `swift package dump-package` output.
 * @returns {string} iOS deployment target version.
 */
function inferPackageDeploymentTarget(packageDump) {
  const iosPlatform = (packageDump.platforms ?? []).find((platform) => platform.platformName === "ios");
  const packageDeploymentTarget = iosPlatform?.version ?? "17.0";
  return Number.parseFloat(packageDeploymentTarget) < 17 ? "17.0" : packageDeploymentTarget;
}

/**
 * Parses user-supplied comma-separated preview selection filters.
 *
 * @param {string} value Filter argument passed to `--preview-filter`.
 * @returns {string[]} Non-empty filters in user-specified order.
 */
function parsePreviewFilters(value) {
  const filters = value
    ?.split(",")
    .map((filter) => filter.trim())
    .filter(Boolean);
  if (!filters?.length) {
    throw new Error("Pass at least one non-empty value to --preview-filter.");
  }
  return filters;
}

/**
 * Boots the selected simulator, waiting until it is ready for install/launch.
 *
 * @param {string} udid Simulator identifier.
 * @returns {Promise<void>}
 */
async function ensureBooted(udid) {
  const json = runJson("xcrun", ["simctl", "list", "devices", "available", "-j"]);
  const device = Object.values(json.devices ?? {}).flat().find((entry) => entry.udid === udid);
  if (!device) throw new Error(`Simulator not found: ${udid}`);
  if (device.state !== "Booted") {
    log(`booting ${device.name}`);
    await run("xcrun", ["simctl", "boot", udid], { allowFailure: true, logOutput: true });
  }
  await run("xcrun", ["simctl", "bootstatus", udid, "-b"], {
    timeoutMs: 120_000,
    logOutput: true,
  });
}

/**
 * Watches the package tree and schedules a reload whenever source content changes.
 *
 * A short debounce collapses the multiple filesystem events commonly emitted
 * by a single editor save into one reload.
 *
 * @param {string} packageRoot Absolute package root path.
 * @param {() => Promise<void> | void} onChange Reload callback.
 * @returns {void}
 */
function watchPackageTree(packageRoot, onChange) {
  let reloadTimer = null;
  watch(packageRoot, { recursive: true }, (_eventType, fileName) => {
    if (fileName && shouldSkipWatchedPackagePath(fileName)) return;

    clearTimeout(reloadTimer);
    reloadTimer = setTimeout(() => void onChange(), 250);
  });
}

/**
 * Excludes generated and VCS paths that should not trigger hot reload.
 *
 * @param {string} fileName Package-relative path reported by `fs.watch`.
 * @returns {boolean} Whether the path belongs to an excluded directory.
 */
function shouldSkipWatchedPackagePath(fileName) {
  return fileName.split(/[\\/]/).some((component) =>
    component === ".build" || component === ".git" || component === ".swiftpm"
  );
}

/**
 * Runs a short synchronous command and decodes its JSON output.
 *
 * This is used only during setup where later work depends immediately on the
 * result, such as package metadata and simulator discovery.
 *
 * @param {string} command Executable name.
 * @param {string[]} args Command arguments.
 * @returns {object} Parsed JSON output.
 */
function runJson(command, args) {
  try {
    const stdout = execFileSync(command, args, { encoding: "utf8", maxBuffer: 20 * 1024 * 1024 });
    return JSON.parse(stdout);
  } catch (error) {
    throw new Error(`${command} ${args.join(" ")} failed: ${error.stderr || error.stdout || error.message}`);
  }
}

/**
 * Runs a command asynchronously, echoes relevant output, and enforces success.
 *
 * @param {string} command Executable name.
 * @param {string[]} args Command arguments.
 * @param {object} [options] Timeout, logging, output-file, and failure-handling options.
 * @returns {Promise<{code: number | null, stdout: string, stderr: string}>} Process result.
 */
async function run(command, args, options = {}) {
  if (options.outputFile) {
    return runWithOutputFile(command, args, options);
  }

  try {
    const result = await execFileAsync(command, args, {
      cwd: options.cwd,
      encoding: "utf8",
      timeout: options.timeoutMs ?? 30_000,
      maxBuffer: options.maxBuffer ?? 20 * 1024 * 1024,
    });
    if (options.logOutput && result.stdout.trim()) log(result.stdout.trim());
    if (options.logOutput && result.stderr.trim()) log(result.stderr.trim());
    return { code: 0, ...result };
  } catch (error) {
    const stdout = error.stdout ?? "";
    const stderr = error.stderr ?? "";
    if (options.logOutput && stdout.trim()) log(stdout.trim());
    if (options.logOutput && stderr.trim()) log(stderr.trim());
    if (options.allowFailure) {
      return { code: error.code ?? null, stdout, stderr };
    }
    throw new Error(`${command} ${args.join(" ")} failed: ${stderr || stdout || error.message}`);
  }
}

/**
 * Runs a command with stdout and stderr connected directly to a diagnostic file.
 *
 * @param {string} command Executable name.
 * @param {string[]} args Command arguments.
 * @param {object} options Timeout, output-file, and failure-handling options.
 * @returns {Promise<{code: number | null, stdout: string, stderr: string}>} Process result.
 */
async function runWithOutputFile(command, args, options) {
  const outputFile = options.outputFile;
  await mkdir(dirname(outputFile), { recursive: true });
  const outputHandle = await open(outputFile, "w");
  let result;

  try {
    result = await new Promise((resolveResult, rejectResult) => {
      const child = spawn(command, args, {
        cwd: options.cwd,
        stdio: ["ignore", outputHandle.fd, outputHandle.fd],
        timeout: options.timeoutMs ?? 30_000,
      });
      child.once("error", rejectResult);
      child.once("close", (code, signal) => resolveResult({ code, signal }));
    });
  } catch (error) {
    if (options.allowFailure) {
      return { code: error.code ?? null, stdout: "", stderr: "" };
    }
    throw new Error(`${command} ${args.join(" ")} failed; full output: ${outputFile}: ${error.message}`);
  } finally {
    await outputHandle.close();
  }

  if (result.code === 0) {
    return { code: 0, stdout: "", stderr: "" };
  }
  if (options.allowFailure) {
    return { code: result.code, stdout: "", stderr: "" };
  }

  const reason = result.signal ? `terminated by ${result.signal}` : `exited with code ${result.code}`;
  throw new Error(`${command} ${args.join(" ")} failed (${reason}); full output: ${outputFile}`);
}

/**
 * Emits a timestamped launcher progress line.
 *
 * @param {string} message Message to show in the terminal.
 * @returns {void}
 */
function log(message) {
  const line = `[${new Date().toLocaleTimeString()}] ${message}`;
  console.log(line);
}

/**
 * Extracts the PID printed by `simctl launch` for the generated host bundle.
 *
 * @param {{stdout: string, stderr: string}} result Launch command output.
 * @returns {number | null} Running host PID, when reported by Simulator.
 */
function launchPid(result) {
  const output = `${result.stdout}\n${result.stderr}`;
  const escapedBundleId = BUNDLE_ID.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = output.match(new RegExp(`${escapedBundleId}:\\s*(\\d+)`));
  return match ? Number(match[1]) : null;
}

/**
 * Resolves the generated host's simulator data container for reload handoff.
 *
 * Reload manifests and host status files are exchanged through this container's
 * documents directory because both Node and the running app can access it.
 *
 * @param {string} udid Simulator identifier.
 * @returns {Promise<string>} Absolute path to the app data container.
 */
async function appDataContainer(udid) {
  const result = await run(
    "xcrun",
    ["simctl", "get_app_container", udid, BUNDLE_ID, "data"],
    { timeoutMs: 15_000 },
  );
  return result.stdout.trim();
}

/**
 * Reads the latest status emitted by the running Swift host app.
 *
 * @param {object} state Mutable launcher state with a data-container path.
 * @returns {object | null} Host status, or `null` before it has been written.
 */
function readHostStatus(state) {
  if (!state.dataContainer) return null;
  const statusPath = join(state.dataContainer, "Documents", "swiftui-preview-browser", "status.json");
  try {
    return JSON.parse(readFileSync(statusPath, "utf8"));
  } catch {
    return null;
  }
}

/**
 * Waits for the initially launched app to publish its running state.
 *
 * @param {object} state Mutable launcher state including the expected PID.
 * @returns {Promise<object>} Initial host status.
 */
async function waitForHostReady(state) {
  return waitForHostStatus(state, {
    attempts: 50,
    isReady: (status) => status.pid === state.appPid && status.phase === "running",
    timeoutMessage:
      "Preview host launched but did not render. The selected preview may not be self-contained; inspect Simulator logs.",
  });
}

/**
 * Waits until the host reports that a specific reload manifest was applied.
 *
 * @param {object} state Mutable launcher state.
 * @param {string} token Unique token written into the reload manifest.
 * @returns {Promise<object>} Updated host status.
 */
async function waitForHostReload(state, token) {
  return waitForHostStatus(state, {
    attempts: 80,
    isReady: (status) => status.lastToken === token && status.phase === "reloaded",
    statusError: (status) =>
      status.lastToken === token && status.phase === "error"
        ? new Error(`Hot reload failed inside host: ${status.lastError ?? "unknown error"}`)
        : null,
    timeoutMessage: "Timed out waiting for the running host app to apply the hot reload",
  });
}

/**
 * Polls host status until a caller-specific terminal state is reached.
 *
 * @param {object} state Mutable launcher state.
 * @param {{attempts: number, isReady: (status: object) => boolean, statusError?: (status: object) => Error | null, timeoutMessage: string}} options Polling conditions.
 * @returns {Promise<object>} Matching host status.
 */
async function waitForHostStatus(state, options) {
  for (let attempt = 0; attempt < options.attempts; attempt += 1) {
    await delay(100);
    const status = readHostStatus(state);
    if (!status) continue;
    const statusError = options.statusError?.(status);
    if (statusError) throw statusError;
    if (options.isReady(status)) return status;
  }
  throw new Error(options.timeoutMessage);
}

/**
 * Pauses polling while waiting for simulator state changes.
 *
 * @param {number} ms Milliseconds to wait.
 * @returns {Promise<void>}
 */
function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv.slice(2)).catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
