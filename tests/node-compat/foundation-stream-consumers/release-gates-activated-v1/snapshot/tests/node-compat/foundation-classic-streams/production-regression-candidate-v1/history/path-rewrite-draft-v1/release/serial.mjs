// Host-side orchestration only. No source or previous result is ever adopted.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {readFile,writeFile,open,statfs} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {hash} from './preflight.mjs';

export async function runSerial(jobs,run){
  const results=[];
  for(const job of jobs){const value=await run(job);results.push(value);if(value.code!==0)break;}
  return results;
}
export function rejectResume(environment){
  for(const name of ['NODE_COMPAT_RELEASE_RESUME','NODE_COMPAT_OPTIONAL_RESUME','NODE_COMPAT_RESUME'])
    assert(!environment[name],'Fresh run only; resume/reuse is not supported: '+name);
}
export function fixedEnvironment(admission,environment){
  rejectResume(environment);
  const result={...environment,NODE_COMPAT_ENGINE:admission.production.engine,
    NODE_COMPAT_ENGINE_SOURCE_ROOT:admission.production.sourceRoot};
  for(const[key,value]of Object.entries({
    NODE_COMPAT_TOOLCHAIN:'/tmp/starling-node-compat/native-toolchain-lock',
    NODE_COMPAT_COMPONENTIZE_MODULE:'/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js',
  })){if(result[key])assert.equal(resolve(result[key]),value,key);result[key]=value;}
  // The old six-foundation orchestration intentionally did not select Events OFF.
  for(const name of ['PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL']){
    delete result['NODE_COMPAT_'+name+'_OFF_ENGINE'];delete result['NODE_COMPAT_'+name+'_OFF_SOURCE_ROOT'];
  }
  return result;
}
export function countAudits(value){
  let count=0;
  function visit(item){if(!item||typeof item!=='object')return;
    if(item.interfaceAudit){assert.deepEqual(item.interfaceAudit.emittedImports,[]);assert.deepEqual(item.interfaceAudit.selectedInterfaces,[]);count++;}
    for(const child of Object.values(item))if(child&&typeof child==='object')visit(child);
  }
  visit(value);return count;
}
export async function spawnJob(job,{output,environment,repository}){
  const status=await statfs(output),free=status.bavail*status.bsize;
  assert(free>=800*1024*1024,'Below the serial guest prelaunch floor; no new child started');
  const logPath=join(output,job.name+'.log'),log=await open(logPath,'wx');
  const startedAtUtc=new Date().toISOString(),runner=resolve(job.runner),runnerSha256=hash(await readFile(runner));
  let terminal;
  try{
    const child=spawn(process.execPath,[runner],{cwd:repository,env:{...environment,[job.variable]:job.output},stdio:['ignore',log.fd,log.fd]});
    terminal=await new Promise(resolve=>{
      let spawnError=null;child.once('error',error=>{spawnError={name:error.name,code:error.code,message:error.message};});
      child.once('close',(code,signal)=>resolve({code,signal,...(spawnError?{spawnError}:{})}));
    });
  }finally{await log.close();}
  return{name:job.name,runner,runnerSha256,output:job.output,logPath,logSha256:hash(await readFile(logPath)),
    startedAtUtc,finishedAtUtc:new Date().toISOString(),prelaunchFreeBytes:free,...terminal};
}
export async function publish(path,value){
  try{await writeFile(path,JSON.stringify(value,null,2)+'\n');}
  catch(error){console.log(JSON.stringify({event:'report-write-failed',path,error:{name:error.name,code:error.code,message:error.message},partialResult:value}));throw error;}
}
