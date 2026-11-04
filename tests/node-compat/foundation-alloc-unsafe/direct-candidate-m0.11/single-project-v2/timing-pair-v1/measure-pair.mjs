// PREPARED; no timing authorization is implied by this file's presence.
// Public host APIs only. Guest imports remain empty. No byte views/private ABI.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,statfs} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {performance} from 'node:perf_hooks';
import {cpus,platform,arch,release,totalmem} from 'node:os';
import {loadCompiled,memoryLengths} from './instantiate.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
assert.equal(process.env.NODE_COMPAT_M011_TIMING_APPROVED,'1','Wait for separate root source review and explicit coordinated timing window');
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const inputBytes=await readFile(join(here,'inputs.json')),input=JSON.parse(inputBytes);
assert.equal(input.state,'frozen-private-m011-measurement-inputs');assert.equal(input.correctnessPassed,true);assert.equal(input.records.length,2);assert.equal(input.scenarios.length,15);
assert.deepEqual(input.records.map(record=>record.arm),['baseline','candidate']);
for(const file of input.sourceFiles)assert.equal(hash(await readFile(join(here,file.path))),file.sha256,file.path);
for(const file of input.receipts)assert.equal(hash(await readFile(join(here,file.path))),file.sha256,file.path);
for(const record of input.records){
  assert.equal(hash(await readFile(record.componentPath)),record.componentSha256,record.arm);
  assert.equal(hash(await readFile(record.enginePath)),record.engineSha256,record.arm+' engine');
  for(const file of record.transpiledFiles)assert.equal(hash(await readFile(join(dirname(record.modulePath),file.name))),file.sha256,file.name);
  assert.deepEqual(record.emittedImports,[]);assert.equal(record.bundleSha256,input.commonBundleSha256);
}
const samples=7,warmups=3;
if(process.argv[2]==='--worker'){
  const arm=process.argv[3],index=Number(process.argv[4]),record=input.records.find(record=>record.arm===arm),scenario=input.scenarios[index];assert(record&&scenario);
  const rss=()=>process.memoryUsage().rss,baselineRssBytes=rss();
  const compileStart=performance.now(),instantiate=await loadCompiled(record),compileAndBindingLoadMs=performance.now()-compileStart;
  const compiledRssBytes=rss(),instanceStart=performance.now(),instance=await instantiate(),instantiateMs=performance.now()-instanceStart;
  const observations=[],observe=label=>{observations.push({label,bytes:memoryLengths(instance),processRssBytes:rss()});};
  const invoke=()=>instance.exports.batch(scenario.operation,scenario.size,scenario.iterations);
  observe('instantiated');
  const firstStart=performance.now(),firstValue=invoke(),firstBatchMs=performance.now()-firstStart;assert.equal(firstValue,scenario.expected);observe('first-batch');
  for(let i=0;i<warmups;i++)assert.equal(invoke(),scenario.expected);observe('warmed');
  const batchMs=[];
  for(let i=0;i<samples;i++){const start=performance.now(),value=invoke(),ms=performance.now()-start;assert.equal(value,scenario.expected);batchMs.push(ms);observe('sample-'+i);}
  let boundaryGrowthEventsLowerBound=0;
  for(let i=1;i<observations.length;i++)for(let memory=0;memory<observations[i].bytes.length;memory++)if(observations[i].bytes[memory]>observations[i-1].bytes[memory])boundaryGrowthEventsLowerBound++;
  console.log(JSON.stringify({arm,scenario,node:process.version,nodeExecutableSha256:hash(await readFile(process.execPath)),baselineRssBytes,compiledRssBytes,
    compileAndBindingLoadMs,instantiateMs,firstBatchMs,batchMs,warmups,observations,processPeakRssKilobytes:process.resourceUsage().maxRSS,
    boundaryGrowthEventsLowerBound,memoryObservation:'Public exported Memory.buffer.byteLength outside timed intervals; no guest bytes/views or grow calls',
    limitations:['In-Wasm grow attempts/failures are unobserved; boundary increases are a lower bound',
      'PeakRSS includes input-file verification, V8 compilation/code/runtime and allocator retention',
      'V8-hosted Wasm via Jco; first batch is batch latency, not isolated allocator latency']}));
}else{
  const output=join(input.experiment,'timing-pair-v1');await mkdir(output,{recursive:true});
  const disk=await statfs(output);assert(disk.bavail*disk.bsize>1.5*1024*1024*1024,'Root1.5GiB disk cutoff; do not create further artifacts');
  await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),inputsSha256:hash(inputBytes)})+'\n',{flag:'wx'});
  const records=[];
  for(let order=0;order<2;order++)for(let index=0;index<input.scenarios.length;index++){
    for(const arm of order===0?['baseline','candidate']:['candidate','baseline']){
      const result=spawnSync(process.execPath,[fileURLToPath(import.meta.url),'--worker',arm,String(index)],{encoding:'utf8',timeout:300000,maxBuffer:4*1024*1024});
      await writeFile(join(output,`order-${order}.case-${index}.${arm}.stdout`),result.stdout??'');await writeFile(join(output,`order-${order}.case-${index}.${arm}.stderr`),result.stderr??'');
      assert.equal(result.status,0,result.error?.message??result.stderr);const record=JSON.parse(result.stdout);assert.equal(record.arm,arm);assert.equal(record.batchMs.length,7);
      records.push({order,index,...record});await writeFile(join(output,'partial.json'),JSON.stringify(records,null,2)+'\n');
    }
  }
  const median=values=>{const sorted=[...values].sort((a,b)=>a-b);return(sorted[(sorted.length-1)>>1]+sorted[sorted.length>>1])/2;};
  const comparisons=input.scenarios.map((scenario,index)=>({
    ...scenario,orders:[0,1].map(order=>{
      const b=records.find(record=>record.order===order&&record.index===index&&record.arm==='baseline'),c=records.find(record=>record.order===order&&record.index===index&&record.arm==='candidate');
      const bm=median(b.batchMs),cm=median(c.batchMs);
      return{order,runOrder:order===0?['baseline','candidate']:['candidate','baseline'],baselineMedianBatchMs:bm,candidateMedianBatchMs:cm,
        baselineOverCandidateMedianTime:bm/cm,candidateSlower:cm>bm,
        baselineNanosecondsPerIteration:bm*1e6/scenario.iterations,candidateNanosecondsPerIteration:cm*1e6/scenario.iterations,
        baselinePeakRssKilobytes:b.processPeakRssKilobytes,candidatePeakRssKilobytes:c.processPeakRssKilobytes,
        baselineFinalMemoryBytes:b.observations.at(-1).bytes,candidateFinalMemoryBytes:c.observations.at(-1).bytes,
        baselineBoundaryGrowthLowerBound:b.boundaryGrowthEventsLowerBound,candidateBoundaryGrowthLowerBound:c.boundaryGrowthEventsLowerBound};
    })}));
  const report={schema:1,state:'private-m011-timing-pair-complete',atUtc:new Date().toISOString(),inputsSha256:hash(inputBytes),sourceFiles:input.sourceFiles,
    machine:{platform:platform(),arch:arch(),release:release(),cpu:cpus()[0]?.model,logicalCpus:cpus().length,totalMemoryBytes:totalmem()},
    protocol:{backend:'Node22.14/V8-hosted Wasm via Jco1.40',scenarios:15,orders:[['baseline','candidate'],['candidate','baseline']],workers:60,
      independentProcessesPerArmScenario:2,correlatedSamplesPerProcess:7,warmups:3,hostTimer:'performance.now around batch WIT call only; asserts after',
      memory:'Public process RSS/resourceUsage and exported Memory.buffer.byteLength only',guestImports:[]},comparisons,records,
    limitations:['n2 independent processes per arm/scenario; seven retained samples are correlated, not fourteen independent trials',
      'Shared desktop with uncontrolled frequency/thermal/background state; no significance or platform-general claim',
      'Controls separately reported and never subtracted; all order reversals/candidate slowdowns retained',
      'Whole return-expression comparison, not isolated attribution to zero-fill/validation/native execution',
      'Registered JS facade on native Uint8Array intrinsic; no new C++ allocator kernel',
      'Snapshot+8513B size counterexample preserved; no snapshot determinism or size win inferred',
      'No old v8 measurements transferred and no current Jco adapter speed comparison',
      'No raw/private memory access or invented internal grow/failure count; peakRSS is whole-process high water']};
  await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({state:report.state,output,workers:records.length,scenarios:comparisons.length,candidateSlowerOrders:comparisons.flatMap(comparison=>comparison.orders).filter(order=>order.candidateSlower).length}));
}
