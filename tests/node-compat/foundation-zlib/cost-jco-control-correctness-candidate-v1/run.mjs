// New explicit control action only. No action runs when this source is imported.
import {dirname,join,relative,isAbsolute,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {mkdir,readFile,statfs} from 'node:fs/promises';
import {descriptor,regular,hash} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {need} from '../cost-jco-correctness-candidate-v2/transport.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {runOwnedCommand} from '../cost-jco-correctness-candidate-v2/durable-host.mjs';
import {controlPreflight,NODE,ARMS,COMPONENT,PRIOR_SOURCE,PRIOR_REVIEW,CONTRACT} from './admission.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
function child(root,path){const name=relative(root,path);need(name&&!isAbsolute(name)&&!name.startsWith('../')&&!name.includes('\\')&&name.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Bounded owned name');return name;}
async function disk(bytes){const s=await statfs('/private/tmp/starling-node-compat');need(s.bavail*s.bsize>=bytes,'Operational2GiB/800MiB disk guard, no space guarantee');}
export async function runControls(options){
 const admitted=await controlPreflight(options); // new NULL authority refuses BEFORE output/loaders
 await disk(2*1024**3);await admitted.recheck();const output=await DurableOutput.create(admitted.outputRoot),origins=[];
 const write=(name,value)=>output.write(name,value,{json:true});
 try{
  await mkdir(join(output.root,'jobs'),{mode:0o700});const checkOwned=(await import('../cost-jco-correctness-candidate-v2/glue-policy.mjs')).checkOwnedTerminal;
  const cases=admitted.criticalFiles.find(r=>r.path===join(HERE,'..','cost-jco-correctness-candidate-v2/cases.json'));need(cases,'Exact indexed original30-case source');
  for(const arm of ARMS){
   await disk(800*1024**2);const artifact=admitted.frames[arm].artifact,value={schemaVersion:1,state:'PARENT_AUDITED_UNTIMED_ZLIB_CONTROL_WORKER_V1',parentAuditedActualComponents:true,controlSourceIndexSha256:admitted.sourceSha,componentSourceIndexSha256:COMPONENT,parentOutputRoot:output.root,outputRoot:join(output.root,'jobs',arm),arm,artifact,oracle:admitted.oracle,cases,criticalFiles:admitted.criticalFiles};
   const row=await write('descriptors/'+arm+'.json',value),input=descriptor({path:join(output.root,row.path),sha256:row.sha256,bytes:row.bytes}),registered=new Set();need(row.bytes<=1024*1024,'Small worker descriptor file, never giant CLI payload');
   const status=await runOwnedCommand({output:output.root,name:arm,executable:NODE.path,args:[join(HERE,'worker.mjs'),JSON.stringify(input)],write:(path,data)=>output.write(child(output.root,path),data),register:path=>registered.add(path),timeoutMs:600000,maxOutputBytes:16*1024*1024,onProgress:event=>process.stdout.write(JSON.stringify({event:'untimed-control-operational-heartbeat',...event})+'\n')});
   for(const path of registered){const raw=await readFile(path),name=child(output.root,path);output.rows.set(name,{path:name,sha256:hash(raw),bytes:raw.length});}checkOwned(status); // durable terminal/pipes before assertions
   const workerRoot=value.outputRoot,indexBytes=await readFile(join(workerRoot,'index.json')),index=JSON.parse(indexBytes),completeBytes=await readFile(join(workerRoot,'completion.json')),complete=JSON.parse(completeBytes);need(complete.state==='CONTROL_ARM_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1'&&complete.index.sha256===hash(indexBytes)&&complete.sourceIndexSha256===admitted.sourceSha&&complete.component.sha256===artifact.component.sha256,'Actual new worker completion/source/component');
   need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=4096,'Finite actual arm inventory');const names=new Set();for(const item of index.files){const path=join(workerRoot,item.path),local=child(workerRoot,path),name=child(output.root,path);need(local===item.path&&!names.has(local),'Unique exact arm-local row; no aliases or other-worker reuse');names.add(local);await regular({path,sha256:item.sha256,bytes:item.bytes},{maxBytes:64*1024*1024});output.rows.set(name,{path:name,sha256:item.sha256,bytes:item.bytes});}
   for(const[name,raw]of[['index.json',indexBytes],['completion.json',completeBytes]])output.rows.set(child(output.root,join(workerRoot,name)),{path:child(output.root,join(workerRoot,name)),sha256:hash(raw),bytes:raw.length});
   const rr=index.files.find(r=>r.path==='results.json');need(rr&&rr.sha256===complete.results.sha256&&rr.bytes===complete.results.bytes,'Actual indexed arm result');const result=JSON.parse(await regular({path:join(workerRoot,'results.json'),sha256:rr.sha256,bytes:rr.bytes}));
   need(result.state==='UNTIMED_ZLIB_JCO_CONTROL_ARM_COMPLETE_UNREVIEWED_V1'&&result.arm===arm&&result.controlSourceIndexSha256===admitted.sourceSha&&result.component.sha256===artifact.component.sha256&&result.records.length===242&&result.controlOperations===180&&result.codecCalls===0&&result.counts.publicFunctionEntries===242&&result.externalWasiImports.length===0&&result.timing===false,'Exact newly executed finite control arm');
   origins.push({arm,component:artifact.component,result:{path:join(workerRoot,'results.json'),sha256:rr.sha256,bytes:rr.bytes},completion:{path:join(workerRoot,'completion.json'),sha256:hash(completeBytes),bytes:completeBytes.length},ownedTerminal:status.terminalPath,rawOwnedExitCode:0,controlOperations:180,rawPrimitiveStringReturns:242});
  }
  await admitted.recheck();await output.recheck();const results=await write('results.json',{schemaVersion:1,state:'UNTIMED_ZLIB_JCO_CONTROLS_COMPLETE_PENDING_INDEPENDENT_REVIEW_V1',controlSourceIndexSha256:admitted.sourceSha,rootAction:admitted.rootAction,priorCorrectnessSourceIndexSha256:PRIOR_SOURCE,priorCorrectnessReviewIndexSha256:PRIOR_REVIEW,priorCorrectnessContractSha256:CONTRACT,priorControlOperations:0,origins,armSessions:3,setupCases:90,distinctControlCases:270,adjacentRepetitions:2,controlOperations:540,rawPrimitiveStringReturns:726,codecCalls:0,allNewOwnedWorkersRawZeroClean:true,timingAllowed:false,stockWasmtimeExecuted:false,pilotPrerequisitesSatisfied:false,operationalAdmission:false,runtimeAcceptanceClaim:false});
  const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]}),completion=await write('completion.json',{schemaVersion:1,state:'CONTROLS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED',results,index,sourceIndexSha256:admitted.sourceSha});await output.recheck();return{index,completion};
 }catch(error){let sourceAudit=false;try{await admitted.recheck();sourceAudit=true;}catch{}try{await write('failure.json',{schemaVersion:1,state:'CONTROL_ACTION_FAILED_NOT_ACCEPTED',thrownType:typeof error,partialRawOutputsRetained:true,completedOrigins:origins,postFailureSourceAuditPassed:sourceAudit,timingAllowed:false});}catch{}throw error;}
 finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact new Root config descriptor');const options=JSON.parse(await regular(JSON.parse(process.argv[2])));process.stdout.write(JSON.stringify(await runControls(options))+'\n');}
