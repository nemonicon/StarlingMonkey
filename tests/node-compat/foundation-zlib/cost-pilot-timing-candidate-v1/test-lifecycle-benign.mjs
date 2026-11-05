// Explicit Root-approved real BENIGN HOST lifecycle regression, not benchmark.
import {mkdtemp,mkdir,readFile,readdir} from 'node:fs/promises';
import {dirname,join,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {descriptor,hash} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {streamHash} from '../cost-tooling-candidate-v3/context.mjs';
import {runOwnedCommand} from './owned-lifecycle.mjs';
import {need} from './planner.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),refs=JSON.parse(await readFile(join(HERE,'references.json'))),node=descriptor(refs.node);
await streamHash(node,{maximumBytes:128*1024*1024});
const container=await mkdtemp('/private/tmp/starling-node-compat/zlib-cost-lifecycle-benign-v1-'),output=await DurableOutput.create(join(container,'capture')),outcomes=[];
const write=(name,value)=>output.write(name,value,{json:true}),local=path=>relative(output.root,path);
try{
 await mkdir(join(output.root,'jobs'),{mode:0o700});await mkdir(join(output.root,'processes'),{mode:0o700});
 await write('scope.json',{schemaVersion:1,state:'ROOT_AUTHORIZED_BOUNDED_BENIGN_HOST_LIFECYCLE_REGRESSION_DATA_V1',authorization:'Explicit Root collaboration instruction, not codec phase authority',cases:['normal','unfinished-raw0','blocking'],actualNodeHostChildrenAllowed:true,guestCodecProviderNativeJcoWasmtimePilotTimingAllowed:false,processSignallingScope:'only the freshly spawned owned child session'});
 for(const mode of['normal','unfinished-raw0','blocking']){
  const registered=new Set(),jobRoot=join(output.root,'jobs',mode),status=await runOwnedCommand({output:output.root,name:mode,executable:node.path,args:[join(HERE,'benign-child-fixture.mjs'),mode,jobRoot],
   timeoutMs:3000,publicCallTimeoutMs:mode==='blocking'?100:500,phaseDeadlineMonotonicMs:Number(process.hrtime.bigint()/1000000n)+5000,maxOutputBytes:65536,
   write:(path,data)=>output.write(local(path),data),register:path=>registered.add(path)});
  for(const path of registered){const b=await readFile(path),name=local(path);output.rows.set(name,{path:name,sha256:hash(b),bytes:b.length});}
  async function adopt(path){for(const entry of await readdir(path,{withFileTypes:true})){const full=join(path,entry.name);if(entry.isDirectory())await adopt(full);else{need(entry.isFile()&&!entry.isSymbolicLink(),'ordinary benign child evidence');const b=await readFile(full),name=local(full);output.rows.set(name,{path:name,sha256:hash(b),bytes:b.length});}}}
  await adopt(jobRoot);const terminalData=JSON.parse(await readFile(status.terminalPath));outcomes.push({mode,status,terminalData});await write('observations/'+mode+'.json',{schemaVersion:1,mode,terminalData,benignHostOnly:true,acceptedBenchmarkResult:false});
 }
 // All raw captures/terminals are durable before any expected-outcome assertions.
 const normal=outcomes[0].status,unfinished=outcomes[1].status,blocking=outcomes[2].status;
 need(normal.status===0&&normal.terminalExitZeroObserved===true&&normal.ownedGroupGone&&normal.errors.length===0&&normal.signals.length===0,'normal real ACK/end lifecycle succeeds');
 need(unfinished.status===0&&unfinished.ownedGroupGone&&unfinished.terminalExitZeroObserved===false&&unfinished.errors.length>0,'raw0 with unfinished call is rejected');
 need(blocking.timedOut===true&&blocking.ownedGroupGone&&blocking.terminalExitZeroObserved===false&&blocking.signals.some(s=>s.signal==='SIGKILL'),'external parent terminates synchronous fake workload and reaps owned group');
 for(const item of outcomes){need(item.status.stderrFile.bytes===0&&item.status.exactEnvironment.RAYON_NUM_THREADS==='1'&&item.status.parentFsyncBeforeCallAck===true,'retained environment/ACK scope and empty stderr');}
 const result=await write('results.json',{schemaVersion:1,state:'BOUNDED_BENIGN_HOST_LIFECYCLE_REGRESSIONS_PASSED_V1',root:output.root,outcomes:outcomes.map(({mode,status})=>({mode,pid:status.pid,rawExitCode:status.status,signal:status.signal,timedOut:status.timedOut,ownedGroupGone:status.ownedGroupGone,terminalExitZeroObserved:status.terminalExitZeroObserved,terminal:status.terminalPath,stdout:status.stdoutFile,stderr:status.stderrFile})),normalPassed:true,unfinishedRawZeroRefused:true,synchronousFakeTerminatedExternally:true,actualHostInfrastructureExecuted:true,preflightGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted:false,operationalAdmission:false});
 await output.recheck();const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]}),completion=await write('completion.json',{schemaVersion:1,state:'BENIGN_HOST_REGRESSION_CAPTURE_COMPLETE',result,index});await output.recheck();
 process.stdout.write(JSON.stringify({state:'BOUNDED_BENIGN_HOST_LIFECYCLE_REGRESSIONS_PASSED_V1',root:output.root,result,index,completion})+'\n');
}catch(error){try{await write('failure.json',{schemaVersion:1,state:'BENIGN_HOST_REGRESSION_FAILED_UNACCEPTED',message:error.message,outcomes:outcomes.map(({mode,terminalData})=>({mode,terminalData})),partialRawPreserved:true});}catch{}process.stdout.write(JSON.stringify({state:'BENIGN_HOST_REGRESSION_FAILED_UNACCEPTED',root:output.root})+'\n');throw error;}
finally{await output.close();}
