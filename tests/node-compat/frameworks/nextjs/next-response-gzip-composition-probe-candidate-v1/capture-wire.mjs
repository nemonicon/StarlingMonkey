// Dormant raw-client Source. Root supplies the owned server and original owner.
import assert from 'node:assert/strict';
import {createConnection} from 'node:net';
import {mkdir,lstat,open,readFile,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,4);
const origin=process.argv[2],out=resolve(process.argv[3]);
assert(/^http:\/\/127\.0\.0\.1:([1-9][0-9]{0,4})$/.test(origin));
const port=Number(origin.slice(origin.lastIndexOf(':')+1));assert(port>0&&port<=65535&&port!==80);
try{await lstat(out);throw new Error('Wire output must be fresh');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(out,{mode:0o700});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const row=async path=>{const b=await readFile(path);return{path,sha256:createHash('sha256').update(b).digest('hex'),bytes:b.length};};
const capture={schemaVersion:1,suite:'GZIP_COMPOSITION_RAW_WIRE_V1',origin,node:process.version,requests:[],errors:[],semanticsInvoked:false};
for(const caseId of ['small','large']){
 const path='/gzip-composition/'+caseId,wire=join(out,caseId+'.http');
 const request='GET '+path+' HTTP/1.1\r\nHost: 127.0.0.1:'+port+'\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n';
 const item={caseId,method:'GET',path,url:origin+path,request,wire:null,receivedBytes:0,
  initialReadDelayMs:250,betweenReadDelayMs:10,timeoutMs:20000,socketEndObserved:false,
  socketCloseObserved:false,socketHadError:false,error:null,cleanupErrors:[]};
 await writeFile(join(out,caseId+'.request.json'),JSON.stringify(item,null,2)+'\n',{flag:'wx',mode:0o600});
 const file=await open(wire,'wx',0o600);let socket,timer;
 try{
  socket=createConnection({host:'127.0.0.1',port});
  socket.once('end',()=>{item.socketEndObserved=true;});
  const closed=new Promise(resolve=>socket.once('close',hadError=>{item.socketCloseObserved=true;item.socketHadError=hadError;resolve();}));
  timer=setTimeout(()=>socket.destroy(new Error('Raw total request timeout')),20000);
  await new Promise((yes,no)=>{socket.once('connect',yes);socket.once('error',no);});
  socket.pause();socket.write(request);await delay(250);
  for await(const chunk of socket){
   if(item.receivedBytes+chunk.length>4194304)throw new RangeError('Wire cap');
   let offset=0;while(offset<chunk.length){const r=await file.write(chunk,offset,chunk.length-offset);if(r.bytesWritten<=0)throw new Error('Wire write made no progress');offset+=r.bytesWritten;item.receivedBytes+=r.bytesWritten;}await delay(10);
  }
  await closed;
 }catch(error){item.error={name:error?.name??null,message:error?.message??String(error)};capture.errors.push({caseId,...item.error});}
 finally{
  clearTimeout(timer);if(socket&&!socket.destroyed)socket.destroy();
  try{await file.sync();}catch(error){item.cleanupErrors.push({stage:'file-sync',message:String(error)});}
  try{await file.close();}catch(error){item.cleanupErrors.push({stage:'file-close',message:String(error)});}
 }
 item.wire=await row(wire);capture.requests.push(item);
 await writeFile(join(out,caseId+'.json'),JSON.stringify(item,null,2)+'\n',{flag:'wx',mode:0o600});
}
await writeFile(join(out,'wire-capture.json'),JSON.stringify(capture,null,2)+'\n',{flag:'wx',mode:0o600});
console.log(JSON.stringify({capture:await row(join(out,'wire-capture.json')),errors:capture.errors,semanticsInvoked:false}));
process.exitCode=capture.errors.length?1:0;
