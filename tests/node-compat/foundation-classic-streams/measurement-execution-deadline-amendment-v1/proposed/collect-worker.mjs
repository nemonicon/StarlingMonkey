// Explicitly owned async host child; terminal evidence precedes caller assertions.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {dirname,basename,join} from 'node:path';
import {runOwnedCommand,persistFile} from './owned-host.mjs';
import {deadlinePolicy} from './deadline-policy.mjs';
export async function collectWorker(entry,args,prefix,{deadlineMs,budget=null}={}){
 assert(Number.isSafeInteger(deadlineMs)&&deadlineMs>0&&deadlineMs<=deadlinePolicy.workerHardMaxMs);
 const output=dirname(prefix),name=basename(prefix).replaceAll('.','_');assert(/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(name));await mkdir(join(output,'processes'),{recursive:true});
 const paths=new Set(),write=async(path,data,options)=>{await writeFile(path,data,options);paths.add(path);},register=path=>paths.add(path);
 await persistFile({output,write,path:prefix+'.budget.json',data:JSON.stringify({deadlineMs,budget,operationalOnly:true,allCaseAdequacyClaim:false},null,2)+'\n'});
 const outcome=await runOwnedCommand({output,name,executable:process.execPath,args:[entry,...args],write,register,timeoutMs:deadlineMs,maxOutputBytes:4*1024*1024,graceMs:5000,heartbeatMs:30000,
  onProgress:detail=>process.stderr.write(JSON.stringify({stage:'owned-worker-heartbeat',...detail})+'\n')});
 const passed=outcome.terminalExitZeroObserved&&outcome.ownedGroupGone;
 return{...outcome,wholeProcessElapsedMs:outcome.operationalElapsedMs,stdout:outcome.stdout??'',error:passed?null:JSON.stringify({status:outcome.status,signal:outcome.signal,spawnError:outcome.spawnError,timedOut:outcome.timedOut,externalSignal:outcome.externalSignal,closed:outcome.closed,ownedGroupGone:outcome.ownedGroupGone,errors:outcome.errors}),capturedFiles:[...paths],budget};
}
