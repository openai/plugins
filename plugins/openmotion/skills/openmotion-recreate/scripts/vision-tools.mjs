import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';

const runScript = `
import runpy
import sys
from pathlib import Path

script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).resolve().parent))
runpy.run_path(script, run_name="__main__")
`;

async function runtimeRoot() {
  let directory = fileURLToPath(new URL('../', import.meta.url));
  for (;;) {
    for (const name of ['openmotion-install.json', 'scope.json']) {
      try {
        const scope = JSON.parse(await readFile(path.join(directory, name), 'utf8'));
        assert(path.isAbsolute(scope.runtimeRoot), 'Installation runtimeRoot must be absolute');
        return scope.runtimeRoot;
      } catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
    try { await access(path.join(directory, 'scripts/vision-runtime.mjs')); return directory; }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = path.dirname(directory);
    assert(parent !== directory, 'Cannot locate OpenMotion runtime. Repair this Skill installation.');
    directory = parent;
  }
}

try {
  const [command, ...args] = process.argv.slice(2);
  assert(['register', 'measure', 'python', 'prepare'].includes(command), 'Usage: node vision-tools.mjs register|measure|python|prepare [arguments]');
  const root = await runtimeRoot();
  const { ensureVisionRuntime, visionEnvironment } = await import(pathToFileURL(path.join(root, 'scripts/vision-runtime.mjs')).href);
  const config = await ensureVisionRuntime(root);
  if (command === 'prepare') console.log(JSON.stringify({ python: config.python, versions: config.runtime.vision }));
  else {
    const script = command === 'python' ? [] : [path.join(root, 'skills/openmotion-recreate/scripts', command === 'register' ? 'register_motion.py' : 'measure_motion.py')];
    const pythonArgs = [...script, ...args];
    // Isolated Python omits the script directory. Restore only that explicit
    // directory so sibling imports work without adopting host site-packages.
    const invocation = pythonArgs[0] && !pythonArgs[0].startsWith('-') ? ['-c', runScript, ...pythonArgs] : pythonArgs;
    const child = spawn(config.python, ['-I', ...invocation], { env: visionEnvironment(), stdio: 'inherit', windowsHide: true });
    for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
    child.once('error', error => { console.error(error.message); process.exitCode = 1; });
    child.once('exit', (code, signal) => { process.exitCode = code ?? (signal === 'SIGINT' ? 130 : 1); });
  }
} catch (error) {
  console.error('VISION_RUNTIME_ERROR: ' + error.message + '\nRun this entry with prepare to retry. Host permissions and network policy still apply.');
  process.exitCode = 1;
}
