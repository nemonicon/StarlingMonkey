import {selectedManifestsForValidation} from "../../../../../../native-preflight.mjs";
// PREPARED/UNEXECUTED. Both runners call this BEFORE componentization or any
// invalid native receiver fixture. No old engine admission or bypass exists.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,join} from 'node:path';

const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function nativePreflight({streamWebEnabled,entropyPolicy}){
  assert.equal(process.version,'v22.14.0');
  assert.equal(typeof streamWebEnabled,'boolean');
  assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT&&process.env.NODE_COMPAT_WASMTIME,
    'Explicit future corrected engine, frozen source root and stock Wasmtime42 required');
  const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
  const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME),metadata=JSON.parse(await readFile(engine+'.build.json'));
  const contract=JSON.parse(await readFile(new URL('../../../foundation-stream-web/production-candidate/native-preflight-contract.json',import.meta.url)));
  assert.equal(hash(await readFile(engine)),metadata.engineSha256);
  assert.equal(metadata.profileEnabled,true);
  assert.equal(metadata[contract.metadataField],streamWebEnabled,'Actual optional module selection must be explicit');
  assert.equal(metadata.observedCMakeOptions?.[contract.cmakeOption],streamWebEnabled?'ON':'OFF');
  assert.equal(metadata.observedCMakeOptions?.CMAKE_BUILD_TYPE,'Release','Only ordinary Release string ABI is admitted');
  assert.equal(metadata.oomTesting,false,'No allocation-fault instrumented engine');
  assert(['off','runtime-only'].includes(entropyPolicy));assert.equal(metadata.entropyPolicy,entropyPolicy,'Explicit fixed capability variant required');
  assert(Array.isArray(metadata.sourceManifest));
  const inputs=new Map();
  for(const entry of metadata.sourceManifest){assert(!inputs.has(entry.path),'Duplicate native input path');inputs.set(entry.path,entry.sha256);
    assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);}
  async function pinned(path,expected){assert.equal(inputs.get(path),expected,'Corrected source not compiled into receipt: '+path);
    assert.equal(hash(await readFile(join(sourceRoot,path))),expected,path);}
  // These exact corrected class/slot guards are mandatory even when testing
  // module OFF. No old prototype entry is ever reached by these runners.
  for(const entry of contract.nativeGuardSources)await pinned(entry.path,entry.sha256);
  await pinned(contract.decoderSource.path,contract.decoderSource.sha256);
  let builtinManifests;
  if(streamWebEnabled){
    await pinned(contract.kernelPath,contract.kernelSha256);
    await pinned(contract.manifestPath,contract.manifestSha256);
    const header=await readFile(join(sourceRoot,contract.headerPath),'utf8');
    assert.equal(hash(header),inputs.get(contract.headerPath),'Generated header must be an actual native input');
    const marker='R"SM_NODE_PROFILE(',start=header.indexOf(marker)+marker.length,end=header.lastIndexOf(')SM_NODE_PROFILE";');
    assert(start>=marker.length&&end>start,'Expected finite generated factory literal');
    assert.equal(hash(header.slice(start,end)),contract.factoryLiteralSha256,'Installed factory changed from reviewed candidate');
    const helper=await readFile(join(sourceRoot,contract.strictFactoryHelperPath),'utf8');
    assert.equal(hash(helper),inputs.get(contract.strictFactoryHelperPath));assert(helper.includes(contract.strictFactoryRequiredSymbol));
    // This intentionally depends on future shared admission support. Current
    // module-selection does not yet admit streamWebEnabled and must reject it.
    builtinManifests=selectedManifestsForValidation(metadata,{sourceRoot});
    const selected=builtinManifests.find(manifest=>Object.hasOwn(manifest.modules,'node:stream/web'));
    assert(selected,'Installed stream/web manifest must be admitted by shared selection');
    assert.equal(selected.profileVersion,contract.profileVersion);
    assert.deepEqual(selected.modules['node:stream/web'].aliases,['stream/web']);
    assert.equal(selected.modules['node:stream/web'].exports.length,18);assert.deepEqual(selected.requiredHostInterfaces,[]);
  }
  if(!streamWebEnabled){builtinManifests=selectedManifestsForValidation(metadata,{sourceRoot});
    assert(!builtinManifests.some(manifest=>Object.hasOwn(manifest.modules,'node:stream/web')),'OFF control must not admit the module');}
  return{engine,sourceRoot,wasmtime,metadata,contract,builtinManifests,hash,
    safetyAudit:{state:'preflight-verified-before-fixture',streamWebEnabled,nativeGuardSources:contract.nativeGuardSources,
      decoderSource:contract.decoderSource,rawMemory:false,faultInjection:false,oldEngineBypass:false}};
}
