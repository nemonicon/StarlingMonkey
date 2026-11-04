// Pure source/metadata tests only. No compiler, componentizer, or guest runs.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {fixture} from './source-model-fixture.mjs';
import {selectClassicPin,variants} from './runtime-contract.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));const hash=value=>createHash('sha256').update(value).digest('hex');
const root=resolve(process.env.NODE_COMPAT_CLASSIC_TEST_ROOT??'/tmp/starling-node-compat/classic-integration-source-tests-v1');
const module=await import(pathToFileURL(join(root,'tests/node-compat/classic-streams-admission.mjs')));
const selection=await import(pathToFileURL(join(root,'tests/node-compat/module-selection.mjs')));
const policy=JSON.parse(await readFile(join(HERE,'policy.json'))),pins=JSON.parse(await readFile(join(HERE,'admission-pins.json')));
const checks=[];const positive=(name,run)=>{run();checks.push({name,passed:true});};
const negative=(name,run)=>{assert.throws(run,undefined,name);checks.push({name,passed:true,expectedRejection:true});};
const make=async options=>{const model=await fixture({sourceRoot:root,...options});return{...model,options:{sourceRoot:model.sourceRoot,parentProtectedSources:model.parentProtectedSources,parentProtectedPatch:model.parentProtectedPatch}};};
const full=await make();
positive('actual342 bytes + explicitly synthetic ON model',()=>assert.equal(module.validateClassicSourceModel(full.metadata,full.options).sourceInputs,342));
negative('synthetic models rejected by production admission',()=>module.validateClassicSourceAdmission(full.metadata,full.options));
assert(!Object.hasOwn(full.metadata,'engineSha256')&&!Object.hasOwn(full.metadata,'engineBytes'));
checks.push({name:'synthetic model contains no invented engine pin',passed:true});
for(const options of [{classic:false},{classic:false,web:false},{classic:true,web:false},{classic:false,ticks:false,web:false},{entropy:'runtime-only'},{gc:true}]){
 const model=await make(options);positive('finite source model '+JSON.stringify(options),()=>module.validateClassicSourceModel(model.metadata,model.options));
}
function mutate(name,change){const model=structuredClone(full);change(model.metadata);negative(name,()=>module.validateClassicSourceModel(model.metadata,model.options));}
mutate('unknown recipe',m=>m.buildRecipeSha256='0'.repeat(64));
mutate('old306 inventory cannot be relabelled342',m=>m.sourceManifest=policy.parentExpectedNativeSourceManifest);
mutate('diagnostic flag refused',m=>m.diagnosticOnly=true);
mutate('diagnostic policy refused',m=>m.internalTickDiagnosticPolicy={});
mutate('no implicit classic bool',m=>delete m.classicStreamsEnabled);
mutate('wrong observed classic option',m=>m.observedCMakeOptions.NODE_COMPAT_CLASSIC_STREAMS='OFF');
mutate('wrong requested classic option',m=>m.requestedCMakeOptions.NODE_COMPAT_CLASSIC_STREAMS='OFF');
for(const name of ['internalTicksEnabled','eventsEnabled','stringDecoderEnabled'])mutate('classic prerequisite '+name,m=>m[name]=false);
mutate('parent source layer before image',m=>m.internalTickPolicy.sourceLayer['cmake/builtins.cmake'].beforeSha256='0'.repeat(64));
mutate('parent private policy pin',m=>m.internalTickPolicy.parentPrivateTickPolicyFileSha256='0'.repeat(64));
mutate('source input changed',m=>m.sourceManifest[0].sha256='0'.repeat(64));
mutate('duplicate source',m=>m.sourceManifest[1]=m.sourceManifest[0]);
mutate('additional source',m=>m.sourceManifest.push({path:'runtime/extra.cpp',sha256:'0'.repeat(64)}));
mutate('missing queue command',m=>m.internalTickPolicy.actualLayoutCompileCommands=m.internalTickPolicy.actualLayoutCompileCommands.filter(v=>!v.includes('/runtime/node_tick_queue.cpp')));
mutate('missing kernel command',m=>m.internalTickPolicy.actualLayoutCompileCommands=m.internalTickPolicy.actualLayoutCompileCommands.filter(v=>!v.includes('/stream-web-kernel.cpp')));
mutate('duplicate native command',m=>m.internalTickPolicy.actualLayoutCompileCommands.push(m.internalTickPolicy.actualLayoutCompileCommands[0]));
mutate('missing private CLASSIC macro',m=>{const i=m.internalTickPolicy.actualLayoutCompileCommands.findIndex(v=>v.includes('/builtins/node-compat/register.cpp'));m.internalTickPolicy.actualLayoutCompileCommands[i]=m.internalTickPolicy.actualLayoutCompileCommands[i].replace(' -DNODE_COMPAT_CLASSIC_STREAMS=1','');});
mutate('spurious CLASSIC macro outside private target',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]+=' -DNODE_COMPAT_CLASSIC_STREAMS=1');
mutate('unknown native command',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]+=' -c /synthetic/extra.cpp');
for(const extra of [' -UNODE_COMPAT_CLASSIC_STREAMS',' -U NODE_COMPAT_CLASSIC_STREAMS',' -D NODE_COMPAT_CLASSIC_STREAMS=1',' -DNODE_COMPAT_CLASSIC_STREAMS=0',' -DNODE_COMPAT_CLASSIC_STREAMS=1',' -DDEBUG=1',' -UNDEBUG']){
 mutate('conflicting/unsafe native option '+extra,m=>{const row=m.internalTickPolicy.actualLayoutCompileCommands.findIndex(v=>v.includes('/builtins/node-compat/register.cpp'));m.internalTickPolicy.actualLayoutCompileCommands[row]+=extra;});
}
mutate('missing actual O3',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]=m.internalTickPolicy.actualLayoutCompileCommands[0].replace(' -O3',''));
mutate('missing NDEBUG',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]=m.internalTickPolicy.actualLayoutCompileCommands[0].replace(' -DNDEBUG',''));
mutate('embedding CLASSIC must be absent',m=>m.internalTickPolicy.actualEmbeddingCompileCommands[0]+=' -DNODE_COMPAT_CLASSIC_STREAMS=1');
mutate('embedding split undef forbidden',m=>m.internalTickPolicy.actualEmbeddingCompileCommands[0]+=' -U NODE_COMPAT_INTERNAL_TICKS');
mutate('no extra classic embedding patch',m=>m.componentizeJsPatches.push({name:'fake-classic',sha256:'0'.repeat(64)}));
mutate('no debug receipt',m=>m.observedCMakeOptions.CMAKE_BUILD_TYPE='Debug');
mutate('no WEVAL receipt',m=>m.observedCMakeOptions.WEVAL='ON');
mutate('no unlocked Rust receipt',m=>m.generatedRustProject.cargoBuildLocked=false);
const off=await make({classic:false,web:false,ticks:false});
for(const suffix of ['/stream-web-kernel.cpp','/runtime/node_tick_queue.cpp']){
 const changed=structuredClone(off);changed.metadata.internalTickPolicy.actualLayoutCompileCommands.push(full.metadata.internalTickPolicy.actualLayoutCompileCommands.find(row=>row.includes(suffix)));
 negative('slim inactive TU forbidden '+suffix,()=>module.validateClassicSourceModel(changed.metadata,changed.options));
}
const runtimeGC=await make({entropy:'runtime-only'});runtimeGC.metadata.gcStress=true;for(const key of ['requestedCMakeOptions','observedCMakeOptions'])runtimeGC.metadata[key].NODE_COMPAT_GC_STRESS='ON';
negative('runtime GC not a finite producer mode',()=>module.validateClassicSourceModel(runtimeGC.metadata,runtimeGC.options));
for(const name of ['recipe-transformations.json','selector-transformations.json']){
 const proof=JSON.parse(await readFile(join(HERE,name)));const target=name.startsWith('recipe')?'build-engine.sh':'module-selection.mjs';let text=await readFile(join(HERE,'source/tests/node-compat',target),'utf8');
 assert.equal(hash(text),proof.afterSha256);for(const edit of [...proof.edits].reverse()){assert.equal(text.split(edit.new).length-1,edit.count??1);text=text.split(edit.new).join(edit.old);}assert.equal(hash(text),proof.beforeSha256);checks.push({name:'reverse byte identity '+target,passed:true});
}
const oldAdmission=await readFile(join(root,'tests/node-compat/private-ticks-admission.mjs'));
positive('old306 admission module unchanged',()=>assert.equal(hash(oldAdmission),pins.current306AdmissionSha256));
const freeze='/tmp/starling-node-compat/production-scheduler-artifacts-v1/native-freeze';
for(const label of ['normal-off','normal-runtime','gc-off']){
 const metadata=JSON.parse(await readFile(join(freeze,label+'.engine.wasm.build.json')));
 const observed=selection.selectedManifestsForEngine(metadata,{sourceRoot:join(freeze,'source')});
 assert(!observed.some(manifest=>Object.hasOwn(manifest.modules,'node:stream')));checks.push({name:'unchanged actual historical306 admission '+label,passed:true,scope:'Source/metadata replay only; no engine executed'});
}
const runtimePins=JSON.parse(await readFile(join(HERE,'runtime-pins.json')));
for(const variant of variants)negative('null actual pin stops before loader '+variant,()=>selectClassicPin(runtimePins,{variant,recipeSha256:pins.productionRecipeSha256}));
negative('no unknown RuntimeGC variant',()=>selectClassicPin(runtimePins,{variant:'gc-runtime',recipeSha256:pins.productionRecipeSha256}));
const classicManifest=JSON.parse(await readFile(join(root,policy.classicManifest)));
positive('exact Node22 root24 promises3 bindings',()=>{assert.equal(classicManifest.modules['node:stream'].exports.length,24);assert.equal(classicManifest.modules['node:stream/promises'].exports.length,3);});
const nativeMap=selection.builtinMap([selection.coreManifest,classicManifest]);
for(const id of policy.newModuleIds)positive('finite real manifest map '+id,()=>assert(nativeMap[id]));
assert.equal(classicManifest.profileVersion,'sm-node-22.14.0-m0.12');
const {createProfilePlugin}=await import(pathToFileURL(join(root,'tests/node-compat/profile-bundler.mjs')));
const selectedPlugin=createProfilePlugin(()=>assert.fail('Parsing not needed for literal resolution'),{builtinManifests:[selection.coreManifest,classicManifest]});
const disabledPlugin=createProfilePlugin(()=>assert.fail('Parsing not needed for literal resolution'),{builtinManifests:[selection.coreManifest]});
for(const id of policy.newModuleIds){positive('native admission precedes available adapters '+id,()=>assert.deepEqual(selectedPlugin.resolveId(id),{id:id.replace(/^stream/,'node:stream'),external:true}));negative('disabled classic rejects before adapter '+id,()=>disabledPlugin.resolveId(id));}
for(const id of ['node:process','process','node:stream/consumers','stream/consumers','node:stream/unknown'])negative('unselected builtin '+id,()=>selectedPlugin.resolveId(id));
const result={schemaVersion:1,state:'CLASSIC_INTEGRATION_SOURCE_AND_SYNTHETIC_MODEL_TESTS_PASSED',node:process.version,checks:checks.length,passed:checks.length,failures:0,
 syntheticMetadataOnly:true,compilerInvoked:false,componentizerInvoked:false,guestInvoked:false,enginePinsInvented:false,sourceRoot:root,observations:checks};
const output=resolve(process.env.NODE_COMPAT_CLASSIC_HOST_TEST_OUTPUT??join(HERE,'host-test-results.json'));await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,checks:checks.length,output}));
