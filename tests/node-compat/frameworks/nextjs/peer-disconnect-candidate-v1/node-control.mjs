// Authorized host-only reference: real Node22 http/net/ALS/Web streams. No WASI mock.
import assert from 'node:assert/strict';
import http from 'node:http';
import net from 'node:net';
import {Readable} from 'node:stream';
import {AsyncLocalStorage} from 'node:async_hooks';
import {createPeerState,peerMarker,errorData} from './diagnostic-common.mjs';
import {createPeerWebHandler} from './diagnostic-handler.mjs';

// DATA-only capture checks; no resource stand-ins or guest calls.
let getterReads=0;
const accessor=Object.defineProperty({},'payload',{get(){getterReads++;throw new Error('must not run');}});
assert.deepEqual(errorData(undefined),{type:'undefined',isNull:false});
assert.deepEqual(errorData(false),{type:'boolean',isNull:false,value:false});
assert.deepEqual(errorData(NaN),{type:'number',isNull:false,value:'NaN'});
assert.deepEqual(errorData(accessor),{type:'object',isNull:false});assert.equal(getterReads,0);

const events=[],waiters=new Set(),liveSockets=new Set(),completed=new Map();
let server,origin,forcedCleanup=false;
function log(event) {
  events.push(event);console.error(JSON.stringify(event));
  for(const waiter of [...waiters])if(waiter.predicate(event))waiter.resolve(event);
}
function waitFor(predicate) {
  const old=events.find(predicate);if(old)return Promise.resolve(old);
  return new Promise((resolve,reject)=>{
    const waiter={predicate,resolve(value){clearTimeout(timer);waiters.delete(waiter);resolve(value);}};
    const timer=setTimeout(()=>{waiters.delete(waiter);reject(new Error('Milestone deadline'));},10000);
    waiters.add(waiter);
  });
}
const state=createPeerState({AsyncLocalStorage,writeLog:log,origin:'node22-http-reference'});
const web=createPeerWebHandler(state,{setTimeout,clearTimeout});
async function serve(req,res) {
  const record=state.begin(req.headers['x-peer-case'],new URL(req.url,origin).pathname);
  let responseReader,inputReader,inputBytes=0;
  req.on('aborted',()=>state.emit(record,'node-request-aborted',{aborted:req.aborted}));
  req.on('error',error=>state.emit(record,'node-request-error',{error:errorData(error)}));
  req.on('close',()=>state.emit(record,'node-request-close',{complete:req.complete,destroyed:req.destroyed}));
  res.on('error',error=>state.emit(record,'node-response-error',{error:errorData(error)}));
  res.on('close',()=>state.emit(record,'node-response-close',{writableFinished:res.writableFinished,destroyed:res.destroyed}));
  try {
    let body;
    if(!['GET','HEAD'].includes(req.method)) {
      inputReader=Readable.toWeb(req).getReader();
      body=new ReadableStream({async pull(controller){
        state.emit(record,'node-input-read-invocation-attempt',{inputBytes,hostReadEnteredOrBlockedProved:false});
        try {
          const part=await inputReader.read();
          inputBytes+=part.done?0:part.value.byteLength;
          state.emit(record,'node-input-read-returned',{done:part.done,bytes:part.done?0:part.value.byteLength,inputBytes});
          if(part.done)controller.close();else controller.enqueue(part.value);
        } catch(error){state.emit(record,'node-input-read-failed',{error:errorData(error)});controller.error(error);}
      },async cancel(reason){
        state.emit(record,'node-input-cancel-invocation-attempt',{reason:errorData(reason)});
        try{await inputReader.cancel(reason);state.emit(record,'node-input-cancel-returned');}
        catch(error){state.emit(record,'node-input-cancel-failed',{error:errorData(error)});throw error;}
      }});
    }
    // Intentionally matches the guest baseline's absent peer->Request.signal link.
    const request=new Request(origin+req.url,{method:req.method,headers:req.headers,
      ...(body?{body,duplex:'half'}:{})});
    const response=await web(request,record);
    res.writeHead(response.status,Object.fromEntries(response.headers));
    if(response.body) {
      responseReader=response.body.getReader();
      for(;;) {
        const part=await responseReader.read();if(part.done)break;
        for(let offset=0;offset<part.value.byteLength;offset+=4096) {
          const bytes=part.value.subarray(offset,offset+4096);
          state.emit(record,'node-output-write-invocation-attempt',{bytes:bytes.byteLength});
          try {
            await new Promise((resolve,reject)=>res.write(bytes,error=>error?reject(error):resolve()));
            state.emit(record,'node-output-write-callback-returned',{peerReceiptProved:false});
          } catch(error){state.emit(record,'node-output-write-failed',{error:errorData(error)});throw error;}
        }
      }
    }
    await new Promise((resolve,reject)=>res.end(error=>error?reject(error):resolve()));
    state.emit(record,'node-response-end-callback-returned',{peerReceiptProved:false});
  } catch(error) {
    state.emit(record,'node-adapter-failed',{error:errorData(error)});
    if(responseReader) {
      state.emit(record,'node-response-reader-cancel-invocation-attempt');
      try{await responseReader.cancel(error);state.emit(record,'node-response-reader-cancel-returned');}
      catch(secondary){state.emit(record,'node-response-reader-cancel-failed-suppressed',{error:errorData(secondary)});}
    }
    if(!res.destroyed)res.destroy();
  } finally {
    if(inputReader) {
      try{inputReader.releaseLock();state.emit(record,'node-input-reader-lock-released');}
      catch(error){state.emit(record,'node-input-reader-release-failed',{error:errorData(error)});}
    }
    if(responseReader)responseReader.releaseLock();
    state.emit(record,'node-adapter-finally-returned');completed.set(record.label,true);
  }
}
function decode(raw,partial=false) {
  const at=raw.indexOf('\r\n\r\n');if(at<0){if(partial)return null;throw new Error('Missing response headers');}
  const headers=raw.subarray(0,at).toString('latin1'),status=Number(headers.split(' ')[1]);
  const encoded=raw.subarray(at+4),chunks=[];
  if(/\r\ntransfer-encoding:\s*chunked/i.test(headers)) {
    let offset=0;
    for(;;) {
      const end=encoded.indexOf('\r\n',offset);if(end<0){if(partial)break;throw new Error('Missing chunk header');}
      const length=Number.parseInt(encoded.subarray(offset,end).toString('ascii').split(';')[0],16);
      if(!Number.isFinite(length))throw new Error('Invalid chunk length');
      offset=end+2;if(!length)break;
      if(offset+length+2>encoded.length){if(partial)break;throw new Error('Incomplete chunk');}
      chunks.push(encoded.subarray(offset,offset+length));offset+=length+2;
    }
  } else chunks.push(encoded);
  return {status,headers,body:Buffer.concat(chunks)};
}
async function request(label,path,{body,partialUpload=false,closeAfterFirst=false}={}) {
  const socket=net.createConnection({host:'127.0.0.1',port:server.address().port});
  liveSockets.add(socket);const received=[],socketEvents=[];let closeRequested=false,deadline;
  const closed=new Promise((resolve,reject)=>{
    deadline=setTimeout(()=>{forcedCleanup=true;socket.destroy();reject(new Error('Client deadline'));},15000);
    socket.on('data',part=>{
      received.push(Buffer.from(part));
      if(Buffer.concat(received).length>131072){forcedCleanup=true;socket.destroy();reject(new Error('Client byte cap'));return;}
      const frame=decode(Buffer.concat(received),true);
      if(closeAfterFirst&&!closeRequested&&frame?.body.byteLength) {
        closeRequested=true;socketEvents.push({phase:'actual-first-response-body-bytes',bytes:frame.body.byteLength});
        // Ordinary close API; never resetAndDestroy, malformed handles or injected errors.
        socketEvents.push({phase:'client-destroySoon-invocation-attempt'});socket.destroySoon();
      }
    });
    socket.on('end',()=>socketEvents.push({phase:'client-end'}));
    socket.on('error',error=>socketEvents.push({phase:'client-error',error:errorData(error)}));
    socket.on('close',hadError=>{clearTimeout(deadline);liveSockets.delete(socket);socketEvents.push({phase:'client-close',hadError});resolve();});
  });
  await new Promise((resolve,reject)=>{socket.once('connect',resolve);socket.once('error',reject);});
  const method=body?'POST':'GET';
  socket.write(`${method} ${path} HTTP/1.1\r\nHost: ${server.address().address}:${server.address().port}\r\nX-Peer-Case: ${label}\r\nConnection: close\r\n${body?'Content-Length: 8192\r\n':''}\r\n`);
  if(body)socket.write(body);
  let synchronizedMilestone;
  if(partialUpload) {
    synchronizedMilestone=await waitFor(e=>e.label===label&&e.phase==='node-input-read-invocation-attempt'&&e.inputBytes>=body.length);
    socketEvents.push({phase:'prefix-return-followed-by-read-invocation-attempt',sequence:synchronizedMilestone.sequence,
      hostReadEnteredOrBlockedProved:false});
    socketEvents.push({phase:'client-end-invocation-attempt'});socket.end();
  }
  await closed;
  await waitFor(e=>e.label===label&&e.phase==='node-adapter-finally-returned');
  const raw=Buffer.concat(received),frame=raw.length?decode(raw,closeAfterFirst):null;
  return {label,path,rawBytes:raw.length,rawBase64:raw.toString('base64'),socketEvents,
    ...(frame?{status:frame.status,headers:frame.headers,decodedBodyBase64:frame.body.toString('base64'),decodedBodyBytes:frame.body.length}:{}),
    synchronizedMilestone:synchronizedMilestone??null,firstBodyBeforeClose:closeAfterFirst?closeRequested:null};
}
const result={schemaVersion:1,marker:peerMarker,hostReferenceCollectionPassed:false,
  nodeVersion:process.version,guestOrEngineOrCompilerExecuted:false,networkScope:'fresh-owned-127.0.0.1-only',
  pureCaptureChecks:5,
  wasiGuestPeerDisconnectCoverage:false,nodeWasiTcpParityClaimed:false,requestSignalLinkedToPeer:false,
  normalTcpApiNotPacketLevelFinOrRstAttestation:true,cases:[],forcedCleanup:false};
let primary,hasPrimary=false;
try {
  server=http.createServer((req,res)=>{serve(req,res).catch(error=>{console.error(JSON.stringify({uncaughtHandler:errorData(error)}));res.destroy();});});
  server.on('connection',socket=>{liveSockets.add(socket);socket.once('close',()=>liveSockets.delete(socket));});
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen({host:'127.0.0.1',port:0,exclusive:true},resolve);});
  origin=`http://127.0.0.1:${server.address().port}`;result.origin=origin;
  const upload=await request('healthy-upload','/upload',{body:Buffer.alloc(8192,80)});result.cases.push(upload);
  assert.equal(upload.status,200);assert.equal(JSON.parse(Buffer.from(upload.decodedBodyBase64,'base64')).complete,true);
  const output=await request('healthy-output','/output');result.cases.push(output);
  assert.equal(output.status,200);assert.equal(output.decodedBodyBytes,32768);
  const bytes=Buffer.from(output.decodedBodyBase64,'base64');for(let i=0;i<8;i++)assert(bytes.subarray(i*4096,(i+1)*4096).every(x=>x===65+i));
  result.cases.push(await request('partial-upload','/upload',{body:Buffer.alloc(1024,80),partialUpload:true}));
  result.cases.push(await request('inspect-after-upload','/inspect'));
  result.cases.push(await request('output-close','/output',{closeAfterFirst:true}));
  result.cases.push(await request('inspect-after-output','/inspect'));
  const uploadEvents=events.filter(e=>e.label==='partial-upload'),outputEvents=events.filter(e=>e.label==='output-close');
  const uploadFailure=uploadEvents.find(e=>e.phase==='node-input-read-failed');
  assert(uploadFailure);assert(uploadEvents.some(e=>e.phase==='handler-read-failed'));
  assert(uploadEvents.some(e=>e.phase==='handler-body-finally'&&e.received===1024&&e.signalAborted===false));
  const outputFailure=outputEvents.find(e=>e.phase==='node-output-write-failed');
  result.outputCancellationCoverage=outputFailure?'observed-node-write-failure-and-cancel':'inconclusive-no-later-write-failure';
  if(outputFailure) {
    assert(outputEvents.some(e=>e.phase==='producer-cancel-returned'));
    assert(outputEvents.some(e=>e.phase==='node-response-reader-cancel-returned'));
  }
  for(const label of ['inspect-after-upload','inspect-after-output']) {
    const record=result.cases.find(c=>c.label===label);assert.equal(record.status,200);
    const inspection=JSON.parse(Buffer.from(record.decodedBodyBase64,'base64')).inspection;
    assert.equal(inspection.firstLabel,'healthy-upload');
    assert(inspection.requests.some(r=>r.label===(label==='inspect-after-upload'?'partial-upload':'output-close')));
  }
  result.uploadCoverage='actual-node-partial-body-read-failure-and-finally';
  result.nodeWriteFailureObserved=Boolean(outputFailure);result.nodeEvents=events;
  result.hostReferenceCollectionPassed=Boolean(outputFailure);
} catch(error){hasPrimary=true;primary=error;result.primaryError=errorData(error);}
finally {
  if(hasPrimary&&liveSockets.size){forcedCleanup=true;for(const socket of liveSockets)socket.destroy();}
  if(server)await new Promise(resolve=>server.close(resolve));
  result.forcedCleanup=forcedCleanup;result.remainingSockets=liveSockets.size;result.waiters=waiters.size;
  if(liveSockets.size||waiters.size||forcedCleanup){result.hostReferenceCollectionPassed=false;if(!hasPrimary){hasPrimary=true;primary=new Error('Host cleanup incomplete');}}
  console.log(JSON.stringify(result));
}
if(hasPrimary)throw primary;
if(!result.hostReferenceCollectionPassed)process.exitCode=1;
