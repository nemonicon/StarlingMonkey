// Thin owned coordinator: Node file reference, existing Wasmtime host, two raw GETs.
import assert from 'node:assert/strict';
import {createServer} from 'node:net';
import {mkdir,lstat,readFile,statfs} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {context,layout,originPort,launch,read,row,durable,jsonBytes,errorData,pause,waitBounded,tcpOnce,clean} from './io.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
async function main(){
 assert.equal(process.argv.length,3);const authpath=resolve(process.argv[2]);const{a,plan,authorityRef,protect}=await context(HERE,authpath);
 const output=layout(plan,a.runId),disk=await statfs(dirname(output));assert(Number(disk.bavail)*Number(disk.bsize)>=1073741824);
 await mkdir(output,{mode:0o700});
 const result={schemaVersion:1,state:'GZIP_COMPOSITION_CONTROLLER_IN_PROGRESS_V1',runId:a.runId,rootAuthority:authorityRef,sourceIndex:a.sourceIndex,plan:a.plan,origin:a.origin,reference:null,server:null,wire:null,validation:null,errors:[],inputsPreserved:false,normalWireCaptured:false,compositionProfilePassed:false,privateWasiFinishCountProved:false,nativeResourceCountsProved:false,fullNextAccepted:false,adoption:false};
 const save=()=>durable(join(output,'result.json'),jsonBytes(result));await save();
 const handles=[],children=[];let lease=null,host=null,stopping=false;
 async function runPhase(phase){
  const wrapper=await launch({exe:plan.python.path,args:['-I','-B',join(HERE,'phase-owner.py'),authpath,phase],cwd:output,env:{...process.env}},phase+'-owner-cli',output,handles,children);
  result[phase]={...wrapper.record,observation:null,rawCapture:null};await save();
  const status=await wrapper.done;result[phase].exit=status;await save();
  const rawPath=join(output,phase==='reference'?'node-reference/reference.json':'wire/wire-capture.json');
  try{result[phase].rawCapture=await row(rawPath);await save();}catch(error){if(error.code!=='ENOENT')throw error;}
  const ownerRoot=join(output,phase==='reference'?'node-reference-owner':'wire-owner'),observationRef=await row(join(ownerRoot,'observation.json')),observation=await read(observationRef.path);
  result[phase].observation=observationRef;await save();
  assert.deepEqual(status,{code:0,signal:null,error:null});assert.equal(observation.captureCompletedCleanly,true);assert.deepEqual(observation.rootAuthority,authorityRef);assert.equal(observation.origin,a.origin);
  assert.deepEqual(observation.phaseAuthority,phase==='reference'?a.nodeReferenceAuthority:a.wireAuthority);await verifyTerminal(observation.terminal,observation.phaseAuthority);
  result[phase].rawCapture=await row(join(output,phase==='reference'?'node-reference/reference.json':'wire/wire-capture.json'));await save();
 }
 async function verifyTerminal(ref,grant){const terminal=await read(ref.path);assert.deepEqual(await row(ref.path),ref);assert(clean(terminal));assert.deepEqual(terminal.authority,grant);}
 async function closeLogs(){
  while(handles.length){const handle=handles.pop();try{await handle.sync();}catch(error){result.errors.push({stage:'log-sync',...errorData(error)});}try{await handle.close();}catch(error){result.errors.push({stage:'log-close',...errorData(error)});}}
 }
 async function streamRows(){
  for(const child of children){child.record.exit=child.status;const target=child===host?result.server:child.record.label==='reference-owner-cli'?result.reference:child.record.label==='wire-owner-cli'?result.wire:child.record.label==='data-verifier'?result.validation:null;
   for(const key of ['stdout','stderr'])try{if(typeof child.record[key]==='string')child.record[key]=await row(child.record[key]);if(target)target[key]=child.record[key];}catch(error){result.errors.push({stage:'stream-descriptor',...errorData(error)});}}
 }
 try{
  // The independent file-only Node reference completes before the guest server starts.
  await runPhase('reference');
  for(const name of ['tmp','xdg-cache','xdg-config','xdg-data'])await mkdir(join(output,name),{mode:0o700});
  const port=originPort(a.origin);lease=createServer();await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port,exclusive:true},yes);});assert.equal(lease.address().port,port);
  result.portLease={origin:a.origin,port,singleAttempt:true,fallbackAllowed:false};await save();await protect();
  await new Promise((yes,no)=>lease.close(error=>error?no(error):yes()));lease=null;
  const args=['serve','--no-logging-prefix','--addr','127.0.0.1:'+port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','128','--idle-instance-timeout','60s',a.component.path];
  assert(!args.includes('--dir')&&!args.includes('--env'));assert.deepEqual(plan.requiredWasmtimeFlags,['--no-logging-prefix']);
  host=await launch({exe:plan.wasmtime.path,args,cwd:output,env:{...process.env,TMPDIR:join(output,'tmp'),XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}},'wasmtime',output,handles,children);
  result.server={...host.record,shutdownRequested:false,sigintSent:false,forcedCleanup:false};void host.done.then(status=>{if(!stopping)result.errors.push({stage:'host-exited-before-owned-stop',status});});await save();
  const deadline=Date.now()+30000;let ready=false;
  while(Date.now()<deadline){assert.equal(host.status,null);let logs='';for(const path of [host.record.stdout,host.record.stderr]){assert((await lstat(path)).size<=plan.listenerLogByteCap);logs+=await readFile(path,'utf8');}
   const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(logs)?.[1];if(found){assert.equal(found,a.origin);ready=true;break;}await pause(plan.readinessPollMilliseconds);}
  assert(ready,'Exact gzip listener missing');assert(await tcpOnce(port,plan.tcpConnectMilliseconds));assert.equal(host.status,null);
  result.readiness={exactListener:true,tcpConnect:true,httpWarmupRequests:0,guestCallObservedAtReadiness:false};await save();
  result.serverAliveBeforeWire=true;await runPhase('wire');assert.equal(host.status,null);result.serverAliveAfterWire=true;result.normalWireCaptured=true;await save();
 }catch(error){result.errors.push({stage:'owned-phase-or-capture',...errorData(error)});}
 finally{
  if(lease?.listening)try{await new Promise(resolve=>lease.close(()=>resolve()));}catch(error){result.errors.push({stage:'lease-close',...errorData(error)});}
  try{if(host&&host.status===null){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.child.kill('SIGINT');await waitBounded(host.done,5000);if(host.status===null){result.server.forcedCleanup=true;host.child.kill('SIGKILL');await waitBounded(host.done,5000);}}if(result.server)result.server.exit=host?.status??null;}catch(error){result.errors.push({stage:'host-shutdown',...errorData(error)});}
  for(const child of children)if(child!==host&&child.status===null){result.errors.push({stage:'unfinished-owned-phase',label:child.record.label});child.child.kill('SIGTERM');if(await waitBounded(child.done,5000)===null){child.child.kill('SIGKILL');await waitBounded(child.done,5000);}}
  await closeLogs();await streamRows();
  try{await protect();result.inputsPreserved=true;}catch(error){result.errors.push({stage:'final-original-protection',...errorData(error)});}
  await save();
 }
 // Raw data and the normal host stop are retained before any semantic comparator.
 if(result.reference?.rawCapture&&result.wire?.rawCapture&&result.server?.stdout){
  await durable(join(output,'raw-publication.json'),jsonBytes({nodeReference:result.reference.rawCapture,wireCapture:result.wire.rawCapture,guestStdout:result.server.stdout,semanticValidationInvoked:false}),true);
  try{
   const validator=await launch({exe:plan.python.path,args:['-I','-B',plan.dataVerifier.path,'--capture',result.wire.rawCapture.path,'--node-reference',result.reference.rawCapture.path,'--guest-log',result.server.stdout.path],cwd:output,env:{...process.env}},'data-verifier',output,handles,children);
   result.validation={...validator.record,exit:await validator.done};if(result.validation.exit.code===0&&result.validation.exit.signal===null&&result.validation.exit.error===null)result.compositionProfilePassed=true;
  }catch(error){result.errors.push({stage:'retained-data-validation',...errorData(error)});}
  await closeLogs();await streamRows();
 }
 const stopped=result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&result.server?.forcedCleanup===false&&result.server?.exit?.code===0&&result.server.exit.signal===null&&result.server.exit.error===null;
 result.passed=result.errors.length===0&&result.inputsPreserved&&result.normalWireCaptured&&result.compositionProfilePassed&&stopped;
 result.state=result.passed?'GZIP_COMPOSITION_CAPTURED_UNREVIEWED_V1':'GZIP_COMPOSITION_FAILED_RAW_PRESERVED_V1';await save();
 console.log(JSON.stringify({state:result.state,passed:result.passed,errors:result.errors,fullNextAccepted:false}));process.exitCode=result.passed?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
