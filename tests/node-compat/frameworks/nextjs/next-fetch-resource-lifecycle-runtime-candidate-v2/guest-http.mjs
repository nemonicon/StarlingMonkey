// One new raw lifecycle GET; no fixture/app mount, Node oracle or semantic evaluator.
import assert from 'node:assert/strict';
import {createServer} from 'node:net';
import {mkdir,lstat,readFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {context,layout,originPort,launch,read,row,durable,jsonBytes,errorData,pause,waitBounded,tcpOnce} from './io.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));

async function main(){
 assert.equal(process.argv.length,3);const authpath=resolve(process.argv[2]);const{a,plan,authorityRef,protect}=await context(HERE,authpath);
 const output=join(layout(plan,a.runId),'guest');await mkdir(output,{mode:0o700});
 const result={schemaVersion:1,state:'PUBLIC_FETCH_LIFECYCLE_GUEST_RAW_IN_PROGRESS_V1',rootAuthority:authorityRef,phaseAuthority:a.guestAuthority,controlOrigin:a.controlOrigin,guestOrigin:a.guestOrigin,component:a.component,probeSourceIndex:plan.probeSourceIndex,response:null,server:null,errors:[],inputsPreserved:false,rawCaptureComplete:false,semanticValidationInvoked:false,fullNextAccepted:false,adoption:false};
 const save=()=>durable(join(output,'result.json'),jsonBytes(result));await save();
 const handles=[],children=[];let lease=null,host=null,stopping=false;
 try{
  for(const name of ['tmp','xdg-cache','xdg-config','xdg-data'])await mkdir(join(output,name),{mode:0o700});
  const port=originPort(a.guestOrigin);lease=createServer();await new Promise((yes,no)=>{lease.once('error',no);lease.listen({host:'127.0.0.1',port,exclusive:true},yes);});
  assert.equal(lease.address().port,port);result.portLease={origin:a.guestOrigin,port,singleAttempt:true,fallbackAllowed:false};await save();
  await protect();await new Promise((yes,no)=>lease.close(e=>e?no(e):yes()));lease=null;
  const args=['serve','--addr','127.0.0.1:'+port,'-S','cli=y,tcp=n,udp=n,allow-ip-name-lookup=n','--env','STARLING_FETCH_CONTROL_ORIGIN='+a.controlOrigin,'--max-instance-reuse-count','128','--idle-instance-timeout','60s',a.component.path];
  assert(!args.includes('--dir'));assert.equal(args.filter(x=>x==='--env').length,1);
  host=await launch({exe:plan.wasmtime.path,args,cwd:output,env:{...process.env,XDG_CACHE_HOME:join(output,'xdg-cache'),XDG_CONFIG_HOME:join(output,'xdg-config'),XDG_DATA_HOME:join(output,'xdg-data')}},'wasmtime',output,handles,children);
  result.server={...host.record,shutdownRequested:false,sigintSent:false,forcedCleanup:false};void host.done.then(status=>{if(!stopping)result.errors.push({stage:'host-exited-before-owned-stop',status});});await save();
  const deadline=Date.now()+30000;let ready=false;
  while(Date.now()<deadline){assert.equal(host.status,null);let logs='';for(const path of [host.record.stdout,host.record.stderr]){assert((await lstat(path)).size<=plan.listenerLogByteCap);logs+=await readFile(path,'utf8');}const found=/Serving HTTP on (http:\/\/127\.0\.0\.1:\d+)/.exec(logs)?.[1];if(found){assert.equal(found,a.guestOrigin);ready=true;break;}await pause(plan.readinessPollMilliseconds);}
  assert(ready,'Exact guest listener missing');assert(await tcpOnce(port,plan.tcpConnectMilliseconds));assert.equal(host.status,null);
  result.readiness={exactListener:true,tcpConnect:true,httpWarmupRequests:0,guestCallObservedAtReadiness:false};
  const response={method:'GET',url:a.guestOrigin+'/fetch-lifecycle',status:null,headers:null,body:null,complete:false,receivedBytes:0,overflow:false,transportError:null,readerCleanupErrors:[]};result.response=response;await save();
  const chunks=[];let kept=0;
  try{
   const http=await fetch(response.url,{method:'GET',redirect:'error',signal:AbortSignal.timeout(120000)});response.status=http.status;response.headers=Object.fromEntries(http.headers);
   const reader=http.body.getReader();try{for(;;){const part=await reader.read();if(part.done){response.complete=true;break;}response.receivedBytes+=part.value.byteLength;const remaining=262144-kept;if(remaining>0){const value=part.value.slice(0,remaining);chunks.push(value);kept+=value.byteLength;}if(response.receivedBytes>262144){response.overflow=true;throw new Error('Lifecycle response cap exceeded; raw prefix retained');}}}
   catch(error){response.transportError=errorData(error);}
   finally{if(!response.complete)try{await reader.cancel();}catch(error){response.readerCleanupErrors.push({operation:'cancel',...errorData(error)});}try{reader.releaseLock();}catch(error){response.readerCleanupErrors.push({operation:'releaseLock',...errorData(error)});}}
  }catch(error){response.transportError??=errorData(error);}
  const body=join(output,'response.body');await durable(body,Buffer.concat(chunks),true);response.body=await row(body);response.retainedPrefixBytes=kept;
  await save(); // Raw response/prefix and original errors precede transport assertions.
  assert.equal(response.transportError,null);assert.deepEqual(response.readerCleanupErrors,[]);assert.equal(response.overflow,false);assert.equal(response.complete,true);assert.equal(response.status,200);assert.equal(response.headers['content-type']?.split(';',1)[0].trim().toLowerCase(),'application/json');
  result.rawCaptureComplete=true;
 }catch(error){result.errors.push({stage:'guest-host-or-raw-capture',...errorData(error)});}
 finally{
  if(lease?.listening)try{await new Promise(r=>lease.close(()=>r()));}catch(error){result.errors.push({stage:'lease-close',...errorData(error)});}
  try{if(host&&host.status===null){stopping=true;result.server.shutdownRequested=true;result.server.sigintSent=host.child.kill('SIGINT');await waitBounded(host.done,5000);if(host.status===null){result.server.forcedCleanup=true;host.child.kill('SIGKILL');await waitBounded(host.done,5000);}}if(result.server)result.server.exit=host?.status??null;}catch(error){result.errors.push({stage:'host-shutdown',...errorData(error)});}
  for(const handle of handles)try{await handle.sync();await handle.close();}catch(error){result.errors.push({stage:'log-close',...errorData(error)});}
  if(result.server)for(const key of ['stdout','stderr'])try{result.server[key]=await row(host.record[key]);}catch(error){result.errors.push({stage:'log-descriptor',...errorData(error)});}
  try{await protect();result.inputsPreserved=true;}catch(error){result.errors.push({stage:'final-input-protection',...errorData(error)});}
  result.observationsValid=result.rawCaptureComplete&&result.errors.length===0&&result.inputsPreserved&&result.server?.shutdownRequested===true&&result.server?.sigintSent===true&&result.server?.forcedCleanup===false&&host?.status?.code===0&&host.status.signal===null&&host.status.error===null;
  result.state=result.observationsValid?'PUBLIC_FETCH_LIFECYCLE_GUEST_RAW_CAPTURED_UNREVIEWED_V1':'PUBLIC_FETCH_LIFECYCLE_GUEST_RAW_FAILED_PRESERVED_V1';await save();
 }
 console.log(JSON.stringify({state:result.state,observationsValid:result.observationsValid,semanticPassClaimed:false,errors:result.errors}));process.exitCode=result.observationsValid?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
