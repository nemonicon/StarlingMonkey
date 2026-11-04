// Supported only as a fresh PARENT-AUDITED owned worker. No code runs on import.
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {realpath} from 'node:fs/promises';
import {descriptor,regular} from './authority.mjs';
import {DurableOutput} from './durable.mjs';
import {need} from './transport.mjs';
import {loadReviewedSession} from './loading.mjs';
import {parseOracleBytes} from './oracle-data.mjs';
import {Collector} from './collector.mjs';
import {executePrimary,executeGuestEdge} from './execution.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const NODE={path:'/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256:'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes:108619024};
export function jobModel(job){need(job&&['retained-primary','fresh-primary','main-crossdecode','off-guest-crossdecode'].includes(job.kind)&&['native-on','fflate-on','fflate-off'].includes(job.arm),'Finite concrete correctness job');
 if(job.kind==='retained-primary')need(job.rotations===3&&JSON.stringify(job.caseIds)===JSON.stringify(Array.from({length:30},(_,i)=>i)),'Exactly30cases times3 retained rotations');
 else if(job.kind==='fresh-primary')need(Number.isInteger(job.caseId)&&job.caseId>=0&&job.caseId<30&&job.rotations===1,'Fresh exact primary case');
 else need(job.stream&&Number.isInteger(job.stream.caseId)&&job.stream.caseId>=0&&job.stream.caseId<30&&job.stream.kind==='codec-cost-stage-v1'&&['node-22.14.0','native-on','fflate-on'].includes(job.stream.provider)&&(job.kind==='off-guest-crossdecode'?job.arm==='fflate-off':['native-on','fflate-on'].includes(job.arm)),'One exact main or separately scoped off staged guest edge');
 return true;
}
export async function runWorker(input){
 const source=descriptor(input),raw=await regular(source,{maxBytes:4*1024*1024}),value=JSON.parse(raw);need(value.schemaVersion===1&&value.state==='PARENT_AUDITED_ZLIB_COST_JCO_WORKER_V2'&&value.parentAuditedActualComponents===true,'Parent-audited worker, not standalone admission');
 need(process.version==='v22.14.0'&&process.execArgv.length===0&&await realpath(process.execPath)===NODE.path&&!process.env.NODE_OPTIONS&&!process.env.NODE_PATH,'Pinned plain Node process');for(const key of Object.keys(process.env))need(!key.startsWith('NAPI_RS_'),'No native-binding override');await regular(NODE,{maxBytes:128*1024*1024});
 need(Array.isArray(value.criticalFiles)&&value.criticalFiles.length>0&&value.criticalFiles.length<=1024,'Finite critical worker source tuple');const critical=Object.freeze(value.criticalFiles.map(descriptor));for(const row of critical)await regular(row,{maxBytes:64*1024*1024});jobModel(value.job);
 const outputRoot=value.outputRoot;need(outputRoot===value.parentOutputRoot+'/jobs/'+value.jobName&&/^[a-z0-9-]+$/.test(value.jobName),'Exact parent-owned fresh job destination');
 const oracleRow=descriptor(value.oracle),oracleBytes=await regular(oracleRow),caseRow=descriptor(value.cases),cases=JSON.parse(await regular(caseRow));const data=parseOracleBytes(oracleBytes,oracleRow.sha256,cases);
 if(value.job.stream)new Collector({arm:value.job.arm,oracleSha256:data.oracleSha256,cases:data.cases,nodeInputs:data.nodeInputs,rawFixtures:data.rawFixtures,write:async()=>{throw new Error('No retention during pre-call stream data validation');}}).stream(value.job.stream,value.job.stream.caseId);
 const artifact=Object.freeze({...value.artifact,parentAuditedActualComponent:true});
 const recheck=async()=>{await regular(source,{maxBytes:4*1024*1024});for(const r of critical)await regular(r,{maxBytes:64*1024*1024});await regular(oracleRow);await regular(caseRow);};await recheck();
 const output=await DurableOutput.create(outputRoot);let session;
 try{
  const write=(path,data)=>output.write(path,data,{json:true});await write('started.json',{schemaVersion:1,job:value.job,component:artifact.component,sourceIndexSha256:value.correctnessSourceIndexSha256,componentSourceIndexSha256:value.componentSourceIndexSha256,partial:true});
  session=await loadReviewedSession(artifact);const common={session,write,arm:value.job.arm,oracleSha256:data.oracleSha256,cases:data.cases,nodeInputs:data.nodeInputs,rawFixtures:data.rawFixtures,prefix:'call'};
  const result=value.job.kind==='retained-primary'?await executePrimary({...common,caseIds:value.job.caseIds,rotations:3}):value.job.kind==='fresh-primary'?await executePrimary({...common,caseIds:[value.job.caseId],rotations:1}):await executeGuestEdge({...common,stream:value.job.stream});
  await session.recheck();await recheck();await output.recheck();
  const results=await write('results.json',{schemaVersion:1,state:'UNTIMED_ZLIB_COST_JCO_JOB_COMPLETE_UNREVIEWED_V2',job:value.job,jobName:value.jobName,correctnessSourceIndexSha256:value.correctnessSourceIndexSha256,componentSourceIndexSha256:value.componentSourceIndexSha256,component:artifact.component,generatedModuleImported:true,initializationCompletedByModuleTLA:true,externalWasiImports:[],observed:result,resetOrCrossProcessReuseProved:false,timing:false});
  const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]});const completion=await write('completion.json',{schemaVersion:1,state:'JCO_CORRECTNESS_JOB_COMPLETE_EXTERNAL_OWNED_EXIT_ZERO_REQUIRED',results,index,sourceIndexSha256:value.correctnessSourceIndexSha256,componentSha256:artifact.component.sha256,timing:false});await output.recheck();return{index,completion};
 }catch(error){let postFailureCriticalFilesAuditPassed=false;try{if(session)await session.recheck();await recheck();postFailureCriticalFilesAuditPassed=true;}catch{}try{await output.write('failure.json',{schemaVersion:1,state:'UNTIMED_JCO_JOB_FAILED_NOT_ACCEPTED',thrownType:typeof error,partialRawRecordsRetained:true,postFailureCriticalFilesAuditPassed,timing:false},{json:true});}catch{}throw error;}
 finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact worker descriptor tuple');process.stdout.write(JSON.stringify(await runWorker(JSON.parse(process.argv[2])))+'\n');}
