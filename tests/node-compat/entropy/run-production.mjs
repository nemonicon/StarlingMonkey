// Real integration gate. Requires a freshly built policy engine and validated
// ComponentizeJS loader; never substitutes a JS entropy implementation.
import assert from 'node:assert/strict';
import { webcrypto, createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { ownershipChecks } from './ownership-checks.mjs';
import { initializationVectors } from './initialization-vectors.mjs';
import { validateEntropySelection, RANDOM } from './selection-policy.mjs';

assert.equal(process.version, 'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE, 'Explicit production policy engine required');
const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../..');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const metadata = JSON.parse(await readFile(engine + '.build.json'));
const policy = metadata.entropyPolicy;
assert(['off', 'runtime-only'].includes(policy));
assert.equal(metadata.debuggerEnabled, false);
assert.equal(metadata.gcStress, false);
const hash = value => createHash('sha256').update(value).digest('hex');
assert.equal(hash(await readFile(engine)), metadata.engineSha256);
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
for (const entry of metadata.sourceManifest) {
  assert.equal(hash(await readFile(join(sourceRoot, entry.path))), entry.sha256, `Engine source mismatch: ${entry.path}`);
}
const output = resolve(process.env.NODE_COMPAT_ENTROPY_OUTPUT ?? `/tmp/starling-node-compat/entropy-production-${policy}`);
const disabled = ['stdio', 'clocks', 'http', 'fetch-event', ...(policy === 'off' ? ['random'] : [])];
const selectedInterfaces = policy === 'off' ? [] : [RANDOM];
validateEntropySelection({ engineMetadata: metadata, disableFeatures: disabled, selectedInterfaces });
const toolchain = await loadToolchain();
const selected = await loadComponentizer(toolchain);
const { componentWit, transpile } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const preview2Adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
const preview2AdapterSha256 = hash(await readFile(preview2Adapter));
assert.equal(preview2AdapterSha256, '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const options = { engine, worldName: 'test', disableFeatures: disabled, selectedInterfaces, preview2Adapter };
const world = 'package test:entropy-policy; world test { export run: func() -> string; }';
const expectedSnapshotCode = policy === 'off' ? 'ERR_SM_ENTROPY_DISABLED' : 'ERR_SM_ENTROPY_INITIALIZATION';
const guest = (await readFile(join(here, 'guest-checks.mjs'), 'utf8')).replaceAll('export async function', 'async function');
const ownership = `const ownershipChecks = ${ownershipChecks.toString()};`;
const snapshotCapture = `const snapshot = []; function capture(operation, callback) { try { callback(); throw new Error('secure operation succeeded in snapshot: '+operation); } catch (error) { if(error.code!==${JSON.stringify(expectedSnapshotCode)}) throw error; snapshot.push({operation,code:error.code}); } }
capture('random-values',()=>crypto.getRandomValues(new Uint8Array(16)));
capture('uuid',()=>crypto.randomUUID());
capture('object-url',()=>URL.createObjectURL(new Blob(['x'])));
capture('multipart',()=>{const form=new FormData();form.append('x','y');new Response(form);});
${policy === 'runtime-only' ? "capture('math-random',()=>Math.random());" : ''}`;
const source = `${guest}\n${ownership}\n${snapshotCapture}\nlet calls=0; export async function run(){ return JSON.stringify({calls:++calls,snapshot,entropy:await entropyChecks(${JSON.stringify(policy)}),digestCopy:await digestCopyCheck(),ownership:await ownershipChecks(crypto)}); }`;
const oracle = await ownershipChecks(webcrypto);
const report = { schema: 1, verifiedAtUtc: new Date().toISOString(), policy, engine, engineSha256: metadata.engineSha256,
  sourceRoot, sourceFilesVerified: metadata.sourceManifest.length, componentizerProvenance: selected.provenance,
  selectedInterfaces, preview2Adapter: { path: preview2Adapter, sha256: preview2AdapterSha256,
    scope: 'Explicit pinned repository guest adapter; final interface audit must still show exact selected0.2.10 names, never remapped' }, expectedSnapshotCode, oracle, positive: [], initialization: [], diagnostics: [] };
async function build(name, app, wit = world) {
  const { component } = await selected.componentize(app, { ...options, witWorld: wit });
  const path = join(output, name + '.component.wasm');
  await writeFile(path, component);
  const emittedWit = await componentWit(component);
  const imports = [...emittedWit.matchAll(/^\s*import\s+([^;\s]+);/gm)].map(match => match[1]).sort();
  // Root component WIT is authoritative for external capabilities. Internal
  // adapter/core imports are not confused with externally required services.
  for (const imported of imports) assert(selectedInterfaces.includes(imported), `Unselected emitted capability: ${imported}`);
  assert.deepEqual(imports.filter(id => id.startsWith('wasi:random/')), selectedInterfaces);
  assert(!imports.some(id => id.includes('wasi_snapshot_preview1')), 'No external Preview1 service');
  const { files } = await transpile(component, { name, wasiShim: true });
  for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
  await writeFile(join(output, name + '.source.mjs'), app);
  await writeFile(join(output, name + '.emitted.wit'), emittedWit);
  return { path, modulePath: join(output, name + '.js'), componentSha256: hash(component), componentBytes: component.length,
    sourceSha256: hash(app), emittedWit, emittedImports: imports };
}
function checkObserved(observed, expectedCalls) {
  assert.equal(observed.calls, expectedCalls);
  assert.equal(observed.snapshot.length, policy === 'off' ? 4 : 5);
  assert(observed.snapshot.every(entry => entry.code === expectedSnapshotCode));
  assert.deepEqual(observed.ownership, oracle);
  assert.equal(observed.entropy.policy, policy);
  return observed;
}
const fixture = await build('entropy', source);
const instance = await import(pathToFileURL(fixture.modulePath));
const calls = [];
for (let i = 1; i <= 3; i++) calls.push(checkObserved(JSON.parse(await instance.run()), i));
const secondInstance = await import(pathToFileURL(fixture.modulePath).href + '?new-instance=1');
const fresh = checkObserved(JSON.parse(await secondInstance.run()), 1);
if (policy === 'runtime-only') {
  const samples = [...calls, fresh].map(call => call.entropy.bytes);
  assert.equal(new Set(samples).size, samples.length, 'Detect obvious random replay across calls/instances');
}
report.positive.push({ ...fixture, calls, freshInstance: fresh });
// bindExports invokes this property getter after finish_pre_initialization.
// A handled denial here must remain a snapshot denial, then runtime works.
const lateWorld = 'package test:late-entropy; world test { export api: interface { run: func() -> string; } }';
const lateSource = `${guest}\n${snapshotCapture}\nexport const api = { get run(){capture('late-export-getter',()=>crypto.getRandomValues(new Uint8Array(16)));return async()=>JSON.stringify({snapshot,entropy:await entropyChecks(${JSON.stringify(policy)})});} };`;
const late = await build('late_entropy', lateSource, lateWorld);
const lateInstance = await import(pathToFileURL(late.modulePath));
const lateObserved = JSON.parse(await lateInstance.api.run());
assert(lateObserved.snapshot.some(entry => entry.operation === 'late-export-getter' && entry.code === expectedSnapshotCode));
report.positive.push({ ...late, observed: lateObserved });
for (const vector of initializationVectors) {
  if (vector.diagnosticOnly) { report.diagnostics.push({ name: vector.name, executed: false, reason: vector.reason }); continue; }
  let failure;
  try { await selected.componentize(vector.source, { ...options, witWorld: vector.wit ?? 'package test:entropy-initialization; world test { export run: func(); }' }); }
  catch (error) { failure = error; }
  assert(failure, `Initialization vector succeeded: ${vector.name}`);
  assert.match(failure.message, new RegExp(expectedSnapshotCode), vector.name);
  report.initialization.push({ name: vector.name, sourceSha256: hash(vector.source), code: expectedSnapshotCode, error: failure.message });
}
if (process.env.NODE_COMPAT_WASMTIME) {
  const binary = resolve(process.env.NODE_COMPAT_WASMTIME);
  const version = spawnSync(binary, ['--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0); assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
  const result = spawnSync(binary, ['run', '--invoke', 'run()', fixture.path], { encoding: 'utf8', timeout: 120000 });
  assert.equal(result.status, 0, result.stderr);
  const observed = checkObserved(JSON.parse(JSON.parse(result.stdout.trim())), 1);
  report.wasmtime = { version: version.stdout.trim(), stdout: result.stdout, stderr: result.stderr, observed };
} else report.wasmtime = { executed: false, reason: 'NODE_COMPAT_WASMTIME not provided' };
report.limitations = ['Different samples detect obvious replay but do not certify entropy quality',
  'No deterministic finalization scheduling or exact GC hook is assumed',
  'Wasmtime scalar fixture does not exercise native incoming HTTP entry; run upstream crypto HTTP on Wasmtime and wasmCloud separately',
  'Root emitted imports are audited here; internal executable core import proof belongs to packaging receipt'];
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, policy, positiveComponents: report.positive.length, initializationRejections: report.initialization.length, ownedInputCases: oracle.length, emittedImports: fixture.emittedImports, wasmtimePassed: !!report.wasmtime.observed }));
