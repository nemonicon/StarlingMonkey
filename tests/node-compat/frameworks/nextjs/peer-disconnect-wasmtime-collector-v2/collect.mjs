// Dormant peer-close collection; no action without exact late Root authority.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createServer} from 'node:net';
import {createReadStream} from 'node:fs';
import {readFile,writeFile,mkdir,lstat,readdir,open,realpath} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
const read=async p=>JSON.parse(await readFile(p,'utf8'));
async function row(path){const h=createHash('sha256');let bytes=0;for await(const b of createReadStream(path)){h.update(b);bytes+=b.length;}return{path,sha256:h.digest('hex'),bytes};}
async function verify(r){assert.deepEqual(await row(r.path),r);}
async function family(ref){await verify(ref);const root=dirname(ref.path),j=await read(ref.path),names=j.files.map(x=>x.path);assert.equal(new Set(names).size,names.length);const actual=await walk(root);assert.deepEqual(actual.files.filter(x=>x!=='index.json').sort(),[...names].sort());assert.equal(actual.links.length,0);for(const r of j.files){assert(!r.path.startsWith('/')&&!r.path.split('/').includes('..'));await verify({...r,path:join(root,r.path)});}}
async function walk(root){const out={files:[],dirs:['.'],links:[]};async function visit(dir){for(const name of(await readdir(dir)).sort()){const path=join(dir,name),s=await lstat(path),r=relative(root,path);if(s.isSymbolicLink())out.links.push(r);else if(s.isDirectory()){out.dirs.push(r);await visit(path);}else{assert(s.isFile(),'Only regular files/directories');assert.equal(s.nlink,1);out.files.push(r);}}}await visit(root);return out;}
async function boundedWait(promise,ms){let timer;try{await Promise.race([promise,new Promise(resolve=>{timer=setTimeout(resolve,ms);})]);}finally{clearTimeout(timer);}}
async function launch(exe,args,id,directory){const stdout=join(directory,id+'.stdout.log'),stderr=join(directory,id+'.stderr.log'),out=await open(stdout,'wx',0o600),err=await open(stderr,'wx',0o600);handles.push(out,err);const child=spawn(exe,args,{cwd:directory,stdio:['ignore',out.fd,err.fd],env:{...process.env,XDG_CACHE_HOME:join(directory,'xdg-cache'),XDG_CONFIG_HOME:join(directory,'xdg-config'),XDG_DATA_HOME:join(directory,'xdg-data')}});let status=null;const done=new Promise(resolve=>{child.once('error',error=>{status={code:null,signal:null,error:errorData(error)};resolve(status);});child.once('exit',(code,signal)=>{status={code,signal,error:null};resolve(status);});});return{child,done,stdout,stderr,get status(){return status;},command:[exe,...args]};}

const errorData=e=>({name:e?.name??'Error',message:e?.message??String(e),stack:e?.stack??null});
const authpath=resolve(process.argv[2]),a=await read(authpath),plan=await read(join(here,'plan.json'));
const authorityRef=await row(authpath);
assert.equal(a.state,'ROOT_PEER_DISCONNECT_HTTP_PROBE_AUTHORIZED_V2');assert.deepEqual(a.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(a.plan,await row(join(here,'plan.json')));
assert(typeof a.runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId)?.[0]===a.runId);
assert.equal(a.firstHostCase,'peer-'+a.runId);assert.deepEqual(a.constructionCallerIndex,plan.constructorSourceIndex);
for(const k of ['ordinaryProbeAllowed','loopbackServeAllowed','normalPeerCloseControlsAllowed'])assert.equal(a[k],true);
for(const k of ['appMountAllowed','componentConstructionAllowed','fullNextAcceptanceAllowed','adoptionAllowed'])assert.equal(a[k],false);
assert(Array.isArray(a.engineBuildEvidence)&&a.engineBuildEvidence.length>0);assert(Array.isArray(a.nativeProtectedInputs)&&a.nativeProtectedInputs.length>0);assert(Array.isArray(a.nativeSourceFamilies));
const extraArtifactRefs=[];
async function protect(){await verify(authorityRef);await family(a.sourceIndex);await family(a.constructionCallerIndex);for(const ref of [...plan.sourceFamilies,...a.nativeSourceFamilies])await family(ref);for(const key of ['node','wasmtime','monitor','adapter','probeEntry','referenceHostChecks','referenceResults','referenceEvidence','referenceBundle'])await verify(plan[key]);for(const key of ['engine','nativeMetadata','constructionResult','component','componentAudit','constructionOuterTerminal','constructionWorldGuard']){assert.equal(await realpath(a[key].path),a[key].path);await verify(a[key]);}for(const ref of [...extraArtifactRefs,...a.engineBuildEvidence,...a.nativeProtectedInputs])await verify(ref);}
await protect();
const construction=await read(a.constructionResult.path),audit=await read(a.componentAudit.path);
for(const ref of [construction.rootAuthority,construction.plan,...construction.artifacts.engineBuildEvidence]){await verify(ref);extraArtifactRefs.push(ref);}
const constructorAuthority=await read(construction.rootAuthority.path),constructorPlan=await read(construction.plan.path);
assert.equal(constructorAuthority.state,'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2');assert.deepEqual(constructorAuthority.callerIndex,a.constructionCallerIndex);assert.equal(constructorAuthority.entryMode,'peer-disconnect');assert.equal(constructorAuthority.componentizeInitAllowed,true);for(const key of ['ordinaryExportsAllowed','httpServingAllowed','networkAllowed','nativeBuildAllowed','packageMutationAllowed','globalPinMutationAllowed','debugAllowed','applicationMountAtInitAllowed','deployedResnapshotAllowed'])assert.equal(constructorAuthority[key],false);
assert.deepEqual(constructorPlan.inputSourceIndex,plan.probeSourceIndex);assert.deepEqual(constructorPlan.entries,{'peer-disconnect':plan.probeEntry});assert.equal(constructorPlan.worldName,'next-http');assert.equal(constructorPlan.witDirectory,plan.witDirectory);assert.deepEqual(constructorPlan.selectedInterfaces,plan.selectedInterfaces);
const {validateNative}=await import('./native-model.mjs');validateNative(await read(a.nativeMetadata.path),a,constructorAuthority);
assert.equal(construction.state,'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');assert.equal(construction.passed,true);assert.equal(construction.entryMode,'peer-disconnect');assert.deepEqual(construction.callerIndex,a.constructionCallerIndex);assert.equal(construction.finalProtection.unchanged,true);assert.equal(construction.error,null);for(const key of ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted'])assert.equal(construction[key],false);assert.deepEqual(construction.artifacts.engineBuildEvidence,a.engineBuildEvidence);
for(const [key,value]of Object.entries({component:a.component,componentAudit:a.componentAudit,inputEntry:plan.probeEntry,inputSourceIndex:plan.probeSourceIndex,engine:a.engine,nativeMetadata:a.nativeMetadata,adapter:plan.adapter}))assert.deepEqual(construction.artifacts[key],value);
assert.equal(audit.state,'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1');assert.equal(audit.passed,true);assert.deepEqual(audit.component,a.component);assert.deepEqual([...audit.selectedInterfaces].sort(),[...plan.selectedInterfaces].sort());assert.equal(new Set(audit.emittedImports).size,audit.emittedImports.length);assert(audit.emittedImports.every(x=>plan.selectedInterfaces.includes(x)&&x.endsWith('@0.2.10')));assert.deepEqual(audit.exports,['wasi:http/incoming-handler@0.2.10']);assert.equal(audit.noExternalPreview1OrCustomImports,true);
assert.equal(audit.allEmittedVersion,'0.2.10');assert.equal(audit.entryMode,'peer-disconnect');
const clean=t=>t.rawExitCode===0&&t.timeout===false&&t.forcedCleanup===false&&t.parentOwnedGroupGone===true&&t.allObservedOwnedGroupsGone===true&&['signals','errors','interruptedSignals','remainingObservedPids'].every(k=>Array.isArray(t[k])&&t[k].length===0);
assert.deepEqual(audit.engine,a.engine);assert.deepEqual(audit.nativeMetadata,a.nativeMetadata);
for(const key of ['validateTerminal','witTerminal']){await verify(audit[key]);const t=await read(audit[key].path);assert(clean(t));extraArtifactRefs.push(audit[key],t.stdout,t.stderr);}
assert.deepEqual([...audit.unusedSelectedInterfaces].sort(),plan.selectedInterfaces.filter(x=>!audit.emittedImports.includes(x)).sort());assert.equal(audit.selectedInterfaces.length,13);
assert.deepEqual(construction.commands.map(x=>x.label),['componentize-init','component-validate','component-wit']);for(const command of construction.commands){await verify(command.terminal);const terminal=await read(command.terminal.path);assert(clean(terminal));assert.deepEqual(terminal.authority,construction.rootAuthority);assert.equal(command.rawExitCode,0);assert.equal(command.clean,true);assert.deepEqual(terminal.stdout,command.stdout);assert.deepEqual(terminal.stderr,command.stderr);extraArtifactRefs.push(command.terminal,terminal.stdout,terminal.stderr);}

const ctorOuter=await read(a.constructionOuterTerminal.path);assert(clean(ctorOuter));assert.deepEqual(ctorOuter.authority,construction.rootAuthority);for(const ref of [ctorOuter.stdout,ctorOuter.stderr]){await verify(ref);extraArtifactRefs.push(ref);}
const worldGuard=await read(a.constructionWorldGuard.path);assert.equal(worldGuard.unchanged,true);assert.deepEqual(worldGuard.before,worldGuard.after);assert.deepEqual(worldGuard.before.sourceIndex,plan.worldSourceIndex);assert.equal(worldGuard.before.members,28);assert.equal(worldGuard.before.witFiles,8);assert.equal(worldGuard.before.exactFileAndDirectoryMembership,true);assert.equal(worldGuard.before.noSymlinkOrHardlinkAliases,true);
const reference=await read(plan.referenceHostChecks.path);assert.equal(reference.passed,true);assert.equal(reference.sourceProtectionPassed,true);assert.equal(reference.hostOnly,true);assert.equal(reference.nodeHttpNetLoopbackAuthorized,true);assert.equal(reference.guestOrEngineOrCompilerExecuted,false);
const referenceResults=await read(plan.referenceResults.path);assert.equal(referenceResults.nodeReferencePassed,true);assert.equal(referenceResults.wasiPeerDisconnectCoverage,false);assert.equal(referenceResults.nodeWasiTransportParityClaimed,false);

await protect();process.umask(0o077);
const output=plan.outputPrefix+'-'+a.runId;assert.equal(resolve(output),output);await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'PEER_DISCONNECT_COLLECTION_IN_PROGRESS_V2',runId:a.runId,
 rootAuthority:authorityRef,sourceIndex:a.sourceIndex,component:a.component,componentAudit:a.componentAudit,
 engine:a.engine,nativeMetadata:a.nativeMetadata,engineBuildEvidence:a.engineBuildEvidence,
 constructionResult:a.constructionResult,constructionCallerIndex:a.constructionCallerIndex,
 constructionOuterTerminal:a.constructionOuterTerminal,constructionWorldGuard:a.constructionWorldGuard,
 probeSourceIndex:plan.probeSourceIndex,referenceHostChecks:plan.referenceHostChecks,
 comparisonScope:'actual-observed-io-abort-and-specific-handled-closed-policy-no-Node-transport-enum-parity',
 cohorts:[],errors:[],observationsValid:false,functionChecksPassed:false,coverageComplete:false,
 nativeDisposalCountsOrStoreDeathProved:false,observedIoRequestSignalImplemented:true,independentPeerDisconnectSignal:false,
 instantIdlePeerAbortClaimed:false,httpBodyCompletionOrTrailersProved:false,
 fullNextAcceptance:false,adoption:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));const handles=[];
const {request}=await import('./tcp-client.mjs');
const {parseDiagnosticLog,analyze}=await import('./classification.mjs');
const {errorData:typedError}=await import('../peer-disconnect-candidate-v1/diagnostic-common.mjs');
async function diagnosticSnapshot(path) {
 assert((await lstat(path)).size<=8388608);return parseDiagnosticLog(await readFile(path,'utf8'),plan.allowedGuestPhases);
}
async function cohort(id) {
 const directory=join(output,id);await mkdir(directory,{mode:0o700});
 const record={id,independentFreshHost:true,notRetryOfOtherCohort:true,responses:[],errors:[],
  functionChecksPassed:false,afterReturnCleanupStatus:'inconclusive-not-inspected',host:null};
 result.cohorts.push(record);await save();
 let lease,host,hostDone,hostExit=null,stopping=false;
 const firstLabel=a.firstHostCase+'-'+id+'-healthy-upload';record.firstLabel=firstLabel;
 try {
  lease=createServer();lease.on('error',()=>{});
  await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});
  const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');
  const origin='http://127.0.0.1:'+address.port;record.portLease={origin,port:address.port,singleAttempt:true,fallbackAllowed:false};await save();
  await protect();await new Promise((resolve,reject)=>lease.close(error=>error?reject(error):resolve()));lease=null;
  const started=await launch(plan.wasmtime.path,['serve','--addr','127.0.0.1:'+address.port,
   '-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','32',
   '--idle-instance-timeout','60s',a.component.path],'wasmtime',directory);
  host=started.child;hostDone=started.done;
  void hostDone.then(status=>{hostExit=status;if(!stopping)record.hostExitedBeforeOwnedShutdown=status;});
  record.host={command:started.command,pid:host.pid??null,stdout:started.stdout,stderr:started.stderr,forcedCleanup:false};await save();
  let ready=false;const listenerDeadline=Date.now()+plan.listenerSeconds*1000;
  while(Date.now()<listenerDeadline){
   if(hostExit)throw new Error('Host exited before readiness');
   const text=await readFile(started.stderr,'utf8');const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];
   if(found){assert.equal(found,origin);ready=true;break;}await pause(50);
  }
  assert(ready,'Exact listener not observed');
  async function eventsUntil(label,predicate,seconds) {
   const deadline=Date.now()+seconds*1000;
   for(;;) {
    const snapshot=await diagnosticSnapshot(started.stderr),own=snapshot.events.filter(e=>e.label===label);
    const found=predicate(own);if(found)return{snapshot,found};
    if(hostExit)throw new Error('Host terminal before requested diagnostic milestone');
    if(Date.now()>=deadline)throw new Error('Diagnostic milestone deadline');await pause(25);
   }
  }
  async function call(kind,ordinal) {
   const label=kind==='healthy-upload'?firstLabel:a.firstHostCase+'-'+id+'-'+kind;
   const path=['healthy-upload','upload-close'].includes(kind)?'/upload':kind==='inspect'?'/inspect':'/output';
   const response=await request({port:address.port,origin,label,path,rawPath:join(directory,'response-'+ordinal+'.http'),
    body:kind==='healthy-upload'?Buffer.alloc(8192,80):kind==='upload-close'?Buffer.alloc(1024,80):undefined,
    partialUpload:kind==='upload-close',closeAfterFirst:kind==='output-close',deadlineMilliseconds:plan.requestSeconds*1000,
    waitForReadAttempt:async(label,prefix)=>{
     const {found}=await eventsUntil(label,own=>own.find(e=>e.phase==='input-read-invocation-attempt'&&e.inputBytes>=prefix),plan.milestoneSeconds);
     return found;
    }});
   response.kind=kind;response.ordinal=ordinal;response.raw=await row(response.rawPath);delete response.rawPath;
   record.responses.push(response);await save();
   let snapshot;
   try {
    const observed=await eventsUntil(label,own=>own.find(e=>e.phase==='adapter-failed'||e.phase==='known-output-closed-handled-return')??(own.some(e=>e.phase==='outgoing-finish-returned')?own.find(e=>e.phase==='adapter-finally-returned'):undefined),plan.outcomeSeconds);
    snapshot=observed.snapshot;
    // On an error, permit bounded observation of naturally executed finally/cancel.
    // This wait never grants a further request or invents a host-completed marker.
    if(observed.found.phase==='adapter-failed'){
     try{snapshot=(await eventsUntil(label,own=>own.find(e=>e.phase==='adapter-finally-returned'),plan.outcomeSeconds)).snapshot;}
     catch(error){response.finallyObservationError=typedError(error);snapshot=await diagnosticSnapshot(started.stderr);}
    }
   } catch(error){response.outcomeObservationError=typedError(error);snapshot=await diagnosticSnapshot(started.stderr);}
   response.diagnosticSnapshot=snapshot;
   response.analysis=analyze(response,snapshot.events,{firstLabel,ordinal,kind});await save();
   if(response.analysis.adapterFailureObserved){response.analysis.safeToRequestAgain=false;
    response.failedExportOutcome='unknown-no-reviewed-per-request-host-discard-marker';}
   return response;
  }
  for(const [ordinal,kind]of [[1,'healthy-upload'],[2,'healthy-output']]) {
   const response=await call(kind,ordinal);
   if(response.analysis.functionChecksPassed!==true||response.analysis.safeToRequestAgain!==true){
    record.safetyStop={kind,reason:'healthy-control-or-normal-completion-not-established'};record.discardOwnedServerRequired=true;return;
   }
  }
  record.functionChecksPassed=true;
  const closed=await call(id==='upload'?'upload-close':'output-close',3);
  record.disconnectCoverage=closed.analysis;record.withinExportIoPathObserved=closed.analysis.ioPathObserved===true;record.signalChecksPassed=closed.analysis.signalPolicyObserved===true;
  if(!closed.analysis.safeToRequestAgain){
   record.safetyStop={kind:closed.kind,reason:closed.analysis.inconclusiveReason??'unknown-failed-export'};
   record.discardOwnedServerRequired=true;record.afterReturnCleanupStatus='inconclusive-unknown-export-or-factory';return;
  }
  const inspect=await call('inspect',4);
  if(inspect.analysis.functionChecksPassed!==true||inspect.analysis.safeToRequestAgain!==true){
   record.safetyStop={kind:'inspect',reason:'inspection-failed-or-factory-changed'};record.discardOwnedServerRequired=true;return;
  }
  record.afterReturnJsHistoryObserved=true;record.afterReturnCleanupStatus='js-history-only-no-native-cleanup-proof';
 } catch(error){record.errors.push(typedError(error));record.discardOwnedServerRequired=true;}
 finally {
  if(lease?.listening)await new Promise(resolve=>lease.close(()=>resolve()));
  if(host&&!hostExit){stopping=true;record.host.shutdownRequested=true;record.host.sigintSent=host.kill('SIGINT');
   await boundedWait(hostDone,5000);if(!hostExit){record.host.forcedCleanup=true;host.kill('SIGKILL');await boundedWait(hostDone,5000);}}
  if(record.host){record.host.exit=hostExit;for(const key of ['stdout','stderr'])record.host[key]=await row(record.host[key]);}
  record.hostShutdownClean=record.host?.shutdownRequested===true&&record.host?.sigintSent===true&&record.host?.forcedCleanup===false&&hostExit?.code===0&&hostExit?.signal===null&&hostExit?.error===null;
  await save();
  if(host&&hostExit===null)throw new Error('Previous cohort host has no terminal outcome; no later cohort allowed');
 }
}
try {
 await cohort('upload');
 // Explicit independent second normal-close case, never a retry/reuse of failed Store.
 await cohort('output');
} catch(error){result.errors.push({stage:'collection',error:typedError(error)});}
finally {
 for(const handle of handles)try{await handle.close();}catch(error){result.errors.push({stage:'raw-stream-close',error:typedError(error)});}
 try{await protect();result.inputsPreserved=true;}catch(error){result.errors.push({stage:'final-protection',error:typedError(error)});}
 result.functionChecksPassed=result.cohorts.length===2&&result.cohorts.every(c=>c.functionChecksPassed===true);
 result.withinExportIoPathsObserved=result.cohorts.length===2&&result.cohorts.every(c=>c.withinExportIoPathObserved===true);
 result.unknownOrFailedInvocationStops=result.cohorts.filter(c=>c.safetyStop).map(c=>({id:c.id,...c.safetyStop}));
 result.signalChecksPassed=result.cohorts.length===2&&result.cohorts.every(c=>c.signalChecksPassed===true);
 result.coverageComplete=result.withinExportIoPathsObserved&&result.signalChecksPassed&&result.cohorts.every(c=>c.afterReturnJsHistoryObserved===true);
 result.coverageStatus=result.coverageComplete?'within-export-paths-and-js-history-only':
  result.withinExportIoPathsObserved?'within-export-io-paths-observed-after-return-inconclusive':'inconclusive-partial-observation';
 result.observationsValid=result.inputsPreserved===true&&result.errors.length===0&&result.cohorts.length===2&&
  result.cohorts.every(c=>c.errors.length===0&&c.hostShutdownClean===true);
 result.collectorAccepted=result.observationsValid&&result.functionChecksPassed&&result.coverageComplete;
 result.state=result.collectorAccepted?'PEER_DISCONNECT_DIAGNOSTIC_OBSERVATIONS_COMPLETE_V2':
  result.observationsValid?'PEER_DISCONNECT_INCONCLUSIVE_OBSERVATIONS_PRESERVED_V2':'PEER_DISCONNECT_COLLECTION_FAILURE_PRESERVED_V2';await save();
}
console.log(JSON.stringify({state:result.state,observationsValid:result.observationsValid,functionChecksPassed:result.functionChecksPassed,
 withinExportIoPathsObserved:result.withinExportIoPathsObserved,signalChecksPassed:result.signalChecksPassed,coverageComplete:result.coverageComplete,coverageStatus:result.coverageStatus,
 collectorAccepted:result.collectorAccepted,errors:result.errors,fullNextAcceptance:false}));
process.exitCode=result.collectorAccepted?0:1;
