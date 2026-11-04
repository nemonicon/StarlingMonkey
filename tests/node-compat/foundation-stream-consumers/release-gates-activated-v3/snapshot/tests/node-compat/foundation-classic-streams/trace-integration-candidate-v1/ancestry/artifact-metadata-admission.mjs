// Actual finite source admission only. No engine bytes, Wasm or toolchain loads.
// Dynamic contract values are fixed by tool-pins and the packet source seal.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const contract=JSON.parse(await readFile(join(here,'../admission-pins.json')));
export const RECIPE=contract.productionRecipeSha256;
const TOOL_PINS_SHA='f68267eff5126af83c099346d07e5befbf6261ed4ca245e14a68f292f32087e3';
export const LABELS=Object.freeze(['normal-off','normal-runtime','gc-off','disabled-off']);
export function classify(metadata,label){
 assert(LABELS.includes(label));assert(metadata&&typeof metadata==='object'&&!Array.isArray(metadata));
 assert(metadata.diagnosticOnly===undefined||metadata.diagnosticOnly===false,'Diagnostic receipts forbidden before engine use');
 assert(!Object.hasOwn(metadata,'internalTickDiagnosticPolicy'),'Diagnostic policy forbidden before engine use');
 assert(metadata.syntheticMetadataOnly===undefined||metadata.syntheticMetadataOnly===false,'Synthetic source models forbidden before engine use');
 assert.equal(metadata.buildRecipeSha256,RECIPE,'Current classic342 production recipe required before engine use');
 const options={gcStress:label==='gc-off',entropyPolicy:label==='normal-runtime'?'runtime-only':'off',classicStreamsEnabled:label!=='disabled-off'};
 for(const[field,value]of Object.entries(options))assert.equal(metadata[field],value,field);
 for(const field of ['profileEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled'])assert.equal(metadata[field],true,field);
 for(const field of ['oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[field],false,field);
 return Object.freeze(options);
}
async function regularBelow(root,relative,sha,bytes){
 assert(typeof relative==='string'&&!relative.includes('\0')&&!relative.includes('\\')&&relative.split('/').every(part=>part&&part!=='.'&&part!=='..'));
 assert(!relative.startsWith('/'));assert((await lstat(root)).isDirectory()&&!(await lstat(root)).isSymbolicLink());
 let path=root;for(const part of relative.split('/')){path=join(path,part);assert(!(await lstat(path)).isSymbolicLink(),path);}
 assert((await lstat(path)).isFile());const data=await readFile(path);assert.equal(hash(data),sha,path);assert.equal(data.length,bytes,path);return data;
}
export async function admit(metadata,label,sourceRoot){
 const options=classify(metadata,label);sourceRoot=resolve(sourceRoot);
 const toolBytes=await readFile(join(here,'tool-pins.json'));assert.equal(hash(toolBytes),TOOL_PINS_SHA);
 const tools=JSON.parse(toolBytes);assert.equal(tools.recipeSha256,RECIPE);assert.equal(tools.nativeSources,342);assert.equal(tools.reviewedEnginePins,null);
 for(const row of tools.toolDependencies)await regularBelow(sourceRoot,row.path,row.sha256,row.bytes);
 const policyBytes=await readFile(join(here,'../policy.json'));assert.equal(hash(policyBytes),contract.policySha256);
 const policy=JSON.parse(policyBytes);
 const parentPins=JSON.parse(await readFile(join(sourceRoot,'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json')));
 // Imports use actual installed finite code only after its exact source hash and
 // complete tool-dependency graph above have passed. No 306-to342 projection.
 const {validateClassicSourceAdmission}=await import(pathToFileURL(join(sourceRoot,'tests/node-compat/classic-streams-admission.mjs')));
 const classic=validateClassicSourceAdmission(metadata,{sourceRoot,
  parentProtectedSources:parentPins.parentProtected.sourceSha256,parentProtectedPatch:parentPins.parentProtected.patchSha256});
 assert.equal(classic.sourceInputs,342);assert.equal(classic.classicStreamsEnabled,options.classicStreamsEnabled);
 const {selectedManifestsForEngine}=await import(pathToFileURL(join(sourceRoot,'tests/node-compat/module-selection.mjs')));
 const manifests=selectedManifestsForEngine(metadata,{sourceRoot});
 const ids=manifests.flatMap(value=>Object.keys(value.modules));
 assert.equal(ids.includes('node:stream'),options.classicStreamsEnabled);assert.equal(ids.includes('node:stream/promises'),options.classicStreamsEnabled);
 const {selectCoreExpectations}=await import(pathToFileURL(join(sourceRoot,'tests/node-compat/core-expectations.mjs')));
 const core=selectCoreExpectations(metadata,{sourceRoot});assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
 assert.equal(metadata.componentizeSourceManifest.length,3);
 assert.equal(metadata.componentizeSourceManifest.find(row=>row.path==='embedding/embedding.cpp')?.sha256,policy.embedding.afterSha256);
 return{state:'ACTUAL_FINITE_CLASSIC_SOURCE_SELECTOR_PASSED_NO_ENGINE_EXECUTION',label,options,sourceRoot,
  sourceFiles:342,externalSources:metadata.componentizeSourceManifest,selectedManifestCount:manifests.length,coreExpectations:core,
  classicSourceAdmission:classic,policySha256:hash(policyBytes),toolPinsSha256:hash(toolBytes),toolDependenciesVerified:tools.toolDependencies.length,
  selectorSourceSha256:hash(await readFile(join(sourceRoot,'tests/node-compat/module-selection.mjs'))),
  admissionSourceSha256:hash(await readFile(join(sourceRoot,'tests/node-compat/classic-streams-admission.mjs'))),engineBytesRead:false,guestExecuted:false};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 assert.equal(process.argv.length,5);const metadata=JSON.parse(await readFile(process.argv[2]));
 console.log(JSON.stringify(await admit(metadata,process.argv[3],resolve(process.argv[4]))));
}
