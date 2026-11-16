import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { access, lstat, mkdir, readFile, readdir, realpath, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
async function owningRuntime(explicit) {
  if (explicit) { assert(path.isAbsolute(explicit), 'RUNTIME_ROOT_MUST_BE_ABSOLUTE'); return explicit; }
  let directory = fileURLToPath(new URL('../', import.meta.url));
  for (;;) {
    for (const name of ['openmotion-install.json', 'scope.json']) {
      try { const scope = JSON.parse(await readFile(path.join(directory, name), 'utf8')); assert(path.isAbsolute(scope.runtimeRoot), 'INVALID_RUNTIME_ROOT'); return scope.runtimeRoot; }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
    try { await access(path.join(directory, 'scripts/zip.mjs')); return directory; }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = path.dirname(directory); assert(parent !== directory, 'OPENMOTION_RUNTIME_NOT_FOUND'); directory = parent;
  }
}

const sha256 = data => createHash('sha256').update(data).digest('hex');
// Mirrors WorkspaceStore: node_modules/renders/output plus tool caches are not project source.
const nonSourceDirectories = new Set(['node_modules', 'renders', 'output', '.git', '.cache', '.thumbnails', '.history', '.artifacts']);
// WorkspaceStore also omits dist trees from the revision, but projects load them directly
// (e.g. vendor/gsap-3.14.2/dist/gsap.min.js), so they ship as non-revision content.
const nonRevisionDirectories = new Set(['dist']);
// The native Studio manifests are the only revision-bearing .hyperframes entries; history-id is editor metadata.
const nativeManifests = new Set(['.hyperframes/studio-manual-edits.json', '.hyperframes/studio-motion.json']);
const editorMetadata = new Set(['.hyperframes/history-id']);
const isNonRevision = relative => relative.split('/').some(part => nonRevisionDirectories.has(part));
const excluded = relative => {
  const parts = relative.split('/');
  if (parts.some(part => nonSourceDirectories.has(part))) return true;
  // Mirrors WorkspaceStore.walk: dotted entries are caches, except the .hyperframes entries handled below.
  if (parts[0] !== '.hyperframes') return parts.some(part => part.startsWith('.'));
  // The .hyperframes directory itself stays traversable; only its identity and manifests are packaged.
  if (relative === '.hyperframes') return false;
  return !nativeManifests.has(relative) && !editorMetadata.has(relative);
};
function safeRelative(value) {
  assert(typeof value === 'string' && value && !value.includes('\\') && !path.posix.isAbsolute(value)
    && !value.split('/').some(part => part === '..' || part === '' || part === '.'), 'UNSAFE_PROJECT_PATH');
  return value;
}
async function scan(directory, relative = '', result = new Map()) {
  for (const entry of await readdir(path.join(directory, relative), { withFileTypes: true })) {
    const name = relative ? relative + '/' + entry.name : entry.name;
    if (excluded(name)) continue;
    const file = path.join(directory, name), stat = await lstat(file);
    assert(!stat.isSymbolicLink(), 'PROJECT_SYMLINK: ' + name);
    if (stat.isDirectory()) await scan(directory, name, result);
    else { assert(stat.isFile(), 'UNSUPPORTED_PROJECT_FILE: ' + name); result.set(name, await readFile(file)); }
  }
  return result;
}
function validateInventory(detail, files) {
  assert(/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/.test(detail.projectId), 'INVALID_PROJECT_ID');
  assert(/^[a-f0-9]{64}$/.test(detail.revision) && typeof detail.currentVersionId === 'string' && detail.currentVersionId, 'MISSING_VERSION_IDENTITY');
  assert(detail.project?.entry === 'index.html' && Array.isArray(detail.project.files) && detail.project.files.length, 'MISSING_PROJECT_INVENTORY');
  const seen = new Set();
  for (const item of detail.project.files) {
    const name = safeRelative(item.path); assert(!seen.has(name), 'DUPLICATE_PROJECT_PATH'); seen.add(name);
    assert(/^[a-f0-9]{64}$/.test(item.hash), 'INVALID_FILE_HASH: ' + name);
    assert(files.has(name) && sha256(files.get(name)) === item.hash, 'SOURCE_DRIFT: ' + name);
  }
  // The pinned inventory is the complete revision-bearing file set; a file the workspace added after the
  // project read changes the revision, so packaging it under the old revision would misreport the source.
  for (const name of files.keys()) assert(seen.has(name) || editorMetadata.has(name) || isNonRevision(name), 'SOURCE_DRIFT: unpinned source file ' + name);
  assert(files.has('index.html'), 'MISSING_HTML_ENTRY');
}
function checkDependencies(files) {
  for (const [name, bytes] of files) {
    if (!/\.(?:html|css)$/.test(name)) continue;
    const text = bytes.toString('utf8'), refs = [];
    if (name.endsWith('.html')) {
      for (const tag of text.matchAll(/<(script|img|video|audio|source|iframe|link)\b[^>]*>/gi)) {
        if (tag[1].toLowerCase() === 'link' && !/rel\s*=\s*["']stylesheet["']/i.test(tag[0])) continue;
        refs.push(...[...tag[0].matchAll(/\s(?:src|href)\s*=\s*["']([^"']+)["']/gi)].map(match => match[1]));
      }
      refs.push(...[...text.matchAll(/\sdata-composition-src\s*=\s*["']([^"']+)["']/gi)].map(match => match[1]));
    }
    refs.push(...[...text.matchAll(/url\(\s*["']?([^\s"')]+)["']?\s*\)/gi)].map(match => match[1]));
    // Quoted imports are CSS dependencies; commented examples and script strings are not.
    const styles = name.endsWith('.css') ? [text] : [...text.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style\s*>/gi)].map(match => match[1]);
    for (const css of styles) {
      const uncommented = css.replace(/\/\*[\s\S]*?\*\//g, '');
      refs.push(...[...uncommented.matchAll(/@import\s+(["'])([^"']+)\1/gi)].map(match => match[2]));
    }
    for (const ref of refs) {
      if (/^(?:data:|blob:|#)/i.test(ref)) continue;
      assert(!/^(?:[a-z][\w+.-]*:|\/\/)/i.test(ref), 'REMOTE_DEPENDENCY: ' + name + ' -> ' + ref);
      const relative = path.posix.normalize(path.posix.join(path.posix.dirname(name), decodeURIComponent(ref.split(/[?#]/)[0])));
      assert(!ref.startsWith('/') && relative !== '..' && !relative.startsWith('../') && files.has(relative), 'MISSING_DEPENDENCY: ' + name + ' -> ' + ref);
    }
  }
}
async function resolvedDestination(destination) {
  let ancestor = destination; const suffix = [];
  for (;;) {
    try { return path.join(await realpath(ancestor), ...suffix.reverse()); }
    catch (error) { if (error.code !== 'ENOENT') throw error; const parent = path.dirname(ancestor); assert(parent !== ancestor, 'INVALID_OUTPUT_PARENT'); suffix.push(path.basename(ancestor)); ancestor = parent; }
  }
}
export async function packageProject(detail, output, options = {}) {
  const runtimeRoot = await owningRuntime(options.runtimeRoot);
  const { zip } = await import(pathToFileURL(path.join(runtimeRoot, 'scripts/zip.mjs')).href);
  assert(path.isAbsolute(output), 'OUTPUT_MUST_BE_ABSOLUTE');
  const directory = detail.project?.directory;
  assert(typeof directory === 'string' && path.isAbsolute(directory) && !(await lstat(directory)).isSymbolicLink(), 'INVALID_PROJECT_DIRECTORY');
  const source = await realpath(directory), target = await resolvedDestination(path.resolve(output));
  assert(target !== source && !target.startsWith(source + path.sep), 'OUTPUT_INSIDE_PROJECT');
  const files = await scan(source); validateInventory(detail, files); checkDependencies(files);
  await mkdir(path.dirname(target), { recursive: true });
  await mkdir(target); // An existing destination is never overwritten.
  try {
    const projectDirectory = path.join(target, 'HTML');
    const entries = [];
    for (const [name, data] of [...files].sort(([a], [b]) => a.localeCompare(b))) {
      const destination = path.join(projectDirectory, name);
      await mkdir(path.dirname(destination), { recursive: true }); await writeFile(destination, data, { flag: 'wx' });
      entries.push({ name: 'HTML/' + name, data });
    }
    const after = await scan(source); validateInventory(detail, after);
    assert.deepEqual([...after].map(([name, bytes]) => [name, sha256(bytes)]).sort(), [...files].map(([name, bytes]) => [name, sha256(bytes)]).sort(), 'SOURCE_DRIFT_DURING_PACKAGE');
    const archive = path.join(target, 'HTML.zip'), archiveBytes = zip(entries);
    await writeFile(archive, archiveBytes, { flag: 'wx' });
    const receipt = { projectId: detail.projectId, revision: detail.revision, versionId: detail.currentVersionId,
      entry: path.join(projectDirectory, 'index.html'), archive, archiveSHA256: sha256(archiveBytes),
      files: entries.map(entry => ({ path: entry.name, bytes: entry.data.length, sha256: sha256(entry.data) })),
      packagedAt: new Date().toISOString(), sourceUnchanged: true, dependencies: 'local' };
    await writeFile(path.join(target, 'delivery.json'), JSON.stringify(receipt, null, 2) + '\n', { flag: 'wx' });
    return receipt;
  } catch (error) { await rm(target, { recursive: true, force: true }); throw error; }
}
async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--help')) { console.log('delivery.mjs package --project-json /absolute/detail.json --output /new/absolute/directory [--runtime-root /absolute/runtime]'); return; }
  assert((args.length === 5 || args.length === 7 && args[5] === '--runtime-root') && args[0] === 'package' && args[1] === '--project-json' && args[3] === '--output' && path.isAbsolute(args[2]), 'Use --help for arguments.');
  const input = JSON.parse(await readFile(args[2], 'utf8'));
  const receipt = await packageProject(input.structuredContent ?? input, args[4], { runtimeRoot: args[6] });
  console.log(JSON.stringify({ projectId: receipt.projectId, versionId: receipt.versionId, entry: receipt.entry, archive: receipt.archive, files: receipt.files.length, archiveSHA256: receipt.archiveSHA256 }));
}
if (process.argv[1] && import.meta.url === pathToFileURL(await realpath(process.argv[1])).href) main().catch(error => { console.error(error.message); process.exitCode = 1; });
