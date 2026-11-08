// One host Node HTTP request. Importing this module allocates no Agent/socket/timer.
import assert from 'node:assert/strict';
import {Agent,request} from 'node:http';
import {MAX_WIRE,MAX_ENCODED} from './wire-model.mjs';
const defaults={request,makeAgent:()=>new Agent({keepAlive:true,maxSockets:1,maxFreeSockets:1}),
  now:()=>process.hrtime.bigint(),setTimer:(fn,ms)=>setTimeout(fn,ms),clearTimer:clearTimeout,
  afterData:()=>new Promise(resolve=>setImmediate(resolve))};
export function errorData(error) {
  const string=value=>{try{return String(value);}catch{return '<unstringifiable>';}};
  return {thrownType:typeof error,name:typeof error?.name==='string'?error.name:null,
    message:typeof error?.message==='string'?error.message:string(error),
    code:typeof error?.code==='string'||typeof error?.code==='number'?error.code:null,
    stack:typeof error?.stack==='string'?error.stack:null};
}
export async function captureOne(origin,record,limits,services=defaults) {
  assert.equal(new URL(origin).origin,origin);assert.equal(new URL(origin).hostname,'127.0.0.1');
  assert.equal(new URL(origin).protocol,'http:');assert.equal(record.path,'/actions');assert.equal(record.method,'POST');
  assert.equal(limits.timeoutMs,20000);assert.equal(limits.maximumWireBytes,MAX_WIRE);assert.equal(limits.maximumEncodedBytes,MAX_ENCODED);
  const body=Buffer.from(record.bodyBase64,'base64');assert.equal(body.length,391);
  const headers={...record.headers,host:new URL(origin).host,origin,referer:origin+'/actions',
    'accept-encoding':'gzip',connection:'keep-alive','content-length':String(body.length)};
  const started=services.now(),wire=[],encoded=[];let agent,req,socket,response,timer,settling=false,settled=false;
  let receivedWire=0,receivedEncoded=0,retainedWire=0,retainedEncoded=0,cleanupRequested=false,socketClosed=false;
  const observation={schemaVersion:1,scope:'single-new-http-client-message-not-browser-or-RSC-parser',origin,
    request:{method:'POST',path:'/actions',headers,bodyBytes:body.length,bodyBase64:record.bodyBase64},
    status:null,rawHeaders:[],responseComplete:false,httpMessageEndObserved:false,peerSocketEndObserved:false,
    rawFinalizedAfterDataListeners:false,events:[],droppedEvents:0,errors:[],omittedErrors:0,
    timingUnit:'same-host-client relative monotonic nanoseconds',timeoutMs:20000,timeout:false,
    rawSocketPrefixTruncated:false,encodedBodyPrefixTruncated:false,clientCleanup:null};
  const at=()=>String(services.now()-started);
  const mark=(event,details={})=>{if(observation.events.length<1024)observation.events.push({event,ns:at(),...details});else observation.droppedEvents++;};
  const fail=(stage,error)=>{if(observation.errors.length<32)observation.errors.push({stage,...errorData(error)});else observation.omittedErrors++;};
  let resolveDone;const done=new Promise(resolve=>{resolveDone=resolve;});
  const finish=()=>{
    if(settling||settled)return;settling=true;
    // The raw observer is prepended, but also leave the current data event's
    // remaining listeners before publication and before any Agent destruction.
    Promise.resolve().then(()=>services.afterData()).then(()=>{
      if(socket)socket.removeListener('data',wireData);
      observation.rawFinalizedAfterDataListeners=true;mark('raw-capture-finalized-after-data-listeners');
      services.clearTimer(timer);settled=true;resolveDone();
    },error=>{fail('after-data-finalization',error);services.clearTimer(timer);settled=true;resolveDone();});
  };
  const stop=(stage,message)=>{const error=Object.assign(new Error(message),{code:'ERR_ACTION_WIRE_BOUND'});fail(stage,error);req?.destroy(error);finish();};
  function wireData(part) {
    mark('raw-socket-data',{bytes:part.length});receivedWire+=part.length;
    const count=Math.min(part.length,MAX_WIRE-retainedWire);if(count>0){wire.push(Buffer.from(part.subarray(0,count)));retainedWire+=count;}
    if(receivedWire>MAX_WIRE){observation.rawSocketPrefixTruncated=true;stop('wire-cap','Raw socket prefix exceeded2MiB');}
  }
  try {
    timer=services.setTimer(()=>{observation.timeout=true;stop('http-deadline','Whole HTTP request exceeded20000ms');},20000);
    agent=services.makeAgent();mark('private-agent-created');
    req=services.request(new URL('/actions',origin),{method:'POST',headers,agent,maxHeaderSize:16384},actual=>{
      response=actual;observation.status=actual.statusCode;observation.rawHeaders=[...actual.rawHeaders];mark('response-headers');
      actual.on('data',part=>{
        mark('node-http-encoded-data',{bytes:part.length});receivedEncoded+=part.length;
        const count=Math.min(part.length,MAX_ENCODED-retainedEncoded);if(count>0){encoded.push(Buffer.from(part.subarray(0,count)));retainedEncoded+=count;}
        if(receivedEncoded>MAX_ENCODED){observation.encodedBodyPrefixTruncated=true;stop('encoded-cap','Node HTTP encoded prefix exceeded2MiB');}
      });
      actual.on('end',()=>{observation.httpMessageEndObserved=true;observation.responseComplete=actual.complete===true;mark('http-message-end',{complete:observation.responseComplete});if(!actual.complete)fail('incomplete-http-end',new Error('IncomingMessage.complete false'));finish();});
      actual.on('aborted',()=>{fail('response-aborted',new Error('IncomingMessage aborted'));mark('response-aborted');finish();});
      actual.on('error',error=>{fail('response-error',error);mark('response-error');finish();});
      actual.on('close',()=>{mark('response-close',{complete:actual.complete===true});if(!observation.httpMessageEndObserved){fail('response-close-before-end',new Error('Response closed before HTTP end'));finish();}});
    });
    req.on('socket',actual=>{
      socket=actual;mark('socket-assigned');actual.prependListener('data',wireData);
      actual.on('end',()=>{mark('socket-end',{clientCleanupRequested:cleanupRequested});if(!cleanupRequested)observation.peerSocketEndObserved=true;});
      actual.on('error',error=>{fail('socket-error',error);mark('socket-error',{clientCleanupRequested:cleanupRequested});if(!settled)finish();});
      actual.on('close',hadError=>{socketClosed=true;mark('socket-close',{hadError,clientCleanupRequested:cleanupRequested});if(!observation.httpMessageEndObserved&&!settled){fail('socket-close-before-http-end',new Error('Socket closed before HTTP end'));finish();}});
    });
    req.on('error',error=>{fail('request-error',error);mark('request-error');finish();});
    req.on('close',()=>mark('request-close'));
    mark('request-end-called');req.end(body);
  } catch(error){fail('request-setup',error);finish();}
  await done;
  observation.receivedWireBytes=receivedWire;observation.receivedEncodedBytes=receivedEncoded;
  observation.retainedWireBytes=retainedWire;observation.retainedEncodedBytes=retainedEncoded;
  observation.captureTerminalNs=at();
  return {observation,wire:Buffer.concat(wire,retainedWire),encoded:Buffer.concat(encoded,retainedEncoded),
    async cleanup({prefixesDurable,validationFinished}) {
      cleanupRequested=true;mark('client-owned-agent-destroy-requested');
      const cleanup={prefixesDurableBeforeCleanup:prefixesDurable===true,validationFinishedBeforeCleanup:validationFinished===true,
        httpMessageEndBeforeCleanup:observation.httpMessageEndObserved,socketClosedBeforeClientCleanup:socketClosed,
        clientInitiatedSocketCloseRequested:Boolean(socket&&!socketClosed),
        agentDestroyCalled:false,socketCloseObserved:socketClosed,noAgentAllocated:agent===undefined,errors:[]};
      observation.clientCleanup=cleanup;
      try {
        if(agent){cleanup.agentDestroyCalled=true;agent.destroy();}
        if(socket&&!socketClosed)await new Promise(resolve=>{
          let handle;const close=()=>{services.clearTimer(handle);resolve();};socket.once('close',close);
          handle=services.setTimer(()=>{socket.removeListener('close',close);cleanup.errors.push({stage:'agent-close-bound',message:'Private socket not closed within1000ms'});resolve();},1000);
        });
      } catch(error){cleanup.errors.push({stage:'agent-destroy',...errorData(error)});}
      cleanup.socketCloseObserved=socketClosed;
      if(socket)socket.removeListener('data',wireData);
      mark('client-owned-agent-cleanup-finished');return cleanup;
    }};
}
