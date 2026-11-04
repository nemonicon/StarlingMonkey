// Future explicit correctness/packaging action. Never run by source tests.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,symlink,statfs,readlink,realpath} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {performance} from 'node:perf_hooks';
import {executionPreflight} from '../measurement-execution-activated-v2/runtime-preflight.mjs';
import {bundleMatched} from './bundle-stock.mjs';
import {parentRoot,parentIndexSha256,verifyCollector,verifyThreeArmAuthority} from './provenance.mjs';
import {cases,arms} from '../measurement-execution-activated-v2/protocol.mjs';
import {loadCompiled} from '../measurement-execution-activated-v2/instantiate.mjs';
import {requireExactJSON} from '../measurement-execution-activated-v2/bounded-comparison.mjs';
import {runOwnedCommand,persistFile} from '../measurement-execution-activated-v2/owned-host.mjs';
import {deadlinePolicy} from '../measurement-execution-activated-v2/deadline-policy.mjs';
const collectorHere=dirname(fileURLToPath(import.meta.url)),here=parentRoot,hash=raw=>createHash('sha256').update(raw).digest('hex');
const [indexSha,authorityPath,authoritySha]=process.argv.slice(2);assert(/^[0-9a-f]{64}$/.test(indexSha??''));
await verifyCollector(collectorHere,indexSha);
const reviewedThree=await verifyThreeArmAuthority(authorityPath,authoritySha);
const recheckCollector=async()=>{await verifyCollector(collectorHere,indexSha);await verifyThreeArmAuthority(authorityPath,authoritySha);};
const on=await executionPreflight({variant:'benchmark-classic-on'}),off=await executionPreflight({variant:'benchmark-classic-off'});
const output=resolve(process.env.NODE_COMPAT_COMMON_BYTE_STOCK_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Fresh output required');}catch(error){if(error.code!=='ENOENT')throw error;}
const initialDisk=await statfs(dirname(output));assert(initialDisk.bavail*initialDisk.bsize>=2*1024**3,'2GiB initial storage guard');
const {loadToolchain}=await import(pathToFileURL(join(on.toolSourceRoot,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();
const {loadComponentizer}=await import(pathToFileURL(join(on.toolSourceRoot,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);
const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const common=JSON.parse(await readFile(join(here,'node-common-oracle.json'))),controls=JSON.parse(await readFile(join(here,'node-control-oracle.json')));
const oracle=[...common.cases,...controls.cases];assert.equal(oracle.length,14);
for(let i=0;i<cases.length;i++){assert.equal(oracle[i].id,cases[i].id);assert.equal(oracle[i].iterations,cases[i].iterations);}
const adapter=join(on.toolSourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');assert.equal(hash(await readFile(host)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
const {decodeCliString}=await import(pathToFileURL(join(on.toolSourceRoot,'tests/node-compat/foundations/native-scalar-harness.mjs')));
await mkdir(output,{recursive:false});await writeFile(join(output,'package.json'),'{"type":"module"}\n',{flag:'wx'});await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));
await mkdir(join(output,'progress'));await mkdir(join(output,'processes'));
const records=[],capturedPaths=new Set();let progressSequence=0,operationFailure=null,postAudit=null;
const write=async(path,data,options)=>{await writeFile(path,data,options);capturedPaths.add(path);},register=path=>capturedPaths.add(path);
async function save(path,data){return persistFile({output,write,path,data:typeof data==='string'?data:JSON.stringify(data,null,2)+'\n'});}
async function progress(arm,stage,index=null,call=null,detail={}){const disk=await statfs(output);assert(disk.bavail*disk.bsize>=800*1024**2,'Stop writes below800MiB');const event={sequence:++progressSequence,arm,stage,index,call,atUtc:new Date().toISOString(),partialObservationOnly:true,...detail};process.stderr.write(JSON.stringify(event)+'\n');return save(join(output,'progress',String(progressSequence).padStart(5,'0')+'.json'),event);}
try{
for(const arm of ['stock-on']){
 await progress(arm,'bundle-and-componentize');
 const admission=arm==='canonical-off'?off:on,directory=join(output,arm);await mkdir(directory);await admission.recheck();
 const bundle=await bundleMatched(toolchain,admission,arm);await writeFile(join(directory,'application.bundle.mjs'),bundle.code,{flag:'wx'});await writeFile(join(directory,'bundle-graph.json'),JSON.stringify(bundle.graph,null,2)+'\n',{flag:'wx'});
 const wit='package test:common-byte; world test { export setup: func(index: u32) -> s32; export inspect: func(index: u32) -> string; export batch: func(index: u32, iterations: u32) -> string; export identity: func() -> string; export checkpoint-probe: func() -> string; }';
 const componentizeStart=performance.now(),{component,interfaceAudit}=await selected.componentize(bundle.code,{engine:admission.enginePath,preview2Adapter:adapter,witWorld:wit,worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]}),componentizationWallMs=performance.now()-componentizeStart;
 await admission.recheck();assert.deepEqual(interfaceAudit.emittedImports,[]);const emittedWit=await componentWit(component);assert.doesNotMatch(emittedWit,/\bimport\b/);
 const exports=(emittedWit.match(/export\s+[\w-]+:\s*func\([^;]*;/g)??[]).map(value=>value.replace(/\s+/g,' ').trim()).sort();
 assert.deepEqual(exports,['export setup: func(index: u32) -> s32;','export inspect: func(index: u32) -> string;','export batch: func(index: u32, iterations: u32) -> string;','export identity: func() -> string;','export checkpoint-probe: func() -> string;'].sort());
 const componentPath=join(directory,'common-byte.component.wasm');await writeFile(componentPath,component,{flag:'wx'});await writeFile(join(directory,'emitted.wit'),emittedWit,{flag:'wx'});
 const transpileStart=performance.now(),{files}=await transpile(component,{name:'common_byte',instantiation:'async'}),transpileWallMs=performance.now()-transpileStart,transpiledFiles=[];
 for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(directory,name)),{recursive:true});await writeFile(join(directory,name),bytes,{flag:'wx'});transpiledFiles.push({name,sha256:hash(bytes),bytes:bytes.length});}
 const record={arm,guestSourceFamilyIndexSha256:parentIndexSha256,collectorSourceIndexSha256:indexSha,componentPath,componentSha256:hash(component),componentBytes:component.length,enginePath:admission.enginePath,engineSha256:admission.pin.engineSha256,engineMetadataSha256:admission.pin.metadataSha256,
  modulePath:join(directory,'common_byte.js'),coreFiles:Object.keys(files).filter(name=>name.endsWith('.wasm')),transpiledFiles,bundleSha256:bundle.graph.bundleSha256,emittedImports:interfaceAudit.emittedImports,interfaceAudit,graph:bundle.graph,packager:selected.provenance,componentizationWallMs,transpileWallMs,buildTimingScope:'Sequential host packaging wall time; cold cache and isolated snapshot time not established'};
 await save(join(directory,'component-record.before-observations.json'),record);await mkdir(join(directory,'calls'));await mkdir(join(directory,'processes'));
 const instantiate=await loadCompiled(record);let recorded=false,callSequence=0;
 async function writeCounterexample(value){assert(!recorded);recorded=true;await writeFile(join(directory,'counterexample.json'),JSON.stringify(value,null,2)+'\n',{flag:'wx'});}
 const expectedIdentity={defaultGraph:true,promisesGraph:true,eventEmitterPrototype:true,selectedTickType:'function',decoderA:'A',bufferView:true,bufferSameAsBefore:arm!=='stock-on',globalSameAsProvider:true,beforeBufferType:'function',globalChangedDuringProvider:arm==='stock-on'};
 async function observeCall(kind,index,call,invoke){const id=String(++callSequence).padStart(4,'0')+'-'+kind;await progress(arm,'call-start',index,call,{id,kind,scenario:index===null?null:cases[index].id,iterations:index===null?null:cases[index].iterations});const start=performance.now();
  try{const raw=await invoke();const rawFile=await save(join(directory,'calls',id+'.raw.txt'),raw);const value=JSON.parse(raw);const observedFile=await save(join(directory,'calls',id+'.observed.json'),value);await progress(arm,'call-observed',index,call,{id,rawFile,observedFile,operationalElapsedMs:performance.now()-start});return value;}
  catch(error){await save(join(directory,'calls',id+'.failure.json'),{id,arm,kind,index,call,error:{name:error.name,message:error.message},partialObservationOnly:true});throw error;}}
 async function identity(instance){const value=await observeCall('identity',null,null,()=>instance.exports.identity());await requireExactJSON({label:'provider-identity',actual:value,expected:expectedIdentity,writeCounterexample});return value;}
 function probe(value){assert.equal(value.callbacks,1);assert.deepEqual([...value.trace].sort(),['microtask','selected-tick']);assert.equal(value.queueDepthObserved,false);assert.equal(value.terminalQueueEmptyObserved,false);return value;}
 async function rotation(instance,start){const rows=[];for(let i=0;i<14;i++){const actual=await observeCall('inspect',i,start+i,()=>instance.exports.inspect(i));await requireExactJSON({label:'full-trace-'+i,actual,expected:{calls:start+i,setup:oracle[i].setup,result:oracle[i].expected},writeCounterexample});rows.push(actual);await progress(arm,'call-validated',i,start+i);}return rows;}
 const retained=await instantiate(),retainedIdentity=await identity(retained),retainedProbe=probe(await observeCall('checkpoint-retained',null,null,()=>retained.exports.checkpointProbe())),rounds=[];
 for(let round=0;round<3;round++)rounds.push(await rotation(retained,round*14+1));
 const afterProbe=probe(await observeCall('checkpoint-after',null,null,()=>retained.exports.checkpointProbe()));await requireExactJSON({label:'retained-checkpoint-probe',actual:afterProbe,expected:retainedProbe,writeCounterexample});
 const fresh=await instantiate();await identity(fresh);const freshProbe=probe(await observeCall('checkpoint-fresh',null,null,()=>fresh.exports.checkpointProbe()));await requireExactJSON({label:'fresh-checkpoint-probe',actual:freshProbe,expected:retainedProbe,writeCounterexample});const freshRows=await rotation(fresh,1);
 const wt=[];for(let i=-2;i<14;i++){
  const expression=i===-2?'identity()':i===-1?'checkpoint-probe()':'inspect('+i+')';
  await progress(arm,'fresh-Wasmtime-start',i,1,{expression,scenario:i<0?null:cases[i].id,iterations:i<0?null:cases[i].iterations,deadlineMs:deadlinePolicy.publicCaseMs});
  const actual=await runOwnedCommand({output:directory,name:'wt-'+(i+2),executable:host,args:['run','--invoke',expression,componentPath],write,register,timeoutMs:deadlinePolicy.publicCaseMs,maxOutputBytes:16*1024*1024,graceMs:5000,heartbeatMs:30000,onProgress:detail=>process.stderr.write(JSON.stringify({arm,index:i,stage:'fresh-Wasmtime-heartbeat',...detail})+'\n')});
  await progress(arm,'fresh-Wasmtime-collected',i,1,{expression,terminalPath:actual.terminalPath,status:actual.status,signal:actual.signal,spawnError:actual.spawnError,timedOut:actual.timedOut,stdoutFile:actual.stdoutFile,stderrFile:actual.stderrFile});
  assert.equal(actual.terminalExitZeroObserved,true,'Owned Wasmtime terminal failed; inspect persisted status');assert.equal(actual.ownedGroupGone,true);assert.equal(actual.status,0);
  const value=JSON.parse(decodeCliString(actual.stdout.trim()));const observedFile=await save(join(directory,'calls','wt-'+(i+2)+'.observed.json'),value);await progress(arm,'fresh-Wasmtime-observed',i,1,{expression,observedFile});
  await requireExactJSON({label:'fresh-WT-'+i,actual:value,expected:i===-2?expectedIdentity:i===-1?retainedProbe:{calls:1,setup:oracle[i].setup,result:oracle[i].expected},context:{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath},writeCounterexample});wt.push({expression,status:actual.status,signal:actual.signal,terminalPath:actual.terminalPath,observed:value});
 }
 record.correctnessPassed=true;record.identityPassed=true;record.checkpointProbePassed=true;record.identity=retainedIdentity;record.checkpointProbe=retainedProbe;
 record.correctness={retainedRotations:3,rounds,freshRows,wasmtime:wt};record.declaredSchedulerLimits=admission.metadata.internalTickPolicy.limits;
 record.schedulerBudget={override:false,cumulativeWorkloadIterationBounds:[1,16],nativeQueueCountersObserved:false,provider:arm==='stock-on'?'Unmodified queueMicrotask FIFO; its callbacks are not native private-nextTick work-counter observations':'Actual private nextTick callable; success under configured limit, no counter observability'};
 records.push(record);await save(join(directory,'arm-results.partial.json'),record);await progress(arm,'arm-complete',null,null,{partialObservationOnly:true});await admission.recheck();
}
assert.equal(records.length,1);assert.equal(records[0].arm,'stock-on');await recheckCollector();
}catch(error){operationFailure=error;try{await save(join(output,'failure-before-source-audit.json'),{error:{name:error.name,message:error.message},completedArms:records.map(row=>row.arm),partialObservationOnly:true,runtimeAcceptanceClaim:false});}catch(storageError){process.stderr.write(JSON.stringify({event:'failure-record-write-failed',original:{name:error.name,message:error.message},storage:{name:storageError.name,message:storageError.message}})+'\n');}}
finally{try{postAudit=await runOwnedCommand({output,name:'post-operation-source-audit',executable:process.execPath,args:[join(here,'audit-inputs.mjs'),parentIndexSha256],write,register,timeoutMs:deadlinePolicy.sourceAuditMs,maxOutputBytes:4*1024*1024,graceMs:5000,heartbeatMs:30000,onProgress:detail=>process.stderr.write(JSON.stringify({stage:'post-operation-source-audit-heartbeat',...detail})+'\n')});await save(join(output,'post-operation-source-audit.json'),{status:postAudit.status,signal:postAudit.signal,spawnError:postAudit.spawnError,timedOut:postAudit.timedOut,terminalPath:postAudit.terminalPath,passed:postAudit.terminalExitZeroObserved&&postAudit.ownedGroupGone,originalFailure:operationFailure?{name:operationFailure.name,message:operationFailure.message}:null});assert(postAudit.terminalExitZeroObserved&&postAudit.ownedGroupGone,'Post-operation source audit failed');}catch(auditError){if(!operationFailure)operationFailure=auditError;else process.stderr.write(JSON.stringify({stage:'post-operation-source-audit-failed',original:{name:operationFailure.name,message:operationFailure.message},audit:{name:auditError.name,message:auditError.message}})+'\n');}}
try{await recheckCollector();}catch(error){if(!operationFailure)operationFailure=error;}
if(operationFailure)throw operationFailure;
const report={schemaVersion:1,state:'ACTUAL_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_PASSED',collectorSourceIndexSha256:indexSha,guestSourceFamilyIndexSha256:parentIndexSha256,pairPinsSha256:on.pairSha256,reviewedThreeArmAuthority:{path:authorityPath,sha256:authoritySha},failedParentRawOuterExit:1,records,commonCases:8,controlCases:6,controlsSubtracted:false,original28CounterexamplesPreserved:true,timingAllowed:false,
 queueEmptyProof:false,rootIsolationProof:false,cppStateMachineClaim:false,requiresIndependentExitCodeZero:true};
const reportPath=join(output,'stock-correctness-results.json');await writeFile(reportPath,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
const files=new Set([...capturedPaths,reportPath,join(output,'package.json')]);
for(const row of records){const directory=dirname(row.componentPath);for(const name of ['application.bundle.mjs','bundle-graph.json','emitted.wit'])files.add(join(directory,name));files.add(row.componentPath);for(const file of row.transpiledFiles)files.add(join(directory,file.name));}
const outputs=[];for(const path of [...files].sort()){assert(path.startsWith(output+'/'));const info=await lstat(path);assert(info.isFile()&&!info.isSymbolicLink());const raw=await readFile(path);outputs.push({path,sha256:hash(raw),bytes:raw.length});}
const linkPath=join(output,'node_modules');assert((await lstat(linkPath)).isSymbolicLink());assert.equal(await readlink(linkPath),join(toolchain.directory,'node_modules'));assert.equal(await realpath(linkPath),await realpath(join(toolchain.directory,'node_modules')));
const links=[{path:linkPath,linkText:await readlink(linkPath),resolvedTarget:await realpath(linkPath)}];
await recheckCollector();
await writeFile(join(output,'stock-completion.json'),JSON.stringify({schemaVersion:1,state:'STOCK_ONLY_OUTPUTS_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED',collectorSourceIndexSha256:indexSha,guestSourceFamilyIndexSha256:parentIndexSha256,pairPinsSha256:on.pairSha256,result:{path:reportPath,sha256:hash(await readFile(reportPath)),bytes:(await lstat(reportPath)).size},outputs,links,requiresIndependentRawOuterExitZero:true,wholeOldParentPassed:false,timingAllowed:false,runtimeAcceptanceClaim:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,output,arms:1,commonCases:8,controlCases:6,imports:[],completion:'stock-completion.json',requiresIndependentRawOuterExitZero:true}));
