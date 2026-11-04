// Pure bounded schedule/calibration DATA. No clock, codec, process or filesystem.
export const ARMS=Object.freeze(['native-on','fflate-on','fflate-off']);
export const COMPARISONS=Object.freeze([
 Object.freeze({id:'same-engine-provider',A:'native-on',B:'fflate-on'}),
 Object.freeze({id:'unused-profile',A:'fflate-on',B:'fflate-off'})
]);
export const POLICY=Object.freeze({cases:30,repetitions:3,warmups:3,samples:7,targetMs:50,
 publicCallHardMs:600000,workerHardMs:7200000,smallNMax:32768,largeNMax:128,
 controlsBefore:3,controlsAfter:3,controlN:1,controlSubtraction:false});
export function need(v,message){if(!v)throw new Error('ERR_COST_PILOT_SOURCE: '+message);}
export function integer(v,min,max,label){need(Number.isSafeInteger(v)&&!Object.is(v,-0)&&v>=min&&v<=max,label);return v;}
export function positive(v,label){need(typeof v==='number'&&Number.isFinite(v)&&v>0,label);return v;}
export function primary(id){return integer(id,0,29,'exact primary case');}
export function caseCap(id){primary(id);return id<18?32768:128;}
export function nValue(id,n){integer(n,1,caseCap(id),'bounded positive N');need((n&(n-1))===0,'geometric power of two');return n;}
export function controlIds(id){primary(id);return Object.freeze([30+id,60+id,90+id]);}
export function candidateNs(id){const rows=[];for(let n=1;n<=caseCap(id);n*=2)rows.push(n);return Object.freeze(rows);}
export function timingSchedule(){
 const rows=[];
 for(const comparison of COMPARISONS)for(let id=0;id<30;id++)for(let repetition=0;repetition<3;repetition++){
  const sides=repetition===1?['B','A']:['A','B'];
  for(const side of sides)rows.push(Object.freeze({comparison:comparison.id,caseId:id,repetition,side,arm:comparison[side],
   order:repetition===1?'BA':'AB',freshOwnedProcess:true,warmups:3,samples:7,
   beforeControls:controlIds(id),afterControls:controlIds(id),controlN:1}));
 }
 need(rows.length===360,'original360 timing workers');return Object.freeze(rows);
}
// Pilot is a proposed refinement: fresh owned worker for each arm/candidate,
// three same-N warmups then one positive full-unit sample. It is NOT a speed
// result. Parent stops at the first geometric N whose observed pair BOTH hit50ms.
export function pilotPairModel(pair,id,n,comparisonId){
 const comparison=COMPARISONS.find(r=>r.id===comparisonId);need(comparison,'exact comparison');nValue(id,n);
 need(pair&&pair.caseId===id&&pair.n===n&&pair.comparison===comparisonId,'exact paired pilot identity');
 need(Array.isArray(pair.arms)&&pair.arms.length===2,'two actual matched-N pilot units');
 const found=new Set();
 for(const value of pair.arms){
  need([comparison.A,comparison.B].includes(value.arm)&&!found.has(value.arm),'one unit per matched arm');found.add(value.arm);
  need(value.caseId===id&&value.n===n&&value.warmups===3&&value.samples===1&&value.freshOwnedProcess===true,'whole warmed pilot unit');
  need(value.rawExitCode===0&&value.ownedGroupGone===true&&value.cleanTerminal===true&&value.allRawRetained===true&&value.finalSourceAuditPassed===true,'actual clean reviewed pilot outcome');
  positive(value.sampleMs,'positive actual full-unit pilot ms');positive(value.wholeProcessMs,'positive actual whole-process ms');
  need(value.sampleMs<=600000&&value.wholeProcessMs<=7200000,'finite original public/worker ceiling');
  need(value.wholeProcessMs>=value.sampleMs,'whole-process operational interval contains public call');
 }
 return pair.arms.every(v=>v.sampleMs>=50);
}
export function chooseMatchedN(pairs,id,comparisonId){
 need(Array.isArray(pairs)&&pairs.length>0&&pairs.length<=candidateNs(id).length,'finite empirical pilot curve');
 const candidates=candidateNs(id);let winner=null;
 for(let i=0;i<pairs.length;i++){
  need(winner===null,'no post-winner candidates silently pooled');
  if(pilotPairModel(pairs[i],id,candidates[i],comparisonId))winner=pairs[i];
 }
 need(winner!==null,'BOTH arms must empirically reach50ms within case cap; no omission/clipping/extrapolation');
 return Object.freeze({comparison:comparisonId,caseId:id,n:winner.n,targetMs:50,
  perArm:Object.freeze(winner.arms.map(v=>Object.freeze({arm:v.arm,pilotBatchMs:v.sampleMs,
   pilotPerOperationMs:v.sampleMs/winner.n,pilotWholeProcessMs:v.wholeProcessMs}))),
  empiricalMatchedN:true,authorizesTiming:false});
}
// Exact original formula. No old16-iteration helper and no deadline extension.
export function workerBudget({pilotPerOperationMs,n,pilotWholeProcessMs}){
 positive(pilotPerOperationMs,'positive empirical per-operation pilot');positive(pilotWholeProcessMs,'positive whole-process pilot');
 integer(n,1,32768,'bounded N');
 const ms=Math.ceil(2*pilotPerOperationMs*n*(3+7)+pilotPerOperationMs*n+120000+
  2*Math.max(0,pilotWholeProcessMs-pilotPerOperationMs));
 need(Number.isSafeInteger(ms)&&ms>0&&ms<=7200000,'original budget exceeds ceiling: refuse entire phase');return ms;
}
export function matchedPlan(calibrations){
 need(Array.isArray(calibrations)&&calibrations.length===60,'complete2comparison30case matched-N plan');
 const seen=new Set(),rows=[];
 for(const comparison of COMPARISONS)for(let id=0;id<30;id++){
  const found=calibrations.filter(v=>v.comparison===comparison.id&&v.caseId===id);
  need(found.length===1&&found[0].empiricalMatchedN===true,'one empirically reviewed result per case/comparison');const v=found[0];nValue(id,v.n);
  need(v.perArm.length===2&&[comparison.A,comparison.B].every(arm=>v.perArm.some(x=>x.arm===arm)),'exact two pilot arms');
  for(const unit of v.perArm){positive(unit.pilotBatchMs,'actual pilot batch');positive(unit.pilotPerOperationMs,'derived empirical per operation');positive(unit.pilotWholeProcessMs,'actual pilot whole process');
   need(unit.pilotBatchMs>=50&&unit.pilotBatchMs<=600000&&unit.pilotWholeProcessMs>=unit.pilotBatchMs&&unit.pilotWholeProcessMs<=7200000&&unit.pilotPerOperationMs===unit.pilotBatchMs/v.n,'empirical target and exact per-operation derivation');}
  const key=comparison.id+':'+id;need(!seen.has(key),'unique match');seen.add(key);
  for(const arm of [comparison.A,comparison.B]){const actual=v.perArm.find(x=>x.arm===arm);rows.push(Object.freeze({comparison:comparison.id,caseId:id,arm,n:v.n,
   workerTimeoutMs:workerBudget({...actual,n:v.n}),publicCallHardMs:600000}));}
 }
 return Object.freeze(rows);
}
export function metric({logicalBytes,n,elapsedNs}){
 integer(logicalBytes,0,524288,'logical uncompressed bytes');integer(n,1,32768,'operation N');
 need(typeof elapsedNs==='string'&&/^[1-9][0-9]{0,18}$/.test(elapsedNs),'positive retained nanosecond decimal');
 const seconds=Number(BigInt(elapsedNs))/1e9;
 return Object.freeze({operationsPerSecond:n/seconds,uncompressedBytesPerSecond:logicalBytes===0?null:logicalBytes*n/seconds,
  unit:'uncompressed fixture bytes for encode and decode',controlSubtraction:false});
}
export const PLAN_MATH=Object.freeze({comparisons:2,cases:30,repetitions:3,armsPerComparison:2,
 timingWorkers:360,codecBatchCalls:360*(3+7),controlCalls:360*6,controlOperations:2160,
 independentUnits:'three fresh processes per arm/case/comparison; seven within-worker samples correlated',
 maxPilotPairs:2*(18*16+12*8),maxPilotWorkers:2*2*(18*16+12*8),
 pilotControlsIfEveryCandidateRuns:6*2*2*(18*16+12*8),
 pilotCountsAreSeparateFromOriginalTimingCounts:true});
