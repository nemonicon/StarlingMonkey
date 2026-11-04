// UNEXECUTED correctness-only driver. Loaded only after fixed actual admission.
import assert from 'node:assert/strict';
import {readFile,mkdir,lstat,symlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {bundleDiagnostic} from './bundle-diagnostic.mjs';
import {trackedWriter,publishCompletion} from './completion.mjs';
import {requireExactJSON,RecordedMismatch} from './bounded-comparison.mjs';
import {persistFile,progressJournal,runOwnedCommand} from './durable-host.mjs';
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
 for(const name of ['progress','case-results','rotations','processes'])await mkdir(join(output,name));
 const progress=progressJournal({output,write});
 const persist=(name,data)=>persistFile({output,write,path:join(output,name),data});
 await progress('driver-started',{workloadCases:20,boundaryCases:14,resumeSupported:false,reusedResults:0});
 try {
 await write(join(output,'package.json'),'{"type":"module"}\n',{flag:'wx'});await write(join(output,'guest.bundle.mjs'),bundle.code,{flag:'wx'});
 const adapter=join(root,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
 assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
 const wit='package test:classic-correctness; world test { export run: func(case-index: u32) -> string; export boundaries: func() -> string; }';
 await progress('componentize-before');
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
 async function validateCase(value,index,call,context=null){const row=expectedCase(index),expected={schemaVersion:1,calls:call,caseIndex:index,setup:row.setup,result:row.oracle};await requireExactJSON({label:'workload-'+index,actual:value,expected,context,writeCounterexample});return value;}
 async function validateBoundaries(value,call,context=null){await requireExactJSON({label:'boundaries',actual:value,expected:{schemaVersion:1,calls:call,observed:encoding.expected},context,writeCounterexample});return value;}
 async function writeCounterexample(record){await write(join(output,'correctness-counterexample.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});}
 async function retainCounterexample(label,actual,expected,error){await write(join(output,'correctness-counterexample.json'),JSON.stringify({label,actual,expected,error:{name:error.name,message:error.message},runtimeAcceptanceClaim:false},null,2)+'\n',{flag:'wx'});throw error;}
 const modulePath=join(output,'classic_correctness.js'),instance=await import(pathToFileURL(modulePath));
 async function jcoCase(instance,startCall,label,index){
  const name=label+'-'+(index<20?'case-'+String(index).padStart(2,'0'):'boundaries'),expression=index<20?'run('+index+')':'boundaries()';
  await progress('jco-before',{label,index,expression,expectedCall:startCall});
  let raw;
  try{raw=index<20?await instance.run(index):await instance.boundaries();}
  catch(error){await progress('jco-call-rejected',{label,index,expression,error:{name:error.name,code:error.code,message:String(error.message).slice(0,512)}});throw error;}
  const rawFile=await persist('case-results/'+name+'.raw.txt',raw);
  let value;
  try{value=JSON.parse(raw);}catch(error){await retainCounterexample(name,{raw},index<20?expectedCase(index):encoding.expected,error);}
  const observedFile=await persist('case-results/'+name+'.observed.json',JSON.stringify(value,null,2)+'\n');
  await progress('jco-returned',{label,index,expression,rawFile,observedFile,validationCompleted:false});
  try{if(index<20)await validateCase(value,index,startCall,{rawFile});else await validateBoundaries(value,startCall,{rawFile});}
  catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample(name,value,index<20?expectedCase(index):encoding.expected,error);}
  await progress('jco-validated',{label,index,expression,rawFile,observedFile});return value;
 }
 async function oneRotation(instance,startCall,label){const cases=[];
  for(let index=0;index<20;index++)cases.push(await jcoCase(instance,startCall+index,label,index));
  const boundaries=await jcoCase(instance,startCall+20,label,20),rotation={cases,boundaries};
  await persist('rotations/'+label+'.json',JSON.stringify(rotation,null,2)+'\n');
  await progress('jco-rotation-validated',{label,cases:20,boundaryCases:14});return rotation;
 }
 const retained=[];for(let round=0;round<3;round++)retained.push(await oneRotation(instance,round*21+1,'retained'+round));
 const fresh=await import(pathToFileURL(modulePath).href+'?fresh=1'),freshJco=await oneRotation(fresh,1,'freshJco');
 await requireExactJSON({label:'fresh-Jco-full-rotation',actual:freshJco,expected:retained[0],writeCounterexample});
 await progress('fresh-jco-full-rotation-exact');
 const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
 assert.equal(hash(await readFile(host)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
 const invoke=(name,args,timeoutMs=600000,maxOutputBytes=16*1024*1024)=>runOwnedCommand({output,name,executable:host,args,write,register:path=>tracked.paths.add(path),timeoutMs,maxOutputBytes,
  onProgress:detail=>console.log(JSON.stringify({event:'wasmtime-running',...detail}))});
 const version=await invoke('wasmtime-version',['--version'],55000,1024*1024);
 if(!version.terminalExitZeroObserved)throw new Error('Wasmtime version process failed; see '+version.terminalPath);
 assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
 const {decodeCliString}=await import(pathToFileURL(join(root,'tests/node-compat/foundations/native-scalar-harness.mjs')));
 const wasmtime=[];
 for(let index=0;index<=20;index++){
  const expression=index<20?'run('+index+')':'boundaries()',name='wasmtime-'+(index<20?'case-'+String(index).padStart(2,'0'):'boundaries');
  await progress('wasmtime-before',{index,expression,deadlineMs:600000,freshProcess:true});
  const actual=await invoke(name,['run','--invoke',expression,componentPath]);
  await progress('wasmtime-process-returned',{index,expression,terminalPath:actual.terminalPath,status:actual.status,timedOut:actual.timedOut,
   stdoutFile:actual.stdoutFile,stderrFile:actual.stderrFile,validationCompleted:false});
  if(!actual.terminalExitZeroObserved)throw new Error('Wasmtime did not complete successfully for '+expression+'; see '+actual.terminalPath);
  let value;
  try{value=JSON.parse(decodeCliString(actual.stdout.trim()));}
  catch(error){await retainCounterexample('freshWasmtime/'+expression,{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath},index<20?expectedCase(index):encoding.expected,error);}
  const observedFile=await persist('case-results/'+name+'.observed.json',JSON.stringify(value,null,2)+'\n');
  try{if(index<20)await validateCase(value,index,1,{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath});else await validateBoundaries(value,1,{stdout:actual.stdout,stderr:actual.stderr,terminalPath:actual.terminalPath});}
  catch(error){if(error instanceof RecordedMismatch)throw error;await retainCounterexample('freshWasmtime/'+expression,{value,stdout:actual.stdout,stderr:actual.stderr},index<20?expectedCase(index):encoding.expected,error);}
  const record={expression,status:actual.status,stdout:actual.stdout,stderr:actual.stderr,observed:value,
   terminalPath:actual.terminalPath,stdoutFile:actual.stdoutFile,stderrFile:actual.stderrFile,deadlineMs:600000};
  await persist('case-results/'+name+'.validated.json',JSON.stringify(record,null,2)+'\n');wasmtime.push(record);
  await progress('wasmtime-validated',{index,expression,observedFile,terminalPath:actual.terminalPath});
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
  durableObservationFiles:true,perCaseWasmtimeDeadlineMs:600000,resumeSupported:false,reusedResults:0,partialObservationsAreNotCompletePasses:true,
  scope:'Full original20Node workloads and14valid boundaries, no trace normalization or scheduler/provider substitution. No wholecomponent cost, GC/root isolation, reset/ALS, reuse or broad Streams claim.'};
 await publishCompletion({output,report,paths:tracked.paths});console.log(JSON.stringify({status:report.status,output,componentSha256:report.componentSha256,imports:[],workloadCases:20,boundaryCases:14}));
 } catch(error) {
  try{await progress('driver-failed',{error:{name:error.name,code:error.code,message:String(error.message).slice(0,512)},completePass:false});}
  catch(recordError){console.error(JSON.stringify({event:'failure-record-write-failed',name:recordError.name,code:recordError.code,message:String(recordError.message).slice(0,512),completePass:false}));}
  throw error;
 }
}
