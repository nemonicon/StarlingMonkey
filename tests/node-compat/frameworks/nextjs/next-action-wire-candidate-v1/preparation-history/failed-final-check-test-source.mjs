// Ordinary host DATA/controller fixtures only. No socket/Agent/request/guest/app.
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {gzipSync,crc32 as nodeCrc32} from 'node:zlib';
import {readFile} from 'node:fs/promises';
import {captureOne} from './capture-core.mjs';
import {parseHttpMessage,decodeSingleGzip,crc32,MAX_WIRE,MAX_ENCODED,MAX_DECODED} from './wire-model.mjs';
import {parseHttpMessage as presealParser} from './preparation-history/strict-parser-before.mjs';
let checks=0;const ok=(value,message)=>{assert(value,message);checks++;};
const refuses=(fn,message)=>{let thrown=false;try{fn();}catch{thrown=true;}ok(thrown,message);};
const input=Buffer.from('opaque synthetic UTF8 € 😀 bytes\n'),gzip=gzipSync(input,{mtime:0});
const head='HTTP/1.1 200 OK\r\nContent-Type: text/x-component\r\nContent-Encoding: gzip\r\nTransfer-Encoding: chunked\r\n\r\n';
const chunked=bytes=>Buffer.concat([Buffer.from(head+bytes.length.toString(16)+'\r\n'),bytes,Buffer.from('\r\n0\r\n\r\n')]);
const wire=chunked(gzip),parsed=parseHttpMessage(wire);
for(const malformed of [Buffer.from(wire.toString('latin1').replace('200 OK','200\n'),'latin1'),
 Buffer.from(wire.toString('latin1').replace('Content-Type:','x\n: value\r\nContent-Type:'),'latin1'),
 Buffer.from(wire.toString('latin1').replace('text/x-component','text/x-component\n'),'latin1'),
 Buffer.from(wire.toString('latin1').replace(gzip.length.toString(16)+'\r\n',gzip.length.toString(16)+'\n\r\n'),'latin1'),
 Buffer.from(wire.toString('latin1').replace('text/x-component','text/x-componentgarbage'),'latin1')]){
  ok(presealParser(malformed).body.equals(gzip),'Genuine stopped preseal parser accepted identified edge');
  refuses(()=>parseHttpMessage(malformed),'Current parser refuses identified edge');
}
ok(parsed.body.equals(gzip)&&parsed.httpMessageEofValidated&&parsed.framing==='chunked','Independent chunk framing');
ok(decodeSingleGzip(parsed.body).decoded.equals(input),'Single member whole opaque bytes');
ok(crc32(input)===nodeCrc32(input)&&crc32(Buffer.from('123456789'))===0xcbf43926,'Independent CRC32 vs pinned host and known vector');
const lengthWire=Buffer.concat([Buffer.from(head.replace('Transfer-Encoding: chunked','Content-Length: '+gzip.length)),gzip]);
ok(parseHttpMessage(lengthWire).body.equals(gzip),'Exact content length profile');
const closeWire=Buffer.concat([Buffer.from(head.replace('Transfer-Encoding: chunked\r\n','')),gzip]);
refuses(()=>parseHttpMessage(closeWire),'Client socket destruction cannot prove close framing');
ok(parseHttpMessage(closeWire,{peerSocketEndObserved:true}).body.equals(gzip),'Actual peer EOF explicit profile');
for(const value of [wire.subarray(0,wire.length-1),Buffer.concat([wire,Buffer.from('x')]),Buffer.from(head+'0\r\n'),
 Buffer.from(head.replace('200 OK','200 bad\x00reason')+'0\r\n\r\n'),
 Buffer.from(head+'1\r\nx\n0\r\n\r\n'),Buffer.from(head.replace('Transfer-Encoding: chunked','Transfer-Encoding: chunked\r\nContent-Length: 0')+'0\r\n\r\n'),
 Buffer.from(head.replace('Content-Encoding: gzip','Content-Encoding: gzip\r\nContent-Encoding: gzip')+'0\r\n\r\n'),
 Buffer.from(head.replace('200 OK','100 Continue')+'0\r\n\r\n'),Buffer.from(head+'0;extension=yes\r\n\r\n'),
 Buffer.from(head+'ffffffffffffffffffffffffffff\r\n'),Buffer.alloc(MAX_WIRE+1)])refuses(()=>parseHttpMessage(value),'Framing ambiguity/truncation/cap unsupported');
for(const size of [0,1,9,10,gzip.length-9,gzip.length-1])refuses(()=>decodeSingleGzip(gzip.subarray(0,size)),'Truncated gzip refused');
for(const value of [Buffer.concat([gzip,gzip]),Buffer.concat([gzip,Buffer.from([0])])])refuses(()=>decodeSingleGzip(value),'Multi-member/trailing padding refused');
for(const index of [gzip.length-8,gzip.length-4]){const bad=Buffer.from(gzip);bad[index]^=1;let error;try{decodeSingleGzip(bad);}catch(e){error=e;}ok(error?.decodedPrefix?.equals(input),'CRC/ISIZE failure retains real unvalidated decoded bytes');}
refuses(()=>decodeSingleGzip(gzipSync(Buffer.alloc(1024)),64),'Bounded decoded output');
const extra=Buffer.from([2,0,0x51,0x52]),name=Buffer.from('name\0comment\0'),base=Buffer.from(gzip.subarray(0,10));base[3]=4|8|16|2;
const header=Buffer.concat([base,extra,name]),hcrc=Buffer.alloc(2);hcrc.writeUInt16LE(crc32(header)&0xffff);
ok(decodeSingleGzip(Buffer.concat([header,hcrc,gzip.subarray(10)])).decoded.equals(input),'Optional header fields and header CRC');
hcrc[0]^=1;refuses(()=>decodeSingleGzip(Buffer.concat([header,hcrc,gzip.subarray(10)])),'Bad header CRC');
const record=JSON.parse(await readFile(new URL('./request.json',import.meta.url),'utf8'));
const limits={timeoutMs:20000,maximumWireBytes:MAX_WIRE,maximumEncodedBytes:MAX_ENCODED,maximumDecodedBytes:MAX_DECODED};
async function fake(scenario) {
  const socket=new EventEmitter(),response=new EventEmitter(),req=new EventEmitter(),timers=[],log=[];
  let counter=0,agentDestroy=0;
  req.destroy=error=>{log.push('request-destroy');req.emit('error',error);socket.emit('close',true);};
  const services={now:()=>BigInt(counter++),setTimer:(fn,ms)=>{const t={fn,ms,cleared:false};timers.push(t);return t;},clearTimer:t=>{if(t)t.cleared=true;},
    afterData:async()=>{log.push('after-data-listeners');},makeAgent:()=>({destroy(){agentDestroy++;log.push('agent-destroy');socket.emit('close',false);}}),
    request(url,options,onResponse){
      ok(url.href==='http://127.0.0.1:61234/actions'&&options.agent&&options.headers['content-length']==='391','Exact one request setup');
      ok(options.headers.origin==='http://127.0.0.1:61234'&&options.headers.referer==='http://127.0.0.1:61234/actions','Only declared leased header substitutions');
      req.end=body=>{ok(body.equals(Buffer.from(record.bodyBase64,'base64')),'Exact captured391B body');queueMicrotask(()=>{
        req.emit('socket',socket);
        if(scenario==='timeout'){timers[0].fn();return;}
        if(scenario==='setup-error'){req.emit('error',null);socket.emit('close',true);return;}
        response.statusCode=200;response.rawHeaders=['Content-Type','text/x-component','Content-Encoding','gzip','Transfer-Encoding','chunked'];response.complete=true;
        onResponse(response);
        // Deliberately put the HTTP parser BEFORE even the prepended raw observer.
        // It emits message end inside this data event; final raw listener must run.
        socket.prependListener('data',()=>{
          const bytes=scenario==='encoded-cap'?Buffer.alloc(MAX_ENCODED+1):gzip;
          response.emit('data',bytes);
          if(scenario==='partial'){response.complete=false;response.emit('error',Object.assign(new Error('partial'),{code:'E_PARTIAL'}));response.emit('close');return;}
          response.emit('end');
        });
        socket.emit('data',scenario==='wire-cap'?Buffer.alloc(MAX_WIRE+1):wire);log.push('all-current-data-listeners-returned');
      });};return req;
    }};
  const value=await captureOne('http://127.0.0.1:61234',record,limits,services);
  ok(agentDestroy===0,'No Agent destruction before caller publishes and validates');
  ok(log.indexOf('all-current-data-listeners-returned')<log.indexOf('after-data-listeners')||['timeout','setup-error'].includes(scenario),'Finalization yields past whole data event');
  return {value,log,timers,get destroys(){return agentDestroy;}};
}
const normal=await fake('normal');
ok(normal.value.wire.equals(wire)&&normal.value.encoded.equals(gzip),'Complete raw final packet despite parser-first end callback');
ok(normal.value.observation.responseComplete&&normal.value.observation.httpMessageEndObserved&&normal.value.observation.errors.length===0,'Normal actual controller terminal fields');
ok(parseHttpMessage(normal.value.wire).body.equals(normal.value.encoded),'Controller raw/encoded equality before cleanup');
ok(decodeSingleGzip(normal.value.encoded).decoded.equals(input),'Controller gzip validated before cleanup');
const cleaned=await normal.value.cleanup({prefixesDurable:true,validationFinished:true});
ok(normal.destroys===1&&cleaned.socketCloseObserved&&cleaned.prefixesDurableBeforeCleanup&&cleaned.httpMessageEndBeforeCleanup,'Owned private Agent closes after normal completion');
ok(normal.value.observation.peerSocketEndObserved===false,'Client Agent close is never peer socket EOF');
ok(cleaned.socketClosedBeforeClientCleanup===false&&cleaned.clientInitiatedSocketCloseRequested===true,'Close-request intent distinguished from prior peer closure');
for(const scenario of ['timeout','setup-error','partial','wire-cap','encoded-cap']){
  const f=await fake(scenario),o=f.value.observation;
  ok(o.errors.length>0,'Failure records original typed cause');
  if(scenario==='timeout')ok(o.timeout&&f.value.wire.length===0&&!o.httpMessageEndObserved,'Genuine zero-received prefix remains failed');
  if(scenario==='partial')ok(f.value.wire.equals(wire)&&f.value.encoded.equals(gzip)&&!o.httpMessageEndObserved,'Partial-error prefixes retained without EOF claim');
  if(scenario==='wire-cap')ok(o.rawSocketPrefixTruncated&&f.value.wire.length===MAX_WIRE,'Raw cap retains exactly bounded prefix');
  if(scenario==='encoded-cap')ok(o.encodedBodyPrefixTruncated&&f.value.encoded.length===MAX_ENCODED,'Encoded cap retains exactly bounded prefix');
  await f.value.cleanup({prefixesDurable:true,validationFinished:true});ok(f.destroys===1,'Failure path still destroys only owned Agent');
}
console.log(JSON.stringify({sourceOnly:true,checks,noActorOrNetworkOrRealAgent:true,syntheticHostZlibOnly:true,parserFirstEndFinalPacketPreserved:true,priorGatesAccepted:false}));
