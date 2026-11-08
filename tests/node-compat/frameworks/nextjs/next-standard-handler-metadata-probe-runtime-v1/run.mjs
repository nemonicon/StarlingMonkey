// Fixed six metadata requests; one original900 owner, logical90s cases, no retries.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createServer,createConnection} from 'node:net';
import http from 'node:http';
import {readFile,lstat,realpath,open,mkdir,readdir,statfs} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const HERE=dirname(fileURLToPath(import.meta.url));
const digest=b=>createHash('sha256').update(b).digest('hex');
const physical=s=>({dev:s.dev,ino:s.ino,mode:s.mode,nlink:s.nlink,size:s.size,mtimeMs:s.mtimeMs,ctimeMs:s.ctimeMs});
const detail=e=>({type:e===null?'null':typeof e,name:typeof e?.name==='string'?e.name:null,message:typeof e?.message==='string'?e.message.slice(0,2048):null});
const sleep=ms=>new Promise(yes=>setTimeout(yes,ms));
async function row(path){assert.equal(await realpath(path),path);const a=await lstat(path);assert(a.isFile()&&!a.isSymbolicLink()&&a.nlink===1);const b=await readFile(path);assert.deepEqual(physical(await lstat(path)),physical(a));return{path,sha256:digest(b),bytes:b.length};}
async function verify(ref){assert(ref&&typeof ref.path==='string');assert.deepEqual(await row(ref.path),ref);}
async function document(ref){assert(ref&&Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=16777216);await verify(ref);const value=JSON.parse(await readFile(ref.path,'utf8'));await verify(ref);return value;}
async function save(path,value){const f=await open(path,'wx',0o600);try{await f.writeFile(JSON.stringify(value,null,2)+'\n');await f.sync();}finally{await f.close();}return row(path);}
async function ownFamily(ref){const index=await document(ref);assert.deepEqual((await readdir(HERE)).sort(),[...index.files.map(x=>x.path),'index.json'].sort());for(const r of index.files){assert(r.path&&!r.path.includes('/')&&!r.path.includes('\\'));await verify({...r,path:join(HERE,r.path)});}}
async function bounded(promise,ms,label){let timer;try{return await Promise.race([promise,new Promise((_,no)=>{timer=setTimeout(()=>no(new Error(label)),ms);})]);}finally{clearTimeout(timer);}}
async function prefix(path,limit){let f;try{f=await open(path,'r');const b=Buffer.alloc(limit+1),r=await f.read(b,0,b.length,0);assert(r.bytesRead<=limit,'Control prefix cap exceeded');const text=b.subarray(0,r.bytesRead).toString('utf8'),last=text.lastIndexOf('\n');return last<0?'':text.slice(0,last+1);}catch(e){if(e.code==='ENOENT')return'';throw e;}finally{await f?.close();}}
async function tcp(port){await new Promise((yes,no)=>{const s=createConnection({host:'127.0.0.1',port});s.setTimeout(1000);s.once('connect',()=>{s.destroy();yes();});s.once('timeout',()=>{s.destroy();no(new Error('TCP readiness timeout'));});s.once('error',no);});}
async function request(port,caseRow,timeoutMs,limit,headerName){
 const rawHeaders=['Host','127.0.0.1:'+port,'Connection','close','Content-Length','0'];
 for(const value of caseRow.headerValues)rawHeaders.push(headerName,value);
 return new Promise(yes=>{let status=null,headers=[],bytes=0,overflow=false,complete=false,error=null,ended=false;const chunks=[];let timer;
  const remember=e=>{if(error===null)error=detail(e);};
  const req=http.request({host:'127.0.0.1',port,method:caseRow.method,path:caseRow.path,headers:rawHeaders,agent:false},res=>{
   status=res.statusCode;headers=res.rawHeaders;
   res.on('data',b=>{if(bytes+b.length>limit){overflow=true;req.destroy(new Error('Response cap exceeded'));return;}bytes+=b.length;chunks.push(b);});
   res.once('end',()=>{ended=true;complete=res.complete===true;});
   res.once('error',e=>{remember(e);req.destroy();});
   res.once('aborted',()=>{remember(new Error('Response aborted'));req.destroy();});
  });
  req.once('error',remember);
  req.once('close',()=>{clearTimeout(timer);if(!ended&&error===null)remember(new Error('Request closed before complete response'));yes({status,headers,requestRawHeaders:rawHeaders,bytes,overflow,unretainedTailUnknown:overflow,error,complete:complete&&ended,requestClosed:true,body:Buffer.concat(chunks)});});
  timer=setTimeout(()=>req.destroy(new Error('One HTTP request deadline')),timeoutMs);req.end();
 });
}
function parseMetadata(raw,expected,plan){
 assert(raw.length>0&&raw.length<=plan.recordBytes,'Exactly one bounded metadata line required');
 assert([...raw].every(byte=>byte<128),'ASCII metadata required');
 const text=raw.toString('ascii');assert(text.endsWith('\n')&&!text.slice(0,-1).includes('\n')&&!text.includes('\r'));
 const value=JSON.parse(text.slice(0,-1));
 assert.deepEqual(Object.keys(value),plan.recordKeys);
 assert.equal(value.marker,plan.marker);assert.equal(value.version,3);assert.equal(value.event,'inner-handler-import-returned');
 assert(['GET','POST','unknown'].includes(value.method));assert(['/actions','/action-result','unknown'].includes(value.path));
 assert(['missing','valid','invalid','duplicate','unknown'].includes(value.corrState));
 assert(value.corrCount===null||Number.isInteger(value.corrCount)&&value.corrCount>=0&&value.corrCount<=2);
 assert(value.corr===null||typeof value.corr==='string'&&value.corr.length===64&&/^[0-9a-f]{64}$/.exec(value.corr)?.[0]===value.corr);
 // Exact canonical re-encoding also rejects duplicate keys, alternate escapes/numbers and trailing data.
 assert.equal(JSON.stringify(value)+'\n',text);
 assert.deepEqual(value,expected);return value;
}
async function collectCase(caseRow,slot,context){
 const{plan,a,inputRefs,work}=context;
 const caseWork=join(work,String(slot).padStart(2,'0')+'-'+caseRow.id);
 await mkdir(caseWork,{mode:0o700});
 const paths={stdout:join(caseWork,'wasmtime.stdout.log'),stderr:join(caseWork,'wasmtime.stderr.log'),body:join(caseWork,'http.body'),response:join(caseWork,'response.json'),result:join(caseWork,'result.json')};
 const startedMs=Date.now(),deadline=startedMs+plan.casePrimarySeconds*1000;
 const result={schemaVersion:1,state:'STANDARD_HANDLER_METADATA_CASE_COLLECTING_V1',slot,caseId:caseRow.id,declaredCase:caseRow,logicalCasePrimarySeconds:plan.casePrimarySeconds,logicalDeadlineEnforced:true,separateOriginalCaseMonitor:false,startedAt:new Date(startedMs).toISOString(),primaryFinishedAt:null,cleanupGraceSeconds:plan.cleanupGraceSeconds,server:null,http:null,stdoutCapture:null,errors:[],semanticErrors:[],positiveMarkerPresenceControl:false,collectionCompletedCleanly:false,metadataAccepted:false,probeResponseAccepted:false,passed:false,fullNextAccepted:false};
 let host=null,status=null,closed=null,stopPromise=null,lease=null,capture=null,out=null,err=null;
 function remaining(){const ms=deadline-Date.now();assert(ms>0,'Logical90s case primary deadline');return ms;}
 async function stop(reason){if(stopPromise)return stopPromise;stopPromise=(async()=>{if(!host)return;result.server.shutdownRequested=true;result.server.shutdownReason=reason;if(status===null){result.server.sigintSent=host.kill('SIGINT');try{await bounded(closed,plan.normalStopSeconds*1000,'Normal host stop deadline');}catch{result.server.forcedCleanup=true;host.kill('SIGKILL');await bounded(closed,plan.forcedStopSeconds*1000,'Forced host stop deadline');}}})();return stopPromise;}
 try{
  for(const ref of inputRefs)await verify(ref);await ownFamily(a.sourceIndex);remaining();
  lease=createServer();await bounded(new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port:0,exclusive:true},yes);}),remaining(),'Port lease deadline');
  const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;
  result.portLease={origin,port:address.port,singleAttempt:true,fallbackAllowed:false};await bounded(new Promise((yes,no)=>lease.close(e=>e?no(e):yes())),remaining(),'Port release deadline');lease=null;
  out=await open(paths.stdout,'wx',0o600);err=await open(paths.stderr,'wx',0o600);remaining();
  const args=['serve','--no-logging-prefix','--addr','127.0.0.1:'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','128','--idle-instance-timeout','60s',a.envelope.path];assert(!args.includes('--dir')&&!args.includes('--env'));
  host=spawn(plan.wasmtime.path,args,{cwd:caseWork,env:{PATH:'/usr/bin:/bin',LANG:'C',LC_ALL:'C'},stdio:['ignore','pipe',err.fd],detached:false});
  result.server={argv:[plan.wasmtime.path,...args],pid:host.pid??null,spawnAttempts:1,shutdownRequested:false,shutdownReason:null,sigintSent:false,forcedCleanup:false,exit:null};
  let spawnError=null;closed=new Promise(yes=>{host.once('error',e=>{spawnError=detail(e);});host.once('close',(code,signal)=>{status={code,signal,error:spawnError};result.server.exit=status;yes(status);});});
  const{captureRawStdout}=await import('./capture-stdout.mjs');capture=captureRawStdout({readable:host.stdout,handle:out,path:paths.stdout,limitBytes:plan.stdoutLimitBytes});out=null;
  void capture.failure.then(error=>{result.errors.push({stage:'stdout-capture-live',error});void stop('capture-failure').catch(e=>result.errors.push({stage:'capture-failure-stop',...detail(e)}));});
  const readyUntil=Math.min(deadline,Date.now()+plan.readinessSeconds*1000);let ready=false;
  while(Date.now()<readyUntil){remaining();assert.equal(status,null,'Host exited before listener');assert.equal(capture.failed,false);
   const text=await prefix(paths.stderr,plan.readinessPrefixBytes)+await prefix(paths.stdout,plan.readinessPrefixBytes),found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];
   if(found){assert.equal(found,origin);ready=true;break;}await sleep(Math.min(plan.pollMilliseconds,remaining()));}
  assert(ready,'Exact listener deadline');await bounded(tcp(address.port),Math.min(1000,remaining()),'TCP-only readiness deadline');assert.equal(status,null);
  result.readiness={exactListener:true,tcpOnly:true,httpWarmupRequests:0};
  const response=await request(address.port,caseRow,Math.min(plan.httpSeconds*1000,remaining()),plan.httpBodyBytes,plan.headerName);
  const bodyFile=await open(paths.body,'wx',0o600);try{await bodyFile.writeFile(response.body);await bodyFile.sync();}finally{await bodyFile.close();}
  const{body,...fields}=response;result.http={...fields,method:caseRow.method,path:caseRow.path,body:await row(paths.body)};
  assert(response.complete&&response.requestClosed&&response.error===null&&!response.overflow,'Incomplete HTTP collection');
  const markerUntil=Math.min(deadline,Date.now()+plan.positiveMarkerWaitSeconds*1000);
  // Presence is shutdown control only. Missing/extra/malformed records are final semantic failures.
  while(Date.now()<markerUntil){remaining();assert.equal(status,null,'Host exited during marker control');assert.equal(capture.failed,false);
   const text=await prefix(paths.stdout,plan.stdoutLimitBytes);
   if(text.split('\n').some(line=>line.startsWith('{"marker":"'+plan.marker+'",'))){result.positiveMarkerPresenceControl=true;break;}
   await sleep(Math.min(plan.pollMilliseconds,remaining()));}
  remaining();
 }catch(error){result.errors.push({stage:'collection',...detail(error)});}
 finally{
  result.primaryFinishedAt=new Date().toISOString();result.primaryElapsedMilliseconds=Date.now()-startedMs;
  if(lease?.listening)try{await bounded(new Promise(yes=>lease.close(()=>yes())),1000,'Lease close deadline');}catch(error){result.errors.push({stage:'lease-close',...detail(error)});}
  try{await stop('case-collection-finished');}catch(error){result.errors.push({stage:'host-stop',...detail(error)});}
  if(capture){try{result.stdoutCapture=await bounded(capture.done,plan.captureFinalizeSeconds*1000,'Stdout EOF/finalization deadline');}catch(error){result.errors.push({stage:'stdout-finalization',...detail(error)});capture.abort('owned-finalization-deadline');try{result.stdoutCapture=await bounded(capture.done,1000,'Aborted stdout finalization deadline');}catch(e){result.errors.push({stage:'stdout-aborted-finalization',...detail(e)});}}}
  if(out){try{await out.sync();}catch(error){result.errors.push({stage:'unused-stdout-sync',...detail(error)});}try{await out.close();}catch(error){result.errors.push({stage:'unused-stdout-close',...detail(error)});}}
  if(err){try{await err.sync();}catch(error){result.errors.push({stage:'stderr-sync',...detail(error)});}try{await err.close();}catch(error){result.errors.push({stage:'stderr-close',...detail(error)});}}
 }
 if(result.stdoutCapture?.complete)try{result.stdout=await row(paths.stdout);}catch(error){result.errors.push({stage:'stdout-publication',...detail(error)});}
 result.stderrPath=paths.stderr;result.stderrFinalDigestDeferredToOriginalOwnerTerminal=true;
 try{for(const ref of inputRefs)await verify(ref);await ownFamily(a.sourceIndex);result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'final-input-protection',...detail(error)});result.originalInputsPreserved=false;}
 const stopped=result.server?.shutdownRequested&&result.server.shutdownReason==='case-collection-finished'&&result.server.sigintSent&&!result.server.forcedCleanup&&status?.code===0&&status.signal===null&&status.error===null;
 result.collectionCompletedCleanly=result.errors.length===0&&result.http?.complete===true&&result.http.requestClosed===true&&result.http.error===null&&!result.http.overflow&&result.stdoutCapture?.complete===true&&stopped&&result.originalInputsPreserved===true&&!!result.stdout;
 // No marker JSON/body semantics are evaluated before normal shutdown and finalized complete capture.
 if(result.collectionCompletedCleanly){
  let raw,bodyRaw;
  try{
   raw=await readFile(paths.stdout);assert.equal(raw.length,result.stdout.bytes);assert.equal(digest(raw),result.stdout.sha256);await verify(result.stdout);
   bodyRaw=await readFile(paths.body);assert.equal(bodyRaw.length,result.http.body.bytes);assert.equal(digest(bodyRaw),result.http.body.sha256);await verify(result.http.body);
  }catch(error){result.errors.push({stage:'final-output-read-or-protection',...detail(error)});result.collectionCompletedCleanly=false;}
  if(result.collectionCompletedCleanly){
   // Only pure framing/schema/value comparisons can be clean semantic failures.
   try{result.observedMetadata=parseMetadata(raw,caseRow.expectedRecord,plan);result.metadataAccepted=true;}catch(error){result.semanticErrors.push({stage:'final-metadata',...detail(error)});}
   let response,responseParsed=false;
   try{response=JSON.parse(bodyRaw.toString('utf8'));responseParsed=true;assert.deepEqual(response,caseRow.expectedResponse);assert.equal(result.http.status,caseRow.expectedStatus);result.probeResponseAccepted=true;}catch(error){result.semanticErrors.push({stage:'final-response',...detail(error)});}
   if(responseParsed)try{result.parsedResponse=await save(paths.response,response);}catch(error){result.errors.push({stage:'final-response-publication',...detail(error)});result.collectionCompletedCleanly=false;}
  }
 }
 result.passed=result.collectionCompletedCleanly&&result.metadataAccepted&&result.probeResponseAccepted&&result.semanticErrors.length===0;
 result.state=result.passed?'STANDARD_HANDLER_METADATA_CASE_PASSED_UNREVIEWED_V1':'STANDARD_HANDLER_METADATA_CASE_FAILED_RAW_PRESERVED_V1';result.finishedAt=new Date().toISOString();
 const resultRef=await save(paths.result,result);return{...result,actualResult:resultRef};
}
async function main(){
 assert.equal(process.argv.length,4);assert.equal(process.argv[2],'--authority');assert.equal(process.env.NODE_OPTIONS,undefined);assert.equal(process.env.NODE_PATH,undefined);
 const plan=JSON.parse(await readFile(join(HERE,'plan.json'),'utf8'));
 assert.equal(plan.prospectiveCompositionBindingsPending,false);assert(plan.expectedEnvelopeBindings.envelope&&plan.expectedEnvelopeBindings.compositionReview);
 assert(plan.compositionReviewFixedValues&&typeof plan.compositionReviewFixedValues==='object'&&!Array.isArray(plan.compositionReviewFixedValues)&&Object.keys(plan.compositionReviewFixedValues).length>0);
 assert.equal(plan.ownerSeconds,900);assert.equal(plan.casePrimarySeconds,90);assert.equal(plan.stdoutLimitBytes,8388608);assert.equal(plan.recordBytes,512);
 assert.deepEqual(plan.cases.map(x=>x.id),['get-actions-missing','get-actions-valid','post-actions-valid','get-action-result-valid','get-actions-uppercase','get-actions-duplicate']);
 const authpath=resolve(process.argv[3]),authority=await row(authpath),a=await document(authority);
 assert.equal(a.schemaVersion,1);assert.equal(a.state,'ROOT_STANDARD_HANDLER_METADATA_PROBES_RUNTIME_AUTHORIZED_V1');assert.equal(a.unissued,false);
 for(const k of ['localhostServeAllowed','probeAllowed'])assert.equal(a[k],true);
 for(const k of ['browserAllowed','guestEnvironmentAllowed','outgoingHttpWorkloadSelected','automaticRetryAllowed','mountsAllowed','constructorAllowed','nativeBuildAllowed'])assert.equal(a[k],false);
 assert.equal(typeof a.runId,'string');const match=/^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId);assert(match&&match[0]===a.runId);
 assert.deepEqual(a.sourceIndex,await row(join(HERE,'index.json')));assert.deepEqual(a.plan,await row(join(HERE,'plan.json')));await ownFamily(a.sourceIndex);
 for(const[k,v]of Object.entries(plan.knownInnerInputs))assert.deepEqual(a[k],v);
 for(const[k,v]of Object.entries(plan.expectedEnvelopeBindings))assert.deepEqual(a[k],v);
 const innerReview=await document(a.innerConstructionReview);assert.equal(innerReview.state,'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_PROBE_COMPONENT_INIT_DATA_REVIEW_PASSED_V1');assert.equal(innerReview.verifiedPassed,true);assert.equal(innerReview.completeReturnedImportAuditVerified,true);assert.deepEqual(innerReview.component,a.innerComponent);assert.deepEqual(innerReview.rootAuthority,a.innerConstructionAuthority);
 const compositionReview=await document(a.compositionReview);for(const[k,v]of Object.entries(plan.compositionReviewFixedValues))assert.deepEqual(compositionReview[k],v);
 const inputRefs=[authority,a.sourceIndex,a.plan,...Object.values(plan.knownInnerInputs),...Object.values(plan.expectedEnvelopeBindings),plan.node,plan.wasmtime,plan.monitor,plan.caseContract,plan.innerEntry,plan.observerSource,plan.observerManifest,plan.observerProtocol];
 for(const ref of inputRefs)await verify(ref);assert.deepEqual(await row(process.execPath),plan.node);
 const protocol=await document(plan.observerProtocol);assert.equal(protocol.marker,plan.marker);assert.equal(protocol.version,3);assert.equal(protocol.headerName,plan.headerName);assert.equal(protocol.headerNameAsciiBytes,33);assert.deepEqual(protocol.fields,plan.recordKeys);
 const work=plan.outputPrefix+'-'+a.runId,owner=work+'-external-root',started=JSON.parse(await readFile(join(owner,'started.json'),'utf8'));
 assert.equal(started.pid,process.pid);assert.equal(started.timeoutSeconds,900);assert.deepEqual(started.argv,[plan.node.path,join(HERE,'run.mjs'),'--authority',authpath]);assert.deepEqual(started.authority,authority);
 const disk=await statfs(dirname(work));assert(Number(disk.bavail)*Number(disk.bsize)>=plan.minimumFreeBytes);await mkdir(work,{mode:0o700});
 const result={schemaVersion:1,state:'STANDARD_HANDLER_METADATA_PROBES_COLLECTING_V1',rootAuthority:authority,sourceIndex:a.sourceIndex,plan:a.plan,innerComponent:a.innerComponent,innerConstructionReview:a.innerConstructionReview,innerConstructionAuthority:a.innerConstructionAuthority,envelope:a.envelope,compositionReview:a.compositionReview,originalOwnerSeconds:900,separateOriginalCaseMonitors:false,declaredCases:plan.cases.map(x=>x.id),attemptedCases:[],cases:[],unattemptedCases:[],errors:[],driverCompletedAllDeclaredCases:false,allCollectionsCompletedCleanly:false,allDeclaredMetadataAndResponsesAccepted:false,passed:false,fullNextAccepted:false};
 for(let index=0;index<plan.cases.length;index++){
  const caseRow=plan.cases[index];result.attemptedCases.push(caseRow.id);
  try{const observation=await collectCase(caseRow,index+1,{plan,a,inputRefs,work});result.cases.push(observation);
   if(!observation.collectionCompletedCleanly){result.errors.push({stage:'unsafe-or-incomplete-case',caseId:caseRow.id});break;}
  }catch(error){result.errors.push({stage:'case-publication-or-orchestration',caseId:caseRow.id,...detail(error)});break;}
  // A complete/clean semantic mismatch is retained and does not replace, retry or skip later fixed cases.
 }
 result.unattemptedCases=result.declaredCases.slice(result.attemptedCases.length);
 try{for(const ref of inputRefs)await verify(ref);await ownFamily(a.sourceIndex);result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'final-input-protection',...detail(error)});result.originalInputsPreserved=false;}
 result.driverCompletedAllDeclaredCases=result.cases.length===plan.cases.length&&result.unattemptedCases.length===0;
 result.allCollectionsCompletedCleanly=result.driverCompletedAllDeclaredCases&&result.cases.every(x=>x.collectionCompletedCleanly)&&result.originalInputsPreserved&&result.errors.length===0;
 result.allDeclaredMetadataAndResponsesAccepted=result.driverCompletedAllDeclaredCases&&result.cases.every(x=>x.passed);
 result.passed=result.allCollectionsCompletedCleanly&&result.allDeclaredMetadataAndResponsesAccepted;
 result.state=result.passed?'STANDARD_HANDLER_METADATA_PROBES_PASSED_UNREVIEWED_V1':'STANDARD_HANDLER_METADATA_PROBES_FAILED_RAW_PRESERVED_V1';
 await save(join(work,'result.json'),result);console.log(JSON.stringify({passed:result.passed,driverCompletedAllDeclaredCases:result.driverCompletedAllDeclaredCases,allCollectionsCompletedCleanly:result.allCollectionsCompletedCleanly,unattemptedCases:result.unattemptedCases,fullNextAccepted:false}));process.exitCode=result.passed?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
