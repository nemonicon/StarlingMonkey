// Source parser tests only. Synthetic models cannot enter production admission.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS&&!process.env.NODE_PATH);
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..'),stage='/tmp/starling-node-compat/trace-integration-source-model-v2',relative='tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1';
const checks=[],pass=name=>checks.push(name),copy=value=>JSON.parse(JSON.stringify(value));
const hash=value=>createHash('sha256').update(value).digest('hex');
const contract=JSON.parse(await readFile(join(here,'contract.json')));
const {fixture}=await import(pathToFileURL(join(stage,relative,'source-model-fixture.mjs')));
const {validateClassicSourceModel,validateClassicSourceAdmission}=await import(pathToFileURL(join(stage,'tests/node-compat/classic-streams-admission.mjs')));
const {selectedManifestsForEngine}=await import(pathToFileURL(join(stage,'tests/node-compat/module-selection.mjs')));
const {validateClassicSourceAdmission:previousAdmission}=await import(pathToFileURL(join(repo,'tests/node-compat/classic-streams-admission.mjs')));
const {selectClassicPin}=await import('./runtime-contract.mjs');
const {classify}=await import('./artifact-tools/metadata-admission.mjs');
function reject(name,fn){assert.throws(fn);pass(name);}
let baseline;
for(const label of ['normal-off','normal-runtime','gc-off','disabled-off']){
 const model=await fixture({sourceRoot:stage,classic:label!=='disabled-off',entropy:label==='normal-runtime'?'runtime-only':'off',gc:label==='gc-off'});
 const options={sourceRoot:stage,parentProtectedSources:model.parentProtectedSources,parentProtectedPatch:model.parentProtectedPatch};
 assert.equal(model.metadata.syntheticMetadataOnly,true);assert(!('engineSha256'in model.metadata)&&!('enginePath'in model.metadata));
 const admitted=validateClassicSourceModel(model.metadata,options);assert.equal(admitted.sourceInputs,342);assert.equal(admitted.branch,'sm-private-ticks-classic-streams-trace-source-v1');pass('explicit synthetic parser model '+label);
 reject('production admission refuses synthetic '+label,()=>validateClassicSourceAdmission(model.metadata,options));
 reject('unchanged real selector refuses synthetic '+label,()=>selectedManifestsForEngine(model.metadata,{sourceRoot:stage}));
 reject('artifact source classifier refuses synthetic '+label,()=>classify(model.metadata,label));
 if(label==='normal-off')baseline={metadata:model.metadata,options};
}
const mutate=(name,fn)=>{const metadata=copy(baseline.metadata);fn(metadata);reject(name,()=>validateClassicSourceModel(metadata,baseline.options));};
mutate('missing explicit trace source provenance',m=>delete m.classicTraceSourcePolicy);
mutate('unknown fix source lineage',m=>m.classicTraceSourcePolicy.fixSourceIndexSha256='0'.repeat(64));
mutate('wrong previous342 ancestry',m=>m.classicTraceSourcePolicy.previousPolicySha256='0'.repeat(64));
mutate('old source recipe identity',m=>m.buildRecipeSha256=contract.previousRecipeSha256);
mutate('old source helper identity',m=>m.classicStreamsPolicy.helperSha256=contract.previousHelperSha256);
mutate('old source policy identity',m=>m.internalTickPolicy.policyFileSha256=contract.previousPolicySha256);
mutate('old core bytes in full342 inventory',m=>m.sourceManifest.find(row=>row.path.endsWith('/classic-core.generated.mjs')).sha256='ba39701153094c6481464fa3f45a7afd87e6d41d673026e8008e12f2693802bf');
mutate('missing one native source',m=>m.sourceManifest.pop());
mutate('duplicate one native source',m=>m.sourceManifest[1]=m.sourceManifest[0]);
mutate('arbitrary strict policy suffix refused',m=>m.strictEventExceptionPolicy.version+='-trace');
mutate('arbitrary protected policy suffix refused',m=>m.protectedAbortListenerPolicy.version+='-trace');
mutate('diagnostic-only source model refused',m=>m.diagnosticOnly=true);
mutate('runtime plus GC remains outside finite producer',m=>{m.gcStress=true;m.entropyPolicy='runtime-only';m.requestedCMakeOptions.NODE_COMPAT_GC_STRESS='ON';m.observedCMakeOptions.NODE_COMPAT_GC_STRESS='ON';m.requestedCMakeOptions.NODE_COMPAT_ENTROPY_MODE='RUNTIME_ONLY';m.observedCMakeOptions.NODE_COMPAT_ENTROPY_MODE='RUNTIME_ONLY';});
for(const flag of ['-O0','-O3','-Og','-Ofast','-DNDEBUG=0','-UNDEBUG','-DDEBUG','-UDEBUG','-DNODE_COMPAT_OOM_TESTING=1','-UNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_INTERNAL_TICKS=0','-UNODE_COMPAT_STRICT_INITIALIZATION','-D']){
 mutate('conflicting native flag '+flag,m=>m.internalTickPolicy.actualLayoutCompileCommands[0]+=' '+flag);
 mutate('conflicting embedding flag '+flag,m=>m.internalTickPolicy.actualEmbeddingCompileCommands[0]+=' '+flag);
}
const oldPins=JSON.parse(await readFile(join(repo,'tests/node-compat/foundation-classic-streams/production-runtime-activated-v3/runtime-pins.json')));
for(const [label,pin]of Object.entries(oldPins.variants)){
 const old=JSON.parse(await readFile(pin.enginePath+'.build.json'));
 assert.equal(old.buildRecipeSha256,contract.previousRecipeSha256);
 reject('unchanged old actual metadata refused by successor '+label,()=>validateClassicSourceAdmission(old,baseline.options));
 reject('previous admission rejects changed source root '+label,()=>previousAdmission(old,baseline.options));
}
reject('old reviewed artifact document not reusable',()=>selectClassicPin(oldPins,{recipeSha256:contract.productionRecipeSha256}));
const nullPins=JSON.parse(await readFile(join(here,'runtime-pins.json')));
assert(Object.values(nullPins.variants).every(value=>value===null));
for(const variant of Object.keys(nullPins.variants))reject('NULL new pins stop '+variant,()=>selectClassicPin(nullPins,{variant,recipeSha256:contract.productionRecipeSha256}));
const result={schemaVersion:1,state:'TRACE_INTEGRATION_SYNTHETIC_SOURCE_PARSER_TESTS_PASSED_NOT_ARTIFACT_PROOF',passed:checks.length,checks,
 explicitSyntheticModels:true,modelHasEngineIdentifiers:false,oldActualMetadataUnmodified:true,oldEnginesNotRead:true,
 productionPositiveAdmissionPendingFreshActualBuild:true,node:{version:process.version,executable:process.execPath,sha256:hash(await readFile(process.execPath))},
 preflightPackageConfigureNativeGuestTargetHostOrTimingExecuted:false};
await writeFile(join(here,'evidence/node-source-tests.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,passed:checks.length}));
