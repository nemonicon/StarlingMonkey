// Dormant isolated diagnostic: all3 complete raw responses precede comparison.
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
async function walk(root){const out={files:[],dirs:['.'],links:[]};async function visit(dir){for(const name of(await readdir(dir)).sort()){const path=join(dir,name),s=await lstat(path),r=relative(root,path);if(s.isSymbolicLink())out.links.push(r);else if(s.isDirectory()){out.dirs.push(r);await visit(path);}else{assert(s.isFile(),'Only regular files/directories');out.files.push(r);}}}await visit(root);return out;}
async function boundedWait(promise,ms){let timer;try{await Promise.race([promise,new Promise(resolve=>{timer=setTimeout(resolve,ms);})]);}finally{clearTimeout(timer);}}
async function launch(exe,args,id){const stdout=join(output,id+'.stdout.log'),stderr=join(output,id+'.stderr.log'),out=await open(stdout,'wx',0o600),err=await open(stderr,'wx',0o600);handles.push(out,err);const child=spawn(exe,args,{cwd:output,stdio:['ignore',out.fd,err.fd],env:{...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}});let status=null;const done=new Promise(resolve=>{child.once('error',error=>{status={code:null,signal:null,error:errorData(error)};resolve(status);});child.once('exit',(code,signal)=>{status={code,signal,error:null};resolve(status);});});return{child,done,stdout,stderr,get status(){return status;},command:[exe,...args]};}

const errorData=e=>({name:e?.name??'Error',message:e?.message??String(e),stack:e?.stack??null});
const authpath=resolve(process.argv[2]),a=await read(authpath),plan=await read(join(here,'plan.json'));
const authorityRef=await row(authpath);
assert.equal(a.state,'ROOT_UNREF_REUSE_HTTP_PROBE_AUTHORIZED_V1');assert.deepEqual(a.sourceIndex,await row(join(here,'index.json')));assert.deepEqual(a.plan,await row(join(here,'plan.json')));
assert(typeof a.runId==='string'&&/^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId)?.[0]===a.runId);
assert.equal(a.firstHostCase,'unref-'+a.runId);
for(const k of ['ordinaryProbeAllowed','loopbackServeAllowed'])assert.equal(a[k],true);
for(const k of ['appMountAllowed','componentConstructionAllowed','fullNextAcceptanceAllowed','adoptionAllowed'])assert.equal(a[k],false);
assert(Array.isArray(a.engineBuildEvidence)&&a.engineBuildEvidence.length>0);assert(Array.isArray(a.nativeProtectedInputs)&&a.nativeProtectedInputs.length>0);assert(Array.isArray(a.nativeSourceFamilies));
const extraArtifactRefs=[];
async function protect(){await verify(authorityRef);await family(a.sourceIndex);await family(a.constructionCallerIndex);for(const ref of [...plan.sourceFamilies,...a.nativeSourceFamilies])await family(ref);for(const key of ['node','wasmtime','monitor','adapter','nodeOracleSource','probeEntry','probeCases','probeValidator','runtimeContract','nodeOracleData','nodeOracleRawIndex'])await verify(plan[key]);for(const key of ['engine','nativeMetadata','constructionResult','component','componentAudit','nodeOracleStdout','nodeOracleTerminal','nodeOracleStarted','nodeOracleHostChecks']){assert.equal(await realpath(a[key].path),a[key].path);await verify(a[key]);}for(const ref of [...extraArtifactRefs,...a.engineBuildEvidence,...a.nativeProtectedInputs])await verify(ref);}
await protect();
const construction=await read(a.constructionResult.path),audit=await read(a.componentAudit.path);
for(const ref of [construction.rootAuthority,construction.plan,...construction.artifacts.engineBuildEvidence]){await verify(ref);extraArtifactRefs.push(ref);}
const constructorAuthority=await read(construction.rootAuthority.path),constructorPlan=await read(construction.plan.path);
assert.equal(constructorAuthority.state,'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2');assert.deepEqual(constructorAuthority.callerIndex,a.constructionCallerIndex);assert.equal(constructorAuthority.entryMode,'unref-reuse');assert.equal(constructorAuthority.componentizeInitAllowed,true);for(const key of ['ordinaryExportsAllowed','httpServingAllowed','networkAllowed','nativeBuildAllowed','packageMutationAllowed','globalPinMutationAllowed','debugAllowed','applicationMountAtInitAllowed','deployedResnapshotAllowed'])assert.equal(constructorAuthority[key],false);
assert.deepEqual(constructorPlan.inputSourceIndex,plan.probeSourceIndex);assert.deepEqual(constructorPlan.entries,{'unref-reuse':plan.probeEntry});assert.equal(constructorPlan.worldName,'next-http');assert.equal(constructorPlan.witDirectory,plan.witDirectory);assert.deepEqual(constructorPlan.selectedInterfaces,plan.selectedInterfaces);
const {validateNative}=await import('./native-model.mjs');validateNative(await read(a.nativeMetadata.path),a,constructorAuthority);
assert.equal(construction.state,'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2');assert.equal(construction.passed,true);assert.equal(construction.entryMode,'unref-reuse');assert.deepEqual(construction.callerIndex,a.constructionCallerIndex);assert.equal(construction.finalProtection.unchanged,true);assert.equal(construction.error,null);for(const key of ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted'])assert.equal(construction[key],false);assert.deepEqual(construction.artifacts.engineBuildEvidence,a.engineBuildEvidence);
for(const [key,value]of Object.entries({component:a.component,componentAudit:a.componentAudit,inputEntry:plan.probeEntry,inputSourceIndex:plan.probeSourceIndex,engine:a.engine,nativeMetadata:a.nativeMetadata,adapter:plan.adapter}))assert.deepEqual(construction.artifacts[key],value);
assert.equal(audit.state,'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1');assert.equal(audit.passed,true);assert.deepEqual(audit.component,a.component);assert.deepEqual([...audit.selectedInterfaces].sort(),[...plan.selectedInterfaces].sort());assert.equal(new Set(audit.emittedImports).size,audit.emittedImports.length);assert(audit.emittedImports.every(x=>plan.selectedInterfaces.includes(x)&&x.endsWith('@0.2.10')));assert.deepEqual(audit.exports,['wasi:http/incoming-handler@0.2.10']);assert.equal(audit.noExternalPreview1OrCustomImports,true);
assert.equal(audit.allEmittedVersion,'0.2.10');assert.equal(audit.entryMode,'unref-reuse');
const clean=t=>t.rawExitCode===0&&t.timeout===false&&t.forcedCleanup===false&&t.parentOwnedGroupGone===true&&t.allObservedOwnedGroupsGone===true&&['signals','errors','interruptedSignals','remainingObservedPids'].every(k=>Array.isArray(t[k])&&t[k].length===0);
assert.deepEqual(audit.engine,a.engine);assert.deepEqual(audit.nativeMetadata,a.nativeMetadata);
for(const key of ['validateTerminal','witTerminal']){await verify(audit[key]);const t=await read(audit[key].path);assert(clean(t));extraArtifactRefs.push(audit[key],t.stdout,t.stderr);}
assert.deepEqual([...audit.unusedSelectedInterfaces].sort(),plan.selectedInterfaces.filter(x=>!audit.emittedImports.includes(x)).sort());assert.equal(audit.selectedInterfaces.length,13);
assert.deepEqual(construction.commands.map(x=>x.label),['componentize-init','component-validate','component-wit']);for(const command of construction.commands){await verify(command.terminal);const terminal=await read(command.terminal.path);assert(clean(terminal));assert.deepEqual(terminal.authority,construction.rootAuthority);assert.equal(command.rawExitCode,0);assert.equal(command.clean,true);assert.deepEqual(terminal.stdout,command.stdout);assert.deepEqual(terminal.stderr,command.stderr);extraArtifactRefs.push(command.terminal,terminal.stdout,terminal.stderr);}
const oracleTerminal=await read(a.nodeOracleTerminal.path);assert(clean(oracleTerminal));assert.deepEqual(oracleTerminal.stdout,a.nodeOracleStdout);extraArtifactRefs.push(oracleTerminal.stderr);
const oracleStarted=await read(a.nodeOracleStarted.path),hostChecks=await read(a.nodeOracleHostChecks.path),hostRawIndex=await read(plan.nodeOracleRawIndex.path);
assert.deepEqual(a.nodeOracleHostChecks,plan.nodeOracleHostChecks);assert.equal(hostChecks.hostOnly,true);assert.equal(hostChecks.guestOrEngineOrCompilerOrNetworkExecuted,false);assert.equal(hostChecks.passed,true);assert.equal(hostChecks.sourceProtectionPassed,true);
const oraclePhase=hostChecks.phases.find(x=>x.name==='node-oracle');assert(oraclePhase);assert.deepEqual(oraclePhase.argv,[plan.node.path,plan.nodeOracleSource.path]);assert.deepEqual(oraclePhase.terminal,a.nodeOracleTerminal);assert.deepEqual(oraclePhase.stdout,a.nodeOracleStdout);assert.deepEqual(oraclePhase.stderr,oracleTerminal.stderr);
assert.deepEqual(oracleStarted.argv,oraclePhase.argv);assert.equal(oracleStarted.pid,oracleTerminal.pid);assert.equal(oracleStarted.timeoutSeconds,120);assert.deepEqual(oracleStarted.authority,oracleTerminal.authority);await verify(oracleTerminal.authority);extraArtifactRefs.push(oracleTerminal.authority);
const startedRow=hostRawIndex.files.find(x=>x.path==='node-oracle/started.json');assert(startedRow);assert.deepEqual(a.nodeOracleStarted,{path:startedRow.originalPath,sha256:startedRow.sha256,bytes:startedRow.bytes});
// The published Source copy and original monitored stdout keep separate physical
// roles; only their complete content tuple is equal.
assert.equal(a.nodeOracleStdout.sha256,plan.nodeOracleData.sha256);assert.equal(a.nodeOracleStdout.bytes,plan.nodeOracleData.bytes);

await protect();process.umask(0o077);
const output=plan.outputPrefix+'-'+a.runId;assert.equal(resolve(output),output);await mkdir(output,{mode:0o700});
const result={schemaVersion:1,state:'UNREF_REUSE_HTTP_PROBE_IN_PROGRESS_V1',runId:a.runId,rootAuthority:await row(authpath),sourceIndex:a.sourceIndex,component:a.component,componentAudit:a.componentAudit,engine:a.engine,nativeMetadata:a.nativeMetadata,engineBuildEvidence:a.engineBuildEvidence,constructionResult:a.constructionResult,constructionCallerIndex:a.constructionCallerIndex,probeSourceIndex:plan.probeSourceIndex,nodeOracleStdout:a.nodeOracleStdout,nodeOracleTerminal:a.nodeOracleTerminal,nodeOracleStarted:a.nodeOracleStarted,nodeOracleHostChecks:a.nodeOracleHostChecks,firstHostCase:a.firstHostCase,comparisonScope:'original-Node-public-projection-plus-strict-Source-admission',nativeBoundaryParityClaimed:false,nativeOwnerIdentityOrTeardownProved:false,responses:[],errors:[],server:null,applicationMounted:false,applicationImported:false,fullNextAcceptance:false,adoption:false};
const save=()=>writeFile(join(output,'result.json'),JSON.stringify(result,null,2)+'\n',{mode:0o600});await save();
const pause=ms=>new Promise(r=>setTimeout(r,ms));const handles=[];let host,hostExit=null,hostDone,stopping=false,lease;
const {validate,compare,parseOracle,assessSafety}=await import('./comparison.mjs');
// Protected Source contract is loaded before any request/safety decision.
const contract=await read(plan.runtimeContract.path);
try{
 lease=createServer();lease.on('error',()=>{});await new Promise((resolve,reject)=>{lease.once('error',reject);lease.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;result.portLease={origin,port:address.port,singleAttempt:true,fallbackAllowed:false};await save();
 await protect();await new Promise((resolve,reject)=>lease.close(e=>e?reject(e):resolve()));lease=null;
 const server=await launch(plan.wasmtime.path,['serve','--addr','127.0.0.1:'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','32','--idle-instance-timeout','60s',a.component.path],'wasmtime');host=server.child;hostDone=server.done;void hostDone.then(status=>{hostExit=status;if(!stopping)result.errors.push({stage:'server-exited-before-owned-shutdown',status});});result.server={command:server.command,pid:host.pid??null,stdout:server.stdout,stderr:server.stderr,forcedCleanup:false};await save();
 let ready=false;const deadline=Date.now()+30000;while(Date.now()<deadline){if(hostExit)throw Error('Server exited before readiness');let log='';for(const path of [server.stdout,server.stderr]){assert((await lstat(path)).size<=8388608);log+=await readFile(path,'utf8');}const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(log)?.[1];if(found){assert.equal(found,origin);ready=true;break;}await pause(50);}assert(ready,'Exact listener unavailable within30s');
 for(let call=1;call<=3;call++){
  const record={call};result.responses.push(record);
  try{const response=await fetch(origin+'/unref-reuse?phase='+plan.phases[call-1]+'&case='+encodeURIComponent(a.firstHostCase),{signal:AbortSignal.timeout(10000)}),bytes=new Uint8Array(await response.arrayBuffer()),path=join(output,'response-'+call+'.body');await writeFile(path,bytes,{flag:'wx',mode:0o600});record.status=response.status;record.headers=Object.fromEntries(response.headers);record.body=await row(path);record.rawValueType='Uint8Array';}
  catch(error){record.transportError=errorData(error);}await save();
  if(record.transportError){result.safetyStop={call,reason:'transport-failed-unknown-component-state'};result.discardOwnedServerRequired=true;await save();break;}
  record.safety=assessSafety(await readFile(record.body.path),record.status,call,contract,a.firstHostCase);await save();
  if(!record.safety.safeToReuse){result.safetyStop={call,...record.safety};result.discardOwnedServerRequired=true;await save();break;}
 }
 result.allThreeCaptureAttemptsComplete=result.responses.length===3;result.allThreePassingResponsesCaptured=result.responses.length===3&&result.responses.every(x=>x.safety?.safeToReuse===true);await save();
 if(result.safetyStop)throw Error('Failed or unknown collection saved; further calls refused and owned server must be discarded: '+result.safetyStop.reason);
 assert.equal(result.allThreePassingResponsesCaptured,true);
 // NO oracle parsing or semantic comparison occurs above this fence.
 const oracleBytes=await readFile(a.nodeOracleStdout.path);await writeFile(join(output,'node-oracle.stdout.jsonl'),oracleBytes,{flag:'wx',mode:0o600});const parsedOracle=parseOracle(new TextDecoder('utf-8',{fatal:true}).decode(oracleBytes),contract);result.nodeOracleSummary=parsedOracle.summary;result.nodeHostCallChecksVerified=parsedOracle.hostCallChecks;result.nodeHostDistinctCallbackChecksVerified=parsedOracle.distinctCallbackChecks;result.nodeHostCallsCaptured=3;result.nodeOracleOriginalCollections=parsedOracle.values;result.comparisons=[];
 for(let call=1;call<=3;call++){
  const record=result.responses[call-1];assert(!record.transportError);assert.equal(record.status,200);assert(record.headers['content-type']?.includes('application/json'));const value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(await readFile(record.body.path)));const expected=parsedOracle.values[call-1];record.typedPayload=value;await save();let verified;try{verified=validate(value,call,contract,a.firstHostCase);}catch(error){record.originalValidationFailure=errorData(error);await save();throw error;}record.callChecksVerified=verified.callChecks;record.cumulativeCallbackChecksVerified=verified.callbackChecks;record.ordinalValidated=true;
  result.comparisons.push(compare(value,expected,call,contract,a.firstHostCase));await save();
 }
 result.nativeCallChecksVerified=result.responses.reduce((n,x)=>n+x.callChecksVerified,0);assert.equal(result.nativeCallChecksVerified,51);result.nativeDistinctCallbackChecksVerified=result.responses[2].cumulativeCallbackChecksVerified;assert.equal(result.nativeDistinctCallbackChecksVerified,9);assert.deepEqual(result.responses.map(x=>x.cumulativeCallbackChecksVerified),[0,7,9]);result.callbackInventoriesAreCumulativeNotSummed=true;result.comparisonComplete=true;result.selectedDifferences=result.comparisons.filter(x=>x.classification==='difference-requires-review').map(x=>({call:x.call,phase:x.phase}));result.nodeSelectedParity=result.selectedDifferences.length===0;result.nodePublicProjectionParity=result.nodeSelectedParity;
}catch(error){result.errors.push({stage:'probe-or-comparison',...errorData(error)});}
finally{
 if(lease?.listening)await new Promise(resolve=>lease.close(()=>resolve()));
 if(host&&!hostExit){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.kill('SIGINT');await boundedWait(hostDone,5000);if(!hostExit){result.server.forcedCleanup=true;host.kill('SIGKILL');await boundedWait(hostDone,5000);}}
 if(result.server){result.server.exit=hostExit;for(const key of ['stdout','stderr'])result.server[key]=await row(result.server[key]);}
 for(const h of handles)try{await h.close();}catch(error){result.errors.push({stage:'raw-stream-close',...errorData(error)});}
 try{await protect();result.inputsPreserved=true;}catch(error){result.errors.push({stage:'final-protection',...errorData(error)});}
 result.observationsValid=result.comparisonComplete===true&&result.errors.length===0&&result.inputsPreserved===true&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&result.server?.forcedCleanup===false&&hostExit?.code===0&&hostExit?.signal===null&&hostExit?.error===null;
 result.state=result.observationsValid?(result.nodeSelectedParity?'UNREF_REUSE_SELECTED_PARITY_OBSERVED_V1':'UNREF_REUSE_SELECTED_DIFFERENCES_OBSERVED_V1'):'UNREF_REUSE_FAILED_OBSERVATION_PRESERVED_V1';await save();
}
console.log(JSON.stringify({state:result.state,observationsValid:result.observationsValid,nodeSelectedParity:result.nodeSelectedParity,selectedDifferences:result.selectedDifferences,errors:result.errors,fullNextAcceptance:false}));process.exitCode=result.observationsValid&&result.nodeSelectedParity?0:1;
