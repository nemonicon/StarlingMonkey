// Future actual-component observation runner. Not imported by Node oracle/tests.
import assert from 'node:assert/strict';
import {readFile,mkdir,lstat,symlink} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
import {hash} from './preflight.mjs';
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..');
export async function runTraceGate(admission){
 assert.equal(process.version,'v22.14.0');assert.equal(admission.variant,'normal-off');await admission.recheck();
 assert(process.env.NODE_COMPAT_STREAM_TRACE_OUTPUT,'Choose an explicit fresh stream trace output');const output=resolve(process.env.NODE_COMPAT_STREAM_TRACE_OUTPUT);assert(output.startsWith('/tmp/starling-node-compat/'));
 try{await lstat(output);assert.fail('Choose a fresh output');}catch(error){if(error.code!=='ENOENT')throw error;}
 await mkdir(dirname(output),{recursive:true});await mkdir(output,{recursive:false});
 const {trackedWriter,publishCompletion}=await import('../production-runtime-activated-v3/harness/completion.mjs');const tracked=trackedWriter(output),write=tracked.write;
 await write(join(output,'package.json'),' {"type":"module"}\n',{flag:'wx'});
 const oracle=JSON.parse(await readFile(join(here,'node-results.json')));assert.equal(oracle.groups,8);assert.equal(oracle.node,'v22.14.0');
 const toolchain=await loadToolchain(),selected=await loadComponentizer(toolchain);
 const builtinManifests=selectedManifestsForEngine(admission.metadata,{sourceRoot:admission.sourceRoot});
 const bundled=await bundleProfile({...toolchain,builtinManifests,input:join(here,'guest.mjs')});assert.deepEqual([...bundled.imports].sort(),['node:buffer','node:stream']);
 assert(bundled.moduleIds.every(value=>value===join(here,'guest.mjs')||value===join(here,'cases.mjs')),'Only guest/cases source may be bundled');
 assert.doesNotMatch(bundled.code,/createClassicStreams|classic-core\.generated|node_modules\/(?:unenv|readable-stream)|reference-kernel/);
 await write(join(output,'guest.bundle.mjs'),bundled.code,{flag:'wx'});await admission.recheck();
 const adapter=join(repository,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
 const options={engine:admission.enginePath,preview2Adapter:adapter,witWorld:'package test:stream-trace; world test { export run: func() -> string; }',worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]};
 const {component,interfaceAudit}=await selected.componentize(bundled.code,options);await admission.recheck();assert.deepEqual(interfaceAudit.emittedImports,[]);
 const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));const emittedWit=await componentWit(component);
 assert.equal(emittedWit.replace(/\s+/g,' ').trim(),'package root:component; world root { export run: func() -> string; }');
 const componentPath=join(output,'stream-trace.component.wasm');await write(componentPath,component,{flag:'wx'});await write(join(output,'emitted.wit'),emittedWit,{flag:'wx'});
 const generated=await transpile(component,{name:'stream_trace',wasiShim:true});for(const[name,bytes]of Object.entries(generated.files)){await mkdir(dirname(join(output,name)),{recursive:true});await tracked.writeGenerated(join(output,name),bytes,{flag:'wx'});}
 await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));
 const modulePath=join(output,'stream_trace.js'),instance=await import(pathToFileURL(modulePath));
 function validate(value,call){assert.equal(value.schema,1);assert.equal(value.calls,call);assert.equal(value.snapshot.bytes,64);assert.equal(value.snapshot.checksum,oracle.nodeObserved[0].checksum);assert.equal(value.observed.length,8);
  for(let i=0;i<8;i++){const row=value.observed[i],expected=oracle.nodeObserved[i];assert.equal(row.id,expected.id);assert.equal(row.bytes,64);assert.equal(row.checksum,expected.checksum);assert.equal(row.writeCalls,1);assert.equal(row.callbackCalls,1);assert(row.events.length<128);}
  return value;}
 const retained=[];for(let call=1;call<=3;call++)retained.push(validate(JSON.parse(await instance.run()),call));
 const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1'),freshJco=validate(JSON.parse(await fresh.run()),1);assert.deepEqual(freshJco,retained[0]);
 for(const value of retained)assert.deepEqual(value.observed,retained[0].observed,'Retained traces must be deterministic');
 const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');assert.equal(hash(await readFile(host)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
 const version=spawnSync(host,['--version'],{encoding:'utf8',timeout:55000});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
 const actual=spawnSync(host,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:55000,maxBuffer:2*1024*1024});assert.equal(actual.status,0,actual.error?.message??actual.stderr);
 const {decodeCliString}=await import('../../foundations/native-scalar-harness.mjs');const freshWasmtime=validate(JSON.parse(decodeCliString(actual.stdout.trim())),1);assert.deepEqual(freshWasmtime,retained[0]);
 const differences=[];for(let i=0;i<8;i++)if(JSON.stringify(retained[0].observed[i])!==JSON.stringify(oracle.nodeObserved[i]))differences.push({id:oracle.nodeObserved[i].id,node:oracle.nodeObserved[i],guest:retained[0].observed[i]});
 await admission.recheck();
 const report={schemaVersion:1,status:'REAL_COMPONENT_PUBLIC_STREAM_TRACE_OBSERVATIONS_COMPLETE',variant:'normal-off',engineSha256:admission.pin.engineSha256,engineReceiptSha256:admission.pin.receiptSha256,
  nativeSources:342,admission:admission.traceSourceAdmission,nodeOracleSha256:hash(await readFile(join(here,'node-results.json'))),nodeObserved:oracle.nodeObserved,labelledHostModel:oracle.hostModel,
  componentPath,componentSha256:hash(component),componentBytes:component.length,interfaceAudit,emittedWit,sourceModules:bundled.moduleIds,bundleImports:bundled.imports,bundleSha256:hash(bundled.code),packager:selected.provenance,
  retained,freshJco,wasmtime:{path:host,sha256:hash(await readFile(host)),version:version.stdout.trim(),status:actual.status,stdout:actual.stdout,stderr:actual.stderr,observed:freshWasmtime},
  differences,nodeCompatibilityPassed:differences.length===0,hostModelEqualsActualGuest:JSON.stringify(oracle.hostModelObserved)===JSON.stringify(retained[0].observed),
  scope:'Observation gate: valid64byte operations and retained/fresh component consistency required. Node trace differences are reported, not suppressed or forced. No host service, private nextTick export, source fix or performance claim.',
  requiresIndependentTerminalExitCodeZero:true};
 await publishCompletion({output,report,paths:tracked.paths});console.log(JSON.stringify({status:report.status,output,nodeCompatibilityPassed:report.nodeCompatibilityPassed,differences:differences.map(row=>row.id),imports:[]}));
}
