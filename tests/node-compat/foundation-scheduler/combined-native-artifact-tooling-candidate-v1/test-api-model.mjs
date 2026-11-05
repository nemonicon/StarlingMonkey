// Pure API shape/current DATA only. Never calls combinedNativeBootstrapPreflight.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureDescriptor,bootstrapFrameModel} from './bootstrap.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),refs=JSON.parse(await readFile(join(HERE,'references.json'))),metadata=JSON.parse(await readFile(refs.metadata.path)),selectedManifests=[];
for(const r of refs.selectedManifestRows)selectedManifests.push(JSON.parse(await readFile(join(refs.frozenSourceRoot,r.path))));
const own={path:join(HERE,'index.json'),sha256:'a'.repeat(64),bytes:1},nativeFrame={state:'COMBINED355_FROZEN_FULL80_NATIVE_DATA_VERIFIED_NO_ACTION_AUTHORITY_V1',toolingIndex:own,metadata,selectedManifests};
const value={schemaVersion:1,state:'COMBINED355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V1',variant:'normal-off',toolingIndex:own,nativeSourceFiles:355,externalEmbeddingSources:3,selectedManifestCount:11,fullMetadataFields:80,engine:refs.engine,metadataDescriptor:refs.metadata,freezeReceipt:refs.freezeReceipt,actualFrozenReview:refs.actualFrozenReview,metadata,selectedManifests,sourceRoot:refs.frozenSourceRoot,configuredSourceRoot:refs.configuredSourceRoot,workRoot:refs.workRoot,componentizeSourceRoot:refs.componentizeSourceRoot,nativeFrame,pin:{nativeFrame,state:'reviewed-combined355-normal-off-pin-v1',reviewRequired:false},nativeSourceIndex:refs.nativeSourceIndex,retryBuildControllerIndex:refs.retryBuildControllerIndex,freezerSourceIndex:refs.freezerSourceIndex,validationBootstrapOnly:true,currentFrozenVerifierCalls:1,engineExecuted:false,guestExecuted:false,operationalAdmission:false,runtimeAcceptanceClaim:false,grantsRuntimeAuthority:false};
let checks=0;const ck=v=>{assert.ok(v);checks++;},deny=fn=>{assert.throws(fn);checks++;};ck(bootstrapFrameModel(value,refs,own));
for(const[k,v]of [['state','FOREIGN'],['nativeSourceFiles',342],['selectedManifestCount',9],['fullMetadataFields',75],['currentFrozenVerifierCalls',2],['engineExecuted',true],['sourceRoot',refs.configuredSourceRoot]])deny(()=>bootstrapFrameModel({...value,[k]:v},refs,own));
for(const v of [{...value,nativeFrame:{...nativeFrame,state:'FOREIGN'}},{...value,pin:{...value.pin,reviewRequired:true}},{...value,metadata:{...metadata,extra:1}}])deny(()=>bootstrapFrameModel(v,refs,own));
ck(captureDescriptor(refs.engine).sha256===refs.engine.sha256);for(const path of ['relative','/a/../b','/a\\b'])deny(()=>captureDescriptor({...refs.engine,path}));deny(()=>captureDescriptor({...refs.engine,bytes:-1}));
console.log(JSON.stringify({schemaVersion:1,passed:true,checks,modelFixtureOnlyNotActualBootstrap:true,readOnlyApiInvoked:false,processOrHelperOrEngineOrGuestInvoked:false}));
