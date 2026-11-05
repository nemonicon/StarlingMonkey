// Future stock-WT action main. No process or guest executes at module import.
import {readFile,mkdir,statfs} from 'node:fs/promises';
import {join,dirname,relative,resolve,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {descriptor,regular,need,hash} from '../ownership-component-candidate-v1/authority.mjs';
import {DurableOutput} from '../ownership-component-candidate-v1/durable.mjs';
import {runOwnedCommand} from '../ownership-component-candidate-v1/durable-host.mjs';
import {validateArgv,argvAudit,parseScalarStringOutput,checkOracle,checkWholeRecord,strictTerminal} from './protocol.mjs';
const local=(root,path)=>{const n=relative(root,path);need(n&&!isAbsolute(n)&&!n.startsWith('../')&&!n.includes('\\')&&n.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Only owned descendant');return n;};
async function rowAt(path){const b=await readFile(path);return descriptor({path,sha256:hash(b),bytes:b.length});}
export async function runWasmtime(frame){
 need(frame?.kind==='secret355-stock-wasmtime-host-admission-v1','Only freshly authenticated new host frame');const space=await statfs(dirname(frame.outputRoot));need(space.bavail*space.bsize>=2*1024**3,'Operational output headroom');checkOracle(frame.oracle);
 const out=await DurableOutput.create(frame.outputRoot),sessions=[];
 try{
  await out.write('node-oracle-reference.json',frame.oracle,{json:true});await mkdir(join(out.root,'processes'),{mode:0o700});
  for(let ordinal=1;ordinal<=3;ordinal++){
   await frame.recheck();const name='validate-'+ordinal,args=validateArgv(frame.component),accounting=argvAudit(frame.wasmtime.path,args,process.env);need(accounting.strictlyBelowArgMax,'Final argv+environment arithmetic bound; actual spawn still required');
   await out.write(name+'-argv.json',{schemaVersion:1,executable:frame.wasmtime,args,accounting,fullEnvironmentValuesRetained:false,noShell:true,noArgumentOrOutputClipping:true},{json:true});
   const registered=new Set(),terminal=await runOwnedCommand({output:out.root,name,executable:frame.wasmtime.path,args,write:(path,bytes)=>out.write(local(out.root,path),bytes),register:path=>registered.add(path),timeoutMs:frame.workerTimeoutMs,maxOutputBytes:frame.maxPipeBytes,onProgress:v=>process.stdout.write(JSON.stringify({event:'secret355-stock-wt-operational-heartbeat',...v})+'\n')});
   for(const path of registered){const r=await rowAt(path);out.rows.set(local(out.root,path),{path:local(out.root,path),sha256:r.sha256,bytes:r.bytes});}
   // Complete stdout/stderr and terminal already fsynced by unchanged collector.
   strictTerminal(terminal);const bytes=await readFile(terminal.stdoutFile.path),value=parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:true});
   const captured=await out.write(name+'-decoded-string.json',{schemaVersion:1,ordinal,kind:'whole-WAVE-scalar-string',value,rawStdout:terminal.stdoutFile,rawStderr:terminal.stderrFile,terminal:await rowAt(terminal.terminalPath),decodedBeforeSemanticAssertions:true},{json:true});
   need(value===frame.jcoWrapper.observed.value,'Whole decoded WAVE string exact actual Jco wrapper bytes');const record=JSON.parse(value);checkWholeRecord(record,frame.oracle,frame.jcoWrapper);await out.write(name+'-record.json',record,{json:true});await frame.recheck();
   sessions.push({ordinal,pid:terminal.pid,terminal:await rowAt(terminal.terminalPath),decodedString:captured,record:await rowAt(join(out.root,name+'-record.json')),rawExitCode:0,ownedGroupGone:true});
  }
  need(new Set(sessions.map(s=>s.pid)).size===3,'Three distinct fresh owned stock-WT processes');await frame.recheck();await out.recheck();
  const result=await out.write('results.json',{schemaVersion:1,state:'SECRET355_STOCK_WASMTIME_VALIDATE_COMPLETE_UNREVIEWED_V1',sourceIndexSha256:frame.sourceIndexSha256,rootAction:frame.rootAction,component:frame.component,wasmtime:frame.wasmtime,sessions,outerPublicStrings:3,withinExportRunRecords:12,guestKeyImports:6,guestSignAttempts:33,guestVerifyAttempts:30,allWholeFieldsMatchActualSecretJcoWrapper:true,allWholeDecodedStringsExactlyMatchActualSecretJco:true,allFourGuardedCasesExecuted:true,successfulFullTagsCompared:27,fullVerifyBooleans:27,verifyTrue:15,verifyFalse:12,emittedImports:[],samePreviouslyAuditedComponent:true,oneOuterExportPerProcess:true,separateHostCallInterleavingProved:false,processOrRequestReuseProved:false,generatedJsImported:false,nodeOracleRerun:false,gcOomFaultResetOrPressureExecuted:false,oldUnsafePrototypeArtifactExecuted:false,onlyGuardedCase3Executed:true,finalizerFreeWipeOrIsolatedRootObserved:false,operationalAdmission:false,runtimeAcceptanceClaim:false,timingAllowed:false},{json:true});
  const index=await out.write('index.json',{schemaVersion:1,files:[...out.rows.values()]},{json:true});const completion=await out.write('completion.json',{schemaVersion:1,state:'SECRET355_STOCK_WT_COMPLETE_EXTERNAL_PARENT_ZERO_AND_INDEPENDENT_REVIEW_REQUIRED_V1',index,result},{json:true});await out.recheck();return {root:out.root,index,completion};
 }catch(error){try{await out.write('failure.json',{schemaVersion:1,state:'FAILED_SECRET355_STOCK_WT_NO_ACCEPTANCE_V1',thrownType:typeof error,completedSessions:sessions.length,partialEvidenceOnly:true,allRawFilesGuaranteed:false},{json:true});}catch{}throw error;}finally{await out.close();}
}
