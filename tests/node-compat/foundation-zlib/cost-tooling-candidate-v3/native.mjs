// Genuine existing350 DATA validation for a future explicit cost action only.
// No engine/native/Wasm/codec call; no old bootstrap preflight/classifier import.
import {readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {need,reviewedPair} from './authority.mjs';
import {streamHash} from './context.mjs';
const ENGINE_FACTS=Object.freeze({'normal-off':'fb16568958f4948cb78aa53818637535b88a0d87a25eb74923798fdc80cac1e6','disabled-off':'3d19535f0bbe910066b6c00aea2cdd9bbee933705429d28f3e23714c93bc2a44'});
const RECIPE='4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2';
export function classifyMetadataForCost(metadata,label){
 need(Object.hasOwn(ENGINE_FACTS,label),'Only normalON/disabledOFF comparison variants');
 need(metadata&&typeof metadata==='object'&&!Array.isArray(metadata),'Actual metadata required');
 need(metadata.diagnosticOnly!==true&&!Object.hasOwn(metadata,'internalTickDiagnosticPolicy')&&metadata.syntheticMetadataOnly!==true,'No diagnostic/synthetic projection');
 need(metadata.buildRecipeSha256===RECIPE&&metadata.engineSha256===ENGINE_FACTS[label],'Exact actual350 tuple before engine bytes');
 need(metadata.sourceManifest?.length===350&&metadata.componentizeSourceManifest?.length===3,'350 native/external3 required');
 need(metadata.hostApi==='wasi-0.2.10'&&metadata.entropyPolicy==='off'&&metadata.gcStress===false&&metadata.classicStreamsEnabled===true&&metadata.zlibEnabled===(label==='normal-off'),'Finite Release/OFF/classic/zlib options');
 for(const field of['profileEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled'])need(metadata[field]===true,'Required actual foundation '+field);
 for(const field of['oomTesting','debuggerEnabled','wptSupportEnabled'])need(metadata[field]===false,'Forbidden mode '+field);
 need(metadata.zlibPolicy?.runtimeBackendProof?.verified===false,'Do not rewrite historical metadata backend-proof field');
}
function tuple(row){return{path:row.path,sha256:row.sha256,bytes:row.bytes};}
function deepFreeze(value){if(value&&typeof value==='object'){for(const item of Object.values(value))deepFreeze(item);Object.freeze(value);}return value;}
export function freezeAdmissionValues(metadata,selected){return Object.freeze({metadata:deepFreeze(structuredClone(metadata)),selectedManifests:deepFreeze(structuredClone(selected))});}
export async function admitNativePair({authority,context,arm}){
 need(['native-on','fflate-on','fflate-off'].includes(arm),'Finite codec arm');
 await authority.recheck();await context.recheck();const pair=await reviewedPair(authority);
 const label=arm==='fflate-off'?'disabled-off':'normal-off',root=pair.data[label==='normal-off'?'nativeOn':'nativeOff'];
 const facts=context.existingNativeFacts.variants.find(v=>v.label===label);need(facts,'Fixed data fact required');
 for(const key of['metadata','freezeReceipt'])need(JSON.stringify(tuple(root[key]))===JSON.stringify(tuple(facts[key])),'Root pair must bind exact unmodified historical descriptor '+key);
 need(root.engine.sha256===facts.engineSha256&&root.engine.bytes===facts.engineBytes,'Exact engine fact');
 const metadata=JSON.parse(await context.readExternal(root.metadata));classifyMetadataForCost(metadata,label);
 const freeze=JSON.parse(await context.readExternal(root.freezeReceipt));
 need(freeze.schema===1&&freeze.state==='immutable-zlib-release-engine-frozen'&&freeze.label===label,'Actual frozen state');
 need(freeze.nativeInputsVerified===350&&freeze.externalEmbeddingInputsVerified===3&&freeze.recipeSha256===RECIPE,'Genuine full frozen350, no342/355 projection');
 need(freeze.engineSha256===root.engine.sha256&&freeze.engineBytes===root.engine.bytes&&freeze.receiptSha256===root.metadata.sha256,'Frozen engine/metadata bindings');
 need(freeze.actualLayoutCompileCommands===(label==='normal-off'?62:61)&&freeze.actualStrictCompileCommands===4&&freeze.actualEmbeddingCompileCommands===1,'Actual conditional native layout plus separate embedding');
 need(freeze.zlibEnabled===(label==='normal-off')&&freeze.entropyPolicy==='off'&&freeze.gcStress===false,'Actual OFF/ON flags');
 need(Array.isArray(freeze.copies)&&freeze.copies.length===1024,'Exact existing frozen inventory');
 const frozenRoot=resolve(root.freezeReceipt.path,'..');
 const captured=[];const seen=new Set();
 for(const row of freeze.copies){
  need(typeof row.path==='string'&&resolve(row.path)===row.path&&row.path.startsWith(frozenRoot+'/')&&!seen.has(row.path),'Frozen copy identity/path');seen.add(row.path);
  const own=Object.freeze(tuple(row));await context.hashExternal(own);captured.push(own);
 }
 // Validate only frozen copies/current immutable references. Never follow
 // freeze.original fields, old Root consumed rows, or mutable original caches.
 await context.hashExternal(root.engine);
 const sourceRoot=freeze.sourceRoot;need(resolve(sourceRoot)===sourceRoot&&sourceRoot===facts.sourceRoot,'Actual frozen native sourceRoot');
 for(const row of metadata.sourceManifest){const file={path:join(sourceRoot,row.path),sha256:row.sha256};await context.hashFrozenSource(file);}
 for(const row of metadata.componentizeSourceManifest){
  const path=join(freeze.componentizeSourceRoot,row.path),copy=freeze.copies.find(value=>resolve(value.path).replace(/^\/tmp(?=\/|$)/,'/private/tmp')===resolve(path).replace(/^\/tmp(?=\/|$)/,'/private/tmp'));
  need(copy&&copy.sha256===row.sha256,'Actual external embedding3 frozen bytes');await context.hashExternal(tuple(copy));
 }
 await context.recheck();
 const modulePath=join(context.packagingRoot,'tests/node-compat/zlib-admission.mjs');
 const {validateZlibBuildSourceAdmission}=await import(pathToFileURL(modulePath));
 const parentPins=JSON.parse(await context.readRepository('tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json'));
 const actual=validateZlibBuildSourceAdmission(metadata,{sourceRoot,parentProtectedSources:parentPins.parentProtected.sourceSha256,parentProtectedPatch:parentPins.parentProtected.patchSha256});
 need(actual&&actual.sourceInputs===350&&actual.zlibEnabled===(label==='normal-off')&&actual.runtimeOrGuestExecutionProof===false,'Actual finite build-only gate required');
 const sdk=[metadata.zlibPolicy.codecWitness.archive,...metadata.zlibPolicy.codecWitness.headers].map(tuple);
 need(Array.isArray(pair.data.selectedSDKReferences)&&pair.data.selectedSDKReferences.length===5&&JSON.stringify(pair.data.selectedSDKReferences.map(tuple))===JSON.stringify(sdk),'New Root pair binds exact selected archive/four-header reference set');
 // This selected SDK is an explicit reference, separate from both physical
 // packaging trees and frozen350 copies. Hash the538MB archive as a stream;
 // never reinterpret old consumed tool/original-cache rows as current inputs.
 for(const row of sdk)await streamHash(row);
 const {validateManifest}=await import(pathToFileURL(join(context.packagingRoot,'builtins/node-compat/validate-manifest.mjs')));
 const schema=JSON.parse(await context.readRepository('builtins/node-compat/manifest.schema.json'));
 const selected=[];
 for(const row of metadata.selectedModuleManifests){
  const raw=await context.readFrozenSource({path:join(sourceRoot,row.path),sha256:row.sha256});
  selected.push(validateManifest(JSON.parse(raw),schema));
 }
 need(selected.length===(label==='normal-off'?10:9),'Actual full manifest catalog');
 // This is deliberately NOT selectedManifestsForEngine: ordinary350 admission
 // remains CLOSED. The action-specific raw cost gate never changes that state.
 const fixedEngine=Object.freeze(tuple(root.engine)),fixedMetadata=Object.freeze(tuple(root.metadata)),fixedFreeze=Object.freeze(tuple(root.freezeReceipt));
 async function recheck(){await authority.recheck();await pair.recheck();await context.recheck();await context.hashExternal(fixedEngine);await context.readExternal(fixedMetadata);await context.readExternal(fixedFreeze);for(const row of captured)await context.hashExternal(row);for(const row of sdk)await streamHash(row);}
 await recheck();
 return Object.freeze({arm,label,enginePath:root.engine.path,sourceRoot,...freezeAdmissionValues(metadata,selected),
  pin:Object.freeze({engineSha256:root.engine.sha256,engineBytes:root.engine.bytes,metadataSha256:root.metadata.sha256,freezeReceiptSha256:root.freezeReceipt.sha256,nativeInputs:350}),
  diagnosticCostOnly:true,validationBuildOnly:true,operationalAdmission:false,metadataProjected:false,recheck});
}
