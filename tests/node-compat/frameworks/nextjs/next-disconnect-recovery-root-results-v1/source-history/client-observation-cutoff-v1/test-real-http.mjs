// Real loopback protocol controls for the collector, never a guest substitute.
import assert from 'node:assert/strict';
import net from 'node:net';
import {once} from 'node:events';
import {mkdir,realpath,readFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {collectCall,hash} from './http-call.mjs';
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,3);
const output=process.argv[2];assert.equal(resolve(output),output);assert(output.startsWith('/private/tmp/starling-node-compat/next-disconnect-recovery-client-protocol-'));
assert.equal(await realpath(dirname(output)),dirname(output));await mkdir(output,{mode:0o700});
const cases=[
 {id:'complete-content-length',wire:'HTTP/1.1 200 OK\r\nContent-Length: 5\r\nConnection: close\r\n\r\nhello',complete:true},
 {id:'complete-chunked',wire:'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n2\r\nhe\r\n3\r\nllo\r\n0\r\n\r\n',complete:true},
 {id:'underlength-content-length',wire:'HTTP/1.1 200 OK\r\nContent-Length: 10\r\nConnection: close\r\n\r\nhello',complete:false},
 {id:'body-overflow',wire:'HTTP/1.1 200 OK\r\nContent-Length: 5\r\nConnection: close\r\n\r\nhello',limit:4},
 {id:'never-body-deadline',wire:'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n',hold:true,deadline:true},
 {id:'first-actual-body-close',wire:'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n5\r\nhello\r\n',hold:true,intentional:true}];
const results=[];
for(const spec of cases){
 let peer,peerClosed=false,requests=0,fixtureError=null;const server=net.createServer(socket=>{
  assert.equal(++requests,1);peer=socket;socket.on('error',error=>{fixtureError={name:error.name,code:error.code,message:error.message};});socket.on('close',()=>{peerClosed=true;});
  let text='',answered=false;socket.on('data',bytes=>{if(answered)return;text+=bytes.toString('latin1');assert(text.length<=65536);if(!text.includes('\r\n\r\n'))return;answered=true;if(spec.hold)socket.write(spec.wire);else socket.end(spec.wire);});
 });
 server.listen({host:'127.0.0.1',port:0,exclusive:true});await once(server,'listening');const port=server.address().port;
 let record;
 try{
  record=await collectCall({origin:'http://127.0.0.1:'+port,spec:{id:spec.id,method:'GET',path:'/',intentionalDisconnect:spec.intentional===true},
   bodyPath:join(output,spec.id+'.body'),httpTimeoutMs:spec.deadline?100:2000,bodyLimitBytes:spec.limit??4194304});
  assert.equal(record.connection.cleanupCompleted,true);assert.equal(record.request.closeObserved,true);assert.equal(record.connection.socketCloseObserved,true);
  const body=await readFile(record.body.path);assert.equal(hash(body),record.body.sha256);assert.equal(body.length,record.body.bytes);
  if(spec.complete!==undefined){assert.equal(record.collectionComplete,true);assert.equal(record.httpComplete,spec.complete);assert.equal(body.toString(),'hello');}
  if(spec.limit){assert.equal(record.capture.overflow,true);assert.equal(record.collectionComplete,false);assert.equal(record.httpComplete,false);}
  if(spec.deadline){assert.equal(record.deadline.exceeded,true);assert.equal(record.httpComplete,false);assert.equal(record.collectionComplete,true);assert.equal(body.length,0);}
  if(spec.intentional){assert.equal(record.intentionalDisconnect.triggered,true);assert.equal(record.intentionalDisconnect.localDestroyInvoked,true);assert.equal(record.intentionalDisconnect.firstChunkBytes,5);assert.equal(record.intentionalDisconnect.completeAtIntent,false);assert.equal(record.httpComplete,false);assert.equal(record.collectionComplete,true);assert.equal(body.toString(),'hello');}
 }finally{
  // The fixture waits for actual client-close propagation on its own socket;
  // this is host loopback evidence, never a guest-resource acknowledgment.
  try{
   if(peer&&!peerClosed){let timer;try{await Promise.race([once(peer,'close'),new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('Fixture peer close deadline')),2000);})]);}finally{clearTimeout(timer);}}
  }finally{peer?.destroy();await new Promise((yes,no)=>server.close(error=>error?no(error):yes()));}
 }
 assert.equal(peerClosed,true);results.push({id:spec.id,collectionComplete:record.collectionComplete,httpComplete:record.httpComplete,deadline:record.deadline.exceeded,intentional:record.intentionalDisconnect.triggered,fixturePeerClosed:peerClosed,fixtureError});
}
process.stdout.write(JSON.stringify({suite:'NEXT_DISCONNECT_RECOVERY_REAL_HTTP_PROTOCOL_CONTROLS_V1',passed:true,cases:results,guestExecuted:false})+'\n');
