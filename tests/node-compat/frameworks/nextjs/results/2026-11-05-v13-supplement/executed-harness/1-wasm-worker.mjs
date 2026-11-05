// One independently captured framework observation. This is a regression runner,
// not a native-profile admission change or a general Next.js Wasm adapter.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, open, realpath, lstat, readdir } from 'node:fs/promises';
import { dirname, join, resolve, relative, isAbsolute } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../../toolchain.mjs';
import { loadComponentizer } from '../../componentizer.mjs';
import { bundleProfile } from '../../profile-bundler.mjs';
import { selectedManifestsForEngine } from '../../module-selection.mjs';
import { runOwnedCommand } from '../../foundation-zlib/cost-jco-correctness-candidate-v2/durable-host.mjs';
import { parseScalarStringOutput } from '../../foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs';

const HERE = dirname(fileURLToPath(import.meta.url)), REPOSITORY = resolve(HERE, '../../../..');
const EXPECTED_ENGINE = 'd54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92';
const EXPECTED_METADATA = 'bfaec95ee0058edf587ebbf1cb020d7871759e896aa0d809e1af788a300531d6';
const EXPECTED_ADAPTER = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0';
const CASES = new Set(['compat', 'compat-caught', 'native-modules', 'react-element', 'react-dom-edge', 'react-dom-string', 'next-server', 'next-headers', 'next-standalone', 'next-page', 'next-route', 'import-fs-promises', 'import-crypto', 'import-async-hooks', 'import-http', 'import-net', 'import-url', 'import-process', 'import-timers', 'child-process-call', 'buffer-unsupported']);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const descriptor = async path => { const bytes = await readFile(path); return { path: resolve(path), sha256: hash(bytes), bytes: bytes.length }; };
async function durable(path, data) {
  const handle = await open(path, 'wx', 0o600);
  try { await handle.writeFile(data); await handle.sync(); } finally { await handle.close(); }
  return descriptor(path);
}
const json = (path, value) => durable(path, JSON.stringify(value, null, 2) + '\n');
function errorData(error) {
  if (typeof error === 'string') return { thrownString: error.slice(0, 65536), diagnosticClipped: error.length > 65536 };
  const result = { classification: 'caught-host-or-guest-error', diagnosticOnly: true };
  try {
    const props = Object.getOwnPropertyDescriptors(error ?? {});
    for (const name of ['name', 'code', 'message', 'stack']) {
      const value = props[name]?.value;
      if (typeof value === 'string') { result[name] = value.slice(0, 65536); if (value.length > 65536) result.diagnosticClipped = true; }
    }
  } catch { result.errorPropertiesUnavailable = true; }
  return result;
}
function options(argv) {
  assert(argv.length % 2 === 0); const result = {};
  for (let i = 0; i < argv.length; i += 2) {
    assert(['--case', '--application', '--output', '--engine', '--source-root'].includes(argv[i]));
    assert(!Object.hasOwn(result, argv[i])); result[argv[i]] = argv[i + 1];
  }
  for (const name of ['--case', '--application', '--output', '--engine', '--source-root']) assert(result[name]);
  return result;
}
async function preflight(engine, sourceRoot) {
  assert.equal(process.version, 'v22.14.0');
  const engineRow = await descriptor(engine), metadataRow = await descriptor(engine + '.build.json');
  assert.equal(engineRow.sha256, EXPECTED_ENGINE); assert.equal(metadataRow.sha256, EXPECTED_METADATA);
  const metadata = JSON.parse(await readFile(metadataRow.path));
  assert.equal(metadata.engineSha256, EXPECTED_ENGINE); assert.equal(metadata.sourceManifest.length, 342);
  assert.equal(metadata.entropyPolicy, 'off'); assert.equal(metadata.gcStress, false); assert.equal(metadata.oomTesting, false);
  const canonicalSourceRoot = await realpath(sourceRoot);
  const sourceInputs = [];
  for (const row of metadata.sourceManifest) {
    assert(!isAbsolute(row.path) && row.path.split('/').every(p => p && p !== '.' && p !== '..'));
    const path = join(canonicalSourceRoot, row.path);
    assert.equal(await realpath(path), path); assert(!(await lstat(path)).isSymbolicLink());
    const actual = await descriptor(path); assert.equal(actual.sha256, row.sha256, row.path); sourceInputs.push(actual);
  }
  const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot: canonicalSourceRoot });
  assert.equal(builtinManifests.length, 9);
  return { engine: engineRow, metadata: metadataRow, sourceRoot: canonicalSourceRoot,
    sourceInputs, selectedModuleManifests: metadata.selectedModuleManifests, builtinManifests };
}
async function toolingEvidence(toolchain, packaging = null) {
  const inputs = [];
  for (const name of ['toolchain.mjs', 'componentizer.mjs', 'profile-bundler.mjs', 'module-selection.mjs',
    'private-ticks-admission.mjs', 'classic-streams-admission.mjs', 'capability-policy.mjs', 'wasi-0.2.10-interfaces.json']) inputs.push(await descriptor(resolve(HERE, '../..', name)));
  const packages = {};
  for (const name of ['@bytecodealliance/componentize-js', '@bytecodealliance/jco', 'rolldown']) packages[name] = await descriptor(join(toolchain.directory, 'node_modules', name, 'package.json'));
  const adapter = await descriptor(join(REPOSITORY, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'));
  assert.equal(adapter.sha256, EXPECTED_ADAPTER);
  return { node: await descriptor(process.execPath), toolchainRoot: toolchain.directory, packages, inputs, adapter,
    packaging: packaging?.provenance ?? null, worker: await descriptor(fileURLToPath(import.meta.url)) };
}
async function recheck(evidence) {
  for (const row of [evidence.engine, evidence.metadata, ...evidence.sourceInputs]) assert.deepEqual(await descriptor(row.path), row);
}
async function componentChild(configPath) {
  const config = JSON.parse(await readFile(configPath));
  const native = await preflight(config.engine, config.sourceRoot); const toolchain = await loadToolchain();
  const selected = await loadComponentizer(toolchain), tools = await toolingEvidence(toolchain, selected);
  assert.deepEqual(await descriptor(config.source.path), config.source);
  await json(join(config.output, 'component-tools.json'), tools);
  const source = await readFile(config.source.path, 'utf8');
  const buildOptions = { engine: native.engine.path, preview2Adapter: tools.adapter.path,
    witWorld: 'package test:framework; world test { export run: func() -> string; }', worldName: 'test',
    disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [],
    finalizeComponent: async result => {
      await durable(join(config.output, 'component.wasm'), result.component);
      return result.component;
    } };
  try {
    const built = await selected.componentize(source, buildOptions);
    await json(join(config.output, 'interface-audit.json'), built.interfaceAudit);
    await recheck(native);
    await json(join(config.output, 'component-child-result.json'), { stage: 'componentization', status: 'passed', component: await descriptor(join(config.output, 'component.wasm')), imports: built.interfaceAudit.emittedImports });
  } catch (error) {
    const retainedComponent = await descriptor(join(config.output, 'component.wasm')).catch(() => null);
    await json(join(config.output, 'component-child-error.json'), { stage: 'componentization-or-final-interface-audit', retainedComponent, ...errorData(error) });
    throw error;
  }
}
async function probeSource(name, application) {
  if (name === 'compat') return { source: `import {runCompat} from './lib/compat.mjs';\nexport async function run(){return JSON.stringify(await runCompat());}\n`, original: join(application, 'lib/compat.mjs') };
  if (name === 'compat-caught') return { source: `import {runCompat} from './lib/compat.mjs';\nexport async function run(){try{return JSON.stringify({passed:true,value:await runCompat()});}catch(e){return JSON.stringify({caught:true,name:e.name,code:e.code,message:e.message,stack:e.stack});}}\n`, original: join(application, 'lib/compat.mjs'), diagnosticOnly: true };
  if (name.startsWith('import-')) {
    const modules = { 'import-fs-promises': 'node:fs/promises', 'import-crypto': 'node:crypto', 'import-async-hooks': 'node:async_hooks',
      'import-http': 'node:http', 'import-net': 'node:net', 'import-url': 'node:url', 'import-process': 'node:process', 'import-timers': 'node:timers' };
    assert(Object.hasOwn(modules, name));
    return { source: `import * as actual from ${JSON.stringify(modules[name])};\nexport function run(){return JSON.stringify({module:${JSON.stringify(modules[name])},exports:Object.keys(actual)});}\n` };
  }
  if (['next-standalone', 'next-page', 'next-route'].includes(name)) {
    const paths = { 'next-standalone': ['.next/standalone/server.js'], 'next-page': ['.next/server/app/page.js'], 'next-route': ['.next/server/app/api/compat/route.js', '.next/server/app/api/health/route.js'] }[name];
    const candidates = paths.map(p => join(application, p));
    let original = null;
    for (const path of candidates) if (await lstat(path).then(s => s.isFile(), e => { if (e.code === 'ENOENT') return false; throw e; })) { original = path; break; }
    if (!original) return { missing: true, candidates };
    return { original, candidates, source: `import * as actual from ${JSON.stringify('./' + relative(application, original))};\nexport function run(){return JSON.stringify({generatedModule:${JSON.stringify(relative(application, original))},exports:Object.keys(actual),serverListenInvokedByProbe:false,routeHandlerInvokedByProbe:false});}\n` };
  }
  const path = join(HERE, 'probes', name + '.mjs');
  return { source: await readFile(path, 'utf8'), original: path };
}
async function retainProcess(output, name, outcome) {
  for (const [kind, row] of [['stdout', outcome.stdoutFile], ['stderr', outcome.stderrFile]]) await durable(join(output, name + '.' + kind + '.log'), await readFile(row.path));
  await json(join(output, name + '.terminal.json'), JSON.parse(await readFile(outcome.terminalPath)));
}
async function main() {
  const args = options(process.argv.slice(2)), name = args['--case'], application = resolve(args['--application']), output = resolve(args['--output']);
  assert(CASES.has(name), 'Unknown finite framework case');
  assert(!output.startsWith(REPOSITORY + '/')); await mkdir(output, { mode: 0o700 }); await mkdir(join(output, 'processes'), { mode: 0o700 });
  const report = { schemaVersion: 1, case: name, stage: 'preflight', status: 'pending',
    source: 'genuine accepted foundations-v13', selectedInterfaces: [], experimentalEngineUsed: false,
    builtinAdaptersUsed: false, fullNextServerClaim: false, failures: [], output };
  const save = async () => {
    const path = join(output, 'result.json'), handle = await open(path, 'w', 0o600);
    try { await handle.writeFile(JSON.stringify(report, null, 2) + '\n'); await handle.sync(); } finally { await handle.close(); }
  };
  let native;
  try {
    native = await preflight(resolve(args['--engine']), resolve(args['--source-root']));
    await json(join(output, 'native-preflight.json'), native); report.engine = native.engine; report.metadata = native.metadata;
    const toolchain = await loadToolchain(); await json(join(output, 'tooling-preflight.json'), await toolingEvidence(toolchain));
    report.stage = 'fixture'; await save();
    const probe = await probeSource(name, application); report.diagnosticOnly = probe.diagnosticOnly === true; await json(join(output, 'fixture.json'), { original: probe.original ?? null, candidates: probe.candidates ?? [], missing: probe.missing ?? false, diagnosticOnly: probe.diagnosticOnly === true });
    if (probe.missing) { report.status = 'missing-fixture'; report.reason = 'GENERATED_NEXT_FIXTURE_NOT_FOUND'; report.candidates = probe.candidates; return; }
    if (probe.original) report.originalSource = await descriptor(probe.original);
    const entry = join(application, '.sm-wasm-' + name + '-' + hash(Buffer.from(output)).slice(0, 12) + '.mjs'); await durable(entry, probe.source); await durable(join(output, 'entry-source.txt'), probe.source);
    report.stage = 'bundling'; await save();
    const bundled = await bundleProfile({ ...toolchain, builtinManifests: native.builtinManifests, input: entry });
    report.bundle = await durable(join(output, 'bundle.mjs'), bundled.code);
    await durable(join(output, 'bundle-source.txt'), bundled.code);
    await json(join(output, 'bundle-graph.json'), { imports: bundled.imports, moduleIds: bundled.moduleIds, admittedBuiltins: bundled.admittedBuiltins, globalBufferPolicy: bundled.globalBufferPolicy });
    report.stage = 'componentization'; await save();
    const configPath = join(output, 'component-config.json'); await json(configPath, { engine: native.engine.path, sourceRoot: native.sourceRoot, output, source: report.bundle });
    const component = await runOwnedCommand({ output, name: 'componentize', executable: process.execPath,
      args: [fileURLToPath(import.meta.url), '--component-child', configPath], write: writeFile, register: () => {}, timeoutMs: 120000, maxOutputBytes: 16 * 1024 * 1024 });
    await retainProcess(output, 'componentize', component);
    report.componentizer = { status: component.status, signal: component.signal, timedOut: component.timedOut, ownedGroupGone: component.ownedGroupGone };
    if (!component.terminalExitZeroObserved || !component.ownedGroupGone) { report.status = 'failed'; report.failures.push({ stage: report.stage, reason: 'Owned component child did not finish raw zero and clean' }); return; }
    report.component = await descriptor(join(output, 'component.wasm'));
    report.stage = 'interface-validation'; await save();
    const { componentWit, transpile } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
    const bytes = await readFile(report.component.path), wit = await componentWit(bytes);
    await durable(join(output, 'emitted.wit'), wit);
    assert.equal(wit.replace(/\s+/g, ' ').trim(), 'package root:component; world root { export run: func() -> string; }');
    const audit = JSON.parse(await readFile(join(output, 'interface-audit.json'))); assert.deepEqual(audit.emittedImports, []);
    const transpiled = await transpile(bytes, { name: 'framework' });
    await json(join(output, 'transpile-metadata.json'), { imports: transpiled.imports, exports: transpiled.exports, files: Object.keys(transpiled.files) });
    await mkdir(join(output, 'transpiled'), { mode: 0o700 }); await durable(join(output, 'transpiled/package.json'), '{"type":"module"}\n');
    for (const [file, data] of Object.entries(transpiled.files)) { assert(!isAbsolute(file) && file.split('/').every(p => p && p !== '.' && p !== '..')); await mkdir(dirname(join(output, 'transpiled', file)), { recursive: true }); await durable(join(output, 'transpiled', file), data); }
    report.stage = 'jco-runtime'; await save();
    let first = null;
    try {
      const loaded = await import(pathToFileURL(join(output, 'transpiled/framework.js'))); assert.equal(typeof loaded.run, 'function');
      for (let i = 0; i < 3; i++) {
        const value = loaded.run();
        await json(join(output, 'jco-' + i + '.raw.json'), { type: typeof value, ...(typeof value === 'string' ? { value } : { opaque: true }) });
        assert.equal(typeof value, 'string'); await durable(join(output, 'jco-' + i + '.string.txt'), value); const parsed = JSON.parse(value);
        await json(join(output, 'jco-' + i + '.parsed.json'), parsed); if (i === 0) first = value; else assert.equal(value, first);
      }
      report.jco = { passed: true, retainedCalls: 3 };
    } catch (error) { report.jco = { passed: false, error: errorData(error) }; report.failures.push({ stage: 'jco-runtime', ...errorData(error) }); }
    report.stage = 'wasmtime'; await save();
    const host = await realpath(process.env.NODE_COMPAT_WASMTIME); report.wasmtimeBinary = await descriptor(host);
    const version = await runOwnedCommand({ output, name: 'wasmtime-version', executable: host, args: ['--version'], write: writeFile, register: () => {}, timeoutMs: 10000 });
    await retainProcess(output, 'wasmtime-version', version); assert(version.terminalExitZeroObserved); assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
    const wt = await runOwnedCommand({ output, name: 'wasmtime-run', executable: host, args: ['run', '--invoke', 'run()', report.component.path], write: writeFile, register: () => {}, timeoutMs: 60000, maxOutputBytes: 16 * 1024 * 1024 });
    await retainProcess(output, 'wasmtime-run', wt);
    report.wasmtime = { status: wt.status, signal: wt.signal, timedOut: wt.timedOut, ownedGroupGone: wt.ownedGroupGone, passed: false };
    if (wt.terminalExitZeroObserved && wt.ownedGroupGone) {
      const value = parseScalarStringOutput({ stdoutBytes: await readFile(wt.stdoutFile.path), rawDurablyRetained: true });
      await durable(join(output, 'wasmtime.string.txt'), value); await json(join(output, 'wasmtime.parsed.json'), JSON.parse(value));
      assert.equal(value, first, 'Fresh Wasmtime whole return must match actual retained Jco return'); report.wasmtime.passed = true;
    } else report.failures.push({ stage: 'wasmtime', reason: 'Actual CLI returned failure; complete streams and terminal retained' });
    await recheck(native); report.stage = 'complete'; report.status = report.jco.passed && report.wasmtime.passed ? 'passed' : 'failed';
  } catch (error) {
    report.status = report.stage === 'bundling' ? 'refused' : 'failed'; report.reason = report.stage === 'bundling' ? 'BUNDLE_PROFILE_REFUSED' : 'OBSERVED_STAGE_FAILURE'; report.failures.push({ stage: report.stage, ...errorData(error) });
    await json(join(output, 'failure.json'), { stage: report.stage, ...errorData(error) });
  } finally {
    if (native) { try { await recheck(native); report.postNativeRecheck = true; } catch (error) { report.postNativeRecheck = false; report.status = 'failed'; report.failures.push({ stage: 'post-native-recheck', ...errorData(error) }); } }
    report.finishedAtUtc = new Date().toISOString(); await save();
    process.stdout.write(JSON.stringify({ case: name, stage: report.stage, status: report.status, output }) + '\n');
  }
}
if (process.argv[2] === '--component-child') {
  assert.equal(process.argv.length, 4);
  await componentChild(resolve(process.argv[3])).catch(error => { process.stderr.write(JSON.stringify(errorData(error)) + '\n'); process.exitCode = 1; });
} else await main();
