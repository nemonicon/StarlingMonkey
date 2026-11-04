// Source proposal: small fresh worker. No composition/native/replay/HTTP audit imports.
import assert from 'node:assert/strict';
import {readFile,lstat,open,writeFile} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {performance} from 'node:perf_hooks';
const rss=()=>process.memoryUsage().rss,bootstrapRssBytes=rss(),started=performance.now();
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex'),SHA=/^[0-9a-f]{64}$/;
const [manifestPath,manifestSha,descriptorPath,descriptorSha,output]=process.argv.slice(2);assert.equal(process.argv.length,7);assert(SHA.test(manifestSha??'')&&SHA.test(descriptorSha??''));
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);assert.equal(process.env.NODE_COMPAT_MEMORY_PROBE_APPROVED,'1');
assert(output&&resolve(output)===output&&output.startsWith('/tmp/starling-node-compat/'));
assert.equal(dirname(dirname(output)),dirname(manifestPath));assert.equal(manifestPath,join(dirname(dirname(output)),'worker-self-manifest.json'));assert.equal(descriptorPath,join(output,'descriptor.json'));assert.equal(dirname(output).split('/').at(-1),'workers');
const outputStat=await lstat(output);assert(outputStat.isDirectory()&&!outputStat.isSymbolicLink());
async function small(path,sha,max){assert(resolve(path)===path);const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink()&&info.size<=max);const raw=await readFile(path);assert.equal(hash(raw),sha);assert(raw.length<=max);return raw;}
async function streamed(row,root){
 assert.equal(dirname(row.path),root);const folder=await lstat(root);assert(folder.isDirectory()&&!folder.isSymbolicLink());const info=await lstat(row.path);assert(info.isFile()&&!info.isSymbolicLink()&&info.size===row.bytes);
 const digest=createHash('sha256');let bytes=0;for await(const chunk of createReadStream(row.path,{highWaterMark:65536})){digest.update(chunk);bytes+=chunk.length;}assert.equal(bytes,row.bytes);assert.equal(digest.digest('hex'),row.sha256);
}
const manifestRaw=await small(manifestPath,manifestSha,4096),manifest=JSON.parse(manifestRaw);
assert.deepEqual(Object.keys(manifest).sort(),['files','schemaVersion','sourceIndexSha256'].sort());assert.equal(manifest.schemaVersion,1);assert(SHA.test(manifest.sourceIndexSha256));assert.equal(manifest.files.length,3);
const expectedPaths=[join(here,'worker.mjs'),join(here,'contracts.mjs'),resolve(here,'../measurement-execution-activated-v2/instantiate.mjs')];
for(const [i,row] of manifest.files.entries()){assert.deepEqual(Object.keys(row).sort(),['bytes','path','sha256']);assert.equal(row.path,expectedPaths[i]);assert(SHA.test(row.sha256)&&Number.isSafeInteger(row.bytes)&&row.bytes>0&&row.bytes<=65536);await streamed(row,dirname(row.path));}
assert.equal(manifest.files[2].sha256,'0b9d3cee8d40160a9fa0c56165e60d6a8ef57e10a9c722069f30d5f162c3492b');
const {validateDescriptor,artifactRoot,packageFile}=await import('./contracts.mjs');
const raw=await small(descriptorPath,descriptorSha,16384),descriptor=validateDescriptor(JSON.parse(raw));assert.equal(descriptor.sourceIndexSha256,manifest.sourceIndexSha256);
assert.equal(output.split('/').at(-1),descriptor.comparison+'.rep-'+descriptor.repetition+'.'+descriptor.arm);
const snapshots=[{stage:'bootstrap-before-descriptor',rssBytes:bootstrapRssBytes,elapsedSinceEntryMs:0},{stage:'pre-critical-file-hash',rssBytes:rss(),elapsedSinceEntryMs:performance.now()-started}];
const stages=[],rawReturns=[];let writeSequence=0;
async function persist(name,value){assert(/^[a-z0-9-]+$/.test(name));const path=join(output,name+'.json');await writeFile(path,JSON.stringify(value,null,2)+'\n',{flag:'wx'});const handle=await open(path,'r');try{await handle.sync();}finally{await handle.close();}}
function snapshot(stage){const value={stage,rssBytes:rss(),elapsedSinceEntryMs:performance.now()-started};snapshots.push(value);return value;}
async function progress(stage,detail={}){const record={stage,...detail,partialObservationOnly:true,requiresExternalExitZero:true};process.stderr.write(JSON.stringify(record)+'\n');await persist(String(++writeSequence).padStart(2,'0')+'-'+stage,record);}
async function exactCall(instance,name,args,expectedRaw,label,{literal=false}={}){
 await progress('before-'+label,{publicExport:name,arguments:args});const start=performance.now(),actual=await instance.exports[name](...args),elapsedMs=performance.now()-start;
 const observed={label,publicExport:name,arguments:args,rawReturn:actual,elapsedMs,rssBytes:rss()};rawReturns.push(observed);await persist('raw-'+label,observed);await progress('returned-'+label);
 assert.equal(typeof actual,'string');const serialized=literal?actual:JSON.stringify(JSON.parse(actual));if(serialized!==expectedRaw)throw new Error('Public scalar mismatch: '+label+' (whole raw return retained)');return elapsedMs;
}
let failure=null;
try{
 for(const row of descriptor.criticalFiles)await streamed(row,row.path===packageFile(descriptor.arm).path?dirname(artifactRoot(descriptor.arm)):artifactRoot(descriptor.arm));snapshot('post-critical-file-hash');await persist('baselines',snapshots);
 // The original helper is authenticated above before loading any glue or Wasm.
 const {loadCompiled}=await import(pathToFileURL(expectedPaths[2]));await progress('before-compile-and-binding-load');let start=performance.now();const instantiate=await loadCompiled(descriptor);stages.push({stage:'compile-and-binding-load',elapsedMs:performance.now()-start});snapshot('after-compile-and-binding-load');await progress('compiled');
 start=performance.now();const instance=await instantiate();stages.push({stage:'instantiate',elapsedMs:performance.now()-start});snapshot('after-instantiate');await progress('instantiated');
 stages.push({stage:'first-identity-export',elapsedMs:await exactCall(instance,'identity',[],descriptor.expected.identityRaw,'identity')});snapshot('after-identity');
 stages.push({stage:'first-checkpoint-probe',elapsedMs:await exactCall(instance,'checkpointProbe',[],descriptor.expected.probeRaw,'probe-before')});snapshot('after-identity-and-probe');
 for(const [i,row] of descriptor.expected.cases.entries()){
  const label=i===0?'small':'large';stages.push({stage:label+'-setup',elapsedMs:await exactCall(instance,'setup',[row.index],row.setupReturn,label+'-setup',{literal:true})});snapshot('after-'+label+'-setup');
  stages.push({stage:label+'-single-batch',elapsedMs:await exactCall(instance,'batch',[row.index,1],row.batchRaw,label+'-batch')});snapshot('after-'+label);
 }
 stages.push({stage:'final-checkpoint-probe',elapsedMs:await exactCall(instance,'checkpointProbe',[],descriptor.expected.probeRaw,'probe-after')});snapshot('after-final-probe');
 const maxRssBeforeFinalHashKilobytes=process.resourceUsage().maxRSS;
 await small(manifestPath,manifestSha,4096);await small(descriptorPath,descriptorSha,16384);for(const row of manifest.files)await streamed(row,dirname(row.path));for(const row of descriptor.criticalFiles)await streamed(row,row.path===packageFile(descriptor.arm).path?dirname(artifactRoot(descriptor.arm)):artifactRoot(descriptor.arm));snapshot('after-final-critical-file-hash');
 const result={schemaVersion:1,state:'SMALL_PUBLIC_PROCESS_RSS_WORKER_OBSERVED',sourceIndexSha256:manifest.sourceIndexSha256,descriptorSha256:descriptorSha,arm:descriptor.arm,comparison:descriptor.comparison,repetition:descriptor.repetition,runOrder:descriptor.runOrder,position:descriptor.position,
  freshProcessPid:process.pid,snapshots,stages,rawReturns,publicCalls:rawReturns.length,iterationsEach:1,caseOrder:[1,5],maxRssBeforeFinalHashKilobytes,terminalMaxRssKilobytes:process.resourceUsage().maxRSS,
  component:descriptor.component,nativeEvidence:descriptor.nativeEvidence,capacityBytes:null,growCount:null,guestHeapBytes:null,
  scope:'Process RSS includes Node/V8, streamed hashes, compile cache, Jco glue, Wasm instance and allocator retention. Small then large on the same instance; no forced GC or reset. Stage wall time is operational, not throughput.',requiresExternalExitZero:true,runtimeAcceptanceClaim:false};
 await persist('result',result);console.log(JSON.stringify(result));
}catch(error){failure={name:error.name,message:error.message};try{await persist('failure',{failure,snapshots,stages,rawReturns,partialObservationOnly:true});}catch(storageError){process.stderr.write(JSON.stringify({stage:'failure-record-write-failed',failure,storageError:{name:storageError.name,message:storageError.message}})+'\n');}throw new Error('Memory worker failed: '+failure.message);}
