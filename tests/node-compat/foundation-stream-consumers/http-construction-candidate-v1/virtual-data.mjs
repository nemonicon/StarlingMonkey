// Host-side fixture DATA/oracle construction derived byte-exact from accepted HTTP runner.
// No node oracle scripts, guest APIs or componentizer are invoked by this function.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {hash} from './authority.mjs';
export async function buildVirtualData(frame,platform,paths){
 const {coreExpectationsForGuest,makeOracleCorpus}=platform;
 const engineMetadata=frame.metadata,engineSourceRoot=frame.sourceRoot,coreExpectations=frame.coreExpectations,builtinManifests=frame.selectedManifests;
 const here=join(paths.packagingRoot,'tests/node-compat/wasmcloud'),httpEntry=paths.baselineEntry;
 const sourcePaths=new Set(engineMetadata.sourceManifest.map(entry=>entry.path));
 const entropyPolicy='runtime-only',protectedAbortFoundationsFixture=true,streamWebFoundationsFixture=true,utilFoundationsFixture=true,expandedFoundationsFixture=true,foundationsIntegrationFixture=true;
 const protectedAbortAdmission=frame.report,corpus=makeOracleCorpus();let foundationOracles=null;
const virtualModules = { 'node-compat:core-expectations': `export default ${JSON.stringify(coreExpectationsForGuest(coreExpectations))};`, 'node-compat:oracle-vectors': `export default ${JSON.stringify(corpus)};`, 'node-compat:entropy-policy': `export default ${JSON.stringify(entropyPolicy)};` };
if (foundationsIntegrationFixture) {
  assert.equal(engineMetadata.pathEnabled, true); assert.equal(engineMetadata.eventsEnabled, true);
  const pathDirectory = resolve(here, '../foundation-path');
  const lexical = JSON.parse(await readFile(join(pathDirectory, 'lexical-vectors.json')));
  const globs = JSON.parse(await readFile(join(pathDirectory, 'glob-vectors.json')));
  const globReport = JSON.parse(await readFile(join(pathDirectory, 'glob-results.json')));
  const pathManifest = builtinManifests.find(manifest => Object.hasOwn(manifest.modules, 'node:path'));
  const pathCorpus = { lexical, globs, denied: globReport.denied, acceptedAdversarial: globReport.acceptedAdversarial,
    exportNames: [...pathManifest.modules['node:path'].exports].sort() };
  const eventsOracle = JSON.parse(await readFile(resolve(here, '../foundation-events/native-node-results.json')));
  assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/node-compat/events.mjs')?.sha256, eventsOracle.facadeSha256);
  virtualModules['node-compat:path-oracles'] = `export default ${JSON.stringify(pathCorpus)};`;
  foundationOracles = { path: { lexical: lexical.length, globs: globs.length, budgets: pathCorpus.denied.length,
    acceptedAdversarial: pathCorpus.acceptedAdversarial.length, corpusSha256: hash(JSON.stringify(pathCorpus)) },
    events: { cases: eventsOracle.cases.length, nativeCases: eventsOracle.nativeCases.length, profile: eventsOracle.profile, facadeSha256: eventsOracle.facadeSha256 },
    dynamicBareAliases: ['buffer', 'child_process', 'path', 'path/posix', 'path/win32', 'events'],
    fixtureSha256: hash(await readFile(httpEntry)) };
  if (expandedFoundationsFixture) {
    for (const field of ['stringDecoderEnabled', 'assertEnabled', 'querystringEnabled']) assert.equal(engineMetadata[field], true);
    assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/web/text-codec/text-decoder.cpp')?.sha256,
      '4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c');
    const decoderCorpus = JSON.parse(await readFile(resolve(here, '../foundation-string-decoder/component-corpus.json')));
    virtualModules['node-compat:string-decoder-oracles'] = `export default ${JSON.stringify(decoderCorpus)};`;
    const readOracle = async name => JSON.parse(await readFile(resolve(here, '../foundation-'+name+'/native-node-results.json')));
    const assertOracle = await readOracle('assert'), querystringOracle = await readOracle('querystring');
    for (const oracle of [assertOracle, querystringOracle]) for (const [name, sha256] of Object.entries(oracle.sources)) {
      if (sourcePaths.has('builtins/node-compat/'+name)) assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/node-compat/'+name)?.sha256, sha256);
    }
    foundationOracles.stringDecoder = { sequences: decoderCorpus.sequences.length,
      writes: decoderCorpus.sequences.reduce((sum, value) => sum+value.chunks.length, 0), genericCases: decoderCorpus.decoderCases.length,
      preservedOrderingDeviations: decoderCorpus.deviations.length, corpusSha256: hash(JSON.stringify(decoderCorpus)) };
    foundationOracles.assert = { cases: assertOracle.cases, profile: assertOracle.sourceProfile };
    foundationOracles.querystring = { cases: querystringOracle.cases, profile: querystringOracle.sourceProfile };
    foundationOracles.dynamicBareAliases.push('string_decoder', 'assert', 'assert/strict', 'querystring');
    if (utilFoundationsFixture) {
      assert.equal(engineMetadata.utilEnabled, true);
      const utilOracle = await readOracle('util');
      for (const [name, sha256] of Object.entries(utilOracle.sources)) {
        if (sourcePaths.has('builtins/node-compat/'+name)) assert.equal(engineMetadata.sourceManifest.find(input => input.path === 'builtins/node-compat/'+name)?.sha256, sha256);
      }
      foundationOracles.util = { variants: utilOracle.variants, expectedExports: utilOracle.expectedExports };
      foundationOracles.dynamicBareAliases.push('util', 'util/types', 'sys');
      if (streamWebFoundationsFixture) {
        assert.equal(engineMetadata.streamWebEnabled, true);
        assert.equal(engineMetadata.observedCMakeOptions.NODE_COMPAT_STREAM_WEB, 'ON');
        assert.equal(engineMetadata.observedCMakeOptions.CMAKE_BUILD_TYPE, 'Release');
        assert.equal(engineMetadata.oomTesting, false);
        const streamDirectory = resolve(here, '../foundation-stream-web');
        const contract = JSON.parse(await readFile(join(streamDirectory, 'production-candidate/native-preflight-contract.json')));
        const sourcePins = [...contract.nativeGuardSources, contract.decoderSource,
          {path:contract.kernelPath, sha256:contract.kernelSha256},
          {path:contract.manifestPath, sha256:contract.manifestSha256}];
        for (const input of sourcePins) assert.equal(engineMetadata.sourceManifest.find(entry => entry.path === input.path)?.sha256,
          input.sha256, 'Corrected installed stream/web source: '+input.path);
        const header = await readFile(join(engineSourceRoot, contract.headerPath), 'utf8');
        const marker = 'R"SM_NODE_PROFILE(', start = header.indexOf(marker) + marker.length, end = header.lastIndexOf(')SM_NODE_PROFILE";');
        assert(start >= marker.length && end > start);
        assert.equal(hash(header.slice(start,end)), contract.factoryLiteralSha256);
        const streamManifest = builtinManifests.find(manifest => Object.hasOwn(manifest.modules, 'node:stream/web'));
        assert.equal(streamManifest?.profileVersion, contract.profileVersion);
        assert.deepEqual(streamManifest.requiredHostInterfaces, []);
        const expected = {names:streamManifest.modules['node:stream/web'].exports.slice().sort()};
        for (const [key, path] of Object.entries({codecs:'candidate/codec-node-results.json',guards:'candidate/byob-node-results.json',
          views:'candidate/typed-view-node-results.json',controllers:'candidate/controller-node-results.json',
          iteration:'iteration/node-results.json',data:'dataview/node-results.json'}))
          expected[key] = JSON.parse(await readFile(join(streamDirectory,path)));
        virtualModules['node-compat:stream-web-installed-oracles'] = 'export default '+JSON.stringify(expected)+';';
        foundationOracles.streamWeb = {names:expected.names, profileVersion:contract.profileVersion,
          oracleCorpusSha256:hash(JSON.stringify(expected)), nativeSourcePins:sourcePins,
          limitations:['Fixed attached unshared BufferSources, bounded UTF-8 codecs and min1 BYOB only',
            'Explicit deferred compression; known controller signal, error-code, proxy/layout and lifecycle gaps remain']};
        foundationOracles.dynamicBareAliases.push('stream/web');
      }
    }
  }
}

if (protectedAbortFoundationsFixture) {
  const directory = resolve(here, '../foundation-add-abort/production-native-m0.10');
  const oracleBytes = await readFile(join(directory, 'node-results.json'));
  const oracle = JSON.parse(oracleBytes);
  const sources = {};
  for (const name of ['component.mjs', 'public-cases.mjs', 'require.cjs']) sources[name] = hash(await readFile(join(directory, name)));
  assert.equal(sources['public-cases.mjs'], oracle.sourceSha256);
  assert.deepEqual(oracle.passed, { public:16, nested:4, receivers:9, total:29 });
  const manifest = builtinManifests.find(value => Object.hasOwn(value.modules, 'node:events'));
  assert.equal(manifest.profileVersion, 'sm-node-22.14.0-m0.10');
  foundationOracles.protectedAbort = {
    counts: oracle.passed, publicCases:oracle.publicCases, nestedOnceCases:oracle.nestedOnceCases,
    receiverCases:oracle.receiverCases, nodeSymbol:oracle.targetSymbolInfo,
    names:manifest.modules['node:events'].exports.slice().sort(), profileVersion:manifest.profileVersion,
    oracleSha256:hash(oracleBytes), sources, admission:protectedAbortAdmission,
    scope:'29 positive/handled groups only; fatal initialized/deployed fixtures remain in the separate focused runner',
  };
}


 return{virtualModules,foundationOracles,corpus};
}
