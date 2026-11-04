// Execute after the root benchmark window. Validates bundled guest semantics;
// native builtin registration/aliases remain a separate integration gate.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
assert.equal(process.version, 'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE && process.env.NODE_COMPAT_WASMTIME);
const here = dirname(fileURLToPath(import.meta.url)), repository = resolve(here, '../../..');
// Wasmtime CLI prints a Rust Debug string. Normalize only actual escape tokens;
// a literal backslash-u sequence inside the returned JSON must remain literal.
function decodeCliString(source) {
  let normalized = '';
  for (let index = 0; index < source.length; index++) {
    const char = source[index];
    if (char !== '\\') { normalized += char; continue; }
    const next = source[++index];
    if (next === 'u' && source[index + 1] === '{') {
      const end = source.indexOf('}', index + 2), digits = source.slice(index + 2, end);
      assert(end > index && /^[0-9a-fA-F]+$/.test(digits));
      normalized += JSON.stringify(String.fromCodePoint(parseInt(digits, 16))).slice(1, -1);
      index = end;
    } else if (next === "'") normalized += "'";
    else normalized += next === '0' ? '\\u0000' : '\\' + next;
  }
  try { return JSON.parse(normalized); }
  catch (error) { throw new Error('Wasmtime CLI string decoding: '+error.message); }
}
assert.equal(decodeCliString('"\\u{feff}"'), '\uFEFF');
assert.equal(decodeCliString('"\\\\u{feff}"'), '\\u{feff}');
assert.equal(decodeCliString("\"\\'\""), "'");
const engine = resolve(process.env.NODE_COMPAT_ENGINE), sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
const metadata = JSON.parse(await readFile(engine + '.build.json'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(engine)), metadata.engineSha256); assert.equal(metadata.entropyPolicy, 'off');
assert.equal(metadata.debuggerEnabled, false); assert.equal(metadata.gcStress, false);
for (const input of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, input.path))), input.sha256, input.path);
const output = resolve(process.env.NODE_COMPAT_QUERYSTRING_OUTPUT ?? '/tmp/starling-node-compat/foundation-querystring-prototype');
const toolchain = await loadToolchain(), selected = await loadComponentizer(toolchain);
const bundle = await bundleProfile({ ...toolchain, input: join(here, 'component.mjs') }); assert.deepEqual(bundle.imports, ['node:buffer']);
const adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(adapter)), '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const options = { engine, preview2Adapter: adapter,
  witWorld: 'package test:querystring-prototype; world test { export run: func() -> string; }', worldName: 'test',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
const { component, interfaceAudit } = await selected.componentize(bundle.code, options);
assert.deepEqual(interfaceAudit.emittedImports, []);
await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); } catch (error) { if (error.code !== 'EEXIST') throw error; }
const { transpile, componentWit } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const emittedWit = await componentWit(component);
assert.equal(emittedWit.replace(/\s+/g, ' ').trim(), 'package root:component; world root { export run: func() -> string; }');
const { files } = await transpile(component, { name: 'querystring_prototype' });
for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
const path = join(output, 'querystring-prototype.component.wasm'); await writeFile(path, component); await writeFile(join(output, 'prototype.bundle.mjs'), bundle.code);
const oracle = JSON.parse(await readFile(join(here, 'node-results.json')));
for (const [name, digest] of Object.entries(oracle.sources)) assert.equal(hash(await readFile(join(here, name))), digest, name);
function check(observed, calls) {
  assert.equal(observed.failure, undefined, JSON.stringify(observed.failure));
  assert.equal(observed.calls, calls); assert.equal(observed.namespaceIdentity, true);
  assert.deepEqual(observed.cases, oracle.cases); assert.deepEqual(observed.profile, oracle.profileCases); return observed;
}
const instance = await import(pathToFileURL(join(output, 'querystring_prototype.js')));
const calls = [check(JSON.parse(await instance.run()), 1), check(JSON.parse(await instance.run()), 2)];
const host = resolve(process.env.NODE_COMPAT_WASMTIME), version = spawnSync(host, ['--version'], { encoding: 'utf8' }); assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
const execution = spawnSync(host, ['run', '--invoke', 'run()', path], { encoding: 'utf8', timeout: 120000 }); assert.equal(execution.status, 0, execution.stderr);
const fresh = check(JSON.parse(decodeCliString(execution.stdout.trim())), 1);
const initialization = [];
for (const [name, expression] of [
  ['unescape-buffer-call', 'root.unescapeBuffer(3)'],
  ['unescape-buffer-new', 'new root.unescapeBuffer(3)'],
  ['unescape-nonstring-fallback', 'root.unescape(Symbol("x"))'],
  ['parse-input-cap', 'root.parse("x".repeat(1048577))'],
  ['deferred-microtask', 'Promise.resolve().then(()=>root.unescapeBuffer(3))'],
]) {
  const source = `import * as root from ${JSON.stringify(join(here, 'prototype.mjs'))}; ${expression}; export function run(){return '';}`;
  const input = join(output, name+'.mjs'); await writeFile(input, source);
  const lowered = await bundleProfile({ ...toolchain, input }); let failure;
  try { await selected.componentize(lowered.code, options); } catch (error) { failure = error; }
  assert(failure, name); assert.match(failure.message, /ERR_SM_NODE_(?:UNSUPPORTED|LIMIT)/, name);
  initialization.push({ name, sourceSha256: hash(source), bundledSourceSha256: hash(lowered.code), error: failure.message });
}
const report = { schema: 1, atUtc: new Date().toISOString(), node: process.version, installedBuiltin: false,
  engineSha256: metadata.engineSha256, sourceRoot, sourceFilesVerified: metadata.sourceManifest.length,
  engineBuildMetadata: metadata,
  adapter: { path: adapter, sha256: hash(await readFile(adapter)) },
  bundleImports: bundle.imports, bundledModules: bundle.moduleIds, interfaceAudit, emittedWit, emittedExports: [{ name: 'run', parameters: [], result: 'string' }],
  componentPath: path, componentSha256: hash(component), componentBytes: component.length,
  bundleSha256: hash(bundle.code), bundleBytes: Buffer.byteLength(bundle.code), sources: oracle.sources,
  componentHarnessSources: await Promise.all(['component.mjs', 'run-component.mjs'].map(async name => ({ name, sha256: hash(await readFile(join(here, name))) }))),
  componentizerProvenance: selected.provenance, calls, initialization,
  wasmtime: { version: version.stdout.trim(), sha256: hash(await readFile(host)), observed: fresh },
  limitations: ['Bundled isolated guest JS; no native module installation, alias/cache or CommonJS proof',
    'Native querystring module is not installed; Buffer module alone is external/native. Querystring profile caps/nonstring overload restrictions remain',
    'Size includes test vectors; no product performance comparison'] };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2)+'\n');
await writeFile(join(here, 'component-results.json'), JSON.stringify(report, null, 2)+'\n');
console.log(JSON.stringify({ output, differentialCases: oracle.cases.length, prototypeOnlyCases: oracle.profileCases.length,
  componentCalls: 3, initializationRejections: initialization.length, imports: [], wasmtimePassed: true }));
