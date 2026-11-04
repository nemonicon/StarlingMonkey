// Future fresh correctness scopes only. Never starts from checked-in NULL templates.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {open,mkdir,lstat,writeFile,statfs} from 'node:fs/promises';
import {join,resolve,basename} from 'node:path';
import {here,regular,hash} from './physical.mjs';
import {verifyFamily} from './native-preflight.mjs';
import {assertRuntimeAuthority} from './contracts.mjs';
const [scope,outputArgument,authorityPath,authoritySha]=process.argv.slice(2);
assert.equal(process.argv.length,6,'scope output authorityPath authoritySha256');
const output=resolve(outputArgument),prefix='/tmp/starling-node-compat/production-consumers355-release-gates-v2/';
assert(output.startsWith(prefix)&&Buffer.byteLength(basename(output))<=128,'New bounded release-gate output namespace required');
const family=await verifyFamily(),authority=JSON.parse(await regular(authorityPath,authoritySha));
const selected=assertRuntimeAuthority(authority,{familyIndexSha256:family.indexSha256,scope,output});
async function absent(path){try{await lstat(path);assert.fail('Fresh output/controller required: '+path);}catch(error){if(error.code!=='ENOENT')throw error;}}
await absent(output);const controller=output+'.controller';await absent(controller);
const disk=await statfs('/tmp/starling-node-compat');assert(disk.bavail*disk.bsize>=2*1024**3,'Below2GiB before fresh gate');
await mkdir(controller,{recursive:false});
const stdoutPath=join(controller,'stdout.log'),stderrPath=join(controller,'stderr.log');
const stdout=await open(stdoutPath,'wx'),stderr=await open(stderrPath,'wx');
const argv=[join(here,'entry.mjs'),'selected',scope,output],startedAtUtc=new Date().toISOString();
let child,terminal,timeout=false,cleanup=[],spawnError=null,cancelKillTimer,deadlineTimer;const pause=ms=>new Promise(done=>setTimeout(done,ms));
function signalGroup(signal){if(!child?.pid){cleanup.push({signal,result:'no-child-pid'});return;}try{process.kill(-child.pid,signal);cleanup.push({signal,result:'sent'});}catch(error){assert.equal(error.code,'ESRCH');cleanup.push({signal,result:'group-absent'});}}
function cancel(){if(child?.pid){signalGroup('SIGTERM');if(!cancelKillTimer){cancelKillTimer=setTimeout(()=>signalGroup('SIGKILL'),5000);cancelKillTimer.unref();}}}
process.once('SIGTERM',cancel);process.once('SIGINT',cancel);
try{
 child=spawn(process.execPath,argv,{cwd:here,detached:true,env:{...process.env,NODE_COMPAT_RELEASE_ACTION_AUTHORITY:resolve(authorityPath),NODE_COMPAT_RELEASE_ACTION_AUTHORITY_SHA256:authoritySha},stdio:['ignore',stdout.fd,stderr.fd]});
 deadlineTimer=setTimeout(()=>{timeout=true;cancel();},selected.deadlineMs);
 terminal=await new Promise(done=>{child.once('error',error=>{spawnError={name:error.name,code:error.code,message:error.message};});child.once('close',(code,signal)=>done({code,signal}));});
 await writeFile(join(controller,'child-terminal.json'),JSON.stringify({schemaVersion:1,state:'child-terminal-before-cleanup-or-assertions',...terminal,spawnError,timeout,finishedAtUtc:new Date().toISOString()},null,2)+'\n',{flag:'wx'});
 clearTimeout(deadlineTimer);clearTimeout(cancelKillTimer);
 // Only this owned process group can be signalled. No global process scan.
 signalGroup('SIGTERM');await pause(50);signalGroup('SIGKILL');
}finally{clearTimeout(deadlineTimer);clearTimeout(cancelKillTimer);process.removeListener('SIGTERM',cancel);process.removeListener('SIGINT',cancel);if(child?.pid)signalGroup('SIGKILL');await stdout.sync();await stderr.sync();await stdout.close();await stderr.close();}
const record={schemaVersion:1,state:'terminal',scope,output,argv:[process.execPath,...argv],startedAtUtc,finishedAtUtc:new Date().toISOString(),...terminal,spawnError,timeout,deadlineMs:selected.deadlineMs,cleanup,stdoutPath,stderrPath,authoritySha256:authoritySha,familyIndexSha256:family.indexSha256};
await writeFile(join(controller,'terminal.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
assert.equal(terminal.code,0,JSON.stringify(record));assert.equal(terminal.signal,null);assert.equal(timeout,false);assert.equal(spawnError,null);
await verifyFamily();await regular(authorityPath,authoritySha);
await writeFile(join(controller,'final-source-recheck.json'),JSON.stringify({state:'passed',sourceInputsRechecked:true,operationalAdmission:false,terminalSha256:hash(await regular(join(controller,'terminal.json'),hash(Buffer.from(JSON.stringify(record,null,2)+'\n'))))},null,2)+'\n',{flag:'wx'});
