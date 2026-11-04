// Private PARENT-AUDITED child. No worker/guest action happens on import.
import {resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {realpath} from 'node:fs/promises';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {need,observedCall} from '../cost-jco-correctness-candidate-v2/transport.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {parseOracleBytes} from '../cost-jco-correctness-candidate-v2/oracle-data.mjs';
import {NODE} from './admission.mjs';
import {loadControlSession} from './loading.mjs';
import {Collector} from './collector.mjs';
export const EXPECTED=Object.freeze({identity:2,setup:30,batch:180,checkpoint:30,observe:0,stage:0,validate:0,publicFunctionEntries:242,codecCalls:0,controlOperations:180});
export async function runControlWorker(input){
 const descriptorRow=descriptor(input),raw=await regular(descriptorRow,{maxBytes:1024*1024}),v=JSON.parse(raw);need(v.schemaVersion===1&&v.state==='PARENT_AUDITED_UNTIMED_ZLIB_CONTROL_WORKER_V1'&&v.parentAuditedActualComponents===true&&['native-on','fflate-on','fflate-off'].includes(v.arm),'Exact private parent-audited control descriptor');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===NODE.path&&!process.env.NODE_OPTIONS&&!process.env.NODE_PATH,'Pinned plain child Node');for(const key of Object.keys(process.env))need(!key.startsWith('NAPI_RS_'),'No native-binding override');await regular(NODE,{maxBytes:128*1024*1024});
 need(v.outputRoot===v.parentOutputRoot+'/jobs/'+v.arm,'Only exact parent-owned fresh arm root');need(Array.isArray(v.criticalFiles)&&v.criticalFiles.length>0&&v.criticalFiles.length<=1024,'Finite actual critical source tuple');const critical=Object.freeze(v.criticalFiles.map(descriptor));
 const oracle=descriptor(v.oracle),casesRow=descriptor(v.cases),recheck=async()=>{await regular(descriptorRow);for(const row of critical)await regular(row,{maxBytes:64*1024*1024});await regular(oracle);await regular(casesRow);};await recheck();
 const data=parseOracleBytes(await regular(oracle),oracle.sha256,JSON.parse(await regular(casesRow))),output=await DurableOutput.create(v.outputRoot);let session;
 try{
  const write=(name,value)=>output.write(name,value,{json:true}),collector=new Collector({arm:v.arm,oracleSha256:data.oracleSha256,cases:data.cases,nodeInputs:data.nodeInputs,rawFixtures:data.rawFixtures,write}),records=[];let sequence=0;
  await write('started.json',{schemaVersion:1,arm:v.arm,sourceIndexSha256:v.controlSourceIndexSha256,component:v.artifact.component,partial:true,codecAllowed:false});session=await loadControlSession(v.artifact);
  async function call(exportName,args,label){const name=String(sequence++).padStart(4,'0')+'-'+label;const result=await observedCall({invoke:session.invoke,write,name,exportName,args});return{value:result.value,raw:result.raw,label,exportName,args};}
  const before=await call('identity',[],'identity-before');await collector.identity(before.value,before.label);records.push(before);
  for(let index=0;index<30;index++){
   const setup=await call('setup',[index],'setup-'+index);await collector.setup(setup.value,index,setup.label);records.push(setup);
   for(const base of[30,60,90])for(let repeat=0;repeat<2;repeat++){const id=base+index,result=await call('batch',[id,1],'control-'+id+'-repeat-'+repeat);await collector.control(result.value,id,result.label);records.push({...result,primaryCaseId:index,controlId:id,repeat});}
   const checkpoint=await call('checkpoint',[],'checkpoint-'+index);await collector.checkpoint(checkpoint.value,checkpoint.label);records.push(checkpoint);
  }
  const after=await call('identity',[],'identity-after');await collector.identity(after.value,after.label);records.push(after);
  const counts=collector.counters();need(sequence===242&&records.length===242&&counts.publicFunctionEntries===242&&counts.codecCalls===0&&counts.controlOperations===180,'Exact actual control-only coverage/counters');for(const name of['identity','setup','batch','checkpoint','observe','stage','validate'])need(counts.perExportEntries[name]===EXPECTED[name],'Exact actual named-entry count '+name);
  await session.recheck();await recheck();await output.recheck();const results=await write('results.json',{schemaVersion:1,state:'UNTIMED_ZLIB_JCO_CONTROL_ARM_COMPLETE_UNREVIEWED_V1',arm:v.arm,controlSourceIndexSha256:v.controlSourceIndexSha256,component:v.artifact.component,records,counts,controlCases:90,adjacentRepetitions:2,controlOperations:180,codecCalls:0,generatedModuleImported:true,initializationCompletedByModuleTLA:true,externalWasiImports:[],checkpointInputProof:'reported full-input FNV and sentinels; no independent guest-heap byte read',internalCopyOwnershipInspected:false,emptyInputIsolationClaim:false,timing:false});
  const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]}),completion=await write('completion.json',{schemaVersion:1,state:'CONTROL_ARM_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1',results,index,sourceIndexSha256:v.controlSourceIndexSha256,component:v.artifact.component});await output.recheck();return{index,completion};
 }catch(error){let sourceAudit=false;try{if(session)await session.recheck();await recheck();sourceAudit=true;}catch{}try{await output.write('failure.json',{schemaVersion:1,state:'CONTROL_ARM_FAILED_UNACCEPTED',thrownType:typeof error,fullPartialRawRetained:true,postFailureSourceAuditPassed:sourceAudit,codecAllowed:false},{json:true});}catch{}throw error;}
 finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact private parent descriptor');process.stdout.write(JSON.stringify(await runControlWorker(JSON.parse(process.argv[2])))+'\n');}
