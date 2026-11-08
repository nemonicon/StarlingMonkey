// One captured semantic HTTP request; Root separately proves the actual host.
import assert from 'node:assert/strict';
import {runPrework} from './prework.mjs';
import http from 'node:http';
import {createHash} from 'node:crypto';
import {writeFileSync} from 'node:fs';
import {readFile,open,mkdir,lstat,realpath} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const here=dirname(fileURLToPath(import.meta.url));
let partialResult;
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const stamp=s=>[s.dev,s.ino,s.mode,s.nlink,s.size,s.mtimeMs,s.ctimeMs];
const errorData=e=>({name:typeof e?.name==='string'?e.name:'Error',code:typeof e?.code==='string'?e.code:null,message:typeof e?.message==='string'?e.message:String(e)});
async function refRead(ref,limit){
 assert(ref&&typeof ref==='object'&&!Array.isArray(ref));
 assert.deepEqual(Object.keys(ref).sort(),['bytes','path','sha256']);
 assert(typeof ref.path==='string'&&resolve(ref.path)===ref.path);
 assert(typeof ref.sha256==='string'&&ref.sha256.length===64&&/^[a-f0-9]+$/.test(ref.sha256));
 assert(Number.isSafeInteger(ref.bytes)&&ref.bytes>=0&&ref.bytes<=limit);
 assert.equal(await realpath(ref.path),ref.path);
 const before=await lstat(ref.path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1&&before.size===ref.bytes);
 const bytes=await readFile(ref.path);assert.deepEqual(stamp(await lstat(ref.path)),stamp(before));
 assert.equal(bytes.length,ref.bytes);assert.equal(hash(bytes),ref.sha256);return bytes;
}
async function publish(path,bytes){
 let handle,primary;
 try{handle=await open(path,'wx',0o600);await handle.writeFile(bytes);await handle.sync();}
 catch(error){primary=error;}
 finally{if(handle)try{await handle.close();}catch(error){primary??=error;}}
 if(primary)throw primary;
 const ref={path,sha256:hash(bytes),bytes:bytes.length};await refRead(ref,Math.max(bytes.length,1));
 return {ref,evidence:{complete:true,fsynced:true,closed:true,fileBytes:bytes.length,sha256:ref.sha256,errors:[]}};
}
function canonicalOrigin(text){
 assert.equal(typeof text,'string');const url=new URL(text);
 assert.equal(url.origin,text);assert.equal(url.protocol,'http:');assert.equal(url.hostname,'127.0.0.1');
 assert(url.port&&Number(url.port)!==80&&url.username===''&&url.password==='');return url;
}

async function main(){
 assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,6,'CLIENT ORIGIN FRESH_OUTPUT RESERVED RUN_ID');
 const origin=canonicalOrigin(process.argv[2]),output=resolve(process.argv[3]),runId=process.argv[5];
 assert.equal(typeof process.argv[4],'string'); // Reserved CLI slot: no tools/browser IO.
 assert(/^[a-z0-9][a-z0-9-]{0,47}$/.exec(runId)?.[0]===runId);
 const policy=JSON.parse(await readFile(join(here,'plan.json'),'utf8'));
 assert(policy.requestCapture!==null,'Source request DATA is unbound; no output or HTTP');
 assert.equal(policy.requestCaptureBindingPending,false);
 assert.equal(policy.suite,'NEXT_RSC_IDENTITY_PREWORK_HTTP_CLIENT_V1');
 assert.equal(policy.encodedBodyLimit,4194304);assert.equal(policy.decodedBodyLimit,16777216);
 assert.equal(policy.httpTimeoutMs,20000);assert.equal(policy.cleanupTimeoutMs,2000);
 const expectedRoot=runId==='rsc-identity-cloud-first'?'/private/tmp/starling-node-compat/next-rsc-identity-prework-cloud-v1-'+runId+'/client':runId==='rsc-identity-stock-first'?'/private/tmp/starling-node-compat/next-rsc-identity-prework-stock-v1-'+runId+'/client':null;
 assert.equal(output,expectedRoot);assert.equal(output,process.argv[3]);
 assert.equal(await realpath(dirname(output)),dirname(output));
 assert.deepEqual(Object.keys(policy.sourceRequirements).sort(),['headerEvidence','requestBody','requestCapture']);
 assert.deepEqual(policy.sourceRequirements.requestCapture,policy.requestCapture);
 const capture=JSON.parse(await refRead(policy.requestCapture,65536));
 assert.equal(capture.schemaVersion,1);assert.equal(capture.state,'RSC_ACTION_REQUEST_CAPTURE_DATA_V1');
 assert.equal(capture.verifiedDataCapturePassed,true);assert.equal(capture.method,'POST');assert.equal(capture.path,'/actions');
 const original=canonicalOrigin(capture.originalOrigin);
 assert.equal(capture.originalUrl,original.origin+capture.path);
 assert.deepEqual(policy.sourceRequirements.requestBody,capture.body);
 assert.deepEqual(policy.sourceRequirements.headerEvidence,capture.headerEvidence);
 const body=await refRead(capture.body,65536);await refRead(capture.headerEvidence,1048576);
 assert(body.length>0);assert.deepEqual(capture.rootSelectedReplayHeaderPolicy.removeHeaderNames,['x-next-public-request-correlation']);
 assert.deepEqual(capture.rootSelectedReplayHeaderPolicy.rewriteOriginBoundHeaderNames,['host','origin','referer']);
 assert.equal(capture.rootSelectedReplayHeaderPolicy.preserveAllOtherHeaders,true);
 assert.equal(capture.rootSelectedReplayHeaderPolicy.preserveBodyBytesAndMultipartBoundary,true);
 assert(Array.isArray(capture.headers)&&capture.headers.length>0&&capture.headers.length<=64);
 const names=new Map(),headers=[],changes=[];let headerBytes=0;
 for(const row of capture.headers){
  assert.deepEqual(Object.keys(row).sort(),['name','value']);
  assert(typeof row.name==='string'&&/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(row.name));
  assert(typeof row.value==='string'&&!/[\r\n\0]/.test(row.value));
  headerBytes+=Buffer.byteLength(row.name)+Buffer.byteLength(row.value);assert(headerBytes<=32768);
  const lower=row.name.toLowerCase();assert(!names.has(lower),'Captured unique headers required');names.set(lower,row.value);
  if(lower==='x-next-public-request-correlation'){changes.push({name:row.name,operation:'remove-captured-public-header'});continue;}
  let value=row.value;
  if(lower==='host'){assert.equal(value,original.host);value=origin.host;}
  if(lower==='origin'){assert.equal(value,original.origin);value=origin.origin;}
  if(lower==='referer'){assert.equal(value,capture.originalUrl);value=origin.origin+capture.path;}
  if(value!==row.value)changes.push({name:row.name,operation:'canonical-origin-substitution',before:row.value,after:value});
  headers.push(row.name,value);
 }
 for(const name of ['host','origin','referer','accept-encoding','content-length','content-type','next-action','next-router-state-tree','x-next-public-request-correlation'])assert(names.has(name));
 assert.equal(names.get('content-length'),String(body.length));assert(!names.has('transfer-encoding'));
 assert.equal(names.get('next-action'),capture.application.actionId);
 assert.equal(names.get('next-action').length,capture.application.actionIdObservedHexLength);
 assert(names.get('accept-encoding').split(',').map(x=>x.trim()).includes('gzip'));
 const boundary=/^multipart\/form-data; boundary=([A-Za-z0-9-]{1,70})$/.exec(names.get('content-type'));
 assert(boundary&&boundary[0]===names.get('content-type'));
 assert(body.subarray(0,boundary[1].length+4).equals(Buffer.from('--'+boundary[1]+'\r\n')));
 assert(body.subarray(-boundary[1].length-6).equals(Buffer.from('--'+boundary[1]+'--\r\n')));
 const preworkPaths={donorFullClient:join(here,'../next-fs-callback-full-client-v1/run-contracts.mjs'),
  portableCacheCollector:join(here,'../next-portable-cache-http-collector-v1/collector.mjs'),
  supplemental:join(here,'../wasmtime-deployment-candidate-v8/supplemental.mjs'),fixtureContract:join(here,'../fixture-contract.json')};
 assert.deepEqual(Object.keys(policy.preworkSourceRequirements).sort(),Object.keys(preworkPaths).sort());
 for(const[key,path]of Object.entries(preworkPaths)){assert.equal(policy.preworkSourceRequirements[key].path,resolve(path));await refRead(policy.preworkSourceRequirements[key],1048576);}
 assert.equal(policy.preworkModule.path,join(here,'prework.mjs'));await refRead(policy.preworkModule,1048576);
 await mkdir(output,{mode:0o700});
 const result={schemaVersion:1,suite:policy.suite,controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,
  origin:origin.origin,runId,requestCapture:policy.requestCapture,sourceRequirements:policy.sourceRequirements,
  preworkSourceRequirements:policy.preworkSourceRequirements,preworkModule:policy.preworkModule,
  precedingWorkload:{executed:false,collectionComplete:false,passed:false,result:null,publication:null},
  publicHeaderPolicy:'captured public header removed; no replacement, manifest consumption or join',
  semanticRequestNotWireIdentity:true,responseProbeExecuted:false,responseCollectionComplete:false,
  limits:{encodedBodyBytes:policy.encodedBodyLimit,decodedBodyBytes:policy.decodedBodyLimit,httpMilliseconds:policy.httpTimeoutMs,cleanupMilliseconds:policy.cleanupTimeoutMs},
  request:{attempted:false,created:false,method:capture.method,path:capture.path,url:origin.origin+capture.path,headers,headerChanges:changes,
   body:capture.body,bodyReserialized:false,finishObserved:false,closeObserved:false,errors:[]},
  response:{received:false,statusCode:null,statusMessage:null,httpVersion:null,headers:null,rawHeaders:[],trailers:null,rawTrailers:[],
   complete:false,endObserved:false,abortedObserved:false,closeObserved:false,errors:[],information:[],encodedBody:null,encodedBodyPublication:null,decodedBody:null,decodedBodyPublication:null,identity:null,
   rawCapture:{observedBytes:0,retainedBytes:0,overflow:false,unretainedBytesUnknown:false,allObservedBytesCaptured:false,
    scope:'All IncomingMessage data events, after transfer framing and before content decoding; not unseen wire bytes or HTTP completion'}},
  connection:{socketAssigned:false,socketCloseObserved:false,socketCloseHadError:null,errors:[],cleanupRequested:false,cleanupRequestedAfterResponseEnd:false,cleanupCompleted:false},
  collectionErrors:[],validationErrors:[],errors:[],passed:false,publicationFile:join(output,'publication.json')};
 partialResult=result;
 const chunks=[];
 const collection=(stage,error)=>result.collectionErrors.push({stage,...errorData(error)});
 try{result.precedingWorkload=await runPrework({origin:origin.origin,output});}
 catch(error){result.precedingWorkload.executed=true;collection('prework-publication',error);}
 if(!result.precedingWorkload.collectionComplete)collection('prework-collection',new Error('Fixed preceding workload collection did not complete'));
 if(result.precedingWorkload.collectionComplete){
 await new Promise(resolveAttempt=>{
  let request,response,socket,httpTimer,cleanupTimer,closing=false,settled=false;
  function completeSnapshot(){if(response){result.response.complete=response.complete===true;result.response.trailers=response.trailers;result.response.rawTrailers=response.rawTrailers??[];}}
  function finishIfClosed(){
   if(!closing||settled||(request&&!result.request.closeObserved)||(socket&&!result.connection.socketCloseObserved))return;
   settled=true;clearTimeout(httpTimer);clearTimeout(cleanupTimer);completeSnapshot();result.connection.cleanupCompleted=true;resolveAttempt();
  }
  function cleanup(reason){
   if(closing)return;closing=true;result.terminalReason=reason;clearTimeout(httpTimer);completeSnapshot();
   result.connection.cleanupRequested=true;result.connection.cleanupRequestedAfterResponseEnd=result.response.endObserved;
   cleanupTimer=setTimeout(()=>{if(settled)return;settled=true;completeSnapshot();collection('cleanup',new Error('Owned request/socket close was not observed within cleanup deadline'));resolveAttempt();},policy.cleanupTimeoutMs);
   try{request?.destroy();socket?.destroy();}catch(error){collection('cleanup.destroy',error);}
   finishIfClosed();
  }
  try{
   result.request.attempted=true;
   request=http.request(new URL(capture.path,origin),{method:capture.method,headers,agent:false,maxHeaderSize:65536},incoming=>{
    response=incoming;result.response.received=true;result.response.statusCode=incoming.statusCode??null;
    result.response.statusMessage=incoming.statusMessage??null;result.response.httpVersion=incoming.httpVersion;
    result.response.headers=incoming.headers;result.response.rawHeaders=[...incoming.rawHeaders];
    if(incoming.rawHeaders.length>=256){collection('response.headers',new Error('Response header count reached collection bound'));cleanup('header-limit');}
    incoming.on('data',chunk=>{
     try{
      if(!Buffer.isBuffer(chunk)){result.response.rawCapture.unretainedBytesUnknown=true;throw new TypeError('Uncoerced Buffer data event required');}
      const raw=result.response.rawCapture;raw.observedBytes+=chunk.length;
      const remaining=Math.max(0,policy.encodedBodyLimit-raw.retainedBytes);
      const keep=chunks.length>=policy.maximumEncodedChunks?0:Math.min(remaining,chunk.length);
      if(keep){chunks.push(Buffer.from(chunk.subarray(0,keep)));raw.retainedBytes+=keep;}
      if(keep!==chunk.length){raw.overflow=true;collection('response.body',new RangeError('Encoded body/chunk collection limit exceeded'));cleanup('encoded-limit');}
     }catch(error){result.response.rawCapture.unretainedBytesUnknown=true;collection('response.data',error);cleanup('collector-error');}
    });
    incoming.on('aborted',()=>{result.response.abortedObserved=true;completeSnapshot();cleanup('response-aborted');});
    incoming.on('error',error=>{result.response.errors.push(errorData(error));completeSnapshot();cleanup('response-error');});
    incoming.on('end',()=>{result.response.endObserved=true;completeSnapshot();cleanup('response-end');});
    incoming.on('close',()=>{result.response.closeObserved=true;completeSnapshot();if(!closing)cleanup('response-close-without-end');});
   });
   result.request.created=true;
   request.maxHeadersCount=128;
   request.on('socket',owned=>{
    socket=owned;result.connection.socketAssigned=true;
    owned.on('error',error=>{result.connection.errors.push(errorData(error));cleanup('socket-error');});
    owned.on('close',hadError=>{result.connection.socketCloseObserved=true;result.connection.socketCloseHadError=hadError;finishIfClosed();});
    if(closing)owned.destroy();
   });
   request.on('finish',()=>{result.request.finishObserved=true;});
   request.on('error',error=>{result.request.errors.push(errorData(error));cleanup('request-error');});
   request.on('close',()=>{result.request.closeObserved=true;if(!closing)cleanup('request-close');finishIfClosed();});
   request.on('information',info=>{const row={statusCode:info.statusCode,headers:info.headers,rawHeaders:info.rawHeaders};if(result.response.information.length>=16||Buffer.byteLength(JSON.stringify([...result.response.information,row]))>65536){collection('response.information',new Error('Interim header bound exceeded'));cleanup('information-limit');}else result.response.information.push(row);});
   request.on('upgrade',(_res,owned,head)=>{result.response.rawCapture.unretainedBytesUnknown=true;collection('response.upgrade',new Error('Upgrade is outside this one-response protocol'));socket=owned;result.connection.socketAssigned=true;owned.on('close',hadError=>{result.connection.socketCloseObserved=true;result.connection.socketCloseHadError=hadError;finishIfClosed();});owned.on('error',error=>result.connection.errors.push(errorData(error)));cleanup('unexpected-upgrade');});
   httpTimer=setTimeout(()=>{result.request.errors.push({name:'Error',code:'ERR_RSC_HTTP_TIMEOUT',message:'Absolute20s HTTP deadline reached'});cleanup('http-timeout');},policy.httpTimeoutMs);
   request.end(body);
  }catch(error){result.request.errors.push(errorData(error));if(!result.request.created)collection('request-construction',error);cleanup('request-synchronous-error');}
 });
 }else{result.terminalReason='prework-collection-incomplete';result.connection.cleanupCompleted=true;}
 await new Promise(resolveTick=>setImmediate(resolveTick));
 const raw=result.response.rawCapture,encoded=Buffer.concat(chunks,raw.retainedBytes);
 raw.allObservedBytesCaptured=!raw.overflow&&!raw.unretainedBytesUnknown&&encoded.length===raw.observedBytes;
 try{
  const encodedPublication=await publish(join(output,'body.raw.bin'),encoded);
  result.response.encodedBody=encodedPublication.ref;result.response.encodedBodyPublication=encodedPublication.evidence;
  result.response.encodedBodyPublication.complete=raw.allObservedBytesCaptured;
 }catch(error){
  result.response.encodedBodyPublication={complete:false,fsynced:false,closed:false,fileBytes:null,sha256:null,errors:[errorData(error)]};
  collection('encoded-body-publication',error);
 }
 result.responseCollectionComplete=result.response.received&&result.response.endObserved&&result.response.complete&&!result.response.abortedObserved
  &&result.response.errors.length===0&&result.request.errors.length===0&&result.connection.errors.length===0&&result.collectionErrors.length===0
  &&raw.allObservedBytesCaptured&&result.connection.cleanupCompleted;
 const check=(name,passed,detail=null)=>{if(!passed)result.validationErrors.push({name,detail});return passed;};
 check('preceding-workload-passed',result.precedingWorkload.passed);
 check('HTTP200',result.response.statusCode===200);check('HTTP-response-complete',result.responseCollectionComplete);
 const headersObserved=result.response.received&&result.response.headers!==null;
 const codingPresent=headersObserved&&Object.hasOwn(result.response.headers,'content-encoding');
 const identityEligible=headersObserved&&!codingPresent;
 check('Content-Encoding-absent',identityEligible);
 result.response.identity={operation:'identity-copy',responseHeadersObserved:headersObserved,contentEncodingHeaderPresent:codingPresent,
  observedContentEncoding:codingPresent?result.response.headers['content-encoding']:null,copyAttempted:identityEligible,copyPublished:false,
  copiedBytes:null,copiedBytesEqualRetainedRaw:null,contentDecodingPerformed:false,
  completeHttpBody:result.responseCollectionComplete,
  scope:result.responseCollectionComplete?'Complete observed HTTP entity body after transfer framing; identity copy, not wire framing'
   :'Observed entity-body prefix after transfer framing; HTTP completion is not established'};
 check('RSC-content-type',typeof result.response.headers?.['content-type']==='string'&&result.response.headers['content-type'].startsWith('text/x-component'));
 check('action-redirect',result.response.headers?.['x-action-redirect']==='/action-result?value=browser-action;push');
 if(identityEligible)try{
  const decoded=Buffer.from(encoded);assert(decoded.length<=policy.decodedBodyLimit);
  const decodedPublication=await publish(join(output,'body.decoded.bin'),decoded);
  result.response.decodedBody=decodedPublication.ref;result.response.decodedBodyPublication=decodedPublication.evidence;
  result.response.identity.copyPublished=true;result.response.identity.copiedBytes=decoded.length;
  result.response.identity.copiedBytesEqualRetainedRaw=decoded.equals(encoded);
  check('identity-copy-equals-retained-raw',result.response.identity.copiedBytesEqualRetainedRaw);
  const text=decoded.toString('utf8');for(const marker of ['NEXT_ACTION_RESULT','browser-action'])check('RSC-marker:'+marker,text.includes(marker));
 }catch(error){
  collection('identity-body-publication',error);
 }
 // Input read bookends are collection evidence, never inferred from HTTP200.
 for(const [key,limit] of [['requestCapture',65536],['requestBody',65536],['headerEvidence',1048576]])
  try{await refRead(policy.sourceRequirements[key],limit);}catch(error){collection('input-final:'+key,error);}
 for(const ref of Object.values(policy.preworkSourceRequirements))try{await refRead(ref,1048576);}catch(error){collection('prework-input-final',error);}
 try{await refRead(policy.preworkModule,1048576);if(result.precedingWorkload.result)await refRead(result.precedingWorkload.result,1048576);}catch(error){collection('prework-output-or-module-final',error);}
 result.responseProbeExecuted=result.request.attempted&&typeof result.terminalReason==='string'&&result.connection.cleanupCompleted
  &&result.response.encodedBody!==null;
 result.errors=[...result.collectionErrors,...result.validationErrors];
 result.passed=result.responseProbeExecuted&&result.responseCollectionComplete&&result.collectionErrors.length===0&&result.validationErrors.length===0;
 const resultBytes=Buffer.from(JSON.stringify(result,null,2)+'\n');assert(resultBytes.length<=1048576);
 const publishedResult=await publish(join(output,'result.json'),resultBytes);
 const publication={schemaVersion:1,state:'RSC_HTTP_RESPONSE_CLIENT_PUBLICATION_COMPLETE_V1',result:publishedResult.ref,
  resultPublication:publishedResult.evidence,
  encodedBody:result.response.encodedBody,decodedBody:result.response.decodedBody,
  responseProbeExecuted:result.responseProbeExecuted,responseCollectionComplete:result.responseCollectionComplete,
  encodedBodyPublication:result.response.encodedBodyPublication,complete:true,errors:[]};
 const receipt=await publish(join(output,'publication.json'),Buffer.from(JSON.stringify(publication,null,2)+'\n'));
 writeFileSync(1,JSON.stringify({state:'RSC_HTTP_RESPONSE_CLIENT_TERMINAL_PUBLISHED_V1',suite:policy.suite,
  result:publishedResult.ref,publication:receipt.ref,passed:result.passed,responseProbeExecuted:result.responseProbeExecuted,
  responseCollectionComplete:result.responseCollectionComplete,collectionErrors:result.collectionErrors.length})+'\n');
 process.exitCode=result.passed?0:1;
}
main().catch(error=>{
 process.exitCode=1;
 try{writeFileSync(2,JSON.stringify({state:'RSC_HTTP_RESPONSE_CLIENT_COLLECTION_FAILURE_V1',error:errorData(error),partialResult:partialResult??null})+'\n');}
 catch{ /* Missing terminal publication still prevents Root continuation. */ }
});
