// Future ROOT-approved timing only. No execution during source preparation.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,statfs} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {performance} from 'node:perf_hooks';
import {cpus,platform,arch,release,totalmem} from 'node:os';
import {selectTimingPhase} from './phase.mjs';
import {cases,comparisons,protocol,orderFor} from './protocol.mjs';
import {loadCompiled,memoryLengths} from './instantiate.mjs';
import {executionPreflight} from './runtime-preflight.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
assert.equal(process.env.NODE_COMPAT_COMMON_BYTE_TIMING_APPROVED,'1','Separate Root timing window required');
const worker=process.argv[2]==='--worker',offset=worker?3:2;
const [ownSha,phasePath,phaseSha]=process.argv.slice(offset,offset+3);assert(/^[0-9a-f]{64}$/.test(ownSha??'')&&/^[0-9a-f]{64}$/.test(phaseSha??''));assert(phasePath&&resolve(phasePath)===phasePath);
const sourceIndexRaw=await readFile(join(here,'index.json'));assert.equal(hash(sourceIndexRaw),ownSha);const sourceIndex=JSON.parse(sourceIndexRaw);
for(const row of sourceIndex.files){const raw=await readFile(join(here,row.path));assert.equal(hash(raw),row.sha256);assert.equal(raw.length,row.bytes);}
const phaseRaw=await readFile(phasePath);assert.equal(hash(phaseRaw),phaseSha);const phase=selectTimingPhase(JSON.parse(phaseRaw));assert.equal(phase.sourceFamilyIndexSha256,ownSha);
async function auditPhase(){assert.equal(hash(await readFile(phasePath)),phaseSha);assert.equal(hash(await readFile(join(here,'index.json'))),ownSha);
 for(const name of ['actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts']){const row=phase[name];assert.equal(hash(await readFile(row.reportPath)),row.reportSha256);assert.equal(hash(await readFile(row.rootReviewPath)),row.rootReviewSha256);}
 for(const row of Object.values(phase.components)){assert.equal(hash(await readFile(row.componentPath)),row.componentSha256);assert.equal(hash(await readFile(row.enginePath)),row.engineSha256);for(const file of row.transpiledFiles){const raw=await readFile(join(dirname(row.modulePath),file.name));assert.equal(hash(raw),file.sha256);assert.equal(raw.length,file.bytes);}}
}
await auditPhase();
const correctness=JSON.parse(await readFile(phase.actualCorrectness.reportPath));assert.equal(correctness.state,'ACTUAL_COMMON_BYTE_FOUR_ARM_CORRECTNESS_PASSED');assert.equal(correctness.sourceFamilyIndexSha256,ownSha);assert.equal(correctness.pairPinsSha256,phase.pairPinsSha256);assert.equal(correctness.records.length,4);
for(const record of correctness.records){const row=phase.components[record.arm];for(const key of ['componentPath','componentSha256','componentBytes','enginePath','engineSha256','modulePath','bundleSha256'])assert.equal(row[key],record[key]);assert.deepEqual(row.transpiledFiles,record.transpiledFiles);assert.deepEqual(row.coreFiles,record.coreFiles);assert.equal(record.correctnessPassed,true);assert.equal(record.identityPassed,true);assert.equal(record.checkpointProbePassed,true);}
const oracle=[...JSON.parse(await readFile(join(here,'node-common-oracle.json'))).cases,...JSON.parse(await readFile(join(here,'node-control-oracle.json'))).cases];assert.equal(oracle.length,14);
function summary(index){const expected=oracle[index].expected;return{result:{...expected,records:[]}};}
function exact(raw,index){const value=JSON.parse(raw);assert.equal(JSON.stringify(value),JSON.stringify(summary(index)),'Compact batch checksum/unit/callback contract');}
if(worker){
 const arm=process.argv[offset+3],index=Number(process.argv[offset+4]);assert(phase.components[arm]&&cases[index]);
 const record=phase.components[arm],scenario=cases[index],rss=()=>process.memoryUsage().rss,initialRssBytes=rss();
 const compileStart=performance.now(),instantiate=await loadCompiled(record),compileAndBindingLoadMs=performance.now()-compileStart,compiledRssBytes=rss();
 const instantiateStart=performance.now(),instance=await instantiate(),instantiateMs=performance.now()-instantiateStart;
 const identity=JSON.parse(await instance.exports.identity());assert.equal(JSON.stringify(identity),JSON.stringify(record.identity));
 const checkpointProbe=JSON.parse(await instance.exports.checkpointProbe());assert.equal(JSON.stringify(checkpointProbe),JSON.stringify(record.checkpointProbe));
 assert.equal(await instance.exports.setup(index),oracle[index].setup);
 const observations=[],observe=label=>observations.push({label,exportedMemoryByteLengths:memoryLengths(instance),processRssBytes:rss()});observe('ready');
 const invoke=()=>instance.exports.batch(index),firstStart=performance.now(),first=await invoke(),firstBatchMs=performance.now()-firstStart;exact(first,index);observe('first-batch');
 for(let i=0;i<3;i++)exact(await invoke(),index);observe('warmed');
 const batchMs=[];for(let sample=0;sample<7;sample++){const start=performance.now(),value=await invoke(),elapsed=performance.now()-start;exact(value,index);batchMs.push(elapsed);observe('sample-'+sample);}
 let observedCapacityIncreaseBoundaries=0;for(let i=1;i<observations.length;i++)for(let m=0;m<observations[i].exportedMemoryByteLengths.length;m++)if(observations[i].exportedMemoryByteLengths[m]>observations[i-1].exportedMemoryByteLengths[m])observedCapacityIncreaseBoundaries++;
 await auditPhase();console.log(JSON.stringify({arm,index,scenario,initialRssBytes,compiledRssBytes,compileAndBindingLoadMs,instantiateMs,firstBatchMs,batchMs,observations,identity,checkpointProbe,observedCapacityIncreaseBoundaries,
  peakProcessRssKilobytes:process.resourceUsage().maxRSS,componentBytes:record.componentBytes,unitsPerBatch:oracle[index].expected.totalUnits,
  memoryScope:'Public process RSS plus exported Memory.buffer.byteLength at boundaries. No byte reads, grow calls, hidden counters or heap ownership claim.'}));
}else{
 const on=await executionPreflight({variant:'benchmark-classic-on'}),off=await executionPreflight({variant:'benchmark-classic-off'});assert.equal(on.pairSha256,phase.pairPinsSha256);
 for(const arm of ['native-on','canonical-on','stock-on'])assert.equal(phase.components[arm].engineSha256,on.pin.engineSha256);assert.equal(phase.components['canonical-off'].engineSha256,off.pin.engineSha256);
 const output=resolve(process.env.NODE_COMPAT_COMMON_BYTE_MEASUREMENT_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
 try{await lstat(output);assert.fail('Fresh timing output required');}catch(error){if(error.code!=='ENOENT')throw error;}
 const disk=await statfs(dirname(output));assert(disk.bavail*disk.bsize>=2*1024**3,'2GiB initial guard retained');await mkdir(output,{recursive:false});
 await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),phaseSha256:phaseSha,sourceIndexSha256:ownSha,protocol})+'\n',{flag:'wx'});
 const samples=[];let failure=null;
 try{
  for(const comparison of comparisons)for(let index=0;index<14;index++)for(let repetition=0;repetition<3;repetition++)for(const arm of orderFor(repetition,index,comparison.arms)){
   const available=await statfs(output);assert(available.bavail*available.bsize>=800*1024**2,'Stop creating artifacts below800MiB');
   const name=comparison.id+'.case-'+index+'.rep-'+repetition+'.'+arm,start=performance.now();
   const result=spawnSync(process.execPath,[fileURLToPath(import.meta.url),'--worker',ownSha,phasePath,phaseSha,arm,String(index)],{encoding:'utf8',timeout:300000,maxBuffer:4*1024*1024});
   const elapsed=performance.now()-start;await writeFile(join(output,name+'.stdout'),result.stdout??'',{flag:'wx'});await writeFile(join(output,name+'.stderr'),result.stderr??'',{flag:'wx'});
   await writeFile(join(output,name+'.status.json'),JSON.stringify({status:result.status,signal:result.signal,error:result.error?.message??null,wholeProcessElapsedMs:elapsed})+'\n',{flag:'wx'});
   assert.equal(result.status,0,result.error?.message??result.stderr);const row=JSON.parse(result.stdout);assert.equal(row.arm,arm);assert.equal(row.index,index);assert.equal(row.batchMs.length,7);
   samples.push({comparison:comparison.id,repetition,caseIndex:index,runOrder:orderFor(repetition,index,comparison.arms),wholeProcessElapsedMs:elapsed,...row});
  }
 }catch(error){failure=error;}finally{
  try{await auditPhase();await on.recheck();await off.recheck();}catch(error){failure??=error;}
  await writeFile(join(output,'terminal-source-audit.json'),JSON.stringify({phaseSha256:phaseSha,sourceIndexSha256:ownSha,successfulWorkers:samples.length,expectedWorkers:252,passed:failure===null,error:failure?{name:failure.name,message:failure.message}:null},null,2)+'\n',{flag:'wx'});
 }
 if(failure)throw failure;assert.equal(samples.length,252);
 const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
 const summaries=comparisons.flatMap(comparison=>cases.map((scenario,index)=>({comparison:comparison.id,caseIndex:index,scenario,arms:comparison.arms.map(arm=>{
  const rows=samples.filter(row=>row.comparison===comparison.id&&row.caseIndex===index&&row.arm===arm),processMedians=rows.map(row=>median(row.batchMs));assert.equal(rows.length,3);
  return{arm,processMedians,medianOfProcessMediansMs:median(processMedians),bytesPerSecondPerProcess:rows.map((row,i)=>row.unitsPerBatch*1000/processMedians[i]),iterationOperationsPerSecondPerProcess:processMedians.map(ms=>scenario.iterations*1000/ms),peakProcessRssKilobytes:rows.map(row=>row.peakProcessRssKilobytes),finalExportedMemoryByteLengths:rows.map(row=>row.observations.at(-1).exportedMemoryByteLengths),componentBytes:rows[0].componentBytes};})})));
 const report={schemaVersion:1,state:'COMMON_BYTE_THREE_COMPARISON_TIMING_COMPLETE',phaseSha256:phaseSha,sourceIndexSha256:ownSha,protocol,machine:{platform:platform(),arch:arch(),release:release(),cpu:cpus()[0]?.model,logicalCpus:cpus().length,totalMemoryBytes:totalmem()},summaries,samples,
  controlsSubtracted:false,independentProcessesPerArmCaseComparison:3,correlatedSamplesPerProcess:7,
  limitations:['Shared desktop/frequency/thermal/background variance; n3 process medians with seven correlated retained samples, no significance claim','Three repetitions have2:1 first-arm order imbalance within each case; opposite case parity rotates it; all raw order reversals remain','Host performance.now around awaited WIT batch only; checks and RSS/capacity reads occur afterward','Compile/binding load, instantiate, first batch and whole worker elapsed are separate observables, not isolated snapshot/deployed or process startup estimates','PeakRSS includes verifier/file hashes/V8/allocator retention; capacities do not establish heap ownership or live bytes','Same-engine is registered JS binding versus identical bundled JS factory on common native slots, not a C++ stream state machine','Whole-profile is ON versusOFF with identical canonical bundle; stock is a different provider/scheduler and ambient Web dependency domain','All original28 trace counterexamples remain;8newcommonbytecases do not establish general streams parity; raw controls are never subtracted']};
 await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:report.state,workers:252,output}));
}
