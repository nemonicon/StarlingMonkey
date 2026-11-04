// Static dependency/demand audit. Never bundles a package or starts a component.
import assert from 'node:assert/strict';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version, 'v22.14.0');
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
const toolchain = resolve(process.env.NODE_COMPAT_TOOLCHAIN ?? '/tmp/starling-node-compat/native-toolchain-lock');
const packages = join(toolchain, 'node_modules'), readable = join(packages, 'readable-stream/lib');
const stdStream = join(packages, '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream');
const hash = value => createHash('sha256').update(value).digest('hex');
async function jsFiles(root) {
  const paths = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) paths.push(...await jsFiles(path));
    else if (entry.name.endsWith('.js')) paths.push(path);
  }
  return paths.sort();
}
const readableFiles = await jsFiles(readable), stdFiles = await jsFiles(stdStream);
const paths = [...readableFiles, ...stdFiles,
  ...['@bytecodealliance/jco/dist/node-builtins/stream.js', 'unenv/dist/runtime/node/stream.mjs',
    'unenv/dist/runtime/node/stream/promises.mjs', 'unenv/dist/runtime/node/stream/consumers.mjs',
    'unenv/dist/runtime/node/internal/process/nexttick.mjs', 'process/browser.js'].map(path => join(packages, path)),
  ...['runtime/engine.cpp', 'runtime/event_loop.cpp', 'include/extension-api.h', 'include/builtin.h',
    'host-apis/wasi-0.2.0/host_api.cpp', 'builtins/web/queue-microtask.cpp', 'builtins/web/timers.cpp',
    'builtins/web/blob.cpp', 'builtins/web/abort/abort-signal.cpp', 'builtins/web/event/event-target.cpp',
    'builtins/node-compat/entropy-policy.cpp', 'builtins/node-compat/events.mjs',
    'builtins/node-compat/export-manifest.node-v22.14.0.json', 'builtins/node-compat/export-manifest.events.node-v22.14.0.json',
    'builtins/node-compat/export-manifest.string-decoder.node-v22.14.0.json', 'tests/node-compat/async-context/architecture.md'].map(path => join(repository, path))];
const sourceFiles = [], dependencyEdges = [], demand = [];
for (const path of paths) {
  const text = await readFile(path, 'utf8'), origin = path.startsWith(packages+'/') ? 'toolchain' : 'repository';
  const name = relative(origin === 'toolchain' ? packages : repository, path);
  sourceFiles.push({ origin, path: name, sha256: hash(text), bytes: Buffer.byteLength(text) });
  if (path.startsWith(readable+'/') || path.startsWith(stdStream+'/')) {
    for (const match of text.matchAll(/require\(['"]([^'"]+)['"]\)|\bfrom\s+['"]([^'"]+)['"]/g))
      dependencyEdges.push({ from: name, specifier: match[1] ?? match[2], line: text.slice(0, match.index).split('\n').length });
    text.split('\n').forEach((line, index) => {
      if (/Buffer\.allocUnsafe|process\.nextTick|require\('events'\)\.addAbortListener|StringDecoder|setTimeout|queueMicrotask/.test(line))
        demand.push({ path: name, line: index+1, source: line.trim() });
    });
  }
}
const enginePath = '/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm';
const receiptBytes = await readFile(enginePath+'.build.json'), receipt = JSON.parse(receiptBytes);
const embeddingPath = receipt.actualEmbeddingCompileCommands.find(line => line.includes('embedding.cpp')).split(' -c ').at(-1);
const embedding = await readFile(embeddingPath);
assert.equal(hash(embedding), receipt.componentizeSourceManifest.find(item => item.path === 'embedding/embedding.cpp').sha256);
const versions = {};
for (const name of ['@bytecodealliance/jco', '@bytecodealliance/jco-std', 'readable-stream', 'events', 'buffer', 'process', 'string_decoder', 'unenv'])
  versions[name] = JSON.parse(await readFile(join(packages, name, 'package.json'))).version;
const readableNames = new Set(readableFiles.map(path => relative(packages, path))), reachable = new Set();
function visit(name) {
  if (reachable.has(name)) return; reachable.add(name);
  for (const edge of dependencyEdges.filter(edge => edge.from === name && edge.specifier.startsWith('.'))) {
    const base = resolve(packages, dirname(name), edge.specifier);
    const target = [base, base+'.js', join(base, 'index.js')].map(path => relative(packages, path)).find(path => readableNames.has(path));
    assert(target, 'Unresolved relative readable-stream edge '+name+' -> '+edge.specifier); visit(target);
  }
}
visit('readable-stream/lib/stream.js');
const report = { schema: 1, node: process.version, toolchain, versions, sourceFiles, dependencyEdges, demand,
  externalEmbedding: { path: embeddingPath, sha256: hash(embedding), revision: receipt.componentizeJsRevision,
    receiptSha256: hash(receiptBytes), engineSha256: receipt.engineSha256,
    contract: 'call() enters permanent deployed entropy policy, increments interest, invokes JS, attaches AddPromiseReactions, drains until result settles; this is not a fresh request owner or Node callback boundary implementation' },
  directNonrelativeReadableDependencies: [...new Set(dependencyEdges.filter(edge => edge.from.startsWith('readable-stream/') && !edge.specifier.startsWith('.')).map(edge => edge.specifier))].sort(),
  readableCoreGraph: { entry: 'readable-stream/lib/stream.js', reachableFiles: [...reachable].sort(),
    externalDependencies: [...new Set(dependencyEdges.filter(edge => reachable.has(edge.from) && !edge.specifier.startsWith('.')).map(edge => edge.specifier))].sort(),
    note: 'All-tree edges also include package main/browser wrappers. The direct portable core avoids their require(stream) and READABLE_STREAM env branch.' },
  requiredDependencyWork: [
    { api: 'Buffer.allocUnsafe', status: 'deferred in current core', callers: ['buffer_list.js::concat', 'buffer_list.js::_getBuffer'], decision: 'Versioned bounded allocation policy and differential tests before byte-mode aggregation; no silent substitution' },
    { api: 'events.addAbortListener', status: 'truthy deferred export in current Events', callers: ['ours/util.js addAbortListener selection', 'pipeline/end-of-stream/add-abort-signal'], decision: 'Implement accepted abort listener semantics or explicitly defer affected stream APIs; existing fallback will not run' },
    { api: 'process.nextTick', status: 'no production Node queue', callers: ['readable/writable/destroy/end-of-stream/pipeline/from/duplexify'], decision: 'Boundary-sensitive native guest scheduler with ALS resource capture and error handling; queueMicrotask shim has measured ordering mismatches' },
    { api: 'StringDecoder', status: 'optional bounded UTF8/hex only', callers: ['ReadableState(options.encoding)', 'Readable.setEncoding'], decision: 'Reuse actual selected constructor for supported encodings; preserve explicit errors for deferred encodings' },
  ],
  primaryReferences: [
    'https://github.com/nodejs/node/blob/v22.14.0/lib/stream.js',
    'https://github.com/nodejs/node/blob/v22.14.0/lib/stream/consumers.js',
    'https://github.com/nodejs/node/blob/v22.14.0/lib/internal/process/task_queues.js',
    'https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-stream-consumers.js',
    'https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-stream-pipeline.js',
  ],
  scope: 'Source/hash/dependency evidence and exact existing embedding receipt. No production stream module, bundle validation, real component execution, or compatibility/performance claim.' };
await writeFile(new URL('source-audit.json', import.meta.url), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ sourceFiles: sourceFiles.length, readableFiles: readableFiles.length, stdStreamFiles: stdFiles.length,
  dependencyEdges: dependencyEdges.length, demandSites: demand.length, dependencies: report.directNonrelativeReadableDependencies }));
