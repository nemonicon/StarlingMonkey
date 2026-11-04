// Actual installed m0.8 allocator/helper gate. Historical isolated prototypes
// are source/oracle controls only and are never bundled or injected here.
import assert from 'node:assert/strict';
import {verifyProductionV10} from '../../foundation-add-abort/production-v10-preflight.mjs';
import {Buffer as NodeBuffer} from 'node:buffer';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../../foundations/native-scalar-harness.mjs';
import {selectCoreExpectations,coreExpectationsForGuest} from '../../core-expectations.mjs';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {allocationChecks} from '../checks.mjs';
import {bufferListDemandModule} from '../demand-source.mjs';

assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const here=dirname(fileURLToPath(import.meta.url)),parent=dirname(here);
const newEnginePreflight=await verifyProductionV10();
const h=await nativeHarness({kind:'installed-allocator',here,enabledField:'profileEnabled',option:'ENABLE_BUILTIN_NODE_COMPAT',outputVariable:'NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT'});
assert.equal(h.evidence.engineSha256,newEnginePreflight.engineSha256);
assert.equal(h.metadata.sourceManifest.length,newEnginePreflight.sourceFilesVerified);assert.equal(h.metadata.strictInitialization,true);
assert.equal(h.metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(h.metadata.observedCMakeOptions.WEVAL,'OFF');
for(const key of ['oomTesting','wptSupportEnabled'])assert.equal(h.metadata[key],false);
const policy=selectCoreExpectations(h.metadata,{sourceRoot:h.evidence.sourceRoot});
assert.equal(policy.coreVersion,'sm-node-22.14.0-m0.8');assert.equal(policy.allocUnsafePolicy,'zeroed-no-pool-v1');
const tc=await loadToolchain(),oracleBytes=await readFile(join(parent,'node-results.json')),
  oracle=JSON.parse(oracleBytes),checksSource=await readFile(join(parent,'checks.mjs'),'utf8');
assert.equal(hash(checksSource),oracle.sources['checks.mjs']);
assert.equal(hash(checksSource),'01eb4e9a1b7d7731a1eabbadf4902fee6fe0c3a149b79cbc617b6a81e60e561f');
const allocationSource=checksSource.split('\nexport function candidateChecks')[0];
assert.equal(allocationSource.includes('export function allocationChecks'),true);
assert.equal(allocationSource.includes('temporarilyPatch'),false);
// Ordinary Node allocation oracle is outside all inherited-error poison windows.
// It reads only bytes it has initialized; real Node child_process is never called.
assert.deepEqual(allocationChecks(NodeBuffer,NodeBuffer.allocUnsafe),oracle.cases);
const core=h.builtinManifests.find(item=>item.profileVersion===policy.coreVersion);assert(core);
const contract={...coreExpectationsForGuest(policy),bufferExports:core.modules['node:buffer'].exports,
  importOnlyExports:core.modules['node:buffer'].importOnlyExports,
  childExports:core.modules['node:child_process'].exports.filter(name=>name!=='default')};
const demandSource=await readFile(oracle.demandSource.path,'utf8');assert.equal(hash(demandSource),oracle.demandSource.sha256);
const demand=bufferListDemandModule(demandSource);assert.equal(hash(demand.text),oracle.demandSource.injectedModuleSha256);
const virtualModules={
  'node-compat:installed-allocation-checks':allocationSource,
  'node-compat:installed-core-contract':'export default '+JSON.stringify(contract)+';',
  'node-compat:installed-buffer-list-demand':demand.text,
};
const bundle=await bundleProfile({...tc,builtinManifests:h.builtinManifests,input:join(here,'component.mjs'),virtualModules});
assert.deepEqual([...bundle.imports].sort(),['node:buffer','node:child_process']);
assert(bundle.moduleIds.every(id=>!id.includes('/builtins/node-compat/')&&!/node_modules\/(?:buffer|unenv)/.test(id)));
assert(!/createBufferModule|createAllocUnsafeCandidate|reference-kernel|temporarilyPatch|__require|buffer-facade\.mjs/.test(bundle.code));
const inputs=['checks.mjs','component.mjs','static-require.cjs','run-component-v10.mjs'];
const sourceFiles=[];await mkdir(join(h.output,'source'),{recursive:true});
for(const name of inputs){const bytes=await readFile(join(here,name));sourceFiles.push({name,sha256:hash(bytes)});await writeFile(join(h.output,'source',name),bytes);}
await writeFile(join(h.output,'application.bundle.mjs'),bundle.code);
const preflight={schema:1,atUtc:new Date().toISOString(),state:'installed-allocator-preflight-passed',
  ...h.evidence,coreExpectations:policy,semanticGuestContract:contract,node:process.version,
  nodeExecutableSha256:hash(await readFile(process.execPath)),oracleSha256:hash(oracleBytes),
  originalChecksSha256:hash(checksSource),allocationSubsetSha256:hash(allocationSource),
  callerDemand:oracle.demandSource,bundle:{sha256:hash(bundle.code),imports:bundle.imports,moduleIds:bundle.moduleIds},sourceFiles,
  scope:'Actual installed native module imports; no allocator replacement, facade/kernel injection or inherited poison on native Node codec/error oracles.'};
await writeFile(join(h.output,'preflight.json'),JSON.stringify(preflight,null,2)+'\n');
if(process.argv.includes('--preflight')){console.log(JSON.stringify({state:preflight.state,output:h.output,engineSha256:h.evidence.engineSha256,coreVersion:policy.coreVersion,sources:newEnginePreflight.sourceFilesVerified,differentialGroups:10,imports:bundle.imports}));process.exit(0);}

const progress={stage:'building-real-installed-component',preflight};
async function checkpoint(){await writeFile(join(h.output,'progress.json'),JSON.stringify(progress,null,2)+'\n');}
await checkpoint();
try{
  const fixture=await h.build('installed_allocator',bundle.code);progress.fixture=fixture;progress.stage='runtime';await checkpoint();
  function validate(observed,count){
    assert.equal(observed.failure,undefined,JSON.stringify(observed.failure));assert.equal(observed.calls,count);
    assert.equal(observed.coreVersion,policy.coreVersion);assert.equal(observed.actualNativeModule,true);
    assert.equal(observed.allocatorReplaced,false);for(const key of ['namespaceAliases','staticCommonJS','globalIdentity'])assert.equal(observed[key],true);
    assert.deepEqual(observed.cases,oracle.cases);assert.equal(observed.profile.length,5);
    assert.deepEqual(observed.refusals,{operations:240,prototypeFunctions:91,counts:{globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0},ownFields:['code','module','operation','profile'],restored:true,pureJsOnly:true});
    assert.deepEqual(observed.demand,oracle.callerDemand);
    assert.deepEqual(observed.snapshot,{first:17+count,shared:true,viewValue:count,byteOffset:1,backingBytes:3});
    return observed;
  }
  const instance=await h.importFixture(fixture),calls=[];progress.calls=calls;
  for(let count=1;count<=2;count++){const observed=JSON.parse(await instance.run());calls.push(observed);await checkpoint();validate(observed,count);}
  const wasmtime=h.runHost(fixture);progress.wasmtime=wasmtime;await checkpoint();validate(wasmtime.observed,1);
  progress.stage='initialization-errors';const initialization=[];progress.initialization=initialization;await checkpoint();
  const unsupported=operation=>new RegExp('node:buffer\\.'+operation.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+' is unavailable in sm-node-22\\.14\\.0-m0\\.8');
  for(const[name,source,pattern]of[
    ['type-call',"Buffer.allocUnsafe('2')",/ERR_INVALID_ARG_TYPE/],
    ['type-new',"new Buffer.allocUnsafe('2')",/ERR_INVALID_ARG_TYPE/],
    ['negative-call','Buffer.allocUnsafe(-0.5)',/ERR_OUT_OF_RANGE/],
    ['raw-fraction-cap','Buffer.allocUnsafe(16777216.25)',/ERR_OUT_OF_RANGE/],
    ['unawaited-rejection','Promise.resolve().then(()=>Buffer.allocUnsafe(-1))',/ERR_OUT_OF_RANGE/],
    ['slow-call','Buffer.allocUnsafeSlow(1)',unsupported('Buffer.allocUnsafeSlow')],
    ['slow-new','new Buffer.allocUnsafeSlow(1)',unsupported('Buffer.allocUnsafeSlow')],
    ['prototype-call','Buffer.alloc(1).fill()',unsupported('Buffer.prototype.fill')],
    ['prototype-new','new Buffer.prototype.fill()',unsupported('Buffer.prototype.fill')],
  ]){initialization.push(await h.expectInitialization(name,`import {Buffer} from 'node:buffer';${source};export function run(){return '';}`,pattern));await checkpoint();}
  for(const[name,expression]of[['child-call','spawn()'],['child-new','new spawn()']]){
    initialization.push(await h.expectInitialization(name,`import {spawn} from 'node:child_process';${expression};export function run(){return '';}`,
      /node:child_process\.spawn is unavailable in sm-node-22\.14\.0-m0\.8/));await checkpoint();}
  // Actual immutable pre-advance engine provides the m0.1 control, without
  // modifying the current allocator or loading the old JS factory source.
  progress.stage='actual-old-core-controls';await checkpoint();
  const oldEngine=resolve(process.env.NODE_COMPAT_ALLOCATOR_OLD_ENGINE??'/tmp/starling-node-compat/foundations-v7/native-freeze/off-foundations.engine.wasm');
  const oldRoot=resolve(process.env.NODE_COMPAT_ALLOCATOR_OLD_SOURCE_ROOT??'/tmp/starling-node-compat/foundations-v7/native-freeze/source');
  const oldReceiptBytes=await readFile(oldEngine+'.build.json'),oldMetadata=JSON.parse(oldReceiptBytes);
  assert.equal(hash(await readFile(oldEngine)),'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09');
  assert.equal(oldMetadata.engineSha256,'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09');
  assert.equal(oldMetadata.sourceManifest.length,293);
  for(const item of oldMetadata.sourceManifest)assert.equal(hash(await readFile(join(oldRoot,item.path))),item.sha256,item.path);
  const oldPolicy=selectCoreExpectations(oldMetadata,{sourceRoot:oldRoot});assert.equal(oldPolicy.coreVersion,'sm-node-22.14.0-m0.1');
  const selected=await loadComponentizer(tc),oldOptions={engine:oldEngine,preview2Adapter:h.evidence.adapter.path,
    witWorld:'package test:allocator-old-core; world test { export run: func() -> string; }',worldName:'test',
    disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]},oldInitialization=[];
  for(const[name,operation]of[['old-core-call','Buffer.allocUnsafe(1)'],['old-core-new','new Buffer.allocUnsafe(1)']]){
    const source=`import {Buffer} from 'node:buffer';${operation};export function run(){return '';}`;let failure;
    await writeFile(join(h.output,name+'.init.mjs'),source);
    try{await selected.componentize(source,oldOptions);}catch(error){failure=error;}
    assert(failure);assert.match(failure.message,/node:buffer\.Buffer\.allocUnsafe is unavailable in sm-node-22\.14\.0-m0\.1/);
    oldInitialization.push({name,source,sourceSha256:hash(source),error:failure.message});
  }
  const oldControl={engine:oldEngine,sourceRoot:oldRoot,engineSha256:oldMetadata.engineSha256,receiptSha256:hash(oldReceiptBytes),receipt:oldMetadata,sourceFilesVerified:293,coreExpectations:oldPolicy,initialization:oldInitialization};
  for(const item of h.metadata.sourceManifest)assert.equal(hash(await readFile(join(h.evidence.sourceRoot,item.path))),item.sha256,item.path);
  for(const item of sourceFiles)assert.equal(hash(await readFile(join(here,item.name))),item.sha256,item.name);
  assert.equal(hash(await readFile(process.env.NODE_COMPAT_ENGINE)),h.evidence.engineSha256);
  const report={...preflight,atUtc:new Date().toISOString(),state:'actual-installed-allocator-helper-passed',installedBuiltin:true,
    fixture,calls,wasmtime,initialization,oldControl,differentialGroups:10,profileGroups:5,refusalChecksPerCall:240,
    sourceFilesVerifiedBeforeAndAfter:newEnginePreflight.sourceFilesVerified,emittedImports:[],
    limitations:['Fresh zeroed exact backing at offset0; no slab or uninitialized contents',
      'Raw requested size <=16MiB before truncation; detailed error messages differ',
      'allocUnsafeSlow and all91 own prototype functions remain refused',
      'Only exact four readable-stream BufferList excerpts; no classic stream or scheduler support',
      'Pure JS inherited-field poison checks; no native codec/error oracle under poison, genuine OOM or private fault tests',
      'No component size or performance benefit inferred from correctness artifacts']};
  await writeFile(join(h.output,'results.json'),JSON.stringify(report,null,2)+'\n');
  await writeFile(join(here,'native-component-v10-results.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({state:report.state,output:h.output,componentSha256:fixture.componentSha256,coreVersion:policy.coreVersion,
    differentialGroups:10,profileGroups:5,refusalsPerCall:240,JcoCalls:2,freshWasmtimeCalls:1,initializationFailures:initialization.length,
    oldCoreFailures:oldInitialization.length,emittedImports:[]}));
}catch(error){await writeFile(join(h.output,'mismatch.json'),JSON.stringify({atUtc:new Date().toISOString(),stage:progress.stage,error:{name:error.name,message:error.message,stack:error.stack},progress},null,2)+'\n');throw error;}
