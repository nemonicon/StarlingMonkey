// Arithmetic over retained raw reports only; no workload/timer/memory sampling.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),bytes=await readFile(join(here,'raw/results.json')),raw=JSON.parse(bytes);
const hash=value=>createHash('sha256').update(value).digest('hex');
const median=values=>{const sorted=[...values].sort((a,b)=>a-b);return(sorted[(sorted.length-1)>>1]+sorted[sorted.length>>1])/2;};
const comparisons=[];
for(let index=0;index<raw.comparisons.length;index++){
  const row=raw.comparisons[index],orders=[];
  for(const order of[0,1]){
    const baseline=raw.records.find(record=>record.index===index&&record.order===order&&record.arm==='baseline');
    const candidate=raw.records.find(record=>record.index===index&&record.order===order&&record.arm==='candidate');assert(baseline&&candidate);
    const b=median(baseline.batchMs),c=median(candidate.batchMs);assert.equal(row.orders[order].baselineMedianBatchMs,b);assert.equal(row.orders[order].candidateMedianBatchMs,c);
    for(const record of[baseline,candidate]){const{order:ignored,index:ignoredIndex,...worker}=record;assert.deepEqual(JSON.parse(await readFile(join(here,'raw',`order-${order}.case-${index}.${record.arm}.stdout`),'utf8')),worker);}
    orders.push({...row.orders[order],baselineInstantiateMs:baseline.instantiateMs,candidateInstantiateMs:candidate.instantiateMs,
      baselineCompileBindingMs:baseline.compileAndBindingLoadMs,candidateCompileBindingMs:candidate.compileAndBindingLoadMs,
      baselineFirstBatchMs:baseline.firstBatchMs,candidateFirstBatchMs:candidate.firstBatchMs,
      candidatePeakRssLarger:candidate.processPeakRssKilobytes>baseline.processPeakRssKilobytes,
      candidateCapacityLarger:candidate.observations.at(-1).bytes.some((value,index)=>value>baseline.observations.at(-1).bytes[index])});
  }
  const ratios=orders.map(order=>order.baselineOverCandidateMedianTime);
  comparisons.push({operation:row.operation,name:row.name,size:row.size,iterations:row.iterations,orders,
    ratioOrderRelativeRange:Math.max(...ratios)/Math.min(...ratios)-1,
    orderDirectionReversal:orders[0].candidateSlower!==orders[1].candidateSlower});
}
const slowdowns=comparisons.flatMap(row=>row.orders.filter(order=>order.candidateSlower).map(order=>({name:row.name,size:row.size,order:order.order,baselineOverCandidateMedianTime:order.baselineOverCandidateMedianTime,control:row.operation>=3})));
const report={schema:1,state:'private-m011-process-median-analysis-complete',rawResultsSha256:hash(bytes),processes:raw.records.length,scenarios:comparisons.length,
  independentProcessesPerArmScenario:2,correlatedSamplesPerProcess:7,comparisons,slowdowns,
  peakRssCandidateHigherOrders:comparisons.flatMap(row=>row.orders).filter(order=>order.candidatePeakRssLarger).length,
  capacityCandidateHigherOrders:comparisons.flatMap(row=>row.orders).filter(order=>order.candidateCapacityLarger).length,
  caveats:['Five control scenarios reverse direction across orders; cannot subtract controls or infer stable general speedups',
    'Two process peaks are conspicuously lower than other repeats; retained without exclusion or causal explanation',
    'No old-v8/current-Jco comparison, isolated-fill attribution, memory reduction, C++ kernel or size-win claim',
    'Host timing/whole-process peakRSS/public linear capacity only; not statistical significance, guest live heap or internal grow counts']};
await writeFile(join(here,'analysis-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({processes:raw.records.length,scenarios:comparisons.length,candidateSlowerOrders:slowdowns.length,
  changedAllocatorSlowdowns:slowdowns.filter(row=>!row.control).length,controlReversals:comparisons.filter(row=>row.orderDirectionReversal).length,
  peakRssCandidateHigherOrders:report.peakRssCandidateHigherOrders,capacityCandidateHigherOrders:report.capacityCandidateHigherOrders}));
