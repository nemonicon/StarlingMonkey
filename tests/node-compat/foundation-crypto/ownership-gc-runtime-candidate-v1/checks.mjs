// Public records only. This module never imports a guest or invokes crypto.
import {need} from '../ownership-component-candidate-v1/authority.mjs';
export const EXPECTED='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7';
const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export const PRESSURE_DELTAS=Object.freeze([4,4,8,0]);
const COUNTERS=['inspectCalls','runCalls','clearCalls','validateCalls','keyImportsAttempted','keyImportsFulfilled','signCalls','verifyCalls'];
export function zeroCounters(){return Object.fromEntries(COUNTERS.map(n=>[n,0]));}
function initial(r){need(equal(r.initial,{keyImportsAttempted:0,signCalls:0,verifyCalls:0,retainedKeys:0,pendingOperations:0}),'Snapshot-local initial counters');}
export function counters(r,expected){need(equal(r.counters,expected),'Exact complete public counters');}
export function state(r,raw,jwk){need(equal(r.state,{rawRetained:raw,jwkRetained:jwk,strongApplicationKeyOwners:Number(raw)+Number(jwk),pendingOperationsInstrumented:false,finalizersOrWipesObserved:false}),'Exact public strong-owner state; no native heap claim');}
function operation(r,extractable,oracle){
 need(r&&r.firstSignatureHex===EXPECTED&&r.secondSignatureHex===EXPECTED&&r.firstSignatureHex===oracle.tagHex&&r.signatureBytes===32&&r.valid===true&&r.invalid===false,'Complete known-answer/Node signatures and verify booleans');
 for(const n of ['priorFullBytesStable','independentNonemptyBacking','mutationRestored'])need(r[n]===true,'Public full-byte ownership '+n);
 const k=r.key,a=k.algorithm;need(k.instanceOfGlobalCryptoKey===true&&k.globalConstructorStable===true&&k.type==='secret'&&k.extractable===extractable&&equal(Object.keys(a).sort(),['hash','length','name'])&&a.name==='HMAC'&&a.length===160&&equal(a.hash,{name:'SHA-256'})&&equal(k.usages,['sign','verify']),'Full selected key metadata');
 need(r.inputBeforeHex===r.inputAfterHex&&r.inputBeforeHex==='a5'.repeat(8)+'4869205468657265'+'a5'.repeat(8),'Full message window/sentinels');
 need(equal(r.inputWindow,{byteOffset:8,byteLength:8,backingBytes:24}),'Offset and backing length');
 need(r.signatureBeforeHex===r.signatureAfterHex&&r.signatureBeforeHex==='a5'.repeat(8)+EXPECTED+'a5'.repeat(8),'Full signature window/sentinels');
}
export function runRecord(r,id,expected,oracle,gcExpected){
 need(r?.schemaVersion===1&&r.kind==='crypto-owner-run-v1'&&r.caseId===id&&r.completed===true,'Whole successful bounded case '+id);initial(r);counters(r,expected);state(r,true,id!==0||expected.keyImportsFulfilled>1);
 need(equal(r.gcObservation,gcObservation('this-run',PRESSURE_DELTAS[id],PRESSURE_DELTAS[id]))&&r.finalizerCountOrWipeProof===false&&Array.isArray(r.observations),'Truthful scoped public pressure observations; no native GC count');observations(r.observations,id);
 if(id<2){need(r.result.format===(id===0?'raw':'jwk')&&r.result.importInputPreserved===true,'Raw/JWK import copy');need(r.result[id===0?'callerKeyBytesChangedAfterImport':'callerJwkChangedAfterImport']===true,'Caller mutation after import');operation(r.result.operations,id===1,oracle);if(id===0)need(r.result.callerBackingHex==='a5'.repeat(8)+'00'.repeat(20)+'a5'.repeat(8),'Complete mutated caller backing');}
 else if(id===2){need(r.result.format==='retained-pair'&&r.result.strongApplicationOwners===true,'Retained pair');operation(r.result.raw,false,oracle);operation(r.result.jwk,true,oracle);}
 else{
  const p=r.result;for(const refusal of [p.signRefusal,p.verifyRefusal,p.ordinaryInvalid])need(refusal.kind==='native-promise-rejection'&&refusal.error.typeError===true&&refusal.error.thrownType==='object','Identifiable native Promise TypeError refusal');
  for(const reads of [p.signConversionReads,p.verifyConversionReads])need(equal(reads,{algorithmName:0,dataByteLength:0,dataPrimitive:0,dataString:0,signatureByteLength:0,signaturePrimitive:0}),'Refusal before harmless conversions');
  need(p.positiveAlgorithmReads===1&&p.positiveVerifyAlgorithmReads===1&&p.positiveFullSignatureHex===EXPECTED&&p.constructorError.typeError===true&&p.onlyNewGuardedArtifactAllowed===true&&p.uniqueNativeErrorCauseInferred===false,'Positive getter controls and explicit guard scope');
  need(equal(p.getters.map(v=>v.name),['algorithm','extractable','type','usages'])&&p.getters.every(v=>v.error.typeError===true),'All prototype getter refusals');
 }
 const whole=structuredClone(gcExpected.records[id]);whole.counters=expected;whole.state=publicState(true,id!==0||expected.keyImportsFulfilled>1);wholeEqual(r,whole,'Whole typed run record, no extra/omitted fields');return true;
}
function observations(rows,id){
 const exercise=['sign:before','sign:returned','sign:before','sign:returned','verify:before','verify:returned','verify:before','verify:returned'];
 const wanted=id<2?['importKey:before','importKey:returned',...exercise]:id===2?[...exercise,...exercise]:['prototype-sign:returned','prototype-verify:returned','sign:before','sign:returned','verify:before','verify:returned','ordinary-invalid-key:returned'];
 need(equal(rows.map(v=>v.operation+':'+v.phase),wanted),'Complete ordered operation observations');let verifies=0;
 for(const row of rows){if(row.phase==='before')need(equal(row.returned,{type:'undefined'}),'Before observation records undefined');else if(row.operation==='sign')need(equal(row.returned,{type:'ArrayBuffer',bytes:32,fullHex:EXPECTED,fullBytesRetained:true}),'Complete native signature return');else if(row.operation==='verify'){need(equal(row.returned,{type:'boolean',value:id===3||verifies%2===0}),'Full true/false verification return');verifies++;}else if(row.operation==='importKey')need(equal(row.returned,{type:'object',opaque:true,fullOpaqueValueClaim:false}),'Opaque native key return is not claimed fully inspected');else need(row.record?.kind==='native-promise-rejection'&&row.record.error.typeError===true,'Recorded prototype/invalid refusal');}
}
export function nextRun(c,id){const r={...c,runCalls:c.runCalls+1};if(id<2){r.keyImportsAttempted++;r.keyImportsFulfilled++;r.signCalls+=2;r.verifyCalls+=2;}else if(id===2){r.signCalls+=4;r.verifyCalls+=4;}else{r.signCalls+=3;r.verifyCalls+=2;}return r;}
export function inspectRecord(r,c,raw,jwk,gcExpected){need(r?.schemaVersion===1&&r.kind==='crypto-owner-inspect-v1'&&r.globalCryptoKeyInstalled===true&&r.constructorStable===true&&r.cryptoOperationsAtSnapshot===0&&r.fullNativeOwnershipOrZeroizationObserved===false,'Installed globals and bounded snapshot observation');initial(r);counters(r,c);state(r,raw,jwk);const whole=structuredClone(gcExpected.before);whole.counters=c;whole.state=publicState(raw,jwk);wholeEqual(r,whole,'Whole typed inspect');return true;}
export function clearRecord(r,c,gcExpected){need(r?.kind==='crypto-owner-clear-v1'&&r.applicationReferencesReleased===true&&r.collectionOrNativeFreeOrWipeObserved===false,'Only application refs released');initial(r);counters(r,c);state(r,false,false);const whole=structuredClone(gcExpected.released);whole.counters=c;wholeEqual(r,whole,'Whole typed clear');return true;}
export function validateRecord(r,oracle,gcExpected){
 need(r?.schemaVersion===2&&r.kind==='crypto-owner-within-export-gc-validation-v2'&&r.withinOneOuterExport===true&&r.separateHostCallInterleavingProved===false&&r.finalizerOrWipeObserved===false,'Within-one-export wrapper scope');need(equal(r.entryCounters,zeroCounters()),'Fresh wrapper zero entry counters');state({state:r.entryState},false,false);
 let c=zeroCounters();c.validateCalls++;c.inspectCalls++;inspectRecord(r.before,c,false,false,gcExpected);need(r.records.length===4,'All four wrapper cases');for(let id=0;id<4;id++){c=nextRun(c,id);runRecord(r.records[id],id,c,oracle,gcExpected);}c.clearCalls++;clearRecord(r.released,c,gcExpected);c.inspectCalls++;inspectRecord(r.after,c,false,false,gcExpected);wholeEqual(r,gcExpected,'Whole typed schema2 GC wrapper');return true;
}

export function gcObservation(scope,requests,records){return{version:'public-buffer-gc-pressure-v1',scope,publicGcPressureRequested:requests>0,publicGcPressureRequests:requests,publicGcPressureRecords:records,entropyRequested:false,actualNativeGcCountObserved:false,strongApplicationOwnersCombined:true,isolatedTemporaryRootsProved:false,finalizerFreeWipeObserved:false};}
export function publicState(raw,jwk){return{rawRetained:raw,jwkRetained:jwk,strongApplicationKeyOwners:Number(raw)+Number(jwk),pendingOperationsInstrumented:false,finalizersOrWipesObserved:false};}
export function canonical(v){if(Array.isArray(v))return v.map(canonical);if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])]));return v;}
export function wholeEqual(actual,expected,label){need(JSON.stringify(canonical(actual))===JSON.stringify(canonical(expected)),label);return true;}
