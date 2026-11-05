// Actual finite source admission only. No engine bytes, Wasm or toolchain loads.
// Dynamic contract values are fixed by tool-pins and the packet source seal.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const contract=JSON.parse(await readFile(join(here,'../source-contract.json')));
export const RECIPE=contract.recipe.sha256;
const sourcePolicy=JSON.parse(await readFile(contract.policy.path));
assert.equal(hash(await readFile(contract.policy.path)),contract.policy.sha256);
const TOOL_PINS_SHA='523f4105a07e375d894a0d07112208b4d5a87ade49a8e2c492e95101352ae237';
export const LABELS=Object.freeze(['normal-off']);
export function classify(metadata,label){
 assert(LABELS.includes(label));assert(metadata&&typeof metadata==='object'&&!Array.isArray(metadata));
 assert(metadata.diagnosticOnly===undefined||metadata.diagnosticOnly===false,'Diagnostic receipts forbidden before engine use');
 assert(!Object.hasOwn(metadata,'internalTickDiagnosticPolicy'),'Diagnostic policy forbidden before engine use');
 assert(metadata.syntheticMetadataOnly===undefined||metadata.syntheticMetadataOnly===false,'Synthetic source models forbidden before engine use');
 assert.equal(metadata.buildRecipeSha256,RECIPE,'Current zlib355 production recipe required before engine use');
 assert.deepEqual(metadata.cryptoSecretFailureSourcePolicy,sourcePolicy.cryptoSecretFailureSourcePolicy,'Exact new secret-failure source policy');
 assert.deepEqual(metadata.cryptoKeyOwnershipPolicy,sourcePolicy.cryptoKeyOwnershipSourcePolicy,'Exact inherited ownership ancestry');
 const options={gcStress:label==='gc-off',entropyPolicy:label==='normal-runtime'?'runtime-only':'off',classicStreamsEnabled:true,zlibEnabled:true,streamConsumersEnabled:label!=='disabled-off'};
 for(const[field,value]of Object.entries(options))assert.equal(metadata[field],value,field);
 for(const field of ['profileEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled'])assert.equal(metadata[field],true,field);
 for(const field of ['oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[field],false,field);
 assert.deepEqual(metadata.classicTraceSourcePolicy,sourcePolicy.classicTraceSourcePolicy,'Corrected source provenance required before engine use');
 return Object.freeze(options);
}
async function regularBelow(root,relative,sha,bytes){
 assert(typeof relative==='string'&&!relative.includes('\0')&&!relative.includes('\\')&&relative.split('/').every(part=>part&&part!=='.'&&part!=='..'));
 assert(!relative.startsWith('/'));assert((await lstat(root)).isDirectory()&&!(await lstat(root)).isSymbolicLink());
 let path=root;for(const part of relative.split('/')){path=join(path,part);assert(!(await lstat(path)).isSymbolicLink(),path);}
 assert((await lstat(path)).isFile());const data=await readFile(path);assert.equal(hash(data),sha,path);assert.equal(data.length,bytes,path);return data;
}
export async function admit(metadata,label,sourceRoot){
 const options=classify(metadata,label);sourceRoot=resolve(sourceRoot);assert.equal(sourceRoot,contract.configuredSourceRoot,'Exact real configured source context');
 const toolBytes=await readFile(join(here,'tool-pins.json'));assert.equal(hash(toolBytes),TOOL_PINS_SHA);
 const tools=JSON.parse(toolBytes);assert.equal(tools.recipeSha256,RECIPE);assert.equal(tools.nativeSources,355);assert.equal(tools.reviewedEnginePins,null);
 for(const row of tools.toolDependencies)await regularBelow(sourceRoot,row.path,row.sha256,row.bytes);
 const policyBytes=await readFile(contract.policy.path);assert.equal(hash(policyBytes),contract.policy.sha256);
 const policy=JSON.parse(policyBytes);
 const parentPins=JSON.parse(await readFile(join(sourceRoot,'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json')));
 // Imports use actual installed finite code only after its exact source hash and
 // complete tool-dependency graph above have passed. No 306-to355 projection.
 const {validateCryptoSecretFailureBuildSourceAdmission}=await import(pathToFileURL(contract.buildAdmission.path));
 const classic=validateCryptoSecretFailureBuildSourceAdmission(metadata,{sourceRoot,
  parentProtectedSources:parentPins.parentProtected.sourceSha256,parentProtectedPatch:parentPins.parentProtected.patchSha256});
 assert.equal(classic.streamConsumersEnabled,options.streamConsumersEnabled);assert.equal(classic.zlibEnabled,options.zlibEnabled);assert.equal(classic.sourceInputs,355);assert.equal(classic.classicStreamsEnabled,options.classicStreamsEnabled);
 const {selectBuildManifests}=await import('./build-manifests.mjs');
 const {manifests,core}=await selectBuildManifests(metadata,{sourceRoot,buildAdmission:classic});
 const ids=manifests.flatMap(value=>Object.keys(value.modules));
 assert.equal(ids.includes('node:zlib'),options.zlibEnabled);
 assert.equal(ids.includes('node:stream/consumers'),options.streamConsumersEnabled);
 assert.equal(ids.includes('node:stream'),options.classicStreamsEnabled);assert.equal(ids.includes('node:stream/promises'),options.classicStreamsEnabled);
 // Core source expectations are checked directly; normal production admission stays closed.
 assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
 assert.equal(metadata.componentizeSourceManifest.length,3);
 assert.equal(metadata.componentizeSourceManifest.find(row=>row.path==='embedding/embedding.cpp')?.sha256,policy.embedding.afterSha256);
 return{state:'ACTUAL_FINITE_SECRET_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION_V1',label,options,sourceRoot,
  sourceFiles:355,externalSources:metadata.componentizeSourceManifest,selectedManifestCount:manifests.length,selectedManifestPaths:metadata.selectedModuleManifests.map(row=>row.path),coreExpectations:core,
  classicSourceAdmission:classic,policySha256:hash(policyBytes),toolPinsSha256:hash(toolBytes),toolDependenciesVerified:tools.toolDependencies.length,
  validationBootstrapOnly:true,operationalAdmission:false,selectorSourceSha256:hash(await readFile(join(sourceRoot,'tests/node-compat/module-selection.mjs'))),
  admissionSourceSha256:hash(await readFile(contract.buildAdmission.path)),engineBytesRead:false,guestExecuted:false};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 assert.equal(process.argv.length,5);const metadata=JSON.parse(await readFile(process.argv[2]));
 console.log(JSON.stringify(await admit(metadata,process.argv[3],resolve(process.argv[4]))));
}
