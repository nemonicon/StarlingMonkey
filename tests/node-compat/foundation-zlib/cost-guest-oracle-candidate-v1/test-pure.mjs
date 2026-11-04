// PURE source/data/staging tests. No codec module or guest/provider is imported.
import assert from 'node:assert/strict';
import {Buffer} from 'node:buffer';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fixtureSpecs,fixtureBytes,consumeFNV1a} from './fixtures.mjs';
import {cases,MAX_INPUT,MAX_WIRE,caseSelection,operationCount,base64,unbase64,stageRecord,jsonRecord,wire,bytesEqual,aggregateStep} from './contract.mjs';
import {ownedWindow,unchangedWindow} from './owned-window.mjs';
import {createRuntime} from './runtime.mjs';
import {renderNodeInputs} from './render-node-inputs.mjs';
import {adler32,crc32} from './framing.mjs';
import {transportValue} from './node-transport.mjs';
const checks=[],hash=raw=>createHash('sha256').update(raw).digest('hex');
const check=(name,run)=>{run();checks.push(name);};
const root=new URL('./',import.meta.url),golden=JSON.parse(await readFile(new URL('raw-fixture-oracle.json',root)));
check('exact30codecCartesianCases',()=>{assert.equal(cases.length,30);assert.equal(new Set(cases.map(row=>row.id)).size,30);for(let i=0;i<30;i++){assert.equal(cases[i].index,i);assert.equal(cases[i].fixture,fixtureSpecs[Math.floor(i/6)].id);}});
for(let i=0;i<fixtureSpecs.length;i++)check('fullPureFixtureSHAAndFNV:'+fixtureSpecs[i].id,()=>{const raw=fixtureBytes(fixtureSpecs[i]),expected=golden.fixtures[i];assert.equal(raw.length,expected.bytes);assert.equal(hash(raw),expected.rawSha256);assert.equal(consumeFNV1a(raw),expected.rawFNV1aU32);});
for(const length of[0,1,2,3,4,64,524288])check('canonicalBase64FullBytes:'+length,()=>{const raw=Uint8Array.from({length},(_,i)=>(i*17+3)&255),encoded=base64(raw);assert(encoded===Buffer.from(raw).toString('base64'),'whole canonical base64');assert(bytesEqual(unbase64(encoded),raw),'whole decoded bytes');});
for(const invalid of['A','AA','AAA','A===','AA=A','AB==','AAB=','AA==\n','AA-_','!!!!','===='])check('invalidBase64Refuses:'+JSON.stringify(invalid),()=>assert.throws(()=>unbase64(invalid)));
check('base64DecodedCapBeforeAllocation',()=>assert.throws(()=>unbase64('AAAA',2)));
check('unknownDecodedBoundRefuses',()=>assert.throws(()=>unbase64('',Infinity)));
check('actualWireStringTypesAndCaps',()=>{assert.throws(()=>jsonRecord(3));assert.throws(()=>jsonRecord('x'.repeat(MAX_WIRE+1)));assert.throws(()=>wire({value:'x'.repeat(MAX_WIRE)}));});
for(const index of[30,59,60,89,90,119])check('finiteControlId:'+index,()=>{const selected=operationCount(index,1);assert.equal(selected.primary.index,index%30);assert.notEqual(selected.kind,'codec');assert.throws(()=>operationCount(index,2));});
for(const invalid of[-1,NaN,1.5,120,'1',4294967296])check('badCaseId:'+String(invalid),()=>assert.throws(()=>caseSelection(invalid)));
check('finiteSmallAndLargeNBounds',()=>{operationCount(0,32768);assert.throws(()=>operationCount(0,32769));operationCount(18,128);assert.throws(()=>operationCount(18,129));assert.throws(()=>operationCount(0,0));});
check('pureChecksumKnownVectors',()=>{const bytes=Uint8Array.from([49,50,51,52,53,54,55,56,57]);assert.equal(crc32(bytes),0xcbf43926);assert.equal(adler32(bytes),0x091e01de);});
check('aggregateFNVOrderAndLengthIncluded',()=>{const a=aggregateStep(2166136261,17,64,0);assert.notEqual(a,aggregateStep(2166136261,17,65,0));assert.notEqual(a,aggregateStep(2166136261,17,64,1));});
const structuralBytes=new Uint8Array([1,2,3]);
const structuralRecord=caseId=>{const row=cases[caseId];return{schemaVersion:1,kind:'codec-cost-stage-v1',caseId,fixture:row.fixture,format:row.format,provider:'node-22.14.0',streamId:'node-22.14.0.'+row.fixture+'.'+row.format,encodedBytes:structuralBytes.length,encodedFNV1aU32:consumeFNV1a(structuralBytes),encodedSha256:hash(structuralBytes),encodedBase64:base64(structuralBytes)};};
// These are deliberately NOT claimed to be compressed streams. They exercise
// byte/ID/state transport only; any provider invocation would fail the test.
check('structuralStageTransportOnly',()=>{const checked=stageRecord(structuralRecord(1));assert(bytesEqual(checked.bytes,structuralBytes));});
for(const [name,change]of[
 ['unknownKey',row=>({...row,unreviewed:true})],['wrongKind',row=>({...row,kind:'unknown'})],['encoderCase',row=>({...row,caseId:0})],['wrongFormat',row=>({...row,format:'raw'})],['wrongFixture',row=>({...row,fixture:'unknown'})],['wrongProvider',row=>({...row,provider:'host-fallback'})],['wrongStream',row=>({...row,streamId:'untrusted'})],['wrongLength',row=>({...row,encodedBytes:4})],['wrongFNV',row=>({...row,encodedFNV1aU32:0})],['badSHA',row=>({...row,encodedSha256:'F'.repeat(64)})],['tooManyBytes',row=>({...row,encodedBytes:MAX_INPUT+1})]
])check('stageRefuses:'+name,()=>assert.throws(()=>stageRecord(change(structuralRecord(1)))));
check('ordinaryOwnedWindowByteOffsetAndSentinels',()=>{const value=ownedWindow(Buffer,structuralBytes);assert.equal(value.input.byteOffset,8);assert.equal(value.input.buffer.byteLength,19);assert(unchangedWindow(value,structuralBytes));value.input[0]=9;assert(!unchangedWindow(value,structuralBytes));value.all[0]=0;assert(!unchangedWindow(value));});
let forbiddenProviderCalls=0;const methods=Object.fromEntries([...new Set(cases.map(row=>row.operation))].map(name=>[name,()=>{forbiddenProviderCalls++;throw new Error('FORBIDDEN_CODEC_CALL_IN_PURE_TEST');}]));
const provider={id:'native',sourceVersion:'STRUCTURAL_SPY_NOT_A_CODEC',Buffer,methods};
const inputs={schemaVersion:1,kind:'codec-cost-node-inputs-v1',oracleSha256:hash(Buffer.from('PURE_STRUCTURAL_DATA_NOT_A_CODEC_ORACLE')),records:cases.filter(row=>row.direction==='decode').map(row=>structuralRecord(row.index))};
check('nullOracleInputsFailBeforeAnyProvider',()=>assert.throws(()=>createRuntime({provider,oracleInputs:null})));
const runtime=createRuntime({provider,oracleInputs:inputs}),decode=raw=>{assert.equal(typeof raw,'string','all proposed export returns are strings');return JSON.parse(raw);};
check('initialSnapshotEmptyAndCounterMeaning',()=>{const value=decode(runtime.identity());assert.deepEqual(value.snapshotState,{prepared:false,staged:false,retainedOutput:false,codecCalls:0,resources:0});assert.equal(value.counters.publicFunctionEntries,1);assert.equal(value.counters.codecCalls,0);assert.equal(value.counters.perExportEntries.identity,1);});
for(let i=0;i<30;i++)check('setupOnlyNoCodec:'+i,()=>{const value=decode(runtime.setup(i));assert.equal(value.caseId,i);assert.equal(value.counters.codecCalls,0);assert.equal(value.stagedValidationCleared,true);assert.equal(value.state.stagedValidation,null);assert.equal(value.state.retainedUntimedOutput,false);});
check('sixControlsN1NoCodec',()=>{runtime.setup(6);for(let round=0;round<2;round++)for(const offset of[30,60,90]){const value=decode(runtime.batch(6+offset,1));assert.equal(value.primaryCaseId,6);assert.equal(value.operations,1);assert.equal(value.counters.codecCalls,0);assert.equal(value.state.retainedUntimedOutput,false);}assert.equal(decode(runtime.identity()).counters.controlOperations,6);});
check('stagingRequiresSetupAndExactActiveCase',()=>{runtime.checkpoint();assert.throws(()=>runtime.stage(JSON.stringify(structuralRecord(1))));runtime.setup(1);assert.throws(()=>runtime.stage(JSON.stringify(structuralRecord(3))));assert.throws(()=>runtime.observe(1));assert.equal(forbiddenProviderCalls,0);});
check('stageCompactMetadataNoCodecAndSetupClears',()=>{runtime.setup(1);const ack=decode(runtime.stage(JSON.stringify(structuralRecord(1))));assert.equal(ack.codecInvoked,false);assert.equal(ack.decodedBytes,3);assert.equal(ack.sha256RecomputedInGuest,false);assert.equal(ack.parentDeclaredSha256,hash(structuralBytes));assert.equal(ack.state.stagedValidation.caseId,1);assert(!Object.hasOwn(ack,'encodedBase64'));const next=decode(runtime.setup(1));assert.equal(next.state.stagedValidation,null);assert.equal(next.inputSource,'node-oracle-input');});
check('wrongOrMissingActiveInputStopsBeforeCodec',()=>{runtime.checkpoint();assert.throws(()=>runtime.observe(0));runtime.setup(0);assert.throws(()=>runtime.observe(1));assert.throws(()=>runtime.batch(0,0));assert.throws(()=>runtime.batch(120,1));assert.throws(()=>runtime.batch(30,2));assert.equal(forbiddenProviderCalls,0);});
for(const value of[{schemaVersion:1,kind:'arbitrary',caseId:0},{schemaVersion:1,kind:'primary',caseId:30},{schemaVersion:1,kind:'primary',caseId:0,script:'not allowed'},{schemaVersion:1,kind:'crossdecode',caseId:0,stageRecord:structuralRecord(1)}])check('validateRejectsBeforeProvider:'+checks.length,()=>assert.throws(()=>runtime.validate(JSON.stringify(value))));
check('checkpointClearsStateNotCountersNoReset',()=>{const before=decode(runtime.identity()).counters.publicFunctionEntries,value=decode(runtime.checkpoint());assert.equal(value.counters.publicFunctionEntries,before+1);assert.equal(value.gcOrResetInvoked,false);assert.deepEqual(value.state,{activeCaseId:null,inputSource:null,stagedValidation:null,prepared:false,retainedUntimedOutput:false});});
check('rendererDigestBeforeParseAndWrongStateRefuses',()=>{const bad=new Uint8Array([123]);assert.throws(()=>renderNodeInputs(bad,'0'.repeat(64)),/digest BEFORE/);assert.throws(()=>renderNodeInputs(bad,hash(bad)),SyntaxError);const wrong=Buffer.from(JSON.stringify({schemaVersion:1,state:'wrong'}));assert.throws(()=>renderNodeInputs(wrong,hash(wrong)));});
check('noCodecSpyEverCalled',()=>assert.equal(forbiddenProviderCalls,0));
for(const value of[undefined,null,true,false,17,-0,NaN,Infinity,-Infinity,12345678901234567890n,'full string'])check('typedNodeCarrier:'+checks.length,()=>{const result=transportValue(value);assert.equal(result.type,typeof value);assert.equal(result.fullPrimitiveValueCaptured,true);assert.doesNotThrow(()=>JSON.stringify(result));});
check('opaqueNodeCarrierDoesNotInspectProperties',()=>{let reads=0;const opaque={toJSON(){reads++;throw new Error('no serialization');}};Object.defineProperty(opaque,'buffer',{get(){reads++;throw new Error('no getter');}});for(const value of[opaque,()=>{},Symbol('opaque')]){const record=transportValue(value);assert.equal(record.kind,'opaque');assert.equal(record.propertiesRead,false);assert.doesNotThrow(()=>JSON.stringify(record));}assert.equal(reads,0);});
const authority=JSON.parse(await readFile(new URL('future-authority.json',root)));check('allPositiveAuthorityRemainsNull',()=>{assert.equal(authority.actionsAllowed,false);assert.equal(authority.operationalAdmission,false);for(const key of['rootActionAuthority','costToolingIndex','actualNodeOracle','renderedNodeInputs','actualEmittedABI','actualComponentTuples','actual45EncoderOutputs','actual135CrossDecodeEdges','additionalFfOffProof','timingPhaseAuthority'])assert.equal(authority[key],null);});
const path=process.env.CODEC_COST_PURE_RESULTS;assert(path,'Fresh explicit pure result path required');
await writeFile(path,JSON.stringify({schemaVersion:1,state:'PURE_CODEC_COST_SOURCE_DATA_AND_STAGING_CHECKED',passed:checks.length,checks,forbiddenProviderCalls,fixtureHashesOnly:true,structuralTransportBytesAreNotCodecFixtures:true,actualCodecOrFflateNodeZlibOracleBundleComponentGuestHostPilotOrTimingExecuted:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({passed:checks.length,codecCalls:forbiddenProviderCalls,sourceOnly:true}));
