// Future explicit correctness/packaging action. Never run by source tests.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat,symlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {performance} from 'node:perf_hooks';
import {executionPreflight} from './runtime-preflight.mjs';
import {bundleMatched} from './bundle-matched.mjs';
import {cases,arms} from './protocol.mjs';
import {loadCompiled} from './instantiate.mjs';
import {requireExactJSON} from './bounded-comparison.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
const indexSha=process.argv[2];assert(/^[0-9a-f]{64}$/.test(indexSha??''));const indexRaw=await readFile(join(here,'index.json'));assert.equal(hash(indexRaw),indexSha);
for(const row of JSON.parse(indexRaw).files){const raw=await readFile(join(here,row.path));assert.equal(hash(raw),row.sha256);assert.equal(raw.length,row.bytes);}
const on=await executionPreflight({variant:'benchmark-classic-on'}),off=await executionPreflight({variant:'benchmark-classic-off'});
const output=resolve(process.env.NODE_COMPAT_COMMON_BYTE_CORRECTNESS_OUTPUT??'');assert(output.startsWith('/tmp/starling-node-compat/'));
try{await lstat(output);assert.fail('Fresh output required');}catch(error){if(error.code!=='ENOENT')throw error;}
const {loadToolchain}=await import(pathToFileURL(join(on.toolSourceRoot,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();
const {loadComponentizer}=await import(pathToFileURL(join(on.toolSourceRoot,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);
const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const common=JSON.parse(await readFile(join(here,'node-common-oracle.json'))),controls=JSON.parse(await readFile(join(here,'node-control-oracle.json')));
const oracle=[...common.cases,...controls.cases];assert.equal(oracle.length,14);
for(let i=0;i<cases.length;i++){assert.equal(oracle[i].id,cases[i].id);assert.equal(oracle[i].iterations,cases[i].iterations);}
const adapter=join(on.toolSourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');assert.equal(hash(await readFile(host)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
const {decodeCliString}=await import(pathToFileURL(join(on.toolSourceRoot,'tests/node-compat/foundations/native-scalar-harness.mjs')));
await mkdir(output,{recursive:false});await writeFile(join(output,'package.json'),'{"type":"module"}\n',{flag:'wx'});await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));
const records=[];
const progress=(arm,stage,index=null,call=null)=>process.stderr.write(JSON.stringify({arm,stage,index,call})+'\n');
for(const arm of arms){
 progress(arm,'bundle-and-componentize');
 const admission=arm==='canonical-off'?off:on,directory=join(output,arm);await mkdir(directory);await admission.recheck();
 const bundle=await bundleMatched(toolchain,admission,arm);await writeFile(join(directory,'application.bundle.mjs'),bundle.code,{flag:'wx'});await writeFile(join(directory,'bundle-graph.json'),JSON.stringify(bundle.graph,null,2)+'\n',{flag:'wx'});
 const wit='package test:common-byte; world test { export setup: func(index: u32) -> s32; export inspect: func(index: u32) -> string; export batch: func(index: u32, iterations: u32) -> string; export identity: func() -> string; export checkpoint-probe: func() -> string; }';
 const componentizeStart=performance.now(),{component,interfaceAudit}=await selected.componentize(bundle.code,{engine:admission.enginePath,preview2Adapter:adapter,witWorld:wit,worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]}),componentizationWallMs=performance.now()-componentizeStart;
 await admission.recheck();assert.deepEqual(interfaceAudit.emittedImports,[]);const emittedWit=await componentWit(component);assert.doesNotMatch(emittedWit,/\bimport\b/);
 const exports=(emittedWit.match(/export\s+[\w-]+:\s*func\([^;]*;/g)??[]).map(value=>value.replace(/\s+/g,' ').trim()).sort();
 assert.deepEqual(exports,['export setup: func(index: u32) -> s32;','export inspect: func(index: u32) -> string;','export batch: func(index: u32, iterations: u32) -> string;','export identity: func() -> string;','export checkpoint-probe: func() -> string;'].sort());
 const componentPath=join(directory,'common-byte.component.wasm');await writeFile(componentPath,component,{flag:'wx'});await writeFile(join(directory,'emitted.wit'),emittedWit,{flag:'wx'});
 const transpileStart=performance.now(),{files}=await transpile(component,{name:'common_byte',instantiation:'async'}),transpileWallMs=performance.now()-transpileStart,transpiledFiles=[];
 for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(directory,name)),{recursive:true});await writeFile(join(directory,name),bytes,{flag:'wx'});transpiledFiles.push({name,sha256:hash(bytes),bytes:bytes.length});}
 const record={arm,componentPath,componentSha256:hash(component),componentBytes:component.length,enginePath:admission.enginePath,engineSha256:admission.pin.engineSha256,engineMetadataSha256:admission.pin.metadataSha256,
  modulePath:join(directory,'common_byte.js'),coreFiles:Object.keys(files).filter(name=>name.endsWith('.wasm')),transpiledFiles,bundleSha256:bundle.graph.bundleSha256,emittedImports:interfaceAudit.emittedImports,interfaceAudit,graph:bundle.graph,packager:selected.provenance,componentizationWallMs,transpileWallMs,buildTimingScope:'Sequential host packaging wall time; cold cache and isolated snapshot time not established'};
 const instantiate=await loadCompiled(record);let recorded=false;
 async function writeCounterexample(value){assert(!recorded);recorded=true;await writeFile(join(directory,'counterexample.json'),JSON.stringify(value,null,2)+'\n',{flag:'wx'});}
 const expectedIdentity={defaultGraph:true,promisesGraph:true,eventEmitterPrototype:true,selectedTickType:'function',decoderA:'A',bufferView:true,bufferSameAsBefore:arm!=='stock-on',globalSameAsProvider:true,beforeBufferType:'function',globalChangedDuringProvider:arm==='stock-on'};
 async function identity(instance){const value=JSON.parse(await instance.exports.identity());await requireExactJSON({label:'provider-identity',actual:value,expected:expectedIdentity,writeCounterexample});return value;}
 function probe(value){assert.equal(value.callbacks,1);assert.deepEqual([...value.trace].sort(),['microtask','selected-tick']);assert.equal(value.queueDepthObserved,false);assert.equal(value.terminalQueueEmptyObserved,false);return value;}
 async function rotation(instance,start){const rows=[];for(let i=0;i<14;i++){progress(arm,'full-trace-Jco',i,start+i);const actual=JSON.parse(await instance.exports.inspect(i));await requireExactJSON({label:'full-trace-'+i,actual,expected:{calls:start+i,setup:oracle[i].setup,result:oracle[i].expected},writeCounterexample});rows.push(actual);}return rows;}
 const retained=await instantiate(),retainedIdentity=await identity(retained),retainedProbe=probe(JSON.parse(await retained.exports.checkpointProbe())),rounds=[];
 for(let round=0;round<3;round++)rounds.push(await rotation(retained,round*14+1));
 const afterProbe=probe(JSON.parse(await retained.exports.checkpointProbe()));await requireExactJSON({label:'retained-checkpoint-probe',actual:afterProbe,expected:retainedProbe,writeCounterexample});
 const fresh=await instantiate();await identity(fresh);const freshProbe=probe(JSON.parse(await fresh.exports.checkpointProbe()));await requireExactJSON({label:'fresh-checkpoint-probe',actual:freshProbe,expected:retainedProbe,writeCounterexample});const freshRows=await rotation(fresh,1);
 const wt=[];for(let i=-2;i<14;i++){
  progress(arm,'fresh-Wasmtime',i,1);
  const expression=i===-2?'identity()':i===-1?'checkpoint-probe()':'inspect('+i+')',actual=spawnSync(host,['run','--invoke',expression,componentPath],{encoding:'utf8',timeout:55000,maxBuffer:16*1024*1024});
  await writeFile(join(directory,'wt-'+(i+2)+'.stdout'),actual.stdout??'',{flag:'wx'});await writeFile(join(directory,'wt-'+(i+2)+'.stderr'),actual.stderr??'',{flag:'wx'});assert.equal(actual.status,0,actual.error?.message??actual.stderr);
  const value=JSON.parse(decodeCliString(actual.stdout.trim()));await requireExactJSON({label:'fresh-WT-'+i,actual:value,expected:i===-2?expectedIdentity:i===-1?retainedProbe:{calls:1,setup:oracle[i].setup,result:oracle[i].expected},context:{stdout:actual.stdout,stderr:actual.stderr},writeCounterexample});wt.push({expression,status:actual.status,observed:value});
 }
 record.correctnessPassed=true;record.identityPassed=true;record.checkpointProbePassed=true;record.identity=retainedIdentity;record.checkpointProbe=retainedProbe;
 record.correctness={retainedRotations:3,rounds,freshRows,wasmtime:wt};record.declaredSchedulerLimits=admission.metadata.internalTickPolicy.limits;
 record.schedulerBudget={override:false,cumulativeWorkloadIterationBounds:[1,16],nativeQueueCountersObserved:false,provider:arm==='stock-on'?'Unmodified queueMicrotask FIFO; its callbacks are not native private-nextTick work-counter observations':'Actual private nextTick callable; success under configured limit, no counter observability'};
 records.push(record);await admission.recheck();await writeFile(join(output,'partial.json'),JSON.stringify({records},null,2)+'\n');
}
assert.equal(records[1].bundleSha256,records[2].bundleSha256,'Canonical ON/OFF application bundle must be byte-identical');
await on.recheck();await off.recheck();
const report={schemaVersion:1,state:'ACTUAL_COMMON_BYTE_FOUR_ARM_CORRECTNESS_PASSED',sourceFamilyIndexSha256:indexSha,pairPinsSha256:on.pairSha256,records,commonCases:8,controlCases:6,controlsSubtracted:false,original28CounterexamplesPreserved:true,timingAllowed:false,
 queueEmptyProof:false,rootIsolationProof:false,cppStateMachineClaim:false,requiresIndependentExitCodeZero:true};
await writeFile(join(output,'correctness-results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:report.state,output,arms:4,commonCases:8,controlCases:6,imports:[]}));
