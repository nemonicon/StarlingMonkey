// Actual Jco1.40 Path adapter against the same profile-enabled engine.
// The shared benchmark world explicitly selects standard cli/environment0.2.10.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir, cp, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { selectedManifestsForEngine } from '../module-selection.mjs';
import { createProfilePlugin } from '../profile-bundler.mjs';
import { componentizeSelectedPath } from './package-selected.mjs';
import { buildDeniedPreview1 } from './denied-preview1.mjs';
import { auditEnvironmentTypes } from './environment-type-audit.mjs';
const here = dirname(fileURLToPath(import.meta.url));
const repository = resolve(here, '../../..');
const sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
const output = resolve(process.env.NODE_COMPAT_PATH_BENCH_OUTPUT ?? '/tmp/starling-node-compat/foundation-path-benchmark');
const engine = resolve(process.env.NODE_COMPAT_ENGINE);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const wasmTools = resolve(process.env.NODE_COMPAT_WASM_TOOLS ?? '/tmp/starling-node-compat/improved-build/cache/wasm-tools/1448/wasm-tools');
assert(process.env.NODE_COMPAT_WASMTIME, 'Explicit Wasmtime42 is required for adapter and component validation');
const metadata = JSON.parse(await readFile(engine + '.build.json'));
assert.equal(hash(await readFile(engine)), metadata.engineSha256); assert.equal(metadata.pathEnabled, true);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE, 'Release');
for (const entry of metadata.sourceManifest) {
  const path = resolve(sourceRoot, entry.path); assert(path.startsWith(sourceRoot + '/'));
  assert.equal(hash(await readFile(path)), entry.sha256, entry.path);
}
const selected = selectedManifestsForEngine(metadata, { sourceRoot });
const tools = await loadToolchain();
const { componentize, provenance, directory: componentizerDirectory } = await loadComponentizer(tools);
const { transpile, componentWit } = await import(pathToFileURL(tools.require.resolve('@bytecodealliance/jco')));
const { _setPreopens, _clearPreopens } = await import(pathToFileURL(tools.require.resolve('@bytecodealliance/preview2-shim/filesystem')));
let wasmtimeVersion;
if (process.env.NODE_COMPAT_WASMTIME) {
  const host = spawnSync(process.env.NODE_COMPAT_WASMTIME, ['--version'], { encoding: 'utf8' });
  assert.equal(host.status, 0, host.stderr); assert.match(host.stdout, /^wasmtime 42\.0\.1\b/);
  wasmtimeVersion = host.stdout.trim();
}
const adapterPath = join(dirname(tools.require.resolve('@bytecodealliance/jco')), 'node-builtins/path.js');
const { createPathBuiltin } = await import(pathToFileURL(adapterPath));
const { VIRTUAL_PREFIX } = await import(pathToFileURL(join(dirname(adapterPath), 'shared.js')));
const adapter = createPathBuiltin({ options: {}, worldMetadata: { imports: [
  { namespace: 'wasi', package: 'cli', interface: 'environment', version: { major: 0n, minor: 2n, patch: 10n } },
] } });
await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
const preview1 = await buildDeniedPreview1(wasmTools, process.env.NODE_COMPAT_WASMTIME, output);
const preview1AdapterPath = preview1.path;
try { await symlink(join(tools.directory, 'node_modules'), join(output, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const witPath = join(output, 'wit'); await mkdir(witPath, { recursive: true });
await cp(join(repository, 'host-apis/wasi-0.2.10/wit/deps'), join(witPath, 'deps'), { recursive: true });
await writeFile(join(witPath, 'profile.wit'), await readFile(join(here, 'benchmark.mjs.wit')));
const nativeBuild = await tools.rolldown({ input: join(here, 'benchmark.mjs'), platform: 'neutral', treeshake: true,
  plugins: [createProfilePlugin(tools.parseAst, { builtinManifests: selected })] });
let native;
try {
  const { output: chunks } = await nativeBuild.generate({ format: 'esm', codeSplitting: false });
  assert.equal(chunks.length, 1);
  native = { code: chunks[0].code, imports: chunks[0].imports, moduleIds: Object.keys(chunks[0].modules) };
} finally { await nativeBuild.close(); }
const existing = await tools.rolldown({ input: join(here, 'benchmark.mjs'), platform: 'neutral', treeshake: true,
  plugins: [{ name: 'actual-jco-path-adapter', resolveId(id) {
    if (id.startsWith(VIRTUAL_PREFIX)) return id;
    if (id.startsWith('wasi:')) return { id, external: true };
    return adapter.resolveId(id);
  }, load(id) { return adapter.load(id); } }] });
let js;
try {
  const { output: chunks } = await existing.generate({ format: 'esm', codeSplitting: false });
  assert.equal(chunks.length, 1);
  js = { code: chunks[0].code, imports: chunks[0].imports, moduleIds: Object.keys(chunks[0].modules) };
} finally { await existing.close(); }
assert.deepEqual(native.imports, ['node:path']);
assert.deepEqual(js.imports, ['wasi:cli/environment@0.2.10']);
assert(js.moduleIds.some(id => /jco-std/.test(id)) && js.moduleIds.some(id => /minimatch/.test(id)));
const adapterSources = await Promise.all(js.moduleIds.filter(id => id.startsWith('/')).map(async path =>
  ({ path, sha256: hash(await readFile(path)) })));
const stdPackage = JSON.parse(await readFile(join(tools.directory, 'node_modules/@bytecodealliance/jco-std/package.json')));
assert.equal(stdPackage.version, '0.10.0');
const iterations = 1000;
let expected = 0x811c9dc5;
for (let i = 0; i < iterations; i++) expected = Math.imul(expected ^ 62, 16777619) | 0;
const arms = [];
for (const [name, bundle] of [['registered-profile', native], ['existing-jco-adapter', js]]) {
  await writeFile(join(output, name + '.bundle.mjs'), bundle.code);
  // Build-tool parser access only; this does not add a deployed filesystem import.
  _setPreopens({ [witPath]: witPath });
  let component, interfaceAudit, packagingAudit;
  try {
    ({ component, interfaceAudit, packagingAudit } = await componentizeSelectedPath(tools, componentize,
      componentizerDirectory, provenance, bundle.code, { engine, witPath, worldName: 'profile', preview2Adapter: preview1AdapterPath,
      disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'],
      selectedInterfaces: ['wasi:cli/environment@0.2.10'] }, async (core, coreImports) => {
        await writeFile(join(output, name + '.final-core.wasm'), core);
        await writeFile(join(output, name + '.core-imports.json'), JSON.stringify(coreImports, null, 2) + '\n');
      }));
  } finally { _clearPreopens(); }
  const path = join(output, name + '.component.wasm'); await writeFile(path, component);
  const wit = await componentWit(component); await writeFile(join(output, name + '.wit'), wit);
  const emittedImports = wit.split('\n').filter(line => /^\s*import /.test(line)).map(line => line.trim());
  assert.deepEqual(emittedImports, ['import wasi:cli/environment@0.2.10;'], 'Exactly the selected standard capability must remain');
  const environmentTypeAudit = await auditEnvironmentTypes(wasmTools, path, witPath, output, name);
  const { files } = await transpile(component, { name, wasiShim: true });
  for (const [filename, bytes] of Object.entries(files)) {
    const destination = join(output, filename); await mkdir(dirname(destination), { recursive: true }); await writeFile(destination, bytes);
  }
  const instance = await import(pathToFileURL(join(output, name + '.js')));
  assert.equal(instance.run(iterations), expected);
  const timingsMs = [];
  if (process.env.NODE_COMPAT_PATH_TIMING === '1') {
    for (let i = 0; i < 3; i++) assert.equal(instance.run(iterations), expected);
    for (let i = 0; i < 7; i++) {
      const start = performance.now(); const checksum = instance.run(iterations); const elapsed = performance.now() - start;
      assert.equal(checksum, expected); timingsMs.push(elapsed);
    }
  }
  let wasmtime;
  if (process.env.NODE_COMPAT_WASMTIME) {
    const host = spawnSync(process.env.NODE_COMPAT_WASMTIME, ['run', '--invoke', `run(${iterations})`, path], { encoding: 'utf8', timeout: 180000 });
    assert.equal(host.status, 0, host.error?.message || host.stderr); assert.equal(Number(host.stdout.trim()), expected);
    wasmtime = { checked: true, checksum: expected };
  }
  arms.push({ name, bundleBytes: Buffer.byteLength(bundle.code), bundleSha256: hash(bundle.code), imports: bundle.imports,
    moduleIds: bundle.moduleIds, componentPath: path, componentBytes: component.length, componentSha256: hash(component),
    emittedImports, emittedWit: wit, interfaceAudit, environmentTypeAudit, packagingAudit, checksum: expected, timingsMs, wasmtime });
}
const report = { schema: 1, measuredAtUtc: new Date().toISOString(), engine, engineSha256: metadata.engineSha256,
  metadata, sourceRoot, componentizer: provenance, node: process.version, wasmtimeVersion,
  preview1Adapter: { path: preview1AdapterPath, ...preview1.audit },
  adapter: { path: adapterPath, sha256: hash(await readFile(adapterPath)),
    version: 'Jco1.40.0 / jco-std0.10.0 / its lock-pinned installed matcher dependency', wasiEnvironment: '0.2.10',
    sourceManifest: adapterSources },
  iterations, bundlerPolicy: { platform: 'neutral', treeshake: true, format: 'esm', codeSplitting: false },
  operationsPerIteration: ['POSIX join', 'Win32 normalize', 'ASCII brace glob match'], arms,
  componentByteDeltaAvoided: arms[1].componentBytes - arms[0].componentBytes,
  timing: { enabled: process.env.NODE_COMPAT_PATH_TIMING === '1', backend: 'V8-hosted Wasm through Jco; host performance.now around persistent instance run batches', warmups: 3, samples: 7 },
  sourceManifest: await Promise.all(['benchmark.mjs', 'benchmark.mjs.wit', 'benchmark-adapter.mjs', 'package-selected.mjs', 'environment-type-audit.mjs',
    'denied-preview1.mjs', 'denied-preview1.wat'].map(async path =>
    ({ path, sha256: hash(await readFile(join(here, path))) }))),
  limitations: ['Both arms use the identical Path-enabled custom engine; size delta measures avoided bundled-adapter duplication, not a minimal deployment saving.',
    'The common benchmark world explicitly admits standard cli/environment0.2.10 because the actual adapter requires it. The pure-profile acceptance fixture independently proves zero imports.',
    'The benchmark-only guest adapter traps four unused internal Preview1 args/environment calls exactly as the pure-profile feature pass does; it implements no environment service. Real P2 environment imports remain selected and type-audited.',
    'The existing adapter targets a newer Node release/matcher and broader host-backed cwd behavior. Only the fixed common benign workload is compared; historical vulnerable adversarial inputs are not run.',
    'Optional warmed V8 timings exclude packaging/instantiation and do not measure Wasmtime throughput, cold startup, RSS or memory high-water.'] };
await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2) + '\n');
await writeFile(join(here, 'benchmark-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output, componentByteDeltaAvoided: report.componentByteDeltaAvoided,
  arms: arms.map(({ name, componentBytes, emittedImports }) => ({ name, componentBytes, emittedImports })) }, null, 2));
