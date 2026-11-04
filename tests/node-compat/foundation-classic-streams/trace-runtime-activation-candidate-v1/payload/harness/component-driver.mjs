// UNEXECUTED FUTURE COMPONENT TEMPLATE. Imported only after classicPreflight.
// The checked-in candidate has no admitted engine artifact for any variant.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFile, mkdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from 'file:///tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/toolchain.mjs';
import { bundleProfile } from 'file:///tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/profile-bundler.mjs';
import { selectedManifestsForEngine } from 'file:///tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/module-selection.mjs';
import { selectedInterfacePolicy, SECURE_RANDOM_INTERFACE } from 'file:///tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/capability-policy.mjs';
import { unsupportedInitializers, caughtInitializer } from './deferred-snippets.mjs';
import { deployedFatal, deployedCleanControls } from './deployed-fixtures.mjs';
import { trackedWriter, publishCompletion } from './completion.mjs';

const WASMTIME_SHA256='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c';
const PREVIEW1_ADAPTER_SHA256='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0';
const CHECKS_SHA256='4b90e2597a18eeb8abd08867bcfe32e6a4043fa909a8206e9e0d7ca90d81ac5b';
const SEALED_NODE_EXPECTED_SHA256='88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce';
const EXPECTED_WIT='package root:component; world root { export run: func() -> string; }';
const hash=value=>createHash('sha256').update(value).digest('hex');
const HERE=dirname(fileURLToPath(import.meta.url));
const REPOSITORY='/tmp/starling-node-compat/classic-trace-source-v1';
const expectedImports=['node:buffer','node:events','node:stream','node:stream/promises','node:util'].sort();

export async function runClassicGate(admission) {
  assert.equal(process.version,'v22.14.0');
  assert(admission && typeof admission.recheck==='function');
  const {enginePath,sourceRoot,metadata,pin,variant}=admission;
  assert(pin && typeof enginePath==='string' && typeof sourceRoot==='string');
  assert(['normal-off','normal-runtime','gc-off','disabled-off'].includes(variant));
  assert.equal(metadata.debuggerEnabled,false);
  assert.equal(metadata.oomTesting,false);
  assert.equal(metadata.gcStress,variant==='gc-off');
  assert.equal(metadata.entropyPolicy,variant==='normal-runtime'?'runtime-only':'off');
  await admission.recheck();
  const output=resolve(process.env.NODE_COMPAT_CLASSIC_OUTPUT??join('/tmp/starling-node-compat/classic-trace-runtime-v1',variant));
  await mkdir(output,{recursive:true});
  const tracked=trackedWriter(output);
  const writeOutput=tracked.write;
  await writeOutput(join(output,'package.json'),'{"type":"module"}\n',{flag:'wx'});
  const toolchain=await loadToolchain();
  const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot});
  const manifestModuleIds=builtinManifests.flatMap(manifest=>Object.keys(manifest.modules));

  async function bundle(input,expected) {
    await admission.recheck();
    const lowered=await bundleProfile({...toolchain,builtinManifests,input});
    if(expected!==null) assert.deepEqual([...lowered.imports].sort(),[...expected].sort());
    assert(lowered.moduleIds.every(id=>!/(?:\/classic-core(?:\.generated)?\.mjs$|\/classic-streams\.mjs$|\/implementation-candidate-v1\/|\/builtins\/node-compat\/)/.test(id)),
      'Only real registered builtin imports; never bundle a semantic factory');
    assert(!lowered.code.includes('builtinFactory'),'No embedded builtin factory');
    await admission.recheck();
    return lowered;
  }

  let completedReport;
  try {
   execution: {
    if(variant==='disabled-off') {
      assert(!manifestModuleIds.includes('node:stream') && !manifestModuleIds.includes('node:stream/promises'));
      const failures=[];
      for(const id of ['node:stream','stream','node:stream/promises','stream/promises']) for(const commonJS of [false,true]) {
        const input=join(output,'disabled-'+failures.length+(commonJS?'.cjs':'.mjs'));
        const source=commonJS?'module.exports=require('+JSON.stringify(id)+');\n':
          'import * as value from '+JSON.stringify(id)+'; export {value};\n';
        await writeOutput(input,source,{flag:'wx'});
        let error;
        try { await bundleProfile({...toolchain,builtinManifests,input}); } catch(caught) { error=caught; }
        assert(error,'Unselected module must fail before packaging: '+id);
        assert.match(error.message,/not admitted/);
        failures.push({id,commonJS,sourceSha256:hash(source),error:error.message});
      }
      await admission.recheck();
      completedReport={schemaVersion:1,variant,
        status:'FUTURE_CLASSIC_DISABLED_ADMISSION_GATE_PASSED',engineSha256:metadata.engineSha256,
        pin,failures,componentizerInvoked:false,componentBuilt:false,hostExecuted:false};
      break execution;
    }

    assert(manifestModuleIds.includes('node:stream') && manifestModuleIds.includes('node:stream/promises'));
    assert.equal(hash(await readFile(join(HERE,'checks.mjs'))),CHECKS_SHA256);
    const sealedBytes=await readFile(join(HERE,'../../implementation-candidate-v1/node-final-acceptance-results.json'));
    assert.equal(hash(sealedBytes),SEALED_NODE_EXPECTED_SHA256);
    const expected=JSON.parse(sealedBytes).expected;
    assert.equal(expected.length,19);
    const oracleBytes=await readFile(join(HERE,'node-oracle-results.json'));
    const oracle=JSON.parse(oracleBytes);
    assert.equal(oracle.status,'NODE22_ONLY_EXACT_SINGLE_WAIT_TRANSFORM_PASSED');
    assert.equal(oracle.groupCount,19);
    assert.deepEqual(oracle.transformedObserved,expected);
    const adapter=join(REPOSITORY,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
    assert.equal(hash(await readFile(adapter)),PREVIEW1_ADAPTER_SHA256);
    // This import and selection happen only after the outer run.mjs preflight.
    const {loadComponentizer}=await import('file:///tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/componentizer.mjs');
    // Reuse the existing native scalar harness's Wasmtime string decoder. Its
    // module also imports componentizer helpers, so keep it out of OFF admission.
    const {decodeCliString}=await import('file:///tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/foundations/native-scalar-harness.mjs');
    const selected=await loadComponentizer(toolchain);
    const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
    try { await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules')); }
    catch(error) { if(error.code!=='EEXIST') throw error; }
    const disableFeatures=['stdio','clocks','http','fetch-event',...(variant==='normal-runtime'?[]:['random'])];
    const selectedInterfaces=variant==='normal-runtime'?[SECURE_RANDOM_INTERFACE]:[];
    const options={engine:enginePath,preview2Adapter:adapter,
      witWorld:'package test:native-classic; world test { export run: func() -> string; }',worldName:'test',
      disableFeatures,selectedInterfaces};
    const capabilityPolicy=selectedInterfacePolicy(metadata,options);
    assert.deepEqual(capabilityPolicy.selectedInterfaces,selectedInterfaces);
    const lowered=await bundle(join(HERE,'guest.mjs'),expectedImports);
    await writeOutput(join(output,'classic.bundle.mjs'),lowered.code,{flag:'wx'});
    await admission.recheck();
    const {component,interfaceAudit}=await selected.componentize(lowered.code,options);
    await admission.recheck();
    assert.deepEqual(interfaceAudit.emittedImports,selectedInterfaces,'Only the explicitly selected entropy capability may remain');
    const emittedWit=await componentWit(component);
    if(variant!=='normal-runtime') assert.equal(emittedWit.replace(/\s+/g,' ').trim(),EXPECTED_WIT);
    else {
      const rootWorld=emittedWit.match(/world root \{([\s\S]*?)\n\}/);
      assert(rootWorld,'Root world must be inspectable');
      assert.deepEqual([...rootWorld[1].matchAll(/^\s*export\s+([^;]+);/gm)].map(match=>match[1]),['run: func() -> string']);
    }
    const componentPath=join(output,'classic.component.wasm');
    await writeOutput(componentPath,component,{flag:'wx'});
    const {files}=await transpile(component,{name:'classic',wasiShim:true});
    for(const [name,bytes] of Object.entries(files)) {
      await mkdir(dirname(join(output,name)),{recursive:true});
      await tracked.writeGenerated(join(output,name),bytes,{flag:'wx'});
    }
    const modulePath=join(output,'classic.js');
    const instance=await import(pathToFileURL(modulePath));
    function validate(observed,call) {
      assert.equal(observed.call,call);
      assert.equal(observed.retainedDefaultBefore,call===1?65536:777);
      assert.deepEqual(observed.snapshotDefaults,[65536,16]);
      assert.equal(observed.snapshotIdentity,call===1?true:null);
      assert.deepEqual(observed.ordinary,expected);
      assert.equal(observed.deferred.length,48);
      assert.equal(observed.overloads.length,17);
      assert.deepEqual(observed.limits.map(value=>[value.name,value.boundary,value.code]),[
        ['writable object units',4096,'ERR_SM_NODE_STREAM_LIMIT'],
        ['readable byte chunks',4096,'ERR_SM_NODE_STREAM_LIMIT'],
        ['readable byte units',16777216,'ERR_SM_NODE_STREAM_LIMIT']]);
      assert.equal(observed.nativeHex,'00cafeff');
      assert.deepEqual(observed.rooting,{hexRounds:8,streamIdentity:true,callbackCalls:1,abortCalls:1,disposedCalls:0});
      assert.equal(observed.graph.aliases,true);
      assert.equal(observed.graph.staticCommonJS,true);
      assert.equal(observed.graph.globalBufferIdentity,true);
      return observed;
    }
    const retained=[];
    for(let call=1;call<=3;call++) retained.push(validate(JSON.parse(await instance.run()),call));
    // A distinct top-level generated module instantiates a new core instance.
    // This tests fresh state separately from the retained module's three calls.
    const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1');
    const freshObserved=validate(JSON.parse(await fresh.run()),1);
    await admission.recheck();
    const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
    assert.equal(hash(await readFile(host)),WASMTIME_SHA256);
    const version=spawnSync(host,['--version'],{encoding:'utf8',timeout:55000});
    assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
    const result=spawnSync(host,['run','--invoke','run()',componentPath],{
      encoding:'utf8',timeout:55000,maxBuffer:4*1024*1024});
    assert.equal(result.status,0,result.error?.message??result.stderr);
    const wasmtimeObserved=validate(JSON.parse(decodeCliString(result.stdout.trim())),1);
    await admission.recheck();

    async function buildDeployed(test) {
      const input=join(output,test.name+'.source.mjs');
      await writeOutput(input,test.source,{flag:'wx'});
      const bundled=await bundle(input,['node:stream']);
      await admission.recheck();
      const built=await selected.componentize(bundled.code,options);
      await admission.recheck();
      assert.deepEqual(built.interfaceAudit.emittedImports,selectedInterfaces);
      const wit=await componentWit(built.component);
      assert.match(wit,/export run: func\(\) -> string;/);
      const componentPath=join(output,test.name+'.component.wasm');
      await writeOutput(componentPath,built.component,{flag:'wx'});
      const generated=await transpile(built.component,{name:test.name,wasiShim:true});
      for(const [name,bytes] of Object.entries(generated.files)) {
        await mkdir(dirname(join(output,name)),{recursive:true});
        await tracked.writeGenerated(join(output,name),bytes,{flag:'wx'});
      }
      await admission.recheck();
      return{componentPath,modulePath:join(output,test.name+'.js'),sourceSha256:hash(test.source),
        bundleSha256:hash(bundled.code),imports:bundled.imports,moduleIds:bundled.moduleIds,
        componentSha256:hash(built.component),componentBytes:built.component.length,
        interfaceAudit:built.interfaceAudit,emittedWit:wit};
    }

    // Deployed failures are separate from initializer failures. Use an isolated
    // Jco child and a fresh Wasmtime process; neither failed instance is reused.
    const fatalFixture=await buildDeployed(deployedFatal);
    const fatalChild=join(output,'deployed-fatal-child.mjs');
    await writeOutput(fatalChild,
      'import {run} from '+JSON.stringify(pathToFileURL(fatalFixture.modulePath).href)+';\n'+
      "try{await run();console.log('UNEXPECTED_FATAL_RETURN');process.exitCode=2;}catch(error){console.log('EXPECTED_FATAL_DISCARD');}\n",{flag:'wx'});
    await admission.recheck();
    const fatalJco=spawnSync(process.execPath,[fatalChild],{encoding:'utf8',timeout:55000,maxBuffer:2*1024*1024});
    assert.equal(fatalJco.status,0,fatalJco.error?.message??fatalJco.stderr);
    assert.match(fatalJco.stdout,/EXPECTED_FATAL_DISCARD/);
    assert.doesNotMatch(fatalJco.stdout,/UNEXPECTED_FATAL_RETURN/);
    await admission.recheck();
    assert.equal(hash(await readFile(host)),WASMTIME_SHA256);
    const fatalHost=spawnSync(host,['run','--invoke','run()',fatalFixture.componentPath],{
      encoding:'utf8',timeout:55000,maxBuffer:2*1024*1024});
    assert.equal(fatalHost.error,undefined,'Spawn errors/timeouts are not guest failure evidence');
    assert.equal(fatalHost.signal,null,'Signal termination is not guest failure evidence');
    assert(Number.isInteger(fatalHost.status)&&fatalHost.status>0,'Fresh deployed export must fail');
    assert.doesNotMatch(fatalHost.stdout,/UNEXPECTED_FATAL_RETURN/);
    await admission.recheck();
    const deployedFailures={fixture:fatalFixture,policy:deployedFatal.policy,
      jco:{status:fatalJco.status,stdout:fatalJco.stdout,stderr:fatalJco.stderr},
      wasmtime:{status:fatalHost.status,stdout:fatalHost.stdout,stderr:fatalHost.stderr},
      errorOriginScope:'Failure is required here; own error code/origin is checked by the paired clean guest controls, not inferred from generic host trap text'};

    const deployedControls=[];
    for(const test of deployedCleanControls) {
      const fixture=await buildDeployed(test);
      const cleanInstance=await import(pathToFileURL(fixture.modulePath));
      const checkClean=(value,calls)=>{
        assert.equal(value.kind,test.kind);assert.equal(value.calls,calls);assert.equal(value.completed,true);
        assert.deepEqual(value.error,{code:'ERR_SM_NODE_UNSUPPORTED',module:'node:stream',operation:'compose',profile:'sm-node-22.14.0-m0.12'});
        if(test.kind==='handled-later')assert.equal(value.handledAfterReaction,true);
        return value;
      };
      const calls=[];
      await admission.recheck();
      for(let call=1;call<=3;call++)calls.push(checkClean(JSON.parse(await cleanInstance.run()),call));
      await admission.recheck();
      assert.equal(hash(await readFile(host)),WASMTIME_SHA256);
      const cleanHost=spawnSync(host,['run','--invoke','run()',fixture.componentPath],{
        encoding:'utf8',timeout:55000,maxBuffer:2*1024*1024});
      assert.equal(cleanHost.status,0,cleanHost.error?.message??cleanHost.stderr);
      const observed=checkClean(JSON.parse(decodeCliString(cleanHost.stdout.trim())),1);
      await admission.recheck();
      deployedControls.push({kind:test.kind,fixture,retainedJcoCalls:calls,
        freshWasmtime:{status:cleanHost.status,observed,stdoutSha256:hash(cleanHost.stdout),stderr:cleanHost.stderr},
        scope:'Only successful caught/handled exports are reused; never the failed instance'});
    }

    assert.equal(unsupportedInitializers.length,65);
    const initializationFailures=[];
    for(const [index,test] of unsupportedInitializers.entries()) {
      const input=join(output,'initializer-'+index+'.mjs');
      await writeOutput(input,test.source,{flag:'wx'});
      const bundled=await bundle(input,null);
      // Unused imports may be removed by the bundler. The actual imports below
      // are recorded; only registered classic modules may remain.
      assert(bundled.imports.every(id=>id==='node:stream'||id==='node:stream/promises'));
      let error;
      await admission.recheck();
      try { await selected.componentize(bundled.code,options); } catch(caught) { error=caught; }
      await admission.recheck();
      assert(error,'Application-top-level unsupported operation must fail: '+test.name);
      // Wizer reports the thrown Error's message/stack, not its own `code`.
      // Own coded properties are checked inside guest catches in guest.mjs and
      // the caught initialization control. Match the actual factory message.
      assert.equal(typeof test.expectedFactoryMessage,'string');
      assert(error.message.includes(test.expectedFactoryMessage),
        'Missing actual factory operation/message: '+test.name+'\n'+error.message);
      initializationFailures.push({name:test.name,operation:test.operation,construct:test.construct??false,
        expectedFactoryOperation:test.expectedFactoryOperation,expectedFactoryMessage:test.expectedFactoryMessage,
        sourceSha256:hash(test.source),bundleSha256:hash(bundled.code),imports:bundled.imports,error:error.message});
    }
    const caughtInput=join(output,'initializer-caught-control.mjs');
    await writeOutput(caughtInput,caughtInitializer.source,{flag:'wx'});
    const caughtBundle=await bundle(caughtInput,null);
    assert(caughtBundle.imports.every(id=>id==='node:stream'||id==='node:stream/promises'));
    await admission.recheck();
    const caught=await selected.componentize(caughtBundle.code,options);
    await admission.recheck();
    assert.deepEqual(caught.interfaceAudit.emittedImports,selectedInterfaces);
    const caughtComponentPath=join(output,'initializer-caught-control.component.wasm');
    await writeOutput(caughtComponentPath,caught.component,{flag:'wx'});
    await admission.recheck();
    const report={schemaVersion:1,status:'FUTURE_CLASSIC_REAL_COMPONENT_GATES_PASSED',variant,
      engineSha256:metadata.engineSha256,engineReceipt:metadata,sourceRoot,pin,
      componentizerProvenance:selected.provenance,selectedManifests:metadata.selectedModuleManifests,capabilityPolicy,
      oracleReceiptSha256:hash(oracleBytes),expectedReceiptSha256:hash(sealedBytes),ordinaryGroups:19,
      bundle:{sha256:hash(lowered.code),imports:lowered.imports,moduleIds:lowered.moduleIds},
      component:{path:componentPath,sha256:hash(component),bytes:component.length,interfaceAudit,emittedWit},
      snapshotAndRetained:{retained,fresh:freshObserved},
      wasmtime:{path:host,sha256:WASMTIME_SHA256,version:version.stdout.trim(),observed:wasmtimeObserved,
        stdoutSha256:hash(result.stdout),stderr:result.stderr},initializationFailures,
      deployedFailures,deployedControls,
      caughtInitializerControl:{componentPath:caughtComponentPath,sourceSha256:hash(caughtInitializer.source),bundleSha256:hash(caughtBundle.code),
        componentSha256:hash(caught.component),interfaceAudit:caught.interfaceAudit},
      gcStressConfigured:variant==='gc-off',
      scope:'Pure guest classic streams; no process/timers/FS/sockets/HTTP capability, no ALS propagation or safe failed-instance reuse claim'};
    completedReport=report;
   }
  } finally { await admission.recheck(); }
  assert(completedReport,'A completed semantic gate must provide its report');
  await publishCompletion({output,report:completedReport,paths:tracked.paths});
}
