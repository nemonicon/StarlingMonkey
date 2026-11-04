// Host-side correctness helper for optional native foundation gates.
// This module is never bundled into a product component.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../toolchain.mjs';
import { loadComponentizer } from '../componentizer.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
import { selectedManifestsForEngine } from '../module-selection.mjs';
export const hash = value => createHash('sha256').update(value).digest('hex');

export function decodeCliString(source) {
  let normalized = '';
  for (let index = 0; index < source.length; index++) {
    const char = source[index];
    if (char !== '\\') { normalized += char; continue; }
    const next = source[++index];
    if (next === 'u' && source[index + 1] === '{') {
      const end = source.indexOf('}', index + 2), digits = source.slice(index + 2, end);
      assert(end > index && /^[0-9a-fA-F]+$/.test(digits));
      normalized += JSON.stringify(String.fromCodePoint(parseInt(digits, 16))).slice(1, -1); index = end;
    } else if (next === "'") normalized += "'";
    else normalized += next === '0' ? '\\u0000' : '\\' + next;
  }
  try { return JSON.parse(normalized); }
  catch (error) { throw new Error('Wasmtime CLI string decoding: '+error.message); }
}

export async function nativeHarness({ kind, here, enabledField, option, outputVariable }) {
  assert.equal(process.version, 'v22.14.0');
  assert(process.env.NODE_COMPAT_ENGINE && process.env.NODE_COMPAT_WASMTIME);
  assert.equal(decodeCliString('"\\u{feff}"'), '\uFEFF');
  assert.equal(decodeCliString('"\\\\u{feff}"'), '\\u{feff}');
  assert.equal(decodeCliString("\"\\'\""), "'");
  const repository = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
  const engine = resolve(process.env.NODE_COMPAT_ENGINE), sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
  const metadataBytes = await readFile(engine+'.build.json'), metadata = JSON.parse(metadataBytes);
  assert.equal(hash(await readFile(engine)), metadata.engineSha256);
  assert.equal(metadata[enabledField], true); assert.equal(metadata.observedCMakeOptions[option], 'ON');
  assert.equal(metadata.entropyPolicy, 'off'); assert.equal(metadata.debuggerEnabled, false); assert.equal(metadata.gcStress, false);
  for (const input of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, input.path))), input.sha256, input.path);
  const registrar = await readFile(join(sourceRoot, 'builtins/node-compat/register.cpp'), 'utf8');
  assert.match(registrar, /options\.setForceStrictMode\(\)/, 'Selected native registrar must preserve ESM strictness');
  const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot });
  const output = resolve(process.env[outputVariable] ?? '/tmp/starling-node-compat/native-'+kind);
  await mkdir(output, { recursive: true }); await writeFile(join(output, 'package.json'), '{"type":"module"}\n');
  const toolchain = await loadToolchain(), selected = await loadComponentizer(toolchain);
  try { await symlink(join(toolchain.directory, 'node_modules'), join(output, 'node_modules')); } catch (error) { if (error.code !== 'EEXIST') throw error; }
  const adapter = join(repository, 'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
  const adapterSha256 = hash(await readFile(adapter)); assert.equal(adapterSha256, '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
  const options = { engine, preview2Adapter: adapter,
    witWorld: `package test:native-${kind}; world test { export run: func() -> string; }`, worldName: 'test',
    disableFeatures: ['stdio', 'random', 'clocks', 'http', 'fetch-event'], selectedInterfaces: [] };
  const { transpile, componentWit } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
  async function build(name, source) {
    const { component, interfaceAudit } = await selected.componentize(source, options);
    assert.deepEqual(interfaceAudit.emittedImports, []);
    const emittedWit = await componentWit(component);
    assert.equal(emittedWit.replace(/\s+/g, ' ').trim(), 'package root:component; world root { export run: func() -> string; }');
    const componentPath = join(output, name+'.component.wasm'), sourcePath = join(output, name+'.source.mjs');
    await writeFile(componentPath, component); await writeFile(sourcePath, source);
    const { files } = await transpile(component, { name });
    for (const [name, bytes] of Object.entries(files)) { await mkdir(dirname(join(output, name)), { recursive: true }); await writeFile(join(output, name), bytes); }
    return { componentPath, modulePath: join(output, name+'.js'), componentSha256: hash(component), componentBytes: component.length,
      sourcePath, sourceSha256: hash(source), interfaceAudit, emittedWit, emittedExports: [{ name: 'run', parameters: [], result: 'string' }] };
  }
  async function bundle(input, expectedImports) {
    const lowered = await bundleProfile({ ...toolchain, builtinManifests, input });
    assert.deepEqual([...lowered.imports].sort(), [...expectedImports].sort());
    assert(lowered.moduleIds.every(id => !id.endsWith('/prototype.mjs') && !id.includes('/builtins/node-compat/')), 'No semantic facade source may be bundled');
    return lowered;
  }
  async function expectInitialization(name, source, code = /ERR_SM_NODE_UNSUPPORTED/) {
    await writeFile(join(output, name+'.init.mjs'), source); let failure;
    try { await selected.componentize(source, options); } catch (error) { failure = error; }
    assert(failure, name); assert.match(failure.message, code, name);
    return { name, source, sourceSha256: hash(source), error: failure.message };
  }
  const host = resolve(process.env.NODE_COMPAT_WASMTIME), version = spawnSync(host, ['--version'], { encoding: 'utf8' });
  assert.match(version.stdout, /^wasmtime 42\.0\.1\b/);
  const hostMetadata = { version: version.stdout.trim(), path: host, sha256: hash(await readFile(host)) };
  function runHost(fixture) {
    const result = spawnSync(host, ['run', '--invoke', 'run()', fixture.componentPath], { encoding: 'utf8', timeout: 120000, maxBuffer: 4*1024*1024 });
    assert.equal(result.status, 0, result.error?.message ?? result.stderr);
    return { ...hostMetadata, stdoutSha256: hash(result.stdout), stdoutBytes: Buffer.byteLength(result.stdout), stderr: result.stderr,
      observed: JSON.parse(decodeCliString(result.stdout.trim())) };
  }
  async function offAdmission(engineVariable, sourceVariable, input) {
    if (!process.env[engineVariable]) return null;
    const offEngine = resolve(process.env[engineVariable]), offMetadataBytes = await readFile(offEngine+'.build.json'), offMetadata = JSON.parse(offMetadataBytes);
    assert.equal(hash(await readFile(offEngine)), offMetadata.engineSha256); assert.notEqual(offMetadata[enabledField], true);
    const offRoot = resolve(process.env[sourceVariable] ?? sourceRoot);
    for (const item of offMetadata.sourceManifest) assert.equal(hash(await readFile(join(offRoot, item.path))), item.sha256, item.path);
    const offManifests = selectedManifestsForEngine(offMetadata, { sourceRoot: offRoot }); let failure;
    try { await bundleProfile({ ...toolchain, builtinManifests: offManifests, input }); } catch (error) { failure = error; }
    assert(failure); assert.match(failure.message, /not admitted/);
    return { engineSha256: offMetadata.engineSha256, sourceRoot: offRoot, receiptSha256: hash(offMetadataBytes), receipt: offMetadata,
      sourceFilesVerified: offMetadata.sourceManifest.length, error: failure.message, scope: 'Actual optional-OFF engine selection rejects module before packaging; no JS adapter fallback' };
  }
  function verifyOracleSources(oracle, requiredNames) {
    assert.equal(hash(registrar), oracle.registrarSha256, 'Native registrar must match strict-script oracle receipt');
    for (const name of requiredNames) {
      const expected = oracle.sources[name]; assert(expected, 'Missing source oracle '+name);
      assert.equal(metadata.sourceManifest.find(item => item.path === 'builtins/node-compat/'+name)?.sha256, expected, name+' must match native engine inputs');
    }
  }
  const evidence = { engineSha256: metadata.engineSha256, sourceRoot, sourceFilesVerified: metadata.sourceManifest.length,
    engineReceiptSha256: hash(metadataBytes), engineReceipt: metadata, componentizerProvenance: selected.provenance,
    selectedModuleManifests: metadata.selectedModuleManifests, adapter: { path: adapter, sha256: adapterSha256 },
    host: hostMetadata, harnessSha256: hash(await readFile(fileURLToPath(import.meta.url))) };
  return { metadata, output, builtinManifests, build, bundle, expectInitialization, runHost, offAdmission, verifyOracleSources, evidence,
    importFixture: fixture => import(pathToFileURL(fixture.modulePath)),
    writeReport: async report => { await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2)+'\n'); await writeFile(join(here, 'native-component-results.json'), JSON.stringify(report, null, 2)+'\n'); } };
}
