import assert from 'node:assert/strict';
import net from 'node:net';
import {openSync,appendFileSync,fsyncSync,closeSync} from 'node:fs';
import {errorData} from '../peer-disconnect-candidate-v1/diagnostic-common.mjs';
export function decode(raw,partial=false) {
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
// Descendant of the real Node reference TCP client, with late leased port,
// raw bytes durably appended BEFORE frame inspection and callback milestone.
export async function request({port,origin,label,path,rawPath,waitForReadAttempt,
  body,partialUpload=false,closeAfterFirst=false,deadlineMilliseconds=10000}) {
  assert(Number.isInteger(port)&&port>0&&port<65536&&origin==='http://127.0.0.1:'+port);
  const fd=openSync(rawPath,'wx',0o600),socket=net.createConnection({host:'127.0.0.1',port});
  const received=[],socketEvents=[];let closeRequested=false,deadline,closedObserved=false,collectionFailure;
  const record={label,path,rawPath,rawBytes:0,socketEvents,firstBodyBeforeClose:null,
    forcedClientCleanup:false,source:'actual-node-net-client-not-a-WASI-backend'};
  const closed=new Promise((resolve,reject)=>{
    deadline=setTimeout(()=>{record.forcedClientCleanup=true;socket.destroy();reject(new Error('Client deadline'));},deadlineMilliseconds);
    socket.on('data',part=>{
      try {
        if(record.rawBytes+part.length>131072)throw new RangeError('Client byte cap');
        appendFileSync(fd,part);received.push(Buffer.from(part));record.rawBytes+=part.length;
        const frame=decode(Buffer.concat(received),true);
        if(closeAfterFirst&&!closeRequested&&frame?.body.byteLength) {
          closeRequested=true;socketEvents.push({phase:'actual-first-response-body-bytes',bytes:frame.body.byteLength});
          socketEvents.push({phase:'client-destroySoon-invocation-attempt'});socket.destroySoon();
        }
      } catch(error){collectionFailure=error;record.forcedClientCleanup=true;socket.destroy();reject(error);}
    });
    socket.on('end',()=>socketEvents.push({phase:'client-end'}));
    socket.on('error',error=>socketEvents.push({phase:'client-error',error:errorData(error)}));
    socket.on('close',hadError=>{closedObserved=true;clearTimeout(deadline);socketEvents.push({phase:'client-close',hadError});resolve();});
  });
  void closed.catch(()=>{});
  try {
    await new Promise((resolve,reject)=>{socket.once('connect',resolve);socket.once('error',reject);});
    const method=body?'POST':'GET';
    socket.write(`${method} ${path} HTTP/1.1\r\nHost: 127.0.0.1:${port}\r\nX-Peer-Case: ${label}\r\nConnection: close\r\n${body?'Content-Length: 8192\r\n':''}\r\n`);
    if(body)socket.write(body);
    if(partialUpload) {
      const milestone=await waitForReadAttempt(label,body.length);
      record.synchronizedMilestone=milestone;
      socketEvents.push({phase:'prefix-return-followed-by-read-invocation-attempt',sequence:milestone.sequence,
        hostReadEnteredOrBlockedProved:false});
      socketEvents.push({phase:'client-end-invocation-attempt'});socket.end();
    }
    await closed;
    if(collectionFailure!==undefined)throw collectionFailure;
  } catch(error){record.transportOrCollectionError=errorData(error);}
  finally {
    if(!closedObserved){record.forcedClientCleanup=true;socket.destroy();}
    clearTimeout(deadline);fsyncSync(fd);closeSync(fd);
  }
  // Raw receipt precedes semantic decoding. Unknown/failed partial frames remain retained.
  const raw=Buffer.concat(received);
  try {
    if(raw.length){const frame=decode(raw,closeAfterFirst);record.status=frame.status;
      record.headers=frame.headers;record.decodedBodyBase64=frame.body.toString('base64');
      record.decodedBodyBytes=frame.body.length;}
  } catch(error){record.frameDecodeError=errorData(error);}
  record.firstBodyBeforeClose=closeAfterFirst?closeRequested:null;
  record.clientCloseObserved=closedObserved;
  return record;
}
