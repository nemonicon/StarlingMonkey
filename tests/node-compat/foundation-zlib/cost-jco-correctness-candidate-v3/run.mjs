// Separate finite untimed correctness action. Import creates no output/process.
import {dirname,join,relative,resolve,isAbsolute} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {mkdir,lstat,readdir,readFile,statfs} from 'node:fs/promises';
import {correctnessPreflight,NODE,COMPONENT,TOOLING,GUEST} from './admission.mjs';
import {descriptor,regular,hash} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {need} from '../cost-jco-correctness-candidate-v2/transport.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {runOwnedCommand} from '../cost-jco-correctness-candidate-v2/durable-host.mjs';
import {primaryJobs,primaryStreams,offJobs} from '../cost-jco-correctness-candidate-v2/plan.mjs';
import {requireCoverage} from '../cost-jco-correctness-candidate-v2/coverage.mjs';
import {parseOracleBytes} from '../cost-jco-correctness-candidate-v2/oracle-data.mjs';
import {assertSameStream} from '../cost-jco-correctness-candidate-v2/scenarios.mjs';
import {executeFreshNodeEdges} from './node-edges.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),DONOR=join(HERE,'..','cost-jco-correctness-candidate-v2');
function childName(root,path){const name=relative(root,path);need(name&&!isAbsolute(name)&&!name.startsWith('../')&&!name.includes('\\')&&name.split('/').every(v=>v&&v!=='.'&&v!=='..'),'Bounded owned output name');return name;}
async function disk(minimum){const s=await statfs('/private/tmp/starling-node-compat');need(s.bavail*s.bsize>=minimum,'Operational disk guard; no space/recovery guarantee');}
async function collectJob(output,root,job,sourceSha,componentSha){
 const indexPath=join(root,'index.json'),completePath=join(root,'completion.json'),indexBytes=await readFile(indexPath),complete=JSON.parse(await readFile(completePath));need(complete.state==='JCO_CORRECTNESS_JOB_COMPLETE_EXTERNAL_OWNED_EXIT_ZERO_REQUIRED'&&complete.index.sha256===hash(indexBytes)&&complete.index.bytes===indexBytes.length&&complete.sourceIndexSha256===sourceSha&&complete.componentSha256===componentSha,'Exact actual child completion/index/source/component');
 const index=JSON.parse(indexBytes);need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=8192,'Bounded actual child file inventory');const seen=new Set();
 for(const row of index.files){const path=join(root,row.path),name=childName(root,path);need(!seen.has(name),'Unique child artifact');seen.add(name);await regular({path,sha256:row.sha256,bytes:row.bytes},{maxBytes:64*1024*1024});output.rows.set(childName(output.root,path),{path:childName(output.root,path),sha256:row.sha256,bytes:row.bytes});}
 for(const path of[indexPath,completePath]){const raw=await readFile(path);output.rows.set(childName(output.root,path),{path:childName(output.root,path),sha256:hash(raw),bytes:raw.length});}
 const resultsPath=join(root,'results.json'),resultRow=index.files.find(row=>row.path==='results.json');need(resultRow&&resultRow.sha256===complete.results.sha256&&resultRow.bytes===complete.results.bytes,'Exact actual indexed result');const result=JSON.parse(await regular({path:resultsPath,sha256:resultRow.sha256,bytes:resultRow.bytes}));
 need(result.state==='UNTIMED_ZLIB_COST_JCO_JOB_COMPLETE_UNREVIEWED_V2'&&result.correctnessSourceIndexSha256===sourceSha&&result.componentSourceIndexSha256===COMPONENT&&result.component.sha256===componentSha&&JSON.stringify(result.job)===JSON.stringify(job)&&result.generatedModuleImported===true&&result.initializationCompletedByModuleTLA===true&&JSON.stringify(result.externalWasiImports)==='[]'&&result.timing===false,'Exact actual worker result identity/source/job, not previous partial');
 return{data:result,row:{path:resultsPath,sha256:resultRow.sha256,bytes:resultRow.bytes},completion:{path:completePath,sha256:hash(await readFile(completePath)),bytes:(await lstat(completePath)).size}};
}
export async function runCorrectness(options){
 const admitted=await correctnessPreflight(options); // NULL/proofs fail BEFORE output
 const casesRow=descriptor(admitted.criticalSourceFiles.find(row=>row.path===join(DONOR,'cases.json'))),cases=JSON.parse(await regular(casesRow)),oracleBytes=await regular(admitted.oracle),data=parseOracleBytes(oracleBytes,admitted.oracle.sha256,cases);
 await disk(2*1024**3);await admitted.recheck();const output=await DurableOutput.create(admitted.outputRoot),primary=[],mainEdges=[],offEncodings=[],offNodeEdges=[],offGuestEdges=[],origins=[],streams=new Map();
 const write=(path,value)=>output.write(path,value,{json:true}),writeBytes=(path,value)=>output.write(path,value);
 const checkOwned=(await import('../cost-jco-correctness-candidate-v2/glue-policy.mjs')).checkOwnedTerminal;
 try{
  await mkdir(join(output.root,'jobs'),{mode:0o700});await mkdir(join(output.root,'processes'),{mode:0o700});
  const criticalFiles=[...admitted.criticalSourceFiles,admitted.rootAction];
  async function run(job,name){
   await disk(800*1024**2);const artifact=admitted.frames[job.arm].artifact;
   const value={schemaVersion:1,state:'PARENT_AUDITED_ZLIB_COST_JCO_WORKER_V2',parentAuditedActualComponents:true,correctnessSourceIndexSha256:admitted.sourceSha,componentSourceIndexSha256:COMPONENT,parentOutputRoot:output.root,outputRoot:join(output.root,'jobs',name),jobName:name,job,artifact,oracle:admitted.oracle,cases:casesRow,criticalFiles};
   const row=await write('descriptors/'+name+'.json',value);need(row.bytes<=4*1024*1024,'Finite worker descriptor file, never a giant CLI argument');const d={path:join(output.root,row.path),sha256:row.sha256,bytes:row.bytes},registered=new Set();
   const status=await runOwnedCommand({output:output.root,name,executable:NODE.path,args:[join(DONOR,'worker.mjs'),JSON.stringify(d)],write:(path,data)=>output.write(childName(output.root,path),data),register:path=>registered.add(path),timeoutMs:600000,maxOutputBytes:16*1024*1024,onProgress:event=>process.stdout.write(JSON.stringify({event:'untimed-correctness-operational-heartbeat',...event})+'\n')});
   // All raw pipes/terminal are persisted before any success assertion.
   for(const path of registered){const raw=await readFile(path),name=childName(output.root,path);output.rows.set(name,{path:name,sha256:hash(raw),bytes:raw.length});}
   checkOwned(status);const collected=await collectJob(output,value.outputRoot,job,admitted.sourceSha,artifact.component.sha256);origins.push({job,workerResults:collected.row,workerCompletion:collected.completion,ownedTerminal:status.terminalPath,ownedRawExitCode:0,component:artifact.component,actualFreshOwnedProcess:true});return collected.data.observed;
  }
  for(const job of primaryJobs()){
   const name=job.kind==='retained-primary'?'retained-'+job.arm:'fresh-'+job.arm+'-'+String(job.caseId).padStart(2,'0'),result=await run(job,name);
   need(result.arm===job.arm&&result.records.length===(job.kind==='retained-primary'?90:1),'Whole actual primary job count');
   for(const row of result.records)primary.push({...row,kind:job.kind});
   for(const stream of result.streams){const old=streams.get(stream.streamId);if(old)await assertSameStream(write,'compare-'+name+'-'+stream.fixture+'-'+stream.format,stream,old);else{need(job.kind==='retained-primary','First actual encoder stream originates in retained full case proof');streams.set(stream.streamId,stream);}}
  }
  const primarySet=new Map(data.nodeInputs.map(row=>[row.streamId,row]));for(const stream of streams.values())if(stream.provider!=='fflate-off')primarySet.set(stream.streamId,stream);
  const expectedStreams=primaryStreams();need(primarySet.size===45&&expectedStreams.every(row=>primarySet.has(row.streamId)),'Actual full45 Node/native/FFON streams captured before matrix');
  for(const stream of streams.values())if(stream.provider==='fflate-off'){const on=streams.get('fflate-on.'+stream.fixture+'.'+stream.format);need(on,'Actual separate FFON encoding exists');await assertSameStream(write,'off-vs-on-'+stream.fixture+'-'+stream.format,stream,on);offEncodings.push({provider:'fflate-off',fixture:stream.fixture,format:stream.format,streamId:stream.streamId,fullBytesComparedWith:on.streamId});}
  await write('actual-encoder-streams.json',{primary:[...primarySet.values()],off:[...streams.values()].filter(row=>row.provider==='fflate-off'),origins:origins.map(row=>({job:row.job,workerResults:row.workerResults,component:row.component}))});
  // Import genuine existing HOST Node audit API only after the full current
  // authority/source/native/artifact chain passed. This is not a guest fallback.
  await admitted.recheck();const nativeFrame=admitted.frames['native-on'].frame;for(const name of['node-oracle.mjs','node-transport.mjs','contract.mjs','framing.mjs','fixtures.mjs','cases.generated.mjs'])await nativeFrame.checkGuestFile(join(nativeFrame.guestRoot,name));
  const {decodeNodeStream}=await import(pathToFileURL(join(nativeFrame.guestRoot,'node-oracle.mjs')).href),nodeZlib=await import('node:zlib'),{Buffer}=await import('node:buffer');
  const sourceBinding={proposalIndexSha256:'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8',protocolDecisionSha256:'0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6',nodeExecutableSha256:NODE.sha256,guestSourceIndexSha256:GUEST,costToolingIndexSha256:TOOLING,rootActionAuthoritySha256:admitted.rootAction.sha256};
  const ordered=expectedStreams.map(row=>primarySet.get(row.streamId)),nodeRows=await executeFreshNodeEdges({streams:ordered,decodeNodeStream,Buffer,nodeZlib,sourceBinding,rawFixtures:data.rawFixtures,write,writeBytes,prefix:'node-main'});mainEdges.push(...nodeRows);
  const offStreams=offJobs().encoding.map(row=>streams.get('fflate-off.'+row.fixture+'.'+row.format));need(offStreams.every(Boolean),'All15 actual off streams');offNodeEdges.push(...await executeFreshNodeEdges({streams:offStreams,decodeNodeStream,Buffer,nodeZlib,sourceBinding,rawFixtures:data.rawFixtures,write,writeBytes,prefix:'node-off'}));
  for(const arm of['native-on','fflate-on','fflate-off'])for(let index=0;index<ordered.length;index++){
   const stream=ordered[index],kind=arm==='fflate-off'?'off-guest-crossdecode':'main-crossdecode',result=await run({kind,arm,stream},'edge-'+arm+'-'+String(index).padStart(2,'0'));need(result.decoder===arm&&result.streamId===stream.streamId&&result.provider===stream.provider&&result.fullRawFixtureEqual===true,'Actual guest edge identity');(arm==='fflate-off'?offGuestEdges:mainEdges).push(result);
  }
  const coverage=requireCoverage({primary,mainEdges,offEncodings,offNodeEdges,offGuestEdges});await admitted.recheck();await output.recheck();
  const result=await write('results.json',{schemaVersion:1,state:'UNTIMED_ZLIB_COST_JCO_CORRECTNESS_COMPLETE_PENDING_INDEPENDENT_REVIEW_V3',correctnessSourceIndexSha256:admitted.sourceSha,componentSourceIndexSha256:COMPONENT,toolingSourceIndexSha256:TOOLING,guestSourceIndexSha256:GUEST,rootAction:admitted.rootAction,oracle:admitted.oracle,components:Object.fromEntries(Object.entries(admitted.frames).map(([arm,v])=>[arm,v.artifact.component])),coverage,primary,mainEdges,offEncodings,offNodeEdges,offGuestEdges,origins,allNewOwnedWorkersCompletedZero:true,wasmtimeExecuted:false,pilotOrTimingExecuted:false,metadataProjection:false,operationalAdmission:false,runtimeAcceptanceClaim:false});
  const index=await write('index.json',{schemaVersion:1,files:[...output.rows.values()]});const completion=await write('completion.json',{schemaVersion:1,state:'UNTIMED_JCO_CORRECTNESS_COMPLETE_EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED_V3',results:result,index,sourceIndexSha256:admitted.sourceSha,timingAllowed:false,operationalAdmission:false});await output.recheck();return{index,completion};
 }catch(error){let postFailureSourceAuditPassed=false;try{await admitted.recheck();postFailureSourceAuditPassed=true;}catch{}try{await write('failure.json',{schemaVersion:1,state:'UNTIMED_JCO_CORRECTNESS_FAILED_NOT_ACCEPTED_V3',thrownType:typeof error,fullPartialRawOutputsRetained:true,completedJobOrigins:origins,postFailureSourceAuditPassed,timingAllowed:false,operationalAdmission:false});}catch{}throw error;}
 finally{await output.close();}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){need(process.argv.length===3,'One exact external Root config descriptor');const options=JSON.parse(await regular(JSON.parse(process.argv[2])));process.stdout.write(JSON.stringify(await runCorrectness(options))+'\n');}
