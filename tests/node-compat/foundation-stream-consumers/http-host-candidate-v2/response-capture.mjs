// Injected host-response transport only. No default fetch, filesystem or host action.
import {Buffer} from 'node:buffer';
import {readinessRetryAllowed} from '../http-host-candidate-v1/models.mjs';
const info=e=>({type:typeof e,name:typeof e?.name==='string'?e.name:null,message:typeof e?.message==='string'?e.message.slice(0,2048):null});
export function captureSetSummary(captures){
 if(!Array.isArray(captures))throw Error('Per-attempt capture array required');
 return{responseCaptures:captures,availableResponseRawRetained:captures.length?captures.every(c=>c.availableRawRetained===true):null,
  responseCaptureWriteFailureObserved:captures.some(c=>c.captureProtocolFailure===true||c.captureWriteFailures?.length>0||(c.requestFailed===true&&c.failureRecordRetained===false))};
}
export async function captureResponse({name,url,tag,fetchResponse,writeJson,writeBytes,maxBytes=16*1024*1024}){
 if(!/^requests\/(?:wasmtime|wash)-[0-9]{4,6}$/.test(name)||typeof url!=='string'||typeof tag!=='string'||typeof fetchResponse!=='function'||typeof writeJson!=='function'||typeof writeBytes!=='function'||!Number.isSafeInteger(maxBytes)||maxBytes<1||maxBytes>16*1024*1024)throw Error('Finite injected response capture contract');
 let response,reader,fetchInvoked=false,status=null,receivedHeaders=false,headersComplete=false,headersSaved=false,streamEnded=false,aggregate=null,failureRecordRetained=null,requestFailed=false,primaryFailure=null;
 const headers=[],chunks=[],chunkFiles=[],writeFailures=[];let bytes=0;
 async function save(kind,path,value){try{return await(kind==='json'?writeJson(path,value):writeBytes(path,value));}catch(e){writeFailures.push({stage:path,thrown:info(e)});throw e;}}
 async function attempt(kind,path,value){try{return await save(kind,path,value);}catch{return null;}}
 function metadata(){return{schemaVersion:1,url:url+tag,fetchInvoked,receivedHeaders,status,headers:headers.map(p=>[...p]),headersComplete,publicFetchHeadersNotWireBytes:true,bodyReadState:'not-read-at-header-capture'};}
 function summary(){
  const allChunksSaved=chunkFiles.length===chunks.length,bodyBytesRetained=aggregate!==null||allChunksSaved;
  return{schemaVersion:1,requestFailed,primaryFailure,fetchInvoked,receivedHeaders,headersComplete,headersRecordRetained:headersSaved,status,
   observedBodyBytes:bytes,observedChunks:chunks.length,retainedChunkFiles:chunkFiles.map(r=>({...r})),allObservedChunkFilesRetained:allChunksSaved,
   aggregateBodyFile:aggregate?{...aggregate}:null,allObservedBodyBytesRetained:bodyBytesRetained,
   bodyStreamEnded:streamEnded,availableRawRetained:headersSaved&&bodyBytesRetained&&writeFailures.length===0,
   completeResponseRetained:receivedHeaders&&headersComplete&&streamEnded&&headersSaved&&bodyBytesRetained&&writeFailures.length===0,
   captureWriteFailures:writeFailures.map(v=>({...v,thrown:{...v.thrown}})),failureRecordRetained,
   rawScope:'Received public header values and observed body bytes only; partial is never a complete response or accepted result'};
 }
 try{
  await save('json',name+'-before.json',{schemaVersion:1,url:url+tag,method:'GET',partial:true});
  fetchInvoked=true;response=await fetchResponse();receivedHeaders=true;status=response.status;
  for(const pair of response.headers)headers.push([pair[0],pair[1]]);headersComplete=true;
  await save('json',name+'-headers.json',metadata());headersSaved=true; // BEFORE getReader/read
  reader=response.body?.getReader();if(!reader)throw Error('Public Node response readable body required');
  for(;;){
   const step=await reader.read();if(step.done){streamEnded=true;break;}
   if(!(step.value instanceof Uint8Array))throw Error('Ordinary public Node byte chunk required');
   const snapshot=Buffer.from(step.value);chunks.push(snapshot);bytes+=snapshot.length;
   const row=await save('bytes',name+'-chunks/'+String(chunks.length).padStart(4,'0')+'.bin',snapshot);chunkFiles.push(row);
   if(bytes>maxBytes)throw Error('Observed response exceeds finite accepted body cap; available prefix is retained, never clipped or accepted');
  }
  aggregate=await save('bytes',name+'-body.bin',Buffer.concat(chunks));
  await save('json',name+'-raw.json',{...metadata(),bodyReadState:'ended',bodyBytes:bytes,bodyStreamEnded:true,bodyFile:aggregate,chunkFiles});
  const text=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(chunks)),get=k=>headers.find(p=>p[0].toLowerCase()===k)?.[1]??null;
  return{response:{status,headers:{contentType:get('content-type'),cacheControl:get('cache-control')},requestTag:tag,text,body:null,rawBodyFile:name+'-body.bin'},capture:summary()};
 }catch(error){
  requestFailed=true;failureRecordRetained=false;primaryFailure=info(error);
  // Even reader acquisition, abort/network and capture-write errors retain
  // every observed prefix BEFORE failure semantics/throw. A failed write is
  // explicit and cannot be converted into a full-capture claim.
  if(!headersSaved){const r=await attempt('json',name+'-headers.partial.json',metadata());headersSaved=r!==null;}
  if(aggregate===null)aggregate=await attempt('bytes',name+'-body.partial.bin',Buffer.concat(chunks));
  const retry=!receivedHeaders&&writeFailures.length===0&&readinessRetryAllowed(false,error?.name);
  const receipt={schemaVersion:1,state:'HTTP_RESPONSE_FAILED_UNACCEPTED_V2',response:metadata(),...summary(),thrown:info(error),acceptedResponse:false,readinessRetryAllowed:retry,
   failureReceiptDurability:'Reported by the caller carrier after this write returns; no self-read claim'};
  failureRecordRetained=(await attempt('json',name+'-failure.json',receipt))!==null;
  const failed=new Error('HTTP response failed; see explicit complete/partial/write-failure capture records');failed.readinessRetryAllowed=retry&&writeFailures.length===0;failed.rawCapture=summary();throw failed;
 }finally{
  if(reader&&!streamEnded){try{const pending=reader.cancel();if(pending&&typeof pending.catch==='function')pending.catch(()=>{});}catch{}}
  try{reader?.releaseLock();}catch{}
 }
}
