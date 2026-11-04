// Future ROOT-approved timing only. No execution during source preparation.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,statfs} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {performance} from 'node:perf_hooks';
import {cpus,platform,arch,release,totalmem} from 'node:os';
import {selectTimingPhase} from './phase.mjs';
import {cases,comparisons,protocol,orderFor,measurementCaseIndices,chooseBatch} from './protocol.mjs';
import {loadCompiled} from './instantiate.mjs';
import {compactExpected} from './compact-oracle.mjs';
import {collectWorker} from './collect-worker.mjs';
import {executionPreflight} from './runtime-preflight.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
assert.equal(process.env.NODE_COMPAT_COMMON_BYTE_TIMING_APPROVED,'1','Separate Root timing window required');
const calibration=process.argv[2]==='--calibrate',worker=process.argv[2]==='--worker'||calibration,offset=worker?3:2;
const [ownSha,phasePath,phaseSha]=process.argv.slice(offset,offset+3);assert(/^[0-9a-f]{64}$/.test(ownSha??'')&&/^[0-9a-f]{64}$/.test(phaseSha??''));assert(phasePath&&resolve(phasePath)===phasePath);
const sourceIndexRaw=await readFile(join(here,'index.json'));assert.equal(hash(sourceIndexRaw),ownSha);const sourceIndex=JSON.parse(sourceIndexRaw);
for(const row of sourceIndex.files){const raw=await readFile(join(here,row.path));assert.equal(hash(raw),row.sha256);assert.equal(raw.length,row.bytes);}
const phaseRaw=await readFile(phasePath);assert.equal(hash(phaseRaw),phaseSha);const phase=selectTimingPhase(JSON.parse(phaseRaw));assert.equal(phase.sourceFamilyIndexSha256,ownSha);
async function auditPhase(){assert.equal(hash(await readFile(phasePath)),phaseSha);assert.equal(hash(await readFile(join(here,'index.json'))),ownSha);
 for(const name of ['actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts']){const row=phase[name];assert.equal(hash(await readFile(row.reportPath)),row.reportSha256);const raw=await readFile(row.rootReviewPath);assert.equal(hash(raw),row.rootReviewSha256);const review=JSON.parse(raw);assert.equal(review.state,'ROOT_REVIEWED_COMMON_BYTE_PREREQUISITE_V1');assert.equal(review.prerequisite,name);assert.equal(review.reportSha256,row.reportSha256);assert.equal(review.pairPinsSha256,phase.pairPinsSha256);assert.equal(review.sourceContractVersion,'sm-classic-trace-source-v1');assert.equal(review.reviewedPassed,true);assert.equal(review.performanceClaim,false);}
 for(const row of Object.values(phase.components)){assert.equal(hash(await readFile(row.componentPath)),row.componentSha256);assert.equal(hash(await readFile(row.enginePath)),row.engineSha256);for(const file of row.transpiledFiles){const raw=await readFile(join(dirname(row.modulePath),file.name));assert.equal(hash(raw),file.sha256);assert.equal(raw.length,file.bytes);}}
}
await auditPhase();
const correctness=JSON.parse(await readFile(phase.actualCorrectness.reportPath));assert.equal(correctness.state,'ACTUAL_COMMON_BYTE_FOUR_ARM_CORRECTNESS_PASSED');assert.equal(correctness.sourceFamilyIndexSha256,ownSha);assert.equal(correctness.pairPinsSha256,phase.pairPinsSha256);assert.equal(correctness.records.length,4);
for(const record of correctness.records){const row=phase.components[record.arm];for(const key of ['componentPath','componentSha256','componentBytes','enginePath','engineSha256','modulePath','bundleSha256'])assert.equal(row[key],record[key]);assert.deepEqual(row.transpiledFiles,record.transpiledFiles);assert.deepEqual(row.coreFiles,record.coreFiles);assert.deepEqual(row.identity,record.identity);assert.deepEqual(row.checkpointProbe,record.checkpointProbe);assert.equal(record.correctnessPassed,true);assert.equal(record.identityPassed,true);assert.equal(record.checkpointProbePassed,true);}
const full=JSON.parse(await readFile(phase.freshFull20And14.reportPath));assert.equal(full.status,'ACTUAL_CLASSIC_DIAGNOSTIC_20_WORKLOAD_14_BOUNDARY_CORRECTNESS_PASSED');assert.equal(full.workloadCases,20);assert.equal(full.boundaryCases,14);assert.equal(full.engineSha256,phase.components['native-on'].engineSha256);assert.deepEqual(full.interfaceAudit.emittedImports,[]);
const oracle=[...JSON.parse(await readFile(join(here,'node-common-oracle.json'))).cases,...JSON.parse(await readFile(join(here,'node-control-oracle.json'))).cases];assert.equal(oracle.length,14);
function exact(raw,index,iterations){const value=JSON.parse(raw);assert.equal(JSON.stringify(value),JSON.stringify(compactExpected(oracle,index,iterations)),'Compact batch checksum/unit/callback contract');}
if(worker){
 const arm=process.argv[offset+3],index=Number(process.argv[offset+4]);assert(phase.components[arm]&&cases[index]);
 const record=phase.components[arm],scenario=cases[index],iterations=calibration?1:Number(process.argv[offset+5]);assert(Number.isInteger(iterations)&&iterations>=1&&iterations<=scenario.iterations);
 const progress=(stage,call)=>process.stderr.write(JSON.stringify({arm,index,iterations,stage,call})+'\n');progress('compile',0);
 const rss=()=>process.memoryUsage().rss,initialRssBytes=rss();
 const compileStart=performance.now(),instantiate=await loadCompiled(record),compileAndBindingLoadMs=performance.now()-compileStart,compiledRssBytes=rss();
 const instantiateStart=performance.now(),instance=await instantiate(),instantiateMs=performance.now()-instantiateStart;
 const firstExportStart=performance.now(),identity=JSON.parse(await instance.exports.identity()),firstIdentityExportMs=performance.now()-firstExportStart;assert.equal(JSON.stringify(identity),JSON.stringify(record.identity));
 const checkpointProbe=JSON.parse(await instance.exports.checkpointProbe());assert.equal(JSON.stringify(checkpointProbe),JSON.stringify(record.checkpointProbe));
 const setupStart=performance.now();assert.equal(await instance.exports.setup(index),oracle[index].setup);const setupMs=performance.now()-setupStart;
 const observations=[],observe=label=>observations.push({label,processRssBytes:rss()});observe('ready');
 const invoke=()=>instance.exports.batch(index,iterations);progress(calibration?'calibration-one-iteration':'first-batch',1);
 const firstStart=performance.now(),first=await invoke(),firstBatchMs=performance.now()-firstStart;exact(first,index,iterations);observe('first-batch');progress('first-complete',1);
 const batchMs=[];if(!calibration){for(let i=0;i<3;i++){progress('warmup',i+1);exact(await invoke(),index,iterations);}observe('warmed');
 for(let sample=0;sample<7;sample++){progress('timed-sample',sample+1);const start=performance.now(),value=await invoke(),elapsed=performance.now()-start;exact(value,index,iterations);batchMs.push(elapsed);observe('sample-'+sample);}}
 const afterCheckpointProbe=JSON.parse(await instance.exports.checkpointProbe());assert.equal(JSON.stringify(afterCheckpointProbe),JSON.stringify(checkpointProbe));
 await auditPhase();console.log(JSON.stringify({arm,index,scenario,iterations,calibration,initialRssBytes,compiledRssBytes,compileAndBindingLoadMs,instantiateMs,firstIdentityExportMs,setupMs,firstBatchMs,batchMs,observations,identity,checkpointProbe,afterCheckpointProbe,
  peakProcessRssKilobytes:process.resourceUsage().maxRSS,componentBytes:record.componentBytes,unitsPerBatch:compactExpected(oracle,index,iterations).result.totalUnits,
  capacityBytes:null,growCount:null,requestedMemoryHostLimitBytes:null,memoryScope:'Public process RSS only. Current scalar world/benchmark module supplies no capacity API; no private core exports or guest bytes inspected. No heap ownership claim.'}));
}else{
 const on=await executionPreflight({variant:'benchmark-classic-on'}),off=await executionPreflight({variant:'benchmark-classic-off'});assert.equal(on.pairSha256,phase.pairPinsSha256);
 for(const arm of ['native-on','canonical-on','stock-on'])assert.equal(phase.components[arm].engineSha256,on.pin.engineSha256);assert.equal(phase.components['canonical-off'].engineSha256,off.pin.engineSha256);
 const output=resolve(process.env.NODE_COMPAT_COMMON_BYTE_MEASUREMENT_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
 try{await lstat(output);assert.fail('Fresh timing output required');}catch(error){if(error.code!=='ENOENT')throw error;}
 const disk=await statfs(dirname(output));assert(disk.bavail*disk.bsize>=2*1024**3,'2GiB initial guard retained');await mkdir(output,{recursive:false});
 await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),phaseSha256:phaseSha,sourceIndexSha256:ownSha,protocol})+'\n',{flag:'wx'});
 const samples=[],calibrations=[];let failure=null;
 async function child(mode,comparison,index,arm,iterations,label){
  const available=await statfs(output);assert(available.bavail*available.bsize>=800*1024**2,'Stop creating artifacts below800MiB');
  process.stderr.write(JSON.stringify({comparison:comparison.id,index,arm,iterations,stage:mode,label})+'\n');
  const result=await collectWorker(fileURLToPath(import.meta.url),[mode,ownSha,phasePath,phaseSha,arm,String(index),String(iterations)],join(output,label));
   assert.equal(result.status,0,result.error??result.signal);assert.equal(result.error,null,'Worker capture evidence incomplete');const row=JSON.parse(result.stdout);assert.equal(row.arm,arm);assert.equal(row.index,index);return{...row,wholeProcessElapsedMs:result.wholeProcessElapsedMs};
 }
 try{
  for(const comparison of comparisons)for(const index of measurementCaseIndices){
   const pilots=[];for(const arm of comparison.arms){const row=await child('--calibrate',comparison,index-1,arm,1,comparison.id+'.case-'+index+'.calibration.'+arm);assert.equal(row.batchMs.length,0);pilots.push(row);}
   const iterations=chooseBatch(pilots[0].firstBatchMs,pilots[1].firstBatchMs);calibrations.push({comparison:comparison.id,caseIndex:index,requestedMaximum:16,chosenIterations:iterations,targetBatchMs:25,pilots});
   for(let repetition=0;repetition<3;repetition++)for(const arm of orderFor(repetition,comparison.arms)){
    const label=comparison.id+'.case-'+index+'.rep-'+repetition+'.'+arm;
    const row=await child('--worker',comparison,index,arm,iterations,label);assert.equal(row.batchMs.length,7);assert.equal(row.iterations,iterations);
    samples.push({comparison:comparison.id,repetition,caseIndex:index,runOrder:orderFor(repetition,comparison.arms),...row});
   }
  }
 }catch(error){failure=error;}finally{
  try{await auditPhase();await on.recheck();await off.recheck();}catch(error){failure??=error;}
  await writeFile(join(output,'terminal-source-audit.json'),JSON.stringify({phaseSha256:phaseSha,sourceIndexSha256:ownSha,successfulTimedWorkers:samples.length,expectedTimedWorkers:126,completedCalibrationPairs:calibrations.length,expectedCalibrationWorkers:42,passed:failure===null,error:failure?{name:failure.name,message:failure.message}:null},null,2)+'\n',{flag:'wx'});
 }
 if(failure)throw failure;assert.equal(samples.length,126);assert.equal(calibrations.length,21);
 const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
 const summaries=comparisons.flatMap(comparison=>measurementCaseIndices.map(index=>({comparison:comparison.id,caseIndex:index,scenario:cases[index],arms:comparison.arms.map(arm=>{
  const rows=samples.filter(row=>row.comparison===comparison.id&&row.caseIndex===index&&row.arm===arm),processMedians=rows.map(row=>median(row.batchMs));assert.equal(rows.length,3);
  return{arm,chosenIterations:rows[0].iterations,processMedians,medianOfProcessMediansMs:median(processMedians),bytesPerSecondPerProcess:rows.map((row,i)=>row.unitsPerBatch*1000/processMedians[i]),iterationOperationsPerSecondPerProcess:rows.map((row,i)=>row.iterations*1000/processMedians[i]),peakProcessRssKilobytes:rows.map(row=>row.peakProcessRssKilobytes),componentBytes:rows[0].componentBytes,capacityBytes:null,growCount:null};})})));
 const report={schemaVersion:1,state:'COMMON_BYTE_THREE_COMPARISON_TIMING_COMPLETE',phaseSha256:phaseSha,sourceIndexSha256:ownSha,protocol,machine:{platform:platform(),arch:arch(),release:release(),cpu:cpus()[0]?.model,logicalCpus:cpus().length,totalMemoryBytes:totalmem()},summaries,samples,calibrations,
  controlsSubtracted:false,independentTimedProcessesPerArmFamilyComparison:3,correlatedSamplesPerProcess:7,
  limitations:['Shared desktop/frequency/thermal/background variance; n3 process medians with seven correlated retained samples, no significance claim','ExactlyAB/BA/AB,2:1 first-arm imbalance; no second order matrix or extra independent samples inferred','One fresh public one-iteration pilot per arm/family/comparison chooses a shared1..16 N using the slower arm; all pilot costs/chosen counts preserved, no clipping','Host performance.now surrounds awaited WIT batch only; progress/checksum parsing/RSS reads occur outside timed intervals','Unchanged per-byte consume validation plus FNV Math.imul remains inside trace=false workload and may dominate; this is not isolated stream bookkeeping','Compile/binding load, instantiate, first batch and whole worker elapsed are separate observables, not isolated snapshot/deployed or process startup estimates','PeakRSS includes file hashes/V8/allocator retention; capacity/grow counts unavailable, no JS heap ownership inference','Same-engine is registered JS binding versus identical bundled JS factory on common native slots, not a C++ stream state machine','Whole-profile is ON versusOFF with identical canonical bundle; stock is a different provider/scheduler and ambient Web dependency domain','All original28 trace counterexamples remain;8newcommonbyte correctness cases do not establish general streams parity; three raw controls are never subtracted']};
 await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:report.state,timedWorkers:126,calibrationWorkers:42,output}));
}
