// Source/pure DATA tests only: no admission/collector/monitor/guest/oracle actions.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {hostAuthority,actualRuntimeModel,artifactModel,plainHostEnvironment} from './entry.mjs';
import {validateArgv,argvAudit,parseScalarStringOutput,checkWholeRecord,strictTerminal} from './protocol.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),read=async p=>JSON.parse(await readFile(p,'utf8')),refs=await read(join(HERE,'references.json')),root=await read(join(HERE,'future-root-authority.template.json')),proof=await read(refs.actualRuntimeReview.result.path),contract=await read(refs.actualRuntimeContract.path),art=await read(refs.actualArtifactReview.result.path),ac=await read(refs.actualArtifactContract.path),wrapper=await read(contract.requiredExactDescriptors.rawWrapper.path),oracle=await read(contract.requiredExactDescriptors.nodeOracle.path),clone=structuredClone;
let cases=0;function pass(fn){assert.equal(fn(),true);cases++;}function refuses(fn){assert.throws(fn);cases++;}
const own={path:join(HERE,'index.json'),sha256:'0'.repeat(64),bytes:1},synthetic={...root,sourceIndex:own};pass(()=>hostAuthority(synthetic,own,refs));
for(const [k,v]of [['wasmtimeValidateAllowed',false],['guardedPrototypeCase3Allowed',false],['freshProcesses',2],['workerTimeoutMs',600001],['fullMetadataFields',80],['outputRoot','/tmp/wrong'],['actualHostReview',{}],['generatedJsAllowed',true],['retainedApiAllowed',true],['gcAllowed',true],['nodeOracleAllowed',true],['operationalAdmission',true]])refuses(()=>hostAuthority({...synthetic,[k]:v},own,refs));
refuses(()=>hostAuthority(synthetic,own,{...refs,actualRuntimeReview:null}));pass(()=>actualRuntimeModel(proof,contract,refs));
for(const [k,v]of [['caseRecords',19],['guestSignAttempts',54],['allFourCasesReviewed',false],['componentSha256','0'.repeat(64)],['fullMetadataFields',80],['operationalAdmission',true]])refuses(()=>actualRuntimeModel({...proof,[k]:v},contract,refs));
pass(()=>artifactModel(art,ac,refs));refuses(()=>artifactModel({...art,emittedImports:['wasi:random/random@0.2.10']},ac,refs));
pass(()=>plainHostEnvironment({}));for(const k of ['NODE_OPTIONS','NODE_PATH','RUST_LOG','RUST_BACKTRACE','WASMTIME_TEST_OVERRIDE'])refuses(()=>plainHostEnvironment({[k]:'1'}));
const argv=validateArgv(refs.artifacts.component);assert.deepEqual(argv,['run','--invoke','validate()',refs.artifacts.component.path]);cases++;
refuses(()=>validateArgv({...refs.artifacts.component,sha256:'0'.repeat(64)}));assert.equal(argvAudit(refs.wasmtime.path,argv,{}).strictlyBelowArgMax,true);cases++;
const value=wrapper.observed.value,bytes=new TextEncoder().encode(JSON.stringify(value)+'\n');assert.equal(parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:true}),value);cases++;
for(const text of ['','"x"\ntrailing','"x"\n\n','{}\n','"bad\\q"\n','"\\u{d800}"\n'])refuses(()=>parseScalarStringOutput({stdoutBytes:new TextEncoder().encode(text),rawDurablyRetained:true}));
refuses(()=>parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:false}));pass(()=>checkWholeRecord(JSON.parse(value),oracle,wrapper));
for(const mutate of [v=>v.records.pop(),v=>v.records[3].result.positiveFullSignatureHex='0'.repeat(64),v=>v.records[3].result.signConversionReads.algorithmName=1,v=>v.records[0].result.operations.inputWindow.byteOffset=0,v=>v.records[2].result.raw.priorFullBytesStable=false,v=>v.after.counters.signCalls--,v=>v.extra=true]){const v=JSON.parse(value);mutate(v);refuses(()=>checkWholeRecord(v,oracle,wrapper));}
const terminal={closed:true,status:0,signal:null,ownedGroupGone:true,terminalExitZeroObserved:true,spawnError:null,timedOut:false,externalSignal:null,outputLimitExceeded:false,errors:[],signals:[],signalCount:0,stderrFile:{bytes:0}};pass(()=>strictTerminal(terminal));
for(const [k,v]of [['status',1],['signal','SIGTERM'],['timedOut',true],['signalCount',1],['signals',[{signal:'SIGTERM'}]],['stderrFile',{bytes:1}],['ownedGroupGone',false],['outputLimitExceeded',true],['errors',[{}]]])refuses(()=>strictTerminal({...terminal,[k]:v}));
console.log(JSON.stringify({schemaVersion:1,pureCases:cases,passed:true,actualAcceptedDataReadOnly:true,inertOwnEntryImported:true,runSecretHostInvoked:false,wasmtimeOrCollectorOrMonitorOrGuestOrOracleInvoked:false,syntheticRootIsNotAuthority:true}));
