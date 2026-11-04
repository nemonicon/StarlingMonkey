// Host admission/null-state tests only. No artifacts, Python verification or tools.
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {selectPin,diagnosticPreflight} from './runtime-preflight.mjs';
import {classify,contract,rawBuiltinManifests} from './metadata-admission.mjs';
import {pathToFileURL} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url));
assert.equal(process.argv.length,4,'READ_ONLY_CORRECTED_SOURCE_ROOT FRESH_TEST_OUTPUT');
const sourceRoot=resolve(process.argv[2]),output=resolve(process.argv[3]);assert(output.startsWith('/tmp/starling-node-compat/'));
await (await import('node:fs/promises')).mkdir(output,{recursive:false});
const selectorPath=join(sourceRoot,'tests/node-compat/module-selection.mjs'),admissionPath=join(sourceRoot,'tests/node-compat/classic-streams-admission.mjs');
assert.equal(createHash('sha256').update(await readFile(selectorPath)).digest('hex'),'57968dc834e9f9efa90e8e26eb1ace60dff182b816f33e36fea15e1fee22ef85');
assert.equal(createHash('sha256').update(await readFile(admissionPath)).digest('hex'),'46acb447c5e2acc6f33d94d3d21e90c1495a8da2d593e08b0f3c21e84e738d24');
const {selectedManifestsForEngine}=await import(pathToFileURL(selectorPath));
const cases=[];
async function check(name,fn){await fn();cases.push(name);}
const select=document=>selectPin(document,{variant:'benchmark-classic-on',recipeSha256:contract.recipeSha256});
await check('checked-in null pins reject before Python/artifact/tool access',async()=>assert.rejects(diagnosticPreflight(),/Null\/unreviewed/));
for(const [name,value]of [['null',null],['unconfigured',{schemaVersion:1,state:'UNCONFIGURED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'}],
 ['unreviewed exporter',{schemaVersion:1,state:'UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V3'}],
 ['reviewed outer with null variant',{schemaVersion:1,state:'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3',variants:{'benchmark-classic-on':null}}]]){
 await check(name+' pin document refused',async()=>assert.throws(()=>select(value)));
}
await check('old reviewed v2 outer authority refused',async()=>assert.throws(()=>select({schemaVersion:1,state:'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2',variants:{}})));
await check('authority digest fails before malformed JSON parse',async()=>{
 const path=join(output,'owned-malformed.json');await writeFile(path,'{broken');
 await assert.rejects(diagnosticPreflight({reviewedPinsPath:path,reviewedPinsSha256:createHash('sha256').update('prior').digest('hex')}),/AssertionError/);
});
await check('installed production selector rejects diagnostic classic ON before engine fields',async()=>assert.throws(()=>selectedManifestsForEngine({profileEnabled:true,diagnosticOnly:true,classicStreamsEnabled:true}),/Diagnostic engines are never classic production/));
await check('installed production selector rejects diagnostic classic OFF before engine fields',async()=>assert.throws(()=>selectedManifestsForEngine({profileEnabled:true,diagnosticOnly:true,classicStreamsEnabled:false}),/Diagnostic engines are never classic production/));
const actual=JSON.parse(await readFile('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/normal-off.engine.wasm.build.json'));
await check('actual old production metadata refused before artifact use',async()=>assert.throws(()=>classify(actual,'benchmark-classic-on')));
for(const value of [{diagnosticOnly:true,buildRecipeSha256:contract.parentRecipeSha256},{diagnosticOnly:true,syntheticMetadataOnly:true,buildRecipeSha256:contract.recipeSha256},null]){
 await check('malformed/old diagnostic shape refused '+cases.length,async()=>assert.throws(()=>classify(value,'benchmark-classic-on')));
}
const before=await readFile(join(here,'reviewed-pins.json'));
await check('source tests leave null pin bytes unchanged',async()=>assert.deepEqual(await readFile(join(here,'reviewed-pins.json')),before));
// This model contains declaration data only, never engine paths/hashes/pins.
const model=Object.fromEntries(['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled'].map(key=>[key,true]));
Object.assign(model,{diagnosticOnly:true,buildRecipeSha256:contract.recipeSha256,entropyPolicy:'off',classicStreamsEnabled:true,
 classicTraceSourcePolicy:structuredClone(contract.classicTraceSourcePolicy),gcStress:false,oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false,sourceManifest:JSON.parse(await readFile(join(here,'policy.json'))).expectedNativeSourceManifest,selectedModuleManifests:actual.selectedModuleManifests,
 classicBenchmarkDiagnosticPolicy:{version:contract.diagnosticVersion,moduleId:contract.moduleId,exports:contract.exports,addonSources:contract.addonSources,
  nativeInputs:342,addonInputs:2,totalDeclaredNativeAndBuildInputs:344,externalEmbeddingInputs:3}});
await check('source-only ON declaration model selects nine exact native manifests',async()=>{const manifests=await rawBuiltinManifests(model,'benchmark-classic-on',sourceRoot);assert.equal(manifests.length,9);assert(manifests.some(row=>Object.hasOwn(row.modules,'node:stream')));});
await check('source-only OFF declaration model omits classic native module IDs',async()=>{const value=structuredClone(model);value.classicStreamsEnabled=false;value.selectedModuleManifests=value.selectedModuleManifests.slice(0,-1);const manifests=await rawBuiltinManifests(value,'benchmark-classic-off',sourceRoot);assert.equal(manifests.length,8);assert(!manifests.some(row=>Object.hasOwn(row.modules,'node:stream')));});
await check('duplicate source inventory refused before native declaration use',async()=>{const value=structuredClone(model);value.sourceManifest[0]=value.sourceManifest[1];await assert.rejects(rawBuiltinManifests(value,'benchmark-classic-on',sourceRoot));});
await check('extra selected manifest declaration refused',async()=>{const value=structuredClone(model);value.selectedModuleManifests.push(value.selectedModuleManifests[0]);await assert.rejects(rawBuiltinManifests(value,'benchmark-classic-on',sourceRoot));});
await check('manifest source hash substitution refused',async()=>{const value=structuredClone(model);value.selectedModuleManifests[0].sha256='0'.repeat(64);await assert.rejects(rawBuiltinManifests(value,'benchmark-classic-on',sourceRoot));});
await check('manifest profile version substitution refused',async()=>{const value=structuredClone(model);value.selectedModuleManifests[0].profileVersion='fabricated';await assert.rejects(rawBuiltinManifests(value,'benchmark-classic-on',sourceRoot));});
await check('original old342 source checkout refused as corrected declarations',async()=>assert.rejects(rawBuiltinManifests(model,'benchmark-classic-on',resolve(here,'../../../..'))));
await check('old source manifest cannot be projected behind new trace policy',async()=>{const value=structuredClone(model);value.sourceManifest=actual.sourceManifest;await assert.rejects(rawBuiltinManifests(value,'benchmark-classic-on',sourceRoot));});
await check('trace provenance missing in declaration shape refused',async()=>{const value=structuredClone(model);delete value.classicTraceSourcePolicy;assert.throws(()=>classify(value,'benchmark-classic-on'));});
const result={schemaVersion:1,state:'NULL_PIN_AND_PRODUCTION_DIAGNOSTIC_REFUSAL_TESTS_PASSED',passed:cases.length,cases,output,
  declarationModelsContainNoEnginePins:true,positiveDeclarationModelsAreNotArtifactAdmission:true,
  engineBytesRead:false,pythonVerifierInvoked:false,toolchainOrPackagerLoaded:false,configureCompilerGuestOrTargetHostInvoked:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
