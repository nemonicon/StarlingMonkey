// Pure host models and genuine extracted caller seam; no packager/splicer load.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import vm from 'node:vm';
import { environmentModel, eligibilityModel, releaseMetadataModel, optionSnapshot } from './loader.mjs';
import { selectedInterfacePolicy, ENTROPY_ENTRY_PATCH_SHA256 } from '../../capability-policy.mjs';
const hash=b=>createHash('sha256').update(b).digest('hex');
const refs=JSON.parse(await readFile(new URL('./references.json',import.meta.url)));
const build=JSON.parse(await readFile(refs.toolsBuildReview.result.path));
const failed=JSON.parse(await readFile(refs.failedAdapterPhaseReview.result.path));
const metadata=JSON.parse(await readFile(refs.metadataReview.result.path));
let checks=0;
const yes=(f,label)=>{f();checks++;};
const no=(f,label)=>{assert.throws(f,undefined,label);checks++;};
yes(()=>environmentModel({},[],'v22.14.0','darwin','arm64'),'plain host');
for(const name of ['NODE_OPTIONS','NODE_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','DYLD_INSERT_LIBRARIES','LD_PRELOAD'])no(()=>environmentModel({[name]:'injected'},[],'v22.14.0','darwin','arm64'),name);
no(()=>environmentModel({},['--import=unreviewed'],'v22.14.0','darwin','arm64'),'execArgv');
no(()=>environmentModel({},[],'v24.0.0','darwin','arm64'),'version');
no(()=>environmentModel({},[],'v22.14.0','linux','arm64'),'platform');
yes(()=>eligibilityModel(build,failed,metadata,refs),'real three proof DATA composition');
for(const [which,key,value]of [['build','verifiedPassed',false],['failed','phasePassed',true],['failed','metadataDecoded',true],['metadata','adapterPromoted',true],['metadata','previousPhasePassed',true],['metadata','decodedPackageCount',5],['metadata','packageVersions',['0.2.10']]]){
  const values={build:structuredClone(build),failed:structuredClone(failed),metadata:structuredClone(metadata)};values[which][key]=value;
  no(()=>eligibilityModel(values.build,values.failed,values.metadata,refs),'composition '+key);
}
// Synthetic consistency fixture, NOT a native artifact frame or admission.
const native={fixturePurpose:'SYNTHETIC_HOST_CONSISTENCY_ONLY',engineSha256:'a'.repeat(64),profileEnabled:true,strictInitialization:true,abiFixEnabled:true,bigIntFixEnabled:true,oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false,entropyPolicy:'off',observedCMakeOptions:{CMAKE_BUILD_TYPE:'Release',ENABLE_BUILTIN_NODE_COMPAT:'ON',NODE_COMPAT_ENTROPY_MODE:'OFF'},entropyEntryPatchApplied:true,componentizeJsPatches:[{name:'node-compat-runtime-entry-v1',applied:true,sha256:ENTROPY_ENTRY_PATCH_SHA256}]};
yes(()=>releaseMetadataModel(native,'a'.repeat(64)),'synthetic consistency only');
for(const [key,value]of [['engineSha256','b'.repeat(64)],['oomTesting',true],['profileEnabled',false],['strictInitialization',false]]){
  const m=structuredClone(native);m[key]=value;no(()=>releaseMetadataModel(m,'a'.repeat(64)),'release '+key);
}
for(const mode of ['Debug','RelWithDebInfo',undefined]){const m=structuredClone(native);m.observedCMakeOptions.CMAKE_BUILD_TYPE=mode;no(()=>releaseMetadataModel(m,'a'.repeat(64)),'ambiguous/debug');}
const source='export function run(){return "synthetic";}';const world='package test:fixture; world fixture { export run: func() -> string; }';
const root={nativeEngine:{path:'/synthetic/unopened/engine.wasm',sha256:'a'.repeat(64)},guestSourceSha256:hash(source),witWorldSha256:hash(world),worldName:'fixture',selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event']};
const options=()=>({engine:root.nativeEngine.path,preview2Adapter:refs.prunedAdapter.path,witWorld:world,worldName:'fixture',selectedInterfaces:[],disableFeatures:[...root.disableFeatures],enableFeatures:[],enableAot:false,env:{}});
yes(()=>optionSnapshot(source,options(),root,refs),'exact public call options');
for(const [key,value]of [['engine','/old-engine'],['preview2Adapter','/default-adapter'],['enableAot',true],['env',{HOST_SECRET:'notempty'}],['witWorld','world wrong {}'],['selectedInterfaces',['wasi:io/poll@0.2.10']],['legacyDiagnostic',true],['finalizeComponent',()=>{}]]){
  const o=options();o[key]=value;no(()=>optionSnapshot(source,o,root,refs),'options '+key);
}
const getter=options();Object.defineProperty(getter,'engine',{get(){throw new Error('getter must not run');},enumerable:true});no(()=>optionSnapshot(source,getter,root,refs),'accessor options');
const iterator=options();iterator.selectedInterfaces[Symbol.iterator]=function*(){throw new Error('must not iterate custom iterator');};no(()=>optionSnapshot(source,iterator,root,refs),'custom array iterator');
no(()=>optionSnapshot(source+' ',options(),root,refs),'unapproved source hash');
const allText=await readFile(new URL('./loader.mjs',import.meta.url),'utf8');
const begin=allText.indexOf('function createSelected(context){'),end=allText.indexOf('\n\nexport async function loadExperimentalClockPackage',begin);
assert(begin>=0&&end>begin);
const pureBegin=allText.indexOf('function data(value,label){'),pureEnd=allText.indexOf('\n\nexport function environmentModel',pureBegin);
const rootBegin=allText.indexOf('function rootModel(root,own,refs){'),rootEnd=allText.indexOf('\n\nfunction createSelected',rootBegin);
const rootCheck=vm.runInNewContext(allText.slice(pureBegin,pureEnd)+'\n'+allText.slice(rootBegin,rootEnd)+'\nrootModel;',{assert,PACKAGE:refs.packageRoot,Object,Array,Reflect,Number,hash,equal:(a,b)=>assert.deepEqual(JSON.parse(JSON.stringify(a)),JSON.parse(JSON.stringify(b)))});
const rootTemplate=JSON.parse(await readFile(new URL('./root-authority.template.json',import.meta.url)));
const own={path:'/synthetic/unopened/index.json',sha256:'c'.repeat(64),bytes:1};
no(()=>rootCheck(rootTemplate,own,refs),'unissued actual Root template');
const issued={...rootTemplate,state:'ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V1',phase:'experimental-component-construction',sourceIndex:own,packageModuleInitializationAllowed:true,componentConstructionAllowed:true,engineInitializationDuringConstructionAllowed:true,nativeEngine:{path:'/synthetic/unopened/engine.wasm',sha256:'a'.repeat(64),bytes:1},nativeMetadata:{path:'/synthetic/unopened/engine.wasm.build.json',sha256:'b'.repeat(64),bytes:1},privateTemporaryRoot:'/private/tmp/SYNTHETIC_NOT_CREATED',guestSourceSha256:hash(source),witWorldSha256:hash(world),worldName:'fixture',selectedInterfaces:[],disableFeatures:[...root.disableFeatures]};
yes(()=>rootCheck(issued,own,refs),'synthetic finite Root shape only');
for(const[key,value]of [['packageRoot','/old-clock-package'],['componentConstructionAllowed',false],['engineInitializationDuringConstructionAllowed',false],['nativeArtifactAdmissionMustBePerformedByCaller',false],['freshOwnedNodeProcessRequired',false],['adapterPromotionAllowed',true],['runtimeAcceptanceClaim',true],['ordinaryGuestExportsAllowed',true],['nativeMetadata',{path:'/wrong-sidecar',sha256:'b'.repeat(64),bytes:1}]]){const r=structuredClone(issued);r[key]=value;no(()=>rootCheck(r,own,refs),'Root '+key);}
const factory=vm.runInNewContext(allText.slice(begin,end)+'\ncreateSelected;',{assert,optionSnapshot,releaseMetadataModel,Uint8Array,Object});
function context(overrides={}){
  const events=[];const out=new Uint8Array([1,2,3]);
  const base={root,refs,nativeMetadata:native,provenance:Object.freeze({kind:'SYNTHETIC_MOCK_NO_ARTIFACT'}),toolchain:{fixture:true},
    recheck:async()=>{events.push('recheck');await Promise.resolve();},
    selectedInterfacePolicy:(m,o)=>{events.push('policy');assert.equal(m,native);return selectedInterfacePolicy(m,o);},
    packageComponentize:async(s,o)=>{events.push('package-mock');assert.equal(s,source);assert.equal(o.engine,root.nativeEngine.path);assert.equal(o.preview2Adapter,refs.prunedAdapter.path);assert.equal(o.witWorld,world);assert.equal(Object.hasOwn(o,'selectedInterfaces'),false);assert(Object.isFrozen(o));return{component:out,imports:[],debug:undefined};},
    auditSelectedInterfaces:async(t,c,p)=>{events.push('audit-mock');assert.equal(c,out);assert.equal(p.entropyPolicy,'off');return{fixtureOnly:true};}};
  return{events,out,value:{...base,...overrides}};
}
{
  const c=context(),selected=factory(c.value),o=options();const pending=selected.componentize(source,o);
  o.engine='/mutated-after-await';o.witWorld='mutated';o.disableFeatures.pop();
  const result=await pending;assert.equal(result.component,c.out);assert.equal(result.packagingProvenance,c.value.provenance);assert.equal(result.interfaceAudit.fixtureOnly,true);assert.deepEqual(c.events,['recheck','policy','package-mock','audit-mock','recheck']);checks++;
  await assert.rejects(()=>selected.componentize(source,options()));assert.equal(c.events.at(-1),'recheck');assert.equal(c.events.filter(x=>x==='recheck').length,3);checks++;
}
{
  const c=context(),o=options();o.enableAot=true;
  await assert.rejects(()=>factory(c.value).componentize(source,o));assert.deepEqual(c.events,['recheck']);checks++;
}
for(const phase of ['package','audit','policy','initial-recheck']){
  const c=context();
  if(phase==='package')c.value.packageComponentize=async()=>{c.events.push('package-mock');throw new Error('injected package failure');};
  if(phase==='audit')c.value.auditSelectedInterfaces=async()=>{c.events.push('audit-mock');throw new Error('injected audit failure');};
  if(phase==='policy')c.value.selectedInterfacePolicy=()=>{c.events.push('policy');throw new Error('injected policy failure');};
  if(phase==='initial-recheck'){let n=0;c.value.recheck=async()=>{c.events.push('recheck');if(++n===1)throw new Error('injected source drift');};}
  await assert.rejects(()=>factory(c.value).componentize(source,options()));assert.equal(c.events.at(-1),'recheck');assert.equal(c.events.filter(x=>x==='recheck').length,2);checks++;
}
{
  const badRoot={...root,selectedInterfaces:['wasi:io/not-standard@0.2.10']};const c=context({root:badRoot});const o=options();o.selectedInterfaces=[...badRoot.selectedInterfaces];await assert.rejects(()=>factory(c.value).componentize(source,o));assert.equal(c.events.includes('package-mock'),false);assert.equal(c.events.at(-1),'recheck');checks++;
}
console.log(JSON.stringify({schemaVersion:1,state:'CLOCK_PACKAGE_LOADER_PURE_HOST_MODELS_PASSED',checks,actualEligibilityProofsReadAsData:true,genuineCapabilitySelectionFunctionUsed:true,realFactoryExtractedWithInjectedPackageAuditAndRecheck:true,syntheticMetadataConsistencyOnly:true,actualPackageSplicerImported:false,actualComponentizeOrWizerInvoked:false,engineOrGuestExecuted:false}));
