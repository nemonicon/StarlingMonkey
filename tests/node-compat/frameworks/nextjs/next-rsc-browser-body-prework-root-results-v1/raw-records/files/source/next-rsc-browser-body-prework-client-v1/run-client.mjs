// One Chrome body-consumption control after the unchanged non-browser workload.
import assert from 'node:assert/strict';
import {runPrework} from './prework.mjs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {writeFileSync} from 'node:fs';
import {readFile,open,mkdir,lstat,realpath} from 'node:fs/promises';
import {dirname,join,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const here=dirname(fileURLToPath(import.meta.url));
let partialResult;
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const stamp=s=>[s.dev,s.ino,s.mode,s.nlink,s.size,s.mtimeMs,s.ctimeMs];
const errorData=e=>({name:typeof e?.name==='string'?e.name:'Error',message:typeof e?.message==='string'?e.message:String(e)});
async function refRead(ref,limit){
 assert(ref&&typeof ref==='object'&&!Array.isArray(ref));assert.deepEqual(Object.keys(ref).sort(),['bytes','path','sha256']);
 assert(typeof ref.path==='string'&&resolve(ref.path)===ref.path);
 assert(typeof ref.sha256==='string'&&/^[a-f0-9]{64}$/.exec(ref.sha256)?.[0]===ref.sha256);
 assert(Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=limit);assert.equal(await realpath(ref.path),ref.path);
 const before=await lstat(ref.path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1&&before.size===ref.bytes);
 const bytes=await readFile(ref.path);assert.deepEqual(stamp(await lstat(ref.path)),stamp(before));
 assert.equal(bytes.length,ref.bytes);assert.equal(hash(bytes),ref.sha256);return bytes;
}
async function publish(path,bytes){
 let handle,primary;
 try{handle=await open(path,'wx',0o600);await handle.writeFile(bytes);await handle.sync();}catch(error){primary=error;}
 finally{if(handle)try{await handle.close();}catch(error){primary??=error;}}
 if(primary)throw primary;
 const ref={path,sha256:hash(bytes),bytes:bytes.length};await refRead(ref,Math.max(bytes.length,1));
 return{ref,evidence:{complete:true,fsynced:true,closed:true,fileBytes:bytes.length,sha256:ref.sha256,errors:[]}};
}
function canonicalOrigin(text){
 const url=new URL(text);assert.equal(url.origin,text);assert.equal(url.protocol,'http:');assert.equal(url.hostname,'127.0.0.1');
 assert(url.port&&Number(url.port)!==80&&url.username===''&&url.password==='');return url;
}
async function bounded(promise,ms,message){
 let timer;try{return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>{const error=new Error(message);error.code='ERR_CONTROL_DEADLINE';reject(error);},ms);})]);}
 finally{clearTimeout(timer);}
}
const SYNTHETIC_HTML='<!doctype html><html><head><meta charset="utf-8"><title>Body control</title><link rel="icon" href="data:,"></head><body></body></html>';
const ALLOWED=['accept','content-type','next-action','next-router-state-tree','accept-language'];
const MANAGED=['host','connection','content-length','origin','referer','accept-encoding','sec-ch-ua-platform','sec-ch-ua','sec-ch-ua-mobile','sec-fetch-site','sec-fetch-mode','sec-fetch-dest','user-agent'];

async function main(){
 assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,6,'CLIENT ORIGIN FRESH_OUTPUT BROWSER_TOOLS RUN_ID');
 const origin=canonicalOrigin(process.argv[2]),output=resolve(process.argv[3]),tools=resolve(process.argv[4]),runId=process.argv[5];
 assert(/^[a-z0-9][a-z0-9-]{0,47}$/.exec(runId)?.[0]===runId);
 const policy=JSON.parse(await readFile(join(here,'plan.json'),'utf8'));
 assert(policy.requestCapture!==null,'Source request DATA unbound; no output/browser/HTTP');assert.equal(policy.requestCaptureBindingPending,false);
 assert.equal(policy.suite,'NEXT_RSC_BROWSER_BODY_PREWORK_CLIENT_V1');assert.equal(policy.bodyLimitBytes,4194304);
 assert.equal(policy.httpTimeoutMs,20000);assert.equal(policy.cleanupTimeoutMs,2000);assert.equal(policy.resultLimitBytes,16777216);
 assert.equal(policy.cdpMaxEvents,8000);assert.equal(policy.cdpMaxEventBytes,262144);assert.equal(policy.cdpMaxPayloadBytes,8388608);
 assert.equal(policy.netlogLimitBytes,20971520);assert.equal(tools,policy.browserTools);assert.equal(process.argv[4],tools);
 assert.equal(await realpath(tools),tools);assert.equal(output,process.argv[3]);assert.equal(await realpath(dirname(output)),dirname(output));
 const expectedRoot=runId==='rsc-browser-body-cloud-first'?'/private/tmp/starling-node-compat/next-rsc-browser-body-prework-cloud-v1-'+runId+'/client':runId==='rsc-browser-body-stock-first'?'/private/tmp/starling-node-compat/next-rsc-browser-body-prework-stock-v1-'+runId+'/client':null;
 assert.equal(output,expectedRoot);
 assert.deepEqual(Object.keys(policy.sourceRequirements).sort(),['headerEvidence','requestBody','requestCapture']);
 assert.deepEqual(policy.sourceRequirements.requestCapture,policy.requestCapture);
 const capture=JSON.parse(await refRead(policy.requestCapture,65536));
 assert.equal(capture.schemaVersion,1);assert.equal(capture.state,'RSC_ACTION_REQUEST_CAPTURE_DATA_V1');assert.equal(capture.verifiedDataCapturePassed,true);
 assert.equal(capture.method,'POST');assert.equal(capture.path,'/actions');
 const original=canonicalOrigin(capture.originalOrigin);assert.equal(capture.originalUrl,original.origin+capture.path);
 assert.deepEqual(policy.sourceRequirements.requestBody,capture.body);assert.deepEqual(policy.sourceRequirements.headerEvidence,capture.headerEvidence);
 const body=await refRead(capture.body,65536);await refRead(capture.headerEvidence,1048576);assert(body.length>0);
 assert.deepEqual(capture.rootSelectedReplayHeaderPolicy.removeHeaderNames,['x-next-public-request-correlation']);
 assert.deepEqual(capture.rootSelectedReplayHeaderPolicy.rewriteOriginBoundHeaderNames,['host','origin','referer']);
 assert.equal(capture.rootSelectedReplayHeaderPolicy.preserveAllOtherHeaders,true);assert.equal(capture.rootSelectedReplayHeaderPolicy.preserveBodyBytesAndMultipartBoundary,true);
 const captured=new Map();let headerBytes=0;
 assert(Array.isArray(capture.headers)&&capture.headers.length===19);
 for(const row of capture.headers){
  assert.deepEqual(Object.keys(row).sort(),['name','value']);assert(typeof row.name==='string'&&/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(row.name));
  assert(typeof row.value==='string'&&!/[\r\n\0]/.test(row.value));const name=row.name.toLowerCase();assert(!captured.has(name));captured.set(name,row.value);
  headerBytes+=Buffer.byteLength(row.name)+Buffer.byteLength(row.value);assert(headerBytes<=32768);
 }
 assert.deepEqual([...captured.keys()].sort(),[...ALLOWED,...MANAGED,'x-next-public-request-correlation'].sort());
 assert.equal(captured.get('host'),original.host);assert.equal(captured.get('origin'),original.origin);assert.equal(captured.get('referer'),capture.originalUrl);
 assert.equal(captured.get('content-length'),String(body.length));assert.equal(captured.get('next-action'),capture.application.actionId);
 assert.equal(captured.get('next-action').length,capture.application.actionIdObservedHexLength);
 const boundary=/^multipart\/form-data; boundary=([A-Za-z0-9-]{1,70})$/.exec(captured.get('content-type'));
 assert(boundary&&boundary[0]===captured.get('content-type'));
 assert(body.subarray(0,boundary[1].length+4).equals(Buffer.from('--'+boundary[1]+'\r\n')));
 assert(body.subarray(-boundary[1].length-6).equals(Buffer.from('--'+boundary[1]+'--\r\n')));
 const scriptHeaders=ALLOWED.map(name=>({name,value:captured.get(name)}));
 const preworkPaths={donorFullClient:join(here,'../next-fs-callback-full-client-v1/run-contracts.mjs'),portableCacheCollector:join(here,'../next-portable-cache-http-collector-v1/collector.mjs'),supplemental:join(here,'../wasmtime-deployment-candidate-v8/supplemental.mjs'),fixtureContract:join(here,'../fixture-contract.json')};
 assert.deepEqual(Object.keys(policy.preworkSourceRequirements).sort(),Object.keys(preworkPaths).sort());
 for(const[key,path]of Object.entries(preworkPaths)){assert.equal(policy.preworkSourceRequirements[key].path,resolve(path));await refRead(policy.preworkSourceRequirements[key],1048576);}
 assert.equal(policy.preworkModule.path,join(here,'prework.mjs'));await refRead(policy.preworkModule,1048576);
 assert(Array.isArray(policy.hostRequirements)&&policy.hostRequirements.length===6);
 for(const ref of policy.hostRequirements)await refRead(ref,2097152);
 const hostByPath=new Map(policy.hostRequirements.map(ref=>[ref.path,ref]));assert.equal(hostByPath.size,6);
 const fromTools=createRequire(join(tools,'package.json')),packagePath=fromTools.resolve('playwright-core/package.json'),entry=fromTools.resolve('playwright-core');
 for(const path of [packagePath,entry]){const rel=relative(tools,await realpath(path));assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));assert(hostByPath.has(path));}
 const pkg=JSON.parse(await refRead(hostByPath.get(packagePath),2097152));assert.equal(pkg.name,'playwright-core');assert.equal(pkg.version,'1.64.1');
 const chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';assert(hostByPath.has(chrome));
 await mkdir(output,{mode:0o700});
 const result={schemaVersion:1,suite:policy.suite,controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,
  origin:origin.origin,runId,requestCapture:policy.requestCapture,sourceRequirements:policy.sourceRequirements,
  preworkSourceRequirements:policy.preworkSourceRequirements,preworkModule:policy.preworkModule,hostRequirements:policy.hostRequirements,
  precedingWorkload:{executed:false,collectionComplete:false,passed:false,result:null,publication:null},
  responseProbeExecuted:false,collectionComplete:false,browserClosed:false,requestFidelityVerified:false,
  browserFetch:{attempted:false,settled:false,outcome:'unattempted',response:null,error:null},
  bodyRead:{attempted:false,outcome:'unattempted',bytes:null,postReadLimitBytes:policy.bodyLimitBytes,allocationPrebounded:false,error:null},
  networkTerminal:{kind:'unobserved',requestId:null,payload:null},browserBody:null,browserBodyPublication:null,
  request:{method:'POST',path:capture.path,url:origin.origin+capture.path,body:capture.body,bodyReserialized:false,scriptHeaders,
   removedHeaderNames:['x-next-public-request-correlation'],browserManagedOmissions:MANAGED.map(name=>({name,capturedValue:captured.get(name),scriptOverrideAttempted:false,observedValue:null,matchesCapturedWithOriginMapping:null})),
   requests:[],selectedPostRequest:null,scriptHeaderObservedMatches:[],semanticRequestNotWireIdentity:true},
  syntheticDocument:{url:origin.origin+capture.path,htmlBytes:Buffer.byteLength(SYNTHETIC_HTML),htmlSha256:hash(Buffer.from(SYNTHETIC_HTML)),
   externalResources:false,dataFavicon:true,fulfilled:0,routeTimes:1,unrouteCompletedBeforeFetch:false,observedLocation:null,
   provenance:'One test-harness document; no Next/React response or guest service. Routing/cache effects during bootstrap are disclosed.'},
  browser:{playwrightVersion:pkg.version,version:null,executable:hostByPath.get(chrome),tools,ephemeralContext:true,serviceWorkers:'block',userProfileUsed:false,wholeBundleHashClaimed:false},
  cdpEvents:[],cdpScope:{semanticPayloadsNotWireBytes:true,requestIdsIndependentFromPlaywrightAndNetlog:true,arrivalClock:'Node hrtime relative nanoseconds; no cross-clock conversion'},
  netlog:{requestedSizeMegabytes:16,limitBytes:policy.netlogLimitBytes,completeJson:false,fsynced:false,fileClosed:false,file:null,eventCount:null,historyCompleteProved:false,errors:[]},
  pageerrors:[],consoleerrors:[],failedrequests:[],collectionErrors:[],validationErrors:[],errors:[],passed:false,
  limits:{bodyPostReadBytes:policy.bodyLimitBytes,httpMilliseconds:policy.httpTimeoutMs,cleanupMilliseconds:policy.cleanupTimeoutMs,resultBytes:policy.resultLimitBytes},
  publicationFile:join(output,'publication.json')};
 partialResult=result;
 const collection=(stage,error)=>result.collectionErrors.push({stage,...errorData(error)});
 const check=(name,passed,detail=null)=>{if(!passed)result.validationErrors.push({name,detail});return passed;};
 try{result.precedingWorkload=await runPrework({origin:origin.origin,output});}catch(error){result.precedingWorkload.executed=true;collection('prework-publication',error);}
 if(!result.precedingWorkload.collectionComplete)collection('prework-collection',new Error('Fixed preceding workload did not complete'));
 let browser,context,page,launchPromise,abandoned=false,active=true,scriptDone=false,resolveObserved,rejectObserver,observerFailed=false,cdpBytes=0,cdpSequence=0,decodedBody=null;
 const observed=new Promise(yes=>{resolveObserved=yes;}),observerFailure=new Promise((_,no)=>{rejectObserver=no;});void observerFailure.catch(()=>{});
 const traceStart=process.hrtime.bigint(),posts=[],terminals=new Map(),requestExtra=new Map(),responseExtra=new Map();
 function observerError(stage,error){if(!active)return;collection(stage,error);if(!observerFailed){observerFailed=true;rejectObserver(error);}}
 function maybeObserved(){
  if(!scriptDone||posts.length!==1)return;
  const id=posts[0].payload.requestId,rows=terminals.get(id)??[];
  if(rows.length&&requestExtra.has(id)&&(result.browserFetch.response===null||responseExtra.has(id)))resolveObserved();
 }
 function noteCdp(event,payload){
  if(!active||observerFailed)return;
  try{
   const text=JSON.stringify(payload),bytes=Buffer.byteLength(text);
   if(result.cdpEvents.length>=policy.cdpMaxEvents||bytes>policy.cdpMaxEventBytes||cdpBytes+bytes>policy.cdpMaxPayloadBytes)throw new RangeError('CDP semantic capture bound exceeded');
   cdpBytes+=bytes;const row={sequence:++cdpSequence,event,arrivalNs:(process.hrtime.bigint()-traceStart).toString(),payloadBytes:bytes,payload:JSON.parse(text)};
   result.cdpEvents.push(row);
   if(event==='Network.requestWillBeSent'&&payload.request?.method==='POST'&&payload.request?.url===result.request.url)posts.push(row);
   if(event==='Network.requestWillBeSentExtraInfo'){const rows=requestExtra.get(payload.requestId)??[];rows.push(row);requestExtra.set(payload.requestId,rows);}
   if(event==='Network.responseReceivedExtraInfo'){const rows=responseExtra.get(payload.requestId)??[];rows.push(row);responseExtra.set(payload.requestId,rows);}
   if(event==='Network.loadingFinished'||event==='Network.loadingFailed'){const rows=terminals.get(payload.requestId)??[];rows.push(row);terminals.set(payload.requestId,rows);}
   maybeObserved();
  }catch(error){observerError('cdp-capture',error);}
 }
 if(result.precedingWorkload.collectionComplete){
  const attempt=(async()=>{
   const module=await import(pathToFileURL(entry).href),chromium=module.chromium??module.default?.chromium;assert(chromium);
   if(abandoned)return;
   launchPromise=chromium.launch({executablePath:chrome,headless:true,timeout:policy.httpTimeoutMs,args:['--log-net-log='+join(output,'netlog.json'),'--net-log-max-size-mb=16']});
   browser=await launchPromise;if(abandoned)return;
   result.browser.version=browser.version();assert.equal(result.browser.version,'156.0.8078.81');
   context=await browser.newContext({viewport:{width:1280,height:800},acceptDownloads:false,serviceWorkers:'block'});
   context.setDefaultTimeout(policy.httpTimeoutMs);context.setDefaultNavigationTimeout(policy.httpTimeoutMs);page=await context.newPage();
   page.on('request',request=>{if(!active||observerFailed)return;try{
    const url=request.url(),method=request.method(),navigation=request.isNavigationRequest(),type=request.resourceType();
    const role=url===result.syntheticDocument.url&&method==='GET'&&navigation&&type==='document'?'synthetic-document':url===result.request.url&&method==='POST'?'selected-post':'unexpected';
    const row={url,method,resourceType:type,isNavigationRequest:navigation,role};
    if(role==='selected-post'){const bytes=request.postDataBuffer();row.body=bytes?{bytes:bytes.length,sha256:hash(bytes)}:null;result.request.selectedPostRequest=row;}
    if(result.request.requests.length>=128)throw new RangeError('Browser request count exceeded');result.request.requests.push(row);
    if(role==='unexpected'&&/^https?:/.test(url))throw new Error('Unexpected workload request: '+url);
   }catch(error){observerError('request-observer',error);}});
   page.on('pageerror',error=>{if(active)result.pageerrors.push(errorData(error));});
   page.on('console',message=>{if(active&&message.type()==='error')result.consoleerrors.push({text:message.text(),location:message.location()});});
   page.on('requestfailed',request=>{if(active)result.failedrequests.push({url:request.url(),method:request.method(),failure:request.failure()});});
   const cdp=await context.newCDPSession(page);
   for(const event of ['Network.requestWillBeSent','Network.requestWillBeSentExtraInfo','Network.responseReceived','Network.responseReceivedExtraInfo','Network.dataReceived','Network.loadingFinished','Network.loadingFailed','Page.navigatedWithinDocument','Page.frameNavigated'])cdp.on(event,payload=>noteCdp(event,payload));
   await cdp.send('Network.enable');await cdp.send('Page.enable');
   const routeHandler=async route=>{try{
    const request=route.request();assert.equal(request.url(),result.syntheticDocument.url);assert.equal(request.method(),'GET');
    assert.equal(request.resourceType(),'document');assert.equal(request.isNavigationRequest(),true);assert.equal(request.frame(),page.mainFrame());
    assert.equal(result.syntheticDocument.fulfilled,0);result.syntheticDocument.fulfilled++;
    await route.fulfill({status:200,contentType:'text/html; charset=utf-8',body:SYNTHETIC_HTML});
   }catch(error){observerError('synthetic-document-route',error);try{await route.abort('failed');}catch(abortError){observerError('synthetic-document-abort',abortError);}}};
   if(abandoned)return;
   await page.route(result.syntheticDocument.url,routeHandler,{times:1});
   await page.goto(result.syntheticDocument.url,{waitUntil:'domcontentloaded'});
   assert.equal(result.syntheticDocument.fulfilled,1);await page.unroute(result.syntheticDocument.url,routeHandler);result.syntheticDocument.unrouteCompletedBeforeFetch=true;
   result.syntheticDocument.observedLocation=await page.evaluate(()=>({origin:location.origin,href:location.href,scripts:document.scripts.length}));
   assert.deepEqual(result.syntheticDocument.observedLocation,{origin:origin.origin,href:result.syntheticDocument.url,scripts:0});
   if(abandoned)return;
   result.browserFetch.attempted=true;
   const value=await page.evaluate(async({url,bodyBase64,headers,bodyLimit})=>{
    const describe=error=>({name:typeof error?.name==='string'?error.name:'Error',message:typeof error?.message==='string'?error.message:String(error)});
    const out={fetchOutcome:'unattempted',response:null,fetchError:null,bodyOutcome:'unattempted',bodyBytes:null,bodyError:null,bodyBase64:null,overLimit:false};
    const binary=atob(bodyBase64),bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
    let response;
    try{response=await window.fetch(url,{method:'POST',headers:headers.map(({name,value})=>[name,value]),body:bytes,redirect:'manual'});out.fetchOutcome='fulfilled';
     out.response={url:response.url,status:response.status,statusText:response.statusText,type:response.type,redirected:response.redirected,headers:Array.from(response.headers,([name,value])=>({name,value}))};
    }catch(error){out.fetchOutcome='rejected';out.fetchError=describe(error);return out;}
    let buffer;
    try{buffer=await response.arrayBuffer();}catch(error){out.bodyOutcome='rejected';out.bodyError=describe(error);return out;}
    out.bodyOutcome='fulfilled';out.bodyBytes=buffer.byteLength;
    if(buffer.byteLength>bodyLimit){out.overLimit=true;return out;}
    try{const bytes=new Uint8Array(buffer);let binary='';for(let i=0;i<bytes.length;i++)binary+=String.fromCharCode(bytes[i]);out.bodyBase64=btoa(binary);
    }catch(error){out.bodySerializationError=describe(error);}
    return out;
   },{url:result.request.url,bodyBase64:body.toString('base64'),headers:scriptHeaders,bodyLimit:policy.bodyLimitBytes});
   if(!active)return;
   assert(['fulfilled','rejected'].includes(value.fetchOutcome));result.browserFetch.settled=true;result.browserFetch.outcome=value.fetchOutcome;result.browserFetch.response=value.response;result.browserFetch.error=value.fetchError;
   assert(['fulfilled','rejected','unattempted'].includes(value.bodyOutcome));result.bodyRead.attempted=value.bodyOutcome!=='unattempted';result.bodyRead.outcome=value.bodyOutcome;result.bodyRead.bytes=value.bodyBytes;result.bodyRead.error=value.bodyError;
   if(value.bodySerializationError)throw new Error('Fulfilled arrayBuffer serialization failed: '+value.bodySerializationError.message);
   if(value.overLimit)throw new RangeError('arrayBuffer exceeded post-read4MiB retention cap; allocation was not prebounded');
   if(value.bodyOutcome==='fulfilled'){
    assert(typeof value.bodyBase64==='string');decodedBody=Buffer.from(value.bodyBase64,'base64');assert.equal(decodedBody.toString('base64'),value.bodyBase64);
    assert.equal(decodedBody.length,value.bodyBytes);assert(decodedBody.length<=policy.bodyLimitBytes);
   }
   scriptDone=true;maybeObserved();await observed;
  })();
  void attempt.catch(()=>{});
  try{await bounded(Promise.race([attempt,observerFailure]),policy.httpTimeoutMs,'Absolute20s browser attempt deadline');}
  catch(error){abandoned=true;collection('browser-attempt',error);if(error?.code==='ERR_CONTROL_DEADLINE'&&!scriptDone){if(!result.browserFetch.settled)result.browserFetch.outcome='timedout';if(result.bodyRead.outcome==='unattempted'&&result.browserFetch.attempted)result.bodyRead.outcome='timedout';}}
 }
 const cleanup=(async()=>{
  if(launchPromise&&!browser)try{browser=await launchPromise;}catch(error){collection('browser-launch-finalization',error);}
  if(context)try{await context.close();}catch(error){collection('context-close',error);}
  if(browser)try{await browser.close();result.browserClosed=!browser.isConnected();}catch(error){collection('browser-close',error);}
 })();void cleanup.catch(()=>{});
 try{await bounded(cleanup,policy.cleanupTimeoutMs,'Absolute2s browser cleanup deadline');}catch(error){collection('browser-cleanup',error);}
 active=false;
 result.responseProbeExecuted=result.browserFetch.attempted&&result.browserFetch.settled;
 if(posts.length===1){
  const id=posts[0].payload.requestId,rows=terminals.get(id)??[];
  result.networkTerminal=rows.length===1?{kind:rows[0].event==='Network.loadingFinished'?'loadingFinished':'loadingFailed',requestId:id,payload:rows[0].payload}:{kind:rows.length?'ambiguous':'unobserved',requestId:id,payload:null};
  const extras=requestExtra.get(id)??[],responses=responseExtra.get(id)??[];
  if(extras.length===1&&(result.browserFetch.response===null||responses.length===1)){
   const actual=new Map(Object.entries(extras[0].payload.headers??{}).map(([name,value])=>{assert.equal(typeof value,'string');return[name.toLowerCase(),value];}));
   result.request.extraInfo={request:extras[0],response:responses[0]??null};
   result.request.scriptHeaderObservedMatches=scriptHeaders.map(({name,value})=>({name,expected:value,observed:actual.get(name)??null,matches:actual.get(name)===value}));
   for(const row of result.request.browserManagedOmissions){
    const expected=row.name==='host'?origin.host:row.name==='origin'?origin.origin:row.name==='referer'?result.request.url:row.capturedValue;
    row.observedValue=actual.get(row.name)??null;row.matchesCapturedWithOriginMapping=row.observedValue===expected;
   }
   const selected=result.request.requests.filter(x=>x.role==='selected-post');
   result.requestFidelityVerified=selected.length===1&&selected[0].body?.bytes===body.length&&selected[0].body?.sha256===capture.body.sha256
    &&result.request.scriptHeaderObservedMatches.every(x=>x.matches)&&actual.get('host')===origin.host&&actual.get('origin')===origin.origin
    &&actual.get('referer')===result.request.url&&actual.get('content-length')===String(body.length)&&!actual.has('x-next-public-request-correlation')
    &&result.syntheticDocument.fulfilled===1&&result.syntheticDocument.unrouteCompletedBeforeFetch===true
    &&!result.request.requests.some(x=>x.role==='unexpected'&&/^https?:/.test(x.url));
  }
 }
 if(result.precedingWorkload.collectionComplete&&!result.requestFidelityVerified)collection('request-fidelity',new Error('One admitted POST/body/header/ExtraInfo tuple was not observed'));
 if(!['loadingFinished','loadingFailed'].includes(result.networkTerminal.kind)&&result.precedingWorkload.collectionComplete)collection('network-terminal',new Error('Unknown or ambiguous selected POST terminal'));
 if(browser&&!result.browserClosed)collection('browser-finalization',new Error('Normal browser closure not observed'));
 if(result.browserClosed){
  let handle;
  try{
   const path=join(output,'netlog.json'),before=await lstat(path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1&&before.size>0&&before.size<=policy.netlogLimitBytes);assert.equal(await realpath(path),path);
   handle=await open(path,'r+');const opened=await handle.stat();assert.equal(opened.dev,before.dev);assert.equal(opened.ino,before.ino);assert.equal(opened.size,before.size);
   await handle.chmod(0o600);await handle.sync();result.netlog.fsynced=true;const start=await handle.stat();assert(start.size>0&&start.size<=policy.netlogLimitBytes);const bytes=await handle.readFile();assert.equal(bytes.length,start.size);
   const parsed=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));assert(parsed&&typeof parsed.constants==='object'&&Array.isArray(parsed.events));
   assert.deepEqual(stamp(await handle.stat()),stamp(start));assert.deepEqual(stamp(await lstat(path)),stamp(start));
   result.netlog.completeJson=true;result.netlog.eventCount=parsed.events.length;result.netlog.file={path,sha256:hash(bytes),bytes:bytes.length};
  }catch(error){result.netlog.errors.push(errorData(error));collection('netlog-publication',error);}
  finally{if(handle)try{await handle.close();result.netlog.fileClosed=true;}catch(error){result.netlog.errors.push(errorData(error));collection('netlog-close',error);}}
 }
 if(decodedBody!==null&&result.bodyRead.outcome==='fulfilled')try{
  const publication=await publish(join(output,'browser-body.bin'),decodedBody);result.browserBody=publication.ref;result.browserBodyPublication=publication.evidence;
 }catch(error){collection('browser-body-publication',error);}
 check('prework-passed',result.precedingWorkload.passed);check('fetch-fulfilled',result.browserFetch.outcome==='fulfilled');check('arrayBuffer-fulfilled',result.bodyRead.outcome==='fulfilled');
 check('selected-network-loadingFinished',result.networkTerminal.kind==='loadingFinished');check('browser-closed',result.browserClosed);
 const response=result.browserFetch.response,headers=new Map((response?.headers??[]).map(({name,value})=>[name.toLowerCase(),value]));
 check('HTTP200',response?.status===200);check('no-redirect-followed',response?.redirected===false);check('Content-Encoding-absent',response!==null&&!headers.has('content-encoding'));
 check('RSC-content-type',headers.get('content-type')?.startsWith('text/x-component')===true);check('action-redirect',headers.get('x-action-redirect')==='/action-result?value=browser-action;push');
 if(decodedBody!==null){const text=decodedBody.toString('utf8');for(const marker of ['NEXT_ACTION_RESULT','browser-action'])check('RSC-marker:'+marker,text.includes(marker));}
 check('no-page-errors',result.pageerrors.length===0);check('no-console-errors',result.consoleerrors.length===0);check('no-request-failures',result.failedrequests.length===0);
 for(const[key,limit]of [['requestCapture',65536],['requestBody',65536],['headerEvidence',1048576]])try{await refRead(policy.sourceRequirements[key],limit);}catch(error){collection('input-final:'+key,error);}
 for(const ref of Object.values(policy.preworkSourceRequirements))try{await refRead(ref,1048576);}catch(error){collection('prework-source-final',error);}
 try{await refRead(policy.preworkModule,1048576);if(result.precedingWorkload.result)await refRead(result.precedingWorkload.result,16777216);}catch(error){collection('prework-result-final',error);}
 for(const ref of policy.hostRequirements)try{await refRead(ref,2097152);}catch(error){collection('host-source-final',error);}
 result.collectionComplete=result.precedingWorkload.collectionComplete&&result.responseProbeExecuted&&result.requestFidelityVerified&&result.browserClosed
  &&['loadingFinished','loadingFailed'].includes(result.networkTerminal.kind)&&['fulfilled','rejected','unattempted'].includes(result.bodyRead.outcome)
  &&result.netlog.completeJson&&result.netlog.fsynced&&result.netlog.fileClosed&&result.collectionErrors.length===0;
 result.errors=[...result.collectionErrors,...result.validationErrors];result.passed=result.collectionComplete&&result.validationErrors.length===0;
 const bytes=Buffer.from(JSON.stringify(result)+'\n');assert(bytes.length<=policy.resultLimitBytes);
 const published=await publish(join(output,'result.json'),bytes);
 const receipt={schemaVersion:1,state:'RSC_HTTP_RESPONSE_CLIENT_PUBLICATION_COMPLETE_V1',result:published.ref,resultPublication:published.evidence,
  browserBody:result.browserBody,browserBodyPublication:result.browserBodyPublication,collectionComplete:result.collectionComplete,browserClosed:result.browserClosed,
  responseProbeExecuted:result.responseProbeExecuted,complete:true,errors:[]};
 const publication=await publish(join(output,'publication.json'),Buffer.from(JSON.stringify(receipt,null,2)+'\n'));
 writeFileSync(1,JSON.stringify({state:'RSC_HTTP_RESPONSE_CLIENT_TERMINAL_PUBLISHED_V1',suite:policy.suite,result:published.ref,publication:publication.ref,
  passed:result.passed,responseProbeExecuted:result.responseProbeExecuted,collectionComplete:result.collectionComplete,browserClosed:result.browserClosed,collectionErrors:result.collectionErrors.length})+'\n');
 process.exitCode=result.passed?0:1;
}
main().catch(error=>{process.exitCode=1;try{writeFileSync(2,JSON.stringify({state:'RSC_HTTP_RESPONSE_CLIENT_COLLECTION_FAILURE_V1',error:errorData(error),partialResult:partialResult??null})+'\n');}catch{}});
