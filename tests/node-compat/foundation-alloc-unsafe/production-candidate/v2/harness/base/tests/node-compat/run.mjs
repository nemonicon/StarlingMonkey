// Native integration only: no released-engine fallback and no JS Buffer kernel.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { loadToolchain } from './toolchain.mjs';
import { loadComponentizer } from './componentizer.mjs';
import { bundleProfile } from './profile-bundler.mjs';
import { selectedManifestsForEngine } from './module-selection.mjs';
import { makeOracleCorpus } from './oracle.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../..');
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
assert(process.env.NODE_COMPAT_ENGINE, 'Set NODE_COMPAT_ENGINE to the rebuilt native-profile ComponentizeJS embedding engine; released fallback is forbidden');
assert(process.env.NODE_COMPAT_WASMTIME, 'Set NODE_COMPAT_WASMTIME to Wasmtime 42.0.1');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const wasmtime = resolve(process.env.NODE_COMPAT_WASMTIME);
const output = resolve(process.env.NODE_COMPAT_OUTPUT ?? '/tmp/starling-node-compat/native-output');
const toolchainInfo = await loadToolchain();
const { directory: toolchain, require, rolldown, parseAst } = toolchainInfo;
const hash = value => createHash('sha256').update(value).digest('hex');
const engineBytes = await readFile(engine);
const engineSha256 = hash(engineBytes);
const metadataPath = resolve(process.env.NODE_COMPAT_ENGINE_METADATA ?? engine + '.build.json');
const engineMetadata = JSON.parse(await readFile(metadataPath));
assert.equal(engineMetadata.engineSha256, engineSha256, 'Engine metadata must identify the tested artifact');
assert.equal(engineMetadata.profileEnabled, true, 'Native profile must be enabled in the build metadata');
assert.equal(engineMetadata.debuggerEnabled, false, 'Native production profile excludes debugger support');
assert.equal(engineMetadata.auditedBaseRevision ?? engineMetadata.starlingMonkeyRevision, '54b3329b3ce818fd1f244e871e9c259b63667cda', 'Unexpected audited StarlingMonkey baseline');
assert.equal(engineMetadata.componentizeJsRevision, '4d812f5a7b524cea5bcfd565cac55f3fab876a57', 'Unexpected ComponentizeJS source baseline');
const sourceFiles = new Set(engineMetadata.sourceManifest?.map(entry => entry.path));
for (const path of ['buffer.cpp', 'register.cpp', 'factories.generated.h', 'buffer-facade.mjs', 'child-process.mjs',
  'unsupported.mjs', 'generate-factories.mjs', 'export-manifest.node-v22.14.0.json'].map(name => 'builtins/node-compat/' + name)
  .concat('cmake/builtins.cmake')) {
  assert(sourceFiles.has(path), `Build metadata must include ${path}`);
}
for (const entry of engineMetadata.sourceManifest) {
  const path = resolve(sourceRoot, entry.path);
  assert(path.startsWith(sourceRoot + '/'), 'Build source manifest paths must stay inside this checkout');
  assert.equal(hash(await readFile(path)), entry.sha256, `Stale engine: current source differs from build metadata (${entry.path})`);
}
const generatedCheck = spawnSync(process.execPath, [join(sourceRoot, 'builtins/node-compat/generate-factories.mjs'), '--check'], { encoding: 'utf8' });
assert.equal(generatedCheck.status, 0, generatedCheck.stderr || generatedCheck.stdout);
const componentizeDirectory = join(toolchain, 'node_modules/@bytecodealliance/componentize-js');
const releasedEngineSha256 = hash(await readFile(join(componentizeDirectory, 'lib/starlingmonkey_embedding.wasm')));
assert.notEqual(engineSha256, releasedEngineSha256, 'Released embedding engine cannot validate native-profile integration');
const { componentize, provenance: componentizerProvenance } = await loadComponentizer(toolchainInfo);
const { transpile, componentWit } = await import(pathToFileURL(require.resolve('@bytecodealliance/jco')));
const hostVersion = spawnSync(wasmtime, ['--version'], { encoding: 'utf8' });
assert.equal(hostVersion.status, 0, hostVersion.error?.message || hostVersion.stderr);
assert.match(hostVersion.stdout, /^wasmtime 42\.0\.1\b/);
await mkdir(output, { recursive: true });
await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
try { await symlink(join(toolchain, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const builtinManifests = selectedManifestsForEngine(engineMetadata, { sourceRoot });
const corpus = makeOracleCorpus();
const virtualModules = { 'node-compat:oracle-vectors': `export default ${JSON.stringify(corpus)};` };
const semanticEntry = resolve(process.env.NODE_COMPAT_SEMANTIC_ENTRY ?? join(here, 'fixtures/component.mjs'));
const bundle = await bundleProfile({ rolldown, parseAst, input: semanticEntry, virtualModules, builtinManifests });
assert.deepEqual(bundle.imports.sort(), ['node:buffer', 'node:child_process']);
assert.doesNotMatch(bundle.code, /reference-kernel|buffer-facade|createBufferModule|hexEncode|hexDecode|__require/,
  'The bundle must call the native registered module, never inline its facade or a JS kernel');
assert(bundle.moduleIds.every(id => !/node_modules\/(?:buffer|unenv)|node-builtins/.test(id)));
await writeFile(join(output, 'application.bundle.mjs'), bundle.code);
await writeFile(join(output, 'oracle-corpus.json'), JSON.stringify(corpus) + '\n');
const opts = { engine, witWorld: await readFile(join(here, 'profile.wit'), 'utf8'), worldName: 'profile',
  disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
const { component, interfaceAudit } = await componentize(bundle.code, opts);
const componentPath = join(output, 'native-profile.component.wasm');
await writeFile(componentPath, component);
const wit = await componentWit(component);
await writeFile(join(output, 'emitted.wit'), wit);
const imports = wit.split('\n').filter(line => /^\s*import /.test(line));
assert.deepEqual(imports, [], 'The final native Buffer/stub component must have zero host imports');
const { files } = await transpile(component, { name: 'native-profile' });
for (const [name, value] of Object.entries(files)) {
  const destination = join(output, name);
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(destination, value);
}
const instance = await import(pathToFileURL(join(output, 'native-profile.js')));
const first = JSON.parse(await instance.run());
assert(!first.failure, JSON.stringify(first.failure, null, 2));
const second = JSON.parse(await instance.run());
assert(!second.failure, JSON.stringify(second.failure, null, 2));
assert.equal(first.calls, 1);
assert.equal(second.calls, 2);
assert.equal(first.strings, corpus.strings.length);
assert.equal(first.bytes, corpus.bytes.length);
assert.equal(first.stubCalls, 9);
assert.equal(first.stubConstructors, 9);
assert.equal(first.globalBufferIdentity, true);
const host = spawnSync(wasmtime, ['run', '--invoke', 'run()', componentPath], { encoding: 'utf8', timeout: 120000 });
assert.equal(host.status, 0, host.stderr || host.stdout);
function decodeWaveReport(stdout) {
  const outer = stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g, (_, hex) => String.fromCodePoint(parseInt(hex, 16)));
  return JSON.parse(JSON.parse(outer));
}
assert.deepEqual(decodeWaveReport(host.stdout), first, 'Wasmtime must execute the same native component successfully');
// The main bundler intentionally canonicalizes bare aliases. This separate
// unbundled fixture proves that the native loader also registers both IDs and
// caches repeated imports, without mistaking bundler deduplication for evidence.
const aliasBuild = await componentize(await readFile(join(here, 'fixtures/raw-aliases.mjs'), 'utf8'), opts);
const aliasPath = join(output, 'native-aliases.component.wasm');
await writeFile(aliasPath, aliasBuild.component);
const aliasWit = await componentWit(aliasBuild.component);
assert.deepEqual(aliasWit.split('\n').filter(line => /^\s*import /.test(line)), []);
const aliasHost = spawnSync(wasmtime, ['run', '--invoke', 'run()', aliasPath], { encoding: 'utf8', timeout: 120000 });
assert.equal(aliasHost.status, 0, aliasHost.stderr || aliasHost.stdout);
assert.match(aliasHost.stdout, /native registry aliases, dynamic imports and per-specifier caching passed/);
const initializationFailures = [];
for (const [fixture, expected] of [
  ['top-level-failure.mjs', /node:child_process\.spawn is unavailable/],
  ['top-level-constructor-failure.mjs', /node:child_process\.ChildProcess is unavailable/],
  ['top-level-await-failure.mjs', /node:child_process\.exec is unavailable/],
  ['unknown-export.mjs', /DefinitelyNotANodeExport|does not provide.*export|not found.*export|indirect export/],
]) {
  const built = await bundleProfile({ rolldown, parseAst, input: join(here, 'fixtures', fixture), builtinManifests });
  let failure = '';
  try { await componentize(built.code, opts); } catch (error) { failure = error.message; }
  assert.match(failure, expected, `${fixture} must fail during componentization`);
  initializationFailures.push({ fixture, expectedFailure: true, excerpt: failure.split('\n').filter(line => /child_process|DefinitelyNotANodeExport|export|Failed to initialize/.test(line)).slice(0, 5) });
}
const summary = {
  schema: 1, node: process.version, engine, engineSha256, releasedEngineRejected: engineSha256 !== releasedEngineSha256,
  engineMetadataPath: metadataPath, engineMetadata, componentizerProvenance,
  wasmtime: hostVersion.stdout.trim(), componentBytes: component.length, componentSha256: hash(component),
  bundleImports: bundle.imports, bundledModules: bundle.moduleIds, globalBufferPolicy: bundle.globalBufferPolicy,
  semanticEntry, sourceRoot,
  emittedImports: imports, emittedWit: wit, interfaceAudit, calls: [first, second], wasmtimeReport: decodeWaveReport(host.stdout),
  rawAliasFixture: { componentBytes: aliasBuild.component.length, componentSha256: hash(aliasBuild.component), emittedWit: aliasWit, wasmtimeStdout: aliasHost.stdout.trim() },
  initializationFailures,
  limitations: ['No wasmCloud deployment in this runner',
    ...(!first.backingCases.includes('shared-rejected') ? ['SharedArrayBuffer is not exposed by this engine, so shared-input construction tests were skipped'] : []),
    engineMetadata.gcStress ? 'Native GC stress enabled; exhaustive OOM injection remains untested' : 'GC stress requires a separately configured native engine build; no production GC hook exposed',
    'Performance thresholds and broad Node compatibility remain outside this vertical slice'],
};
await writeFile(join(output, 'results.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));
