// Host collection only. No engine, guest, toolchain or native imports.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createReadStream} from 'node:fs';
import {open,readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,isAbsolute,join,relative,resolve,sep} from 'node:path';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
async function ordinary(output,path){
 const root=resolve(output),target=resolve(path),name=relative(root,target);
 assert(name&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name));
 let current=dirname(target);
 for(;;){const stat=await lstat(current);assert(stat.isDirectory()&&!stat.isSymbolicLink());if(current===root)break;const parent=dirname(current);assert.notEqual(parent,current);current=parent;}
 return target;
}
export async function persistFile({output,write,path,data}){
 const target=await ordinary(output,path);await write(target,data,{flag:'wx'});
 const handle=await open(target,'r');try{await handle.sync();}finally{await handle.close();}
 const bytes=typeof data==='string'?Buffer.from(data):Buffer.from(data);
 return{path:target,sha256:hash(bytes),bytes:bytes.length};
}
export function progressJournal({output,write}){
 let sequence=0;
 return async function progress(event,detail={}){
  const record={schemaVersion:1,sequence:++sequence,event,atUtc:new Date().toISOString(),...detail,
   partialObservationOnly:true,requiresFinalCompletionAndExternalExitZero:true,runtimeAcceptanceClaim:false};
  console.log(JSON.stringify({event:'correctness-progress',sequence,eventName:event,...detail}));
  await persistFile({output,write,path:join(output,'progress',String(sequence).padStart(5,'0')+'.json'),data:JSON.stringify(record,null,2)+'\n'});
  return record;
 };
}
async function fileInfo(path){const digest=createHash('sha256');let bytes=0;for await(const chunk of createReadStream(path)){digest.update(chunk);bytes+=chunk.length;}return{path,sha256:digest.digest('hex'),bytes};}
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));

// Each command is a fresh owned POSIX session. All bytes read from its pipes are
// streamed to exclusively created files; a failed command cannot publish a pass.
// The timeout is a finite operational bound, never a timing/performance sample.
export async function runOwnedCommand({output,name,executable,args,write,register,
 timeoutMs=600000,maxOutputBytes=16*1024*1024,graceMs=5000,heartbeatMs=30000,onProgress=()=>{},env,cwd}){
 assert(/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(name));assert(isAbsolute(executable));assert(env&&typeof env==='object'&&isAbsolute(cwd),'Explicit private child context');
 assert(Number.isSafeInteger(timeoutMs)&&timeoutMs>0&&timeoutMs<=600000);
 assert(Number.isSafeInteger(maxOutputBytes)&&maxOutputBytes>0);assert(graceMs>0&&graceMs<=5000);
 const prefix=join(output,'processes',name),stdoutPath=await ordinary(output,prefix+'.stdout.txt'),stderrPath=await ordinary(output,prefix+'.stderr.txt');
 const launchPath=prefix+'.launch.json',terminalPath=prefix+'.terminal.json';
 await persistFile({output,write,path:launchPath,data:JSON.stringify({schemaVersion:1,executable,args,timeoutMs,maxOutputBytes,
  detachedOwnedSession:true,completed:false,startedAtUtc:new Date().toISOString(),runtimeAcceptanceClaim:false},null,2)+'\n'});
 let stdoutHandle,stderrHandle;
 try{stdoutHandle=await open(stdoutPath,'wx');register(stdoutPath);stderrHandle=await open(stderrPath,'wx');register(stderrPath);}
 catch(error){if(stdoutHandle)await stdoutHandle.close();throw error;}
 const started=Date.now(),errors=[],signals=[];let child,pid=null,closed=false,exitCode=null,exitSignal=null,spawnError=null;
 let timedOut=false,outputLimitExceeded=false,groupGone=false,termination=null,stdoutBytes=0,stderrBytes=0,externalSignal=null,signalCount=0;
 function groupAlive(){
  if(groupGone||pid===null)return false;
  try{process.kill(-pid,0);return true;}catch(error){if(error.code==='ESRCH'){groupGone=true;return false;}throw error;}
 }
 function signal(number){
  if(groupGone||pid===null)return;
  try{process.kill(-pid,number);signals.push({signal:number,result:'sent'});}catch(error){if(error.code==='ESRCH'){groupGone=true;signals.push({signal:number,result:'already-gone'});}else errors.push({stage:'signal',code:error.code,message:error.message});}
 }
 async function terminate(reason,immediate=false){
  if(termination)return termination;
  termination=(async()=>{try{
   if(immediate)signal('SIGKILL');else{signal('SIGTERM');const deadline=Date.now()+graceMs;while(groupAlive()&&Date.now()<deadline)await delay(25);if(groupAlive())signal('SIGKILL');}
   const deadline=Date.now()+graceMs;while(groupAlive()&&Date.now()<deadline)await delay(25);
   return{reason,groupGone:!groupAlive()};
  }catch(error){errors.push({stage:'owned-group-observation',code:error.code,message:error.message});return{reason,groupGone:false};}
  })();
  return termination;
 }
 let timer,heartbeat,ceilingTimer,releaseClose;
 const closePromise=new Promise(resolve=>{releaseClose=resolve;});
 const onSigterm=()=>{externalSignal='SIGTERM';signalCount++;void terminate('collector-SIGTERM');};
 const onSigint=()=>{externalSignal='SIGINT';signalCount++;void terminate('collector-SIGINT');};
 process.on('SIGTERM',onSigterm);process.on('SIGINT',onSigint);
 try{
  child=spawn(executable,args,{detached:true,stdio:['ignore','pipe','pipe'],env:{...env},cwd});
  if(child.pid!==undefined){pid=child.pid;assert(pid>1&&pid!==process.pid);}
  child.once('error',error=>{spawnError={name:error.name,code:error.code,message:error.message};});
  child.once('exit',(code,signal)=>{exitCode=code;exitSignal=signal;});
  child.once('close',(code,signal)=>{closed=true;exitCode=code;exitSignal=signal;releaseClose();});
  timer=setTimeout(()=>{timedOut=true;void terminate('deadline');},timeoutMs);
  heartbeat=setInterval(()=>{try{onProgress({name,elapsedMs:Date.now()-started,stdoutBytes,stderrBytes,partialObservationOnly:true});}catch(error){errors.push({stage:'heartbeat',message:error.message});}},heartbeatMs);
  async function pump(stream,handle,kind){
   try{for await(const chunk of stream){await handle.writeFile(chunk);if(kind==='stdout')stdoutBytes+=chunk.length;else stderrBytes+=chunk.length;
    if((kind==='stdout'?stdoutBytes:stderrBytes)>maxOutputBytes&&!outputLimitExceeded){outputLimitExceeded=true;void terminate('output-limit',true);}}}
   catch(error){errors.push({stage:kind+'-stream',code:error.code,message:error.message});void terminate('stream-error',true);}
  }
  const pumps=[pump(child.stdout,stdoutHandle,'stdout'),pump(child.stderr,stderrHandle,'stderr')];
  // A bounded deadline also handles a leader that exits while descendants keep
  // inherited pipes open. No unrelated process/group is searched or signalled.
  const ceiling=timeoutMs+2*graceMs+1000;
  const completed=await Promise.race([closePromise.then(()=>true),new Promise(resolve=>{ceilingTimer=setTimeout(()=>resolve(false),ceiling);})]);
  if(!completed){errors.push({stage:'bounded-reap',message:'Owned close/reap did not complete within deadline plus cleanup allowance'});await terminate('bounded-reap',true);child.stdout.destroy();child.stderr.destroy();child.unref();}
  if(closed&&groupAlive()){errors.push({stage:'owned-descendants',message:'Owned group remained after leader close'});await terminate('owned-descendants');}
  await Promise.all(pumps);
  if(termination)await termination;
 }catch(error){errors.push({stage:'launch-or-collection',name:error.name,code:error.code,message:error.message});await terminate('collection-error',true);}
 finally{
  clearTimeout(timer);clearInterval(heartbeat);clearTimeout(ceilingTimer);
  process.removeListener('SIGTERM',onSigterm);process.removeListener('SIGINT',onSigint);
  for(const handle of[stdoutHandle,stderrHandle]){try{await handle.sync();}catch(error){errors.push({stage:'stream-sync',code:error.code,message:error.message});}try{await handle.close();}catch(error){errors.push({stage:'stream-close',code:error.code,message:error.message});}}
 }
 const stdout=await fileInfo(stdoutPath),stderr=await fileInfo(stderrPath);
 const outcome={schemaVersion:1,name,executable,args,pid,status:exitCode,signal:exitSignal,spawnError,timedOut,timeoutMs,externalSignal,signalCount,
  outputLimitExceeded,maxOutputBytes,stdout,stderr,signals,errors,closed,ownedGroupGone:!groupAlive(),
  operationalElapsedMs:Date.now()-started,terminalExitZeroObserved:closed&&exitCode===0&&!exitSignal&&!spawnError&&!timedOut&&!externalSignal&&!outputLimitExceeded&&errors.length===0,
  validationCompleted:false,runtimeAcceptanceClaim:false};
 await persistFile({output,write,path:terminalPath,data:JSON.stringify(outcome,null,2)+'\n'});
 return{...outcome,terminalPath,stdout:stdout.bytes<=maxOutputBytes?await readFile(stdoutPath,'utf8'):null,
  stderr:stderr.bytes<=maxOutputBytes?await readFile(stderrPath,'utf8'):null,stdoutFile:stdout,stderrFile:stderr};
}
