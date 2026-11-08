// One normal request. Root owns genuine inner admission/composition audits/outer owner.
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
async function request(port,seconds,limit){return new Promise(yes=>{let status=null,headers=[],bytes=0,overflow=false,done=false;const chunks=[];
 const finish=(error,complete)=>{if(done)return;done=true;clearTimeout(timer);yes({status,headers,bytes,overflow,unretainedTailUnknown:overflow,error:error?detail(error):null,complete,body:Buffer.concat(chunks)});};
 const req=http.request({host:'127.0.0.1',port,method:'GET',path:'/none',agent:false},res=>{status=res.statusCode;headers=res.rawHeaders;res.on('data',b=>{if(bytes+b.length>limit){overflow=true;req.destroy(new Error('Response cap exceeded'));return;}bytes+=b.length;chunks.push(b);});res.once('end',()=>finish(null,res.complete===true));res.once('error',e=>finish(e,false));res.once('aborted',()=>finish(new Error('Response aborted'),false));});
 const timer=setTimeout(()=>req.destroy(new Error('One GET deadline')),seconds*1000);req.once('error',e=>finish(e,false));req.end();});}

async function main(){
 assert.equal(process.argv.length,4);assert.equal(process.argv[2],'--authority');assert.equal(process.env.NODE_OPTIONS,undefined);assert.equal(process.env.NODE_PATH,undefined);
 const plan=JSON.parse(await readFile(join(HERE,'plan.json'),'utf8'));assert.equal(plan.prospectiveCompositionBindingsPending,false);assert(plan.expectedEnvelopeBindings.envelope&&plan.expectedEnvelopeBindings.compositionReview);assert(plan.compositionReviewFixedValues&&typeof plan.compositionReviewFixedValues==='object'&&!Array.isArray(plan.compositionReviewFixedValues)&&Object.keys(plan.compositionReviewFixedValues).length>0);
 const authpath=resolve(process.argv[3]),authority=await row(authpath),a=await document(authority);assert.equal(a.schemaVersion,1);assert.equal(a.state,'ROOT_STANDARD_HANDLER_RETURN_PROBE_RUNTIME_AUTHORIZED_V1');assert.equal(a.unissued,false);
 for(const k of ['localhostServeAllowed','probeAllowed'])assert.equal(a[k],true);
 for(const k of ['browserAllowed','guestEnvironmentAllowed','outgoingHttpWorkloadSelected','automaticRetryAllowed','mountsAllowed','constructorAllowed','nativeBuildAllowed'])assert.equal(a[k],false);
 assert.equal(typeof a.runId,'string');const match=/^[a-z0-9][a-z0-9-]{0,47}$/.exec(a.runId);assert(match&&match[0]===a.runId);
 assert.deepEqual(a.sourceIndex,await row(join(HERE,'index.json')));assert.deepEqual(a.plan,await row(join(HERE,'plan.json')));await ownFamily(a.sourceIndex);
 for(const[k,v]of Object.entries(plan.knownInnerInputs))assert.deepEqual(a[k],v);
 for(const[k,v]of Object.entries(plan.expectedEnvelopeBindings))assert.deepEqual(a[k],v);
 const innerReview=await document(a.innerConstructionReview);assert.equal(innerReview.state,'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_PROBE_COMPONENT_INIT_DATA_REVIEW_PASSED_V1');assert.equal(innerReview.verifiedPassed,true);assert.equal(innerReview.completeReturnedImportAuditVerified,true);assert.deepEqual(innerReview.component,a.innerComponent);assert.deepEqual(innerReview.rootAuthority,a.innerConstructionAuthority);
 const compositionReview=await document(a.compositionReview);for(const[k,v]of Object.entries(plan.compositionReviewFixedValues))assert.deepEqual(compositionReview[k],v);
 const inputRefs=[authority,a.sourceIndex,a.plan,...Object.values(plan.knownInnerInputs),...Object.values(plan.expectedEnvelopeBindings),plan.node,plan.wasmtime,plan.monitor,plan.caseContract,plan.observerSource,plan.observerManifest,plan.observerProtocol];
 for(const ref of inputRefs)await verify(ref);assert.deepEqual(await row(process.execPath),plan.node);
 const work=plan.outputPrefix+'-'+a.runId,owner=work+'-external-root',started=JSON.parse(await readFile(join(owner,'started.json'),'utf8'));assert.equal(started.pid,process.pid);assert.equal(started.timeoutSeconds,180);assert.deepEqual(started.argv,[plan.node.path,join(HERE,'run.mjs'),'--authority',authpath]);assert.deepEqual(started.authority,authority);
 const disk=await statfs(dirname(work));assert(Number(disk.bavail)*Number(disk.bsize)>=plan.minimumFreeBytes);await mkdir(work,{mode:0o700});
 const paths={stdout:join(work,'wasmtime.stdout.log'),stderr:join(work,'wasmtime.stderr.log'),body:join(work,'http.body'),response:join(work,'response.json'),result:join(work,'result.json')};
 const result={schemaVersion:1,state:'STANDARD_HANDLER_RETURN_PROBE_COLLECTING_V1',rootAuthority:authority,sourceIndex:a.sourceIndex,innerComponent:a.innerComponent,innerConstructionReview:a.innerConstructionReview,envelope:a.envelope,compositionReview:a.compositionReview,server:null,http:null,stdoutCapture:null,errors:[],positiveMarkerPresenceControl:false,collectionCompletedCleanly:false,innerImportReturnSiteObserved:false,probeResponseAccepted:false,passed:false,fullNextAccepted:false};
 let host=null,status=null,closed=null,stopPromise=null,lease=null,capture=null,out=null,err=null;
 async function stop(reason){if(stopPromise)return stopPromise;stopPromise=(async()=>{if(!host)return;result.server.shutdownRequested=true;result.server.shutdownReason=reason;if(status===null){result.server.sigintSent=host.kill('SIGINT');try{await bounded(closed,plan.normalStopSeconds*1000,'Normal host stop deadline');}catch{result.server.forcedCleanup=true;host.kill('SIGKILL');await bounded(closed,plan.forcedStopSeconds*1000,'Forced host stop deadline');}}})();return stopPromise;}
 try{
  lease=createServer();await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port:0,exclusive:true},yes);});const address=lease.address();assert(address&&typeof address==='object'&&address.address==='127.0.0.1');const origin='http://127.0.0.1:'+address.port;result.portLease={origin,port:address.port,singleAttempt:true,fallbackAllowed:false};await new Promise((yes,no)=>lease.close(e=>e?no(e):yes()));lease=null;
  out=await open(paths.stdout,'wx',0o600);err=await open(paths.stderr,'wx',0o600);
  const args=['serve','--no-logging-prefix','--addr','127.0.0.1:'+address.port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--max-instance-reuse-count','128','--idle-instance-timeout','60s',a.envelope.path];assert(!args.includes('--dir')&&!args.includes('--env'));
  host=spawn(plan.wasmtime.path,args,{cwd:work,env:{PATH:'/usr/bin:/bin',LANG:'C',LC_ALL:'C'},stdio:['ignore','pipe',err.fd],detached:false});result.server={argv:[plan.wasmtime.path,...args],pid:host.pid??null,spawnAttempts:1,shutdownRequested:false,shutdownReason:null,sigintSent:false,forcedCleanup:false,exit:null};let spawnError=null;closed=new Promise(yes=>{host.once('error',e=>{spawnError=detail(e);});host.once('close',(code,signal)=>{status={code,signal,error:spawnError};result.server.exit=status;yes(status);});});
  const{captureRawStdout}=await import('./capture-stdout.mjs');capture=captureRawStdout({readable:host.stdout,handle:out,path:paths.stdout,limitBytes:plan.stdoutLimitBytes});out=null;void capture.failure.then(error=>{result.errors.push({stage:'stdout-capture-live',error});void stop('capture-failure').catch(e=>result.errors.push({stage:'capture-failure-stop',...detail(e)}));});
  const until=Date.now()+plan.readinessSeconds*1000;let ready=false;
  while(Date.now()<until){assert.equal(status,null,'Host exited before listener');assert.equal(capture.failed,false);const text=await prefix(paths.stderr,plan.readinessPrefixBytes)+await prefix(paths.stdout,plan.readinessPrefixBytes),found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(text)?.[1];if(found){assert.equal(found,origin);ready=true;break;}await sleep(plan.pollMilliseconds);}
  assert(ready,'Exact listener deadline');await tcp(address.port);assert.equal(status,null);result.readiness={exactListener:true,tcpOnly:true,httpWarmupRequests:0};
  const response=await request(address.port,plan.httpSeconds,plan.httpBodyBytes),bodyFile=await open(paths.body,'wx',0o600);try{await bodyFile.writeFile(response.body);await bodyFile.sync();}finally{await bodyFile.close();}const{body,...fields}=response;result.http={...fields,method:'GET',path:'/none',body:await row(paths.body)};
  const markerUntil=Date.now()+plan.positiveMarkerWaitSeconds*1000;
  while(Date.now()<markerUntil){assert.equal(status,null,'Host exited during marker control');assert.equal(capture.failed,false);const text=await prefix(paths.stdout,plan.stdoutLimitBytes);if(text.split('\n').includes(plan.successLine.slice(0,-1))){result.positiveMarkerPresenceControl=true;break;}await sleep(plan.pollMilliseconds);}
  assert(result.positiveMarkerPresenceControl,'Bounded literal marker-presence control deadline');
 }catch(error){result.errors.push({stage:'collection',...detail(error)});}
 finally{
  if(lease?.listening)try{await new Promise(yes=>lease.close(()=>yes()));}catch(error){result.errors.push({stage:'lease-close',...detail(error)});}
  try{await stop('request-and-control-collected');}catch(error){result.errors.push({stage:'host-stop',...detail(error)});}
  if(capture){try{result.stdoutCapture=await bounded(capture.done,plan.captureFinalizeSeconds*1000,'Stdout EOF/finalization deadline');}catch(error){result.errors.push({stage:'stdout-finalization',...detail(error)});capture.abort('owned-finalization-deadline');try{result.stdoutCapture=await bounded(capture.done,1000,'Aborted stdout finalization deadline');}catch(e){result.errors.push({stage:'stdout-aborted-finalization',...detail(e)});}}}
  if(out){try{await out.sync();}catch(error){result.errors.push({stage:'unused-stdout-sync',...detail(error)});}try{await out.close();}catch(error){result.errors.push({stage:'unused-stdout-close',...detail(error)});}}
  if(err){try{await err.sync();}catch(error){result.errors.push({stage:'stderr-sync',...detail(error)});}try{await err.close();}catch(error){result.errors.push({stage:'stderr-close',...detail(error)});}}
 }
 if(result.stdoutCapture?.complete)result.stdout=await row(paths.stdout);result.stderrPath=paths.stderr;result.stderrFinalDigestDeferredToOriginalOwnerTerminal=true;
 try{for(const ref of inputRefs)await verify(ref);await ownFamily(a.sourceIndex);result.originalInputsPreserved=true;}catch(error){result.errors.push({stage:'final-input-protection',...detail(error)});result.originalInputsPreserved=false;}
 const stopped=result.server?.shutdownRequested&&result.server.shutdownReason==='request-and-control-collected'&&result.server.sigintSent&&!result.server.forcedCleanup&&status?.code===0&&status.signal===null&&status.error===null;
 result.collectionCompletedCleanly=result.errors.length===0&&result.http?.complete===true&&result.http.error===null&&!result.http.overflow&&result.stdoutCapture?.complete===true&&stopped&&result.originalInputsPreserved===true;
 // Semantic interpretation starts only after owned host shutdown and full capture.
 if(result.collectionCompletedCleanly){try{const raw=await readFile(paths.stdout);await verify(result.stdout);result.innerImportReturnSiteObserved=raw.equals(Buffer.from(plan.successLine,'ascii'));result.observerMarkerBytes=raw.length;const response=JSON.parse(await readFile(paths.body,'utf8'));result.parsedResponse=await save(paths.response,response);assert.deepEqual(response,plan.expectedProbeResponse);result.probeResponseAccepted=result.http.status===200;}catch(error){result.errors.push({stage:'final-interpretation',...detail(error)});}}
 result.passed=result.collectionCompletedCleanly&&result.innerImportReturnSiteObserved&&result.probeResponseAccepted&&result.errors.length===0;result.state=result.passed?'STANDARD_HANDLER_RETURN_PROBE_PASSED_UNREVIEWED_V1':'STANDARD_HANDLER_RETURN_PROBE_FAILED_RAW_PRESERVED_V1';
 await save(paths.result,result);console.log(JSON.stringify({passed:result.passed,collectionCompletedCleanly:result.collectionCompletedCleanly,innerImportReturnSiteObserved:result.innerImportReturnSiteObserved,probeResponseAccepted:result.probeResponseAccepted,fullNextAccepted:false}));process.exitCode=result.passed?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
