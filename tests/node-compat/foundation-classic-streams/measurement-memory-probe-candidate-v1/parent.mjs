// Source proposal. Full historical/native/source audits occur only in this parent.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,open,statfs,readdir,readlink,realpath} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),base=resolve(here,'..'),old=join(base,'measurement-execution-activated-v2'),timing=join(base,'measurement-composition-timing-admission-amendment-v1');
const SHA=/^[0-9a-f]{64}$/,hash=raw=>createHash('sha256').update(raw).digest('hex');
const [ownSha,authorityPath,authoritySha,outputArg]=process.argv.slice(2);assert.equal(process.argv.length,6);assert(SHA.test(ownSha??'')&&SHA.test(authoritySha??''));
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);assert.equal(process.env.NODE_COMPAT_MEMORY_PROBE_APPROVED,'1');
async function streamed(row){assert(isAbsolute(row.path)&&SHA.test(row.sha256));const info=await lstat(row.path);assert(info.isFile()&&!info.isSymbolicLink());if(row.bytes!==undefined)assert.equal(info.size,row.bytes);const digest=createHash('sha256');let bytes=0;for await(const chunk of createReadStream(row.path,{highWaterMark:65536})){digest.update(chunk);bytes+=chunk.length;}assert.equal(digest.digest('hex'),row.sha256,row.path);if(row.bytes!==undefined)assert.equal(bytes,row.bytes);return{path:row.path,sha256:row.sha256,bytes};}
async function pinned(path,sha,max=1024*1024){const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink()&&info.size<=max);const raw=await readFile(path);assert(raw.length<=max);assert.equal(hash(raw),sha,path);return raw;}
async function ownIndex(){const raw=await pinned(join(here,'index.json'),ownSha),index=JSON.parse(raw);assert.equal(index.schemaVersion,1);const seen=new Set();for(const row of index.files){const path=resolve(here,row.path),name=relative(here,path);assert(name&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name)&&!seen.has(name));seen.add(name);await streamed({...row,path});}const found=index.files.filter(row=>row.path==='input-freeze.json');assert.equal(found.length,1);return{index,inputSha:found[0].sha256};}
const {index,inputSha}=await ownIndex();
const {validateAuthority,validateDescriptor,schedule,artifactRoot,packageFile,timingSourceSha,instantiateSha,phaseSha,timingSha}=await import('./contracts.mjs');
const authorityRaw=await pinned(authorityPath,authoritySha,16384),authority=validateAuthority(JSON.parse(authorityRaw),ownSha);
// No output, provider, artifact or historical proof access occurs for NULL or
// unreviewed authority. The expected input-manifest digest is a captured primitive.
const expectedInputSha=inputSha,expectedAuthoritySha=authoritySha;
async function ownInputs(){await pinned(authorityPath,expectedAuthoritySha,16384);const check=await ownIndex();assert.equal(check.inputSha,expectedInputSha);const raw=await pinned(join(here,'input-freeze.json'),expectedInputSha,4*1024*1024),manifest=JSON.parse(raw);assert.equal(manifest.schemaVersion,1);const seen=new Set();for(const row of manifest.inputs){assert(!seen.has(row.path));seen.add(row.path);await streamed(row);}return manifest.inputs.length;}
async function auditParent(){
 const ownInputsCount=await ownInputs();
 const {verifyTimingSources,auditComposedCorrectness}=await import(pathToFileURL(join(timing,'admission.mjs')));
 const {selectTimingPhase}=await import(pathToFileURL(join(timing,'phase.mjs')));
 const {executionPreflight}=await import(pathToFileURL(join(old,'runtime-preflight.mjs')));
 await verifyTimingSources(timing,timingSourceSha);
 const phase=selectTimingPhase(JSON.parse(await pinned(authority.phase.path,authority.phase.sha256,65536)));
 const report=JSON.parse(await pinned(authority.timingReport.path,authority.timingReport.sha256,2*1024*1024));assert.equal(report.state,'COMMON_BYTE_THREE_COMPARISON_TIMING_COMPLETE');assert.equal(report.phaseSha256,phaseSha);assert.equal(report.samples.length,126);assert.equal(report.calibrations.length,21);
 const root=JSON.parse(await pinned(authority.timingRootReceipt.path,authority.timingRootReceipt.sha256,1024*1024));assert.equal(root.state,'ROOT_COMPOSED_COMMON_BYTE_TIMING_TERMINAL_ZERO_V1');assert.equal(root.rawExitCode,0);assert.equal(root.phaseSha256,phaseSha);
 const proofIndex=JSON.parse(await pinned(authority.integrityIndex.path,authority.integrityIndex.sha256));assert.equal(proofIndex.schemaVersion,1);
 for(const row of proofIndex.files){assert(!row.path.includes('..')&&!isAbsolute(row.path));await streamed({...row,path:resolve(dirname(authority.integrityIndex.path),row.path)});}
 const proofRows=proofIndex.files.filter(row=>row.path==='results.json');assert.equal(proofRows.length,1);const proof=JSON.parse(await pinned(resolve(dirname(authority.integrityIndex.path),'results.json'),proofRows[0].sha256,4*1024*1024));assert.equal(proof.state,'INDEPENDENT_COMPOSED_TIMING_INTEGRITY_PROVENANCE_PASSED');assert.equal(proof.reportSha256,timingSha);assert.equal(proof.rootReceiptSha256,authority.timingRootReceipt.sha256);assert.equal(proof.issuedPhaseSha256,phaseSha);
 const composition=await auditComposedCorrectness(phase,timingSourceSha);
 for(const {record} of composition.records){const r=phase.components[record.arm];for(const key of ['componentPath','componentSha256','componentBytes','engineSha256','engineMetadataSha256','modulePath','bundleSha256','transpiledFiles','coreFiles','identity','checkpointProbe'])assert.equal(JSON.stringify(r[key]),JSON.stringify(record[key]),key);}
 const on=await executionPreflight({variant:'benchmark-classic-on'}),off=await executionPreflight({variant:'benchmark-classic-off'});assert.equal(on.pairSha256,phase.pairPinsSha256);assert.equal(off.pairSha256,phase.pairPinsSha256);
 for(const [arm,r] of Object.entries(phase.components)){const native=arm==='canonical-off'?off:on;assert.equal(r.engineSha256,native.pin.engineSha256);assert.equal(r.engineMetadataSha256,native.pin.metadataSha256);await streamed({path:r.componentPath,sha256:r.componentSha256,bytes:r.componentBytes});for(const file of r.transpiledFiles)await streamed({path:join(dirname(r.modulePath),file.name),sha256:file.sha256,bytes:file.bytes});}
 // Ordinary raw reports are read and authenticated in the parent only. They
 // never enter worker arguments, descriptors, helper imports or child stdout.
 for(const name of ['freshFull20And14','freshReplay','freshHttpBothHosts']){const row=phase[name];await streamed({path:row.reportPath,sha256:row.reportSha256});await streamed({path:row.rootReviewPath,sha256:row.rootReviewSha256});}
 const {compactExpected}=await import(pathToFileURL(join(old,'compact-oracle.mjs')));
 const oracle=[...JSON.parse(await readFile(join(old,'node-common-oracle.json'))).cases,...JSON.parse(await readFile(join(old,'node-control-oracle.json'))).cases];assert.equal(oracle.length,14);
 const expectedCases=[1,5].map(index=>({index,iterations:1,setupReturn:oracle[index].setup,batchRaw:JSON.stringify(compactExpected(oracle,index,1)),units:compactExpected(oracle,index,1).result.totalUnits}));
 return{phase,expectedCases,ownInputsCount,nativeEvidence:{on:{engineSha256:on.pin.engineSha256,metadataSha256:on.pin.metadataSha256},off:{engineSha256:off.pin.engineSha256,metadataSha256:off.pin.metadataSha256}}};
}
await streamed({path:process.execPath,sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'});
const before=await auditParent();
const output=resolve(outputArg??'');assert(output===outputArg&&output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Fresh exclusive output required');}catch(error){if(error.code!=='ENOENT')throw error;}
const outputParent=await lstat(dirname(output));assert(outputParent.isDirectory()&&!outputParent.isSymbolicLink());
const startingDisk=await statfs(dirname(output));assert(startingDisk.bavail*startingDisk.bsize>=2*1024**3,'2GiB starting capacity guard');
await mkdir(output);await mkdir(join(output,'workers'));
async function persist(path,value){assert(path.startsWith(output+sep));const raw=typeof value==='string'?value:JSON.stringify(value,null,2)+'\n';await writeFile(path,raw,{flag:'wx'});const handle=await open(path,'r');try{await handle.sync();}finally{await handle.close();}return{path,sha256:hash(raw),bytes:Buffer.byteLength(raw)};}
const helperPath=join(old,'instantiate.mjs');await streamed({path:helperPath,sha256:instantiateSha,bytes:646});
const selfManifest={schemaVersion:1,sourceIndexSha256:ownSha,files:['worker.mjs','contracts.mjs'].map(name=>{const row=index.files.find(row=>row.path===name);assert(row);return{path:join(here,name),sha256:row.sha256,bytes:row.bytes};}).concat([{path:helperPath,sha256:instantiateSha,bytes:646}])};
const self=await persist(join(output,'worker-self-manifest.json'),selfManifest),descriptors=[];
for(const row of schedule()){
 const r=before.phase.components[row.arm],native=before.nativeEvidence[row.arm==='canonical-off'?'off':'on'];
 const component={path:r.componentPath,sha256:r.componentSha256,bytes:r.componentBytes};
 const descriptor=validateDescriptor({schemaVersion:1,state:'PARENT_AUTHENTICATED_SMALL_MEMORY_WORKER_INPUT_V1',sourceIndexSha256:ownSha,parentPhaseSha256:phaseSha,...row,component,modulePath:r.modulePath,coreFiles:r.coreFiles,
  criticalFiles:[component,...['common_byte.core.wasm','common_byte.js','common_byte.d.ts'].map(name=>{const f=r.transpiledFiles.find(f=>f.name===name);assert(f);return{path:join(artifactRoot(row.arm),name),sha256:f.sha256,bytes:f.bytes};}),packageFile(row.arm)],
  expected:{identityRaw:JSON.stringify(r.identity),probeRaw:JSON.stringify(r.checkpointProbe),cases:before.expectedCases},nativeEvidence:{...native,notLoadedByWorker:true}});
 const label=row.comparison+'.rep-'+row.repetition+'.'+row.arm,workerOutput=join(output,'workers',label);await mkdir(workerOutput);descriptors.push({...row,label,workerOutput,descriptor:await persist(join(workerOutput,'descriptor.json'),descriptor)});
}
await persist(join(output,'started.json'),{schemaVersion:1,state:'PROCESS_RSS_SUPPLEMENT_STARTED',sourceIndexSha256:ownSha,authority:{path:authorityPath,sha256:authoritySha},phaseSha256:phaseSha,timingReportSha256:timingSha,workers:18,order:'AB/BA/AB per comparison; each worker small then large; N1 only',throughputProtocolChanged:false,throughputClaim:false,runtimeAcceptanceClaim:false});
const {collectWorker}=await import(pathToFileURL(join(old,'collect-worker.mjs'))),observations=[];let failure=null,postAudit=null;
try{
 for(const row of descriptors){
  const disk=await statfs(output);assert(disk.bavail*disk.bsize>=800*1024**2,'Stop spawning below 800MiB');process.stderr.write(JSON.stringify({stage:'memory-worker-launch',...row,descriptor:row.descriptor.sha256})+'\n');
  const captured=await collectWorker(join(here,'worker.mjs'),[self.path,self.sha256,row.descriptor.path,row.descriptor.sha256,row.workerOutput],join(output,row.label),{deadlineMs:600000,budget:{scope:'public-memory-supplement-worker',fixedCapMs:600000,adequacyNotUniversal:true}});
  // Raw stdout/stderr and terminal are durable before any assertion below.
  assert(captured.terminalExitZeroObserved&&captured.ownedGroupGone&&captured.status===0&&captured.error===null,'Fresh worker requires actual exit zero and owned cleanup');
  const actual=JSON.parse(captured.stdout);await persist(join(output,row.label+'.observed.json'),actual);assert.equal(actual.state,'SMALL_PUBLIC_PROCESS_RSS_WORKER_OBSERVED');assert.equal(actual.freshProcessPid,captured.pid);assert.equal(actual.descriptorSha256,row.descriptor.sha256);assert.equal(actual.sourceIndexSha256,ownSha);for(const key of ['arm','comparison','repetition','runOrder','position'])assert.equal(JSON.stringify(actual[key]),JSON.stringify(row[key]));assert.equal(actual.publicCalls,7);assert.deepEqual(actual.caseOrder,[1,5]);assert.equal(actual.iterationsEach,1);
  const descriptor=JSON.parse(await pinned(row.descriptor.path,row.descriptor.sha256,16384)),expected=[descriptor.expected.identityRaw,descriptor.expected.probeRaw,...descriptor.expected.cases.flatMap(c=>[c.setupReturn,c.batchRaw]),descriptor.expected.probeRaw];assert.equal(actual.rawReturns.length,7);
  for(const [i,value] of actual.rawReturns.entries()){const literal=i===2||i===4;const serialized=literal?value.rawReturn:JSON.stringify(JSON.parse(value.rawReturn));assert.equal(serialized,expected[i],'Parent independently checks retained public raw returns');}
  observations.push({...row,descriptorSha256:row.descriptor.sha256,actual,terminalPath:captured.terminalPath,wholeProcessElapsedMs:captured.wholeProcessElapsedMs});
 }
}catch(error){failure={name:error.name,message:error.message};await persist(join(output,'failure-before-source-audit.json'),{failure,completedWorkers:observations.length,partialObservationOnly:true});}
finally{try{const after=await auditParent();assert.equal(JSON.stringify(after.phase),JSON.stringify(before.phase));assert.equal(JSON.stringify(after.expectedCases),JSON.stringify(before.expectedCases));postAudit={passed:true,ownInputsCount:after.ownInputsCount};}catch(error){postAudit={passed:false,error:{name:error.name,message:error.message}};failure??=postAudit.error;}await persist(join(output,'post-operation-source-audit.json'),postAudit);}
if(failure)throw new Error('Process RSS supplement incomplete: '+failure.message);assert.equal(observations.length,18);
const result={schemaVersion:1,state:'PUBLIC_PROCESS_RSS_SUPPLEMENT_OBSERVED_EXTERNAL_EXIT_ZERO_REQUIRED',sourceIndexSha256:ownSha,authority:{path:authorityPath,sha256:authoritySha},phaseSha256:phaseSha,timingReportSha256:timingSha,workerCount:18,observations,postAudit,
 limitations:['Three fresh processes per arm/comparison; AB/BA/AB has 2:1 first-arm imbalance','Small case1 then large case5 on one instance; large retains prior instance/compiler/allocator history','RSS and maxRSS are public whole-process metrics, not guest heap, linear-memory capacity, unique physical pages or grow counts','Stream hashing and small descriptor/self validation affect process RSS; both pre/post hash baselines retained','loadCompiled combines core compile and Jco binding import; not pure compile or physical cold startup','No forced GC, allocator trim, private exports, queue counters or reset','Stage wall time is operational context only; no throughput sample, significance or universal advantage claim','Parent retains/audits full proof data outside worker processes; shared-machine/background and parent memory pressure remain uncontrolled'],throughputProtocolChanged:false,throughputClaim:false,runtimeAcceptanceClaim:false};
const resultFile=await persist(join(output,'results.json'),result),files=[],links=[];
async function inventory(root){for(const item of await readdir(root,{withFileTypes:true})){const path=join(root,item.name);if(item.isDirectory())await inventory(path);else if(item.isSymbolicLink())links.push({path,linkText:await readlink(path),resolvedTarget:await realpath(path)});else{assert(item.isFile());const info=await lstat(path),digest=createHash('sha256');for await(const chunk of createReadStream(path))digest.update(chunk);files.push({path,sha256:digest.digest('hex'),bytes:info.size});}}}
await inventory(output);assert.equal(links.length,0,'No output symlinks expected');
await persist(join(output,'completion.json'),{schemaVersion:1,state:'PROCESS_RSS_SUPPLEMENT_FILES_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED',sourceIndexSha256:ownSha,authoritySha256:authoritySha,result:resultFile,files,links,workerCount:18,requiresActualExternalTerminalExitZero:true,throughputClaim:false,runtimeAcceptanceClaim:false});
console.log(JSON.stringify({state:result.state,output,workers:18,requiresActualExternalTerminalExitZero:true}));
