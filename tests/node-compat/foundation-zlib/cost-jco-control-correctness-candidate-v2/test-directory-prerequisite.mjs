// Explicitly authorized BENIGN host-child regression only. No guest/provider/codec/preflight.
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,readdir,writeFile} from 'node:fs/promises';
import {join,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {runOwnedCommand} from '../cost-jco-correctness-candidate-v2/durable-host.mjs';
import {checkOwnedTerminal} from '../cost-jco-correctness-candidate-v2/glue-policy.mjs';
import {descriptor,regular,hash} from '../cost-jco-correctness-candidate-v2/authority.mjs';
const NODE={path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024};
export async function regression(){
 await regular(NODE,{maxBytes:128*1024*1024});const root=await mkdtemp('/private/tmp/starling-node-compat/control-directory-regression-v2-'),records=[];let checks=0;const ck=(v,m)=>{assert(v,m);checks++;};
 for(const prepared of [false,true]){
  const output=await DurableOutput.create(join(root,prepared?'prepared':'missing')),registered=new Set();await mkdir(join(output.root,'jobs'),{mode:0o700});if(prepared)await mkdir(join(output.root,'processes'),{mode:0o700});
  const write=(path,data)=>output.write(relative(output.root,path),data),args=['-e',"process.stdout.write('BENIGN_CONTROL_DIRECTORY_STDOUT\\n');process.stderr.write('BENIGN_CONTROL_DIRECTORY_STDERR\\n');"];
  try{
   let result,error;try{result=await runOwnedCommand({output:output.root,name:'benign',executable:NODE.path,args,write,register:path=>registered.add(path),timeoutMs:10000,maxOutputBytes:4096,heartbeatMs:1000});}catch(value){error=value;}
   if(!prepared){
    // Record ordinary observed failure BEFORE expected-failure assertions. The
    // unchanged helper source places this error before its launch/spawn lines.
    const observed={schemaVersion:1,prepared:false,thrown:error!==undefined,code:error?.code??null,path:typeof error?.path==='string'?error.path:null,registeredFiles:[...registered],collectedFiles:[...output.rows.keys()],directoryEntries:await readdir(output.root),noChildClaimBasis:'source ordering: ordinary() precedes launch record and spawn; no runtime spawn instrumentation',guestOrCodecInvoked:false};
    await writeFile(join(root,'missing-observed.json'),JSON.stringify(observed,null,2)+'\n',{flag:'wx',mode:0o600});
    ck(error?.code==='ENOENT'&&error.path===join(output.root,'processes'),'actual missing processes ENOENT');ck(registered.size===0&&output.rows.size===0,'before launch/raw files');ck(JSON.stringify(observed.directoryEntries)==='["jobs"]','no worker/output/control artifacts');await output.recheck();records.push(observed);
   }else{
    // Helper already fsynced the complete raw pipes and terminal. Retain a
    // whole return descriptor before status checks; no fabricated terminal.
    await writeFile(join(root,'prepared-helper-return.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx',mode:0o600});
    const terminalRaw=await readFile(result.terminalPath),stdoutRaw=await readFile(result.stdoutFile.path),stderrRaw=await readFile(result.stderrFile.path);
    await writeFile(join(root,'prepared-raw-capture.json'),JSON.stringify({terminalPath:result.terminalPath,terminalSha256:hash(terminalRaw),stdoutPath:result.stdoutFile.path,stdoutSha256:hash(stdoutRaw),stderrPath:result.stderrFile.path,stderrSha256:hash(stderrRaw),rawPersistedBeforeAssertions:true},null,2)+'\n',{flag:'wx',mode:0o600});
    for(const path of registered){const bytes=await readFile(path),name=relative(output.root,path);output.rows.set(name,{path:name,sha256:hash(bytes),bytes:bytes.length});}
    checkOwnedTerminal(result);checks++;ck(result.status===0&&result.ownedGroupGone&&result.terminalExitZeroObserved,'actual raw0 owned cleanup');ck(stdoutRaw.toString()==='BENIGN_CONTROL_DIRECTORY_STDOUT\n'&&stderrRaw.toString()==='BENIGN_CONTROL_DIRECTORY_STDERR\n','whole benign raw pipes');
    ck(output.rows.size===4,'launch/stdout/stderr/terminal exact membership');await output.recheck();checks++;records.push({prepared:true,status:0,ownedGroupGone:true,terminal:descriptor({path:result.terminalPath,sha256:hash(terminalRaw),bytes:terminalRaw.length}),files:[...output.rows.values()],guestOrCodecInvoked:false});
   }
  }finally{await output.close();}
 }
 const result={schemaVersion:1,state:'BENIGN_GENUINE_LIFECYCLE_DIRECTORY_REGRESSION_PASSED',root,checks,benignHostChildrenStarted:1,oldControlActionInvoked:false,newControlActionInvoked:false,preflightInvoked:false,guestInvoked:false,providerOrCodecInvoked:false,records};await writeFile(join(root,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx',mode:0o600});return result;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))process.stdout.write(JSON.stringify(await regression())+'\n');
