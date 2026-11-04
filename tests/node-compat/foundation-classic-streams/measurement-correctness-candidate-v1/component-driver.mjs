// UNEXECUTED correctness-only driver. Loaded only after fixed actual admission.
import assert from 'node:assert/strict';
import {readFile,mkdir,lstat,symlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {bundleDiagnostic} from './bundle-diagnostic.mjs';
import {trackedWriter,publishCompletion} from './completion.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=data=>createHash('sha256').update(data).digest('hex');
export async function runCorrectness(admission){
 assert.equal(process.version,'v22.14.0');assert.equal(admission.variant,'benchmark-classic-on');await admission.recheck();
 const root=admission.toolSourceRoot;assert(root);assert(process.env.NODE_COMPAT_CLASSIC_CORRECTNESS_OUTPUT);
 const output=resolve(process.env.NODE_COMPAT_CLASSIC_CORRECTNESS_OUTPUT);assert(output.startsWith('/tmp/starling-node-compat/'));
 try{await lstat(output);assert.fail('Choose a fresh correctness output');}catch(error){if(error.code!=='ENOENT')throw error;}
 const workload=JSON.parse(await readFile(join(here,'node-workload-oracle.json'))),encoding=JSON.parse(await readFile(join(here,'node-encoding-oracle.json')));
 assert.equal(workload.node,'v22.14.0');assert.equal(workload.expected.length,20);assert.equal(encoding.expected.length,14);
 const {loadToolchain}=await import(pathToFileURL(join(root,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();
 const {loadComponentizer}=await import(pathToFileURL(join(root,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(toolchain);
 const bundle=await bundleDiagnostic({toolchain,admission,input:join(here,'guest.mjs'),allowedModuleIds:['guest.mjs','native-provider.mjs','workload.mjs','encoding-cases.mjs'].map(name=>join(here,name))});
 await admission.recheck();await mkdir(dirname(output),{recursive:true});await mkdir(output,{recursive:false});
 const tracked=trackedWriter(output),write=tracked.write;
 await write(join(output,'package.json'),'{"type":"module"}\n',{flag:'wx'});await write(join(output,'guest.bundle.mjs'),bundle.code,{flag:'wx'});
 const adapter=join(root,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
 assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
 const wit='package test:classic-correctness; world test { export run: func(case-index: u32) -> string; export boundaries: func() -> string; }';
 const {component,interfaceAudit}=await selected.componentize(bundle.code,{engine:admission.enginePath,preview2Adapter:adapter,witWorld:wit,worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
 await admission.recheck();assert.deepEqual(interfaceAudit.emittedImports,[]);
 const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco'))),emittedWit=await componentWit(component);
 const declared=(emittedWit.match(/export\s+[\w-]+:\s*func\([^;]*;/g)??[]).map(value=>value.replace(/\s+/g,' ').trim()).sort();
 assert.deepEqual(declared,['export boundaries: func() -> string;','export run: func(case-index: u32) -> string;']);assert.doesNotMatch(emittedWit,/\bimport\b/);
 const componentPath=join(output,'classic-correctness.component.wasm');await write(componentPath,component,{flag:'wx'});await write(join(output,'emitted.wit'),emittedWit,{flag:'wx'});
 const generated=await transpile(component,{name:'classic_correctness',wasiShim:true});
 for(const[name,bytes]of Object.entries(generated.files)){await mkdir(dirname(join(output,name)),{recursive:true});await tracked.writeGenerated(join(output,name),bytes,{flag:'wx'});}
 await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));
 function expectedCase(index){const row=workload.expected[index];assert(row&&[1,16].includes(row.iterations));return row;}
 function validateCase(value,index,call){const expected=expectedCase(index);assert.equal(value.schemaVersion,1);assert.equal(value.calls,call);assert.equal(value.caseIndex,index);assert.equal(value.setup,expected.setup);assert.deepEqual(value.result,expected.oracle);return value;}
 function validateBoundaries(value,call){assert.equal(value.schemaVersion,1);assert.equal(value.calls,call);assert.deepEqual(value.observed,encoding.expected);return value;}
 async function retainCounterexample(label,actual,expected,error){await write(join(output,'correctness-counterexample.json'),JSON.stringify({label,actual,expected,error:{name:error.name,message:error.message},runtimeAcceptanceClaim:false},null,2)+'\n',{flag:'wx'});throw error;}
 const modulePath=join(output,'classic_correctness.js'),instance=await import(pathToFileURL(modulePath));
 async function oneRotation(instance,startCall,label){const cases=[];
  for(let index=0;index<20;index++){const value=JSON.parse(await instance.run(index));try{cases.push(validateCase(value,index,startCall+index));}catch(error){await retainCounterexample(label+'/case'+index,value,expectedCase(index),error);}}
  const boundaries=JSON.parse(await instance.boundaries());try{validateBoundaries(boundaries,startCall+20);}catch(error){await retainCounterexample(label+'/boundaries',boundaries,encoding.expected,error);}return{cases,boundaries};}
 const retained=[];for(let round=0;round<3;round++)retained.push(await oneRotation(instance,round*21+1,'retained'+round));
 const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1'),freshJco=await oneRotation(fresh,1,'freshJco');
 assert.deepEqual(freshJco,retained[0]);
 const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
 assert.equal(hash(await readFile(host)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
 const version=spawnSync(host,['--version'],{encoding:'utf8',timeout:55000});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
 const {decodeCliString}=await import(pathToFileURL(join(root,'tests/node-compat/foundations/native-scalar-harness.mjs')));
 const wasmtime=[];
 for(let index=0;index<=20;index++){
  const expression=index<20?'run('+index+')':'boundaries()',actual=spawnSync(host,['run','--invoke',expression,componentPath],{encoding:'utf8',timeout:55000,maxBuffer:16*1024*1024});
  assert.equal(actual.status,0,actual.error?.message??actual.stderr);const value=JSON.parse(decodeCliString(actual.stdout.trim()));
  try{if(index<20)validateCase(value,index,1);else validateBoundaries(value,1);}catch(error){await retainCounterexample('freshWasmtime/'+expression,{value,stdout:actual.stdout,stderr:actual.stderr},index<20?expectedCase(index):encoding.expected,error);}
  wasmtime.push({expression,status:actual.status,stdout:actual.stdout,stderr:actual.stderr,observed:value});
 }
 await admission.recheck();
 const report={schemaVersion:1,status:'ACTUAL_CLASSIC_DIAGNOSTIC_20_WORKLOAD_14_BOUNDARY_CORRECTNESS_PASSED',variant:admission.variant,
  engineSha256:admission.pin.engineSha256,engineMetadataSha256:admission.pin.metadataSha256,recipeSha256:admission.pin.recipeSha256,
  nativeSources:342,addonSources:2,componentPath,componentSha256:hash(component),componentBytes:component.length,interfaceAudit,emittedWit,
  bundleImports:bundle.imports,sourceModules:bundle.moduleIds,bundleSha256:hash(bundle.code),packager:selected.provenance,
  nodeWorkloadOracleSha256:hash(await readFile(join(here,'node-workload-oracle.json'))),nodeBoundaryOracleSha256:hash(await readFile(join(here,'node-encoding-oracle.json'))),
  workloadCases:20,boundaryCases:14,retainedRotations:3,retained,freshJco,wasmtime:{path:host,sha256:hash(await readFile(host)),version:version.stdout.trim(),freshCalls:21,results:wasmtime},
  declaredSchedulerLimits:admission.metadata.internalTickPolicy.limits,
  schedulerObservability:'One exported entry per workload case, cumulative1/16 iterations within that checkpoint; no budget override or await reset. scheduledCallbacks is the original explicit-workload counter, not a native queue/work counter. The addon exports nextTick only; terminal empty-queue counters are unavailable.',
  timingPerformed:false,timingAllowed:false,requiresIndependentTerminalExitCodeZero:true,runtimeAcceptanceClaim:false,
  scope:'Full original20Node workloads and14valid boundaries, no trace normalization or scheduler/provider substitution. No wholecomponent cost, GC/root isolation, reset/ALS, reuse or broad Streams claim.'};
 await publishCompletion({output,report,paths:tracked.paths});console.log(JSON.stringify({status:report.status,output,componentSha256:report.componentSha256,imports:[],workloadCases:20,boundaryCases:14}));
}
