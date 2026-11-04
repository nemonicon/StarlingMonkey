// Host-side correctness helper for optional native foundation gates.
// This module is never bundled into a product component.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../../../../toolchain.mjs';
import { loadComponentizer } from '../../../../componentizer.mjs';
import { bundleProfile } from '../../../../profile-bundler.mjs';
import { selectedManifestsForEngine } from '../../../../module-selection.mjs';
export const hash = value => createHash('sha256').update(value).digest('hex');

// BEGIN FINITE CLASSIC REGISTRAR ORACLE ANCESTRY
export function verifyClassicRegistrarOracle({kind, oracle, requiredNames, registrar, metadata, proof}) {
  const path='builtins/node-compat/register.cpp';
  const before='19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b';
  const after='2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a';
  const documents={
    assert:{sha:'cbb3bcb3f6bc9e97b12b1a61167483ac0f949de199ae6bd0172926419f4c01a3',required:['assert.mjs','assert-strict.mjs','assert-factories.generated.h','export-manifest.assert.node-v22.14.0.json']},
    querystring:{sha:'e59e05a7cb470970d9bcce230f359cf74bf62a00b094510a2df16d4ab3f901a4',required:['querystring.mjs','querystring-factories.generated.h','export-manifest.querystring.node-v22.14.0.json']},
    util:{sha:'489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816',required:['util.mjs','util-types.mjs','util-core.mjs','util-metadata.mjs','util-unsupported.mjs','export-manifest.util.node-v22.14.0.json','generate-util-factories.mjs','util-factories.generated.h']}
  };
  assert(Object.hasOwn(documents,kind),'Only three pinned strict-script oracles have this registrar ancestry');
  const expected=documents[kind];
  assert.equal(hash(proof.oracleBytes),expected.sha,'Exact unchanged Node oracle document required');
  assert.deepEqual(oracle,JSON.parse(proof.oracleBytes),'Caller oracle differs from captured bytes');
  assert.deepEqual([...requiredNames].sort(),[...expected.required].sort(),'Exact facade-source check set required');
  assert.equal(oracle.registrarSha256,before);
  // Authenticate both policy documents and both exact native patches BEFORE
  // parsing policy rows. The Tick patch never changes register.cpp.
  assert.equal(hash(proof.tickPolicyBytes),'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0');
  assert.equal(hash(proof.tickPatchBytes),'e286ebeb3f09b438999422dbc2059fed565ef71b98d9f7f62b09291fb5eb5491');
  assert.equal(hash(proof.classicPolicyBytes),'137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f');
  assert.equal(hash(proof.classicPatchBytes),'0574b88e1126e616e4adaac2d7dea4435657c70e2d07a429531218aff24bd73c');
  const tick=JSON.parse(proof.tickPolicyBytes),classic=JSON.parse(proof.classicPolicyBytes);
  assert.equal(tick.version,'sm-private-ticks-source-v1');
  assert.equal(tick.nativePatchSha256,hash(proof.tickPatchBytes));
  assert(!Object.hasOwn(tick.sourceLayer,path),'Tick registrar must remain unchanged');
  assert.equal(classic.parentPolicySha256,hash(proof.tickPolicyBytes));
  assert.equal(classic.parentRecipeSha256,'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173');
  assert.deepEqual(classic.parentExpectedNativeSourceManifest,tick.expectedNativeSourceManifest);
  assert.equal(tick.expectedNativeSourceManifest.length,306);
  assert.equal(tick.expectedNativeSourceManifest.find(row=>row.path===path)?.sha256,before);
  assert.deepEqual(classic.sourceLayer[path],{beforeSha256:before,afterSha256:after});
  assert.equal(classic.nativePatchSha256,hash(proof.classicPatchBytes));
  assert.equal(classic.expectedNativeSourceManifest.length,342);
  assert.equal(classic.expectedNativeSourceManifest.find(row=>row.path===path)?.sha256,after);
  assert.equal(metadata.buildRecipeSha256,'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7');
  assert.notEqual(metadata.syntheticMetadataOnly,true);assert.notEqual(metadata.diagnosticOnly,true);
  assert.equal(metadata.classicStreamsEnabled,true);assert.equal(metadata.internalTicksEnabled,true);
  assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
  assert.equal(metadata.classicStreamsPolicy.policyFileSha256,hash(proof.classicPolicyBytes));
  assert.equal(metadata.classicStreamsPolicy.nativePatchSha256,hash(proof.classicPatchBytes));
  assert.equal(metadata.internalTickPolicy.parentPrivateTickPolicyFileSha256,hash(proof.tickPolicyBytes));
  assert.equal(metadata.internalTickPolicy.policyFileSha256,hash(proof.classicPolicyBytes));
  assert.equal(metadata.sourceManifest.length,342);
  const rows=metadata.sourceManifest.map(row=>({path:row.path,sha256:row.sha256}));
  assert.equal(new Set(rows.map(row=>row.path)).size,342);
  assert.deepEqual(rows,classic.expectedNativeSourceManifest,'Actual342 source manifest must match the pinned Classic afterimage');
  assert.equal(hash(registrar),after,'Captured actual registrar must be the exact342 afterimage');
  assert.match(registrar,/options\.setForceStrictMode\(\)/,'Force-strict compilation must remain');
  for(const name of requiredNames)
    assert.equal(rows.find(row=>row.path==='builtins/node-compat/'+name)?.sha256,oracle.sources[name],'Unchanged oracle facade/source '+name);
  return {version:'exact-classic342-registrar-oracle-ancestry-v1',kind,oracleSha256:expected.sha,
    oracleRegistrarSha256:before,actualRegistrarSha256:after,tickRegistrarChanged:false,
    classicPatchSha256:hash(proof.classicPatchBytes),oracleRewritten:false,metadataProjected:false};
}
// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY

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
  const repository = resolve(dirname(fileURLToPath(import.meta.url)), '../../../../../..');
  const engine = resolve(process.env.NODE_COMPAT_ENGINE), sourceRoot = resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT ?? repository);
  const metadataBytes = await readFile(engine+'.build.json'), metadata = JSON.parse(metadataBytes);
  assert.equal(hash(await readFile(engine)), metadata.engineSha256);
  assert.equal(metadata[enabledField], true); assert.equal(metadata.observedCMakeOptions[option], 'ON');
  assert.equal(metadata.entropyPolicy, 'off'); assert.equal(metadata.debuggerEnabled, false); assert.equal(metadata.gcStress, false);
  for (const input of metadata.sourceManifest) assert.equal(hash(await readFile(join(sourceRoot, input.path))), input.sha256, input.path);
  const registrar = await readFile(join(sourceRoot, 'builtins/node-compat/register.cpp'), 'utf8');
  assert.match(registrar, /options\.setForceStrictMode\(\)/, 'Selected native registrar must preserve ESM strictness');
  const builtinManifests = selectedManifestsForEngine(metadata, { sourceRoot });
  const registrarProof = {
    oracleBytes: await readFile(join(here,'native-node-results.json')),
    tickPolicyBytes: await readFile(join(repository,'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json')),
    tickPatchBytes: await readFile(join(repository,'tests/node-compat/foundation-scheduler/taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch')),
    classicPolicyBytes: await readFile(join(repository,'tests/node-compat/foundation-classic-streams/integration-candidate-v1/policy.json')),
    classicPatchBytes: await readFile(join(repository,'tests/node-compat/foundation-classic-streams/implementation-candidate-v1-allocation-order-amendment/native-integration.corrected.UNAPPLIED.patch'))
  };
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
    evidence.registrarOracleAncestry = verifyClassicRegistrarOracle({kind,oracle,requiredNames,registrar,metadata,proof:registrarProof});
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
    writeReport: async report => { await writeFile(join(output, 'results.json'), JSON.stringify(report, null, 2)+'\n'); await writeFile(join(output, 'native-component-results.json'), JSON.stringify(report, null, 2)+'\n'); } };
}
