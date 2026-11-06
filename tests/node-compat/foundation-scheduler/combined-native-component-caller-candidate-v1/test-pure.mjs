// Inert own Source imports and actual retained DATA reads only. No API/phase.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeRecordModel,phaseModel,environmentModel,prerequisiteModel,captureDescriptor} from './entry.mjs';
import {snapshotBytes,safe,observed,writeWhole} from './io.mjs';
const P=dirname(fileURLToPath(import.meta.url));
const refs=JSON.parse(await readFile(join(P,'references.json'))),proof=JSON.parse(await readFile(refs.actualBootstrapReview.result.path)),bootstrap=JSON.parse(await readFile(proof.bootstrapFrame.path)),metadata=JSON.parse(await readFile(refs.nativeMetadata.path)),catalogue=JSON.parse(await readFile(refs.fixtureCatalogue.path));
let cases=0;const ok=f=>{f();cases++;},reject=f=>{assert.throws(f);cases++;};
const fakeDescriptor=label=>({path:'/synthetic-source-model/'+label,sha256:'a'.repeat(64),bytes:1});
// This is a host model around genuine actual bootstrap DATA. It is not a
// returned retained-API record, Root permission or operational proof.
const modelRefs={...refs,readOnlyConfig:fakeDescriptor('readonly-config.json')};
const record=()=>Object.freeze({schemaVersion:1,kind:'retained-combined355-bootstrap-v1',sourceIndex:refs.nativeApiSourceIndex,actualReview:refs.actualBootstrapReview,bootstrap:structuredClone(bootstrap),currentVerification:{schemaVersion:1,kind:'current-read-hash-verification-v1',config:modelRefs.readOnlyConfig,rootAuthority:fakeDescriptor('readonly-root.json'),sourceIndex:refs.nativeApiSourceIndex,fullMetadataFields:80,selectedWholeManifests:11,helperInvocations:0,processesSpawned:0,filesCreated:0,engineExecuted:false,guestExecuted:false,operationalAdmission:false},recheck:()=>{throw Error('MODEL ONLY: recheck must never execute');}});
ok(()=>assert.equal(nativeRecordModel(record(),modelRefs,metadata,bootstrap).fullMetadataFields,80));
if(refs.actualReadOnlyData){const actualData=JSON.parse(await readFile(refs.actualReadOnlyData.path)),hostModel=Object.freeze({...structuredClone(actualData),recheck:()=>{throw Error('host data model, not real API');}});ok(()=>nativeRecordModel(hostModel,refs,metadata,bootstrap,actualData));reject(()=>nativeRecordModel(hostModel,refs,metadata,bootstrap,{...actualData,currentVerification:{...actualData.currentVerification,helperInvocations:1}}));}
for(const change of [r=>r.bootstrap.metadata.sourceManifest.splice(342),r=>r.bootstrap.selectedManifests.splice(9),r=>r.bootstrap.metadata.enginePath=refs.nativeEngine.path,r=>r.bootstrap.currentFrozenVerifierCalls=0,r=>r.bootstrap.pin.nativeFrame.verificationCapsule.state='accepted',r=>r.currentVerification.helperInvocations=1,r=>r.currentVerification.processesSpawned=1,r=>r.currentVerification.filesCreated=1,r=>r.currentVerification.fullMetadataFields=75,r=>r.currentVerification.selectedWholeManifests=9])reject(()=>{const r=record();change(r);nativeRecordModel(r,modelRefs,metadata,bootstrap);});
reject(()=>nativeRecordModel({...record()},modelRefs,metadata,bootstrap));
reject(()=>nativeRecordModel(Object.freeze({...record(),recheck:null}),modelRefs,metadata,bootstrap));
const own=fakeDescriptor('caller/index.json');
const template=JSON.parse(await readFile(join(P,'future-root-authority.template.json')));
for(const fixture of catalogue.fixtures)for(const phase of ['bundle','construct']){
 const root={...template,state:template.requiredIssuedState,sourceIndex:own,phase,fixtureId:fixture.id,fixtureSource:fixture.source,fixtureWit:fixture.wit,worldName:fixture.worldName,nativeEngine:refs.nativeEngine,nativeMetadata:refs.nativeMetadata,readOnlyConfig:refs.readOnlyConfig,actualBootstrapReview:refs.actualBootstrapReview,actualReadOnlyReview:refs.actualReadOnlyReview,selectedInterfaces:fixture.selectedInterfaces,disableFeatures:fixture.disableFeatures,bundlePreparationAllowed:phase==='bundle',componentConstructionAllowed:phase==='construct',engineInitializationAllowed:phase==='construct',nativeReadOnlyApiAllowed:true,outputRoot:refs.outputBase+'-'+phase+'-'+fixture.id,externalRoot:refs.outputBase+'-'+phase+'-'+fixture.id+'-external-root',privateTemporaryRoot:refs.outputBase+'-'+phase+'-'+fixture.id+'-tmp',ownedNodeDeadlineSeconds:phase==='bundle'?1200:2400};
 if(phase==='construct')Object.assign(root,{bundleReport:fakeDescriptor('bundle-result.json'),bundle:fakeDescriptor('bundle.mjs'),bundleExternalTerminal:fakeDescriptor('bundle-terminal.json'),loaderConfig:fakeDescriptor('loader-config.json'),loaderRootAuthority:fakeDescriptor('loader-root.json'),guestSourceSha256:'a'.repeat(64),witWorldSha256:fixture.wit.sha256});
 ok(()=>assert.equal(phaseModel(root,own,refs,fixture,phase),true));
 for(const[k,v]of [['nativeSourceFiles',342],['fullMetadataFields',75],['selectedWholeManifests',9],['ordinaryGuestExportsAllowed',true],['engineInitializationAllowed',phase!=='construct'],['ownedNodeDeadlineSeconds',1],['outputRoot','/synthetic/wrong'],['actualRuntimeAuthority',fakeDescriptor('runtime')]])reject(()=>phaseModel({...root,[k]:v},own,refs,fixture,phase));
}
if(['fixtureSourcePeer','actualReadOnlyReview','actualReadOnlyContract','readOnlyConfig','actualReadOnlyRequiredState'].some(k=>refs[k]===null))reject(()=>prerequisiteModel(refs));else ok(()=>prerequisiteModel(refs));
const supplied={...refs};for(const k of ['fixtureSourcePeer','fixtureReviewRequiredState','fixtureReviewSourceField','readOnlyConfig','actualReadOnlyReview','actualReadOnlyContract','actualReadOnlyRequiredState'])supplied[k]=k.endsWith('State')||k.endsWith('Field')?'synthetic-model-only':fakeDescriptor(k);
ok(()=>prerequisiteModel(supplied));
for(const k of ['actualReadOnlyReview','actualReadOnlyContract','readOnlyConfig','fixtureSourcePeer','actualBootstrapReview'])reject(()=>prerequisiteModel({...supplied,[k]:null}));
ok(()=>environmentModel({},[],'v22.14.0'));for(const k of ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','NAPI_RS_NATIVE_LIBRARY_PATH','NODE_COMPAT_COMPONENTIZE_MODULE'])reject(()=>environmentModel({[k]:'x'},[],'v22.14.0'));
reject(()=>environmentModel({},['--require=x'],'v22.14.0'));reject(()=>environmentModel({},[],'v22.15.0'));
for(const bad of ['../escape','/absolute','x//y','x/./y','x/../y','x\\y','x\0y'])reject(()=>safe(bad));ok(()=>safe('transpiled/component.core.wasm'));
for(const bad of [{path:'/x/../y',sha256:'a'.repeat(64),bytes:1},{path:'/x',sha256:'bad',bytes:1},{path:'/x',sha256:'a'.repeat(64),bytes:-1}])reject(()=>captureDescriptor(bad));
ok(()=>{const input=new Uint8Array([1,2,3]),snapshot=snapshotBytes(input);input.fill(9);assert.deepEqual([...snapshot],[1,2,3]);assert.notEqual(snapshot.buffer,input.buffer);});reject(()=>snapshotBytes([1,2,3]));
for(const x of [null,undefined,false,0,'',17,'opaque diagnostic'])ok(()=>assert.equal(observed(x).type,typeof x));
// Run the real host writer with an explicitly injected in-memory fd. No file
// or directory is created; the actual construction call supplies no override.
for(const failure of [null,'open','write','sync','stat','close','hardlink','short']){
 const input=new Uint8Array([4,5,6]),out={root:'/synthetic-writer-model',rows:new Map(),check:async()=>{}},events=[];let retained=null;
 const openFile=async(path,flags,mode)=>{events.push('open');assert.equal(flags,'wx');assert.equal(mode,0o600);assert.equal(path,out.root+'/component.wasm');if(failure==='open')throw Error('open');return{
  writeFile:async snapshot=>{events.push('write');retained=[...snapshot];input.fill(9);if(failure==='write')throw Error('partial-write');},
  sync:async()=>{events.push('sync');if(failure==='sync')throw Error('fsync');},
  stat:async()=>{events.push('stat');if(failure==='stat')throw Error('stat');return{isFile:()=>true,nlink:failure==='hardlink'?2:1,size:failure==='short'?2:3};},
  close:async()=>{events.push('close');if(failure==='close')throw Error('close');}
 };};
 if(failure===null){const result=await writeWhole(out,'component.wasm',input,{openFile});assert.deepEqual(retained,[4,5,6]);assert.deepEqual([...result.snapshot],[4,5,6]);assert.equal(out.rows.size,1);assert.deepEqual(events,['open','write','sync','stat','close']);}
 else{await assert.rejects(()=>writeWhole(out,'component.wasm',input,{openFile}));assert.equal(out.rows.size,0);if(failure!=='open')assert.equal(events.at(-1),'close');}
 cases++;
}
process.stdout.write(JSON.stringify({schemaVersion:1,passed:true,cases,genuineFull80BootstrapDataUsed:true,actualRetainedApiInvoked:false,ownerPhaseOrGuestActions:false,syntheticFutureRootAndRecordModelsOnly:true})+'\n');
