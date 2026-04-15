import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const IGNORED_DIRS = new Set([
  ".git",
  ".hg",
  ".svn",
  "node_modules",
  "dist",
  "build",
  ".next",
  ".turbo",
  ".cache",
  ".tmp",
  ".venv",
  "venv",
  "__pycache__",
  ".pytest_cache",
  "coverage",
]);

const TEXT_EXTENSIONS = new Set([
  ".cjs",
  ".css",
  ".csv",
  ".html",
  ".js",
  ".json",
  ".jsonc",
  ".jsx",
  ".md",
  ".mjs",
  ".py",
  ".sh",
  ".svg",
  ".toml",
  ".ts",
  ".tsx",
  ".txt",
  ".xml",
  ".yaml",
  ".yml",
]);

export async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

export async function isDirectory(targetPath) {
  try {
    const stats = await fs.stat(targetPath);
    return stats.isDirectory();
  } catch {
    return false;
  }
}

export async function isFile(targetPath) {
  try {
    const stats = await fs.stat(targetPath);
    return stats.isFile();
  } catch {
    return false;
  }
}

export async function readText(targetPath) {
  return fs.readFile(targetPath, "utf8");
}

export async function readJson(targetPath) {
  return JSON.parse(await readText(targetPath));
}

export async function writeText(targetPath, content) {
  await fs.mkdir(path.dirname(targetPath), { recursive: true });
  await fs.writeFile(targetPath, content, "utf8");
}

export async function writeJson(targetPath, payload) {
  await writeText(targetPath, `${JSON.stringify(payload, null, 2)}\n`);
}

export function isProbablyTextFile(filePath) {
  return TEXT_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

export function toPosixPath(filePath) {
  return filePath.split(path.sep).join("/");
}

export function relativePath(fromPath, toPath) {
  const value = path.relative(fromPath, toPath) || ".";
  return toPosixPath(value);
}

export function formatCommandPath(targetPath, options = {}) {
  const absoluteTargetPath = path.resolve(targetPath);
  const cwd = path.resolve(options.cwd || process.cwd());
  const homeDir = path.resolve(options.homeDir || os.homedir());

  if (absoluteTargetPath === homeDir) {
    return "~";
  }

  const relativeToHome = path.relative(homeDir, absoluteTargetPath);
  if (relativeToHome && !relativeToHome.startsWith("..") && !path.isAbsolute(relativeToHome)) {
    return `~/${toPosixPath(relativeToHome)}`;
  }

  const relativeToCwd = path.relative(cwd, absoluteTargetPath) || ".";
  if (!relativeToCwd.startsWith("..") && !path.isAbsolute(relativeToCwd)) {
    return toPosixPath(relativeToCwd);
  }

  return toPosixPath(absoluteTargetPath);
}

export async function walkFiles(rootPath, options = {}) {
  const files = [];
  const {
    excludeDirs = [],
    skipTopLevel = ["fixtures", "__fixtures__"],
  } = options;
  const excluded = new Set([...IGNORED_DIRS, ...excludeDirs]);

  async function visit(currentPath, depth = 0) {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        if (excluded.has(entry.name)) {
          continue;
        }
        if (depth === 0 && skipTopLevel.includes(entry.name)) {
          continue;
        }
        await visit(entryPath, depth + 1);
        continue;
      }
      if (entry.isFile()) {
        files.push(entryPath);
      }
    }
  }

  await visit(rootPath);
  return files.sort();
}

export async function listImmediateDirectories(rootPath) {
  const entries = await fs.readdir(rootPath, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(rootPath, entry.name))
    .sort();
}
