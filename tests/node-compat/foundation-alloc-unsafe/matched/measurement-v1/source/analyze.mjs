// Read-only arithmetic/receipt analysis of completed measurements. Does not
// instantiate components, run workloads, collect clocks or sample memory.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,readdir,copyFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
const artifact=resolve(process.env.NODE_COMPAT_ALLOC_UNSAFE_MATCHED_OUTPUT??'/tmp/starling-node-compat/foundations-v8/allocunsafe-matched-v2');
const output=join(here,'measurement-v1'),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const resultBytes=await readFile(join(artifact,'measurement/results.json')),result=JSON.parse(resultBytes);
const correctnessBytes=await readFile(join(artifact,'correctness-results.json')),correctness=JSON.parse(correctnessBytes);
assert.equal(result.records.length,60);assert.equal(result.comparisons.length,15);
assert.equal(result.correctnessManifestSha256,hash(correctnessBytes));
for(const file of correctness.sourceFiles)assert.equal(hash(await readFile(join(here,file.name))),file.sha256,file.name);
for(const arm of correctness.records){
  assert.equal(hash(await readFile(arm.componentPath)),arm.componentSha256);
  for(const file of arm.transpiledFiles)assert.equal(hash(await readFile(join(dirname(arm.modulePath),file.name))),file.sha256,file.name);
}
const engine='/tmp/starling-node-compat/foundations-v8/native-freeze/off-foundations.engine.wasm';
assert.equal(hash(await readFile(engine)),correctness.engineSha256);
for(const file of correctness.engineReceipt.sourceManifest)assert.equal(hash(await readFile(join(correctness.sourceRoot,file.path))),file.sha256,file.path);
const median=values=>{const sorted=[...values].sort((a,b)=>a-b);return(sorted[(sorted.length-1)>>1]+sorted[sorted.length>>1])/2;};
const relativeRange=values=>Math.max(...values)/Math.min(...values)-1;
const armView=record=>({medianBatchMs:median(record.batchMs),nanosecondsPerIteration:median(record.batchMs)*1e6/record.scenario.iterations,
  compileAndBindingLoadMs:record.compileAndBindingLoadMs,instantiateMs:record.instantiateMs,firstBatchMs:record.firstBatchMs,
  processPeakRssBytes:record.processPeakRssKilobytes*1024,
  instantiatedProcessRssBytes:record.observations[0].processRssBytes,finalProcessRssBytes:record.observations.at(-1).processRssBytes,
  finalMemoryByteLengths:record.observations.at(-1).bytes,observedBoundaryGrowthEvents:record.observedByteLengthGrowthEvents});
const comparisons=[];
for(let index=0;index<result.comparisons.length;index++){
  const scenario=result.comparisons[index],processes=result.records.filter(record=>record.index===index),orders=[];
  for(let order=0;order<2;order++){
    const native=processes.find(record=>record.order===order&&record.arm==='native'),js=processes.find(record=>record.order===order&&record.arm==='jco-js');
    assert(native&&js);
    for(const record of[native,js]){
      assert.equal(record.batchMs.length,7);assert.equal(record.warmups,3);
      const {order:ignoredOrder,index:ignoredIndex,...worker}=record;
      assert.deepEqual(JSON.parse(await readFile(join(artifact,'measurement',`order-${order}.case-${index}.${record.arm}.stdout`),'utf8')),worker);
      assert.equal((await readFile(join(artifact,'measurement',`order-${order}.case-${index}.${record.arm}.stderr`))).length,0);
    }
    const n=armView(native),j=armView(js);
    orders.push({order,runOrder:order===0?['native','jco-js']:['jco-js','native'],native:n,javascript:j,
      javascriptOverNativeMedianTime:j.medianBatchMs/n.medianBatchMs,
      nativeSlower:j.medianBatchMs<n.medianBatchMs,
      nativePeakRssLarger:n.processPeakRssBytes>j.processPeakRssBytes,
      nativeFinalLinearMemoryLarger:n.finalMemoryByteLengths.some((value,index)=>value>j.finalMemoryByteLengths[index])});
  }
  comparisons.push({operation:scenario.operation,name:scenario.name,size:scenario.size,iterations:scenario.iterations,
    independentProcessesPerArm:2,correlatedSamplesPerProcess:7,orders,
    ratioRelativeRange:relativeRange(orders.map(order=>order.javascriptOverNativeMedianTime)),
    nativeProcessMedianRelativeRange:relativeRange(orders.map(order=>order.native.medianBatchMs)),
    javascriptProcessMedianRelativeRange:relativeRange(orders.map(order=>order.javascript.medianBatchMs)),
    directionChangesWithOrder:orders[0].nativeSlower!==orders[1].nativeSlower});
}
const counterexamples=comparisons.flatMap(comparison=>comparison.orders.filter(order=>order.nativeSlower).map(order=>({name:comparison.name,size:comparison.size,order:order.order,
  javascriptOverNativeMedianTime:order.javascriptOverNativeMedianTime,control:comparison.operation>=3})));
const memoryCounterexamples=comparisons.flatMap(comparison=>comparison.orders.filter(order=>order.nativePeakRssLarger||order.nativeFinalLinearMemoryLarger)
  .map(order=>({name:comparison.name,size:comparison.size,order:order.order,nativePeakRssLarger:order.nativePeakRssLarger,nativeFinalLinearMemoryLarger:order.nativeFinalLinearMemoryLarger})));
const analysis={schema:1,atUtc:new Date().toISOString(),state:'matched-allocation-measurement-complete',engineSha256:result.engineSha256,
  sourceResultSha256:hash(resultBytes),correctnessManifestSha256:hash(correctnessBytes),machine:result.machine,
  processes:60,scenarios:15,independentProcessesPerArmScenario:2,correlatedSamplesPerProcess:7,comparisons,counterexamples,memoryCounterexamples,
  checks:{all60RawReportsMatch:true,all60StderrEmpty:true,sourceAndNativeInputsVerifiedAfter:true,
    frozenNativeSources:293,sourceFiles:correctness.sourceFiles.length,transpiledFiles:correctness.records.reduce((sum,record)=>sum+record.transpiledFiles.length,0),components:2},
  limitations:['Two independent processes per arm/scenario; seven retained samples per process are correlated, not fourteen independent trials',
    'Arm-order ratios are reported separately; no confidence interval, statistical significance or broad platform conclusion',
    'Shared desktop, uncontrolled background load/frequency/thermal state; peer heavy jobs were held during the coordinated window',
    'Process peakRSS includes validation file reads before baseline, V8 compilation/code/runtime and allocator retention; not isolated guest heap',
    'Public Memory byte lengths are capacities sampled at boundaries; growth events are a lower bound, not internal grow attempts/failures',
    'Both arms use the same full profile-enabled v8 engine; JS adapter replaces its own component global Buffer deliberately',
    'V8-hosted Wasm through Jco; Wasmtime correctness is separate and no Wasmtime throughput claim follows',
    'No raw memory/private ABI/DEBUG/fault work or previous timing data participates']};
await mkdir(join(output,'raw'),{recursive:true});await mkdir(join(output,'source'),{recursive:true});
for(const file of await readdir(join(artifact,'measurement')))await copyFile(join(artifact,'measurement',file),join(output,'raw',file));
await copyFile(join(artifact,'measurement.run.log'),join(output,'run.log'));
await writeFile(join(output,'correctness-results.json'),correctnessBytes);
for(const file of correctness.sourceFiles)await copyFile(join(here,file.name),join(output,'source',file.name));
await writeFile(join(output,'analysis-results.json'),JSON.stringify(analysis,null,2)+'\n');
console.log(JSON.stringify({output,processes:60,scenarios:15,counterexamples:counterexamples.length,
  allocatorCounterexamples:counterexamples.filter(value=>!value.control).length,
  orderDirectionChanges:comparisons.filter(value=>value.directionChangesWithOrder).map(value=>({name:value.name,size:value.size})),allRawMatched:true}));
