// Pure/mock/source-JSON checks only. Never launches a worker or real session.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {candidateNs,nValue,chooseMatchedN,workerBudget,timingSchedule,PLAN_MATH,matchedPlan,metric,COMPARISONS} from './planner.mjs';
import {CompactCollector,aggregate,decodeRetainedString,emptyCounts,NAMES} from './collector.mjs';
import {CallWatchdog,remainingBudget,lifecycleBounds,armedAck,validateArmedAck} from './lifecycle-policy.mjs';
import {scalarArguments,validateNamespace} from './loading.mjs';
import {injectedWorker} from './worker.template.mjs';
import {replayWorker,aggregateTiming} from './result-collector.mjs';
import {contractModel,same,quietWindowModel,providerComparisons} from './proof-model.mjs';
import {compactExpectations} from './compact-plan.mjs';
import {phaseAuthorityModel} from './parent-guard.template.mjs';
let checks=0;const check=(fn)=>{fn();checks++;},reject=fn=>check(()=>assert.throws(fn)),clone=v=>JSON.parse(JSON.stringify(v));
check(()=>assert.equal(timingSchedule().length,360));check(()=>assert.equal(PLAN_MATH.codecBatchCalls,3600));check(()=>assert.equal(PLAN_MATH.controlCalls,2160));
check(()=>assert.equal(PLAN_MATH.maxPilotWorkers,1536));check(()=>assert.equal(PLAN_MATH.pilotControlsIfEveryCandidateRuns,9216));
check(()=>assert.deepEqual(candidateNs(18),[1,2,4,8,16,32,64,128]));reject(()=>nValue(18,256));reject(()=>nValue(0,3));reject(()=>nValue(-0,1));reject(()=>nValue(30,1));
check(()=>assert.equal(workerBudget({pilotPerOperationMs:2,n:32,pilotWholeProcessMs:500}),122340));reject(()=>workerBudget({pilotPerOperationMs:1e9,n:1,pilotWholeProcessMs:1e9}));reject(()=>workerBudget({pilotPerOperationMs:0,n:1,pilotWholeProcessMs:5}));
const unit=(arm,n,ms)=>({arm,caseId:0,n,warmups:3,samples:1,freshOwnedProcess:true,rawExitCode:0,ownedGroupGone:true,cleanTerminal:true,allRawRetained:true,finalSourceAuditPassed:true,sampleMs:ms,wholeProcessMs:1000});
const pair=(n,a,b)=>({comparison:'same-engine-provider',caseId:0,n,arms:[unit('native-on',n,a),unit('fflate-on',n,b)]});
check(()=>assert.equal(chooseMatchedN([pair(1,52,20),pair(2,55,51)],0,'same-engine-provider').n,2));
reject(()=>chooseMatchedN([pair(1,52,20)],0,'same-engine-provider'));reject(()=>chooseMatchedN([pair(2,60,60)],0,'same-engine-provider'));
reject(()=>chooseMatchedN([pair(1,60,60),pair(2,70,70)],0,'same-engine-provider'));
const unclean=pair(1,60,60);unclean.arms[1].ownedGroupGone=false;reject(()=>chooseMatchedN([unclean],0,'same-engine-provider'));
reject(()=>remainingBudget({startMs:0,nowMs:8,globalBudgetMs:10,workerBudgetMs:3}));check(()=>remainingBudget({startMs:0,nowMs:7,globalBudgetMs:10,workerBudgetMs:3}));
check(()=>lifecycleBounds({timeoutMs:7200000,maxOutputBytes:1048576}));reject(()=>lifecycleBounds({timeoutMs:7200001,maxOutputBytes:1}));reject(()=>lifecycleBounds({timeoutMs:5,maxOutputBytes:1048577}));
const watch=new CallWatchdog();check(()=>watch.accept({event:'cost-public-call-start',sequence:0,name:'batch'},100));check(()=>assert.equal(watch.expired(600101),true));reject(()=>watch.finish());reject(()=>watch.accept({event:'cost-public-call-start',sequence:0,name:'batch'},101));reject(()=>watch.accept({event:'cost-public-call-end',sequence:0,name:'setup'},105));check(()=>watch.accept({event:'cost-public-call-end',sequence:0,name:'batch'},110));check(()=>assert.equal(watch.finish(),1));
const announcing={event:'cost-public-call-start',sequence:4,name:'batch'};check(()=>validateArmedAck(JSON.stringify(armedAck(announcing)),announcing));reject(()=>validateArmedAck(JSON.stringify({...armedAck(announcing),sequence:5}),announcing));reject(()=>validateArmedAck('',announcing));
for(const args of[['batch',[0,32768]],['batch',[18,128]],['batch',[119,1]],['setup',[29]],['identity',[]]])check(()=>scalarArguments(...args));
for(const args of[['batch',[18,256]],['batch',[60,2]],['batch',[120,1]],['batch',[0,3]],['setup',[-0]],['observe',[0]],['stage',['x']],['validate',['x']]])reject(()=>scalarArguments(...args));
const ns=Object.fromEntries(NAMES.map(n=>[n,()=>{}]));ns._util={};check(()=>validateNamespace(ns));ns._util.extra=1;reject(()=>validateNamespace(ns));delete ns._util.extra;ns.then=()=>{};reject(()=>validateNamespace(ns));
const receipt={path:'raw.json',sha256:'a'.repeat(64),bytes:1,fsynced:true,fullPrimitiveCaptured:true};reject(()=>decodeRetainedString('null',{...receipt,fsynced:false}));reject(()=>decodeRetainedString('{}',{...receipt,fullPrimitiveCaptured:false}));reject(()=>decodeRetainedString('{',receipt));reject(()=>decodeRetainedString('{"n":1e999}',receipt));
check(()=>assert.equal(metric({logicalBytes:0,n:1,elapsedNs:'50000000'}).uncompressedBytesPerSecond,null));check(()=>assert.equal(metric({logicalBytes:64,n:2,elapsedNs:'50000000'}).uncompressedBytesPerSecond,2560));
reject(()=>metric({logicalBytes:64,n:1,elapsedNs:'0'}));
const expected={schemaVersion:1,caseId:6,caseName:'codec-v1.small-repeat.deflateSync',arm:'native-on',direction:'encode',logicalBytes:64,inputBytes:64,inputFNV:123,outputBytes:19,outputFNV:456,oracleSha256:'b'.repeat(64),inputSource:'raw-fixture',parentDeclaredInputSha256:null,timingNMax:32768};
const descriptorRow={path:'/private/tmp/fixture.json',sha256:'a'.repeat(64),bytes:10};
const job={schemaVersion:1,jobId:'pure-mock',phase:'timing',comparison:'same-engine-provider',repetition:0,side:'A',expected,n:2,warmups:3,samples:7,publicCallHardMs:600000,workerTimeoutMs:200000,
 sourceIndexSha256:'c'.repeat(64),rootAuthority:descriptorRow,sourceIndependentReviewIndex:descriptorRow,phaseAuthority:descriptorRow,quietWindowAuthority:descriptorRow,warmNPlan:descriptorRow};
const window=bytes=>({byteOffset:8,byteLength:bytes,backingBytes:bytes+16,prefix:Array(8).fill(165),suffix:Array(8).fill(90),construction:'new ordinary ArrayBuffer; fixed/attached/unshared by construction'});
// An ordinary synthetic return table, not an import/evaluation of guest code.
function mockSession(value){const c=clone(value);let counts=emptyCounts(),active=false;const records=[];
 const state=()=>active?{activeCaseId:c.caseId,inputSource:c.inputSource,stagedValidation:null,prepared:true,retainedUntimedOutput:false}:{activeCaseId:null,inputSource:null,stagedValidation:null,prepared:false,retainedUntimedOutput:false};
 function invoke(name,args){counts.publicFunctionEntries++;counts.perExportEntries[name]++;let v;
  if(name==='identity')v={schemaVersion:1,kind:'codec-cost-identity-v1',version:'bounded-zlib-cost-guest-v1',provider:c.arm==='native-on'?'native':'fflate',providerSourceVersion:c.arm==='native-on'?'registered-node-zlib-m0.13':'fflate-browser-0.8.3',oracleSha256:c.oracleSha256,primaryCases:30,controlCaseRanges:{consumeInput:[30,59],copyInputAndConsume:[60,89],harnessNoCodec:[90,119]},exports:[...NAMES],snapshotState:{prepared:false,staged:false,retainedOutput:false,codecCalls:0,resources:0},counterMeaning:'named-function entries including internal validate calls; outer host calls are parent raw records',codecPrewarmedAtSnapshot:false};
  else if(name==='setup'){active=true;v={schemaVersion:1,kind:'codec-cost-setup-v1',caseId:c.caseId,caseName:c.caseName,inputSource:c.inputSource,input:window(c.inputBytes),inputFNV1aU32:c.inputFNV,parentDeclaredInputSha256:c.parentDeclaredInputSha256,oracleSha256:c.oracleSha256,stagedValidationCleared:true,priorOutputCleared:true};}
  else if(name==='checkpoint'){v={schemaVersion:1,kind:'codec-cost-checkpoint-v1',before:state(),input:{...window(c.inputBytes),fnv1aU32:c.inputFNV,matchesSetupFNV:true,sentinelsUnchanged:true},preparedAndStageAndPriorOutputCleared:true,gcOrResetInvoked:false};active=false;}
  else if(args[0]>=30){counts.controlOperations++;const control=args[0]<60?'consumeInput':args[0]<90?'copyInputAndConsume':'harnessNoCodec';v={schemaVersion:1,kind:'codec-cost-control-v1',caseId:args[0],primaryCaseId:c.caseId,control,operations:1,result:control==='harnessNoCodec'?{bytesConsumed:0,declaredInputBytes:c.inputBytes,tag:2166136261,copies:0,codecCalls:0}:{bytesConsumed:c.inputBytes,fnv:c.inputFNV,copies:control==='copyInputAndConsume'?1:0,codecCalls:0},logicalUncompressedBytes:c.logicalBytes};}
  else{const n=args[1];counts.codecCalls+=n;v={schemaVersion:1,kind:'codec-cost-batch-v1',caseId:c.caseId,caseName:c.caseName,provider:c.arm==='native-on'?'native':'fflate',operations:n,inputBytes:c.inputBytes,logicalUncompressedBytesPerOperation:c.logicalBytes,totalLogicalUncompressedBytes:c.logicalBytes*n,totalOutputBytes:c.outputBytes*n,lastOutputBytes:c.outputBytes,lastOutputFNV1aU32:c.outputFNV,aggregateFNV1aU32:aggregate(c.outputFNV,c.outputBytes,n),outputArraysRetained:false};}
  v.counters=clone(counts);v.state=state();records.push(clone(v));return JSON.stringify(v);
 }
 return{invoke,recheck:async()=>{},records};
}
async function mockRun({value=job,session=mockSession(value.expected),clockBad=false,mutate=null}={}){
 const writes=new Map(),markers=[];let clock=0n;
 const write=async(name,data)=>{writes.set(name,clone(data));if(mutate)mutate(name);return{path:name,sha256:'a'.repeat(64),bytes:Buffer.byteLength(JSON.stringify(data))};};
 const resources={boundarySamples:['after-source-authentication-before-loader','after-reviewed-esm-tla-load','after-final-source-audit'].map(label=>({label,rssBytes:1000,nodePublicMaxRssKilobytes:10})),reviewedEsmTlaLoadNs:'1000000',nodePublicMaxRssKilobytes:10,maxRssUnits:'Node22 resourceUsage API kilobytes',rssUnits:'bytes',wholeNodeProcessOnly:true,includesAuthenticationAndLoaderOverhead:true,parentHugeProofAndOracleReportsLoaded:false,guestHeapOrCapacityClaim:false,continuousRssSamplingClaim:false,physicallyColdStartupClaim:false};
 try{await injectedWorker({descriptor:value,session,clock:{nowNs:()=>{if(clockBad)return 0n;clock+=10000000n;return clock;}},write,recheck:async()=>{},onCallStart:e=>markers.push(e),onCallEnd:e=>markers.push(e),resourceFacts:()=>resources});return{writes,markers,result:writes.get('worker-results.json')};}
 catch(error){return{writes,markers,error};}
}
const good=await mockRun();check(()=>assert.equal(good.error,undefined));check(()=>assert.equal(good.result.records.length,20));check(()=>assert.equal(good.result.counts.codecCalls,20));check(()=>assert.equal(good.result.counts.controlOperations,6));check(()=>assert.equal(good.markers.length,40));
const handshakeOrder=[],handshakeSession=mockSession(expected),originalInvoke=handshakeSession.invoke;
handshakeSession.invoke=(...args)=>{handshakeOrder.push('invoke');return originalInvoke(...args);};let handshakeClock=0n;
await injectedWorker({descriptor:job,session:handshakeSession,clock:{nowNs:()=>{handshakeClock+=1000000n;return handshakeClock;}},
 write:async(name,value)=>{if(name.endsWith('-before.json'))handshakeOrder.push('precall-fsynced');if(name.endsWith('-raw.json'))handshakeOrder.push('raw-fsynced');return{path:name,sha256:'a'.repeat(64),bytes:JSON.stringify(value).length};},recheck:async()=>{},
 onCallStart:async()=>{handshakeOrder.push('announcement');await Promise.resolve();handshakeOrder.push('parent-armed-ack');},onCallEnd:()=>handshakeOrder.push('end'),resourceFacts:()=>({mockOnly:true})});
check(()=>assert.deepEqual(handshakeOrder.slice(0,6),['precall-fsynced','announcement','parent-armed-ack','invoke','raw-fsynced','end']));
const terminal={pid:100,status:0,closed:true,ownedGroupGone:true,terminalExitZeroObserved:true,timedOut:false,signal:null,spawnError:null,externalSignal:null,outputLimitExceeded:false,errors:[],signals:[],operationalElapsedMs:2000};
const rawCalls=good.result.records.map(r=>good.writes.get(r.raw.path));const replay=replayWorker({job,result:good.result,rawCalls,terminal});check(()=>assert.equal(replay.measuredSamples.length,7));check(()=>assert.equal(replay.rawControls.length,6));
const tampered=clone(rawCalls);tampered[8].returned.value=tampered[8].returned.value.replace('"lastOutputBytes":19','"lastOutputBytes":20');reject(()=>replayWorker({job,result:good.result,rawCalls:tampered,terminal}));
reject(()=>replayWorker({job,result:good.result,rawCalls,terminal:{...terminal,ownedGroupGone:false}}));
const badClock=await mockRun({clockBad:true});check(()=>assert(badClock.error));check(()=>assert([...badClock.writes.keys()].some(n=>n.endsWith('-raw.json'))));
let opaqueInspected=false;const opaque=Object.defineProperty({},'then',{get(){opaqueInspected=true;throw Error('must not inspect');}});const opaqueRun=await mockRun({session:{invoke:()=>opaque,recheck:async()=>{}}});check(()=>assert(opaqueRun.error));check(()=>assert.equal(opaqueInspected,false));check(()=>assert.equal(opaqueRun.writes.get('0000-identity-before-raw.json').returned.kind,'opaque'));
const mutable=clone(job);const mutation=await mockRun({value:mutable,mutate:()=>{mutable.n=32769;mutable.expected.inputFNV=999;}});check(()=>assert.equal(mutation.error,undefined));check(()=>assert.equal(mutation.result.n,2));
const zero={...expected,caseId:0,caseName:'codec-v1.empty.deflateSync',logicalBytes:0,inputBytes:0,inputFNV:2166136261,outputBytes:8};const empty=await mockRun({value:{...job,expected:zero}});check(()=>assert.equal(empty.error,undefined));
reject(()=>phaseAuthorityModel(null,'c'.repeat(64)));reject(()=>phaseAuthorityModel({state:'ROOT_REVIEWED_FRESH_ZLIB350_COST_ACTION_V1'},'c'.repeat(64)));
const q={schemaVersion:1,state:'ROOT_COORDINATED_CODEC_MEASUREMENT_QUIET_WINDOW_V1',exclusiveMeasurementApproved:true,runId:'r',sourceIndexSha256:'c'.repeat(64),phase:'timing',startsAtUtc:'2026-01-01T00:00:00.000Z',expiresAtUtc:'2026-01-01T01:00:00.000Z'};
check(()=>quietWindowModel(q,{runId:'r',sourceSha:'c'.repeat(64),phase:'timing',nowUtcMs:Date.parse('2026-01-01T00:01:00.000Z'),globalBudgetMs:1000}));reject(()=>quietWindowModel(q,{runId:'r',sourceSha:'c'.repeat(64),phase:'timing',nowUtcMs:Date.parse('2026-01-01T01:00:00.000Z'),globalBudgetMs:1}));
const HERE=dirname(fileURLToPath(import.meta.url));
// Existing authenticated proof JSON is DATA only. No guard/preflight imported or called.
for(const name of['independent-cost-jco-correctness-v3-results-review-v1','independent-cost-wasmtime-strings-v1-results-review-v1','independent-cost-jco-control-v2-results-review-v1']){
 const base=join(HERE,'..',name),data=JSON.parse(await readFile(join(base,'results.json'))),contract=JSON.parse(await readFile(join(base,'result-contract.json'))),ix=JSON.parse(await readFile(join(base,'index.json')));
 const rows=ix.files.map(r=>({...r,path:join(base,r.path)}));check(()=>contractModel(data,contract,rows));const bad=clone(data);bad.verifiedPassed=false;reject(()=>contractModel(bad,contract,rows));
}
const read=async path=>JSON.parse(await readFile(join(HERE,'..',path)));
const artifactResults=Object.fromEntries(await Promise.all(['native-on','fflate-on','fflate-off'].map(async arm=>[arm,await read('independent-cost-component-v3-results-review-v1/'+arm+'/results.json')])));
check(()=>providerComparisons(artifactResults));const wrongBundle=clone(artifactResults);wrongBundle['fflate-off'].code.bytes++;reject(()=>providerComparisons(wrongBundle));
const compact=compactExpectations({cases:await read('cost-jco-correctness-candidate-v2/cases.json'),inputFacts:await read('independent-cost-jco-control-v2-results-review-v1/expected-input-facts.json'),rawFixtures:(await read('cost-guest-oracle-candidate-v2/raw-fixture-oracle.json')).fixtures,streams:(await read('independent-cost-jco-correctness-v3-results-review-v1/reviewed-encoder-streams.json')).streams,oracleSha256:'bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5'});
check(()=>assert.equal(compact.length,90));check(()=>assert(Buffer.byteLength(JSON.stringify({expected:compact,artifacts:Object.fromEntries(Object.entries(artifactResults).map(([arm,v])=>[arm,{parentAuditedActualComponent:true,...Object.fromEntries(['component','glue','core','dts','wit','transpileMetadata','packageJson'].map(k=>[k,v[k]]))}]))},null,2))<128*1024));
const fakeTiming=[];let pid=1000;
for(const spec of timingSchedule())fakeTiming.push({...replay,...spec,jobId:String(pid),pid:pid++,n:2,measuredSamples:Array.from({length:7},()=>({elapsedNs:'50000000'}))});
check(()=>assert.equal(aggregateTiming(fakeTiming).groups.length,60));const duplicate=clone(fakeTiming);duplicate[1].pid=duplicate[0].pid;reject(()=>aggregateTiming(duplicate));
console.log(JSON.stringify({schemaVersion:1,state:'CODEC_PILOT_TIMING_PURE_MOCK_SOURCE_DATA_CHECKS_PASSED',checks,realClockRead:false,filesystemWrites:false,ownedWorkerOrGuestOrCodecOrPreflightOrJcoOrWasmtimeOrPilotTimingExecuted:false,existingProofsReadAsJsonDataOnly:true}));
