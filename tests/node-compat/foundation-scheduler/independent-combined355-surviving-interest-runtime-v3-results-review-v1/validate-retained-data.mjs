// Prepared pure retained-DATA validation, never application/module/guest calls.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {plannedCalls,validateSession,validateWasmtime} from '../combined-native-runtime-candidate-v3/session-model.mjs';
import {terminalModel} from '../combined-native-runtime-candidate-v3/models.mjs';
import * as collectors from '../combined-clock-lifecycle-candidate-v2/collectors.mjs';
import {parseScalarStringOutput} from '../clock-v13-runtime-candidate-v2/wave.mjs';
const P=dirname(fileURLToPath(import.meta.url)),json=async p=>JSON.parse(await readFile(p)),input=await json(join(P,'intake-summary.json'));
assert.equal(input.originalRootTerminalSupplied,true,'No live or partial output inspection');assert.equal(input.state,'INDEPENDENT_SURVIVING_INTEREST_RUNTIME_V3_ACTUAL_READ_ONLY_INTAKE_PASSED');
const sha=b=>createHash('sha256').update(b).digest('hex');let checks=0;
async function exact(r){const b=await readFile(r.path);assert.equal(b.length,r.bytes);assert.equal(sha(b),r.sha256);checks++;return b;}
const refs=await json(join(P,'../combined-native-runtime-candidate-v3/references.json')),fixture=(await json(refs.fixtureCatalogue.path)).fixtures.find(x=>x.id==='surviving-interest'),result=JSON.parse((await exact(input.result)).toString()),root=input.actualOutputRoot;
assert.equal(result.state,'COMBINED355_RUNTIME_COMPLETE_UNREVIEWED_V3');assert.equal(result.fixtureId,'surviving-interest');assert.deepEqual(result.sourceIndex,input.sourceIndex);assert.equal(result.sessions.length,5);checks+=4;
const values=[],sessions=[],pids=new Set();
for(let n=0;n<2;n++){
 const scenario=n===0?'retained':'fresh',session=result.sessions[n],count=n===0?3:1;assert.equal(session.host,'jco-standard-shim');assert.equal(session.scenario,scenario);
 const t=JSON.parse((await exact(session.terminal)).toString());terminalModel(t);assert(!pids.has(t.pid));pids.add(t.pid);assert.equal(t.executable,refs.node.path);assert.deepEqual(t.args,[join(P,'../combined-native-runtime-candidate-v3/entry.mjs'),'worker',JSON.stringify(input.runtimeConfig),scenario]);
 const child=JSON.parse((await exact(session.result)).toString());assert.equal(child.state,'COMBINED355_JCO_SESSION_COMPLETE_UNREVIEWED_V3');assert.equal(child.fixtureId,'surviving-interest');assert.equal(child.scenario,scenario);assert.deepEqual(child.sourceIndex,input.sourceIndex);assert.equal(child.rawAttempts,count);assert.equal(child.rawWritten,count);assert.equal(child.captureFailures,0);assert.deepEqual(child.finalProtectionErrors,[]);
 const rows=[];for(let i=1;i<=count;i++)rows.push(await json(join(root,scenario,'raw',String(i).padStart(3,'0')+'.json')));
 const validation=validateSession(fixture,scenario,rows,collectors);assert.deepEqual(validation,child.validation);assert.deepEqual(validation,session.validation);assert.equal(plannedCalls('surviving-interest',scenario).length,count);
 const observed=[],ids=new Set();
 for(let i=0;i<count;i++){const v=collectors.validateSurvivingInterest(rows[i].observed.value);assert.equal(v.calls,i+1);assert.deepEqual(v.values,['a','b']);assert.deepEqual(v.events,['job-before-timers','timer-a','job-after-a','timer-b','fence']);assert.equal(v.ids.length,11);assert.deepEqual(v.cancelled,v.ids.slice(0,8));assert.equal(v.cancelledCallbacks,0);assert.equal(v.pendingPromiseResolved,true);for(const id of v.ids){assert(!ids.has(id));ids.add(id);}values.push(v);observed.push(v);checks+=9;}
 assert.equal(ids.size,count*11);const stdout=JSON.parse((await exact(t.stdout)).toString());assert.equal(stdout.root,join(root,scenario));assert.equal(stdout.completeUnreviewed,true);assert.deepEqual(stdout.index,{...session.index,path:'index.json'});assert.deepEqual(stdout.completion,{...session.completion,path:'completion.json'});
 sessions.push({host:'jco-standard-shim',scenario,pid:t.pid,publicStrings:count,callCounters:observed.map(v=>v.calls),uniqueIdsWithinSession:ids.size,values:observed});checks+=19;
}
for(let n=0;n<3;n++){
 const session=result.sessions[n+2];assert.equal(session.host,'stock-wasmtime42');assert.equal(session.fresh,true);assert.equal(session.literalInvoke,'run()');const t=JSON.parse((await exact(session.terminal)).toString());terminalModel(t);assert(!pids.has(t.pid));pids.add(t.pid);assert.equal(t.executable,refs.wasmtime.path);assert.deepEqual(t.args,['run','--invoke','run()',input.component.path]);
 const raw=parseScalarStringOutput({stdoutBytes:await exact(t.stdout),rawDurablyRetained:true}),saved=await json(join(root,'wasmtime-'+n+'.decoded.json'));assert.equal(saved.returnedType,'string');assert.equal(saved.value,raw);assert.deepEqual(saved.rawStdout,t.stdout);
 const validation=validateWasmtime(fixture,raw,saved.hostWallBeforeMs,saved.hostWallAfterMs,collectors);assert.deepEqual(validation,session.validation);const v=collectors.validateSurvivingInterest(raw);assert.deepEqual(validation.fullValue,v);assert.equal(v.calls,1);values.push(v);sessions.push({host:'stock-wasmtime42',fresh:true,pid:t.pid,publicStrings:1,callCounters:[1],uniqueIdsWithinSession:11,values:[v]});checks+=13;
}
const coverage={jcoRetainedStrings:3,jcoFreshStrings:1,freshWasmtimeStrings:3};assert.equal(pids.size,5);assert.equal(values.length,7);assert.deepEqual(result.coverage,coverage);checks+=3;
const counts={wholePublicStrings:values.length,registrationIdObservations:values.reduce((a,v)=>a+v.ids.length,0),cancelledIdObservations:values.reduce((a,v)=>a+v.cancelled.length,0),resolvedPromiseValueObservations:values.reduce((a,v)=>a+v.values.length,0),orderedEventObservations:values.reduce((a,v)=>a+v.events.length,0)};assert.deepEqual(counts,{wholePublicStrings:7,registrationIdObservations:77,cancelledIdObservations:56,resolvedPromiseValueObservations:14,orderedEventObservations:35});checks++;
for(const key of ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','nativeOffsetInterestDropOrTeardownProved','fullSixFixturesAccepted','all17GatesSatisfied','fullProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']){assert.equal(result[key],false);checks++;}
console.log(JSON.stringify({schemaVersion:1,state:'INDEPENDENT_RETAINED_SURVIVING_INTEREST_RAW_DATA_SEMANTICS_PASSED',checks,coverage,sessions,publicObservations:counts,typedNodeStrings:4,fullWaveStringsDecoded:3,distinctFreshOwnedChildren:5,allWholeValuesParsedWithoutClipping:true,allCancelledCallbacksZero:true,allOrderedEventsAndPromiseValuesValidated:true,uniqueTimerIdsScope:'Within each component instance, including33 across three retained calls; no numericID uniqueness acrossfreshinstances claim',allInvalidNativeTaskSelectionProved:false,nativeInterestDropHandleGcOrTeardownCountsObserved:false,crossHostExactByteEqualityClaim:false,apiHelperOrGuestReruns:false}));
