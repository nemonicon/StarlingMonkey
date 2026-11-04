// Host-side artifact preservation only. No guest or toolchain imports.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, readFile, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');

function below(output, path) {
  const root = resolve(output), target = resolve(path), name = relative(root, target);
  assert(name && name !== '..' && !name.startsWith('..' + sep) && !isAbsolute(name), 'Output must be below its own directory');
  return { root, target, name };
}

async function ordinaryParent(output, path) {
  const { root, target } = below(output, path);
  let cursor = dirname(target);
  for (;;) {
    const stat = await lstat(cursor);
    assert(stat.isDirectory() && !stat.isSymbolicLink(), cursor);
    if (cursor === root) return;
    const parent = dirname(cursor);
    assert.notEqual(parent, cursor, 'Output root must be reachable');
    cursor = parent;
  }
}

async function ordinaryFile(output, path) {
  const { root, target, name } = below(output, path);
  const rootStat = await lstat(root);
  assert(rootStat.isDirectory() && !rootStat.isSymbolicLink(), root);
  let cursor = target;
  while (cursor !== root) {
    const stat = await lstat(cursor);
    assert(!stat.isSymbolicLink(), cursor);
    if (cursor === target) assert(stat.isFile(), cursor);
    const parent = dirname(cursor);
    assert.notEqual(parent, cursor, 'Output root must be reachable');
    cursor = parent;
  }
  const data = await readFile(target);
  return { path: name, sha256: hash(data), bytes: data.length };
}

export function trackedWriter(output) {
  const paths = new Set();
  const written = new Map();
  async function write(path, data, options) {
    const { target } = below(output, path);
    assert(options?.flag === 'wx', 'Tracked outputs require exclusive creation');
    await ordinaryParent(output, target);
    await writeFile(target, data, options);
    paths.add(target);
    const bytes = typeof data === 'string' ? Buffer.from(data, options.encoding ?? 'utf8') : Buffer.from(data);
    written.set(target, { sha256: hash(bytes), bytes: bytes.length });
  }
  // Jco may emit a shared interface declaration for multiple components.
  // Only exact declarations created by this writer may be reused. All other
  // outputs retain exclusive creation; an old directory is never repaired.
  async function writeGenerated(path, data, options) {
    const { target, name } = below(output, path);
    assert(options?.flag === 'wx', 'Generated outputs require exclusive creation');
    if (!paths.has(target)) return write(target, data, options);
    assert(/^interfaces\/[A-Za-z0-9][A-Za-z0-9._-]*\.d\.ts$/.test(name),
      'Only already-tracked interface declarations may repeat');
    await ordinaryParent(output, target);
    const previous = await ordinaryFile(output, target);
    const bytes = typeof data === 'string' ? Buffer.from(data, options.encoding ?? 'utf8') : Buffer.from(data);
    const original = written.get(target);
    assert(original && original.sha256 === previous.sha256 && original.bytes === previous.bytes,
      'Tracked declaration changed after creation');
    assert.equal(hash(bytes), original.sha256, 'Repeated declaration differs');
    assert.equal(bytes.length, original.bytes, 'Repeated declaration length differs');
    assert((await readFile(target)).equals(bytes), 'Repeated declaration bytes differ');
  }
  return Object.freeze({ write, writeGenerated, paths });
}

// The caller must finish its final admission.recheck() BEFORE calling this.
// A success-looking results file alone is never a completion gate. If writing,
// hashing, or publication fails, preserve partial outputs and fail the process.
export async function publishCompletion({ output, report, paths }) {
  assert(paths instanceof Set && report && typeof report === 'object');
  const resultsPath = join(resolve(output), 'results.json');
  const completionPath = join(resolve(output), 'completion.json');
  await ordinaryParent(output, resultsPath);
  for (const path of paths) {
    const { target } = below(output, path);
    assert(target !== resultsPath && target !== completionPath, 'Results and completion are exclusively published here');
  }
  // Refuse an old completion before creating a fresh report. No overwrite or
  // automatic repair of a previous/partial output tree is performed.
  try {
    await lstat(completionPath);
    assert.fail('Completion already exists');
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const files = [];
  for (const path of [...paths].sort()) files.push(await ordinaryFile(output, path));
  const resultsBytes = Buffer.from(JSON.stringify(report, null, 2) + '\n');
  await writeFile(resultsPath, resultsBytes, { flag: 'wx' });
  const results = await ordinaryFile(output, resultsPath);
  assert.equal(results.sha256, hash(resultsBytes));
  files.push(results);
  files.sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  const completion = {
    schemaVersion: 1,
    state: 'CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO',
    variant: report.variant,
    reportStatus: report.status,
    engineSha256: report.engineSha256,
    results,
    files,
    componentFiles: files.filter(row => row.path.endsWith('.component.wasm')).map(row => row.path),
    generatedWasmFiles: files.filter(row => row.path.endsWith('.wasm') && !row.path.endsWith('.component.wasm')).map(row => row.path),
    generatedJavaScriptFiles: files.filter(row => row.path.endsWith('.js')).map(row => row.path),
    finalAdmissionRecheckCompletedBeforeReportPublication: true,
    requiresIndependentTerminalExitCodeZero: true,
    terminalExitCodeObservedByThisHelper: null,
    runtimeAcceptanceClaim: false,
    scope: 'Hashes the actual files written by this run. The external collector must rehash them and require raw terminal exit 0. No self-hash, node_modules traversal, or crash/concurrent-writer guarantee.'
  };
  await writeFile(completionPath, JSON.stringify(completion, null, 2) + '\n', { flag: 'wx' });
  return completion;
}
