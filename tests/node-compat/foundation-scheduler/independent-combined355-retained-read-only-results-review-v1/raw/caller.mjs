// Host-only observer of the reviewed read/hash API; never imports a packager/guest.
import assert from 'node:assert/strict';
import {readFile,open,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);
assert.equal(process.argv.length,4);
const config=JSON.parse(process.argv[2]),out=process.argv[3],hash=b=>createHash('sha256').update(b).digest('hex');
async function checked(row){const b=await readFile(row.path);assert.equal(b.length,row.bytes);assert.equal(hash(b),row.sha256);return b;}
async function write(name,value){const f=await open(join(out,name),'wx',0o600);try{await f.writeFile(JSON.stringify(value,null,2)+'\n');await f.sync();}finally{await f.close();}}
const cfg=JSON.parse(await checked(config)),sourceRoot=cfg.toolingIndex.path.slice(0,-'/index.json'.length),index=JSON.parse(await checked(cfg.toolingIndex));
const apiRow=index.files.find(r=>r.path==='bootstrap.mjs');assert(apiRow);await checked({...apiRow,path:join(sourceRoot,apiRow.path)});
const api=await import(pathToFileURL(join(sourceRoot,'bootstrap.mjs')));assert.equal(typeof api.combinedNativeBootstrapPreflight,'function');
await mkdir(join(out,'calls'),{mode:0o700});
async function capture(frame,n){
 const shape=Object.fromEntries(Object.entries(Object.getOwnPropertyDescriptors(frame)).map(([k,d])=>[k,{type:typeof d.value,enumerable:d.enumerable,writable:d.writable,configurable:d.configurable}]));
 const data=Object.fromEntries(Object.entries(frame).filter(([k])=>k!=='recheck'));
 await write('calls/'+n+'.data.json',data);await write('calls/'+n+'.shape.json',{shape,callableRecheckSerialized:false,allOtherReturnedDataRetained:true});
 assert.deepEqual(Reflect.ownKeys(frame),['schemaVersion','kind','sourceIndex','actualReview','bootstrap','currentVerification','recheck']);
 assert(Object.isFrozen(frame)&&Object.isFrozen(frame.bootstrap)&&Object.isFrozen(frame.bootstrap.metadata));
 assert.equal(typeof frame.recheck,'function');assert.equal(frame.kind,'retained-combined355-bootstrap-v1');
 assert.equal(frame.bootstrap.fullMetadataFields,80);assert.equal(Object.keys(frame.bootstrap.metadata).length,80);
 assert.equal(frame.bootstrap.nativeSourceFiles,355);assert.equal(frame.bootstrap.externalEmbeddingSources,3);assert.equal(frame.bootstrap.selectedManifests.length,11);
 assert.equal(frame.bootstrap.currentFrozenVerifierCalls,1); // Historical CLI DATA, not this call.
 for(const k of ['helperInvocations','processesSpawned','filesCreated'])assert.equal(frame.currentVerification[k],0);
 for(const k of ['engineExecuted','guestExecuted','operationalAdmission'])assert.equal(frame.currentVerification[k],false);
 assert.equal(shape.recheck.writable,false);assert.equal(shape.recheck.configurable,false);
}
try{
 const first=await api.combinedNativeBootstrapPreflight({configDescriptor:config});await capture(first,'001');await first.recheck();
 const second=await api.combinedNativeBootstrapPreflight({configDescriptor:config});await capture(second,'002');await second.recheck();await first.recheck();
 assert.notEqual(first,second);assert.notEqual(first.recheck,second.recheck);assert.deepEqual(first.bootstrap,second.bootstrap);
 await write('results.json',{schemaVersion:1,state:'ROOT_COMBINED355_RETAINED_READ_ONLY_API_COMPLETE_UNREVIEWED_V1',config,sourceIndex:cfg.toolingIndex,actualReview:first.actualReview,calls:2,freshRechecks:2,recheckCalls:3,wholeHistoricalBootstrapDataEqual:true,currentHelperInvocations:0,currentProcessesSpawnedByApi:0,currentFilesCreatedByApi:0,currentVerificationDataSeparateFromHistoricalBootstrap:true,fullMetadataFields:80,nativeSourceFiles:355,externalEmbeddingSources:3,selectedManifestCount:11,engineExecuted:false,guestExecuted:false,componentBuilt:false,operationalAdmission:false,runtimeAcceptanceClaim:false});
 console.log(JSON.stringify({calls:2,recheckCalls:3,completeUnreviewed:true,engineExecuted:false}));
}catch(error){await write('failure.json',{schemaVersion:1,name:error?.name,message:error?.message,stack:error?.stack,partialEvidenceOnly:true});throw error;}
