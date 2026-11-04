// Authenticated full355 validation-only frame. Ordinary operational selection stays closed.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {here,hash,regular,verifyInventory,safeLocal} from './physical.mjs';
import {assertFourPins,assertFrame,assertSourceTransition,assertRuntimeAuthority,variantForScope,consumerValidationSha256,assertConsumerPrerequisite} from './contracts.mjs';
const CONFIG_SHA='@CONFIG_SHA@',INPUTS_SHA='@INPUTS_SHA@',frames=new Map();
export {hash};
let captured,historicalSelectors;
const frozen=value=>{if(value&&typeof value==='object'){for(const item of Object.values(value))frozen(item);Object.freeze(value);}return value;};
export async function verifyFamily(){
 const config=JSON.parse(await regular(join(here,'activation.json'),CONFIG_SHA));assert.equal(config.state,'REVIEWED_CONSUMERS355_RELEASE_SOURCE_ACTIVATED_V1');assert.equal(config.operationalAdmission,false);
 const indexSha=process.env.NODE_COMPAT_RELEASE_FAMILY_INDEX_SHA256;assert(/^[0-9a-f]{64}$/.test(indexSha??''),'Explicit reviewed family index SHA required');
 const index=JSON.parse(await regular(join(here,'index.json'),indexSha));for(const row of index.files)await regular(await safeLocal(here,row.path),row.sha256,row.bytes);
 const seal=JSON.parse(await regular(join(here,'input-freeze.json'),INPUTS_SHA));const result=await verifyInventory(here,seal);
 let template=(await readFile(join(here,'native-preflight.template.mjs'),'utf8')).replaceAll('@'+'CONFIG_SHA'+'@',CONFIG_SHA).replaceAll('@'+'INPUTS_SHA'+'@',INPUTS_SHA);
 assert.equal(hash(await readFile(join(here,'native-preflight.mjs'))),hash(template),'Compiled bridge must equal sealed template');
 assert.equal(config.nativeConfiguredSourceRoot,resolve(config.bootstrapRoot,'../../../..'));assert.equal(config.nativeConfiguredSourceRoot,'/private/tmp/starling-node-compat/consumers-source-v2');
 assert.equal(config.componentToolRoot,join(here,'snapshot'));assert.notEqual(config.componentToolRoot,config.nativeConfiguredSourceRoot);
 const pins=JSON.parse(await regular(join(here,'reviewed-pins.json'),config.pinsSha256)),review=JSON.parse(await regular(join(here,'root-review.json'),config.rootReviewSha256));assertFourPins(pins,review,config.pinsSha256);
 const prerequisite=JSON.parse(await regular(join(here,'reviewed-consumer-validation.json'),consumerValidationSha256));assertConsumerPrerequisite(prerequisite);
 captured=frozen({config,pins,review,seal});return{...result,indexSha256:indexSha,sha256:INPUTS_SHA,path:join(here,'input-freeze.json')};
}
export async function validationPreflight({variant='normal-off'}={}){
 await verifyFamily();const {config,pins}=captured;assert(['normal-off','normal-runtime','gc-off'].includes(variant),'This release cut has no disabled runtime stage');
 const nativeIndex=JSON.parse(await regular(join(config.bootstrapRoot,'index.json'),config.bootstrapIndexSha256));for(const row of nativeIndex.files)await regular(await safeLocal(config.bootstrapRoot,row.path),row.sha256,row.bytes);
 // Both imports occur only after the exact native owner index and complete source/tool closure above.
 const {consumersBootstrapPreflight}=await import(pathToFileURL(join(config.bootstrapRoot,'artifact-tools/bootstrap-preflight.mjs')));
 const native=await consumersBootstrapPreflight({variant,reviewedPinsPath:join(here,'reviewed-pins.json'),reviewedPinsSha256:config.pinsSha256,rootReviewPath:join(here,'root-review.json'),rootReviewSha256:config.rootReviewSha256});
 const {admit}=await import(pathToFileURL(join(config.bootstrapRoot,'artifact-tools/metadata-admission.mjs')));
 const sourceAdmission=await admit(native.metadata,variant,native.sourceRoot);assert.equal(sourceAdmission.sourceFiles,355);assert.equal(sourceAdmission.operationalAdmission,false);
 assert.equal(native.validationBootstrapOnly,true);assert.equal(native.operationalAdmission,false);assert.equal(native.metadata.sourceManifest.length,355);
 assert.equal(native.metadata.streamConsumersEnabled,true);assert.equal(native.metadata.zlibEnabled,true);assert.equal(native.metadata.entropyPolicy,variant==='normal-runtime'?'runtime-only':'off');assert.equal(native.metadata.gcStress,variant==='gc-off');
 assert.deepEqual(native.pin,pins.variants[variant]);
 // The original ordinary selectors are used ONLY for the exact sealed older
 // control tuples. They remain closed for355 and never supply its frame.
 historicalSelectors={...(await import(pathToFileURL(join(config.componentToolRoot,'tests/node-compat/module-selection.mjs')))),...(await import(pathToFileURL(join(config.componentToolRoot,'tests/node-compat/core-expectations.mjs'))))};
 const expected=JSON.parse(await regular(join(here,'lineage.json'),config.lineageSha256));assert.deepEqual(native.metadata.sourceManifest.map(({path,sha256})=>({path,sha256})),expected.native355);
 const frame=frozen({...native,metadata:structuredClone(native.metadata),selectedManifests:structuredClone(native.selectedManifests),core:structuredClone(sourceAdmission.coreExpectations),lineage:expected});frames.set(native.metadata.engineSha256,frame);
 async function recheck(){await verifyFamily();await native.recheck();await admit(frame.metadata,variant,frame.sourceRoot);assertFrame(native.metadata,native.sourceRoot,frame);}
 await recheck();return Object.freeze({...native,selectedManifests:frame.selectedManifests,coreExpectations:frame.core,componentToolRoot:config.componentToolRoot,toolSourceRoot:config.componentToolRoot,recheck});
}
export async function assertActionContext({variant}={}){
 const family=await verifyFamily(),scope=process.env.NODE_COMPAT_RELEASE_SCOPE,output=process.env.NODE_COMPAT_RELEASE_SCOPE_OUTPUT;
 assert(output&&resolve(output)===output);const authority=JSON.parse(await regular(process.env.NODE_COMPAT_RELEASE_ACTION_AUTHORITY,process.env.NODE_COMPAT_RELEASE_ACTION_AUTHORITY_SHA256));
 assertRuntimeAuthority(authority,{familyIndexSha256:family.indexSha256,scope,output});assert.equal(variant,variantForScope(scope));
 for(const [key,value]of Object.entries(process.env))if(key.startsWith('NODE_COMPAT_')&&key.endsWith('_OUTPUT'))assert(resolve(value)===output||resolve(value).startsWith(output+'/'),'Output escapes authorized fresh scope: '+key);
 return{scope,output};
}
function current(metadata,sourceRoot){const frame=frames.get(metadata.engineSha256);assertFrame(metadata,sourceRoot,frame);return frame;}
function historical(metadata,sourceRoot){assert(captured,'No authenticated family');const control=captured.seal.historicalControls.find(row=>row.engineSha256===metadata.engineSha256&&row.sourceRoot===sourceRoot);assert(control,'Unknown historical lineage');assert.deepEqual(metadata,control.metadata,'Historical metadata cannot be relabelled');return control;}
export function selectedManifestsForValidation(metadata,{sourceRoot}={}){
 if(metadata.sourceManifest?.length===355)return current(metadata,sourceRoot).selectedManifests;
 historical(metadata,sourceRoot);assert(historicalSelectors);return historicalSelectors.selectedManifestsForEngine(metadata,{sourceRoot});
}
export function coreExpectationsForValidation(metadata,{sourceRoot}={}){if(metadata.sourceManifest?.length===355)return current(metadata,sourceRoot).core;historical(metadata,sourceRoot);assert(historicalSelectors);return historicalSelectors.selectCoreExpectations(metadata,{sourceRoot});}
export function assertRegistrarOracleAncestry({kind,oracle,requiredNames,registrar,metadata,proof}){
 const frame=frames.get(metadata.engineSha256);assertFrame(metadata,frame?.sourceRoot,frame);const data=frame.lineage;
 const item=data.oracles[kind];assert(item,'Only the three exact strict-script Node oracles are supported');assert.equal(hash(proof.oracleBytes),item.sha256);assert.deepEqual(oracle,JSON.parse(proof.oracleBytes));assert.deepEqual([...requiredNames].sort(),[...item.required].sort());
 assert.equal(oracle.registrarSha256,data.registrars[0]);for(const [key,expected]of Object.entries(data.originalProofHashes))assert.equal(hash(proof[key]),expected,key);
 assert.equal(data.native306.length,306);assert.equal(data.native342.length,342);assert.equal(data.native350.length,350);assert.equal(data.native355.length,355);
 assertSourceTransition(data.native306,data.native342,data.delta342,data.added342);assertSourceTransition(data.native342,data.native350,data.delta350,data.added350);assertSourceTransition(data.native350,data.native355,data.delta355,data.added355);
 assert.equal(hash(registrar),data.registrars[3]);assert.match(registrar,/options\.setForceStrictMode\(\)/);assert.deepEqual(metadata.sourceManifest.map(({path,sha256})=>({path,sha256})),data.native355);
 for(const name of requiredNames)assert.equal(data.native355.find(row=>row.path==='builtins/node-compat/'+name)?.sha256,oracle.sources[name],name);
 return{version:'explicit-306-342-350-355-registrar-oracle-ancestry-v1',kind,oracleSha256:item.sha256,oracleRegistrarSha256:data.registrars[0],actualRegistrarSha256:data.registrars[3],sourceCounts:[306,342,350,355],oracleRewritten:false,metadataProjected:false};
}
