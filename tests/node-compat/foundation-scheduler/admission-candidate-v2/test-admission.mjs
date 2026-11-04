// Source-only unit tests. Synthetic metadata is NOT an engine/build/runtime proof.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,copyFile,mkdtemp,rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
assert.equal(process.version,'v22.14.0');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const json=async path=>JSON.parse(await readFile(path));
const integration=resolve(here,'../integration-candidate-v1');
const policy=await json(join(integration,'policy.json')),pins=await json(join(here,'pins.json'));
assert.equal(hash(await readFile(join(here,'private-ticks-admission.proposed.mjs'))),
  hash(await readFile(join(here,'source/tests/node-compat/private-ticks-admission.mjs'))),'Test the exact proposed helper');
const selected=await import(pathToFileURL(join(here,'source/tests/node-compat/module-selection.mjs')));
const original=await import(pathToFileURL(join(repo,'tests/node-compat/module-selection.mjs')));
const base=await json('/tmp/starling-node-compat/foundations-v11/native-freeze/off-foundations.engine.wasm.build.json');
const temporary=await mkdtemp(join(tmpdir(),'starling-tick-admission-source-only-'));
const sourceRoot=join(temporary,'source'),results=[];
function test(name,run){try{run();results.push({name,passed:true});}catch(error){results.push({name,passed:false,error:error.message});}}
function layer(map){return Object.fromEntries(Object.entries(map).map(([path,value])=>[path,policy.sourceLayer[path]?.afterSha256??value]));}
const nativePaths=policy.expectedNativeSourceManifest.filter(item=>item.path.endsWith('.cpp')&&/^(builtins|runtime)\//.test(item.path)).map(item=>item.path);
function synthetic(enabled=true,{events=true,gc=false,streamWeb=true,slim=false}={}){
  const value=structuredClone(base);
  // These are deliberate test values, never published as a real engine receipt.
  value.syntheticMetadataOnly=true;value.engineSha256='0'.repeat(64);value.enginePath='NO_ENGINE_EXISTS';
  value.buildRecipeSha256=pins.productionRecipeSha256;value.sourceManifest=structuredClone(policy.expectedNativeSourceManifest);
  value.eventsEnabled=events;value.protectedAbortListenerEnabled=events;value.gcStress=gc;
  value.streamWebEnabled=streamWeb;
  for(const [field,option,path] of [['pathEnabled','NODE_COMPAT_PATH',selected.PATH_MANIFEST],
    ['stringDecoderEnabled','NODE_COMPAT_STRING_DECODER',selected.STRING_DECODER_MANIFEST],
    ['assertEnabled','NODE_COMPAT_ASSERT',selected.ASSERT_MANIFEST],
    ['querystringEnabled','NODE_COMPAT_QUERYSTRING',selected.QUERYSTRING_MANIFEST],
    ['utilEnabled','NODE_COMPAT_UTIL',selected.UTIL_MANIFEST],
    ['streamWebEnabled','NODE_COMPAT_STREAM_WEB',selected.STREAM_WEB_MANIFEST]]){
    if(slim&&field!=='streamWebEnabled')value[field]=false;
    const flag=value[field];
    value.requestedCMakeOptions[option]=value.observedCMakeOptions[option]=flag?'ON':'OFF';
    if(!flag)value.selectedModuleManifests=value.selectedModuleManifests.filter(item=>item.path!==path);
  }
  value.observedCMakeOptions.NODE_COMPAT_EVENTS=events?'ON':'OFF';
  value.requestedCMakeOptions.NODE_COMPAT_EVENTS=events?'ON':'OFF';
  value.observedCMakeOptions.NODE_COMPAT_GC_STRESS=gc?'ON':'OFF';
  value.requestedCMakeOptions.NODE_COMPAT_GC_STRESS=gc?'ON':'OFF';
  value.observedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS=enabled?'ON':'OFF';
  value.requestedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS=enabled?'ON':'OFF';
  if(!events)value.selectedModuleManifests=value.selectedModuleManifests.filter(item=>item.path!==selected.EVENTS_MANIFEST);
  const command=path=>'/synthetic/clang++ -DNODE_COMPAT_STRICT_INITIALIZATION=1 '+
    (events?'-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 ':'')+(enabled?'-DNODE_COMPAT_INTERNAL_TICKS=1 ':'')+
    (streamWeb&&path.startsWith('builtins/node-compat/')?'-DNODE_COMPAT_STREAM_WEB=1 ':'')+
    '-c "/synthetic/source root/'+path+'" -o /synthetic/out.o';
  const active=nativePaths.filter(path=>(enabled||path!=='runtime/node_tick_queue.cpp')&&
    (streamWeb||path!=='builtins/node-compat/stream-web-kernel.cpp'));
  const layout=active.map(command),embedding=[command('embedding/embedding.cpp')];
  const strict=value.strictEventExceptionPolicy,protectedPolicy=value.protectedAbortListenerPolicy;
  strict.parentSourcePolicy=structuredClone(pins.parentStrict);strict.version=policy.strictPolicyVersion;
  strict.nativeSourceSha256=layer(pins.parentStrict.nativeSourceSha256);
  for(const name of ['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h'])strict.nativeSourceSha256[name]=policy.sourceLayer[name].afterSha256;
  strict.actualNativeCompileCommands=Object.keys(strict.nativeSourceSha256).filter(path=>path.endsWith('.cpp')&&(enabled||path!=='runtime/node_tick_queue.cpp')).map(command);
  protectedPolicy.parentSourcePolicy=structuredClone(pins.parentProtected);protectedPolicy.version=policy.protectedPolicyVersion;
  protectedPolicy.sourceSha256=layer(pins.parentProtected.sourceSha256);protectedPolicy.strictPolicyVersion=strict.version;
  protectedPolicy.enabled=events;protectedPolicy.actualLayoutCompileCommands=layout;protectedPolicy.actualEmbeddingCompileCommands=embedding;
  value.actualEmbeddingCompileCommands=embedding;
  value.actualStreamWebKernelCompileCommands=streamWeb?[command('builtins/node-compat/stream-web-kernel.cpp')]:[];
  value.componentizeSourceManifest=pins.parentExternalSourceManifest.map(item=>({...item,sha256:item.path==='embedding/embedding.cpp'?policy.embedding.afterSha256:item.sha256}));
  value.componentizeJsPatches=[...structuredClone(pins.parentPatchChain),{name:policy.version+'-boundary',sha256:policy.embedding.patchSha256,
    baseRevision:pins.componentizeJsRevision,applied:true,files:['embedding/embedding.cpp']}];
  value.internalTicksEnabled=enabled;
  value.internalTickPolicy={version:policy.version,enabled,sourcePolicyInstalled:true,parentRecipeSha256:policy.parentRecipeSha256,
    parentNativeManifestCanonicalSha256:policy.parentNativeManifestCanonicalSha256,sourceLayer:structuredClone(policy.sourceLayer),
    nativePatchSha256:policy.nativePatchSha256,embeddingPatchSha256:policy.embedding.patchSha256,
    embeddingBeforeSha256:policy.embedding.beforeSha256,embeddingAfterSha256:policy.embedding.afterSha256,
    policyFileSha256:pins.policySha256,helperSha256:pins.helperSha256,actualLayoutCompileCommands:layout,
    actualQueueCompileCommands:enabled?[command('runtime/node_tick_queue.cpp')]:[],actualEmbeddingCompileCommands:embedding,
    requestedCMake:enabled?'ON':'OFF',observedCMake:enabled?'ON':'OFF',limits:structuredClone(policy.limits),
    addsExternalCapabilities:false,publicProcessModule:false,resetSafeReuse:'OPEN; cancellation and teardown not established'};
  return value;
}
function accept(value){return selected.selectedManifestsForEngine(value,{sourceRoot});}
try{
  for(const entry of base.sourceManifest){const destination=join(sourceRoot,entry.path);await mkdir(dirname(destination),{recursive:true});
    const bytes=await readFile(join('/tmp/starling-node-compat/foundations-v11/native-freeze/source',entry.path));assert.equal(hash(bytes),entry.sha256);await writeFile(destination,bytes);}
  const patch=resolve(integration,'../taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch');
  assert.equal(hash(await readFile(patch)),policy.nativePatchSha256);
  const applied=spawnSync('patch',['--batch','-p1','-d',sourceRoot,'-i',patch],{encoding:'utf8'});
  assert.equal(applied.status,0,applied.stdout+applied.stderr);
  for(const entry of policy.expectedNativeSourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256);
  for(const enabled of [false,true])for(const events of [false,true])for(const gc of [false,true])for(const streamWeb of [false,true])
    test('synthetic finite branch ticks='+enabled+' events='+events+' gc='+gc+' streamWeb='+streamWeb,()=>{
      const manifests=accept(synthetic(enabled,{events,gc,streamWeb})),map=selected.builtinMap(manifests);
      assert.equal(map['node:process'],undefined);assert.equal(map.process,undefined);
      assert.equal(map['starling:test-internal-ticks'],undefined);assert.equal(map['starling:test-initializer-ticks'],undefined);
      assert.equal(manifests.length,(events?8:7)-(streamWeb?0:1));
    });
  for(const enabled of [false,true])test('synthetic slim core-only StreamWeb OFF ticks='+enabled,()=>{
    const m=synthetic(enabled,{events:false,streamWeb:false,slim:true});
    const manifests=accept(m);assert.equal(manifests.length,1);
    assert.equal(m.internalTickPolicy.actualLayoutCompileCommands.length,enabled?60:59);
    assert.deepEqual(m.actualStreamWebKernelCompileCommands,[]);
    assert.equal(selected.builtinMap(manifests)['node:stream/web'],undefined);
  });
  const mutations=[
    ['old recipe',m=>m.buildRecipeSha256=pins.parentRecipeSha256],['unknown recipe',m=>m.buildRecipeSha256='1'.repeat(64)],
    ['missing tick boolean',m=>delete m.internalTicksEnabled],['string tick boolean',m=>m.internalTicksEnabled='ON'],
    ['false policy selection',m=>m.internalTickPolicy.enabled=false],['missing installed flag',m=>delete m.internalTickPolicy.sourcePolicyInstalled],
    ['missing observed option',m=>delete m.observedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS],['wrong requested option',m=>m.requestedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS='OFF'],
    ['future tick version',m=>m.internalTickPolicy.version+='-future'],['parent strict version',m=>m.strictEventExceptionPolicy.version=pins.parentStrict.version],
    ['future strict version',m=>m.strictEventExceptionPolicy.version+='-future'],['parent protected version',m=>m.protectedAbortListenerPolicy.version=pins.parentProtected.version],
    ['wrong helper',m=>m.internalTickPolicy.helperSha256='0'.repeat(64)],['wrong policy',m=>m.internalTickPolicy.policyFileSha256='0'.repeat(64)],
    ['wrong source layer',m=>m.internalTickPolicy.sourceLayer={}],['missing source',m=>m.sourceManifest.pop()],
    ['duplicate source',m=>m.sourceManifest.push(m.sourceManifest[0])],['unsafe source path',m=>m.sourceManifest[0].path='../escape.cpp'],
    ['altered source digest',m=>m.sourceManifest[0].sha256='0'.repeat(64)],
    ['extra source',m=>m.sourceManifest.push({path:'runtime/unreviewed.cpp',sha256:'1'.repeat(64)})],
    ['parent ancestry erased',m=>delete m.strictEventExceptionPolicy.parentSourcePolicy],
    ['parent ancestry carries fabricated commands',m=>m.strictEventExceptionPolicy.parentSourcePolicy.actualNativeCompileCommands=[]],
    ['old current strict map',m=>m.strictEventExceptionPolicy.nativeSourceSha256=structuredClone(pins.parentStrict.nativeSourceSha256)],
    ['old current CMake map',m=>m.protectedAbortListenerPolicy.sourceSha256=structuredClone(pins.parentProtected.sourceSha256)],
    ['missing embedding source',m=>m.componentizeSourceManifest.shift()],['wrong embedding source',m=>m.componentizeSourceManifest[0].sha256='0'.repeat(64)],
    ['missing boundary patch',m=>m.componentizeJsPatches.pop()],['unapplied boundary',m=>m.componentizeJsPatches.at(-1).applied=false],
    ['extra boundary patch',m=>m.componentizeJsPatches.push(m.componentizeJsPatches[0])],
    ['no queue compiler observation',m=>m.internalTickPolicy.actualQueueCompileCommands=[]],
    ['missing Engine TU',m=>m.internalTickPolicy.actualLayoutCompileCommands=m.internalTickPolicy.actualLayoutCompileCommands.filter(c=>!c.includes('/runtime/engine.cpp'))],
    ['duplicate TU',m=>m.internalTickPolicy.actualLayoutCompileCommands.push(m.internalTickPolicy.actualLayoutCompileCommands[0])],
    ['syntax-only command',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]+=' -fsyntax-only'],
    ['missing compile mode',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]=m.internalTickPolicy.actualLayoutCompileCommands[0].replace(' -c ',' ')],
    ['macro zero is not OFF',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]=m.internalTickPolicy.actualLayoutCompileCommands[0].replace('INTERNAL_TICKS=1','INTERNAL_TICKS=0')],
    ['duplicate macro',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]+=' -DNODE_COMPAT_INTERNAL_TICKS=1'],
    ['separate macro spelling',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]+=' -D NODE_COMPAT_INTERNAL_TICKS=1'],
    ['missing embedding observations',m=>m.internalTickPolicy.actualEmbeddingCompileCommands=[]],
    ['lost protected layout flag',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]=m.internalTickPolicy.actualLayoutCompileCommands[0].replace('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 ','')],
    ['lost strict flag',m=>m.internalTickPolicy.actualLayoutCompileCommands[0]=m.internalTickPolicy.actualLayoutCompileCommands[0].replace('-DNODE_COMPAT_STRICT_INITIALIZATION=1 ','')],
    ['wrong limit',m=>m.internalTickPolicy.limits.pendingCallbacks++],['new capability claim',m=>m.internalTickPolicy.addsExternalCapabilities=true],
    ['public process claim',m=>m.internalTickPolicy.publicProcessModule=true],['closed reset claim',m=>m.internalTickPolicy.resetSafeReuse='CLOSED'],
    ['debug engine',m=>m.observedCMakeOptions.CMAKE_BUILD_TYPE='Debug'],['OOM engine',m=>m.oomTesting=true],
    ['requested Debug',m=>m.requestedCMakeOptions.CMAKE_BUILD_TYPE='Debug'],
    ['Weval variant',m=>m.observedCMakeOptions.WEVAL='ON'],['wasm-opt disabled',m=>m.requestedCMakeOptions.USE_WASM_OPT='OFF'],
    ['unlocked Rust option',m=>m.observedCMakeOptions.NODE_COMPAT_LOCKED_RUST='OFF'],
    ['unlocked Cargo receipt',m=>m.generatedRustProject.cargoBuildLocked=false],
    ['unchecked Cargo manifest',m=>m.generatedRustProject.manifestAndLockCheckedBeforeAndAfterBuild=false],
    ['wrong host API',m=>m.hostApi='wasi-0.2.0'],['missing strict initialization',m=>m.strictInitialization=false],
    ['missing ABI fix',m=>m.abiFixEnabled=false],['missing BigInt fix',m=>m.bigIntFixEnabled=false],
    ['implicit optional boolean',m=>delete m.utilEnabled],['requested Events disagrees',m=>m.requestedCMakeOptions.NODE_COMPAT_EVENTS='OFF'],
    ['requested GC disagrees',m=>m.requestedCMakeOptions.NODE_COMPAT_GC_STRESS='ON'],
    ['entropy mode disagrees',m=>m.observedCMakeOptions.NODE_COMPAT_ENTROPY_MODE='RUNTIME_ONLY'],
    ['missing StreamWeb boolean',m=>delete m.streamWebEnabled],
    ['requested StreamWeb disagrees',m=>m.requestedCMakeOptions.NODE_COMPAT_STREAM_WEB='OFF'],
    ['observed StreamWeb disagrees',m=>m.observedCMakeOptions.NODE_COMPAT_STREAM_WEB='OFF'],
    ['missing StreamWeb compile receipt',m=>delete m.actualStreamWebKernelCompileCommands],
    ['empty selected StreamWeb compile receipt',m=>m.actualStreamWebKernelCompileCommands=[]],
    ['duplicate StreamWeb compile receipt',m=>m.actualStreamWebKernelCompileCommands.push(m.actualStreamWebKernelCompileCommands[0])],
    ['StreamWeb private macro missing on registration',m=>{const a=m.internalTickPolicy.actualLayoutCompileCommands;const i=a.findIndex(c=>c.includes('/builtins/node-compat/register.cpp'));a[i]=a[i].replace('-DNODE_COMPAT_STREAM_WEB=1 ','');}],
    ['StreamWeb private macro zero',m=>{const a=m.internalTickPolicy.actualLayoutCompileCommands;const i=a.findIndex(c=>c.includes('/builtins/node-compat/register.cpp'));a[i]=a[i].replace('NODE_COMPAT_STREAM_WEB=1','NODE_COMPAT_STREAM_WEB=0');}],
    ['StreamWeb private macro must not leak to runtime',m=>{const a=m.internalTickPolicy.actualLayoutCompileCommands;const i=a.findIndex(c=>c.includes('/runtime/engine.cpp'));a[i]+=' -DNODE_COMPAT_STREAM_WEB=1';}],
    ['StreamWeb private macro must not leak to embedding',m=>m.internalTickPolicy.actualEmbeddingCompileCommands[0]+=' -DNODE_COMPAT_STREAM_WEB=1'],
    ['diagnostic true',m=>m.diagnosticOnly=true],['diagnostic string',m=>m.diagnosticOnly='true'],
    ['diagnostic policy hidden behind false',m=>{m.diagnosticOnly=false;m.internalTickDiagnosticPolicy={};}],
    ['public process manifest',m=>m.selectedModuleManifests.push({path:'builtins/node-compat/export-manifest.process.json',sha256:'0'.repeat(64)})]
  ];
  for(const[name,mutate]of mutations)test('synthetic rejection: '+name,()=>{const value=synthetic();mutate(value);assert.throws(()=>accept(value));});
  for(const enabled of [false,true]){
    test('selected StreamWeb missing kernel TU ticks='+enabled,()=>{
      const m=synthetic(enabled),layout=m.internalTickPolicy.actualLayoutCompileCommands.filter(c=>!c.includes('/stream-web-kernel.cpp'));
      m.internalTickPolicy.actualLayoutCompileCommands=m.protectedAbortListenerPolicy.actualLayoutCompileCommands=layout;
      m.actualStreamWebKernelCompileCommands=[];assert.throws(()=>accept(m));
    });
    test('unselected StreamWeb extra kernel TU ticks='+enabled,()=>{
      const m=synthetic(enabled,{streamWeb:false});
      const command=synthetic(enabled).actualStreamWebKernelCompileCommands[0].replace('-DNODE_COMPAT_STREAM_WEB=1 ','');
      m.internalTickPolicy.actualLayoutCompileCommands.push(command);m.actualStreamWebKernelCompileCommands=[command];
      assert.throws(()=>accept(m));
    });
    test('unselected StreamWeb extra kernel receipt ticks='+enabled,()=>{
      const m=synthetic(enabled,{streamWeb:false});m.actualStreamWebKernelCompileCommands=synthetic(enabled).actualStreamWebKernelCompileCommands;
      assert.throws(()=>accept(m));
    });
    test('unselected StreamWeb private macro rejected ticks='+enabled,()=>{
      const m=synthetic(enabled,{streamWeb:false}),a=m.internalTickPolicy.actualLayoutCompileCommands;
      const i=a.findIndex(c=>c.includes('/builtins/node-compat/register.cpp'));a[i]+=' -DNODE_COMPAT_STREAM_WEB=1';
      assert.throws(()=>accept(m));
    });
  }
  test('OFF cannot carry queue compile',()=>{const m=synthetic(false);m.internalTickPolicy.actualQueueCompileCommands=synthetic().internalTickPolicy.actualQueueCompileCommands;assert.throws(()=>accept(m));});
  test('stripped hints cannot relabel known new source as old',()=>{const m=synthetic(false,{events:false});delete m.internalTicksEnabled;delete m.internalTickPolicy;delete m.observedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS;m.buildRecipeSha256=pins.parentRecipeSha256;m.strictEventExceptionPolicy.version=pins.parentStrict.version;m.protectedAbortListenerPolicy.version=pins.parentProtected.version;m.sourceManifest=m.sourceManifest.filter(i=>!i.path.startsWith('runtime/node_tick_queue.'));assert.throws(()=>accept(m));});
  const source=join(sourceRoot,'runtime/node_tick_queue.cpp'),before=await readFile(source);await writeFile(source,Buffer.concat([before,Buffer.from('\n')]));
  test('actual source-byte tampering rejects',()=>assert.throws(()=>accept(synthetic())));await writeFile(source,before);
  for(const[version,label]of [[10,'off-foundations'],[10,'runtime-foundations'],[10,'gc-foundations'],[10,'events-off-control'],[11,'off-foundations'],[11,'runtime-foundations'],[11,'gc-foundations']]){
    const freeze='/tmp/starling-node-compat/foundations-v'+version+'/native-freeze',metadata=await json(join(freeze,label+'.engine.wasm.build.json'));
    test('actual old receipt unchanged v'+version+' '+label,()=>{
      assert.equal(Object.hasOwn(metadata,'internalTicksEnabled'),false);
      const a=original.selectedManifestsForEngine(metadata,{sourceRoot:join(freeze,'source')}),b=selected.selectedManifestsForEngine(metadata,{sourceRoot:join(freeze,'source')});
      assert.deepEqual(b,a);assert.deepEqual(selected.builtinMap(b),original.builtinMap(a));
    });
  }
}finally{await rm(temporary,{recursive:true,force:true});}
const failed=results.filter(item=>!item.passed);
const report={state:failed.length?'SOURCE_ONLY_ADMISSION_TESTS_FAILED':'SOURCE_ONLY_ADMISSION_TESTS_PASSED',node:process.version,
 tests:results.length,passed:results.length-failed.length,failed,results,syntheticMetadataOnly:true,
 actualOldReceiptSelectionsCompared:7,engineBuilt:false,guestExecuted:false,receiverNegativesExecuted:false,
 resetSafeReuse:'OPEN',publicProcessOrPrivateIdsAdmitted:false,scope:'Source and metadata policy validation only; no compiler, componentizer, host or VM execution.'};
const reportOutput=process.env.NODE_COMPAT_ADMISSION_TEST_OUTPUT
  ?resolve(process.env.NODE_COMPAT_ADMISSION_TEST_OUTPUT):join(here,'test-results.json');
await writeFile(reportOutput,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,tests:report.tests,passed:report.passed,failed,reportOutput},null,2));
if(failed.length)process.exitCode=1;
