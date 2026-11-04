// Audited packaging entry point. Native engine selection remains independent.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, realpath } from 'node:fs/promises';
import { dirname, join, resolve, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { selectedInterfacePolicy, auditSelectedInterfaces } from './capability-policy.mjs';

const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const here = dirname(fileURLToPath(import.meta.url));
export const IMPORT_I32_PATCH = Object.freeze({
  id: 'sm-import-i32.v1',
  baseRevision: '4d812f5a7b524cea5bcfd565cac55f3fab876a57',
  sha256: 'd300e345cb56a5bb1560f1f993c2cc763bca273e6bcf51e38aadc8e27d84782c',
  patchedSourceSha256: 'f54d9d7562c525131def2a89d512883118d3c7a6af29a1e1021dfec76c31a048',
  lockSha256: '6472e3cd45eeaacdd5f7133e8eaab8e4411ef77272812d97dd6ac729462f6ffd',
});
export const PATCHED_COMPONENTIZER_PINS = Object.freeze({
  'src/componentize.js': 'e58ef4f3b126f4a3fd07c61b368930bbf02dd0029f0f03e4c6928528e994e559',
  'src/platform.js': '7a510717aae2a99b24b95aa80f3f40288a9ca6b1bc77129d833ebd67f62e1370',
  'package.json': '62deec3b3c95aec1d87352f50022f1232823779f5e5fa45b01a380345f038559',
  'lib/spidermonkey-embedding-splicer.js': 'a4aceb62d760ca39eb6c8abfb4e4e4cc0c2abafb302a162f8a08b8a71699ae37',
  'lib/spidermonkey-embedding-splicer.core.wasm': '5029939694148ea66c72fe5a8f7f5db406b473cde1f2eda8964fd005254a6cdb',
  'lib/spidermonkey-embedding-splicer.core2.wasm': '30fff64b635b191d59e59b6b2aadf117f3e4c6326db35111f69a19ea1bd42a4e',
});
export const CLOCK_ERRNO_PATCH = Object.freeze({
  id: 'sm-clock-errno.v1',
  sha256: '57ace551f7d723cbf9faa41c42eda08feace9370f571175284e36c67d4c24da3',
  patchedSourceSha256: 'a8bd26e5ab6edba7a83dcf8642e2c591c1465f92f0bf3f0c8eda15a99c3da2d8',
});
// Exact isolated v2 build artifacts; regression evidence is recorded separately.
const clockV2Pins = Object.freeze({ ...PATCHED_COMPONENTIZER_PINS,
  'lib/spidermonkey-embedding-splicer.core.wasm': 'edad4a6f77dfc307a42096bb90d2b7c8c37c893e7fb2325d785cf0d50fa52214',
});
export const DEBUG_SCALAR_OOM_DIAGNOSTIC = Object.freeze({
  id: 'sm-debug-scalar-oom-v1',
  worldSha256: '2384f23573d9f9264940b5f2e574ca06d43ad3a43587beb53f2fc308cd3ebb84',
  worldName: 'profile',
  emittedWorld: 'package root:component; world root { export run: func() -> s32; }',
});
const RELEASED_ENGINE_SHA256 = '6094cd93d966f9bec9b01332db6e0eedbaf22f60b745c9f823f21e33cbd4d365';
const LEGACY_RELEASE_ENGINE_PINS = Object.freeze({
  [RELEASED_ENGINE_SHA256]: 'componentize-js-0.23.0-released-broken-control',
  '3f5bf602ad2d1507db5c1bcd5b938984aba9ca65af4c5a840b5bf8fcd09d370f': '188-source-release-held-constant-import-i32-control',
});
const stockPins = Object.freeze({
  'src/componentize.js': PATCHED_COMPONENTIZER_PINS['src/componentize.js'],
  'src/platform.js': PATCHED_COMPONENTIZER_PINS['src/platform.js'],
  'package.json': PATCHED_COMPONENTIZER_PINS['package.json'],
  'lib/spidermonkey-embedding-splicer.js': '075b7e63ca2c8d9337b9a05c3aebe392c22b11ebcadbef0292f8251814c91e7d',
  'lib/spidermonkey-embedding-splicer.core.wasm': '6190193dbfefc48afa9ff191af442e27c59741a4a2b62681b4c4943a8fa7c055',
  'lib/spidermonkey-embedding-splicer.core2.wasm': '364466ad6cb6eb27aa2e6f38a15f6a986b50f0d964aa7bb838e2bb3a1259e4c2',
});

export function getComponentizerPins(provenance) {
  assert.equal(provenance.patch?.sha256, IMPORT_I32_PATCH.sha256);
  if (provenance.selection === 'patched-import-i32-v1') {
    assert.equal(provenance.additionalPatches?.length ?? 0,0,'Unknown additional patches in v1 provenance');
    return PATCHED_COMPONENTIZER_PINS;
  }
  assert.equal(provenance.selection, 'patched-import-i32-clock-v2');
  assert.equal(provenance.additionalPatches?.length, 1);
  assert.equal(provenance.additionalPatches[0].sha256, CLOCK_ERRNO_PATCH.sha256);
  assert(clockV2Pins, 'Clock-v2 artifact pins are not published');
  return clockV2Pins;
}

/** toolchain is the object returned by loadToolchain(). Stock is diagnostic only. */
export async function loadComponentizer(toolchain, { legacyDiagnostic = false, debugScalarOOMDiagnostic = false } = {}) {
  const requested = process.env.NODE_COMPAT_COMPONENTIZE_MODULE;
  const stock = !requested;
  assert(!stock || legacyDiagnostic || process.env.NODE_COMPAT_LEGACY_COMPONENTIZER === '1',
    'Select NODE_COMPAT_COMPONENTIZE_MODULE from abi-fix/build-splicer.sh; stock packaging requires explicit legacyDiagnostic');
  const modulePath = await realpath(resolve(requested ?? join(toolchain.directory, 'node_modules/@bytecodealliance/componentize-js/src/componentize.js')));
  const directory = dirname(dirname(modulePath));
  assert.equal(relative(directory, modulePath), join('src', 'componentize.js'));
  let manifest;
  let manifestSha256;
  let selection = stock ? 'stock-legacy-diagnostic' : 'patched-import-i32-v1';
  let selectedPins = stock ? stockPins : PATCHED_COMPONENTIZER_PINS;
  if (!stock) {
    const bytes = await readFile(join(directory, 'splicer-build.json'));
    manifestSha256 = digest(bytes); manifest = JSON.parse(bytes);
    assert.equal(manifest.schemaVersion, 1);
    const v2 = manifest.packagingVersion === 'componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1';
    if(v2) {
      assert.equal(manifest.additionalPatches?.length,1);
      assert.equal(manifest.additionalPatches[0].id,CLOCK_ERRNO_PATCH.id);
      assert.equal(manifest.additionalPatches[0].sha256,CLOCK_ERRNO_PATCH.sha256);
      assert.equal(manifest.additionalPatches[0].patchedSourceSha256,CLOCK_ERRNO_PATCH.patchedSourceSha256);
      assert.equal(digest(await readFile(join(here,'oom/componentize-clock-errno-v2.patch'))),CLOCK_ERRNO_PATCH.sha256);
      assert(clockV2Pins,'Clock-v2 artifact pins are not published');
      selection='patched-import-i32-clock-v2';selectedPins=clockV2Pins;
    } else {
      assert.equal(manifest.packagingVersion, 'componentize-js-0.23.0+sm-import-i32.v1');
      assert.equal(manifest.additionalPatches?.length ?? 0,0,'Unknown additional patches in v1 manifest');
    }
    assert.equal(manifest.baseRevision, IMPORT_I32_PATCH.baseRevision);
    assert.equal(manifest.basePackageVersion, '0.23.0');
    assert.equal(manifest.module, 'src/componentize.js');
    assert.equal(manifest.patch.id, IMPORT_I32_PATCH.id);
    assert.equal(manifest.patch.sha256, IMPORT_I32_PATCH.sha256);
    assert.equal(manifest.patch.patchedSourceSha256, IMPORT_I32_PATCH.patchedSourceSha256);
    assert.equal(manifest.lock.sha256, IMPORT_I32_PATCH.lockSha256);
    assert.equal(manifest.build.locked, true);
    assert.equal(manifest.build.jcoVersion, '1.40.0');
    assert.equal(digest(await readFile(join(here, 'abi-fix/componentize-import-i32-v1.patch'))), IMPORT_I32_PATCH.sha256);
    assert.equal(digest(await readFile(join(here, 'abi-fix/splicer-Cargo.v1.lock'))), IMPORT_I32_PATCH.lockSha256);
    const seen = new Set();
    for (const entry of manifest.checkedFiles) {
      assert.equal(typeof entry.path, 'string');
      assert(!entry.path.startsWith('/') && !entry.path.split(/[\\/]/).includes('..'));
      assert(!seen.has(entry.path)); seen.add(entry.path);
      assert.equal(digest(await readFile(join(directory, entry.path))), entry.sha256, `Packaging manifest mismatch: ${entry.path}`);
    }
    for (const [path, expected] of Object.entries(selectedPins)) {
      assert(seen.has(path));
      assert.equal(manifest.checkedFiles.find(entry => entry.path === path).sha256, expected);
    }
  }
  const checkedFiles = [];
  for (const [path, expected] of Object.entries(selectedPins)) {
    assert.equal(await realpath(join(directory, path)), resolve(directory, path), `Critical packaging files must reside in the audited package: ${path}`);
    assert.equal(digest(await readFile(join(directory, path))), expected, `Unrecognized packaging artifact: ${path}`);
    checkedFiles.push({ path, sha256: expected });
  }
  const pkg = JSON.parse(await readFile(join(directory, 'package.json')));
  assert.equal(pkg.version, '0.23.0');
  const loaded = await import(pathToFileURL(modulePath));
  const { splicer } = await import(pathToFileURL(join(directory, 'lib/spidermonkey-embedding-splicer.js')));
  assert.equal(typeof loaded.componentize, 'function');
  for (const method of ['spliceBindings', 'stubWasi']) assert.equal(typeof splicer[method], 'function');
  const componentize = (...args) => {
    const options = typeof args[0] === 'string' ? (typeof args[1] === 'string' ? args[2] : args[1]) : args[0];
    assert(options?.engine, 'An explicit audited native engine is required; released fallback is disabled');
    return (async () => {
      let metadata;
      try { metadata = JSON.parse(await readFile(options.engine + '.build.json')); }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
      const engineSha256 = digest(await readFile(options.engine));
      if (metadata) assert.equal(metadata.engineSha256, engineSha256, 'Engine metadata does not match its bytes');
      const interfacePolicy = selectedInterfacePolicy(metadata, options);
      // These are this repository wrapper's options, not public ComponentizeJS
      // options. Finalization runs BEFORE the actual final-interface audit.
      const { selectedInterfaces: _selected, finalizeComponent, ...publicOptions } = options;
      if (finalizeComponent !== undefined) assert.equal(typeof finalizeComponent, 'function');
      const publicArgs = [...args];
      const optionsIndex = typeof args[0] === 'string' ? (typeof args[1] === 'string' ? 2 : 1) : 0;
      publicArgs[optionsIndex] = publicOptions;
      const observedBuildType = metadata?.observedCMakeOptions?.CMAKE_BUILD_TYPE;
      let legacyEngineDiagnosticAudit = null;
      if (!metadata) {
        assert(legacyDiagnostic && engineSha256 === RELEASED_ENGINE_SHA256,
          'Audited engine metadata required; missing metadata is admitted only for the explicitly selected known released control');
        legacyEngineDiagnosticAudit = {id:LEGACY_RELEASE_ENGINE_PINS[engineSha256],engineSha256,reason:'Known released control has no custom build sidecar; explicit diagnostic only'};
      } else if (!['Release','Debug'].includes(observedBuildType)) {
        assert(legacyDiagnostic && Object.hasOwn(LEGACY_RELEASE_ENGINE_PINS,engineSha256),
          'Unambiguous observed Release/Debug configuration required; unknown configuration is refused');
        legacyEngineDiagnosticAudit = {id:LEGACY_RELEASE_ENGINE_PINS[engineSha256],engineSha256,reason:'Known historical release control predates actual CMake-option capture; explicit diagnostic only'};
      }
      const isDebug = metadata?.observedCMakeOptions?.CMAKE_BUILD_TYPE === 'Debug';
      if (isDebug || debugScalarOOMDiagnostic) {
        assert.equal(finalizeComponent, undefined, 'The fixed DEBUG scalar diagnostic cannot replace its component');
        if (!debugScalarOOMDiagnostic) {
          const error = new Error('Known unsafe unrebased DEBUG canonical memory. Only the exact admitted no-import run()->s32 allocator diagnostic may use this engine.');
          error.code = 'ERR_SM_NODE_UNREBASED_DEBUG_MEMORY';
          throw error;
        }
        assert.equal(isDebug, true, 'The scalar allocator diagnostic requires its explicit DEBUG engine');
        assert.equal(stock, false, 'The scalar allocator diagnostic requires the audited patched packager');
        assert.equal(selection, 'patched-import-i32-clock-v2', 'The scalar allocator diagnostic requires the corrected clock-errno packager');
        assert.equal(metadata.profileEnabled, true);
        assert.equal(metadata.oomTesting, true);
        assert.equal(metadata.gcStress, true);
        assert.equal(metadata.debuggerEnabled, false);
        assert.equal(metadata.wptSupportEnabled, false);
        assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_OOM_TESTING, 'ON');
        assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_GC_STRESS, 'ON');
        assert.equal(digest(await readFile(options.engine)), metadata.engineSha256);
        assert.equal(typeof options.witWorld, 'string');
        assert.equal(digest(options.witWorld), DEBUG_SCALAR_OOM_DIAGNOSTIC.worldSha256, 'Unadmitted DEBUG diagnostic world');
        assert.equal(options.worldName, DEBUG_SCALAR_OOM_DIAGNOSTIC.worldName);
        assert.equal(options.witPath, undefined);
        assert.deepEqual([...(options.disableFeatures ?? [])].sort(), ['clocks','fetch-event','http','random','stdio']);
        assert.equal(options.enableFeatures?.length ?? 0, 0);
        const result = await loaded.componentize(...publicArgs);
        const { componentWit } = await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
        const emittedWit = await componentWit(result.component);
        assert.equal(emittedWit.replace(/\s+/g,' ').trim(), DEBUG_SCALAR_OOM_DIAGNOSTIC.emittedWorld,
          'DEBUG diagnostic must emit exactly zero imports and the sole no-argument s32 run export');
        return {...result, interfaceAudit: await auditSelectedInterfaces(toolchain, result.component, interfacePolicy), debugDiagnosticAudit: {
          ...DEBUG_SCALAR_OOM_DIAGNOSTIC, engineSha256:metadata.engineSha256,
          emittedWit, emittedImports:[], emittedExports:[{name:'run',parameters:[],result:'s32'}],
          scope:'Only the fixed scalar allocator diagnostic is admitted; indirect DEBUG canonical memory remains unavailable. No assertion, allocator check or Buffer operation is bypassed.',
        }};
      }
      let result = await loaded.componentize(...publicArgs);
      if (finalizeComponent) {
        const final = await finalizeComponent(result);
        assert(final instanceof Uint8Array, 'Component finalizer must return component bytes');
        result = { ...result, component: final };
      }
      const interfaceAudit = await auditSelectedInterfaces(toolchain, result.component, interfacePolicy);
      return { ...result, interfaceAudit, ...(legacyEngineDiagnosticAudit ? { legacyEngineDiagnosticAudit } : {}) };
    })();
  };
  return { componentize, directory, splicer, provenance: {
    schemaVersion: 1, selection,
    modulePath, legacyEngineDiagnosticEnabled:legacyDiagnostic, debugScalarOOMDiagnostic:debugScalarOOMDiagnostic ? DEBUG_SCALAR_OOM_DIAGNOSTIC : null, manifestPath: stock ? null : join(directory, 'splicer-build.json'), manifestSha256,
    packagingVersion: stock ? 'componentize-js-0.23.0-npm' : manifest.packagingVersion,
    patch: stock ? null : manifest.patch, additionalPatches: stock ? [] : (manifest.additionalPatches ?? []), lock: stock ? null : manifest.lock, checkedFiles,
    build: stock ? null : manifest.build,
    scope: 'Guest packaging only; native guest engine and host executable selected separately',
  } };
}
