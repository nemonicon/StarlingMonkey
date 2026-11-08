// Uncompiled host-side per-case core. No guest/marker semantics or Source execution at import.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createServer,createConnection} from 'node:net';
import http from 'node:http';
import {open,readFile,lstat,realpath,mkdir,readdir,statfs} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const MARKER='NEXT_NATIVE_EXPORT_PUBLIC_CORRELATION_V1';
const sleep=ms=>new Promise(yes=>setTimeout(yes,ms));
const hash=b=>createHash('sha256').update(b).digest('hex');
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const errorData=e=>({name:typeof e?.name==='string'?e.name.slice(0,128):'unknown',message:typeof e?.message==='string'?e.message.slice(0,2048):'unknown'});
async function row(path){assert.equal(await realpath(path),path);const a=await lstat(path);assert(a.isFile()&&!a.isSymbolicLink()&&a.nlink===1);const b=await readFile(path),z=await lstat(path);for(const k of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(a[k],z[k]);return{path,sha256:hash(b),bytes:b.length};}
async function document(ref){assert.deepEqual(await row(ref.path),ref);assert(ref.bytes<=16777216);const v=JSON.parse(await readFile(ref.path,'utf8'));assert.deepEqual(await row(ref.path),ref);return v;}
async function save(path,value){const f=await open(path,'wx',0o600);try{await f.writeFile(JSON.stringify(value,null,2)+'\n');await f.sync();}finally{await f.close();}return row(path);}
async function prefix(path,limit){let f;try{f=await open(path,'r');const b=Buffer.alloc(limit+1),{bytesRead}=await f.read(b,0,b.length,0);assert(bytesRead<=limit,'Readiness prefix exceeded');const t=b.subarray(0,bytesRead).toString('utf8'),last=t.lastIndexOf('\n');return last<0?'':t.slice(0,last+1);}catch(e){if(e.code==='ENOENT')return'';throw e;}finally{await f?.close();}}
async function bounded(promise,ms,label){let timer;try{return await Promise.race([promise,new Promise((_,no)=>{timer=setTimeout(()=>no(new Error(label)),ms);})]);}finally{clearTimeout(timer);}}
function portOf(origin){const u=new URL(origin);assert.equal(u.origin,origin);assert.equal(u.protocol,'http:');assert.equal(u.hostname,'127.0.0.1');assert.equal(u.pathname,'/');assert(!u.username&&!u.password&&!u.search&&!u.hash);const p=Number(u.port);assert(Number.isInteger(p)&&p>0&&p<=65535&&p!==80);return p;}
async function tcp(port){return new Promise((yes,no)=>{const s=createConnection({host:'127.0.0.1',port});s.setTimeout(1000);s.once('connect',()=>{s.destroy();yes();});s.once('timeout',()=>{s.destroy();no(new Error('TCP readiness deadline'));});s.once('error',no);});}
async function request(port,path,seconds,limit){return new Promise(yes=>{const chunks=[];let bytes=0,settled=false,headers=[],status=null,overflow=false;const finish=(error,complete)=>{if(settled)return;settled=true;clearTimeout(timer);yes({body:Buffer.concat(chunks),status,headers,bodyBytes:bytes,overflow,unretainedTailUnknown:overflow,error:error?errorData(error):null,complete});};const req=http.request({host:'127.0.0.1',port,method:'GET',path,agent:false},res=>{status=res.statusCode;headers=res.rawHeaders;res.on('data',b=>{if(bytes+b.length>limit){overflow=true;req.destroy(new Error('HTTP body cap'));return;}chunks.push(b);bytes+=b.length;});res.once('end',()=>finish(null,res.complete===true));res.once('error',e=>finish(e,false));res.once('aborted',()=>finish(new Error('HTTP response aborted'),false));});const timer=setTimeout(()=>req.destroy(new Error('HTTP request deadline')),seconds*1000);req.once('error',e=>finish(e,false));req.end();});}
function ownerClean(t){return Number.isInteger(t.rawExitCode)&&t.rawExitCode===0&&t.parentOwnedGroupGone===true&&t.allObservedOwnedGroupsGone===true&&t.timeout===false&&t.forcedCleanup===false&&['errors','signals','interruptedSignals','remainingObservedPids'].every(k=>Array.isArray(t[k])&&t[k].length===0)&&t.finalGroups.every(g=>g.alive===false);}
async function main(){
 assert.equal(process.argv.length,6);assert.equal(process.argv[2],'--authority');assert.equal(process.argv[4],'--case');
 const plan=JSON.parse(await readFile(join(HERE,'plan.json'),'utf8'));
 // This core is unissued. Root must first implement/review the enclosing admission+owner driver.
 assert.equal(plan.prospectiveArtifactBindingsPending,false,'New artifact bindings pending');
 assert(plan.wasmtime&&plan.node&&typeof plan.expectedConstructorReviewState==='string');
 assert(Object.values(plan.expectedBindings).every(x=>x&&typeof x.path==='string'));
 const authpath=resolve(process.argv[3]),ar=await row(authpath),a=await document(ar),index=Number(process.argv[5]);
 assert(Number.isInteger(index)&&String(index)===process.argv[5]&&index>=0&&index<17);
 assert.equal(a.state,'ROOT_NATIVE_EXPORT_DIAGNOSTIC_PROBE_RUNTIME_AUTHORIZED_V1');assert.equal(a.unissued,false);
 assert.equal(a.perCaseCollectionAllowed,true);for(const key of ['nativeBuildAllowed','constructorAllowed','browserAllowed','applicationMountAllowed','guestEnvironmentAllowed','outgoingHttpWorkloadSelected','automaticRetryAllowed'])assert.equal(a[key],false);
 assert.equal(typeof a.runId,'string');const runIdMatch=/^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId);assert(runIdMatch&&runIdMatch[0]===a.runId);assert.deepEqual(a.sourceIndex,await row(join(HERE,'index.json')));assert.deepEqual(a.plan,await row(join(HERE,'plan.json')));assert.deepEqual(a.caseIds,plan.fixedCaseIds);
 for(const[key,value]of Object.entries(plan.expectedBindings))assert.deepEqual(a[key],value);
 assert.deepEqual(a.wasmtime,plan.wasmtime);assert.deepEqual(a.node,plan.node);assert.deepEqual(await row(process.execPath),plan.node);assert.deepEqual(await row(plan.wasmtime.path),plan.wasmtime);assert.deepEqual(await row(a.component.path),a.component);
 const review=await document(a.constructionDataReview);assert.equal(review.state,plan.expectedConstructorReviewState);assert.equal(review.verifiedPassed,true);assert.equal(review.completeReturnedImportAuditVerified,true);for(const key of ['component','componentAudit','engine','nativeMetadata'])assert.deepEqual(review[key],a[key]);assert.deepEqual(review.actualResult,a.constructionResult);assert.deepEqual(review.fullBuildReview,a.fullNativeBuildReview);
 const contract=await document(plan.caseContract);assert.equal(contract.cases.length,17);assert.deepEqual(contract.cases.map(x=>x.id),plan.fixedCaseIds);const fixture=contract.cases[index];assert.equal(fixture.request.method,'GET');assert.equal(fixture.request.path,'/'+fixture.id);assert.equal(plan.fixedCaseIds[0],'none');
 const output=plan.outputPrefix+'-'+a.runId,ownerRoot=join(output,'case-'+String(index).padStart(2,'0')+'-'+fixture.id),dataRoot=join(ownerRoot,'data');
 assert.equal(await realpath(output),output);assert.equal(await realpath(ownerRoot),ownerRoot);const disk=await statfs(output);assert(Number(disk.bavail)*Number(disk.bsize)>=plan.minimumFreeBytes);
 // Existing original-monitor rows supply process ownership. No marker token/Store identity is used.
 const ownStart=JSON.parse(await readFile(join(ownerRoot,'started.json'),'utf8'));assert.deepEqual(ownStart.authority,ar);assert.equal(ownStart.pid,process.pid);assert.equal(ownStart.timeoutSeconds,plan.perCaseOwnerSeconds);assert.deepEqual(ownStart.argv,[plan.node.path,join(HERE,'run-case.mjs'),'--authority',authpath,'--case',String(index)]);
 const expectedDirs=contract.cases.slice(0,index+1).map((x,i)=>'case-'+String(i).padStart(2,'0')+'-'+x.id);const actualDirs=(await readdir(output)).filter(x=>/^case-/.test(x));assert.deepEqual(actualDirs.sort(),expectedDirs.sort());
 if(index>0){const prev=contract.cases[index-1],prevRoot=join(output,'case-'+String(index-1).padStart(2,'0')+'-'+prev.id),t=JSON.parse(await readFile(join(prevRoot,'terminal.json'),'utf8')),s=JSON.parse(await readFile(join(prevRoot,'started.json'),'utf8'));assert(ownerClean(t));assert.equal(s.pid,t.pid);assert.deepEqual(t.authority,ar);assert.deepEqual(s.authority,ar);const p=JSON.parse(await readFile(join(prevRoot,'data/case-result.json'),'utf8'));assert.equal(p.collectionCompleted,true);assert.equal(p.stdoutCapture.complete,true);assert.equal(p.semanticValidationInvoked,false);}
 await mkdir(dataRoot,{mode:0o700});
 const paths={stdout:join(dataRoot,'wasmtime.stdout.log'),stderr:join(dataRoot,'wasmtime.stderr.log'),body:join(dataRoot,'http.body'),result:join(dataRoot,'case-result.json')};
 const result={schemaVersion:1,state:'NATIVE_EXPORT_PROBE_CASE_COLLECTING_V1',caseIndex:index,caseId:fixture.id,rootAuthority:ar,origin:a.origin,http:null,server:null,stdoutCapture:null,markerPresenceControl:{required:fixture.expectedObserveAttempts>0,observed:false,deadlineReached:false,semanticInterpretation:false},errors:[],collectionCompleted:false,semanticValidationInvoked:false,storeIdentityProved:false,nativeExportOrHostCompletionProved:false};
 let host=null,closed=null,status=null,capture=null,captureDone=null,lease=null,stderrHandle=null,stdoutHandle=null,stopPromise=null;
 function stopHost(reason){if(stopPromise)return stopPromise;stopPromise=(async()=>{if(!host)return;result.server.shutdownReason=reason;result.server.shutdownRequested=true;if(status===null){result.server.sigintSent=host.kill('SIGINT');try{await bounded(closed,plan.normalStopSeconds*1000,'Normal host stop deadline');}catch{result.server.forcedCleanup=true;host.kill('SIGKILL');await bounded(closed,plan.forcedStopSeconds*1000,'Forced host stop deadline');}}})();return stopPromise;}
 try{
  const port=portOf(a.origin);lease=createServer();await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port,exclusive:true},yes);});await new Promise((yes,no)=>lease.close(e=>e?no(e):yes()));lease=null;
  stdoutHandle=await open(paths.stdout,'wx',0o600);stderrHandle=await open(paths.stderr,'wx',0o600);
  const args=['serve','--no-logging-prefix','--addr','127.0.0.1:'+port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','128','--idle-instance-timeout','60s',a.component.path];assert(!args.includes('--dir')&&!args.includes('--env'));
  host=spawn(plan.wasmtime.path,args,{cwd:dataRoot,env:{PATH:'/usr/bin:/bin',LANG:'C',LC_ALL:'C'},stdio:['ignore','pipe',stderrHandle.fd],detached:false});
  result.server={argv:[plan.wasmtime.path,...args],pid:host.pid??null,freshProcess:true,spawnAttempts:1,shutdownRequested:false,sigintSent:false,forcedCleanup:false,shutdownReason:null,exit:null};
  let spawnError=null;closed=new Promise(yes=>{host.once('error',e=>{spawnError=errorData(e);});host.once('close',(code,signal)=>{status={code,signal,error:spawnError};result.server.exit=status;yes(status);});});
  const{captureRawStdout}=await import('./capture-stdout.mjs');capture=captureRawStdout({readable:host.stdout,handle:stdoutHandle,path:paths.stdout,limitBytes:plan.stdoutLimitBytes});stdoutHandle=null;
  void capture.failure.then(error=>{result.errors.push({stage:'stdout-capture-live',error});void stopHost('capture-failure').catch(e=>result.errors.push({stage:'capture-failure-stop',...errorData(e)}));});
  const until=Date.now()+plan.readinessSeconds*1000;let ready=false;
  while(Date.now()<until){assert.equal(status,null,'Host exited before listener');assert.equal(capture.failed,false);const text=await prefix(paths.stderr,plan.readinessPrefixBytes)+await prefix(paths.stdout,plan.readinessPrefixBytes);const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];if(found){assert.equal(found,a.origin);ready=true;break;}await sleep(plan.pollMilliseconds);}
  assert(ready,'Exact listener deadline');await tcp(port);assert.equal(status,null);result.readiness={exactListener:true,tcpConnectOnly:true,httpWarmupRequests:0};
  const response=await request(port,fixture.request.path,plan.httpSeconds,plan.httpBodyBytes);const bodyHandle=await open(paths.body,'wx',0o600);try{await bodyHandle.writeFile(response.body);await bodyHandle.sync();}finally{await bodyHandle.close();}const{body,...fields}=response;result.http={...fields,method:'GET',path:fixture.request.path,body:await row(paths.body)};
  if(fixture.expectedObserveAttempts>0){const end=Date.now()+plan.positiveMarkerWaitSeconds*1000;while(Date.now()<end){assert.equal(capture.failed,false);if((await prefix(paths.stdout,plan.readinessPrefixBytes)).split('\n').some(line=>line.includes(MARKER))){result.markerPresenceControl.observed=true;break;}if(status!==null)break;await sleep(plan.pollMilliseconds);}result.markerPresenceControl.deadlineReached=!result.markerPresenceControl.observed;}
  else{await sleep(plan.noneQuietMilliseconds);result.markerPresenceControl.noneQuietMilliseconds=plan.noneQuietMilliseconds;}
 }catch(error){result.errors.push({stage:'case-control',...errorData(error)});}
 finally{
  if(lease?.listening)try{await new Promise(yes=>lease.close(()=>yes()));}catch(error){result.errors.push({stage:'lease-close',...errorData(error)});}
  try{await stopHost('case-collected');}catch(error){result.errors.push({stage:'host-stop',...errorData(error)});}
  if(capture){try{captureDone=await bounded(capture.done,plan.captureFinalizeSeconds*1000,'Stdout EOF/finalization deadline');}catch(error){result.errors.push({stage:'stdout-finalization',...errorData(error)});capture.abort('owned-finalization-deadline');try{captureDone=await bounded(capture.done,1000,'Aborted capture finalization deadline');}catch(e){result.errors.push({stage:'stdout-abort-finalization',...errorData(e)});}}result.stdoutCapture=captureDone;}
  if(stdoutHandle){try{await stdoutHandle.sync();}catch(error){result.errors.push({stage:'unused-stdout-sync',...errorData(error)});}try{await stdoutHandle.close();}catch(error){result.errors.push({stage:'unused-stdout-close',...errorData(error)});}}
  if(stderrHandle){try{await stderrHandle.sync();}catch(error){result.errors.push({stage:'stderr-sync',...errorData(error)});}try{await stderrHandle.close();}catch(error){result.errors.push({stage:'stderr-close',...errorData(error)});}}
 }
 if(result.stdoutCapture?.complete){assert.equal(result.stdoutCapture.pipeEof,true);assert.equal(result.stdoutCapture.fileClosed,true);assert.equal(result.stdoutCapture.finalized,true);result.stdout=await row(paths.stdout);}
 result.stderrPath=paths.stderr;result.stderrFinalDigestDeferredToOriginalOwnerTerminal=true;
 const stopped=result.server?.shutdownReason==='case-collected'&&result.server.shutdownRequested&&result.server.sigintSent&&!result.server.forcedCleanup&&status?.code===0&&status.signal===null&&status.error===null;
 result.collectionCompleted=result.errors.length===0&&!!result.http&&result.stdoutCapture?.complete===true&&stopped;
 result.state=result.collectionCompleted?'NATIVE_EXPORT_PROBE_CASE_RAW_CAPTURED_UNREVIEWED_V1':'NATIVE_EXPORT_PROBE_CASE_FAILED_RAW_PRESERVED_V1';
 await save(paths.result,result);console.log(JSON.stringify({caseIndex:index,caseId:fixture.id,collectionCompleted:result.collectionCompleted,semanticValidationInvoked:false}));process.exitCode=result.collectionCompleted?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
