// Owned POSIX server lifecycle, using the accepted serve/dev commands and
// existing detached-group capture/cleanup pattern. Import starts nothing.
import {spawn} from 'node:child_process';
import {open,readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {need,hash} from './authority.mjs';
import {signalGroup} from './models.mjs';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
export async function ownedServer({output,name,executable,args,env,cwd,visit,timeoutMs=600000}){
 need(['wasmtime','wash'].includes(name)&&timeoutMs===600000&&typeof visit==='function','Finite host/controller');
 const prefix='servers/'+name,stdoutPath=join(output.root,prefix+'.stdout.log'),stderrPath=join(output.root,prefix+'.stderr.log');
 await output.write(prefix+'.launch.json',{schemaVersion:1,executable,args,env,cwd,detachedOwnedGroup:true,timeoutMs,partial:true},{json:true});
 let stdout,stderr;try{stdout=await open(stdoutPath,'wx',0o600);stderr=await open(stderrPath,'wx',0o600);}catch(error){if(stdout)await stdout.close();throw error;}
 let child,pid=null,closed=false,status=null,signal=null,spawnError=null,timedOut=false,outputLimitExceeded=false,externalSignal=null,exitResolve;
 const errors=[],shutdownSignals=[],counts={stdout:0,stderr:0},started=Date.now(),exit=new Promise(r=>{exitResolve=r;});
 const alive=()=>{if(pid===null)return false;try{process.kill(signalGroup(pid,process.pid),0);return true;}catch(e){if(e.code==='ESRCH')return false;errors.push({stage:'owned-group-observation',code:e.code,message:e.message});return true;}};
 const send=s=>{if(pid===null)return;try{process.kill(signalGroup(pid,process.pid),s);shutdownSignals.push(s);}catch(e){if(e.code!=='ESRCH')errors.push({stage:'owned-signal',code:e.code,message:e.message});}};
 const interrupt=s=>{externalSignal=s;send('SIGKILL');};const onInt=()=>interrupt('SIGINT'),onTerm=()=>interrupt('SIGTERM');
 let timer,pumps=[],value,thrown=null;
 process.on('SIGINT',onInt);process.on('SIGTERM',onTerm);
 try{
  child=spawn(executable,args,{detached:true,env:{...env},cwd,stdio:['ignore','pipe','pipe']});pid=child.pid??null;if(pid!==null)signalGroup(pid,process.pid);
  child.once('error',e=>{spawnError={name:e.name,code:e.code,message:e.message};});child.once('close',(code,s)=>{closed=true;status=code;signal=s;exitResolve();});
  async function pump(source,target,kind){try{for await(const chunk of source){await target.writeFile(chunk);counts[kind]+=chunk.length;if(counts[kind]>16*1024*1024){outputLimitExceeded=true;send('SIGKILL');}}}catch(e){errors.push({stage:kind+'-capture',code:e.code,message:e.message});send('SIGKILL');}}
  pumps=[pump(child.stdout,stdout,'stdout'),pump(child.stderr,stderr,'stderr')];timer=setTimeout(()=>{timedOut=true;send('SIGKILL');},timeoutMs);
  await output.write(prefix+'.owned.json',{schemaVersion:1,pid,processGroup:pid===null?null:-pid,executable,args,cwd,env,detachedOwnedSession:pid!==null,externalControllerMayCleanOnlyThisOwnedSession:true},{json:true});
  value=await visit({pid,closed:()=>closed,readLogs:async()=>({stdout:await readFile(stdoutPath,'utf8'),stderr:await readFile(stderrPath,'utf8')}),check:()=>need(!closed&&!timedOut&&!outputLimitExceeded&&!spawnError,'Owned host alive inside deadline')});
 }catch(e){thrown={type:typeof e,name:e?.name,message:String(e?.message??'host operation failed').slice(0,2048)};}
 finally{
  if(!closed)send('SIGINT');await Promise.race([exit,pause(8000)]);
  if(!closed||alive()){send('SIGTERM');await Promise.race([exit,pause(3000)]);}
  if(!closed||alive()){send('SIGKILL');await Promise.race([exit,pause(3000)]);}
  if(!closed){errors.push({stage:'bounded-reap',message:'Owned server close not observed'});child?.stdout?.destroy();child?.stderr?.destroy();child?.unref();}
  await Promise.all(pumps);clearTimeout(timer);process.removeListener('SIGINT',onInt);process.removeListener('SIGTERM',onTerm);
  for(const handle of [stdout,stderr]){try{await handle.sync();}catch(e){errors.push({stage:'stream-sync',message:e.message});}await handle.close();}
 }
 for(const [suffix,path] of [['stdout.log',stdoutPath],['stderr.log',stderrPath]]){const raw=await readFile(path);output.rows.set(prefix+'.'+suffix,{path:prefix+'.'+suffix,sha256:hash(raw),bytes:raw.length});}
 const terminal={schemaVersion:1,pid,status,signal,closed,spawnError,timedOut,outputLimitExceeded,externalSignal,errors,shutdownSignals,ownedGroupGone:!alive(),elapsedOperationalMs:Date.now()-started,thrown};
 await output.write(prefix+'.terminal.json',terminal,{json:true}); // durable BEFORE caller assertions
 return{value,terminal};
}
