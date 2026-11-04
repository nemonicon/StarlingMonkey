// PREPARED ONLY. Parent coordinator must open the measurement window first.
// All timers/RSS/Memory observations are host-side public APIs. No guest clock,
// raw-memory view, private engine API, memory limit or custom host service.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {spawnSync} from 'node:child_process';
import {cpus,platform,arch,release,totalmem} from 'node:os';
import {loadCompiled,memoryLengths} from './instantiate.mjs';
assert.equal(process.version,'v22.14.0');
assert.equal(process.env.NODE_COMPAT_ALLOC_UNSAFE_MEASURE,'1','Measurement window must be explicitly authorized; correctness build never sets this variable');
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const output=resolve(process.env.NODE_COMPAT_ALLOC_UNSAFE_MATCHED_OUTPUT??'/tmp/starling-node-compat/allocunsafe-matched');
const manifestBytes=await readFile(join(output,'correctness-results.json')),manifest=JSON.parse(manifestBytes);
assert.equal(manifest.state,'matched-allocation-correctness-only-passed');assert.equal(manifest.measurementsExecuted,false);
for(const file of manifest.sourceFiles)assert.equal(hash(await readFile(join(here,file.name))),file.sha256,file.name);
for(const record of manifest.records){assert.equal(hash(await readFile(record.componentPath)),record.componentSha256);
  for(const file of record.transpiledFiles)assert.equal(hash(await readFile(join(dirname(record.modulePath),file.name))),file.sha256,file.name);}
const samples=7,warmups=3;
if(process.argv[2]==='--worker'){
  const arm=process.argv[3],index=Number(process.argv[4]),record=manifest.records.find(record=>record.arm===arm),scenario=manifest.scenarios[index];
  assert(record&&scenario);const rss=()=>process.memoryUsage().rss;
  const baselineRssBytes=rss(),start=performance.now(),instantiate=await loadCompiled(record),compileAndBindingLoadMs=performance.now()-start;
  const compiledRssBytes=rss(),instanceStart=performance.now(),instance=await instantiate(),instantiateMs=performance.now()-instanceStart;
  const observations=[],readMemory=label=>{const result={label,bytes:memoryLengths(instance),processRssBytes:rss()};observations.push(result);return result;};
  readMemory('instantiated');
  const invoke=()=>instance.exports.batch(scenario.operation,scenario.size,scenario.iterations);
  // Warmups occur only after the first separately reported batch.
  const firstStart=performance.now(),firstValue=invoke(),firstBatchMs=performance.now()-firstStart;assert.equal(firstValue,scenario.expected);readMemory('first-batch');
  for(let i=0;i<warmups;i++)assert.equal(invoke(),scenario.expected);readMemory('warmed');
  const batchMs=[];
  for(let i=0;i<samples;i++){const start=performance.now(),value=invoke(),duration=performance.now()-start;assert.equal(value,scenario.expected);batchMs.push(duration);readMemory('sample-'+i);}
  let observedByteLengthGrowthEvents=0;
  for(let i=1;i<observations.length;i++)for(let memory=0;memory<observations[i].bytes.length;memory++)
    if(observations[i].bytes[memory]>observations[i-1].bytes[memory])observedByteLengthGrowthEvents++;
  const report={arm,scenario,node:process.version,nodeExecutableSha256:hash(await readFile(process.execPath)),baselineRssBytes,compiledRssBytes,
    compileAndBindingLoadMs,instantiateMs,firstBatchMs,batchMs,warmups,observations,
    processPeakRssKilobytes:process.resourceUsage().maxRSS,observedByteLengthGrowthEvents,
    memoryObservation:'Public exported WebAssembly.Memory.buffer.byteLength sampled outside timed intervals; no raw byte reads/views or explicit grow calls',
    limitations:['Boundary growth events are a lower bound; in-Wasm memory.grow calls/failures are not intercepted',
      'Node/Jco execution uses V8-hosted Wasm; not Wasmtime throughput',
      'PeakRSS includes V8 compilation/runtime/code and allocator retention; point RSS is whole process, not guest live heap',
      'Compile-and-binding-load includes Wasm compilation and generated JS module import; first batch is batch latency, not isolated allocation latency']};
  console.log(JSON.stringify(report));
}else{
  const measurement=join(output,'measurement');await mkdir(measurement,{recursive:true});
  await writeFile(join(measurement,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),manifestSha256:hash(manifestBytes)})+'\n',{flag:'wx'});
  const records=[];
  for(let order=0;order<2;order++)for(let index=0;index<manifest.scenarios.length;index++){
    const arms=order===0?['native','jco-js']:['jco-js','native'];
    for(const arm of arms){
      const result=spawnSync(process.execPath,[fileURLToPath(import.meta.url),'--worker',arm,String(index)],{encoding:'utf8',timeout:300000,maxBuffer:4*1024*1024});
      await writeFile(join(measurement,`order-${order}.case-${index}.${arm}.stdout`),result.stdout??'');
      await writeFile(join(measurement,`order-${order}.case-${index}.${arm}.stderr`),result.stderr??'');
      assert.equal(result.status,0,result.error?.message??result.stderr);const record=JSON.parse(result.stdout);assert.equal(record.arm,arm);
      records.push({order,index,...record});await writeFile(join(measurement,'partial.json'),JSON.stringify(records,null,2)+'\n');
    }
  }
  const median=values=>{const sorted=[...values].sort((a,b)=>a-b),middle=sorted.length>>1;return sorted.length%2?sorted[middle]:(sorted[middle-1]+sorted[middle])/2;};
  const comparisons=manifest.scenarios.map((scenario,index)=>{
    const arms=Object.fromEntries(['native','jco-js'].map(arm=>{const selected=records.filter(record=>record.index===index&&record.arm===arm),batchMs=selected.flatMap(record=>record.batchMs),ms=median(batchMs);
      return[arm,{medianBatchMs:ms,nanosecondsPerIteration:ms*1e6/scenario.iterations,
        requestedMiBPerSecond:scenario.operation===5?null:scenario.size*scenario.iterations/1048576/(ms/1000),
        perProcessMediansMs:selected.map(record=>median(record.batchMs)),instantiateMs:selected.map(record=>record.instantiateMs),
        processPeakRssKilobytes:selected.map(record=>record.processPeakRssKilobytes),
        memoryBoundaryObservations:selected.map(record=>record.observations),observedByteLengthGrowthEvents:selected.map(record=>record.observedByteLengthGrowthEvents)}];}));
    return{...scenario,arms,javascriptOverNativeMedianTime:arms['jco-js'].medianBatchMs/arms.native.medianBatchMs};
  });
  const report={schema:1,atUtc:new Date().toISOString(),engineSha256:manifest.engineSha256,correctnessManifestSha256:hash(manifestBytes),
    sourceFiles:manifest.sourceFiles,machine:{platform:platform(),arch:arch(),release:release(),cpu:cpus()[0]?.model,logicalCpus:cpus().length,totalMemoryBytes:totalmem()},
    protocol:{backend:'Node22.14/V8-hosted Wasm through actual Jco1.40 explicit instantiate API',orders:[['native','jco-js'],['jco-js','native']],
      processPerArmScenarioOrder:true,freshInstancesPerArmScenario:2,retainedSamplesPerProcess:7,warmups:3,
      imports:[],timer:'host performance.now around one batch WIT invocation',memory:'Public process RSS/resourceUsage; exported WebAssembly.Memory.buffer.byteLength only'},
    comparisons,records,limitations:['Two independent processes per arm/scenario; seven within-process samples are correlated',
      'Same installed v8 engine in both arms; adapter globalBuffer replacement is deliberate and isolated by component/process',
      'Controls are separately reported; their noisy medians are not subtracted',
      'Reuse control performs one Uint8Array allocation per batch and zero per iteration; byte throughput is not reported',
      'No guest clock/custom host import, raw memory read, private engine diagnostic or inferred internal grow count',
      'This experiment supplies no Wasmtime throughput or profile-free deployment size result; no older timings are combined']};
  await writeFile(join(measurement,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({output:join(measurement,'results.json'),scenarios:comparisons.length,records:records.length}));
}
