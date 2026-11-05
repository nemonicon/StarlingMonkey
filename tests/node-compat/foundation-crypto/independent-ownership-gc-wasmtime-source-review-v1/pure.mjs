// Actual pure protocol/models only. No preflight, oracle or host/guest operation.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {validateArgv,argvAudit,parseScalarStringOutput,checkWholeRecord} from '../ownership-gc-wasmtime-candidate-v1/protocol.mjs';
import {authorityModel,jcoModel} from '../ownership-gc-wasmtime-candidate-v1/guard.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const SOURCE=join(HERE,'../ownership-gc-wasmtime-candidate-v1');
let checks=0;
function ok(value){assert(value);checks++;}
function rejects(fn){assert.throws(fn);checks++;}
const bytes=await readFile(join(SOURCE,'index.json'));
ok(createHash('sha256').update(bytes).digest('hex')==='c5d3ea491e81db5fad6c02e244bcc0cf784c8135a6ab1d5e552326f4f2e1ec35');
const refs=JSON.parse(await readFile(join(SOURCE,'references.json')));
const input=JSON.parse(await readFile('/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v2/wrapper/raw/001.json'));
const oracle=JSON.parse(await readFile('/private/tmp/starling-node-compat/crypto-owner355-gc-runtime-v2/node-oracle.json'));
const expected=JSON.parse(await readFile(refs.expectedCompleteRecord.path));
ok(checkWholeRecord(JSON.parse(input.value),oracle,input,expected)===true);
const wave=new TextEncoder().encode(JSON.stringify(input.value)+'\n');
ok(parseScalarStringOutput({stdoutBytes:wave,rawDurablyRetained:true})===input.value);
for(const data of [new Uint8Array([255,10]),new TextEncoder().encode('3\n'),new TextEncoder().encode(JSON.stringify(input.value)+'\n\n'),wave.subarray(0,wave.length-2),new TextEncoder().encode('junk'+JSON.stringify(input.value)+'\n')])rejects(()=>parseScalarStringOutput({stdoutBytes:data,rawDurablyRetained:true}));
rejects(()=>parseScalarStringOutput({stdoutBytes:wave,rawDurablyRetained:false}));
ok(JSON.stringify(validateArgv(refs.artifacts.component))===JSON.stringify(['run','--invoke','validate()',refs.artifacts.component.path]));
rejects(()=>validateArgv({...refs.artifacts.component,sha256:'0'.repeat(64)}));
rejects(()=>validateArgv({...refs.artifacts.component,bytes:1}));
ok(argvAudit(refs.wasmtime.path,validateArgv(refs.artifacts.component),{}).strictlyBelowArgMax===true);
for(const mutate of [v=>v.schemaVersion=1,v=>v.gcObservation.actualNativeGcCountObserved=true,v=>v.pressure.records.pop(),v=>v.records[0].result.operations.firstSignatureHex='00'.repeat(32),v=>v.records[0].counters.runCalls++]){
 const changed=structuredClone(expected);mutate(changed);rejects(()=>checkWholeRecord(changed,oracle,input,expected));
}
// Pure prospective fixtures are never issued as authority or actual proof.
const root=JSON.parse(await readFile(join(SOURCE,'future-root-authority.template.json')));
Object.assign(root,{state:'ROOT_REVIEWED_CRYPTO_OWNER355_GC_STOCK_WASMTIME_V1',sourceIndexSha256:'a'.repeat(64),wasmtimeValidateAllowed:true,publicBufferGcPressureAllowed:true,boundedKeyFixtureAllowed:true,sourceIndependentReview:{index:{},result:{}},jcoGcReview:{index:{},result:{}},jcoGcContract:{},externalController:{path:'/source-model-not-issued',sha256:'0'.repeat(64),bytes:0}});
ok(authorityModel(root,'a'.repeat(64))===true);
for(const [key,value]of [['freshProcesses',1],['invocation','validate(0)'],['nodeOracleAllowed',true],['generatedJsAllowed',true],['oomAllowed',true],['unsafePrototypeProbesAllowed',true],['operationalAdmission',true],['nativeGcCountObservedClaim',true],['externalParentDeadlineSeconds',1]])rejects(()=>authorityModel({...root,[key]:value},'a'.repeat(64)));
const proof={schemaVersion:1,state:'INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_RESULTS_REVIEW_PASSED_V2',verifiedPassed:true,sourceIndexSha256:refs.gcRuntimeSourceIndex.sha256,componentSha256:refs.artifacts.component.sha256,nativeEngineSha256:'289df4455b56b50a9598c42a7d924aaa2adca7f5461f96782f5758a979e966c8',nativeSourceFiles:355,generatedModuleImported:true,stockWasmtimeExecuted:false,publicBufferPressureFixtureExecuted:true,actualNativeGcCountObserved:false,operationalAdmission:false,runtimeAcceptanceClaim:false,coverage:{rawPublicStrings:23,runRecords:20,guestKeyImports:10,guestSignAttempts:55,guestVerifyAttempts:50,publicGcPressureRequests:{retained:48,fresh:16,wrapper:16,total:80},fullWrapperPressureRecords:16}};
jcoModel(proof,refs);ok(true);
for(const [key,value]of [['sourceIndexSha256','0'.repeat(64)],['generatedModuleImported',false],['stockWasmtimeExecuted',true],['actualNativeGcCountObserved',true],['runtimeAcceptanceClaim',true]])rejects(()=>jcoModel({...proof,[key]:value},refs));
rejects(()=>jcoModel({...proof,coverage:{...proof.coverage,fullWrapperPressureRecords:80}},refs));
await writeFile(join(HERE,'pure-results.json'),JSON.stringify({schemaVersion:1,checks,actualProtocolAndModelsImported:true,preflightCalled:false,nodeOracleCalled:false,wasmtimeCliInvoked:false,guestOrKeyOrPressureInvoked:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({checks,sourceOnly:true,ownerActionsInvoked:false}));
