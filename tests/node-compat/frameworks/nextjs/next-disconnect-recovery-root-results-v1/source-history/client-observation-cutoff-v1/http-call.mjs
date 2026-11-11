// Inert real Node HTTP collector. Importing creates no request, timer or file.
import assert from 'node:assert/strict';
import http from 'node:http';
import {createHash} from 'node:crypto';
import {open,readFile,lstat,realpath} from 'node:fs/promises';

export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export const errorData=error=>({name:error?.name??null,code:error?.code??null,message:error?.message??String(error),stack:error?.stack??null});
export async function publish(path,bytes){
 assert(Buffer.isBuffer(bytes));let handle,failed=false,primary;
 const evidence={complete:false,fsynced:false,closed:false,fileBytes:null,sha256:null,errors:[]};
 try{handle=await open(path,'wx',0o600);await handle.writeFile(bytes);await handle.sync();evidence.fsynced=true;}
 catch(error){failed=true;primary=error;evidence.errors.push({stage:'write-or-sync',...errorData(error)});}
 finally{if(handle)try{await handle.close();evidence.closed=true;}catch(error){evidence.errors.push({stage:'close',...errorData(error)});if(!failed){failed=true;primary=error;}}}
 if(failed)throw primary;
 const before=await lstat(path);assert(before.isFile()&&!before.isSymbolicLink()&&before.nlink===1);assert.equal(await realpath(path),path);
 const actual=await readFile(path),after=await lstat(path);
 for(const key of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(before[key],after[key]);
 assert(actual.equals(bytes));evidence.fileBytes=bytes.length;evidence.sha256=hash(bytes);evidence.complete=true;
 return{ref:{path,sha256:evidence.sha256,bytes:bytes.length},evidence};
}

export async function collectCall({origin,spec,bodyPath,httpTimeoutMs=20000,cleanupTimeoutMs=2000,bodyLimitBytes=4194304,chunkLimit=65536,metadataLimitBytes=262144}){
 const url=new URL(origin);assert.equal(url.origin,origin);assert.equal(url.protocol,'http:');assert.equal(url.hostname,'127.0.0.1');assert(url.port);
 for(const value of [httpTimeoutMs,cleanupTimeoutMs,bodyLimitBytes,chunkLimit,metadataLimitBytes])assert(Number.isSafeInteger(value)&&value>0);
 assert(httpTimeoutMs<=20000&&cleanupTimeoutMs<=2000&&bodyLimitBytes<=4194304&&chunkLimit<=65536&&metadataLimitBytes<=262144);
 const started=process.hrtime.bigint(),now=()=>(process.hrtime.bigint()-started).toString();let sequence=0,metadataBytes=0;
 const requestBody=spec.body===undefined?null:Buffer.from(spec.body,'utf8');
 const headers={'accept':'*/*','accept-encoding':'identity','connection':'close',...(spec.headers??{})};
 if(requestBody!==null)headers['content-length']=String(requestBody.length);
 const result={schemaVersion:1,id:spec.id,method:spec.method,path:spec.path,startedNs:'0',terminalNs:null,events:[],
  request:{attempted:false,created:false,url:origin+spec.path,headers,bodyBytes:requestBody?.length??0,bodySha256:requestBody===null?null:hash(requestBody),finishObserved:false,closeObserved:false,errors:[]},
  response:{received:false,statusCode:null,statusMessage:null,httpVersion:null,headers:null,rawHeaders:[],trailers:null,rawTrailers:[],complete:false,readableEnded:false,endObserved:false,abortedObserved:false,closeObserved:false,errors:[]},
  connection:{socketAssigned:false,socketEndObserved:false,socketCloseObserved:false,socketCloseHadError:null,errors:[],cleanupRequested:false,cleanupCompleted:false},
  capture:{observedBytes:0,retainedBytes:0,chunks:[],overflow:false,unretainedBytesUnknown:false,allObservedBytesRetained:false,meaning:'IncomingMessage entity data after HTTP transfer framing; no content decoder, wire or guest-read claim'},
  intentionalDisconnect:{configured:spec.intentionalDisconnect===true,triggered:false,intentSequence:null,firstChunkBytes:null,completeAtIntent:null,readableEndedAtIntent:null,endObservedAtIntent:null,localDestroyInvoked:false,guestCancellationObserved:false,guestPropagation:'inconclusive; no guest acknowledgment or resource-retirement observation'},
  deadline:{limitMs:httpTimeoutMs,exceeded:false},
  body:null,bodyPublication:null,collectionErrors:[],httpComplete:false,collectionComplete:false};
 const chunks=[];let request,response,socket,httpTimer,cleanupTimer,closing=false,settled=false;
 const uncertain=(stage,error)=>{if(result.collectionErrors.length<16)result.collectionErrors.push({stage,...errorData(error)});else result.capture.unretainedBytesUnknown=true;};
 const event=(kind,details={})=>{const row={sequence:++sequence,ns:now(),kind,...details};if(result.events.length<128)result.events.push(row);else uncertain('event-limit',new RangeError('Call event bound'));return row;};
 const recordError=(target,error,kind)=>{const row={...event(kind),...errorData(error)};if(target.length<16)target.push(row);else uncertain('error-limit',new RangeError('Call error bound'));};
 const snapshot=()=>{if(response){result.response.complete=response.complete===true;result.response.readableEnded=response.readableEnded===true;result.response.trailers=response.trailers;result.response.rawTrailers=[...(response.rawTrailers??[])];}};
 await new Promise(resolve=>{
  const finishIfClosed=()=>{
   if(!closing||settled||(request&&!result.request.closeObserved)||(socket&&!result.connection.socketCloseObserved)||(response&&!result.response.closeObserved))return;
   settled=true;clearTimeout(httpTimer);clearTimeout(cleanupTimer);snapshot();result.connection.cleanupCompleted=true;result.terminalNs=now();resolve();
  };
  const cleanup=reason=>{
   if(closing)return;closing=true;result.terminalReason=reason;clearTimeout(httpTimer);snapshot();result.connection.cleanupRequested=true;event('cleanup-requested',{reason});
   cleanupTimer=setTimeout(()=>{if(settled)return;settled=true;snapshot();uncertain('cleanup-timeout',new Error('Request/response/socket close not observed within bounded cleanup'));result.terminalNs=now();resolve();},cleanupTimeoutMs);
   try{request?.destroy();socket?.destroy();}catch(error){uncertain('destroy',error);}finishIfClosed();
  };
  try{
   result.request.attempted=true;event('request-attempt');
   httpTimer=setTimeout(()=>{result.deadline.exceeded=true;event('absolute-request-deadline',{limitMs:httpTimeoutMs});cleanup('http-timeout');},httpTimeoutMs);
   request=http.request(new URL(spec.path,origin),{method:spec.method,headers,agent:false,maxHeaderSize:65536},incoming=>{
    response=incoming;result.response.received=true;result.response.statusCode=incoming.statusCode??null;result.response.statusMessage=incoming.statusMessage??null;
    result.response.httpVersion=incoming.httpVersion;result.response.headers=incoming.headers;result.response.rawHeaders=[...incoming.rawHeaders];event('response');
    incoming.on('data',chunk=>{
     try{
      if(!Buffer.isBuffer(chunk)){result.capture.unretainedBytesUnknown=true;throw new TypeError('Uncoerced Buffer body event required');}
      const capture=result.capture;capture.observedBytes+=chunk.length;
      if(capture.overflow||capture.unretainedBytesUnknown)return; // Stop retaining a rejected tail.
      if(result.response.endObserved){capture.unretainedBytesUnknown=true;uncertain('body-after-end',new Error('Data after response end'));cleanup('body-after-end');return;}
      const entry={sequence:++sequence,ns:now(),offset:capture.retainedBytes,bytes:chunk.length,sha256:hash(chunk)};
      const meta=Buffer.byteLength(JSON.stringify(entry));
      if(capture.chunks.length>=chunkLimit||metadataBytes+meta>metadataLimitBytes||capture.retainedBytes+chunk.length>bodyLimitBytes){capture.overflow=true;uncertain('body-or-metadata-limit',new RangeError('Body/chunk/metadata limit; no accepted tail'));cleanup('body-limit');return;}
      chunks.push(Buffer.from(chunk));capture.chunks.push(entry);capture.retainedBytes+=chunk.length;metadataBytes+=meta;
      if(spec.intentionalDisconnect===true&&chunk.length>0&&!result.intentionalDisconnect.triggered){
       const intent=result.intentionalDisconnect;intent.triggered=true;intent.firstChunkBytes=chunk.length;intent.completeAtIntent=incoming.complete===true;intent.readableEndedAtIntent=incoming.readableEnded===true;intent.endObservedAtIntent=result.response.endObserved;
       intent.intentSequence=event('intentional-close-after-first-actual-body-buffer',{bytes:chunk.length}).sequence;intent.localDestroyInvoked=true;cleanup('intentional-first-body-close');
      }
     }catch(error){result.capture.unretainedBytesUnknown=true;uncertain('body-collector',error);cleanup('body-collector-error');}
    });
    incoming.on('aborted',()=>{result.response.abortedObserved=true;event('response-aborted');snapshot();cleanup('response-aborted');});
    incoming.on('error',error=>{recordError(result.response.errors,error,'response-error');snapshot();cleanup('response-error');});
    incoming.on('end',()=>{result.response.endObserved=true;event('response-end');snapshot();cleanup('response-end');});
    incoming.on('close',()=>{result.response.closeObserved=true;event('response-close');snapshot();if(!closing)cleanup('response-close-without-end');finishIfClosed();});
    if(incoming.rawHeaders.length>=256){uncertain('header-count',new RangeError('Response headers reached collection bound'));cleanup('header-limit');}
   });
   result.request.created=true;request.maxHeadersCount=128;
   request.on('socket',owned=>{socket=owned;result.connection.socketAssigned=true;event('socket-assigned');
    owned.on('end',()=>{result.connection.socketEndObserved=true;event('socket-end');});
    owned.on('error',error=>{recordError(result.connection.errors,error,'socket-error');cleanup('socket-error');});
    owned.on('close',hadError=>{result.connection.socketCloseObserved=true;result.connection.socketCloseHadError=hadError;event('socket-close',{hadError});finishIfClosed();});
    if(closing)owned.destroy();});
   request.on('finish',()=>{result.request.finishObserved=true;event('request-finish');});
   request.on('error',error=>{recordError(result.request.errors,error,'request-error');if(error?.code==='HPE_HEADER_OVERFLOW')uncertain('header-byte-limit',error);cleanup('request-error');});
   request.on('close',()=>{result.request.closeObserved=true;event('request-close');if(!closing)cleanup('request-close');finishIfClosed();});
   request.on('information',()=>{uncertain('interim-response',new Error('Interim response outside fixed fixture protocol'));cleanup('unexpected-information');});
   request.on('upgrade',(_response,owned)=>{result.capture.unretainedBytesUnknown=true;uncertain('upgrade',new Error('Upgrade outside one-response protocol'));owned.destroy();cleanup('unexpected-upgrade');});
   request.end(requestBody??undefined);
  }catch(error){recordError(result.request.errors,error,'request-synchronous-error');uncertain('request-construction-or-write',error);cleanup('request-synchronous-error');}
 });
 snapshot();const body=Buffer.concat(chunks,result.capture.retainedBytes);
 result.capture.allObservedBytesRetained=!result.capture.overflow&&!result.capture.unretainedBytesUnknown&&result.capture.observedBytes===body.length;
 try{const stored=await publish(bodyPath,body);result.body=stored.ref;result.bodyPublication=stored.evidence;result.bodyPublication.complete=result.capture.allObservedBytesRetained;}
 catch(error){uncertain('body-publication',error);}
 const cl=result.response.headers?.['content-length'];let contentLengthValid=true;
 result.response.declaredContentLength=cl??null;result.response.contentLengthMatches=null;
 if(cl!==undefined){contentLengthValid=typeof cl==='string'&&/^(0|[1-9][0-9]*)$/.test(cl)&&Number.isSafeInteger(Number(cl));result.response.contentLengthMatches=contentLengthValid&&Number(cl)===body.length;}
 result.httpComplete=!result.deadline.exceeded&&result.request.finishObserved&&result.connection.socketCloseHadError===false&&result.response.received&&result.response.complete&&result.response.readableEnded&&result.response.endObserved&&!result.response.abortedObserved
  &&result.response.errors.length===0&&result.request.errors.length===0&&result.connection.errors.length===0&&contentLengthValid&&(cl===undefined||result.response.contentLengthMatches===true);
 result.collectionComplete=result.request.created&&result.request.closeObserved&&result.connection.socketAssigned&&result.connection.socketCloseObserved&&result.connection.cleanupCompleted
  &&(!result.response.received||result.response.closeObserved)&&result.capture.allObservedBytesRetained&&result.bodyPublication?.complete===true&&result.collectionErrors.length===0;
 return result;
}
