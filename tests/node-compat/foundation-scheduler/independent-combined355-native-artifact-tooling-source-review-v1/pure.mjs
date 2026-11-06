// Inert Source/pure models only. Never calls combinedNativeBootstrapPreflight.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const fixture=JSON.parse(await readFile(process.argv[2],'utf8'));assert.equal(fixture.syntheticRootSlotsOnly,true);assert.equal(fixture.actualBootstrap,false);
const {bootstrapFrameModel,captureDescriptor}=await import(pathToFileURL(fixture.api.path)),{value,refs,own}=fixture;let cases=0;const yes=fn=>{assert.equal(fn(),true);cases++;},no=fn=>{assert.throws(fn);cases++;};
yes(()=>bootstrapFrameModel(value,refs,own));
for(const[k,v]of [['state','OTHER'],['variant','gc-off'],['nativeSourceFiles',342],['externalEmbeddingSources',4],['selectedManifestCount',9],['fullMetadataFields',75],['sourceRoot',refs.configuredSourceRoot],['workRoot',refs.frozenRoot],['currentFrozenVerifierCalls',0],['currentFrozenVerifierCalls',2],['engineExecuted',true],['guestExecuted',true],['operationalAdmission',true],['runtimeAcceptanceClaim',true],['grantsRuntimeAuthority',true]])no(()=>bootstrapFrameModel({...value,[k]:v},refs,own));
no(()=>bootstrapFrameModel({...value,metadata:{...value.metadata,extra:true}},refs,own));no(()=>bootstrapFrameModel({...value,pin:{...value.pin,reviewRequired:true}},refs,own));no(()=>bootstrapFrameModel({...value,nativeFrame:{...value.nativeFrame,state:'OLD_NOT_ACCEPTED'}},refs,own));
assert.equal(captureDescriptor(refs.engine).sha256,refs.engine.sha256);cases++;for(const path of ['relative','/a/../b','/a\\b'])no(()=>captureDescriptor({...refs.engine,path}));no(()=>captureDescriptor({...refs.engine,bytes:-1}));
console.log(JSON.stringify({schemaVersion:1,passed:true,cases,actualFull80NativeDataUsed:true,realSourceModuleImportedInertly:true,syntheticRootSlotsOnly:true,actualBootstrap:false,retainedApiInvoked:false,helperVerifierMonitorExportBootstrapEngineGuestInvoked:false}));
